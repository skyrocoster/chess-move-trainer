"""Persisted backend analysis contracts."""

from .errors import (
    AnalysisBusyError,
    AnalysisLockError,
    AnalysisSchemaError,
    AnalysisTimeoutError,
    AnalysisValidationError,
    EngineLifecycleError,
    StockfishSetupError,
)
from .locking import AnalysisRunLock
from .models import (
    AnalysisCandidate,
    AnalysisProfile,
    AnalysisResult,
    ResultEligibility,
    canonical_fen,
)
from .preflight import (
    CorpusPreflight,
    ProjectionBasis,
    build_preflight,
    load_projection_basis,
    run_read_only_preflight,
)
from .repository import AnalysisRepository
from .runner import (
    DEFAULT_WORKERS,
    MAX_WORKERS,
    BatchRunResult,
    InterruptController,
    run_all_positions,
    run_batch,
    run_selected_games,
)
from .schema import ANALYSIS_SCHEMA_VERSION, initialize_analysis_schema, require_analysis_schema
from .selection import (
    GameSelectionError,
    SelectedOccurrence,
    SelectedPosition,
    SelectionReport,
    select_all_positions,
    select_positions,
)

__all__ = [
    "ANALYSIS_SCHEMA_VERSION",
    "AnalysisBusyError",
    "AnalysisLockError",
    "AnalysisRunLock",
    "AnalysisCandidate",
    "AnalysisProfile",
    "AnalysisRepository",
    "AnalysisResult",
    "BatchRunResult",
    "CorpusPreflight",
    "DEFAULT_WORKERS",
    "AnalysisSchemaError",
    "AnalysisTimeoutError",
    "AnalysisValidationError",
    "EngineLifecycleError",
    "GameSelectionError",
    "InterruptController",
    "MAX_WORKERS",
    "ProjectionBasis",
    "ResultEligibility",
    "SelectedOccurrence",
    "SelectedPosition",
    "SelectionReport",
    "StockfishSetupError",
    "canonical_fen",
    "build_preflight",
    "initialize_analysis_schema",
    "load_projection_basis",
    "require_analysis_schema",
    "run_batch",
    "run_all_positions",
    "run_read_only_preflight",
    "run_selected_games",
    "select_all_positions",
    "select_positions",
]
