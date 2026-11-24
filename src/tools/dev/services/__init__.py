"""Docker Compose lifecycle for the persistent development services.

The live database lives in the ``chess-database`` volume; only ``setup_database``
may create it, and it refuses to run when the file already exists.

Modules: ``compose`` (commands, budgets, Docker preflight), ``workers`` (worker
mode, health), ``jobs`` (one-shot probe and update containers) and ``lifecycle``
(the ``sg dev`` actions). The public names are re-exported here.
"""

from __future__ import annotations

from tools.dev.services.compose import (
    compose,
    compose_command,
    require_docker,
    worker_compose,
)
from tools.dev.services.jobs import (
    budgeted_compose_run,
    live_database_exists,
    run_database_updates,
)
from tools.dev.services.lifecycle import (
    logs,
    rebuild,
    restart,
    setup_database,
    start,
    status,
    stop,
    update,
)
from tools.dev.services.workers import (
    WorkerMode,
    classify_worker_mode,
    get_worker_mode,
    parse_ps_rows,
    require_stack_healthy,
    rows_healthy,
    stack_healthy,
)

__all__ = [
    "WorkerMode",
    "budgeted_compose_run",
    "classify_worker_mode",
    "compose",
    "compose_command",
    "get_worker_mode",
    "live_database_exists",
    "logs",
    "parse_ps_rows",
    "rebuild",
    "require_docker",
    "require_stack_healthy",
    "restart",
    "rows_healthy",
    "run_database_updates",
    "setup_database",
    "stack_healthy",
    "start",
    "status",
    "stop",
    "update",
    "worker_compose",
]
