"""Choose complete games from a frozen full snapshot before expensive replay."""

from __future__ import annotations

import hashlib
import os
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .artifacts import Budget, digest, file_digest, read_json, write_json
from .pilot import _allocate_quotas, _coverage_band, _length_band, _write_notes
from .snapshot import code_provenance, verify_snapshot

SAMPLER_VERSION = "snapshot-rank1-pair-pilot-v1"
STRATUM_FIELDS = (
    "learner_color",
    "time_class",
    "game_length",
    "learner_rank1_pair_coverage",
    "opponent_rank1_pair_coverage",
)
MARGINAL_FIELDS = (*STRATUM_FIELDS, "calendar_year", "game_result")


def _readonly(path: Path):
    return sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True, timeout=5)


def _interrupt_if_expired(budget):
    try:
        budget.check()
    except TimeoutError:
        return 1
    return 0


def _source_games(connection, budget):
    query = """WITH occurrences AS (
        SELECT g.dg_game_id AS game_id, g.dg_trainer_color, gp.dgp_ply,
            CASE WHEN (g.dg_trainer_color='white' AND gp.dgp_ply % 2=0)
                   OR (g.dg_trainer_color='black' AND gp.dgp_ply % 2=1)
                 THEN 1 ELSE 0 END AS learner_move,
            CASE WHEN before_line.dal_rank=1 AND after_line.dal_rank=1
                 THEN 1 ELSE 0 END AS rank1_pair
        FROM datasource_game g
        JOIN derived_game_position gp
          ON gp.datasource_game_id=g.dg_game_id AND gp.dgp_move_uci IS NOT NULL
        LEFT JOIN derived_game_position following
          ON following.datasource_game_id=gp.datasource_game_id
         AND following.dgp_ply=gp.dgp_ply+1
        LEFT JOIN derived_analysis_line before_line
          ON before_line.derived_analysis_result_id=gp.derived_position_id
         AND before_line.dal_rank=1
        LEFT JOIN derived_analysis_line after_line
          ON after_line.derived_analysis_result_id=following.derived_position_id
         AND after_line.dal_rank=1
    ), coverage AS (
        SELECT game_id, COUNT(*) AS plies,
            SUM(CASE WHEN learner_move=1 THEN 1 ELSE 0 END) AS learner_moves,
            SUM(CASE WHEN learner_move=1 AND rank1_pair=1 THEN 1 ELSE 0 END)
                AS learner_rank1_pairs,
            SUM(CASE WHEN learner_move=0 THEN 1 ELSE 0 END) AS opponent_moves,
            SUM(CASE WHEN learner_move=0 AND rank1_pair=1 THEN 1 ELSE 0 END)
                AS opponent_rank1_pairs
        FROM occurrences GROUP BY game_id
    )
    SELECT g.dg_game_id, g.dg_trainer_color, COALESCE(g.dg_time_class, 'unknown'),
        g.dg_started_at_utc, g.dg_trainer_outcome,
        COALESCE(c.plies, 0), COALESCE(c.learner_moves, 0),
        COALESCE(c.learner_rank1_pairs, 0), COALESCE(c.opponent_moves, 0),
        COALESCE(c.opponent_rank1_pairs, 0)
    FROM datasource_game g LEFT JOIN coverage c ON c.game_id=g.dg_game_id
    ORDER BY g.dg_game_id"""
    connection.row_factory = sqlite3.Row
    connection.set_progress_handler(lambda: _interrupt_if_expired(budget), 10000)
    try:
        games = []
        for row in connection.execute(query):
            budget.check()
            plies, learner_moves, learner_pairs, opponent_moves, opponent_pairs = row[5:10]
            learner_rate = learner_pairs / learner_moves if learner_moves else None
            opponent_rate = opponent_pairs / opponent_moves if opponent_moves else None
            year_text = row[3] or ""
            year = year_text[:4] if len(year_text) >= 4 and year_text[:4].isdigit() else "unknown"
            length = _length_band(plies) if plies else "no_moves"
            dimensions = {
                "learner_color": row[1],
                "time_class": row[2],
                "game_length": length,
                "learner_rank1_pair_coverage": _coverage_band(learner_rate),
                "opponent_rank1_pair_coverage": _coverage_band(opponent_rate),
                "calendar_year": year,
                "game_result": row[4] or "unknown",
            }
            games.append(
                {
                    "id": row[0],
                    "dimensions": dimensions,
                    "stratum": tuple(dimensions[field] for field in STRATUM_FIELDS),
                    "plies": plies,
                    "learner_moves": learner_moves,
                    "learner_rank1_pairs": learner_pairs,
                    "opponent_moves": opponent_moves,
                    "opponent_rank1_pairs": opponent_pairs,
                }
            )
        return games
    except sqlite3.OperationalError as error:
        try:
            budget.check()
        except TimeoutError:
            raise
        if "interrupted" in str(error).lower():
            raise TimeoutError("source coverage scan was interrupted") from error
        raise
    finally:
        connection.set_progress_handler(None, 0)


def _select(games, *, max_games, seed, budget):
    groups = defaultdict(list)
    for game in games:
        budget.check()
        groups[game["stratum"]].append(game)
    target = min(max_games, len(games))
    sizes = {key: len(rows) for key, rows in groups.items()}
    quotas = _allocate_quotas(sizes, target)
    selected = []
    for key in sorted(groups):
        budget.check()
        ranked = sorted(
            groups[key],
            key=lambda game: (
                hashlib.sha256(f"{seed}\0{game['id']}".encode()).hexdigest(),
                game["id"],
            ),
        )
        selected.extend(ranked[: quotas[key]])
    selected.sort(key=lambda game: game["id"])
    return selected, sizes, quotas


def _summaries(games, selected_ids):
    selected_ids = set(selected_ids)
    summaries = {}
    for field in MARGINAL_FIELDS:
        source, sample = Counter(), Counter()
        for game in games:
            value = game["dimensions"][field]
            source[value] += 1
            if game["id"] in selected_ids:
                sample[value] += 1
        summaries[field] = [
            {
                "value": value,
                "source_games": source[value],
                "sample_games": sample[value],
                "source_share": source[value] / len(games),
                "sample_share": sample[value] / len(selected_ids),
                "share_difference": sample[value] / len(selected_ids)
                - source[value] / len(games),
            }
            for value in sorted(source)
        ]
    return summaries


def _subset_snapshot(source_path, target_path, selected_ids, expected_games, budget):
    partial = target_path.with_suffix(target_path.suffix + ".partial")
    source = _readonly(source_path)
    target = sqlite3.connect(partial, timeout=5)
    target.set_progress_handler(lambda: _interrupt_if_expired(budget), 10000)
    try:
        source.backup(
            target,
            pages=256,
            sleep=0.01,
            progress=lambda *_: budget.check(),
        )
        target.execute("PRAGMA journal_mode=DELETE")
        target.execute("PRAGMA foreign_keys=ON")
        target.execute("CREATE TEMP TABLE selected_game_ids (game_id INTEGER PRIMARY KEY)")
        target.executemany(
            "INSERT INTO selected_game_ids VALUES (?)", ((game_id,) for game_id in selected_ids)
        )
        with target:
            target.execute(
                "DELETE FROM derived_game_position WHERE datasource_game_id NOT IN "
                "(SELECT game_id FROM selected_game_ids)"
            )
            target.execute(
                "DELETE FROM datasource_game WHERE dg_game_id NOT IN "
                "(SELECT game_id FROM selected_game_ids)"
            )
        if target.execute("SELECT COUNT(*) FROM datasource_game").fetchone()[0] != expected_games:
            raise ValueError("pilot snapshot game count failed post-write verification")
        if target.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise ValueError("pilot snapshot contains broken foreign keys")
    except sqlite3.OperationalError as error:
        try:
            budget.check()
        except TimeoutError:
            raise
        if "interrupted" in str(error).lower():
            raise TimeoutError("pilot snapshot reduction was interrupted") from error
        raise
    finally:
        target.close()
        source.close()
    os.replace(partial, target_path)
    return file_digest(target_path, budget)


def _pilot_notes(directory, pilot):
    source_run = Path(pilot["source_run"]).as_posix()
    output = directory.as_posix()
    return f"""# Snapshot-selected pilot sample

This directory contains a deterministic, whole-game sample of
{pilot['sampled_games']} from {pilot['source_total_games']} source games. It was
selected **before** replay, using learner colour, time class, game length, and
raw rank-one before/after analysis availability for learner and opponent moves.
The rank-one availability bands are sampling aids, not validated outcome coverage.
Extraction must complete before audit/report. Excluded or invalid games are
retained in the sample and are counted by extraction rather than silently removed.

Sample weights and source-versus-sample margins are in `pilot.json`; weights are
not applied to descriptions or models. This pilot is engineering/coverage work,
not a confirmatory analysis and not a source of promotable findings.

## Resume this pilot

The sample snapshot and seed are immutable. Extraction is game-atomic and resumable:
if a bounded extraction call stops, rerun `extract` on this **same** directory
with the same code/protocol until `extraction.json` says `complete`.

```text
timeout 180s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis pilot-snapshot --source-run "{source_run}" --output "<new-pilot-directory>" --max-games {pilot['requested_max_games']} --seed {pilot['seed']} --seconds 150
timeout 120s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis extract --run "{output}" --seconds 90 --max-games 200
timeout 120s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis audit --run "{output}" --seconds 90
timeout 120s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis report --run "{output}"
```

## Reset for a full run

Never delete or reuse this pilot directory. To reprocess the complete frozen live
snapshot, use `prepare-full` with a **new** output directory; it copies the full
snapshot and registry, not this subset's records or diagnostic ledger. Then run
complete extraction in that directory. If extraction stops, resume in the same
full-run directory; if preparation stops before it is ready, choose another new
output path. A refreshed live snapshot is a separate new run and is not produced
by `prepare-full`.

```text
timeout 120s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis prepare-full --source-run "{source_run}" --output "<new-full-run-directory>" --seconds 90
timeout 180s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis extract --run "<new-full-run-directory>" --seconds 150
```
"""


def create_snapshot_pilot(
    source_run: Path,
    output: Path,
    *,
    max_games=1000,
    seed=20260922,
    seconds=120,
):
    """Create a stratified subset snapshot so only pilot games need replay."""
    budget = Budget(seconds)
    if isinstance(max_games, bool) or not isinstance(max_games, int) or max_games < 1:
        raise ValueError("max_games must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    source_run = source_run.resolve(strict=True)
    output = output.resolve()
    if source_run == output:
        raise ValueError("pilot output must be separate from its source run")
    if output.exists():
        raise FileExistsError("pilot output directory must be new; existing artifacts are immutable")
    if (source_run / "pilot.json").exists():
        raise ValueError("a pilot cannot be sampled again; use a frozen full snapshot")

    source_manifest = verify_snapshot(source_run, budget)
    registry = read_json(source_run / "registry.json")
    if digest({key: value for key, value in registry.items() if key != "identity"}) != registry.get(
        "identity"
    ):
        raise ValueError("frozen registry contents changed")
    if registry.get("protocol_sha256") != source_manifest.get("protocol_sha256"):
        raise ValueError("registry and snapshot protocols disagree")
    source = _readonly(source_run / "snapshot.db")
    try:
        games = _source_games(source, budget)
    finally:
        source.close()
    if not games:
        raise ValueError("pilot creation requires a non-empty frozen population")

    selected, sizes, quotas = _select(games, max_games=max_games, seed=seed, budget=budget)
    selected_ids = [game["id"] for game in selected]
    selected_hash = digest(selected_ids)
    pilot_identity = digest(
        {
            "sampler_version": SAMPLER_VERSION,
            "source_snapshot_sha256": source_manifest["snapshot_sha256"],
            "registry_identity": registry["identity"],
            "seed": seed,
            "requested_max_games": max_games,
            "selected_game_ids_sha256": selected_hash,
        }
    )
    strata = [
        {
            "key": dict(zip(STRATUM_FIELDS, key, strict=True)),
            "source_games": sizes[key],
            "sample_games": quotas[key],
            "inclusion_probability": quotas[key] / sizes[key],
            "inverse_probability_weight": sizes[key] / quotas[key],
        }
        for key in sorted(sizes)
    ]
    learner_moves = sum(game["learner_moves"] for game in games)
    learner_pairs = sum(game["learner_rank1_pairs"] for game in games)
    opponent_moves = sum(game["opponent_moves"] for game in games)
    opponent_pairs = sum(game["opponent_rank1_pairs"] for game in games)
    pilot = {
        "status": "sampling_incomplete",
        "mode": "snapshot_selected_non_confirmatory_pilot",
        "sampler_version": SAMPLER_VERSION,
        "identity": pilot_identity,
        "source_run": str(source_run),
        "source_snapshot_sha256": source_manifest["snapshot_sha256"],
        "registry_identity": registry["identity"],
        "source_total_games": len(games),
        "sampled_games": len(selected),
        "sampled_plies": sum(game["plies"] for game in selected),
        "requested_max_games": max_games,
        "seed": seed,
        "selected_game_ids_sha256": selected_hash,
        "stratum_fields": list(STRATUM_FIELDS),
        "strata": strata,
        "marginal_distributions": _summaries(games, selected_ids),
        "source_raw_rank1_pair_coverage": {
            "learner": learner_pairs / learner_moves if learner_moves else None,
            "opponent": opponent_pairs / opponent_moves if opponent_moves else None,
        },
        "coverage_definition": (
            "availability of stored rank-one before/after lines; terminal scoring and full "
            "analysis validation are applied later during extraction"
        ),
        "weights_applied_to_outputs": False,
        "claim_boundary": "sample descriptions only; no confirmatory or promoted findings",
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    write_json(output / "pilot.json", pilot)
    try:
        snapshot_hash = _subset_snapshot(
            source_run / "snapshot.db",
            output / "snapshot.db",
            selected_ids,
            len(selected),
            budget,
        )
        manifest = {
            **source_manifest,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "snapshot_sha256": snapshot_hash,
            "code": code_provenance(),
            "parent_snapshot_sha256": source_manifest["snapshot_sha256"],
            "pilot_identity": pilot_identity,
            "snapshot_kind": "stratified_game_pilot_subset",
        }
        write_json(output / "manifest.json", manifest)
        if verify_snapshot(output, budget).get("snapshot_sha256") != snapshot_hash:
            raise ValueError("pilot snapshot manifest failed verification")
        write_json(output / "registry.json", registry)
        pilot.update(
            status="ready_for_extraction",
            subset_snapshot_sha256=snapshot_hash,
        )
        write_json(output / "pilot.json", pilot)
        _write_notes(output / "PILOT.md", _pilot_notes(output, pilot))
        return pilot
    except BaseException as error:
        pilot.update(status="sampling_incomplete", error=f"{type(error).__name__}: {error}")
        write_json(output / "pilot.json", pilot)
        raise
