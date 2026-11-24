"""The ``check`` command group: the full fail-fast process, or the service preflight."""

from __future__ import annotations

import typer

from tools.dev import services
from tools.dev.checks import full_process

app = typer.Typer(
    add_completion=False,
    no_args_is_help=False,
    help="Run the full fail-fast check process (resumable) when no subcommand is given.",
)


@app.callback(invoke_without_command=True)
def check_command(
    ctx: typer.Context,
    list_checks: bool = typer.Option(
        False, "--list", help="Show the ordered inventory without running it."
    ),
    fresh: bool = typer.Option(
        False, "--fresh", help="Discard the checkpoint and start from the first check."
    ),
    from_step: str = typer.Option(
        "", "--from", help="Start at one exactly or uniquely matching check."
    ),
    only_step: str = typer.Option(
        "", "--only", help="Run exactly one matching check without changing the checkpoint."
    ),
) -> None:
    """Run the full process when no check subcommand is selected."""
    if ctx.invoked_subcommand is None:
        full_process.run_full_process(
            list_checks=list_checks, fresh=fresh, from_step=from_step, only_step=only_step
        )


@app.command("services", help="Fail unless backend, frontend and datasette are healthy.")
def services_command() -> None:
    """Preflight for the real-backend and browser checks."""
    services.require_stack_healthy()
