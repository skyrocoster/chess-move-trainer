"""Game replay, fingerprinting, and state building."""

from __future__ import annotations

import hashlib
import io
import json
import sqlite3
from collections.abc import Iterable

import chess
import chess.pgn

from ._errors import CorpusReplayError

STATE_FIELDS = ("placement", "side_to_move", "castling", "en_passant")


def _canonical_fingerprint(
    pgn: str, initial_setup: str | None, fen: str | None, rules: str | None
) -> str:
    source = {
        "pgn": pgn,
        "initial_setup": initial_setup,
        "fen": fen,
        "rules": rules,
    }
    encoded = json.dumps(source, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def fingerprint_game(
    pgn: str | sqlite3.Connection,
    initial_setup: str | None = None,
    fen: str | None = None,
    rules: str | None = None,
) -> str:
    """Return the settled fingerprint for source fields or a source game row."""

    if isinstance(pgn, sqlite3.Connection):
        game_uuid = initial_setup
        if game_uuid is None:
            raise CorpusReplayError("fingerprint_game requires a game UUID")
        row = pgn.execute(
            "SELECT pgn, initial_setup, fen, rules FROM games WHERE uuid = ?",
            (game_uuid,),
        ).fetchone()
        if row is None:
            raise CorpusReplayError(f"game {game_uuid}: source row is missing")
        pgn, initial_setup, fen, rules = row
    return _canonical_fingerprint(pgn, initial_setup, fen, rules)


def _fen_record(
    game_uuid: str, ply: int, san: str | None, uci: str | None, board: chess.Board
) -> dict[str, object]:
    fen = board.fen(en_passant="fen")
    fields = fen.split()
    if len(fields) != 6:
        raise CorpusReplayError(f"game {game_uuid}: generated FEN has {len(fields)} fields")
    return {
        "game_uuid": game_uuid,
        "ply": ply,
        "san": san,
        "uci": uci,
        "fen": fen,
        "key": " ".join(fields[:4]),
        "placement": fields[0],
        "side_to_move": fields[1],
        "castling": fields[2],
        "en_passant": fields[3],
        "halfmove_clock": int(fields[4]),
        "fullmove_number": int(fields[5]),
    }


def _verify_source_fen(game_uuid: str, final_fen: str, source_fen: str | None, label: str) -> None:
    if source_fen is None:
        return
    source_fields = " ".join(source_fen.split()).split()
    if len(source_fields) not in (4, 6):
        raise CorpusReplayError(
            f"game {game_uuid}: {label} has {len(source_fields)} FEN fields; expected 4 or 6"
        )
    if final_fen.split()[: len(source_fields)] != source_fields:
        raise CorpusReplayError(
            f"game {game_uuid}: final position does not match {label}: "
            f"generated={final_fen!r}, source={source_fen!r}"
        )


def replay_game(
    connection: sqlite3.Connection, game_uuid: str
) -> tuple[list[dict[str, object]], str]:
    row = connection.execute(
        "SELECT uuid, pgn, initial_setup, fen, rules FROM games WHERE uuid = ?",
        (game_uuid,),
    ).fetchone()
    if row is None:
        raise CorpusReplayError(f"game {game_uuid}: source row is missing")
    _, raw_pgn, initial_setup, source_fen, rules = row
    if rules != "chess":
        raise CorpusReplayError(f"game {game_uuid}: rules={rules!r}, expected 'chess'")
    try:
        game = chess.pgn.read_game(io.StringIO(raw_pgn))
    except Exception as error:
        raise CorpusReplayError(f"game {game_uuid}: PGN failed to parse: {error}") from error
    if game is None:
        raise CorpusReplayError(f"game {game_uuid}: PGN parsed to an empty game")
    try:
        board = game.board()
    except Exception as error:
        raise CorpusReplayError(
            f"game {game_uuid}: starting position is invalid: {error}"
        ) from error

    occurrences = [_fen_record(game_uuid, 0, None, None, board)]
    try:
        for ply, move in enumerate(game.mainline_moves(), start=1):
            san = board.san(move)
            uci = move.uci()
            board.push(move)
            occurrences.append(_fen_record(game_uuid, ply, san, uci, board))
    except Exception as error:
        raise CorpusReplayError(
            f"game {game_uuid}: replay failed at ply {len(occurrences)}: {error}"
        ) from error
    if len(occurrences) == 1:
        raise CorpusReplayError(f"game {game_uuid}: PGN contains no moves")

    final_fen = occurrences[-1]["fen"]
    assert isinstance(final_fen, str)
    _verify_source_fen(game_uuid, final_fen, source_fen, "games.fen")
    _verify_source_fen(
        game_uuid,
        final_fen,
        game.headers.get("CurrentPosition"),
        "PGN CurrentPosition",
    )
    fingerprint = fingerprint_game(raw_pgn, initial_setup, source_fen, rules)
    return occurrences, fingerprint


def _state_tuple(occurrence: dict[str, object]) -> tuple[str, str, str, str]:
    try:
        return tuple(occurrence[field] for field in STATE_FIELDS)  # type: ignore[return-value]
    except KeyError as error:
        raise CorpusReplayError(f"missing state field {error.args[0]!r}") from error


def build_states(
    occurrences: Iterable[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    copied = [dict(occurrence) for occurrence in occurrences]
    keys = sorted({_state_tuple(occurrence) for occurrence in copied})
    state_ids = {key: index for index, key in enumerate(keys, start=1)}
    states = [
        dict(zip(("state_id", "key", *STATE_FIELDS), (state_ids[key], " ".join(key), *key)))
        for key in keys
    ]
    linked = []
    for occurrence in copied:
        occurrence["state_id"] = state_ids[_state_tuple(occurrence)]
        linked.append(occurrence)
    return states, linked


def build_fixture(connection: sqlite3.Connection, game_uuids: Iterable[str]) -> dict[str, object]:
    ordered_ids = sorted(game_uuids)
    if len(ordered_ids) != len(set(ordered_ids)):
        raise CorpusReplayError("fixture contains duplicate game UUIDs")
    games = []
    occurrences: list[dict[str, object]] = []
    for game_uuid in ordered_ids:
        game_occurrences, fingerprint = replay_game(connection, game_uuid)
        games.append({"game_uuid": game_uuid, "rules": "chess", "fingerprint": fingerprint})
        occurrences.extend(game_occurrences)
    states, linked = build_states(occurrences)
    return {"games": games, "states": states, "occurrences": linked}
