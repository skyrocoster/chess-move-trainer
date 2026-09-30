"""Create immutable pilot samples and clean full-run directories.

Pilot selection is game-level and non-confirmatory. Resetting never deletes or
rewrites a prior run: callers provide a new output directory for every run.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from .artifacts import Budget, digest, file_digest, read_json, write_json
from .snapshot import verify_snapshot

SAMPLER_VERSION = "stratified-game-pilot-v1"
STRATUM_FIELDS = (
    "status",
    "learner_color",
    "time_class",
    "game_length",
    "learner_analysis_coverage",
    "opponent_analysis_coverage",
)
MARGINAL_FIELDS = (
    "status",
    "learner_color",
    "time_class",
    "calendar_year",
    "game_length",
    "learner_analysis_coverage",
    "opponent_analysis_coverage",
    "game_result",
    "exclusion_reason",
)


def _readonly(path: Path):
    return sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True, timeout=5)


def _coverage_band(value):
    if value is None:
        return "unknown"
    coverage = float(value)
    if not math.isfinite(coverage) or not 0 <= coverage <= 1:
        raise ValueError("game summary contains invalid engine-analysis coverage")
    if coverage == 0:
        return "none"
    if coverage >= 0.90:
        return "high"
    return "partial"


def _length_band(move_count):
    if move_count <= 20:
        return "short_1_to_20_plies"
    if move_count <= 60:
        return "medium_21_to_60_plies"
    return "long_over_60_plies"


def _game_info(row):
    status = row["status"]
    if status == "excluded":
        reason = row["reason"] or "unknown"
        row["move_count"] = 0
        dimensions = {field: "unknown" for field in MARGINAL_FIELDS}
        dimensions.update(status="excluded", exclusion_reason=reason)
        key = ("excluded", reason)
        return {"row": row, "dimensions": dimensions, "stratum": key}
    if status != "valid":
        raise ValueError(f"unsupported extracted game status: {status}")

    summary = json.loads(row["record"])
    if not isinstance(summary, dict):
        raise ValueError("valid extracted game is missing its summary")
    move_count = summary.get("move_count")
    if isinstance(move_count, bool) or not isinstance(move_count, int) or move_count < 1:
        raise ValueError("valid extracted game has an invalid move count")
    row["move_count"] = move_count
    learner = summary.get("learner")
    opponent = summary.get("opponent")
    if not isinstance(learner, dict) or not isinstance(opponent, dict):
        raise ValueError("valid game summary is missing a player population")
    started_at = summary.get("started_at") or ""
    year = started_at[:4] if len(started_at) >= 4 and started_at[:4].isdigit() else "unknown"
    color = summary.get("learner_color") or "unknown"
    time_class = summary.get("time_class") or "unknown"
    length = _length_band(move_count)
    learner_coverage = _coverage_band(learner.get("coverage"))
    opponent_coverage = _coverage_band(opponent.get("coverage"))
    dimensions = {
        "status": "valid",
        "learner_color": color,
        "time_class": time_class,
        "calendar_year": year,
        "game_length": length,
        "learner_analysis_coverage": learner_coverage,
        "opponent_analysis_coverage": opponent_coverage,
        "game_result": summary.get("game_result") or "unknown",
        "exclusion_reason": "none",
    }
    return {
        "row": row,
        "dimensions": dimensions,
        "stratum": (
            "valid",
            color,
            time_class,
            length,
            learner_coverage,
            opponent_coverage,
        ),
    }


def _stratum_description(key):
    if key[0] == "excluded":
        return {"status": "excluded", "reason": key[1]}
    return dict(zip(STRATUM_FIELDS, key, strict=True))


def _allocate_quotas(group_sizes, target):
    total = sum(group_sizes.values())
    if target >= total:
        return dict(group_sizes)
    if target < len(group_sizes):
        raise ValueError(
            f"pilot cap {target} is smaller than the {len(group_sizes)} non-empty strata; "
            "increase --max-games so every stratum is represented"
        )
    quotas = {key: 1 for key in group_sizes}
    remaining = target - len(quotas)
    while remaining:
        capacities = {key: group_sizes[key] - quotas[key] for key in group_sizes}
        available = sum(capacities.values())
        if available <= 0:
            raise RuntimeError("pilot sample quota allocation exceeded the population")
        shares = {key: remaining * capacities[key] / available for key in group_sizes}
        additions = {
            key: min(capacities[key], math.floor(shares[key]))
            for key in group_sizes
        }
        allocated = sum(additions.values())
        for key, count in additions.items():
            quotas[key] += count
        remaining -= allocated
        if remaining:
            order = sorted(
                group_sizes,
                key=lambda key: (-(shares[key] - math.floor(shares[key])), key),
            )
            for key in order:
                if quotas[key] < group_sizes[key]:
                    quotas[key] += 1
                    remaining -= 1
                    if not remaining:
                        break
    return quotas


def _source_rows(connection, budget):
    rows = []
    query = """SELECT id, uuid, status, reason, fingerprint, record
               FROM games ORDER BY id"""
    connection.row_factory = sqlite3.Row
    for row in connection.execute(query):
        budget.check()
        rows.append(dict(row))
    return rows


def _validate_source_run(directory: Path, budget: Budget):
    if (directory / "pilot.json").exists():
        raise ValueError("a pilot cannot be sampled again; use the complete source run")
    manifest = verify_snapshot(directory, budget)
    extraction = read_json(directory / "extraction.json")
    if extraction.get("status") != "complete" or extraction.get("processed_games") != extraction.get(
        "total_games"
    ):
        raise ValueError("pilot creation requires a complete full-game extraction")
    if extraction.get("snapshot_sha256") != manifest.get("snapshot_sha256"):
        raise ValueError("extraction and frozen snapshot identities disagree")
    registry = read_json(directory / "registry.json")
    if digest({key: value for key, value in registry.items() if key != "identity"}) != registry.get(
        "identity"
    ):
        raise ValueError("frozen registry contents changed")
    if registry.get("protocol_sha256") != manifest.get("protocol_sha256"):
        raise ValueError("registry and snapshot protocols disagree")
    records = _readonly(directory / "records.db")
    try:
        metadata = dict(records.execute("SELECT key, value FROM metadata"))
        if metadata.get("identity") != extraction.get("identity"):
            raise ValueError("extraction and records database identities disagree")
        rows = _source_rows(records, budget)
        if len(rows) != extraction.get("total_games"):
            raise ValueError("extraction manifest and records database game counts disagree")
        if not rows:
            raise ValueError("pilot creation requires a non-empty source population")
        infos = [_game_info(row) for row in rows]
        for info in infos:
            if info["row"]["status"] == "valid" and info["row"]["move_count"] < 1:
                raise ValueError("valid source game contains no extracted moves")
            if info["row"]["status"] == "excluded" and info["row"]["move_count"]:
                raise ValueError("excluded source game unexpectedly contains extracted moves")
        return manifest, extraction, registry, records, infos
    except BaseException:
        records.close()
        raise


def _selected_infos(infos, *, max_games, seed, budget):
    groups = defaultdict(list)
    for info in infos:
        budget.check()
        groups[info["stratum"]].append(info)
    target = min(max_games, len(infos))
    sizes = {key: len(rows) for key, rows in groups.items()}
    quotas = _allocate_quotas(sizes, target)
    selected = []
    for key in sorted(groups):
        budget.check()
        ranked = sorted(
            groups[key],
            key=lambda info: (
                hashlib.sha256(f"{seed}\0{info['row']['id']}".encode()).hexdigest(),
                info["row"]["id"],
            ),
        )
        selected.extend(ranked[: quotas[key]])
    return selected, sizes, quotas


def _copy_snapshot(source, target, expected_sha256, budget):
    partial = target.with_suffix(target.suffix + ".partial")
    with source.open("rb") as reader, partial.open("xb") as writer:
        while chunk := reader.read(1024 * 1024):
            budget.check()
            writer.write(chunk)
    os.replace(partial, target)
    if file_digest(target, budget) != expected_sha256:
        raise ValueError("copied frozen snapshot failed its content hash")


def _copy_records(source, target_path, selected, identity, budget):
    target = sqlite3.connect(target_path, timeout=5)
    try:
        target.executescript("""
            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE games (id INTEGER PRIMARY KEY, uuid TEXT NOT NULL,
                status TEXT NOT NULL, reason TEXT, fingerprint TEXT, record TEXT);
            CREATE TABLE moves (game INTEGER NOT NULL, ply INTEGER NOT NULL,
                record TEXT NOT NULL, PRIMARY KEY(game, ply));
        """)
        with target:
            target.execute("INSERT INTO metadata VALUES ('identity', ?)", (identity,))
            expected_moves = 0
            for info in selected:
                budget.check()
                row = info["row"]
                target.execute(
                    "INSERT INTO games VALUES (?, ?, ?, ?, ?, ?)",
                    (row["id"], row["uuid"], row["status"], row["reason"],
                     row["fingerprint"], row["record"]),
                )
                game_moves = row["move_count"]
                expected_moves += game_moves
                cursor = source.execute(
                    "SELECT game, ply, record FROM moves WHERE game=? ORDER BY ply", (row["id"],)
                )

                def records():
                    for move in cursor:
                        budget.check()
                        yield tuple(move)

                target.executemany("INSERT INTO moves VALUES (?, ?, ?)", records())
        actual_games = target.execute("SELECT COUNT(*) FROM games").fetchone()[0]
        actual_moves = target.execute("SELECT COUNT(*) FROM moves").fetchone()[0]
        if actual_games != len(selected) or actual_moves != expected_moves:
            raise ValueError("pilot database row counts failed post-write verification")
    finally:
        target.close()


def _distribution(infos, selected_ids):
    selected_set = set(selected_ids)
    result = {}
    for field in MARGINAL_FIELDS:
        source_counts, sample_counts = Counter(), Counter()
        for info in infos:
            value = info["dimensions"][field]
            source_counts[value] += 1
            if info["row"]["id"] in selected_set:
                sample_counts[value] += 1
        result[field] = [
            {
                "value": value,
                "source_games": source_counts[value],
                "sample_games": sample_counts[value],
                "source_share": source_counts[value] / len(infos),
                "sample_share": sample_counts[value] / len(selected_ids),
                "share_difference": sample_counts[value] / len(selected_ids)
                - source_counts[value] / len(infos),
            }
            for value in sorted(source_counts)
        ]
    return result


def _write_notes(path: Path, contents: str):
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_text(contents, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def _pilot_notes(directory, pilot):
    source_run = Path(pilot["source_run"]).as_posix()
    output = directory.as_posix()
    return f"""# Non-confirmatory pilot sample

This directory contains {pilot['sampled_games']} complete games sampled from
{pilot['source_total_games']} games in the frozen source run. Seed: {pilot['seed']}.
The whole-game sample is stratified by learner colour, time class, game length,
learner/opponent analysis-coverage band, and extraction status. Inclusion weights
are recorded in `pilot.json` but are **not** applied to audit or model outputs.
This artifact is for code, coverage, report, and runtime checks only; it cannot
produce a promoted finding or stand in for the complete historical programme.

## Use this pilot

Recreate the same selection in a new directory from the repository root, or audit
and report this already-created sample. Use finite command and tool timeouts:

```text
timeout 180s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis pilot --source-run "{source_run}" --output "<new-pilot-directory>" --max-games {pilot['requested_max_games']} --seed {pilot['seed']} --seconds 150
timeout 120s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis audit --run "{output}" --seconds 90
timeout 120s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis report --run "{output}"
```

Any model run must use the explicitly exploratory diagnostic mode and stays
non-confirmatory. Do not interpret sample proportions as full-corpus estimates.

## Clean full-run reset

Reset means creating a **new** full-run directory, not deleting or reusing this
pilot. `prepare-full` copies only the verified frozen `snapshot.db`, its manifest,
and the frozen registry from a complete full-source run. It deliberately omits
`records.db`, audits, reports, and diagnostic ledgers. Then extract all games
again and rebuild the audit/report in that new directory:

```text
timeout 120s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis prepare-full --source-run "<complete-full-source-run>" --output "<new-full-run-directory>" --seconds 90
timeout 180s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis extract --run "<new-full-run-directory>" --seconds 150
timeout 120s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis audit --run "<new-full-run-directory>" --seconds 90
timeout 120s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis report --run "<new-full-run-directory>"
```

Use a never-before-used output path; the command refuses to overwrite an existing
directory. Never copy the pilot `records.db` into a full run, never reuse a prior
`diagnostics.json`, and never remove old run artifacts to make a path reusable.
For intentionally refreshed live data, take a new safe snapshot and freeze the
approved registry in a different new directory instead of calling `prepare-full`.
"""


def create_pilot(
    source_run: Path,
    output: Path,
    *,
    max_games=1000,
    seed=20260922,
    seconds=120,
):
    """Create a fixed-seed stratified game sample without mutating its source run."""
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

    manifest, extraction, registry, source, infos = _validate_source_run(source_run, budget)
    try:
        selected, sizes, quotas = _selected_infos(
            infos, max_games=max_games, seed=seed, budget=budget
        )
        selected.sort(key=lambda info: info["row"]["id"])
        selected_ids = [info["row"]["id"] for info in selected]
        selection_identity = digest(selected_ids)
        identity = digest(
            {
                "sampler_version": SAMPLER_VERSION,
                "source_extraction_identity": extraction["identity"],
                "registry_identity": registry["identity"],
                "seed": seed,
                "requested_max_games": max_games,
                "selected_game_ids_sha256": selection_identity,
            }
        )
        move_total = sum(info["row"]["move_count"] for info in selected)
        source_moves = sum(info["row"]["move_count"] for info in infos)
        strata = [
            {
                "key": _stratum_description(key),
                "source_games": sizes[key],
                "sample_games": quotas[key],
                "inclusion_probability": quotas[key] / sizes[key],
                "inverse_probability_weight": sizes[key] / quotas[key],
            }
            for key in sorted(sizes)
        ]
        pilot = {
            "status": "run_incomplete",
            "mode": "non_confirmatory_representative_pilot",
            "sampler_version": SAMPLER_VERSION,
            "identity": identity,
            "source_run": str(source_run),
            "source_extraction_identity": extraction["identity"],
            "source_snapshot_sha256": manifest["snapshot_sha256"],
            "registry_identity": registry["identity"],
            "source_total_games": len(infos),
            "source_total_moves": source_moves,
            "sampled_games": len(selected),
            "sampled_moves": move_total,
            "requested_max_games": max_games,
            "seed": seed,
            "selected_game_ids_sha256": selection_identity,
            "stratum_fields": list(STRATUM_FIELDS),
            "strata": strata,
            "marginal_distributions": _distribution(infos, selected_ids),
            "weights_applied_to_outputs": False,
            "claim_boundary": "sample descriptions only; no confirmatory or promoted findings",
        }

        output.parent.mkdir(parents=True, exist_ok=True)
        output.mkdir()
        write_json(output / "pilot.json", pilot)
        try:
            _copy_snapshot(
                source_run / "snapshot.db",
                output / "snapshot.db",
                manifest["snapshot_sha256"],
                budget,
            )
            write_json(output / "manifest.json", manifest)
            write_json(output / "registry.json", registry)
            _copy_records(source, output / "records.db", selected, identity, budget)
            write_json(
                output / "extraction.json",
                {
                    "status": "complete",
                    "total_games": len(selected),
                    "processed_games": len(selected),
                    "identity": identity,
                    "records_version": extraction["records_version"],
                    "source_extraction_identity": extraction["identity"],
                    "snapshot_sha256": manifest["snapshot_sha256"],
                    "protocol_sha256": manifest["protocol_sha256"],
                    "pilot_identity": identity,
                },
            )
            pilot["status"] = "complete"
            write_json(output / "pilot.json", pilot)
            _write_notes(output / "PILOT.md", _pilot_notes(output, pilot))
            return pilot
        except BaseException as error:
            pilot.update(status="run_incomplete", error=f"{type(error).__name__}: {error}")
            write_json(output / "pilot.json", pilot)
            raise
    finally:
        source.close()
