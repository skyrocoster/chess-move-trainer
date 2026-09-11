"""Typer application objects."""

import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)
schema_app = typer.Typer(add_completion=False, no_args_is_help=True)
update_app = typer.Typer(add_completion=False, no_args_is_help=True)
openings_app = typer.Typer(add_completion=False, no_args_is_help=True)
preferred_moves_app = typer.Typer(add_completion=False, no_args_is_help=True)
stockfish_app = typer.Typer(add_completion=False, no_args_is_help=True)
app.add_typer(schema_app, name="schema")
app.add_typer(update_app, name="update")
app.add_typer(openings_app, name="openings")
app.add_typer(preferred_moves_app, name="preferred-moves")
app.add_typer(stockfish_app, name="stockfish")
