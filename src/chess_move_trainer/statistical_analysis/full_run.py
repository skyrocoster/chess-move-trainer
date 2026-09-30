"""Prepare a new full run without carrying over pilot or diagnostic results."""

import sqlite3
from pathlib import Path

from .artifacts import Budget, digest, read_json, write_json
from .pilot import _copy_snapshot, _write_notes
from .snapshot import verify_snapshot


def prepare_full_run(source_run: Path, output: Path, *, seconds=120):
    """Copy frozen inputs into a new directory; never delete or reuse a prior run."""
    budget = Budget(seconds)
    source_run = source_run.resolve(strict=True)
    output = output.resolve()
    if source_run == output:
        raise ValueError("full-run output must be separate from its source run")
    if output.exists():
        raise FileExistsError("full-run output directory must be new; existing artifacts are immutable")
    if (source_run / "pilot.json").exists():
        raise ValueError("prepare-full requires a full snapshot, not a pilot sample")
    manifest = verify_snapshot(source_run, budget)
    if manifest.get("pilot_identity") or manifest.get("snapshot_kind") == "stratified_game_pilot_subset":
        raise ValueError("prepare-full refuses a pilot subset snapshot")
    registry = read_json(source_run / "registry.json")
    if digest({key: value for key, value in registry.items() if key != "identity"}) != registry.get(
        "identity"
    ):
        raise ValueError("frozen registry contents changed")
    if registry.get("protocol_sha256") != manifest.get("protocol_sha256"):
        raise ValueError("registry and frozen snapshot protocols disagree")
    source = sqlite3.connect(
        f"{(source_run / 'snapshot.db').resolve().as_uri()}?mode=ro", uri=True, timeout=5
    )
    try:
        source_total_games = source.execute("SELECT COUNT(*) FROM datasource_game").fetchone()[0]
        if not source_total_games:
            raise ValueError("full-run preparation requires a non-empty full snapshot")
        preparation = {
            "status": "run_incomplete",
            "mode": "fresh_full_extraction_from_frozen_inputs",
            "source_run": str(source_run),
            "snapshot_sha256": manifest["snapshot_sha256"],
            "registry_identity": registry["identity"],
            "source_total_games": source_total_games,
            "copied_results": False,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.mkdir()
        write_json(output / "run-preparation.json", preparation)
        try:
            _copy_snapshot(
                source_run / "snapshot.db",
                output / "snapshot.db",
                manifest["snapshot_sha256"],
                budget,
            )
            write_json(output / "manifest.json", manifest)
            write_json(output / "registry.json", registry)
            if any((output / name).exists() for name in ("records.db", "diagnostics.json")):
                raise RuntimeError("fresh full-run directory unexpectedly contains result artifacts")
            preparation["status"] = "ready_for_full_extraction"
            write_json(output / "run-preparation.json", preparation)
            _write_notes(
                output / "FULL_RUN_RESET.md",
                f"""# Fresh full-run directory

This new directory uses the exact frozen snapshot and registry from
`{source_run.as_posix()}`. The source extraction may be partial or complete. It
intentionally contains no `records.db`, audit, report, or
diagnostic ledger. Run complete extraction here before analysis.

```text
timeout 180s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis extract --run "{output.as_posix()}" --seconds 150
timeout 120s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis audit --run "{output.as_posix()}" --seconds 90
timeout 120s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis report --run "{output.as_posix()}"
```

This is a non-destructive reset: old pilot and diagnostic artifacts remain
untouched. If `prepare-full` itself is interrupted before it reports
`ready_for_full_extraction`, preserve that directory and prepare another
never-used output path. If `extract` is interrupted, rerun `extract` on this same
directory with the same code and protocol; game-atomic extraction resumes from
its checkpoints. If record semantics change, prepare a new directory instead of
mixing versions. Do not delete artifacts to make a path reusable. This resets
derived run state only; it does not refresh the live database or approve
historical inference.
""",
            )
            return preparation
        except BaseException as error:
            preparation.update(status="run_incomplete", error=f"{type(error).__name__}: {error}")
            write_json(output / "run-preparation.json", preparation)
            raise
    finally:
        source.close()
