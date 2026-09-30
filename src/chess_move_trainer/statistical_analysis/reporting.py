"""Deterministic review package. No generated chess explanations."""

from pathlib import Path

from .artifacts import read_json, write_json


def report(directory: Path):
    audit = read_json(directory / "audit.json")
    registry = read_json(directory / "registry.json")
    manifest = read_json(directory / "manifest.json")
    pilot_path = directory / "pilot.json"
    pilot = read_json(pilot_path) if pilot_path.exists() else None
    if pilot is not None and pilot.get("status") != "complete":
        raise ValueError("complete pilot artifact required for a review report")
    diagnostic_path = directory / "diagnostics.json"
    ledger = (
        read_json(diagnostic_path)
        if diagnostic_path.exists()
        else {"status": "not_run", "results": {}}
    )
    findings = [
        dict(
            row,
            statement=(
                f"In the {'pilot sample' if pilot is not None else 'frozen snapshot'}, "
                f"{row['value']} accounts for "
                f"{row['share_all_moves']:.2%} of eligible {row['population']} moves "
                f"for the {row['feature']} classification."
            ),
        )
        for row in audit["inventory"]
        if row["feature"] in ("piece", "capture", "check")
    ]
    write_json(
        directory / "findings.json",
        {
            "status": "pilot_sample_descriptive_only"
            if pilot is not None
            else "descriptive_census_only",
            "snapshot_sha256": manifest["snapshot_sha256"],
            "pilot_identity": pilot["identity"] if pilot is not None else None,
            "descriptions": findings,
            "associations": [],
            "reason": "Pilot descriptions are unweighted and non-confirmatory."
            if pilot is not None
            else "Full inference calibration and sensitivity acceptance are incomplete.",
        },
    )
    disposition = {}
    for entry in registry["catalogue"]:
        disposition[entry["status"]] = disposition.get(entry["status"], 0) + 1
    lines = [
        "# Chess pilot sample review" if pilot is not None else "# Chess evidence review",
        "",
        "## Status",
        "",
        "This package contains pilot-sample descriptions, not full-corpus estimates."
        if pilot is not None
        else "This package contains snapshot descriptions, not established weaknesses or lessons.",
        "Pilot outputs are unweighted and cannot support a promoted finding."
        if pilot is not None
        else "",
        "",
        "No association is promoted: complete model calibration and registered "
        "sensitivities remain pending.",
        "",
        f"- Snapshot: `{manifest['snapshot_sha256']}`",
        f"- Source: `{manifest['source']}`",
        f"- Registry: `{registry['identity']}`",
        f"- Games in {'pilot sample' if pilot is not None else 'snapshot'}: "
        f"{audit['total_games']}; excluded: {audit['excluded_games']}.",
        f"- Diagnostic model run: {ledger['status']}.",
        "",
    ]
    if pilot is not None:
        lines += [
            f"- Pilot identity: `{pilot['identity']}`; seed: {pilot['seed']}",
            f"- Sampled {pilot['sampled_games']} of {pilot['source_total_games']} source games; "
            f"sampling weights applied: {pilot['weights_applied_to_outputs']}.",
            "- Source-versus-sample margins and stratum inclusion probabilities are in `pilot.json`.",
            "",
        ]
    lines += [
        "## Coverage",
        "",
        "| Population | Eligible moves | Comparable moves | Coverage |",
        "|---|---:|---:|---:|",
    ]
    for who, counts in audit["populations"].items():
        eligible, comparable = counts["eligible_moves"], counts["comparable_moves"]
        lines.append(f"| {who} | {eligible} | {comparable} | {comparable / eligible:.2%} |")
    lines += [
        "",
        "## Piece inventory (exact counts in this pilot sample)"
        if pilot is not None
        else "## Piece inventory (exact counts in this snapshot)",
        "",
        "| Population | Piece | Moves | Share | Independent games |",
        "|---|---|---:|---:|---:|",
    ]
    for row in audit["inventory"]:
        if row["feature"] == "piece":
            lines.append(
                f"| {row['population']} | {row['value']} | {row['count']} | "
                f"{row['share_all_moves']:.2%} | {row['games']} |"
            )
    lines += ["", "## Data and method limits", ""]
    lines.extend(f"- {text}" for text in audit["limitations"])
    lines.extend(
        f"- `{key}`: {value} occurrences." for key, value in audit["measurement_limits"].items()
    )
    lines += ["", "## Complete catalogue disposition", ""]
    lines.extend(f"- {key}: {value}." for key, value in sorted(disposition.items()))
    lines += [
        "",
        "## Review artifacts",
        "",
        "- `manifest.json`: snapshot, protocol, source and dependency identity.",
        "- `registry.json`: every source bullet, exact registered contrasts, "
        "blocked/deferred work.",
        "- `pilot.json` and `PILOT.md`: sampling design, representation checks, and safe reset notes."
        if pilot is not None
        else "",
        "- `audit.json`: denominators, concentration, inventory, missingness, "
        "exclusions and measurement limits.",
        "- `records.db`: validated per-move and per-game facts, FENs and provenance; "
        "query read-only.",
        "- `findings.json`: exact pilot sample descriptions; no promoted associations."
        if pilot is not None
        else "- `findings.json`: exact snapshot descriptions; no promoted associations.",
        "- `diagnostics.json` (if present): provisional fits, correction accounting "
        "and every failed gate.",
        "",
        "## Next review",
        "",
        "Review data coverage and definitions first. Missing or inconclusive results "
        "are not weaknesses.",
        "Do not use the same historical data repeatedly until a test passes. "
        "Follow the Plan's pending stages.",
        "For a clean full run, use `prepare-full` with a new output directory; do not reuse this sample."
        if pilot is not None
        else "",
        "",
    ]
    target = directory / "REVIEW.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    return target
