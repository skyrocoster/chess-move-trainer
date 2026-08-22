"""Deterministic replay-derived opening relationship facts."""

from __future__ import annotations

import io
from collections import defaultdict
from dataclasses import dataclass

import chess
import chess.pgn

from .importer import OpeningRecord, OpeningReplayError, SourceManifest

PositionKey = tuple[str, str, str, str]
SourceIdentity = tuple[str, int]


@dataclass(frozen=True)
class MembershipFact:
    source_file: str
    source_row_ordinal: int
    ply: int
    key: PositionKey
    uci: str
    san: str
    uci_prefix: str


@dataclass(frozen=True)
class ParentFact:
    child_source_file: str
    child_source_row_ordinal: int
    child_ply: int
    parent_source_file: str
    parent_source_row_ordinal: int


@dataclass(frozen=True)
class TranspositionFact:
    key: PositionKey
    source_file_a: str
    source_row_ordinal_a: int
    ply_a: int
    uci_prefix_a: str
    source_file_b: str
    source_row_ordinal_b: int
    ply_b: int
    uci_prefix_b: str


@dataclass(frozen=True)
class RelationshipFacts:
    manifest_hash: str
    record_count: int
    positions: tuple[PositionKey, ...]
    memberships: tuple[MembershipFact, ...]
    parents: tuple[ParentFact, ...]
    transpositions: tuple[TranspositionFact, ...]

    @property
    def position_count(self) -> int:
        return len(self.positions)

    @property
    def membership_count(self) -> int:
        return len(self.memberships)

    @property
    def parent_link_count(self) -> int:
        return len(self.parents)

    @property
    def transposition_link_count(self) -> int:
        return len(self.transpositions)


@dataclass(frozen=True)
class RelationshipImportResult:
    run_id: str
    manifest_hash: str
    status: str
    record_count: int
    position_count: int
    membership_count: int
    parent_link_count: int
    transposition_link_count: int


def _source_identity(source_file: str, source_row_ordinal: int) -> SourceIdentity:
    return source_file, source_row_ordinal


def _replay_memberships(record: OpeningRecord) -> list[MembershipFact]:
    try:
        game = chess.pgn.read_game(io.StringIO('[Result "*"]\n\n' + record.move_sequence))
        if game is None:
            raise ValueError("PGN parsed to no game")
        parser_errors = getattr(game, "errors", ())
        if parser_errors:
            raise ValueError(f"PGN parser errors: {parser_errors[0]}")
        board = game.board()
        prefix: list[str] = []
        memberships: list[MembershipFact] = []
        for ply, move in enumerate(game.mainline_moves(), start=1):
            if move not in board.legal_moves:
                raise ValueError(f"illegal move at ply {ply}: {move.uci()}")
            san = board.san(move)
            uci = move.uci()
            prefix.append(uci)
            board.push(move)
            fields = board.fen(en_passant="fen").split()
            if len(fields) != 6:
                raise ValueError(f"generated FEN has {len(fields)} fields")
            memberships.append(
                MembershipFact(
                    record.source_file,
                    record.source_row_ordinal,
                    ply,
                    tuple(fields[:4]),  # type: ignore[return-value]
                    uci,
                    san,
                    " ".join(prefix),
                )
            )
        if not memberships:
            raise ValueError("PGN contains no moves")
        final_fen = " ".join(board.fen(en_passant="fen").split())
        if final_fen != record.endpoint_fen:
            raise ValueError(
                f"endpoint differs from catalog: generated={final_fen!r}, "
                f"catalog={record.endpoint_fen!r}"
            )
        return memberships
    except Exception as error:
        if isinstance(error, OpeningReplayError):
            raise
        raise OpeningReplayError(
            f"{record.source_file} row {record.source_row_ordinal}: "
            f"relationship replay failed: {error}"
        ) from error


def derive_relationships(manifest: SourceManifest) -> RelationshipFacts:
    """Replay every source row and derive all approved relationship facts in memory."""

    records = tuple(
        sorted(manifest.records, key=lambda item: (item.source_file, item.source_row_ordinal))
    )
    paths: dict[SourceIdentity, list[MembershipFact]] = {}
    by_position: defaultdict[PositionKey, list[MembershipFact]] = defaultdict(list)
    endpoint_records: defaultdict[PositionKey, list[OpeningRecord]] = defaultdict(list)

    for record in records:
        identity = _source_identity(record.source_file, record.source_row_ordinal)
        path = _replay_memberships(record)
        paths[identity] = path
        endpoint_records[record.endpoint_key].append(record)
        for membership in path:
            by_position[membership.key].append(membership)

    parents: list[ParentFact] = []
    for record in records:
        identity = _source_identity(record.source_file, record.source_row_ordinal)
        candidates: list[tuple[int, OpeningRecord]] = []
        path = paths[identity]
        for membership in path[:-1]:
            for parent in endpoint_records[membership.key]:
                if _source_identity(parent.source_file, parent.source_row_ordinal) != identity:
                    candidates.append((membership.ply, parent))
        if candidates:
            deepest_ply = max(item[0] for item in candidates)
            for child_ply, parent in candidates:
                if child_ply == deepest_ply:
                    parents.append(
                        ParentFact(
                            record.source_file,
                            record.source_row_ordinal,
                            child_ply,
                            parent.source_file,
                            parent.source_row_ordinal,
                        )
                    )

    transpositions: list[TranspositionFact] = []
    for key, memberships in by_position.items():
        ordered = sorted(
            memberships,
            key=lambda item: (item.source_file, item.source_row_ordinal, item.ply),
        )
        for left_index, left in enumerate(ordered):
            left_identity = _source_identity(left.source_file, left.source_row_ordinal)
            for right in ordered[left_index + 1 :]:
                right_identity = _source_identity(right.source_file, right.source_row_ordinal)
                if left_identity == right_identity or left.uci_prefix == right.uci_prefix:
                    continue
                transpositions.append(
                    TranspositionFact(
                        key,
                        left.source_file,
                        left.source_row_ordinal,
                        left.ply,
                        left.uci_prefix,
                        right.source_file,
                        right.source_row_ordinal,
                        right.ply,
                        right.uci_prefix,
                    )
                )

    return RelationshipFacts(
        manifest.manifest_hash,
        manifest.record_count,
        tuple(sorted(by_position)),
        tuple(
            sorted(
                (membership for path in paths.values() for membership in path),
                key=lambda item: (item.source_file, item.source_row_ordinal, item.ply),
            )
        ),
        tuple(
            sorted(
                parents,
                key=lambda item: (
                    item.child_source_file,
                    item.child_source_row_ordinal,
                    item.child_ply,
                    item.parent_source_file,
                    item.parent_source_row_ordinal,
                ),
            )
        ),
        tuple(
            sorted(
                transpositions,
                key=lambda item: (
                    *item.key,
                    item.source_file_a,
                    item.source_row_ordinal_a,
                    item.ply_a,
                    item.source_file_b,
                    item.source_row_ordinal_b,
                    item.ply_b,
                ),
            )
        ),
    )
