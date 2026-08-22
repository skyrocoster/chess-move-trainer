class AnalysisSchemaError(RuntimeError):
    """The independently versioned analysis schema is absent or incompatible."""


class AnalysisValidationError(ValueError):
    """An analysis profile or complete result violates the persistence contract."""


class AnalysisTimeoutError(TimeoutError):
    """A node-limited engine call exceeded its independent wall-clock watchdog."""


class EngineLifecycleError(RuntimeError):
    """A tracked engine process could not be started or stopped safely."""


class AnalysisLockError(RuntimeError):
    """Another top-level analysis operator owns the database lock."""


class AnalysisBusyError(RuntimeError):
    """A short coordinator SQLite transaction could not acquire its lock."""


class StockfishSetupError(RuntimeError):
    """Pinned Stockfish provisioning or executable verification failed safely."""
