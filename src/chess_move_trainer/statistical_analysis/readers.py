"""Batch adapters reusing production validation, canonicalization, and date rules."""

from collections import defaultdict, OrderedDict
from datetime import datetime, timezone
import re

from chess_move_trainer.database.analysis.reading import AnalysisReadError, _materialize_result
from chess_move_trainer.database.openings.recognition import _materialize_routes, _endpoint_map
from chess_move_trainer.database.preferred_moves.ranges import (
    Preference, normalize_periods, period_from_literals, resolve_date,
)


class AnalysisCache:
    def __init__(self, connection, size=20000):
        self.connection = connection
        self.size = size
        self.cache = OrderedDict()

    def load(self, position_ids):
        missing = sorted(set(position_ids) - self.cache.keys())
        loaded = {}
        for start in range(0, len(missing), 400):
            ids = missing[start:start + 400]
            marks = ",".join("?" for _ in ids)
            parents = self.connection.execute(f"""
                SELECT derived_position_id, dar_quality, dar_configuration_version,
                  dar_settings_json, dar_engine_name, dar_engine_version, dar_terminal_kind,
                  dp_placement, dp_side_to_move, dp_castling_rights, dp_legal_en_passant
                FROM derived_analysis_result JOIN derived_position
                  ON derived_position_id=dp_position_id WHERE derived_position_id IN ({marks})
            """, ids).fetchall()
            lines = defaultdict(list)
            for row in self.connection.execute(f"""
                SELECT derived_analysis_result_id, dal_rank, dal_score_kind, dal_score_value,
                  dal_wdl_wins, dal_wdl_draws, dal_wdl_losses, dal_pv_uci_json, dal_depth
                FROM derived_analysis_line WHERE derived_analysis_result_id IN ({marks})
                ORDER BY derived_analysis_result_id, dal_rank
            """, ids):
                lines[row[0]].append(tuple(row)[1:])
            loaded.update({i: (None, None) for i in ids})
            for parent in parents:
                try:
                    loaded[parent[0]] = (_materialize_result(parent, lines[parent[0]]), None)
                except AnalysisReadError as error:
                    loaded[parent[0]] = (None, str(error))
        result = {i: self.cache[i] if i in self.cache else loaded[i] for i in position_ids}
        self.cache.update(loaded)
        for i in position_ids:
            if i in self.cache:
                self.cache.move_to_end(i)
        while len(self.cache) > self.size:
            self.cache.popitem(last=False)
        return result


def load_openings(connection):
    routes = connection.execute("""
        SELECT r.dor_route_id, r.datasource_opening_id, r.derived_position_id, o.do_eco,
          o.do_name, p.dp_position_id, p.dp_placement, p.dp_side_to_move,
          p.dp_castling_rights, p.dp_legal_en_passant
        FROM derived_opening_route r LEFT JOIN datasource_opening o
          ON o.do_opening_id=r.datasource_opening_id
        LEFT JOIN derived_position p ON p.dp_position_id=r.derived_position_id
        ORDER BY r.dor_route_id
    """).fetchall()
    moves = connection.execute("""SELECT derived_opening_route_id, dorm_ply, dorm_move_uci
        FROM derived_opening_route_move ORDER BY derived_opening_route_id, dorm_ply""").fetchall()
    return _endpoint_map(_materialize_routes(routes, moves))


def load_preferences(connection):
    grouped = defaultdict(list)
    for pid, start, end, move in connection.execute("""SELECT derived_position_id,
        dpm_effective_from, dpm_effective_until, dpm_move_uci
        FROM datasource_preferred_move_period ORDER BY derived_position_id, dpm_effective_from"""):
        preference = Preference.preferred_move(move) if move else Preference.no_preference()
        grouped[pid].append(period_from_literals(start, end, preference))
    return {pid: normalize_periods(periods) for pid, periods in grouped.items()}


def preference_at(preferences, pid, day):
    if day is None:
        return None
    return resolve_date(preferences.get(pid, ()), day).move


def timestamp(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError, AttributeError):
        return None


def time_control(value):
    if value is None or value == "":
        return {"kind": "unknown", "base": None, "increment": None}
    if re.fullmatch(r"[1-9]\d*/[1-9]\d*", value):
        return {"kind": "daily", "base": None, "increment": None}
    if re.fullmatch(r"[1-9]\d*(\+\d+)?", value):
        parts = value.split("+")
        return {"kind": "increment" if len(parts) == 2 else "no_increment",
                "base": int(parts[0]), "increment": int(parts[1]) if len(parts) == 2 else 0}
    return {"kind": "unsupported", "base": None, "increment": None}
