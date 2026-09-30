"""Streaming census and measurement-limit report, without association testing."""

import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from .artifacts import Budget, read_json, write_json

INVENTORY_FIELDS = (
    "piece",
    "phase",
    "capture",
    "check",
    "castling",
    "promotion",
    "en_passant",
    "opening",
    "time_class",
    "calendar_period",
    "captured_piece",
    "capture_pair",
)


def iter_records(path):
    connection = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True, timeout=5)
    try:
        for game, ply, value in connection.execute(
            "SELECT game, ply, record FROM moves ORDER BY game, ply"
        ):
            yield json.loads(value)
    finally:
        connection.close()


def category(record, name):
    if name == "capture_pair":
        return f"{record['piece']}:{record['captured_piece']}" if record["capture"] else None
    return record.get(name)


def build_audit(directory: Path, *, seconds=120):
    budget = Budget(seconds)
    extraction = read_json(directory / "extraction.json")
    if extraction["status"] != "complete":
        raise ValueError("complete extraction required for a census report")
    pilot_path = directory / "pilot.json"
    pilot = read_json(pilot_path) if pilot_path.exists() else None
    if pilot is not None and pilot.get("status") != "complete":
        raise ValueError("complete pilot artifact required for a pilot audit")
    population = defaultdict(Counter)
    inventories = {}
    measurement = Counter()
    game_totals = defaultdict(Counter)
    identity_counts = defaultdict(Counter)
    for record in iter_records(directory / "records.db"):
        budget.check()
        who = record["population"]
        comparable = record["loss"] is not None
        population[who]["eligible_moves"] += 1
        population[who]["comparable_moves"] += comparable
        game_totals[who][record["game_id"]] += 1
        identity_counts[who][record["position_id"]] += 1
        for issue in record["issues"]:
            population[who][issue] += 1
        if record["issues"]:
            population[who]["primary_exclusion:" + record["issues"][0]] += 1
        measurement["history_sensitive"] += record["history_sensitive"]
        measurement["negative_signed_loss"] += (
            record["signed_loss_units"] is not None and record["signed_loss_units"] < 0
        )
        measurement["near_zero_signed_loss"] += (
            record["signed_loss_units"] is not None and 0 < abs(record["signed_loss_units"]) <= 2
        )
        measurement["missing_opponent_identity"] += record["opponent_id"] is None
        measurement["missing_timestamp"] += record["started_at"] is None
        measurement["missing_rating"] += (
            record["rating_difference"] is None or record["learner_rating"] is None
        )
        measurement["saturated_before_wdl"] += record["expected_before_units"] in (0, 2000)
        measurement["multipv_positions_occurrences"] += record["stored_candidates"] > 1
        measurement["candidate_censored_occurrences"] += (
            0 < record["stored_candidates"] < record["legal_moves"]
        )
        for field in INVENTORY_FIELDS:
            value = category(record, field)
            if value is None:
                continue
            key = (who, field, str(value))
            bucket = inventories.setdefault(
                key,
                {
                    "count": 0,
                    "comparable": 0,
                    "games": Counter(),
                    "opponents": set(),
                    "positions": set(),
                },
            )
            bucket["count"] += 1
            bucket["comparable"] += comparable
            bucket["games"][record["game_id"]] += 1
            if record["opponent_id"]:
                bucket["opponents"].add(record["opponent_id"])
            bucket["positions"].add(record["position_id"])
    inventory = []
    for (who, field, value), bucket in sorted(inventories.items()):
        total = population[who]["eligible_moves"]
        count = bucket["count"]
        game_weighted = sum(n / game_totals[who][g] for g, n in bucket["games"].items()) / len(
            game_totals[who]
        )
        inventory.append(
            {
                "population": who,
                "feature": field,
                "value": value,
                "count": count,
                "all_move_denominator": total,
                "share_all_moves": count / total,
                "game_weighted_share": game_weighted,
                "comparable": bucket["comparable"],
                "coverage": bucket["comparable"] / count,
                "games": len(bucket["games"]),
                "opponents": len(bucket["opponents"]),
                "positions": len(bucket["positions"]),
                "largest_game_share": max(bucket["games"].values()) / count,
                "claim_type": "pilot_sample_unweighted_descriptive_only"
                if pilot is not None
                else "snapshot_census_no_sampling_interval",
            }
        )
    with sqlite3.connect(directory / "records.db") as connection:
        exclusions = dict(
            connection.execute(
                "SELECT reason, COUNT(*) FROM games WHERE status='excluded' GROUP BY reason"
            )
        )
        duplicates = [
            {"fingerprint": fp, "game_count": count}
            for fp, count in connection.execute(
                "SELECT fingerprint, COUNT(*) FROM games GROUP BY fingerprint HAVING COUNT(*)>1"
            )
        ]
    report = {
        "status": "complete",
        "extraction_identity": extraction["identity"],
        "total_games": extraction["total_games"],
        "excluded_games": sum(exclusions.values()),
        "exclusions": exclusions,
        "possible_duplicate_games": duplicates,
        "populations": {k: dict(v) for k, v in population.items()},
        "measurement_limits": dict(measurement),
        "inventory": inventory,
        "limitations": [
            "No association models are fitted by this audit.",
            "Move counts are not independent sample sizes.",
            "Stored candidate count is not the number of sound legal moves.",
            "Canonical WDL ignores occurrence history and counters.",
            "No clock-pressure, intention, training-effect, or causal claims.",
        ],
    }
    if pilot is not None:
        report["pilot"] = {
            "identity": pilot["identity"],
            "source_total_games": pilot["source_total_games"],
            "sampled_games": pilot["sampled_games"],
            "seed": pilot["seed"],
            "weights_applied": False,
            "claim_boundary": pilot["claim_boundary"],
        }
    write_json(directory / "audit.json", report)
    return report
