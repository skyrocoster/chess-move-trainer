"""Closed, outcome-independent contrast registry and complete source inventory."""

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .artifacts import digest, file_digest, write_json
from .protocol import DEFAULT_PROTOCOL as P

ADJUSTMENT = (
    "learner_color",
    "learner_rating",
    "rating_difference",
    "time_class",
    "calendar_period",
    "opening",
    "phase",
    "before_material",
    "expected_before_units",
)
FORBIDDEN_ADJUSTMENT = {
    "game_result",
    "termination",
    "loss",
    "severe",
    "expected_after_units",
    "delta_material",
    "collapse",
    "recovery",
    "game_length",
}


@dataclass(frozen=True)
class Question:
    id: str
    family: str
    population: str
    feature: str
    value: object
    outcome: str
    adjustment: tuple[str, ...] = ADJUSTMENT
    unit: str = "move"
    observation_time: str = "before_learner_move_or_played_move_geometry"
    comparator: str = "all_other_eligible_moves_in_same_population"
    direction: str = "two_sided"
    correction_family: str = "complete_v1"
    status: str = "registered"

    def to_dict(self):
        return {
            **asdict(self),
            "meaningful_effect": P.meaningful_risk
            if self.outcome == "severe"
            else P.meaningful_loss,
            "model": "binomial_gee" if self.outcome == "severe" else "two_part_gee",
            "cluster": "game_id",
            "missing": "complete_case_no_engine_imputation",
            "null": "adjusted_marginal_difference=0",
            "eligible": "validated_standard_chess_moves",
            "sensitivities": [
                "game_weighted",
                "opponent_cluster",
                "position_concentration",
                "leave_dominant_clusters_out",
                "phase_boundaries",
                "history_flag",
                "severe_010",
                "severe_030",
                "dead_band",
            ],
            "seed": P.seed,
            "bootstrap_replicates": P.bootstrap_replicates,
        }


def questions():
    exposures = [("Q01", "piece", p) for p in ("pawn", "knight", "bishop", "rook", "queen", "king")]
    exposures += [
        ("Q02", "capture_pair", f"{p}:{t}")
        for p in ("pawn", "knight", "bishop", "rook", "queen", "king")
        for t in ("pawn", "knight", "bishop", "rook", "queen")
    ]
    exposures += [
        (family, feature, True)
        for family, feature in (
            ("Q01", "capture"),
            ("Q03", "check"),
            ("Q03", "capture_check"),
            ("Q03", "one_legal_reply_check"),
            ("Q04", "pinned_mover"),
            ("Q04", "pinned_target"),
            ("Q04", "geometric_nonpawn_fork"),
            ("Q05", "before_bishop_pair"),
            ("Q05", "before_queenless"),
            ("Q06", "pawn_two_squares"),
            ("Q07", "castling"),
            ("Q07", "early_queen"),
            ("Q07", "in_check"),
            ("Q08", "same_piece_consecutive_turns"),
            ("Q08", "return_move"),
            ("Q08", "immediate_recapture"),
            ("Q09", "adherent"),
            ("Q10", "rank_one_agreement"),
        )
    ]
    registered = []
    for family, feature, value in exposures:
        for outcome in ("severe", "loss"):
            key = f"{family}.{feature}.{str(value).lower()}.{outcome}"
            # Rank-one agreement is engine-dependent, but not a quality-tier restriction.
            registered.append(
                Question(
                    key,
                    family,
                    "learner",
                    feature,
                    value,
                    outcome,
                    comparator="other_eligible_captures"
                    if feature == "capture_pair"
                    else "all_other_eligible_moves_in_same_population",
                )
            )
    for feature in (
        "opponent_previous_check",
        "opponent_previous_capture",
        "opponent_previous_pawn",
        "opponent_previous_early_queen",
        "opponent_previous_severe",
    ):
        for outcome in ("severe", "loss"):
            registered.append(
                Question(f"Q12.{feature}.{outcome}", "Q12", "learner", feature, True, outcome)
            )
    return tuple(registered)


def validate_question(question):
    if set(question.adjustment) & FORBIDDEN_ADJUSTMENT:
        raise ValueError("future/outcome leakage in adjustment")
    if question.outcome not in ("severe", "loss"):
        raise ValueError("unregistered model outcome")
    if question.observation_time != "before_learner_move_or_played_move_geometry":
        raise ValueError("unregistered observation timing")


# Exact source prefixes identify implemented *descriptions*, not whole-family completion.
DESCRIPTIONS = {
    "Moves by moving piece:": "piece",
    "Pawn moves as a percentage": "piece=pawn",
    "Moves by origin square": "origin,destination,destination_file,relative_rank",
    "Move distance by piece": "distance",
    "Quiet moves versus captures": "capture",
    "Checks versus non-checks": "check",
    "Castling, promotion, and en-passant": "castling,promotion,en_passant",
    "Legal-move count available": "legal_moves",
    "Capture rate overall": "capture",
    "Capture matrix:": "capture_pair",
    "Bishop captures of": "capture_pair=bishop:*",
    "Equivalent capture breakdowns": "capture_pair",
    "Captures with check": "capture_check",
    "Captures that produce checkmate": "checkmate,capture",
    "Captures made by a pinned": "pinned_mover",
    "Captures of a pinned": "pinned_target",
    "Absolute pins to the king": "before_absolutely_pinned_pieces",
    "Material balance before": "before_material,delta_material",
    "Queenless versus queen-present": "before_queenless",
    "Pawn-move frequency overall": "piece,phase,destination_file",
    "Pawn captures versus": "piece,capture",
    "One-square versus two-square": "pawn_two_squares",
    "Castling rate and": "castling",
    "Ply at which": "castling,ply",
    "Quality of responses to checks": "in_check",
    "Early queen moves": "early_queen",
    "Consecutive moves by the same piece": "same_piece_consecutive_turns",
    "Moving a piece and then returning": "return_move",
    "Preferred-move adherence and quality": "adherent",
    "Expected-score loss for every": "loss",
    "Severe-loss count and rate": "severe",
    "Difference between played move": "rank_one_agreement",
    "Whether the played move appears": "played_in_stored_candidates",
    "Opponent move mix": "population=opponent,piece",
    "Opponent pawn-move rate": "population=opponent,piece=pawn",
    "Opponent capture rate": "population=opponent,capture",
    "Opponent check rate": "population=opponent,check",
    "Opponent quiet-move rate": "population=opponent,capture=false",
}


def catalogue_inventory(path):
    """Every bullet from candidate analyses through unavailable inputs receives an ID.

    IDs depend on section and literal text, not mutable line numbers. All unmapped
    entries remain explicit; availability labels are never treated as implemented code.
    """
    entries = []
    section, active = "", False
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("## Candidate learner-move analyses"):
            active = True
        if line.startswith("## Reliability and interpretation hazards"):
            active = False
        if line.startswith("#"):
            section = line.lstrip("# ")
        if not active or not line.startswith("- "):
            continue
        text = line[2:]
        mapped = next(
            (value for prefix, value in DESCRIPTIONS.items() if text.startswith(prefix)), None
        )
        if "New " in text or section == "Data unavailable today":
            status, reason = (
                "data_unavailable",
                "Requires inputs or causal information not supported by v1.",
            )
        elif mapped:
            status, reason = (
                "descriptive_only",
                f"Literal extracted fields: {mapped}; inferential coverage is listed separately.",
            )
        elif "Definition required" in text or "definition" in text.lower():
            status, reason = (
                "definition_blocked",
                "Exact full-concept definition and counterexample fixtures are not yet accepted.",
            )
        else:
            status, reason = (
                "deferred",
                "Not yet implemented as a complete registered question; retained for continuation.",
            )
        entries.append(
            {
                "id": "CAT-" + digest([section, re.sub(r"\s+", " ", text)])[:12],
                "section": section,
                "source_line": line_number,
                "text": text,
                "status": status,
                "reason": reason,
            }
        )
    return entries


def freeze_registry(catalogue: Path, target: Path):
    if target.exists():
        raise FileExistsError("registry is immutable; select a new run")
    items = questions()
    for item in items:
        validate_question(item)
    value = {
        "protocol_sha256": P.identity,
        "source_catalogue_sha256": file_digest(catalogue),
        "questions": [q.to_dict() for q in items],
        "catalogue": catalogue_inventory(catalogue),
        "pending_families": [
            "Q11.game_outcomes",
            "Q13.calendar_models",
            "Q14.interactions",
            "Q08.volatility_models",
            "L03.full_pipeline_power",
            "L04.equivalence",
        ],
        "family_size": len(items),
        "status": "frozen_initial_contrasts_not_complete_plan",
    }
    value["identity"] = digest(value)
    write_json(target, value)
    return value
