"""Read-only aggregate proof helpers for the direct-database boundary.

Thin compatibility shim. Implementation lives in focused modules:
proof_models, proof_statements, proof_opening_helpers,
proof_capabilities, proof_measurements, proof_query, proof_verification.
"""

from __future__ import annotations

from .proof_capabilities import collect_direct_capabilities
from .lifecycle import HOST_SEED_DATABASE_PATH
from .proof_measurements import (
    collect_direct_measurements,
    print_direct_measurements,
)
from .proof_models import (
    DIRECT_TABLE_NAMES,
    DirectCapabilities,
    DirectMeasurementCorpus,
    DirectMeasurements,
    DirectPreflightError,
    DirectProof,
    DirectVerification,
    QueryPlanMeasurement,
)
from .proof_opening_helpers import _board_for_moves, _find_transposition_pair
from .proof_verification import collect_direct_proof

__all__ = [
    "HOST_SEED_DATABASE_PATH",
    "DIRECT_TABLE_NAMES",
    "DirectCapabilities",
    "DirectMeasurementCorpus",
    "DirectMeasurements",
    "DirectPreflightError",
    "DirectProof",
    "DirectVerification",
    "QueryPlanMeasurement",
    "_board_for_moves",
    "_find_transposition_pair",
    "collect_direct_capabilities",
    "collect_direct_measurements",
    "collect_direct_proof",
    "print_direct_measurements",
]
