"""Run history, progress reporting, game selection, and validation."""

from __future__ import annotations

import sqlite3
import sys
import time
from datetime import datetime, timezone
from typing import TextIO

from ._errors import CorpusReplayError
from ._replay import fingerprint_game


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _select_games(
    connection: sqlite3.Connection, subject_uuid: str
) -> tuple[list[tuple[str, str, str, str]], list[tuple[str, str]]]:
    accepted: list[tuple[str, str, str, str]] = []
    excluded: list[tuple[str, str]] = []
    rows = connection.execute(
        "SELECT uuid, rules, white_player_uuid, black_player_uuid FROM games ORDER BY uuid"
    ).fetchall()
    for game_uuid, rules, white_uuid, black_uuid in rows:
        subject_count = (white_uuid == subject_uuid) + (black_uuid == subject_uuid)
        if rules == "chess" and subject_count == 1:
            accepted.append((game_uuid, rules, white_uuid, black_uuid))
        elif rules != "chess":
            excluded.append((game_uuid, f"rules={rules!r}; expected 'chess'"))
        else:
            excluded.append((game_uuid, f"subject ownership count={subject_count}; expected 1"))
    return accepted, excluded


def progress(
    completed: int,
    total: int,
    positions: int,
    started: float,
    output: TextIO | None = None,
) -> float:
    """Emit one compact progress update and return elapsed seconds."""

    stream = output or sys.stdout
    elapsed = max(0.0, time.monotonic() - started)
    percent = 100.0 * completed / total if total else 100.0
    text = (
        f"progress: {completed}/{total} ({percent:.1f}%) "
        f"positions={positions} elapsed={elapsed:.1f}s"
    )
    is_tty = bool(getattr(stream, "isatty", lambda: False)())
    print(f"\r{text}" if is_tty else text, end="" if is_tty else "\n", file=stream, flush=True)
    return elapsed


def write_run_history(
    connection: sqlite3.Connection,
    corpus_id: int,
    status: str,
    *,
    run_id: int | None = None,
    accepted_games: int = 0,
    excluded_games: int = 0,
    new_games: int = 0,
    changed_games: int = 0,
    removed_games: int = 0,
    unchanged_games: int = 0,
    ordered_positions: int = 0,
    unique_states: int = 0,
    validation: str = "pending",
    details: str | None = None,
) -> int:
    """Insert or finish a run-history row in its own short transaction."""

    now = _timestamp()
    if run_id is None:
        cursor = connection.execute(
            "INSERT INTO corpus_run "
            "(corpus_id, status, started_at, finished_at, accepted_games, excluded_games, "
            "new_games, changed_games, removed_games, unchanged_games, ordered_positions, "
            "unique_states, validation, details) "
            "VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                corpus_id,
                status,
                now,
                accepted_games,
                excluded_games,
                new_games,
                changed_games,
                removed_games,
                unchanged_games,
                ordered_positions,
                unique_states,
                validation,
                details,
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)
    connection.execute(
        "UPDATE corpus_run SET status = ?, finished_at = ?, accepted_games = ?, "
        "excluded_games = ?, new_games = ?, changed_games = ?, removed_games = ?, "
        "unchanged_games = ?, ordered_positions = ?, unique_states = ?, validation = ?, "
        "details = ? WHERE run_id = ? AND corpus_id = ?",
        (
            status,
            now,
            accepted_games,
            excluded_games,
            new_games,
            changed_games,
            removed_games,
            unchanged_games,
            ordered_positions,
            unique_states,
            validation,
            details,
            run_id,
            corpus_id,
        ),
    )
    connection.commit()
    return run_id


def reconcile_interrupted_runs(connection: sqlite3.Connection, corpus_id: int) -> None:
    rows = connection.execute(
        "SELECT run_id FROM corpus_run WHERE corpus_id = ? AND status = 'running'",
        (corpus_id,),
    ).fetchall()
    for (run_id,) in rows:
        connection.execute(
            "UPDATE corpus_run SET status = 'interrupted', finished_at = ?, "
            "validation = ?, details = ? WHERE run_id = ?",
            (
                _timestamp(),
                "stale running row reconciled",
                "reconciled before new extraction",
                run_id,
            ),
        )
    connection.commit()


_reconcile_stale_runs = reconcile_interrupted_runs


def _corpus_id(connection: sqlite3.Connection, subject_uuid: str) -> int:
    row = connection.execute(
        "SELECT corpus_id FROM corpus WHERE subject_player_uuid = ?", (subject_uuid,)
    ).fetchone()
    if row is None:
        raise RuntimeError(f"Corpus metadata is missing for subject {subject_uuid}")
    return int(row[0])


def diff_corpus(
    connection: sqlite3.Connection, subject_uuid: str
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Classify source games against the selected corpus membership."""

    corpus_id = _corpus_id(connection, subject_uuid)
    accepted, _ = _select_games(connection, subject_uuid)
    current = {
        row[0]: row[1]
        for row in connection.execute(
            "SELECT game_uuid, fingerprint FROM corpus_game WHERE corpus_id = ?",
            (corpus_id,),
        )
    }
    current_source = {game_uuid: fingerprint for game_uuid, fingerprint in current.items()}
    new: list[str] = []
    changed: list[str] = []
    unchanged: list[str] = []
    for game_uuid, _, _, _ in accepted:
        fingerprint = fingerprint_game(connection, game_uuid)
        old_fingerprint = current_source.pop(game_uuid, None)
        if old_fingerprint is None:
            new.append(game_uuid)
        elif old_fingerprint == fingerprint:
            unchanged.append(game_uuid)
        else:
            changed.append(game_uuid)
    removed = sorted(current_source)
    return sorted(new), sorted(changed), removed, sorted(unchanged)


def _validate_run(
    connection: sqlite3.Connection,
    corpus_id: int,
    subject_uuid: str,
    accepted: list[tuple[str, str, str, str]],
    excluded: list[tuple[str, str]],
    ordered_positions: int,
    state_ids: dict[tuple[str, str, str, str], int],
) -> tuple[int, str]:
    expected_ids = {row[0] for row in accepted}
    actual_ids = {
        row[0]
        for row in connection.execute(
            "SELECT game_uuid FROM corpus_game WHERE corpus_id = ?", (corpus_id,)
        )
    }
    if actual_ids != expected_ids:
        raise CorpusReplayError("accepted game membership is incomplete")
    bad_membership = connection.execute(
        "SELECT COUNT(*) FROM corpus_game cg JOIN games g ON g.uuid = cg.game_uuid "
        "WHERE cg.corpus_id = ? AND (g.rules <> 'chess' OR "
        "((g.white_player_uuid = ?) + (g.black_player_uuid = ?)) <> 1)",
        (corpus_id, subject_uuid, subject_uuid),
    ).fetchone()[0]
    if bad_membership:
        raise CorpusReplayError("corpus membership has invalid rules or subject ownership")
    actual_positions = connection.execute(
        "SELECT COUNT(*) FROM position_occurrence o JOIN corpus_game cg "
        "ON cg.game_uuid = o.game_uuid WHERE cg.corpus_id = ?",
        (corpus_id,),
    ).fetchone()[0]
    if actual_positions != ordered_positions:
        raise CorpusReplayError("ordered position count is inconsistent")
    invalid_refs = connection.execute(
        "SELECT COUNT(*) FROM position_occurrence o LEFT JOIN games g ON g.uuid = o.game_uuid "
        "LEFT JOIN position_state s ON s.state_id = o.state_id "
        "WHERE g.uuid IS NULL OR s.state_id IS NULL"
    ).fetchone()[0]
    orphan_states = connection.execute(
        "SELECT COUNT(*) FROM position_state s LEFT JOIN position_occurrence o "
        "ON o.state_id = s.state_id WHERE o.state_id IS NULL"
    ).fetchone()[0]
    if invalid_refs or orphan_states:
        raise CorpusReplayError("corpus references or unique-state rows are inconsistent")
    for game_uuid, reason in excluded:
        leftovers = connection.execute(
            "SELECT COUNT(*) FROM position_occurrence o JOIN corpus_game cg "
            "ON cg.game_uuid = o.game_uuid WHERE cg.corpus_id = ? AND o.game_uuid = ?",
            (corpus_id, game_uuid),
        ).fetchone()[0]
        if leftovers:
            raise CorpusReplayError(f"excluded game {game_uuid} remains in corpus: {reason}")
    unique_states = connection.execute("SELECT COUNT(*) FROM position_state").fetchone()[0]
    if unique_states != len(state_ids):
        raise CorpusReplayError("unique-state count is inconsistent")
    reasons: dict[str, int] = {}
    for _, reason in excluded:
        label = reason.split(";", 1)[0]
        reasons[label] = reasons.get(label, 0) + 1
    exclusion_text = ", ".join(f"{label} x{count}" for label, count in reasons.items()) or "none"
    validation = (
        f"complete; accepted_games={len(accepted)}; excluded_games={len(excluded)}; "
        f"ordered_positions={ordered_positions}; unique_states={unique_states}; "
        f"replay_failures=0; references=ok; ownership=ok; excluded={exclusion_text}"
    )
    return unique_states, validation
