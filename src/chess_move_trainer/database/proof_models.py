"""Read-only aggregate proof helpers for the direct-database boundary."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import chess
from sqlalchemy import text

from .connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from .games.reading import GameReadRepository
from .openings.recognition import lookup_fen, replay_pgn
from .openings.source import OpeningRouteSource, load_opening_sources
from .positions import canonicalize_board
from .schema import _assert_compatible_schema
from .statistics import MoveResponseDistributionReader, PositionContextReader


DEFAULT_DATABASE_PATH = Path("data/database/chess.db")
DIRECT_TABLE_NAMES = (
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



class DirectPreflightError(ValueError):
    """Raised when fixed direct proof inputs are unavailable or unsafe."""


@dataclass(frozen=True, slots=True)
class DirectVerification:
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
class DirectMeasurementCorpus:
    """Aggregate corpus counts used as the basis for access measurements."""

    database_count: int
    game_count: int
    position_count: int
    occurrence_count: int
    analysis_result_count: int
    analysis_line_count: int


@dataclass(frozen=True, slots=True)
class DirectMeasurements:
    """Privacy-safe, repeatable access-path evidence for the fixed database."""

    database_path: Path
    corpus: DirectMeasurementCorpus
    measurements: tuple[QueryPlanMeasurement, ...]
    index_decision: MeasurementDecision
    index_table: str | None
    index_columns: tuple[str, ...]
    decision_reason: str


@dataclass(frozen=True, slots=True)
class DirectProof:
    """Read-only aggregate facts suitable for bounded direct evidence."""

    database_path: Path
    verification: DirectVerification
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

        return self.table_names == DIRECT_TABLE_NAMES

    @property
    def game_occurrences_valid(self) -> bool:
        """Whether every stored game has a complete ordered occurrence set."""

        return self.game_occurrence_invariant_violations == 0

    @property
    def opening_routes_valid(self) -> bool:
        """Whether every stored route has contiguous one-based move plies."""

        return self.opening_route_invariant_violations == 0


@dataclass(frozen=True, slots=True)
class DirectCapabilities:
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


