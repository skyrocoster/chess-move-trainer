"""Explicit observed sequences. Future-derived fields are not adjustment inputs."""

from statistics import median

from .protocol import DEFAULT_PROTOCOL as P


def enrich_sequences(records):
    previous_capture = None
    for i, record in enumerate(records):
        record["immediate_recapture"] = bool(record["capture"] and previous_capture == record["destination"])
        previous_capture = record["destination"] if record["capture"] else None
        previous = records[i - 1] if i else None
        for name in ("check", "capture", "early_queen", "severe"):
            record[f"opponent_previous_{name}"] = previous[name] if previous else None
        record["opponent_previous_pawn"] = previous["piece"] == "pawn" if previous else None
        record["missed_opportunity"] = (
            bool(record["severe"]) if previous and previous["severe"] == 1
            and record["severe"] is not None else None)
    for population in ("learner", "opponent"):
        own = [r for r in records if r["population"] == population]
        occupied_until = -1
        for i, record in enumerate(own):
            record["collapse"] = record["recovery"] = None
            record["episode_censored"] = None
            if record["severe"] != 1 or i <= occupied_until:
                continue
            occupied_until = i + P.recovery_window
            next_three = own[i + 1:i + 1 + P.response_window]
            next_five = own[i + 1:i + 1 + P.recovery_window]
            record["episode_censored"] = len(next_five) < P.recovery_window
            if len(next_three) == P.response_window and all(r["severe"] is not None for r in next_three):
                record["collapse"] = any(r["severe"] for r in next_three)
            if len(next_five) == P.recovery_window and all(r["expected_after_units"] is not None for r in next_five):
                record["recovery"] = any(r["expected_after_units"] >= record["expected_before_units"] - P.recovery_tolerance_units
                                         for r in next_five)


def summarize_game(records, metadata):
    result = dict(metadata)
    result["move_count"] = len(records)
    result["score"] = {"win": 1, "draw": 0.5, "loss": 0}.get(metadata["game_result"])
    for population in ("learner", "opponent"):
        own = [r for r in records if r["population"] == population]
        losses = [r["loss"] for r in own if r["loss"] is not None]
        signed = [r["signed_loss_units"] / 2000 for r in own if r["signed_loss_units"] is not None]
        mad = median(abs(v - median(signed)) for v in signed) if signed else None
        early = own[:P.early_opponent_moves]
        result[population] = {
            "moves": len(own), "comparable": len(losses),
            "coverage": len(losses) / len(own) if own else None,
            "mean_loss": sum(losses) / len(losses) if losses else None,
            "signed_change_mad": mad, "early_landmark_reached": len(early) == P.early_opponent_moves,
            "early_pawn_share": sum(r["piece"] == "pawn" for r in early) / len(early) if len(early) == P.early_opponent_moves else None,
            "early_queen_moves": sum(r["early_queen"] for r in early) if len(early) == P.early_opponent_moves else None,
            "capture_share": sum(r["capture"] for r in own) / len(own) if own else None,
            "check_share": sum(r["check"] for r in own) / len(own) if own else None,
        }
    landmarks = [r for r in records if r["population"] == "learner" and r["phase"] != "opening"
                 and r["expected_before_units"] is not None and r["expected_before_units"] >= P.advantage_units]
    result["advantage_landmark_ply"] = landmarks[0]["ply"] if landmarks else None
    return result
