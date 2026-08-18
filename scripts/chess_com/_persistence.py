"""Corpus persistence: inserting and validating persisted fixtures and games."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable

from ._errors import CorpusReplayError
from ._replay import STATE_FIELDS, _state_tuple, build_fixture


def _validate_persisted_fixture(connection: sqlite3.Connection, payload: dict[str, object]) -> None:
    games = payload["games"]
    occurrences = payload["occurrences"]
    game_ids = [game["game_uuid"] for game in games]
    placeholders = ",".join("?" for _ in game_ids)
    actual = connection.execute(
        f"SELECT COUNT(*) FROM position_occurrence WHERE game_uuid IN ({placeholders})",
        game_ids,
    ).fetchone()[0]
    if actual != len(occurrences):
        raise CorpusReplayError("persisted occurrence count is inconsistent")
    linked = connection.execute(
        f"SELECT COUNT(*) FROM position_occurrence AS o "
        f"JOIN position_state AS s ON s.state_id = o.state_id "
        f"WHERE o.game_uuid IN ({placeholders})",
        game_ids,
    ).fetchone()[0]
    if linked != len(occurrences):
        raise CorpusReplayError("persisted occurrence references are inconsistent")


def persist_fixture(
    connection: sqlite3.Connection, corpus_id: int, game_uuids: Iterable[str]
) -> dict[str, object]:
    payload = build_fixture(connection, game_uuids)
    if (
        connection.execute("SELECT 1 FROM corpus WHERE corpus_id = ?", (corpus_id,)).fetchone()
        is None
    ):
        raise CorpusReplayError(f"corpus {corpus_id}: metadata row is missing")
    games = payload["games"]
    states = payload["states"]
    occurrences = payload["occurrences"]
    with connection:
        state_ids: dict[str, int] = {}
        for state in states:
            key = tuple(state[field] for field in STATE_FIELDS)
            row = connection.execute(
                "SELECT state_id FROM position_state WHERE placement = ? AND side_to_move = ? "
                "AND castling = ? AND en_passant = ?",
                key,
            ).fetchone()
            if row is None:
                cursor = connection.execute(
                    "INSERT INTO position_state (placement, side_to_move, castling, en_passant) "
                    "VALUES (?, ?, ?, ?)",
                    key,
                )
                state_ids[state["key"]] = cursor.lastrowid
            else:
                state_ids[state["key"]] = row[0]
        for game in games:
            connection.execute(
                "INSERT INTO corpus_game "
                "(corpus_id, game_uuid, rules, fingerprint) VALUES (?, ?, ?, ?)",
                (corpus_id, game["game_uuid"], game["rules"], game["fingerprint"]),
            )
        for occurrence in occurrences:
            connection.execute(
                "INSERT INTO position_occurrence "
                "(game_uuid, ply, state_id, san, uci, halfmove_clock, fullmove_number) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    occurrence["game_uuid"],
                    occurrence["ply"],
                    state_ids[occurrence["key"]],
                    occurrence["san"],
                    occurrence["uci"],
                    occurrence["halfmove_clock"],
                    occurrence["fullmove_number"],
                ),
            )
        _validate_persisted_fixture(connection, payload)
    return payload


def _clear_corpus(connection: sqlite3.Connection, corpus_id: int) -> None:
    old_games = [
        row[0]
        for row in connection.execute(
            "SELECT game_uuid FROM corpus_game WHERE corpus_id = ?", (corpus_id,)
        )
    ]
    for game_uuid in old_games:
        shared = connection.execute(
            "SELECT 1 FROM corpus_game WHERE game_uuid = ? AND corpus_id != ? LIMIT 1",
            (game_uuid, corpus_id),
        ).fetchone()
        if shared is None:
            connection.execute("DELETE FROM position_occurrence WHERE game_uuid = ?", (game_uuid,))
    connection.execute("DELETE FROM corpus_game WHERE corpus_id = ?", (corpus_id,))
    connection.execute(
        "DELETE FROM position_occurrence WHERE game_uuid NOT IN (SELECT game_uuid FROM corpus_game)"
    )
    connection.execute(
        "DELETE FROM position_state WHERE NOT EXISTS "
        "(SELECT 1 FROM position_occurrence WHERE state_id = position_state.state_id)"
    )


def _remove_orphan_states(connection: sqlite3.Connection) -> None:
    connection.execute(
        "DELETE FROM position_state WHERE NOT EXISTS "
        "(SELECT 1 FROM position_occurrence WHERE state_id = position_state.state_id)"
    )


def remove_game_occurrences(
    connection: sqlite3.Connection, game_uuid: str, corpus_id: int | None = None
) -> None:
    """Remove one corpus membership and unshared game-global occurrences."""

    if corpus_id is not None:
        connection.execute(
            "DELETE FROM corpus_game WHERE corpus_id = ? AND game_uuid = ?",
            (corpus_id, game_uuid),
        )
    shared = connection.execute(
        "SELECT 1 FROM corpus_game WHERE game_uuid = ? LIMIT 1", (game_uuid,)
    ).fetchone()
    if shared is None:
        connection.execute("DELETE FROM position_occurrence WHERE game_uuid = ?", (game_uuid,))
        _remove_orphan_states(connection)


def _remove_game_for_rebuild(connection: sqlite3.Connection, game_uuid: str) -> None:
    connection.execute("DELETE FROM position_occurrence WHERE game_uuid = ?", (game_uuid,))
    _remove_orphan_states(connection)


def load_state_ids(connection: sqlite3.Connection) -> dict[tuple[str, str, str, str], int]:
    rows = connection.execute(
        "SELECT state_id, placement, side_to_move, castling, en_passant FROM position_state"
    ).fetchall()
    return {tuple(row[1:]): int(row[0]) for row in rows}


def _persist_game(
    connection: sqlite3.Connection,
    corpus_id: int,
    game_uuid: str,
    occurrences: list[dict[str, object]],
    fingerprint: str,
    state_ids: dict[tuple[str, str, str, str], int],
) -> None:
    has_occurrences = connection.execute(
        "SELECT 1 FROM position_occurrence WHERE game_uuid = ? LIMIT 1", (game_uuid,)
    ).fetchone()
    if has_occurrences:
        _validate_persisted_game(connection, game_uuid, occurrences)
    else:
        rows = []
        for occurrence in occurrences:
            key = _state_tuple(occurrence)
            if key not in state_ids:
                connection.execute(
                    "INSERT OR IGNORE INTO position_state "
                    "(placement, side_to_move, castling, en_passant) VALUES (?, ?, ?, ?)",
                    key,
                )
                state_ids[key] = int(
                    connection.execute(
                        "SELECT state_id FROM position_state WHERE placement = ? "
                        "AND side_to_move = ? AND castling = ? AND en_passant = ?",
                        key,
                    ).fetchone()[0]
                )
            rows.append(
                (
                    game_uuid,
                    occurrence["ply"],
                    state_ids[key],
                    occurrence["san"],
                    occurrence["uci"],
                    occurrence["halfmove_clock"],
                    occurrence["fullmove_number"],
                )
            )
        connection.executemany(
            "INSERT INTO position_occurrence "
            "(game_uuid, ply, state_id, san, uci, halfmove_clock, fullmove_number) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
    connection.execute(
        "INSERT INTO corpus_game (corpus_id, game_uuid, rules, fingerprint) "
        "VALUES (?, ?, 'chess', ?)",
        (corpus_id, game_uuid, fingerprint),
    )


def _validate_persisted_game(
    connection: sqlite3.Connection, game_uuid: str, occurrences: list[dict[str, object]]
) -> None:
    actual = connection.execute(
        "SELECT o.ply, o.san, o.uci, s.placement, s.side_to_move, s.castling, s.en_passant, "
        "o.halfmove_clock, o.fullmove_number FROM position_occurrence o "
        "JOIN position_state s ON s.state_id = o.state_id WHERE o.game_uuid = ? ORDER BY o.ply",
        (game_uuid,),
    ).fetchall()
    expected = [
        (
            item["ply"],
            item["san"],
            item["uci"],
            *(_state_tuple(item)),
            item["halfmove_clock"],
            item["fullmove_number"],
        )
        for item in occurrences
    ]
    if actual != expected:
        raise CorpusReplayError(f"game {game_uuid}: persisted SAN/UCI/state records differ")
