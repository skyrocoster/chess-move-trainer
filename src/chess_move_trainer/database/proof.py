"""Read-only aggregate proof helpers for the direct-database boundary.

Thin compatibility shim. Implementation lives in focused modules:
proof_models, proof_statements, proof_opening_helpers,
proof_capabilities, proof_measurements, proof_query, proof_verification.
"""

from __future__ import annotations

from .proof_capabilities import _collect_opening_capabilities, collect_direct_capabilities
from .proof_measurements import (
    _MEASUREMENT_PAGE_SIZE,
    _MEASUREMENT_REPETITIONS,
    _bulk_page_parameters,
    _measurement_corpus,
    _measurement_decision,
    _measurement_inputs,
    _median,
    _MeasurementInputs,
    _plan_scans_alias,
    collect_direct_measurements,
    print_direct_measurements,
)
from .proof_models import (
    DEFAULT_DATABASE_PATH,
    DIRECT_TABLE_NAMES,
    DirectCapabilities,
    DirectMeasurementCorpus,
    DirectMeasurements,
    DirectPreflightError,
    DirectProof,
    DirectVerification,
    MeasurementDecision,
    QueryPlanMeasurement,
)
from .proof_opening_helpers import (
    _board_for_moves,
    _bounded_move_reorders,
    _find_nested_routes,
    _find_transposition_pair,
    _opening_label,
    _pgn_for_moves,
    _positive_scalar,
)
from .proof_query import _measure_query
from .proof_statements import (
    _ANALYSIS_LINE_STATEMENT,
    _ANALYSIS_RESULT_STATEMENT,
    _BULK_ELIGIBILITY_STATEMENT,
    _BULK_GAME_PAGE_CURSOR_STATEMENT,
    _BULK_GAME_PAGE_FIRST_STATEMENT,
    _BULK_ROUTE_MOVE_STATEMENT,
    _GAME_READ_STATEMENT,
    _MOVE_RESPONSE_STATEMENT,
    _OPENING_ROUTE_MOVE_STATEMENT,
    _OPENING_ROUTE_STATEMENT,
    _POSITION_CONTEXT_STATEMENT,
    _PREFERRED_POSITION_STATEMENT,
    _PREFERRED_SCHEDULE_STATEMENT,
)
from .proof_verification import _verify_direct_database, collect_direct_proof

__all__ = [
    "DEFAULT_DATABASE_PATH",
    "DIRECT_TABLE_NAMES",
    "DirectCapabilities",
    "DirectMeasurementCorpus",
    "DirectMeasurements",
    "DirectPreflightError",
    "DirectProof",
    "DirectVerification",
    "QueryPlanMeasurement",
    "collect_direct_capabilities",
    "collect_direct_measurements",
    "collect_direct_proof",
    "print_direct_measurements",
]
