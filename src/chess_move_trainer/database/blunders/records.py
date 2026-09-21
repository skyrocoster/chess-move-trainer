"""Internal blunder occurrence and analysis records."""

from __future__ import annotations

from dataclasses import dataclass

from .models import TrainerColor


@dataclass(frozen=True, slots=True)
class _GameScope:
    game_uuid: str
    source_url: str
    trainer_color: TrainerColor
    started_at_utc: str
    started_at_sortable: str


@dataclass(frozen=True, slots=True)
class _Occurrence:
    ply: int
    position_id: int
    placement: str
    side_to_move: str
    castling_rights: str
    legal_en_passant: str
    move_uci: str | None
    halfmove_clock: int
    fullmove_number: int

    @property
    def fen(self) -> str:
        return " ".join(
            (
                self.placement,
                self.side_to_move,
                self.castling_rights,
                self.legal_en_passant,
                str(self.halfmove_clock),
                str(self.fullmove_number),
            )
        )


@dataclass(frozen=True, slots=True)
class _Analysis:
    quality: str
    terminal_kind: str | None
    rank1_wins: int | None
    rank1_draws: int | None
    rank1_losses: int | None
    rank1_preferred_move: str | None


__all__ = ["_Analysis", "_GameScope", "_Occurrence"]
