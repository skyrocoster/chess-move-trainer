"""Read-only aggregate proof helpers for the DB-09 boundary."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import chess
from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..games.reading import GameReadRepository
from ..openings.recognition import lookup_fen, replay_pgn
from ..openings.source import OpeningRouteSource, load_opening_sources
from ..positions import canonicalize_board
from ..schema import _assert_compatible_schema
from ..statistics import MoveResponseDistributionReader, PositionContextReader
DEFAULT_DATABASE_PATH = Path("data/database/chess.db")
DB09_TABLE_NAMES = (
    "datasource_game",
    "datasource_opening",
    "datasource_preferred_move_period",
    "derived_analysis_line",
    "derived_analysis_queue",
    "derived_analysis_result",
    "derived_game_position",
    "derived_opening_route",
    "derived_opening_route_move",
    "derived_position",
)


class Db09PreflightError(ValueError):
    """Raised when fixed DB-09 proof inputs are unavailable or unsafe."""


@dataclass(frozen=True, slots=True)
class Db09Verification:
    """Aggregate integrity facts for the fixed database proof target."""

    database_path: Path
    schema_compatible: bool
    user_version: int | None
    integrity_result: str
    foreign_key_errors: tuple[str, ...]
    opening_count: int
    opening_route_count: int
    opening_move_count: int
    position_count: int
    game_count: int
    game_position_count: int

    @property
    def openings_ready(self) -> bool:
        """Whether the opening catalogue has its required data."""

        return (
            self.opening_count > 0
            and self.opening_route_count > 0
            and self.opening_move_count > 0
            and self.position_count > 0
        )

    @property
    def games_ready(self) -> bool:
        """Whether imported games and occurrences are present."""

        return self.game_count > 0 and self.game_position_count > 0

    @property
    def complete(self) -> bool:
        """Whether the fixed database passes the aggregate readiness checks."""

        return (
            self.schema_compatible
            and self.integrity_result.lower() == "ok"
            and not self.foreign_key_errors
            and self.openings_ready
            and self.games_ready
        )


@dataclass(frozen=True, slots=True)
class QueryPlanMeasurement:
    """Aggregate query-plan and elapsed-time evidence without row data."""

    name: str
    plan: tuple[str, ...]
    elapsed_seconds: tuple[float, ...]
    result_row_count: int

    @property
    def repetitions(self) -> int:
        """Return the number of timed executions represented by this value."""

        return len(self.elapsed_seconds)


MeasurementDecision = Literal["NO-INDEX", "INDEX-JUSTIFIED", "ESCALATED"]


@dataclass(frozen=True, slots=True)
class Db09MeasurementCorpus:
    """Aggregate corpus counts used as the basis for access measurements."""

    database_count: int
    game_count: int
    position_count: int
    occurrence_count: int
    analysis_result_count: int
    analysis_line_count: int


@dataclass(frozen=True, slots=True)
class Db09Measurements:
    """Privacy-safe, repeatable access-path evidence for the fixed database."""

    database_path: Path
    corpus: Db09MeasurementCorpus
    measurements: tuple[QueryPlanMeasurement, ...]
    index_decision: MeasurementDecision
    index_table: str | None
    index_columns: tuple[str, ...]
    decision_reason: str


@dataclass(frozen=True, slots=True)
class Db09Proof:
    """Read-only aggregate facts suitable for bounded DB-09 evidence."""

    database_path: Path
    verification: Db09Verification
    table_names: tuple[str, ...]
    table_counts: tuple[tuple[str, int], ...]
    preference_row_count: int
    analysis_result_count: int
    analysis_line_count: int
    game_occurrence_invariant_violations: int
    opening_route_invariant_violations: int
    measurements: tuple[QueryPlanMeasurement, ...]

    @property
    def preferences_empty(self) -> bool:
        """Whether the retained canonical preference table is empty."""

        return self.preference_row_count == 0

    @property
    def exact_ten_table_schema(self) -> bool:
        """Whether the fixed database exposes exactly the catalogue's ten tables."""

        return self.table_names == DB09_TABLE_NAMES

    @property
    def game_occurrences_valid(self) -> bool:
        """Whether every stored game has a complete ordered occurrence set."""

        return self.game_occurrence_invariant_violations == 0

    @property
    def opening_routes_valid(self) -> bool:
        """Whether every stored route has contiguous one-based move plies."""

        return self.opening_route_invariant_violations == 0


@dataclass(frozen=True, slots=True)
class Db09DirectCapabilities:
    """Aggregate-only facts from the real direct-capability proof."""

    real_game_metadata_complete: bool
    real_game_occurrence_count: int
    real_game_final_occurrence_present: bool
    context_all_game_count: int
    context_white_game_count: int
    context_black_game_count: int
    actor_occurrence_count: int
    actor_played_occurrence_count: int
    actor_final_occurrence_count: int
    actor_outgoing_move_kind_count: int
    actor_my_choice_count: int
    actor_opponent_response_count: int
    final_position_final_occurrence_count: int
    opening_ordered_recognition_count: int
    opening_current_after_departure: bool
    opening_route_match_proven: bool
    opening_transposition_match_proven: bool
    opening_fen_clock_insensitive: bool
    opening_future_variation_excluded: bool


_MEASUREMENT_REPETITIONS = 3
_MEASUREMENT_PAGE_SIZE = 100
_GAME_READ_STATEMENT = """
    SELECT
        g.dg_game_id,
        g.dg_chesscom_game_uuid,
        g.dg_source_url,
        g.dg_original_pgn,
        g.dg_trainer_color,
        g.dg_trainer_chesscom_uuid,
        g.dg_opponent_chesscom_uuid,
        g.dg_trainer_rating,
        g.dg_opponent_rating,
        g.dg_started_at_utc,
        g.dg_ended_at_utc,
        g.dg_trainer_outcome,
        g.dg_termination_reason,
        g.dg_time_control_source,
        g.dg_time_class,
        o.dgp_ply,
        o.derived_position_id,
        o.dgp_move_uci,
        o.dgp_halfmove_clock,
        o.dgp_fullmove_number,
        p.dp_placement,
        p.dp_side_to_move,
        p.dp_castling_rights,
        p.dp_legal_en_passant
    FROM datasource_game AS g
    LEFT JOIN derived_game_position AS o
      ON o.datasource_game_id = g.dg_game_id
    LEFT JOIN derived_position AS p
      ON p.dp_position_id = o.derived_position_id
    WHERE g.dg_game_id = :game_id
    ORDER BY o.dgp_ply
"""
_POSITION_CONTEXT_STATEMENT = """
    SELECT COUNT(DISTINCT o.datasource_game_id)
    FROM derived_game_position AS o
    JOIN datasource_game AS g
      ON g.dg_game_id = o.datasource_game_id
    WHERE o.derived_position_id = :position_id
      AND (
          :trainer_color IS NULL
          OR g.dg_trainer_color = :trainer_color
      )
"""
_MOVE_RESPONSE_STATEMENT = """
    SELECT o.dgp_move_uci, p.dp_side_to_move, g.dg_trainer_color
    FROM derived_game_position AS o
    JOIN datasource_game AS g
      ON g.dg_game_id = o.datasource_game_id
    JOIN derived_position AS p
      ON p.dp_position_id = o.derived_position_id
    WHERE o.derived_position_id = :position_id
      AND (
          :trainer_color IS NULL
          OR g.dg_trainer_color = :trainer_color
      )
    ORDER BY o.datasource_game_id, o.dgp_ply
"""
_OPENING_ROUTE_STATEMENT = """
    SELECT r.dor_route_id, r.datasource_opening_id,
           r.derived_position_id, o.do_eco, o.do_name,
           p.dp_position_id, p.dp_placement, p.dp_side_to_move,
           p.dp_castling_rights, p.dp_legal_en_passant
    FROM derived_opening_route AS r
    LEFT JOIN datasource_opening AS o
      ON o.do_opening_id = r.datasource_opening_id
    LEFT JOIN derived_position AS p
      ON p.dp_position_id = r.derived_position_id
    ORDER BY r.dor_route_id
"""
_OPENING_ROUTE_MOVE_STATEMENT = """
    SELECT derived_opening_route_id, dorm_ply, dorm_move_uci
    FROM derived_opening_route_move
    ORDER BY derived_opening_route_id, dorm_ply
"""
_PREFERRED_POSITION_STATEMENT = """
    SELECT dp_position_id
    FROM derived_position
    WHERE dp_placement = :placement
      AND dp_side_to_move = :side_to_move
      AND dp_castling_rights = :castling_rights
      AND dp_legal_en_passant = :legal_en_passant
"""
_PREFERRED_SCHEDULE_STATEMENT = """
    SELECT dpm_effective_from, dpm_effective_until, dpm_move_uci
    FROM datasource_preferred_move_period
    WHERE derived_position_id = :position_id
    ORDER BY dpm_effective_from
"""
_ANALYSIS_RESULT_STATEMENT = """
    SELECT derived_position_id, dar_quality,
           dar_configuration_version, dar_settings_json,
           dar_engine_name, dar_engine_version, dar_terminal_kind
    FROM derived_analysis_result
    WHERE derived_position_id = :position_id
    ORDER BY CASE dar_quality
        WHEN 'browser' THEN 0 WHEN 'tool' THEN 1 END
"""
_ANALYSIS_LINE_STATEMENT = """
    SELECT dal_rank, dal_score_kind, dal_score_value,
           dal_wdl_wins, dal_wdl_draws, dal_wdl_losses,
           dal_pv_uci_json, dal_depth
    FROM derived_analysis_line
    WHERE derived_analysis_result_id = :position_id
    ORDER BY dal_rank
"""
_BULK_ROUTE_MOVE_STATEMENT = """
    SELECT r.dor_route_id, m.dorm_ply, m.dorm_move_uci
    FROM derived_opening_route AS r
    LEFT JOIN derived_opening_route_move AS m
      ON m.derived_opening_route_id = r.dor_route_id
    ORDER BY r.dor_route_id, m.dorm_ply
"""
_BULK_GAME_PAGE_FIRST_STATEMENT = """
    WITH game_counts AS (
        SELECT derived_position_id AS position_id,
               COUNT(*) AS occurrence_count
        FROM derived_game_position
        WHERE dgp_ply BETWEEN :min_ply AND :max_ply
        GROUP BY derived_position_id
    )
    SELECT gc.position_id, gc.occurrence_count,
           p.dp_placement, p.dp_side_to_move,
           p.dp_castling_rights, p.dp_legal_en_passant
    FROM game_counts AS gc
    JOIN derived_position AS p
      ON p.dp_position_id = gc.position_id
    ORDER BY gc.occurrence_count DESC, gc.position_id ASC
    LIMIT :page_size
"""
_BULK_GAME_PAGE_CURSOR_STATEMENT = """
    WITH game_counts AS (
        SELECT derived_position_id AS position_id,
               COUNT(*) AS occurrence_count
        FROM derived_game_position
        WHERE dgp_ply BETWEEN :min_ply AND :max_ply
        GROUP BY derived_position_id
    )
    SELECT gc.position_id, gc.occurrence_count,
           p.dp_placement, p.dp_side_to_move,
           p.dp_castling_rights, p.dp_legal_en_passant
    FROM game_counts AS gc
    JOIN derived_position AS p
      ON p.dp_position_id = gc.position_id
    WHERE gc.occurrence_count < :last_frequency
       OR (
           gc.occurrence_count = :last_frequency
           AND gc.position_id > :last_position_id
       )
    ORDER BY gc.occurrence_count DESC, gc.position_id ASC
    LIMIT :page_size
"""
_BULK_ELIGIBILITY_STATEMENT = """
    SELECT dar_quality, dar_configuration_version, dar_engine_version
    FROM derived_analysis_result
    WHERE derived_position_id = :position_id
"""


@dataclass(frozen=True, slots=True)
class _MeasurementInputs:
    game_id: int
    context_position_id: int
    position_identity: tuple[str, str, str, str]
    analysis_position_id: int
    bulk_cursor: tuple[int, int]


def _positive_scalar(value: object) -> int:
    if type(value) is not int or value < 1:
        raise Db09PreflightError("fixed DB-09 database lacks a usable proof input")
    return value


def _pgn_for_moves(moves_uci: tuple[str, ...]) -> str:
    board = chess.Board()
    tokens: list[str] = []
    for move_uci in moves_uci:
        try:
            move = chess.Move.from_uci(move_uci)
        except (TypeError, ValueError) as error:
            raise Db09PreflightError("opening source move could not be replayed") from error
        if move not in board.legal_moves:
            raise Db09PreflightError("opening source move is not legal")
        if board.turn is chess.WHITE:
            tokens.append(f"{board.fullmove_number}.")
        elif not tokens:
            tokens.append(f"{board.fullmove_number}...")
        tokens.append(board.san(move))
        board.push(move)
    if not tokens:
        raise Db09PreflightError("opening source route has no moves")
    return " ".join(tokens)


def _opening_label(item: object) -> tuple[str, str]:
    return (str(item.eco), str(item.name))


def _find_transposition_pair(
    routes: tuple[OpeningRouteSource, ...],
) -> tuple[OpeningRouteSource, tuple[str, ...]]:
    source_identities = {
        (route.eco, route.name, route.moves_uci) for route in routes
    }
    ordered = sorted(routes, key=lambda route: (len(route.moves_uci), route.eco, route.name))
    for route in ordered:
        for transposed_moves in _bounded_move_reorders(route.moves_uci):
            if (route.eco, route.name, transposed_moves) in source_identities:
                continue
            try:
                board = _board_for_moves(transposed_moves)
            except Db09PreflightError:
                continue
            if canonicalize_board(board) == route.endpoint_position:
                return route, transposed_moves
    raise Db09PreflightError("pinned opening source has no bounded transposition pair")


def _bounded_move_reorders(moves_uci: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    """Return bounded deterministic reorders of one pinned source route."""

    candidates: list[tuple[str, ...]] = []
    seen: set[tuple[str, ...]] = set()
    for start in range(len(moves_uci)):
        for destination in range(len(moves_uci)):
            if start == destination:
                continue
            reordered = list(moves_uci)
            moved = reordered.pop(start)
            reordered.insert(destination, moved)
            candidate = tuple(reordered)
            if candidate not in seen:
                seen.add(candidate)
                candidates.append(candidate)
    for first in range(len(moves_uci)):
        for second in range(first + 1, len(moves_uci)):
            if first % 2 != second % 2:
                continue
            reordered = list(moves_uci)
            reordered[first], reordered[second] = reordered[second], reordered[first]
            candidate = tuple(reordered)
            if candidate not in seen:
                seen.add(candidate)
                candidates.append(candidate)
    return tuple(candidates)


def _board_for_moves(moves_uci: tuple[str, ...]) -> chess.Board:
    board = chess.Board()
    for move_uci in moves_uci:
        try:
            move = chess.Move.from_uci(move_uci)
        except (TypeError, ValueError) as error:
            raise Db09PreflightError("opening source move could not be replayed") from error
        if move not in board.legal_moves:
            raise Db09PreflightError("opening source move is not legal")
        board.push(move)
    return board


def _find_nested_routes(
    routes: tuple[OpeningRouteSource, ...],
) -> tuple[OpeningRouteSource, OpeningRouteSource]:
    ordered = sorted(routes, key=lambda route: (len(route.moves_uci), route.eco, route.name))
    for deep in ordered:
        for prefix in ordered:
            if len(prefix.moves_uci) >= len(deep.moves_uci):
                continue
            if deep.moves_uci[: len(prefix.moves_uci)] != prefix.moves_uci:
                continue
            if _opening_label(prefix) == _opening_label(deep):
                continue
            return prefix, deep
    raise Db09PreflightError("pinned opening source has no bounded nested route pair")


def _collect_opening_capabilities(
    database_path: Path,
    opening_source_dir: Path,
) -> dict[str, object]:
    routes = load_opening_sources(opening_source_dir)
    transposition_route, transposed_moves = _find_transposition_pair(routes)
    exact = replay_pgn(database_path, _pgn_for_moves(transposition_route.moves_uci))
    transposed = replay_pgn(database_path, _pgn_for_moves(transposed_moves))
    route_match_proven = any(
        item.eco == transposition_route.eco
        and item.name == transposition_route.name
        and item.match == "route"
        for item in exact.recognized
    )
    transposition_match_proven = any(
        item.eco == transposition_route.eco
        and item.name == transposition_route.name
        and item.match == "transposition"
        for item in transposed.recognized
    )

    prefix, deep = _find_nested_routes(routes)
    partial = replay_pgn(database_path, _pgn_for_moves(prefix.moves_uci))
    deep_result = replay_pgn(database_path, _pgn_for_moves(deep.moves_uci))
    ordered_recognitions = tuple(item.ply for item in deep_result.recognized)
    if not ordered_recognitions or ordered_recognitions != tuple(sorted(ordered_recognitions)):
        raise Db09PreflightError("real opening recognitions are not ordered")
    future_variation_excluded = not any(
        item.eco == deep.eco and item.name == deep.name for item in partial.recognized
    )

    board = chess.Board()
    for move_uci in deep.moves_uci:
        board.push(chess.Move.from_uci(move_uci))
    departure = None
    for move in board.legal_moves:
        departed = replay_pgn(
            database_path,
            _pgn_for_moves((*deep.moves_uci, move.uci())),
        )
        if departed.current == deep_result.current:
            departure = departed
            break
    current_after_departure = (
        departure is not None
        and deep_result.current is not None
        and departure.current == deep_result.current
    )

    fields = deep.endpoint_fen.split()
    if len(fields) != 6:
        raise Db09PreflightError("pinned opening endpoint is not a complete FEN")
    clockless = lookup_fen(database_path, deep.endpoint_fen)
    clock_changed = lookup_fen(
        database_path,
        " ".join((*fields[:4], "99", "120")),
    )
    fen_clock_insensitive = tuple(
        (item.ply, item.eco, item.name, item.match)
        for item in clockless.recognized
    ) == tuple(
        (item.ply, item.eco, item.name, item.match)
        for item in clock_changed.recognized
    )

    if not route_match_proven or not transposition_match_proven:
        raise Db09PreflightError("real opening recognition did not distinguish route and transposition")
    if not current_after_departure or not fen_clock_insensitive or not future_variation_excluded:
        raise Db09PreflightError("real opening recognition meanings were not all proven")
    return {
        "opening_ordered_recognition_count": len(deep_result.recognized),
        "opening_current_after_departure": current_after_departure,
        "opening_route_match_proven": route_match_proven,
        "opening_transposition_match_proven": transposition_match_proven,
        "opening_fen_clock_insensitive": fen_clock_insensitive,
        "opening_future_variation_excluded": future_variation_excluded,
    }


def collect_db09_direct_capabilities(
    database_path: str | Path,
    opening_source_dir: str | Path,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> Db09DirectCapabilities:
    """Exercise real readers while retaining only bounded aggregate facts."""

    path = Path(database_path).expanduser().resolve(strict=False)
    source_dir = Path(opening_source_dir).expanduser().resolve(strict=False)
    try:
        with _open_connection(path, "read-only", lock_timeout) as connection:
            _assert_compatible_schema(connection, lock_timeout)
            game_id = _positive_scalar(
                connection.execute(
                    text(
                        """
                        SELECT g.dg_game_id
                        FROM datasource_game AS g
                        JOIN derived_game_position AS o
                          ON o.datasource_game_id = g.dg_game_id
                        GROUP BY g.dg_game_id
                        ORDER BY g.dg_game_id
                        LIMIT 1
                        """
                    )
                ).scalar_one_or_none()
            )
            context_position_id = _positive_scalar(
                connection.execute(
                    text(
                        """
                        SELECT o.derived_position_id
                        FROM derived_game_position AS o
                        JOIN datasource_game AS g
                          ON g.dg_game_id = o.datasource_game_id
                        GROUP BY o.derived_position_id
                        HAVING COUNT(DISTINCT CASE
                                   WHEN g.dg_trainer_color = 'white'
                                   THEN g.dg_game_id END) > 0
                           AND COUNT(DISTINCT CASE
                                   WHEN g.dg_trainer_color = 'black'
                                   THEN g.dg_game_id END) > 0
                        ORDER BY o.derived_position_id
                        LIMIT 1
                        """
                    )
                ).scalar_one_or_none()
            )
            actor_position_id = _positive_scalar(
                connection.execute(
                    text(
                        """
                        SELECT o.derived_position_id
                        FROM derived_game_position AS o
                        JOIN datasource_game AS g
                          ON g.dg_game_id = o.datasource_game_id
                        JOIN derived_position AS p
                          ON p.dp_position_id = o.derived_position_id
                        WHERE o.dgp_move_uci IS NOT NULL
                        GROUP BY o.derived_position_id
                        HAVING SUM(CASE
                                   WHEN (p.dp_side_to_move = 'w'
                                         AND g.dg_trainer_color = 'white')
                                     OR (p.dp_side_to_move = 'b'
                                         AND g.dg_trainer_color = 'black')
                                   THEN 1 ELSE 0 END) > 0
                           AND SUM(CASE
                                   WHEN (p.dp_side_to_move = 'w'
                                         AND g.dg_trainer_color = 'black')
                                     OR (p.dp_side_to_move = 'b'
                                         AND g.dg_trainer_color = 'white')
                                   THEN 1 ELSE 0 END) > 0
                        ORDER BY o.derived_position_id
                        LIMIT 1
                        """
                    )
                ).scalar_one_or_none()
            )
            final_position_id = _positive_scalar(
                connection.execute(
                    text(
                        """
                        SELECT o.derived_position_id
                        FROM derived_game_position AS o
                        WHERE o.dgp_move_uci IS NULL
                        GROUP BY o.derived_position_id
                        ORDER BY o.derived_position_id
                        LIMIT 1
                        """
                    )
                ).scalar_one_or_none()
            )
    except Exception as error:
        if isinstance(error, Db09PreflightError):
            raise
        raise Db09PreflightError(
            "real DB-09 direct-capability inputs could not be selected"
        ) from error

    game = GameReadRepository(path, lock_timeout=lock_timeout).read(game_id)
    if game is None or not game.occurrences:
        raise Db09PreflightError("real DB-09 game reconstruction returned no game")
    final_occurrence = game.occurrences[-1]
    if (
        tuple(item.ply for item in game.occurrences)
        != tuple(range(len(game.occurrences)))
        or final_occurrence.ply != len(game.occurrences) - 1
        or final_occurrence.move_uci is not None
        or any(item.move_uci is None for item in game.occurrences[:-1])
    ):
        raise Db09PreflightError("real game occurrences are not ordered with one final occurrence")
    metadata_complete = (
        game.game_id > 0
        and bool(game.source_url)
        and bool(game.original_pgn)
        and game.trainer_color in ("white", "black")
        and bool(game.trainer_chesscom_uuid)
    )

    context_reader = PositionContextReader(path, lock_timeout=lock_timeout)
    context_all = context_reader.read(context_position_id)
    context_white = context_reader.read(context_position_id, "white")
    context_black = context_reader.read(context_position_id, "black")

    distribution_reader = MoveResponseDistributionReader(path, lock_timeout=lock_timeout)
    actor_distribution = distribution_reader.read(actor_position_id)
    final_distribution = distribution_reader.read(final_position_id)
    actor_outgoing_count = sum(actor_distribution.outgoing_moves.values())
    actor_my_choice_count = sum(actor_distribution.my_choices.values())
    actor_opponent_count = sum(actor_distribution.opponent_responses.values())
    if (
        actor_distribution.occurrence_count <= 0
        or actor_distribution.final_occurrence_count < 0
        or actor_distribution.played_occurrence_count != actor_outgoing_count
        or actor_my_choice_count + actor_opponent_count != actor_outgoing_count
        or actor_my_choice_count <= 0
        or actor_opponent_count <= 0
        or final_distribution.final_occurrence_count <= 0
        or final_distribution.played_occurrence_count
        != sum(final_distribution.outgoing_moves.values())
    ):
        raise Db09PreflightError(
            "real DB-09 statistics did not preserve actor and final-occurrence meanings"
        )

    opening_facts = _collect_opening_capabilities(path, source_dir)
    return Db09DirectCapabilities(
        real_game_metadata_complete=metadata_complete,
        real_game_occurrence_count=len(game.occurrences),
        real_game_final_occurrence_present=final_occurrence.move_uci is None,
        context_all_game_count=context_all.distinct_game_count,
        context_white_game_count=context_white.distinct_game_count,
        context_black_game_count=context_black.distinct_game_count,
        actor_occurrence_count=actor_distribution.occurrence_count,
        actor_played_occurrence_count=actor_distribution.played_occurrence_count,
        actor_final_occurrence_count=actor_distribution.final_occurrence_count,
        actor_outgoing_move_kind_count=len(actor_distribution.outgoing_moves),
        actor_my_choice_count=actor_my_choice_count,
        actor_opponent_response_count=actor_opponent_count,
        final_position_final_occurrence_count=final_distribution.final_occurrence_count,
        **opening_facts,
    )


def collect_db09_measurements(
    database_path: str | Path,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    repetitions: int = _MEASUREMENT_REPETITIONS,
) -> Db09Measurements:
    """Measure the named clean-package SQL reads without retaining row data.

    The statements below intentionally mirror the SQL in the package-owned
    readers and selectors.  Inputs are selected inside the read-only
    connection and are never returned in the evidence value.
    """

    if type(repetitions) is not int or repetitions < 2:
        raise Db09PreflightError("measurement repetitions must be at least two")
    path = Path(database_path).expanduser().resolve(strict=False)
    measurements: list[QueryPlanMeasurement] = []
    try:
        with _open_connection(path, "read-only", lock_timeout) as connection:
            _assert_compatible_schema(connection, lock_timeout)
            corpus = _measurement_corpus(connection)
            inputs = _measurement_inputs(connection)

            measurements.extend(
                _measure_query(
                    connection,
                    "GameReadRepository.read",
                    _GAME_READ_STATEMENT,
                    {"game_id": inputs.game_id},
                    repetitions=repetitions,
                )
            )
            for color, label in (
                (None, "all"),
                ("white", "white"),
                ("black", "black"),
            ):
                parameters = {
                    "position_id": inputs.context_position_id,
                    "trainer_color": color,
                }
                measurements.extend(
                    _measure_query(
                        connection,
                        f"PositionContextReader.read/{label}",
                        _POSITION_CONTEXT_STATEMENT,
                        parameters,
                        repetitions=repetitions,
                    )
                )
                measurements.extend(
                    _measure_query(
                        connection,
                        f"MoveResponseDistributionReader.read/{label}",
                        _MOVE_RESPONSE_STATEMENT,
                        parameters,
                        repetitions=repetitions,
                    )
                )

            measurements.extend(
                _measure_query(
                    connection,
                    "openings.recognition/routes",
                    _OPENING_ROUTE_STATEMENT,
                    {},
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "openings.recognition/route-moves",
                    _OPENING_ROUTE_MOVE_STATEMENT,
                    {},
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "PreferredMoveRepository/find-position",
                    _PREFERRED_POSITION_STATEMENT,
                    {
                        "placement": inputs.position_identity[0],
                        "side_to_move": inputs.position_identity[1],
                        "castling_rights": inputs.position_identity[2],
                        "legal_en_passant": inputs.position_identity[3],
                    },
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "PreferredMoveRepository/load-schedule",
                    _PREFERRED_SCHEDULE_STATEMENT,
                    {"position_id": inputs.context_position_id},
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "AnalysisReadRepository/read-result",
                    _ANALYSIS_RESULT_STATEMENT,
                    {"position_id": inputs.analysis_position_id},
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "AnalysisReadRepository/read-lines",
                    _ANALYSIS_LINE_STATEMENT,
                    {"position_id": inputs.analysis_position_id},
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "BulkTargetSelector/load-route-moves",
                    _BULK_ROUTE_MOVE_STATEMENT,
                    {},
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "BulkTargetSelector/load-game-page/first",
                    _BULK_GAME_PAGE_FIRST_STATEMENT,
                    _bulk_page_parameters(),
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "BulkTargetSelector/load-game-page/cursor",
                    _BULK_GAME_PAGE_CURSOR_STATEMENT,
                    {
                        **_bulk_page_parameters(),
                        "last_frequency": inputs.bulk_cursor[0],
                        "last_position_id": inputs.bulk_cursor[1],
                    },
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "BulkTargetSelector/check-eligibility",
                    _BULK_ELIGIBILITY_STATEMENT,
                    {"position_id": inputs.analysis_position_id},
                    repetitions=repetitions,
                )
            )
    except Db09PreflightError:
        raise
    except Exception as error:
        raise Db09PreflightError(
            "real DB-09 query-plan measurements could not be collected"
        ) from error

    decision, index_table, index_columns, reason = _measurement_decision(measurements)
    return Db09Measurements(
        database_path=path,
        corpus=corpus,
        measurements=tuple(measurements),
        index_decision=decision,
        index_table=index_table,
        index_columns=index_columns,
        decision_reason=reason,
    )


def print_db09_measurements(report: Db09Measurements) -> None:
    """Print only aggregate measurement facts and normalized plan details."""

    corpus = report.corpus
    print(
        "DB09 measurement corpus: "
        f"databases={corpus.database_count}; games={corpus.game_count}; "
        f"positions={corpus.position_count}; occurrences={corpus.occurrence_count}; "
        f"analysis_results={corpus.analysis_result_count}; "
        f"analysis_lines={corpus.analysis_line_count}"
    )
    for measurement in report.measurements:
        elapsed_ms = tuple(value * 1000 for value in measurement.elapsed_seconds)
        print(
            f"DB09 measurement: operation={measurement.name}; "
            f"plan={' | '.join(measurement.plan)}; "
            f"result_rows={measurement.result_row_count}; "
            f"repetitions={measurement.repetitions}; "
            f"elapsed_ms_min={min(elapsed_ms):.3f}; "
            f"elapsed_ms_median={_median(elapsed_ms):.3f}; "
            f"elapsed_ms_max={max(elapsed_ms):.3f}"
        )
    index_description = (
        "none"
        if report.index_table is None
        else f"{report.index_table}({','.join(report.index_columns)})"
    )
    print(
        f"DB09 index decision: decision={report.index_decision}; "
        f"recommended_index={index_description}; reason={report.decision_reason}"
    )


def _measurement_corpus(connection: Any) -> Db09MeasurementCorpus:
    def count(table_name: str) -> int:
        return int(
            connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            .scalar_one()
        )

    return Db09MeasurementCorpus(
        database_count=1,
        game_count=count("datasource_game"),
        position_count=count("derived_position"),
        occurrence_count=count("derived_game_position"),
        analysis_result_count=count("derived_analysis_result"),
        analysis_line_count=count("derived_analysis_line"),
    )


def _measurement_inputs(connection: Any) -> _MeasurementInputs:
    game_id = _positive_scalar(
        connection.execute(
            text(
                """
                SELECT g.dg_game_id
                FROM datasource_game AS g
                JOIN derived_game_position AS o
                  ON o.datasource_game_id = g.dg_game_id
                GROUP BY g.dg_game_id
                ORDER BY g.dg_game_id
                LIMIT 1
                """
            )
        ).scalar_one_or_none()
    )
    context_position_id = _positive_scalar(
        connection.execute(
            text(
                """
                SELECT o.derived_position_id
                FROM derived_game_position AS o
                JOIN datasource_game AS g
                  ON g.dg_game_id = o.datasource_game_id
                GROUP BY o.derived_position_id
                HAVING COUNT(DISTINCT CASE
                           WHEN g.dg_trainer_color = 'white'
                           THEN g.dg_game_id END) > 0
                   AND COUNT(DISTINCT CASE
                           WHEN g.dg_trainer_color = 'black'
                           THEN g.dg_game_id END) > 0
                ORDER BY o.derived_position_id
                LIMIT 1
                """
            )
        ).scalar_one_or_none()
    )
    position_row = connection.execute(
        text(
            """
            SELECT dp_placement, dp_side_to_move,
                   dp_castling_rights, dp_legal_en_passant
            FROM derived_position
            ORDER BY dp_position_id
            LIMIT 1
            """
        )
    ).first()
    if position_row is None or any(not isinstance(value, str) for value in position_row):
        raise Db09PreflightError("fixed DB-09 database lacks a position identity")
    analysis_position_id = _positive_scalar(
        connection.execute(
            text(
                """
                SELECT derived_position_id
                FROM derived_analysis_result
                ORDER BY derived_position_id
                LIMIT 1
                """
            )
        ).scalar_one_or_none()
    )
    first_page = connection.execute(
        text(_BULK_GAME_PAGE_FIRST_STATEMENT),
        _bulk_page_parameters(),
    ).all()
    if not first_page:
        raise Db09PreflightError("fixed DB-09 database lacks a bulk target page")
    try:
        bulk_cursor = (int(first_page[-1][1]), int(first_page[-1][0]))
    except (IndexError, TypeError, ValueError) as error:
        raise Db09PreflightError("real DB-09 bulk target page is malformed") from error
    return _MeasurementInputs(
        game_id=game_id,
        context_position_id=context_position_id,
        position_identity=tuple(str(value) for value in position_row),
        analysis_position_id=analysis_position_id,
        bulk_cursor=bulk_cursor,
    )


def _bulk_page_parameters() -> dict[str, int]:
    return {"min_ply": 0, "max_ply": 19, "page_size": _MEASUREMENT_PAGE_SIZE}


def _measurement_decision(
    measurements: list[QueryPlanMeasurement],
) -> tuple[MeasurementDecision, str | None, tuple[str, ...], str]:
    position_reads = tuple(
        measurement
        for measurement in measurements
        if measurement.name.startswith(
            ("PositionContextReader.read/", "MoveResponseDistributionReader.read/")
        )
    )
    if any(_plan_scans_alias(measurement, "o") for measurement in position_reads):
        return (
            "INDEX-JUSTIFIED",
            "derived_game_position",
            ("derived_position_id", "datasource_game_id", "dgp_ply"),
            "PositionContextReader and MoveResponseDistributionReader each "
            "repeatably scan derived_game_position for one position lookup; "
            "one composite supporting index covers both direct paths. No timing "
            "threshold was used. Catalogue loads and the bounded first-20-ply "
            "bulk aggregate remain structurally appropriate scans.",
        )
    return (
        "NO-INDEX",
        None,
        (),
        "PK, UNIQUE, and existing supporting indexes serve the measured direct "
        "lookups; remaining scans load complete catalogues or bounded aggregates "
        "and are structurally appropriate. No timing threshold was used.",
    )


def _plan_scans_alias(measurement: QueryPlanMeasurement, alias: str) -> bool:
    prefix = f"SCAN {alias.upper()}"
    return any(detail.upper().startswith(prefix) for detail in measurement.plan)


def _median(values: tuple[float, ...]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def _verify_direct_database(path: Path, *, lock_timeout: float) -> Db09Verification:
    """Read aggregate verification facts from one already-created database."""

    try:
        with _open_connection(path, "read-only", lock_timeout) as connection:
            user_version = int(
                connection.execute(text("PRAGMA user_version")).scalar_one()
            )
            try:
                _assert_compatible_schema(connection, lock_timeout)
            except Exception:
                return Db09Verification(
                    database_path=path,
                    schema_compatible=False,
                    user_version=user_version,
                    integrity_result="unknown",
                    foreign_key_errors=(),
                    opening_count=0,
                    opening_route_count=0,
                    opening_move_count=0,
                    position_count=0,
                    game_count=0,
                    game_position_count=0,
                )

            integrity_result = str(
                connection.execute(text("PRAGMA integrity_check")).scalar_one()
            )
            foreign_key_errors = tuple(
                " ".join(str(value) for value in row)
                for row in connection.execute(text("PRAGMA foreign_key_check")).all()
            )
            counts = {
                name: int(
                    connection.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar_one()
                )
                for name in DB09_TABLE_NAMES
            }
            return Db09Verification(
                database_path=path,
                schema_compatible=True,
                user_version=user_version,
                integrity_result=integrity_result,
                foreign_key_errors=foreign_key_errors,
                opening_count=counts["datasource_opening"],
                opening_route_count=counts["derived_opening_route"],
                opening_move_count=counts["derived_opening_route_move"],
                position_count=counts["derived_position"],
                game_count=counts["datasource_game"],
                game_position_count=counts["derived_game_position"],
            )
    except Db09PreflightError:
        raise
    except Exception as error:
        raise Db09PreflightError("fixed DB-09 database could not be verified") from error


def collect_db09_proof(
    database_path: str | Path,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    explain_position_id: int | None = None,
) -> Db09Proof:
    """Collect aggregate integrity, emptiness, query-plan, and timing facts only."""

    path = Path(database_path).expanduser().resolve(strict=False)
    verification = _verify_direct_database(path, lock_timeout=lock_timeout)
    measurements: list[QueryPlanMeasurement] = []
    try:
        with _open_connection(path, "read-only", lock_timeout) as connection:
            _assert_compatible_schema(connection, lock_timeout)
            table_names = tuple(
                str(row[0])
                for row in connection.execute(
                    text(
                        """
                        SELECT name
                        FROM sqlite_master
                        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                        ORDER BY name
                        """
                    )
                ).all()
            )
            counts = tuple(
                (name, int(connection.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar_one()))
                for name in DB09_TABLE_NAMES
            )
            preference_count = dict(counts)["datasource_preferred_move_period"]
            analysis_result_count = dict(counts)["derived_analysis_result"]
            analysis_line_count = dict(counts)["derived_analysis_line"]
            game_occurrence_invariant_violations = int(
                connection.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM (
                            SELECT g.dg_game_id,
                                   COUNT(o.dgp_ply) AS occurrence_count,
                                   MIN(o.dgp_ply) AS first_ply,
                                   MAX(o.dgp_ply) AS last_ply,
                                   SUM(CASE WHEN o.dgp_move_uci IS NULL THEN 1 ELSE 0 END)
                                       AS final_count,
                                   MAX(
                                       CASE
                                           WHEN o.dgp_move_uci IS NULL THEN o.dgp_ply
                                           ELSE -1
                                       END
                                   ) AS final_ply,
                                   COUNT(
                                       CASE WHEN o.dgp_move_uci IS NOT NULL THEN 1 END
                                   ) AS outgoing_move_count
                            FROM datasource_game AS g
                            LEFT JOIN derived_game_position AS o
                              ON o.datasource_game_id = g.dg_game_id
                            GROUP BY g.dg_game_id
                            HAVING occurrence_count < 1
                                OR first_ply <> 0
                                OR occurrence_count <> last_ply + 1
                                OR final_count <> 1
                                OR final_ply <> last_ply
                                OR outgoing_move_count <> occurrence_count - 1
                        )
                        """
                    )
                ).scalar_one()
            )
            opening_route_invariant_violations = int(
                connection.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM (
                            SELECT r.dor_route_id,
                                   COUNT(m.dorm_ply) AS move_count,
                                   MIN(m.dorm_ply) AS first_ply,
                                   MAX(m.dorm_ply) AS last_ply,
                                   COUNT(DISTINCT m.dorm_ply) AS distinct_ply_count
                            FROM derived_opening_route AS r
                            LEFT JOIN derived_opening_route_move AS m
                              ON m.derived_opening_route_id = r.dor_route_id
                            GROUP BY r.dor_route_id
                            HAVING move_count < 1
                                OR first_ply <> 1
                                OR last_ply <> move_count
                                OR distinct_ply_count <> move_count
                        )
                        """
                    )
                ).scalar_one()
            )
            if explain_position_id is not None:
                if type(explain_position_id) is not int or explain_position_id < 1:
                    raise Db09PreflightError("explain_position_id must be a positive integer")
                measurements.extend(
                    _measure_query(
                        connection,
                        "position_context",
                        """
                        SELECT COUNT(DISTINCT o.datasource_game_id)
                        FROM derived_game_position AS o
                        JOIN datasource_game AS g
                          ON g.dg_game_id = o.datasource_game_id
                        WHERE o.derived_position_id = :position_id
                        """,
                        {"position_id": explain_position_id},
                    )
                )
                measurements.extend(
                    _measure_query(
                        connection,
                        "move_response_distribution",
                        """
                        SELECT o.dgp_move_uci, p.dp_side_to_move, g.dg_trainer_color
                        FROM derived_game_position AS o
                        JOIN datasource_game AS g
                          ON g.dg_game_id = o.datasource_game_id
                        JOIN derived_position AS p
                          ON p.dp_position_id = o.derived_position_id
                        WHERE o.derived_position_id = :position_id
                        """,
                        {"position_id": explain_position_id},
                    )
                )
                measurements.extend(
                    _measure_query(
                        connection,
                        "analysis_read",
                        """
                        SELECT r.derived_position_id, r.dar_quality, l.dal_rank
                        FROM derived_analysis_result AS r
                        LEFT JOIN derived_analysis_line AS l
                          ON l.derived_analysis_result_id = r.derived_position_id
                        WHERE r.derived_position_id = :position_id
                        ORDER BY CASE r.dar_quality
                            WHEN 'browser' THEN 0 WHEN 'tool' THEN 1 END,
                            l.dal_rank
                        """,
                        {"position_id": explain_position_id},
                    )
                )
    except Db09PreflightError:
        raise
    except Exception as error:
        raise Db09PreflightError("aggregate DB-09 proof could not be collected") from error

    return Db09Proof(
        database_path=path,
        verification=verification,
        table_names=table_names,
        table_counts=counts,
        preference_row_count=preference_count,
        analysis_result_count=analysis_result_count,
        analysis_line_count=analysis_line_count,
        game_occurrence_invariant_violations=game_occurrence_invariant_violations,
        opening_route_invariant_violations=opening_route_invariant_violations,
        measurements=tuple(measurements),
    )


def _measure_query(
    connection: Any,
    name: str,
    statement: str,
    parameters: dict[str, object],
    *,
    repetitions: int = 1,
) -> tuple[QueryPlanMeasurement, ...]:
    if type(repetitions) is not int or repetitions < 1:
        raise Db09PreflightError("measurement repetitions must be positive")
    plan_rows = connection.execute(
        text(f"EXPLAIN QUERY PLAN {statement}"), parameters
    ).all()
    elapsed_seconds: list[float] = []
    result_row_count: int | None = None
    for _ in range(repetitions):
        started = time.perf_counter()
        rows = connection.execute(text(statement), parameters).all()
        elapsed_seconds.append(time.perf_counter() - started)
        if result_row_count is None:
            result_row_count = len(rows)
        elif len(rows) != result_row_count:
            raise Db09PreflightError(
                f"measurement result count changed for {name}"
            )
    return (
        QueryPlanMeasurement(
            name=name,
            plan=tuple(" ".join(str(row[-1]).split()) for row in plan_rows),
            elapsed_seconds=tuple(elapsed_seconds),
            result_row_count=0 if result_row_count is None else result_row_count,
        ),
    )


__all__ = [
    "DEFAULT_DATABASE_PATH",
    "DB09_TABLE_NAMES",
    "Db09DirectCapabilities",
    "Db09MeasurementCorpus",
    "Db09Measurements",
    "Db09PreflightError",
    "Db09Proof",
    "Db09Verification",
    "QueryPlanMeasurement",
    "collect_db09_direct_capabilities",
    "collect_db09_measurements",
    "collect_db09_proof",
    "print_db09_measurements",
]
