"""Literal board relations, not tactical explanations or causal labels."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

import chess

from .protocol import DEFAULT_PROTOCOL as P

VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}


def material(board, color, *, pawns=True):
    return sum(
        value * len(board.pieces(piece, color))
        for piece, value in VALUES.items()
        if pawns or piece != chess.PAWN
    )


def phase(board, ply, opening=P.opening_last_ply, endgame=P.endgame_material):
    if ply <= opening:
        return "opening"
    return (
        "endgame"
        if sum(material(board, c, pawns=False) for c in chess.COLORS) <= endgame
        else "middlegame"
    )


def pawn_structure(board, color):
    pawns = list(board.pieces(chess.PAWN, color))
    enemy = list(board.pieces(chess.PAWN, not color))
    files = Counter(chess.square_file(s) for s in pawns)
    passed = []
    for s in pawns:
        f, r = chess.square_file(s), chess.square_rank(s)
        if not any(
            abs(chess.square_file(e) - f) <= 1
            and (chess.square_rank(e) > r if color else chess.square_rank(e) < r)
            for e in enemy
        ):
            passed.append(s)
    return {
        "doubled_pawns": sum(max(0, n - 1) for n in files.values()),
        "isolated_pawns": sum(n for f, n in files.items() if not files[f - 1] and not files[f + 1]),
        "pawn_islands": sum(1 for f in files if not files[f - 1]),
        "passed_pawns": len(passed),
        "blocked_passed_pawns": sum(
            board.piece_at(s + (8 if color else -8)) is not None
            for s in passed
            if 0 <= s + (8 if color else -8) < 64
        ),
        "connected_passed_pawns": sum(
            any(
                abs(chess.square_file(s) - chess.square_file(t)) == 1
                and abs(chess.square_rank(s) - chess.square_rank(t)) <= 1
                for t in passed
            )
            for s in passed
        ),
    }


def position_features(board, color):
    pawns = pawn_structure(board, color)
    king = board.king(color)
    zone = set(board.attacks(king)) | {king} if king is not None else set()
    shelter = sum(board.piece_at(s) == chess.Piece(chess.PAWN, color) for s in zone)
    attacked = [
        s
        for s, piece in board.piece_map().items()
        if piece.color == color
        and piece.piece_type != chess.KING
        and board.is_attacked_by(not color, s)
    ]
    return {
        **pawns,
        "material": material(board, color) - material(board, not color),
        "nonpawn_material": sum(material(board, c, pawns=False) for c in chess.COLORS),
        "bishop_pair": len(board.pieces(chess.BISHOP, color)) >= 2,
        "queenless": not bool(board.queens),
        "castling_rights": board.has_castling_rights(color),
        "king_shelter_pawns": shelter,
        "king_zone_attacked_squares": sum(board.is_attacked_by(not color, s) for s in zone),
        "central_control": sum(
            board.is_attacked_by(color, s) for s in (chess.D4, chess.E4, chess.D5, chess.E5)
        ),
        "attacked_undefended_pieces": sum(not board.is_attacked_by(color, s) for s in attacked),
        "absolutely_pinned_pieces": sum(
            board.is_pinned(color, s) for s in board.piece_map() if board.color_at(s) == color
        ),
    }


@dataclass
class ReplayState:
    identities: dict[int, str] = field(
        default_factory=lambda: {s: chess.square_name(s) for s in chess.Board().piece_map()}
    )
    counts: Counter = field(default_factory=Counter)
    last_by_color: dict = field(default_factory=dict)
    last_origins: dict = field(default_factory=dict)
    castled: dict = field(default_factory=dict)

    def apply(self, board, move):
        identity = self.identities.pop(move.from_square)
        if board.is_en_passant(move):
            self.identities.pop(move.to_square + (-8 if board.turn else 8), None)
        if board.is_castling(move):
            rank = 0 if board.turn else 7
            kingside = chess.square_file(move.to_square) > chess.square_file(move.from_square)
            origin = chess.square(7 if kingside else 0, rank)
            target = chess.square(5 if kingside else 3, rank)
            self.identities[target] = self.identities.pop(origin)
            self.castled[board.turn] = "kingside" if kingside else "queenside"
        self.identities[move.to_square] = identity
        self.counts[identity] += 1
        self.last_by_color[board.turn] = identity
        self.last_origins[identity] = move.from_square


def move_features(board: chess.Board, move: chess.Move, ply: int, state: ReplayState):
    if move not in board.legal_moves:
        raise ValueError("cannot extract features for an illegal move")
    color = board.turn
    piece = board.piece_type_at(move.from_square)
    capture_square = (
        move.to_square + (-8 if color else 8) if board.is_en_passant(move) else move.to_square
    )
    captured = board.piece_type_at(capture_square)
    identity = state.identities[move.from_square]
    before = position_features(board, color)
    after = board.copy(stack=False)
    after.push(move)
    following = position_features(after, color)
    checkers = set(after.checkers())
    targets = [
        s
        for s in after.attacks(move.to_square)
        if after.color_at(s) == (not color) and after.piece_type_at(s) != chess.PAWN
    ]
    df = chess.square_file(move.to_square) - chess.square_file(move.from_square)
    dr = (chess.square_rank(move.to_square) - chess.square_rank(move.from_square)) * (
        1 if color else -1
    )
    result = {
        "piece": chess.piece_name(piece),
        "captured_piece": chess.piece_name(captured) if captured else "none",
        "piece_identity": identity,
        "origin": chess.square_name(move.from_square),
        "destination": chess.square_name(move.to_square),
        "destination_file": chess.FILE_NAMES[chess.square_file(move.to_square)],
        "relative_rank": chess.square_rank(move.to_square) + 1
        if color
        else 8 - chess.square_rank(move.to_square),
        "direction": "forward" if dr > 0 else "backward" if dr < 0 else "sideways",
        "distance": max(abs(df), abs(dr)),
        "diagonal": bool(df and dr and abs(df) == abs(dr)),
        "kingside": chess.square_file(move.to_square) >= 4,
        "central_destination": move.to_square in (chess.D4, chess.E4, chess.D5, chess.E5),
        "phase": phase(board, ply),
        "phase_early": phase(board, ply, 16, 10),
        "phase_late": phase(board, ply, 24, 16),
        "capture": board.is_capture(move),
        "check": after.is_check(),
        "capture_check": board.is_capture(move) and after.is_check(),
        "double_check": len(checkers) >= 2,
        "discovered_check": bool(checkers - {move.to_square}) and not board.is_castling(move),
        "checkmate": after.is_checkmate(),
        "in_check": board.is_check(),
        "one_legal_reply_check": after.is_check() and after.legal_moves.count() == 1,
        "legal_moves": board.legal_moves.count(),
        "legal_capture_available": any(board.generate_legal_captures()),
        "opponent_legal_replies": after.legal_moves.count(),
        "castling": board.is_castling(move),
        "en_passant": board.is_en_passant(move),
        "promotion": chess.piece_name(move.promotion) if move.promotion else "none",
        "pinned_mover": board.is_pinned(color, move.from_square),
        "pinned_target": bool(captured) and board.is_pinned(not color, capture_square),
        "target_geometrically_defended": bool(captured)
        and board.is_attacked_by(not color, capture_square),
        "destination_attacked_before": board.is_attacked_by(not color, move.to_square),
        "mover_attacked_after": after.is_attacked_by(not color, move.to_square),
        "geometric_nonpawn_fork": len(targets) >= 2,
        "fork_targets": sorted(chess.piece_name(after.piece_type_at(s)) for s in targets),
        "capture_value_difference": VALUES.get(captured, 0) - VALUES[piece] if captured else None,
        "repeated_piece": state.counts[identity] > 0,
        "same_piece_consecutive_turns": state.last_by_color.get(color) == identity,
        "return_move": state.last_origins.get(identity) == move.to_square,
        "pawn_two_squares": piece == chess.PAWN and abs(dr) == 2,
        "early_queen": piece == chess.QUEEN and ply <= P.opening_last_ply,
        "knight_rim": piece == chess.KNIGHT
        and (
            chess.square_file(move.to_square) in (0, 7)
            or chess.square_rank(move.to_square) in (0, 7)
        ),
        "rook_seventh": piece == chess.ROOK
        and chess.square_rank(move.to_square) == (6 if color else 1),
        "castled_side_before": state.castled.get(color, "none"),
        **{f"before_{k}": v for k, v in before.items()},
        **{f"delta_{k}": int(following[k]) - int(v) for k, v in before.items()},
    }
    return result
