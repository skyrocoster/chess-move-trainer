"""Package-owned Chess.com game acquisition and import contracts."""

from .configuration import (
    ACQUIRE_DEFAULT_DELAY_SECONDS,
    ACQUIRE_DEFAULT_TIMEOUT_SECONDS,
    AcquireConfiguration,
    GamesConfigurationError,
    ImportConfiguration,
    load_acquire_configuration,
    load_import_configuration,
)

__all__ = [
    "ACQUIRE_DEFAULT_DELAY_SECONDS",
    "ACQUIRE_DEFAULT_TIMEOUT_SECONDS",
    "AcquireConfiguration",
    "GamesConfigurationError",
    "ImportConfiguration",
    "load_acquire_configuration",
    "load_import_configuration",
]
