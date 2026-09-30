"""Resumable game-atomic extraction from a verified frozen snapshot."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import chess

from chess_move_trainer.database.connection import _create_sqlite_connection
from chess_move_trainer.database.games.normalization import _parse_pgn
from chess_move_trainer.database.positions import canonicalize_board

from .artifacts import Budget, digest, read_json, write_json
from .features import ReplayState, move_features
from .readers import (
    AnalysisCache,
    load_openings,
    load_preferences,
    preference_at,
    time_control,
    timestamp,
)
from .scoring import engine_features, outcomes
from .snapshot import code_provenance, verify_snapshot


def _position_matches(board, row):
    return (
        tuple(asdict(canonicalize_board(board)).values())
        == tuple(
            row[k]
            for k in (
                "dp_placement",
                "dp_side_to_move",
                "dp_castling_rights",
                "dp_legal_en_passant",
            )
        )
        and board.halfmove_clock == row["dgp_halfmove_clock"]
        and board.fullmove_number == row["dgp_fullmove_number"]
    )


def replay_game(game, rows, analyses, openings, preferences, budget):
    parsed = _parse_pgn(game["dg_original_pgn"])
    board = parsed.board()
    if parsed.headers.get("Variant", "Standard") not in ("Standard", "Chess") or board.chess960:
        raise ValueError("unsupported_variant")
    if board.fen() != chess.STARTING_FEN:
        raise ValueError("nonstandard_start")
    moves = list(parsed.mainline_moves())
    if not moves or len(rows) != len(moves) + 1:
        raise ValueError("occurrence_count_mismatch")
    if [r["dgp_ply"] for r in rows] != list(range(len(rows))):
        raise ValueError("nonconsecutive_plies")
    if rows[-1]["dgp_move_uci"] is not None:
        raise ValueError("final_outgoing_move")
    date = timestamp(game["dg_started_at_utc"])
    tc = time_control(game["dg_time_control_source"])
    state = ReplayState()
    trainer = game["dg_trainer_color"] == "white"
    trainer_rating, opponent_rating = game["dg_trainer_rating"], game["dg_opponent_rating"]
    metadata = {
        "game_id": game["dg_chesscom_game_uuid"],
        "source_url": game["dg_source_url"],
        "learner_id": game["dg_trainer_chesscom_uuid"],
        "opponent_id": game["dg_opponent_chesscom_uuid"],
        "learner_color": game["dg_trainer_color"],
        "learner_rating": trainer_rating,
        "rating_difference": trainer_rating - opponent_rating
        if trainer_rating is not None and opponent_rating is not None
        else None,
        "started_at": date.isoformat() if date else None,
        "calendar_period": date.strftime("%Y-%m") if date else None,
        "time_class": game["dg_time_class"] or "unknown",
        "time_control": tc,
        "game_result": game["dg_trainer_outcome"],
        "termination": game["dg_termination_reason"] or "unknown",
    }
    records, played = [], []
    opening = "unknown"
    opening_match = None
    position_counts = Counter()
    for index, move in enumerate(moves):
        budget.check()
        row, next_row = rows[index : index + 2]
        if not _position_matches(board, row) or row["dgp_move_uci"] != move.uci():
            raise ValueError("pgn_occurrence_mismatch")
        if move not in board.legal_moves or board.is_game_over(claim_draw=False):
            raise ValueError("illegal_move_or_terminal_before")
        canonical = canonicalize_board(board)
        position_counts[canonical] += 1
        matched = openings.get(canonical, ())
        if matched:
            exact = [r for r in matched if r.moves_uci == tuple(played)]
            choice = min(exact or matched, key=lambda r: (r.eco, r.name))
            opening = choice.eco[0]  # Fixed A–E adjustment; no future/deepest label.
            opening_match = "route" if exact else "transposition"
        feature = move_features(board, move, index + 1, state)
        before, before_error = analyses[row["derived_position_id"]]
        following, after_error = analyses[next_row["derived_position_id"]]
        after = board.copy(stack=True)
        after.push(move)
        if not _position_matches(after, next_row):
            raise ValueError("next_position_mismatch")
        repetition_possible = max(position_counts.values()) >= 2
        history = (
            board.halfmove_clock >= 99
            or after.halfmove_clock >= 99
            or (
                repetition_possible
                and (
                    board.can_claim_threefold_repetition() or after.can_claim_threefold_repetition()
                )
            )
        )
        preferred = preference_at(
            preferences, row["derived_position_id"], date.date().isoformat() if date else None
        )
        if preferred is not None and chess.Move.from_uci(preferred) not in board.legal_moves:
            raise ValueError("illegal_dated_preference")
        score = outcomes(board, after, before, following)
        issues = []
        if before_error:
            issues.append("invalid_before_analysis")
        if after_error:
            issues.append("invalid_after_analysis")
        if score["before_score_source"] == "missing_analysis":
            issues.append("missing_before_analysis")
        if score["after_score_source"] == "missing_analysis":
            issues.append("missing_after_analysis")
        if before_error or after_error:
            # Even when a terminal can be scored, malformed stored evidence is not trusted.
            score.update(
                {
                    k: None
                    for k in (
                        "signed_loss_units",
                        "loss_units",
                        "loss",
                        "severe",
                        "severe_010",
                        "severe_030",
                    )
                }
            )
        record = {
            **metadata,
            **feature,
            **score,
            **engine_features(board, move, before),
            "ply": index + 1,
            "position_id": row["derived_position_id"],
            "after_position_id": next_row["derived_position_id"],
            "population": "learner" if board.turn == trainer else "opponent",
            "fen_before": board.fen(),
            "fen_after": after.fen(),
            "played_move": move.uci(),
            "opening": opening,
            "opening_match": opening_match,
            "preferred_move": preferred,
            "adherent": move.uci() == preferred if preferred else None,
            "history_sensitive": history,
            "issues": issues,
            "before_analysis": _provenance(before),
            "after_analysis": _provenance(following),
        }
        records.append(record)
        state.apply(board, move)
        board.push(move)
        played.append(move.uci())
    # Sequences are added only after complete replay validation; do not leak into adjustment.
    from .sequences import enrich_sequences, summarize_game

    enrich_sequences(records)
    return records, summarize_game(records, metadata)


RECORD_VERSION = "records-v1"


def _provenance(result):
    if result is None:
        return None
    return {
        "quality": result.quality.value,
        "engine": result.engine_name,
        "version": result.engine_version,
        "configuration": result.configuration_version,
        "settings": result.settings,
        "depth": result.lines[0].depth if result.lines else None,
        "score_kind": result.lines[0].score_kind.value if result.lines else None,
    }


def extract(directory: Path, *, seconds=300, max_games=None):
    budget = Budget(seconds)
    manifest = verify_snapshot(directory, budget)
    pilot_path = directory / "pilot.json"
    pilot = read_json(pilot_path) if pilot_path.exists() else None
    if pilot is not None:
        if pilot.get("status") not in ("ready_for_extraction", "complete"):
            raise ValueError("pilot snapshot is not ready for extraction")
        if manifest.get("pilot_identity") not in (None, pilot.get("identity")):
            raise ValueError("pilot and subset snapshot identities disagree")
    source = _create_sqlite_connection(directory / "snapshot.db", "read-only", 5)
    source.row_factory = sqlite3.Row
    target = sqlite3.connect(directory / "records.db", timeout=5)
    target.executescript("""
        CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY, uuid TEXT NOT NULL,
            status TEXT NOT NULL, reason TEXT, fingerprint TEXT, record TEXT);
        CREATE TABLE IF NOT EXISTS moves (game INTEGER NOT NULL, ply INTEGER NOT NULL,
            record TEXT NOT NULL, PRIMARY KEY(game, ply));
    """)
    identity = digest(
        {
            "snapshot": manifest["snapshot_sha256"],
            "protocol": manifest["protocol_sha256"],
            "records": RECORD_VERSION,
        }
    )
    provenance = code_provenance()
    try:
        previous = target.execute("SELECT value FROM metadata WHERE key='identity'").fetchone()
        if previous and previous[0] != identity:
            raise ValueError(
                "extractor changed; use a fresh snapshot/run instead of mixing records"
            )
        target.execute("INSERT OR IGNORE INTO metadata VALUES ('identity', ?)", (identity,))
        target.commit()
        learners = [
            r[0]
            for r in source.execute("SELECT DISTINCT dg_trainer_chesscom_uuid FROM datasource_game")
        ]
        if len(learners) > 1:
            raise ValueError("multiple learner identities require separate approved populations")
        openings, preferences = load_openings(source), load_preferences(source)
        cache = AnalysisCache(source)
        done = {row[0] for row in target.execute("SELECT id FROM games")}
        completed_now = 0
        for game in source.execute("SELECT * FROM datasource_game ORDER BY dg_game_id"):
            if game["dg_game_id"] in done:
                continue
            budget.check()
            if max_games is not None and completed_now >= max_games:
                break
            rows = source.execute(
                """SELECT gp.*, p.* FROM derived_game_position gp
                JOIN derived_position p ON gp.derived_position_id=p.dp_position_id
                WHERE datasource_game_id=? ORDER BY dgp_ply""",
                (game["dg_game_id"],),
            ).fetchall()
            analysis = cache.load([r["derived_position_id"] for r in rows])
            records, summary, reason = [], None, None
            try:
                records, summary = replay_game(game, rows, analysis, openings, preferences, budget)
            except (ValueError, KeyError, TypeError, IndexError) as error:
                reason = f"{type(error).__name__}: {error}"
            fingerprint = digest(
                {
                    "moves": [r["dgp_move_uci"] for r in rows],
                    "started": game["dg_started_at_utc"],
                    "learner": game["dg_trainer_chesscom_uuid"],
                    "opponent": game["dg_opponent_chesscom_uuid"],
                }
            )
            with target:
                target.execute(
                    "INSERT INTO games VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        game["dg_game_id"],
                        game["dg_chesscom_game_uuid"],
                        "excluded" if reason else "valid",
                        reason,
                        fingerprint,
                        json.dumps(summary, allow_nan=False),
                    ),
                )
                target.executemany(
                    "INSERT INTO moves VALUES (?, ?, ?)",
                    (
                        (game["dg_game_id"], r["ply"], json.dumps(r, allow_nan=False))
                        for r in records
                    ),
                )
            completed_now += 1
            if completed_now % 100 == 0:
                processed = target.execute("SELECT COUNT(*) FROM games").fetchone()[0]
                write_json(
                    directory / "extraction.progress.json",
                    {
                        "status": "run_incomplete",
                        "processed_games": processed,
                        "completed_this_call": completed_now,
                        "identity": identity,
                    },
                )
        total = source.execute("SELECT COUNT(*) FROM datasource_game").fetchone()[0]
        processed = target.execute("SELECT COUNT(*) FROM games").fetchone()[0]
        report = {
            "status": "complete" if processed == total else "run_incomplete",
            "total_games": total,
            "processed_games": processed,
            "identity": identity,
            "records_version": RECORD_VERSION,
            "extractor_source_sha256": provenance["source_sha256"],
            "learner_ids": learners,
            "snapshot_sha256": manifest["snapshot_sha256"],
            "protocol_sha256": manifest["protocol_sha256"],
        }
        if pilot is not None:
            report["pilot_identity"] = pilot["identity"]
        write_json(directory / "extraction.json", report)
        if pilot is not None and report["status"] == "complete":
            pilot.update(status="complete", extraction_identity=identity)
            write_json(pilot_path, pilot)
        return report
    except BaseException as error:
        try:
            processed = target.execute("SELECT COUNT(*) FROM games").fetchone()[0]
        except Exception:
            processed = None
        write_json(
            directory / "extraction.json",
            {
                "status": "run_incomplete",
                "error": str(error),
                "processed_games": processed,
                "identity": identity,
            },
        )
        raise
    finally:
        source.close()
        target.close()
