"""Frozen defaults. Changing any definition changes the protocol identity."""

import json
from dataclasses import asdict, dataclass

from . import PROTOCOL_VERSION
from .artifacts import digest


@dataclass(frozen=True)
class Protocol:
    version: str = PROTOCOL_VERSION
    severe_loss_units: int = 400  # Expected score in exact 1/2000 units.
    severe_sensitivity_units: tuple[int, ...] = (200, 600)
    dead_band_units: int = 2
    opening_last_ply: int = 20
    endgame_material: int = 13
    sound_distance_units: int = 40
    early_opponent_moves: int = 10
    response_window: int = 3
    recovery_window: int = 5
    recovery_tolerance_units: int = 100
    advantage_units: int = 1600
    minimum_games: int = 100
    minimum_group_games: int = 50
    minimum_event_games: int = 30
    minimum_coverage: float = 0.90
    maximum_coverage_gap: float = 0.05
    alpha: float = 0.05
    meaningful_risk: float = 0.02
    meaningful_loss: float = 0.01
    meaningful_score: float = 0.05
    bootstrap_replicates: int = 2000
    bootstrap_cap: int = 10000
    minimum_fit_success: float = 0.99
    calendar_block_days: int = 28
    seed: int = 20260922
    # Untested crossing of these limits blocks promotion, not silent trimming.
    maximum_cluster_share: float = 0.10
    minimum_overlap_fraction: float = 0.95
    primary_history_policy: str = "retain_and_flag_no_history_aware_claims"
    missing_engine_policy: str = "no_imputation"
    promotion_correction: str = "holm_complete_family"
    interval_method: str = "bonferroni_normal_max_robust_bootstrap_se"
    calibration_status: str = "not_validated"

    def to_dict(self):
        return json.loads(json.dumps(asdict(self)))

    @property
    def identity(self):
        return digest(self.to_dict())


DEFAULT_PROTOCOL = Protocol()
