"""Generate deterministic, descriptive historical metrics for the Caro-Kann tree.

This is a noncanonical exploratory report.  It treats ``caro_kann_tree.json`` as
the approved exact-prefix population, replays the same population from the
tracked-corpus SQLite database in read-only mode, and writes no production or
engine data.  Every source position and every observed immediate move is kept,
including small and unexpanded branches.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timezone
from itertools import groupby
from pathlib import Path
from typing import Any, Iterable

import chess

import caro_kann_tree as tree_builder


EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[2]
DEFAULT_DATABASE = REPO_ROOT / "data" / "database" / "chess_games.db"
DEFAULT_SOURCE = EXPERIMENT_DIR / "caro_kann_tree.json"
DEFAULT_JSON_OUTPUT = EXPERIMENT_DIR / "caro_kann_historical_metrics.json"
DEFAULT_MARKDOWN_OUTPUT = EXPERIMENT_DIR / "caro_kann_historical_metrics.md"

SCHEMA = "caro-kann-historical-metrics/v1"
ROOT_PREFIX = ("e4", "c6")
EXPECTED_CANDIDATE_GAMES = 6180
EXPECTED_ROOT_GAMES = 3358
EXPECTED_ROOT_OUTCOMES = {"win": 1697, "draw": 91, "loss": 1570, "unknown": 0}
EXPECTED_NODE_COUNT = 229
EXPECTED_BRANCH_COUNT = 863
EXPECTED_UNEXPANDED_BRANCH_COUNT = 635
EXPECTED_NEWEST_DATE = date(2026, 8, 17)
RECENCY_CUTOFF = date(2025, 8, 17)
WILSON_Z = 1.959963984540054
PERCENT_DECIMALS = 2
KNOWN_DRAW_CODES = tree_builder.KNOWN_DRAW_CODES
TIME_CLASS_KEYS = ("bullet", "blitz", "rapid", "other_or_unknown")
RECENCY_KEYS = ("recent_12_months", "older", "date_unknown")
STRENGTH_KEYS = ("stronger", "similar", "weaker", "unknown")

OCCURRENCE_QUERY = """
SELECT cg.game_uuid, g.black_result, g.white_result, g.end_time, g.time_class,
       g.white_rating, g.black_rating, po.ply, po.san, po.uci,
       po.halfmove_clock, po.fullmove_number,
       ps.placement, ps.side_to_move, ps.castling, ps.en_passant
FROM corpus_game AS cg JOIN games AS g ON g.uuid = cg.game_uuid
JOIN position_occurrence AS po ON po.game_uuid = cg.game_uuid
JOIN position_state AS ps ON ps.state_id = po.state_id
WHERE cg.corpus_id = ? AND cg.rules = 'chess'
  AND g.black_player_uuid = ? AND g.white_player_uuid <> ?
ORDER BY cg.game_uuid, po.ply
"""


def fail(message: str) -> None:
    raise SystemExit(f"Historical metrics validation failed: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def ensure_experiment_path(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(EXPERIMENT_DIR.resolve())
    except ValueError as error:
        raise SystemExit(f"{label} must remain under {EXPERIMENT_DIR}") from error
    return resolved


def format_line(sans: Iterable[str]) -> str:
    parts: list[str] = []
    for index, san in enumerate(sans):
        if index % 2 == 0:
            parts.append(f"{index // 2 + 1}.")
        parts.append(san)
    return " ".join(parts)


def node_id_for(sans: Iterable[str]) -> str:
    joined = "\x1f".join(sans)
    return "n" + hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def branch_id_for(sans: Iterable[str]) -> str:
    joined = "\x1f".join(sans)
    return "b" + hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def exact_pct(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return 100.0 * numerator / denominator


def outcome_counts(records: Iterable["GameRecord"], indexes: Iterable[int]) -> dict[str, int]:
    counts = {"win": 0, "draw": 0, "loss": 0, "unknown": 0}
    for index in indexes:
        counts[records[index].outcome] += 1
    return counts


def classify_outcome(black_result: str, white_result: str) -> str:
    black_won, white_won = black_result == "win", white_result == "win"
    if black_won != white_won:
        return "win" if black_won else "loss"
    if black_result in KNOWN_DRAW_CODES and white_result in KNOWN_DRAW_CODES:
        return "draw"
    return "unknown"


class GameRecord:
    def __init__(
        self,
        game_uuid: str,
        sans: tuple[str, ...],
        ucis: tuple[str, ...],
        outcome: str,
        end_time: int | None,
        time_class: str | None,
        white_rating: int | None,
        black_rating: int | None,
    ) -> None:
        self.game_uuid = game_uuid
        self.sans = sans
        self.ucis = ucis
        self.outcome = outcome
        self.end_time = end_time
        self.time_class = time_class
        self.white_rating = white_rating
        self.black_rating = black_rating

    @property
    def date_utc(self) -> date | None:
        if self.end_time is None:
            return None
        return datetime.fromtimestamp(self.end_time, timezone.utc).date()

    @property
    def time_class_key(self) -> str:
        return self.time_class if self.time_class in {"bullet", "blitz", "rapid"} else "other_or_unknown"

    @property
    def recency_key(self) -> str:
        if self.date_utc is None:
            return "date_unknown"
        return "recent_12_months" if self.date_utc >= RECENCY_CUTOFF else "older"

    @property
    def strength_key(self) -> str:
        if self.white_rating is None or self.black_rating is None:
            return "unknown"
        difference = self.white_rating - self.black_rating
        if difference >= 100:
            return "stronger"
        if difference <= -100:
            return "weaker"
        return "similar"


def validate_game(rows: list[tuple[Any, ...]]) -> GameRecord | None:
    game_uuid = str(rows[0][0])

    def corrupted(detail: str) -> None:
        fail(f"game {game_uuid}: {detail}")

    plies = [row[7] for row in rows]
    if plies != list(range(len(rows))):
        corrupted("occurrence plies are missing or not adjacent from ply 0")
    head = rows[0]
    if head[8:12] != (None, None, 0, 1):
        corrupted("ply 0 must store no move and start both clocks")
    initial_state = tuple(chess.Board().fen(en_passant="fen").split()[:4])
    if tuple(head[12:16]) != initial_state:
        corrupted("ply 0 state is not the standard initial position")
    for row in rows:
        if row[1:7] != head[1:7]:
            corrupted("game metadata changes within its occurrence rows")

    board = chess.Board()
    sans: list[str] = []
    ucis: list[str] = []
    for row in rows[1:]:
        ply, san, uci = row[7], row[8], row[9]
        try:
            move = board.parse_san(san)
        except ValueError as error:
            corrupted(f"ply {ply} SAN {san!r} does not parse: {error}")
        if board.san(move) != san or move.uci() != uci:
            corrupted(f"ply {ply} stored SAN/UCI {san!r}/{uci!r} is not canonical")
        board.push(move)
        state = tuple(row[12:16])
        if tuple(board.fen(en_passant="fen").split()[:4]) != state:
            corrupted(f"ply {ply} stored position state disagrees with replay")
        if board.halfmove_clock != row[10] or board.fullmove_number != row[11]:
            corrupted(f"ply {ply} stored clocks disagree with replay")
        sans.append(san)
        ucis.append(uci)

    if tuple(sans[: len(ROOT_PREFIX)]) != ROOT_PREFIX:
        return None
    return GameRecord(
        game_uuid,
        tuple(sans),
        tuple(ucis),
        classify_outcome(str(head[1]), str(head[2])),
        head[3],
        head[4],
        head[5],
        head[6],
    )


def load_replayed_games(
    connection: sqlite3.Connection, corpus_id: int, player_uuid: str
) -> tuple[int, list[GameRecord]]:
    rows = connection.execute(OCCURRENCE_QUERY, (corpus_id, player_uuid, player_uuid)).fetchall()
    candidate_count = len({row[0] for row in rows})
    records: list[GameRecord] = []
    for _game_uuid, grouped in groupby(rows, key=lambda row: row[0]):
        record = validate_game(list(grouped))
        if record is not None:
            records.append(record)
    return candidate_count, records


def load_source(path: Path) -> tuple[dict[str, Any], list[tuple[dict[str, Any], str | None]]]:
    with path.open("r", encoding="utf-8") as handle:
        source = json.load(handle)
    require(source.get("schema") == "caro-kann-history-tree/v1", "source schema changed")
    root = source.get("tree")
    require(isinstance(root, dict), "source tree is missing")
    require(root.get("moves_san") == list(ROOT_PREFIX), "source root prefix changed")
    require(root.get("games") == EXPECTED_ROOT_GAMES, "source root games changed")
    require(source.get("root_cohort", {}).get("total_games") == EXPECTED_ROOT_GAMES, "source root denominator changed")
    require(source.get("stats", {}).get("real_position_nodes") == EXPECTED_NODE_COUNT, "source node count metadata changed")

    nodes: list[tuple[dict[str, Any], str | None]] = []

    def walk(node: dict[str, Any], parent_id: str | None) -> None:
        node_id = node.get("node_id")
        require(isinstance(node_id, str), "source node has no stable ID")
        require(node_id == node_id_for(node["moves_san"]), f"source node ID disagrees for {node_id}")
        if parent_id is None:
            require(node.get("arrived_via") is None, "source root has an arrival edge")
        else:
            arrival = node.get("arrived_via")
            require(isinstance(arrival, dict), f"source child {node_id} has no arrival edge")
        nodes.append((node, parent_id))
        for child in node.get("children", []):
            walk(child, node_id)

    walk(root, None)
    require(len(nodes) == EXPECTED_NODE_COUNT, "source does not contain 229 nodes")
    require(len({node["node_id"] for node, _ in nodes}) == len(nodes), "source node IDs are not unique")

    observed_count = sum(len(node["observed_next_moves"]) for node, _ in nodes)
    unexpanded_count = 0
    for node, _parent_id in nodes:
        child_sans = {child["arrived_via"]["san"] for child in node["children"]}
        require(
            set(child_sans).issubset({edge["san"] for edge in node["observed_next_moves"]}),
            f"source child branches are not observed at {node['node_id']}",
        )
        unexpanded_count += sum(edge["san"] not in child_sans for edge in node["observed_next_moves"])
    require(observed_count == EXPECTED_BRANCH_COUNT, "source does not contain 863 observed branches")
    require(unexpanded_count == EXPECTED_UNEXPANDED_BRANCH_COUNT, "source does not contain 635 unexpanded branches")
    return source, nodes


def replay_prefix(sans: Iterable[str], ucis: Iterable[str] | None = None) -> tuple[chess.Board, tuple[str, ...]]:
    board = chess.Board()
    replayed_ucis: list[str] = []
    expected_ucis = tuple(ucis) if ucis is not None else None
    for index, san in enumerate(sans):
        try:
            move = board.parse_san(san)
        except ValueError as error:
            fail(f"prefix SAN {san!r} does not replay: {error}")
        require(board.san(move) == san, f"prefix SAN is not canonical at ply {index + 1}")
        move_uci = move.uci()
        if expected_ucis is not None:
            require(move_uci == expected_ucis[index], f"prefix UCI disagrees at ply {index + 1}")
        replayed_ucis.append(move_uci)
        board.push(move)
    return board, tuple(replayed_ucis)


def metric_core(counts: dict[str, int]) -> dict[str, Any]:
    counts = {key: int(counts[key]) for key in ("win", "draw", "loss", "unknown")}
    games = sum(counts.values())
    classifiable = counts["win"] + counts["draw"] + counts["loss"]
    raw_win = exact_pct(counts["win"], classifiable)
    score = exact_pct(2 * counts["win"] + counts["draw"], 2 * classifiable)
    interval: dict[str, Any] | None = None
    if classifiable:
        successes = 2 * counts["win"] + counts["draw"]
        trials = 2 * classifiable
        p = successes / trials
        z2 = WILSON_Z * WILSON_Z
        center = (p + z2 / (2 * trials)) / (1 + z2 / trials)
        half = WILSON_Z * ((p * (1 - p) / trials + z2 / (4 * trials * trials)) ** 0.5) / (
            1 + z2 / trials
        )
        interval = {
            "method": "95% Wilson-style heuristic on effective half-points; descriptive uncertainty, not a binomial claim",
            "z": WILSON_Z,
            "effective_successes_2W_plus_D": successes,
            "effective_trials_2_classifiable": trials,
            "lower_pct": max(0.0, 100.0 * (center - half)),
            "upper_pct": min(100.0, 100.0 * (center + half)),
        }
    return {
        "games": games,
        "outcomes": counts,
        "classifiable_games": classifiable,
        "raw_win_pct": raw_win,
        "chess_score_pct": score,
        "chess_score_pct_unrounded": score,
        "wilson_95_interval": interval,
    }


def add_extended_metrics(
    core: dict[str, Any],
    record_indexes: list[int],
    root_core: dict[str, Any],
    root_loss_count: int,
    root_total: int,
    parent_core: dict[str, Any] | None = None,
    sibling_indexes: list[int] | None = None,
    records: list[GameRecord] | None = None,
) -> dict[str, Any]:
    score = core["chess_score_pct_unrounded"]
    root_score = root_core["chess_score_pct_unrounded"]
    delta = None if score is None or root_score is None else score - root_score
    parent_delta = None
    if parent_core is not None and score is not None and parent_core["chess_score_pct_unrounded"] is not None:
        parent_delta = score - parent_core["chess_score_pct_unrounded"]
    sibling_comparison: dict[str, Any] | None = None
    if sibling_indexes is not None and records is not None:
        sibling_core = metric_core(outcome_counts(records, sibling_indexes))
        if sibling_core["classifiable_games"]:
            gap = None if score is None else score - sibling_core["chess_score_pct_unrounded"]
            sibling_comparison = {
                "games": sibling_core["games"],
                "outcomes": sibling_core["outcomes"],
                "classifiable_games": sibling_core["classifiable_games"],
                "chess_score_pct": sibling_core["chess_score_pct"],
                "chess_score_pct_unrounded": sibling_core["chess_score_pct_unrounded"],
                "wilson_95_interval": sibling_core["wilson_95_interval"],
                "branch_minus_other_siblings_gap_pp": gap,
            }
    impact = None if score is None or root_score is None else core["classifiable_games"] * (score - root_score) / 100.0
    shortfall = None if impact is None else max(0.0, -impact)
    return {
        **core,
        "below_50": score is not None and score < 50.0,
        "below_50_amount_pp": None if score is None else max(0.0, 50.0 - score),
        "delta_from_root_score_pp": delta,
        "move_branch_delta_from_parent_score_pp": parent_delta,
        "sibling_comparison": sibling_comparison,
        "root_reach_pct": exact_pct(core["games"], root_total),
        "loss_count": core["outcomes"]["loss"],
        "root_loss_share_pct": exact_pct(core["outcomes"]["loss"], root_loss_count),
        "score_point_impact_descriptive": impact,
        "below_baseline_shortfall_score_points": shortfall,
        "impact_label": "descriptive, noncausal, non-additive across nested records",
    }


def classify_indexes(records: list[GameRecord], indexes: list[int], attr: str, keys: tuple[str, ...]) -> dict[str, list[int]]:
    grouped = {key: [] for key in keys}
    for index in indexes:
        grouped[getattr(records[index], attr)].append(index)
    return grouped


def validate_core_metric(metric: dict[str, Any], counts: dict[str, int], label: str) -> None:
    expected = metric_core(counts)
    for key in (
        "games",
        "outcomes",
        "classifiable_games",
        "raw_win_pct",
        "chess_score_pct",
        "chess_score_pct_unrounded",
        "wilson_95_interval",
    ):
        require(metric.get(key) == expected[key], f"{label} metric field {key} is inconsistent")


def validate_slice_metrics(records: list[GameRecord], indexes: list[int], slices: dict[str, Any], label: str) -> None:
    validate_core_metric(slices["combined"], outcome_counts(records, indexes), f"{label} combined slice")
    specifications = (
        ("time_class", "time_class_key", TIME_CLASS_KEYS),
        ("recency", "recency_key", RECENCY_KEYS),
        ("opponent_strength", "strength_key", STRENGTH_KEYS),
    )
    for group_name, attr, keys in specifications:
        buckets = classify_indexes(records, indexes, attr, keys)
        for key in keys:
            validate_core_metric(
                slices[group_name][key],
                outcome_counts(records, buckets[key]),
                f"{label} {group_name}/{key} slice",
            )


def validate_extended_metrics(
    metrics: dict[str, Any],
    core: dict[str, Any],
    indexes: list[int],
    root_core: dict[str, Any],
    root_loss_count: int,
    root_total: int,
    label: str,
    parent_core: dict[str, Any] | None = None,
    sibling_indexes: list[int] | None = None,
    records: list[GameRecord] | None = None,
) -> None:
    expected = add_extended_metrics(
        core,
        indexes,
        root_core,
        root_loss_count,
        root_total,
        parent_core=parent_core,
        sibling_indexes=sibling_indexes,
        records=records,
    )
    require(metrics == expected, f"{label} extended metric fields are inconsistent")


def make_slices(records: list[GameRecord], indexes: list[int]) -> dict[str, Any]:
    result: dict[str, Any] = {"combined": metric_core(outcome_counts(records, indexes))}
    specifications = (
        ("time_class", "time_class_key", TIME_CLASS_KEYS),
        ("recency", "recency_key", RECENCY_KEYS),
        ("opponent_strength", "strength_key", STRENGTH_KEYS),
    )
    for group_name, attr, keys in specifications:
        buckets = classify_indexes(records, indexes, attr, keys)
        result[group_name] = {
            key: metric_core(outcome_counts(records, bucket_indexes))
            for key, bucket_indexes in buckets.items()
        }
        require(
            sum(metric["games"] for metric in result[group_name].values()) == result["combined"]["games"],
            f"{group_name} slice games do not reconcile",
        )
        for outcome in ("win", "draw", "loss", "unknown"):
            require(
                sum(metric["outcomes"][outcome] for metric in result[group_name].values())
                == result["combined"]["outcomes"][outcome],
                f"{group_name} slice {outcome} outcomes do not reconcile",
            )
    return result


def engine_reference(fen: str, moves_uci: list[str]) -> dict[str, Any]:
    return {
        "fen": fen,
        "position_fen_command": f"position fen {fen}",
        "moves_uci": moves_uci,
        "engine_process_started": False,
    }


def validate_replayed_population(
    source: dict[str, Any],
    nodes: list[tuple[dict[str, Any], str | None]],
    root_records: list[GameRecord],
) -> tuple[dict[str, list[int]], list[dict[str, Any]], dict[str, list[int]]]:
    require(len(root_records) == EXPECTED_ROOT_GAMES, "replay root games are not 3,358")
    root_outcomes = outcome_counts(root_records, range(len(root_records)))
    require(root_outcomes == EXPECTED_ROOT_OUTCOMES, "replay root outcomes changed")
    require(all(record.sans[:2] == ROOT_PREFIX for record in root_records), "a root game does not start exactly e4 c6")
    root_ucis = root_records[0].ucis[:2]
    require(all(record.ucis[:2] == root_ucis for record in root_records), "root UCI prefixes disagree")

    prefix_members: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for index, record in enumerate(root_records):
        for length in range(len(ROOT_PREFIX), len(record.sans) + 1):
            prefix_members[record.sans[:length]].append(index)

    node_members: dict[str, list[int]] = {}
    branch_specs: list[dict[str, Any]] = []
    branch_members: dict[str, list[int]] = {}
    seen_branch_ids: set[str] = set()

    for node, parent_id in nodes:
        node_id = node["node_id"]
        sans = tuple(node["moves_san"])
        ucis = tuple(node["moves_uci"])
        require(sans in prefix_members, f"source node {node_id} has no replay members")
        member_indexes = prefix_members[sans]
        node_members[node_id] = member_indexes
        counts = outcome_counts(root_records, member_indexes)
        require(len(member_indexes) == node["games"], f"node {node_id} replay membership count differs")
        require(counts == node["outcomes"], f"node {node_id} replay outcomes differ")
        require(node["classifiable_games"] == sum(counts[key] for key in ("win", "draw", "loss")), f"node {node_id} classifiable count differs")
        require(sum(edge["count"] for edge in node["observed_next_moves"]) == node["games_with_next"], f"node {node_id} observed next counts do not partition")
        expected_next = {index for index in member_indexes if len(root_records[index].sans) > len(sans)}
        require(len(expected_next) == node["games_with_next"], f"node {node_id} games_with_next differs on replay")

        board, replayed_ucis = replay_prefix(sans, ucis)
        require(tuple(replayed_ucis) == ucis, f"node {node_id} UCI prefix does not replay")
        require(board.fen(en_passant="fen") == node["fen"], f"node {node_id} FEN does not replay")
        expected_side = "white" if board.turn == chess.WHITE else "black"
        require(node["side_to_move"] == expected_side, f"node {node_id} side does not replay")
        if parent_id is not None:
            parent = next(parent_node for parent_node, parent_parent in nodes if parent_node["node_id"] == parent_id)
            require(tuple(sans[:-1]) == tuple(parent["moves_san"]), f"node {node_id} parent prefix differs")

        child_by_san = {child["arrived_via"]["san"]: child for child in node["children"]}
        represented_indexes: set[int] = set()
        for edge in node["observed_next_moves"]:
            edge_san = edge["san"]
            full_sans = (*sans, edge_san)
            members = prefix_members.get(full_sans, [])
            branch_id = branch_id_for(full_sans)
            require(branch_id not in seen_branch_ids, f"duplicate branch ID {branch_id}")
            seen_branch_ids.add(branch_id)
            require(len(members) == edge["count"], f"branch {branch_id} replay membership count differs")
            require(all(root_records[index].ucis[len(sans)] == edge["uci"] for index in members), f"branch {branch_id} UCI membership differs")
            represented_indexes.update(members)
            branch_board, full_ucis = replay_prefix(full_sans, (*ucis, edge["uci"]))
            child = child_by_san.get(edge_san)
            if child is not None:
                require(child["node_id"] == node_id_for(full_sans), f"child ID does not match branch {branch_id}")
                require(child["games"] == edge["count"], f"child count does not match branch {branch_id}")
                require(set(members) == set(node_members.get(child["node_id"], members)), f"child membership differs for branch {branch_id}")
            expected_actor = "White opponent" if node["side_to_move"] == "white" else "Black Skyrocoster"
            branch_members[branch_id] = members
            branch_specs.append(
                {
                    "branch_id": branch_id,
                    "parent_node_id": node_id,
                    "child_node_id": child["node_id"] if child is not None else None,
                    "branch_status": "expanded_child" if child is not None else "unexpanded_observed_move",
                    "parent_sans": sans,
                    "parent_ucis": ucis,
                    "parent_fen": node["fen"],
                    "parent_side_to_move": node["side_to_move"],
                    "parent_games_with_next": node["games_with_next"],
                    "full_sans": full_sans,
                    "full_ucis": full_ucis,
                    "line": format_line(full_sans),
                    "fen": branch_board.fen(en_passant="fen"),
                    "side_to_move": "white" if branch_board.turn == chess.WHITE else "black",
                    "actor": expected_actor,
                    "move_san": edge_san,
                    "move_uci": edge["uci"],
                    "source_edge": edge,
                    "member_indexes": members,
                }
            )
        require(represented_indexes == expected_next, f"node {node_id} branches do not partition games_with_next")

    require(len(node_members) == EXPECTED_NODE_COUNT, "replay did not cover all source nodes")
    require(len(branch_specs) == EXPECTED_BRANCH_COUNT, "replay did not cover all source branches")
    require(sum(spec["branch_status"] == "unexpanded_observed_move" for spec in branch_specs) == EXPECTED_UNEXPANDED_BRANCH_COUNT, "replay unexpanded count differs")
    return node_members, branch_specs, branch_members


def build_records(
    nodes: list[tuple[dict[str, Any], str | None]],
    branch_specs: list[dict[str, Any]],
    node_members: dict[str, list[int]],
    records: list[GameRecord],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    root_indexes = node_members[nodes[0][0]["node_id"]]
    root_core = metric_core(outcome_counts(records, root_indexes))
    root_loss_count = root_core["outcomes"]["loss"]
    node_cores: dict[str, dict[str, Any]] = {}
    for node, _parent_id in nodes:
        node_cores[node["node_id"]] = metric_core(outcome_counts(records, node_members[node["node_id"]]))

    position_records: list[dict[str, Any]] = []
    for node, parent_id in nodes:
        node_id = node["node_id"]
        indexes = node_members[node_id]
        core = node_cores[node_id]
        metrics = add_extended_metrics(core, indexes, root_core, root_loss_count, len(root_indexes), records=records)
        slices = make_slices(records, indexes)
        validate_extended_metrics(metrics, core, indexes, root_core, root_loss_count, len(root_indexes), f"node {node_id}", records=records)
        validate_slice_metrics(records, indexes, slices, f"node {node_id}")
        position_records.append(
            {
                "record_type": "position_node",
                "node_id": node_id,
                "parent_node_id": parent_id,
                "line": node["line"],
                "moves_san": node["moves_san"],
                "moves_uci": node["moves_uci"],
                "ply": node["ply"],
                "fen": node["fen"],
                "side_to_move": node["side_to_move"],
                "engine_ready": engine_reference(node["fen"], node["moves_uci"]),
                "source": {
                    "games": node["games"],
                    "outcomes": node["outcomes"],
                    "games_with_next": node["games_with_next"],
                    "games_without_next": node["games_without_next"],
                    "tree_expansion": node["expansion"],
                    "stop_reason": node["stop_reason"],
                    "replayed_member_count": len(indexes),
                },
                "metrics": metrics,
                "slices": slices,
            }
        )

    branch_indexes_by_parent: dict[str, list[tuple[str, list[int]]]] = defaultdict(list)
    for spec in branch_specs:
        branch_indexes_by_parent[spec["parent_node_id"]].append((spec["branch_id"], spec["member_indexes"]))

    branch_records: list[dict[str, Any]] = []
    for spec in branch_specs:
        parent_core = node_cores[spec["parent_node_id"]]
        indexes = spec["member_indexes"]
        branch_core = metric_core(outcome_counts(records, indexes))
        sibling_indexes = [
            index
            for other_branch_id, other_indexes in branch_indexes_by_parent[spec["parent_node_id"]]
            if other_branch_id != spec["branch_id"]
            for index in other_indexes
        ]
        metrics = add_extended_metrics(
            branch_core,
            indexes,
            root_core,
            root_loss_count,
            len(root_indexes),
            parent_core=parent_core,
            sibling_indexes=sibling_indexes,
            records=records,
        )
        slices = make_slices(records, indexes)
        validate_extended_metrics(
            metrics,
            branch_core,
            indexes,
            root_core,
            root_loss_count,
            len(root_indexes),
            f"branch {spec['branch_id']}",
            parent_core=parent_core,
            sibling_indexes=sibling_indexes,
            records=records,
        )
        validate_slice_metrics(records, indexes, slices, f"branch {spec['branch_id']}")
        branch_records.append(
            {
                "record_type": "move_branch",
                "branch_id": spec["branch_id"],
                "parent_node_id": spec["parent_node_id"],
                "child_node_id": spec["child_node_id"],
                "branch_status": spec["branch_status"],
                "actor": spec["actor"],
                "parent_line": format_line(spec["parent_sans"]),
                "parent_moves_san": list(spec["parent_sans"]),
                "parent_moves_uci": list(spec["parent_ucis"]),
                "parent_fen": spec["parent_fen"],
                "parent_side_to_move": spec["parent_side_to_move"],
                "line": spec["line"],
                "moves_san": list(spec["full_sans"]),
                "moves_uci": list(spec["full_ucis"]),
                "ply": len(spec["full_sans"]),
                "fen": spec["fen"],
                "side_to_move": spec["side_to_move"],
                "move": {"san": spec["move_san"], "uci": spec["move_uci"]},
                "engine_ready": engine_reference(spec["fen"], list(spec["full_ucis"])),
                "source": {
                    "games": branch_core["games"],
                    "outcomes": branch_core["outcomes"],
                    "tree_edge": spec["source_edge"],
                    "parent_games_with_next": spec["parent_games_with_next"],
                    "replayed_member_count": len(indexes),
                },
                "metrics": metrics,
                "slices": slices,
            }
        )

    root_summaries = {
        "combined": root_core,
        "time_class": {key: metric_core(outcome_counts(records, classify_indexes(records, root_indexes, "time_class_key", TIME_CLASS_KEYS)[key])) for key in TIME_CLASS_KEYS},
        "recency": {key: metric_core(outcome_counts(records, classify_indexes(records, root_indexes, "recency_key", RECENCY_KEYS)[key])) for key in RECENCY_KEYS},
        "opponent_strength": {key: metric_core(outcome_counts(records, classify_indexes(records, root_indexes, "strength_key", STRENGTH_KEYS)[key])) for key in STRENGTH_KEYS},
    }
    validate_core_metric(root_summaries["combined"], outcome_counts(records, root_indexes), "root combined")
    for group_name, attr, keys in (
        ("time_class", "time_class_key", TIME_CLASS_KEYS),
        ("recency", "recency_key", RECENCY_KEYS),
        ("opponent_strength", "strength_key", STRENGTH_KEYS),
    ):
        buckets = classify_indexes(records, root_indexes, attr, keys)
        for key in keys:
            validate_core_metric(root_summaries[group_name][key], outcome_counts(records, buckets[key]), f"root {group_name}/{key}")
    return position_records, branch_records, root_summaries


def metric_for_lens(record: dict[str, Any], lens: dict[str, Any]) -> tuple[float | None, dict[str, Any]]:
    metric = record["metrics"] if lens["slice_group"] is None else record["slices"][lens["slice_group"]][lens["slice_key"]]
    return metric.get(lens["metric_key"]), metric


LENSES: tuple[dict[str, Any], ...] = (
    {
        "id": "lowest_absolute_combined_score",
        "title": "Lowest absolute combined score",
        "slice_group": None,
        "slice_key": None,
        "metric_key": "chess_score_pct_unrounded",
        "metric_label": "combined chess score %",
        "direction": "ascending",
    },
    {
        "id": "largest_negative_delta_from_root",
        "title": "Largest negative delta from root",
        "slice_group": None,
        "slice_key": None,
        "metric_key": "delta_from_root_score_pp",
        "metric_label": "delta from root (pp)",
        "direction": "ascending",
    },
    {
        "id": "largest_negative_delta_from_parent",
        "title": "Largest negative delta from parent",
        "slice_group": None,
        "slice_key": None,
        "metric_key": "move_branch_delta_from_parent_score_pp",
        "metric_label": "delta from parent (pp)",
        "direction": "ascending",
    },
    {
        "id": "largest_negative_branch_vs_other_siblings_gap",
        "title": "Largest negative branch-versus-other-siblings gap",
        "slice_group": None,
        "slice_key": None,
        "metric_key": "sibling_comparison.branch_minus_other_siblings_gap_pp",
        "metric_label": "branch minus other siblings (pp)",
        "direction": "ascending",
    },
    {
        "id": "largest_root_baseline_shortfall",
        "title": "Largest nonnegative high-volume root-baseline shortfall",
        "slice_group": None,
        "slice_key": None,
        "metric_key": "below_baseline_shortfall_score_points",
        "metric_label": "below-baseline shortfall (score-points)",
        "direction": "descending",
    },
    {
        "id": "lowest_bullet_score",
        "title": "Lowest bullet score",
        "slice_group": "time_class",
        "slice_key": "bullet",
        "metric_key": "chess_score_pct_unrounded",
        "metric_label": "bullet chess score %",
        "direction": "ascending",
    },
    {
        "id": "lowest_blitz_score",
        "title": "Lowest blitz score",
        "slice_group": "time_class",
        "slice_key": "blitz",
        "metric_key": "chess_score_pct_unrounded",
        "metric_label": "blitz chess score %",
        "direction": "ascending",
    },
    {
        "id": "lowest_rapid_score",
        "title": "Lowest rapid score",
        "slice_group": "time_class",
        "slice_key": "rapid",
        "metric_key": "chess_score_pct_unrounded",
        "metric_label": "rapid chess score %",
        "direction": "ascending",
    },
    {
        "id": "lowest_recent_12_month_score",
        "title": "Lowest recent-12-month score",
        "slice_group": "recency",
        "slice_key": "recent_12_months",
        "metric_key": "chess_score_pct_unrounded",
        "metric_label": "recent-12-month chess score %",
        "direction": "ascending",
    },
    {
        "id": "lowest_older_score",
        "title": "Lowest older score",
        "slice_group": "recency",
        "slice_key": "older",
        "metric_key": "chess_score_pct_unrounded",
        "metric_label": "older chess score %",
        "direction": "ascending",
    },
    {
        "id": "lowest_stronger_opponent_score",
        "title": "Lowest stronger-opponent score",
        "slice_group": "opponent_strength",
        "slice_key": "stronger",
        "metric_key": "chess_score_pct_unrounded",
        "metric_label": "stronger-opponent chess score %",
        "direction": "ascending",
    },
    {
        "id": "lowest_similar_opponent_score",
        "title": "Lowest similar-opponent score",
        "slice_group": "opponent_strength",
        "slice_key": "similar",
        "metric_key": "chess_score_pct_unrounded",
        "metric_label": "similar-opponent chess score %",
        "direction": "ascending",
    },
    {
        "id": "lowest_weaker_opponent_score",
        "title": "Lowest weaker-opponent score",
        "slice_group": "opponent_strength",
        "slice_key": "weaker",
        "metric_key": "chess_score_pct_unrounded",
        "metric_label": "weaker-opponent chess score %",
        "direction": "ascending",
    },
)


def nested_metric_value(metrics: dict[str, Any], key: str) -> float | None:
    value: Any = metrics
    for part in key.split("."):
        if value is None:
            return None
        value = value.get(part)
    return value


def build_rankings(branch_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rankings: list[dict[str, Any]] = []
    for lens in LENSES:
        candidates: list[tuple[float, int, str, str, str, dict[str, Any], dict[str, Any]]] = []
        for record in branch_records:
            metric, metric_object = metric_for_lens(record, lens)
            if lens["slice_group"] is None and "." in lens["metric_key"]:
                metric = nested_metric_value(record["metrics"], lens["metric_key"])
            if metric is None:
                continue
            direction_value = metric if lens["direction"] == "ascending" else -metric
            candidates.append(
                (
                    direction_value,
                    -metric_object["games"],
                    record["line"],
                    record["move"]["san"],
                    record["move"]["uci"],
                    record,
                    metric_object,
                )
            )
        candidates.sort(key=lambda item: item[:5])
        rows: list[dict[str, Any]] = []
        for rank, (_sort_metric, _negative_games, _line, _san, _uci, record, metric_object) in enumerate(candidates[:10], 1):
            metric_value = metric_object.get(lens["metric_key"])
            if "." in lens["metric_key"]:
                metric_value = nested_metric_value(record["metrics"], lens["metric_key"])
            rows.append(
                {
                    "rank": rank,
                    "record_type": "move_branch",
                    "record_id": record["branch_id"],
                    "json_pointer": f"/move_branches/{branch_records.index(record)}",
                    "metric_key": lens["metric_key"],
                    "metric_value_unrounded": metric_value,
                    "sample_games": metric_object["games"],
                    "interval": metric_object["wilson_95_interval"],
                    "actor": record["actor"],
                    "line": record["line"],
                    "move_san": record["move"]["san"],
                    "move_uci": record["move"]["uci"],
                }
            )
        rankings.append(
            {
                "lens_id": lens["id"],
                "title": lens["title"],
                "metric_label": lens["metric_label"],
                "metric_key": lens["metric_key"],
                "slice_group": lens["slice_group"],
                "slice_key": lens["slice_key"],
                "direction": lens["direction"],
                "sample_filter": None,
                "ranking_tie_break": ["larger relevant slice sample", "complete exact SAN line", "move SAN", "move UCI"],
                "rows": rows,
            }
        )
    return rankings


def validate_rankings(rankings: list[dict[str, Any]], branch_records: list[dict[str, Any]]) -> None:
    by_id = {record["branch_id"]: record for record in branch_records}
    require(len(rankings) == 13, "ranking lens count is not 13")
    for ranking, lens in zip(rankings, LENSES):
        require(ranking["lens_id"] == lens["id"], f"ranking lens order changed for {lens['id']}")
        require(ranking["sample_filter"] is None, f"ranking {lens['id']} added a sample filter")
        require(len(ranking["rows"]) <= 10, f"ranking {lens['id']} has more than 10 rows")
        values: list[tuple[float, int, str, str, str]] = []
        for row in ranking["rows"]:
            record = by_id[row["record_id"]]
            metric, metric_object = metric_for_lens(record, lens)
            if "." in lens["metric_key"]:
                metric = nested_metric_value(record["metrics"], lens["metric_key"])
            require(metric is not None, f"ranking {lens['id']} retained a null metric")
            require(row["metric_value_unrounded"] == metric, f"ranking {lens['id']} metric display/reference differs")
            require(row["sample_games"] == metric_object["games"], f"ranking {lens['id']} sample differs")
            require(row["interval"] == metric_object["wilson_95_interval"], f"ranking {lens['id']} interval differs")
            require(row["line"] == record["line"], f"ranking {lens['id']} line reference differs")
            values.append(
                (
                    metric if lens["direction"] == "ascending" else -metric,
                    -metric_object["games"],
                    record["line"],
                    record["move"]["san"],
                    record["move"]["uci"],
                )
            )
        require(values == sorted(values), f"ranking {lens['id']} order is not deterministic")


def build_payload(
    source: dict[str, Any],
    source_path: Path,
    database_path: Path,
    database_hash: str,
    username: str,
    player_uuid: str,
    corpus_id: int,
    candidate_count: int,
    records: list[GameRecord],
    position_records: list[dict[str, Any]],
    branch_records: list[dict[str, Any]],
    root_summaries: dict[str, Any],
    rankings: list[dict[str, Any]],
) -> dict[str, Any]:
    actor_counts = {"White opponent": 0, "Black Skyrocoster": 0}
    for record in branch_records:
        actor_counts[record["actor"]] += 1
    root = root_summaries["combined"]
    root_indexes = list(range(root["games"]))
    dates = [records[index].date_utc for index in root_indexes if records[index].date_utc is not None]
    return {
        "schema": SCHEMA,
        "description": "Descriptive, noncanonical historical poor-results metrics for every exact Caro-Kann tree node and observed move branch; no move is labelled wrong or useful.",
        "generated_from": {
            "source_tree": {
                "path": display_path(source_path),
                "sha256": sha256_file(source_path),
                "schema": source["schema"],
            },
            "database": {
                "path": display_path(database_path),
                "sha256": database_hash,
                "access_mode": "read-only SQLite URI (mode=ro)",
            },
            "username_requested": "Skyrocoster",
            "username_resolved_case_insensitively": username,
            "player_uuid": player_uuid,
            "corpus_id": corpus_id,
            "player_color": "black",
            "rules_filter": "chess",
            "root_cohort_rule": "Tracked-corpus games where the resolved player is Black, not White, and exact opening plies from the initial board are SAN 1.e4 c6.",
            "candidate_black_games_fully_replayed": candidate_count,
            "root_games_fully_replayed": root["games"],
            "end_time_interpretation": "Unix end_time converted to a UTC calendar date",
            "engine_used": False,
            "engine_processes_started": 0,
        },
        "validation_expectations": {
            "root_games": EXPECTED_ROOT_GAMES,
            "root_outcomes_wdl_unknown": EXPECTED_ROOT_OUTCOMES,
            "position_nodes": EXPECTED_NODE_COUNT,
            "observed_move_branches": EXPECTED_BRANCH_COUNT,
            "unexpanded_move_entries": EXPECTED_UNEXPANDED_BRANCH_COUNT,
            "newest_root_date_utc": EXPECTED_NEWEST_DATE.isoformat(),
            "recency_cutoff_utc_inclusive": RECENCY_CUTOFF.isoformat(),
        },
        "record_counts": {
            "position_nodes": len(position_records),
            "move_branches": len(branch_records),
            "expanded_child_branches": sum(record["child_node_id"] is not None for record in branch_records),
            "unexpanded_move_entries": sum(record["child_node_id"] is None for record in branch_records),
            "actor_branch_records": actor_counts,
        },
        "root_cohort_summaries": root_summaries,
        "root_date_range_utc": {
            "oldest": min(dates).isoformat() if dates else None,
            "newest": max(dates).isoformat() if dates else None,
        },
        "metric_definitions": {
            "outcomes": "Whole-game outcomes from Skyrocoster's Black perspective; W/D/L plus unknown are retained.",
            "combined_all_time": "The combined slice is the all-time cohort for that record; time, recency, and opponent-strength slices reconcile to it.",
            "raw_win_pct": "100 * W / (W + D + L); unknown is excluded from classifiable denominators.",
            "chess_score_pct": "100 * (W + 0.5 * D) / (W + D + L).",
            "wilson_95_interval": "Deterministic exploratory Wilson-style interval on effective half-points: successes=2W+D, trials=2(W+D+L), z=1.959963984540054; null when classifiable outcomes are absent. It is a heuristic uncertainty display.",
            "below_50": "Combined or slice score is below 50%; below_50_amount_pp is the nonnegative percentage-point amount.",
            "delta_from_root_score_pp": "Signed record score minus the combined root score, in percentage points.",
            "move_branch_delta_from_parent_score_pp": "For a move branch, signed branch score minus its parent position score; null for position nodes.",
            "sibling_comparison": "For a move branch, the branch is compared with all other observed immediate moves at the same parent. The sibling is a pooled descriptive cohort; null when it has no classifiable outcomes.",
            "root_reach_pct": "100 * record games / 3,358 root games; nested records overlap.",
            "root_loss_share_pct": "100 * record losses / 1,570 root losses; nested records overlap.",
            "score_point_impact_descriptive": "classifiable_games * (record_score - root_score) / 100; descriptive, noncausal, and non-additive across nested records.",
            "below_baseline_shortfall_score_points": "max(0, -score_point_impact_descriptive); descriptive, noncausal, and non-additive across nested records.",
            "slices": "Time class is bullet, blitz, rapid, or other_or_unknown; recency uses UTC end_time with 2025-08-17 inclusive for recent_12_months; strength uses white_rating - black_rating: stronger >=100, similar >-100 and <100, weaker <=-100, unknown when either rating is missing.",
            "actor": "White moves are labelled White opponent; Black moves are labelled Black Skyrocoster.",
            "ranking": "All observed move branches are eligible with no sample filter. Null lens metrics are excluded only from that individual lens. Exact unrounded metric values rank first, then larger relevant slice sample, complete exact SAN line, move SAN, and move UCI.",
        },
        "warnings": [
            "All 229 position nodes and all 863 observed move branches are retained in JSON, including below-20 nodes and currently grouped/unexpanded moves.",
            "Tiny samples are included; the heuristic interval is visible and should not be read as a decision rule.",
            "Nested position and branch records overlap. Loss shares and score-point impacts cannot be summed across the tree.",
            "Outcomes are descriptive and noncausal. No metric decides usefulness or labels a move wrong.",
            "This report covers the current core only; secondary/long-tail tiers and engine analysis remain future work.",
            "Ranking views are separate descriptive lenses and do not produce a global recommendation.",
        ],
        "positions": position_records,
        "move_branches": branch_records,
        "rankings": rankings,
        "global_recommendation": None,
    }


def fmt(value: float | None, suffix: str = "") -> str:
    return "n/a" if value is None else f"{value:.2f}{suffix}"


def fmt_outcomes(metric: dict[str, Any]) -> str:
    outcomes = metric["outcomes"]
    return f"{outcomes['win']}-{outcomes['draw']}-{outcomes['loss']}/{outcomes['unknown']}"


def fmt_interval(interval: dict[str, Any] | None) -> str:
    if interval is None:
        return "n/a"
    return f"[{interval['lower_pct']:.2f}%, {interval['upper_pct']:.2f}%]"


def markdown_summary_table(name: str, metric_map: dict[str, dict[str, Any]]) -> list[str]:
    lines = [f"### {name}", "", "| Slice | n | W-D-L / unknown | Raw win | Chess score | 95% heuristic interval |", "|---|---:|---:|---:|---:|---:|"]
    for key, metric in metric_map.items():
        lines.append(
            f"| `{key}` | {metric['games']} | {fmt_outcomes(metric)} | {fmt(metric['raw_win_pct'], '%')} | {fmt(metric['chess_score_pct'], '%')} | {fmt_interval(metric['wilson_95_interval'])} |"
        )
    return lines + [""]


def build_markdown(payload: dict[str, Any]) -> str:
    generated = payload["generated_from"]
    counts = payload["record_counts"]
    root = payload["root_cohort_summaries"]
    lines = [
        "# Caro-Kann historical poor-results metrics",
        "",
        "**Noncanonical exploratory analysis. No engine was used. No metric is a recommendation, a usefulness decision, or a claim that a move is wrong.**",
        "",
        "## Scope and retained population",
        "",
        f"- Current core only: **{counts['position_nodes']} position nodes** and **{counts['move_branches']} observed move branches** are retained, including **{counts['unexpanded_move_entries']} unexpanded move entries** and tiny samples.",
        f"- Root cohort: {payload['root_cohort_summaries']['combined']['games']} tracked-corpus games where `{generated['username_resolved_case_insensitively']}` played Black and the exact opening was `1. e4 c6`.",
        f"- Branch actors are distinguished: `{counts['actor_branch_records']['White opponent']}` White-opponent branches and `{counts['actor_branch_records']['Black Skyrocoster']}` Black-Skyrocoster choices.",
        "- Every node and branch preserves its exact SAN/UCI prefix, replayed six-field FEN, side to move, and engine-ready `position fen` reference. This report does not start an engine.",
        "- Tiny samples are included rather than filtered; uncertainty is visible in every classifiable metric.",
        "",
        "## Source and root facts",
        "",
        f"- Database: `{generated['database']['path']}`; SQLite access was read-only (`mode=ro`). SHA-256: `{generated['database']['sha256']}`.",
        f"- Source tree: `{generated['source_tree']['path']}`; SHA-256: `{generated['source_tree']['sha256']}`.",
        f"- Candidate Black games fully replayed: {generated['candidate_black_games_fully_replayed']}; root games fully replayed: {generated['root_games_fully_replayed']}.",
        f"- Root W-D-L/unknown: **{fmt_outcomes(root['combined'])}**; chess score **{fmt(root['combined']['chess_score_pct'], '%')}**.",
        f"- UTC newest root date: **{payload['root_date_range_utc']['newest']}**. Recency cutoff: **{RECENCY_CUTOFF.isoformat()}**, inclusive for recent games; earlier dates are older.",
        "",
    ]
    lines.extend(markdown_summary_table("Root time-class summary", root["time_class"]))
    lines.extend(markdown_summary_table("Root recency summary", root["recency"]))
    lines.extend(markdown_summary_table("Root opponent-strength summary", root["opponent_strength"]))
    lines.extend(
        [
            "## Metric definitions and boundaries",
            "",
            "- Combined/all-time raw win is `100 * W / (W + D + L)`; chess score is `100 * (W + 0.5 * D) / (W + D + L)`. Unknown outcomes stay outside classifiable denominators.",
            "- The 95% interval is a deterministic **Wilson-style heuristic** on effective half-points: successes `2W + D`, trials `2(W + D + L)`, and `z=1.959963984540054`. It is null when no classifiable outcome exists.",
            "- Root and parent deltas are signed percentage-point differences. Branch sibling comparisons pool all other observed moves at that parent.",
            "- Root reach, root-loss share, and score-point impact are descriptive. Records are nested and overlap, so loss shares and impacts are not additive across the tree.",
            "- Outcomes are descriptive and noncausal. The individual ranking lenses below do not decide whether a move is useful or wrong.",
            "- Strength is based on `white_rating - black_rating`: stronger `>=100`, similar `>-100 and <100`, weaker `<=-100`, unknown if either rating is missing. Time classes are bullet, blitz, rapid, and other/unknown.",
            "- Secondary/long-tail tiers and engine analysis remain future work.",
            "",
            "## Top-10 branch views",
            "",
            "Each view ranks **all observed move branches with no sample filter**. Null lens metrics are excluded only from that individual view. Ranking uses the exact unrounded metric, then larger relevant slice `n`, complete exact SAN line, move SAN, and move UCI. These are separate tables, not a global recommendation.",
            "",
        ]
    )
    for ranking in payload["rankings"]:
        lines.extend(
            [
                f"### {ranking['title']}",
                "",
                f"Metric: `{ranking['metric_label']}`; direction: **{ranking['direction']}**; sample filter: **none**.",
                "",
                "| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |",
                "|---:|---:|---:|---|---|---|---|",
            ]
        )
        for row in ranking["rows"]:
            unit = (
                "%"
                if "score %" in ranking["metric_label"]
                else " score-points"
                if "score-points" in ranking["metric_label"]
                else " pp"
            )
            lines.append(
                f"| {row['rank']} | {fmt(row['metric_value_unrounded'], unit)} | {row['sample_games']} | {fmt_interval(row['interval'])} | {row['actor']} | `{row['line']}` | `{row['move_san']} / {row['move_uci']}` |"
            )
        if not ranking["rows"]:
            lines.append("| — | no classifiable slice metric | — | n/a | — | — | — |")
        lines.append("")
    lines.extend(
        [
            "## Limitations",
            "",
            "This is current-core historical cohort reporting only. It does not establish causality, move quality, usefulness, or a training recommendation. Nested records overlap, the intervals are heuristic, and engine analysis plus secondary/long-tail coverage are intentionally future work.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(json_path: Path, markdown_path: Path, payload: dict[str, Any]) -> None:
    rendered_json = json.dumps(payload, indent=2, ensure_ascii=True) + "\n"
    rendered_markdown = build_markdown(payload)
    with json_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered_json)
    with markdown_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered_markdown)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    parser.add_argument("--username", default="Skyrocoster")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_path = ensure_experiment_path(args.source, "source")
    json_path = ensure_experiment_path(args.json_output, "JSON output")
    markdown_path = ensure_experiment_path(args.markdown_output, "Markdown output")
    database_path = args.database.resolve()
    require(args.username.casefold() == "skyrocoster", "this approved analysis is fixed to Skyrocoster")
    source, nodes = load_source(source_path)
    source_hash = sha256_file(source_path)

    database_hash_before = sha256_file(database_path)
    connection = sqlite3.connect(f"{database_path.as_uri()}?mode=ro", uri=True)
    try:
        player_uuid, username, corpus_id = tree_builder.resolve_corpus_player(connection, args.username)
        candidate_count, validated_records = load_replayed_games(connection, corpus_id, player_uuid)
    finally:
        connection.close()
    database_hash_after = sha256_file(database_path)
    require(database_hash_before == database_hash_after, "database hash changed during read-only replay")
    require(candidate_count == EXPECTED_CANDIDATE_GAMES, "candidate game count changed")
    root_records = [record for record in validated_records if record.sans[:2] == ROOT_PREFIX]
    require(max(record.date_utc for record in root_records if record.date_utc is not None) == EXPECTED_NEWEST_DATE, "newest root cohort date changed")
    require(sum(record.time_class_key == "bullet" for record in root_records) == 1346, "root bullet dimension changed")
    require(sum(record.time_class_key == "blitz" for record in root_records) == 1463, "root blitz dimension changed")
    require(sum(record.time_class_key == "rapid" for record in root_records) == 544, "root rapid dimension changed")
    require(sum(record.time_class_key == "other_or_unknown" for record in root_records) == 5, "root other/unknown time dimension changed")
    require(sum(record.recency_key == "recent_12_months" for record in root_records) + sum(record.recency_key == "older" for record in root_records) + sum(record.recency_key == "date_unknown" for record in root_records) == EXPECTED_ROOT_GAMES, "root recency buckets do not reconcile")
    require(sum(record.strength_key == "stronger" for record in root_records) == 29, "root stronger dimension changed")
    require(sum(record.strength_key == "similar" for record in root_records) == 3325, "root similar dimension changed")
    require(sum(record.strength_key == "weaker" for record in root_records) == 4, "root weaker dimension changed")

    node_members, branch_specs, _branch_members = validate_replayed_population(source, nodes, root_records)
    position_records, branch_records, root_summaries = build_records(nodes, branch_specs, node_members, root_records)
    require(root_summaries["combined"]["outcomes"] == EXPECTED_ROOT_OUTCOMES, "generated root outcomes changed")
    rankings = build_rankings(branch_records)
    validate_rankings(rankings, branch_records)
    payload = build_payload(
        source,
        source_path,
        database_path,
        database_hash_before,
        username,
        player_uuid,
        corpus_id,
        candidate_count,
        root_records,
        position_records,
        branch_records,
        root_summaries,
        rankings,
    )
    require(payload["generated_from"]["source_tree"]["sha256"] == source_hash, "source hash changed during run")
    write_outputs(json_path, markdown_path, payload)
    print(
        f"Validated {len(position_records)} position nodes, {len(branch_records)} observed move branches "
        f"({payload['record_counts']['unexpanded_move_entries']} unexpanded); root {EXPECTED_ROOT_GAMES} games."
    )
    print(f"Database read-only/hash stable: {database_hash_before}")
    print("Engine processes started: 0")
    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {markdown_path}")


if __name__ == "__main__":
    main()
