"""Package-owned database connection services."""

from .connection import (
    DEFAULT_LOCK_TIMEOUT_SECONDS,
    AccessMode,
    ConnectionProbe,
    probe_connection,
)
from .inspection import (
    SchemaColumn,
    SchemaForeignKey,
    SchemaIndex,
    SchemaInspection,
    SchemaObject,
    SchemaTable,
    inspect_schema,
    render_schema_markdown,
)
from .publication import publish_schema
from .schema import SCHEMA_VERSION, SchemaCreationResult, SchemaIncompatibleError, create_schema

__all__ = [
    "AccessMode",
    "ConnectionProbe",
    "DEFAULT_LOCK_TIMEOUT_SECONDS",
    "SchemaColumn",
    "SchemaForeignKey",
    "SchemaIndex",
    "SchemaInspection",
    "SchemaObject",
    "SchemaTable",
    "SCHEMA_VERSION",
    "SchemaCreationResult",
    "SchemaIncompatibleError",
    "create_schema",
    "inspect_schema",
    "publish_schema",
    "probe_connection",
    "render_schema_markdown",
]
