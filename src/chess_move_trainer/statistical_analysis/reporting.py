"""Deterministic review package. No generated chess explanations."""

from pathlib import Path

from .artifacts import read_json, write_json


def report(directory: Path):
    audit = read_json(directory / "audit.json")
    registry = read_json(directory / "registry.json")
    manifest = read_json(directory / "manifest.json")
    diagnostic_path = directory / "diagnostics.json"
    ledger = read_json(diagnostic_path) if diagnostic_path.exists() else {"status": "not_run", "results": {}}
    findings = [dict(row, statement=(f"In the frozen snapshot, {row['value']} accounts for "
                                    f"{row['share_all_moves']:.2%} of eligible {row['population']} moves "
                                    f"for the {row['feature']} classification."))
                for row in audit["inventory"] if row["feature"] in ("piece", "capture", "check")]
    write_json(directory / "findings.json", {"status": "descriptive_census_only",
        "snapshot_sha256": manifest["snapshot_sha256"], "descriptions": findings, "associations": [],
        "reason": "Full inference calibration and sensitivity acceptance are incomplete."})
    disposition = {}
    for entry in registry["catalogue"]:
        disposition[entry["status"]] = disposition.get(entry["status"], 0) + 1
    lines = ["# Chess evidence review", "", "## Status", "",
             "This package contains snapshot descriptions, not established weaknesses or lessons.",
             "No association is promoted: complete model calibration and registered sensitivities remain pending.",
             "", f"- Snapshot: `{manifest['snapshot_sha256']}`",
             f"- Source: `{manifest['source']}`", f"- Registry: `{registry['identity']}`",
             f"- Games: {audit['total_games']}; excluded: {audit['excluded_games']}.",
             f"- Diagnostic model run: {ledger['status']}.", "", "## Coverage", "",
             "| Population | Eligible moves | Comparable moves | Coverage |", "|---|---:|---:|---:|"]
    for who, counts in audit["populations"].items():
        eligible, comparable = counts["eligible_moves"], counts["comparable_moves"]
        lines.append(f"| {who} | {eligible} | {comparable} | {comparable/eligible:.2%} |")
    lines += ["", "## Piece inventory (exact counts in this snapshot)", "",
              "| Population | Piece | Moves | Share | Independent games |", "|---|---|---:|---:|---:|"]
    for row in audit["inventory"]:
        if row["feature"] == "piece":
            lines.append(f"| {row['population']} | {row['value']} | {row['count']} | {row['share_all_moves']:.2%} | {row['games']} |")
    lines += ["", "## Data and method limits", ""]
    lines.extend(f"- {text}" for text in audit["limitations"])
    lines.extend(f"- `{key}`: {value} occurrences." for key, value in audit["measurement_limits"].items())
    lines += ["", "## Complete catalogue disposition", ""]
    lines.extend(f"- {key}: {value}." for key, value in sorted(disposition.items()))
    lines += ["", "## Review artifacts", "",
              "- `manifest.json`: snapshot, protocol, source and dependency identity.",
              "- `registry.json`: every source bullet, exact registered contrasts, blocked/deferred work.",
              "- `audit.json`: denominators, concentration, inventory, missingness, exclusions and measurement limits.",
              "- `records.db`: validated per-move and per-game facts, FENs and provenance; query read-only.",
              "- `findings.json`: exact snapshot descriptions; no promoted associations.",
              "- `diagnostics.json` (if present): provisional fits, correction accounting and every failed gate.",
              "", "## Next review", "",
              "Review data coverage and definitions first. Missing or inconclusive results are not weaknesses.",
              "Do not use the same historical data repeatedly until a test passes. Follow the Plan's pending stages.", ""]
    target = directory / "REVIEW.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    return target
