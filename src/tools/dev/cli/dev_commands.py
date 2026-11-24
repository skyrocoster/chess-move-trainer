"""``sg dev``: manage the persistent Docker Compose development services."""

from __future__ import annotations

from enum import Enum
from typing import Annotated

import typer

from tools.dev import services
from tools.dev.console import set_dry_run


class Service(str, Enum):
    all = "all"
    backend = "backend"
    frontend = "frontend"
    datasette = "datasette"
    worker = "worker"
    worker_six = "worker-six"


app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Start, stop and inspect the Docker development services.",
)

ServiceArg = Annotated[Service, typer.Argument(help="Service to target (default: all).")]
DryRun = Annotated[
    bool,
    typer.Option("--dry-run", help="Print the docker commands without running them."),
]


@app.command("start", help="Start services; `all` refreshes data first unless already healthy.")
def start_command(service: ServiceArg = Service.all, dry_run: DryRun = False) -> None:
    set_dry_run(dry_run)
    services.start(service.value)


@app.command("stop", help="Stop services (workers included for `all`).")
def stop_command(service: ServiceArg = Service.all, dry_run: DryRun = False) -> None:
    set_dry_run(dry_run)
    services.stop(service.value)


@app.command("restart", help="Restart services and wait for health.")
def restart_command(service: ServiceArg = Service.all, dry_run: DryRun = False) -> None:
    set_dry_run(dry_run)
    services.restart(service.value)


@app.command("rebuild", help="Rebuild images, recreate containers and wait for health.")
def rebuild_command(service: ServiceArg = Service.all, dry_run: DryRun = False) -> None:
    set_dry_run(dry_run)
    services.rebuild(service.value)


@app.command("status", help="Show container status and the worker mode.")
def status_command(
    service: ServiceArg = Service.all,
    as_json: Annotated[bool, typer.Option("--json", help="Print compose ps JSON.")] = False,
    dry_run: DryRun = False,
) -> None:
    set_dry_run(dry_run)
    services.status(service.value, as_json=as_json)


@app.command("logs", help="Show recent logs (default last 100 lines).")
def logs_command(
    service: ServiceArg = Service.all,
    tail: Annotated[int, typer.Option("--tail", min=1, help="Lines per container.")] = 100,
    dry_run: DryRun = False,
) -> None:
    set_dry_run(dry_run)
    services.logs(service.value, tail=tail)


@app.command("update", help="Refresh games and openings with workers paused (all services only).")
def update_command(dry_run: DryRun = False) -> None:
    set_dry_run(dry_run)
    services.update()


@app.command(
    "setup-db",
    help="One-time creation of the live database; refuses if it already exists.",
)
def setup_db_command(dry_run: DryRun = False) -> None:
    set_dry_run(dry_run)
    services.setup_database()
