"""Initialize and inspect the Chess.com position-corpus schema."""

from __future__ import annotations

import logging
import sqlite3
import sys
import time
from pathlib import Path
from typing import TextIO

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = "scripts.chess_com"

from ._cli import (
    DEFAULT_LOG,
    DEFAULT_SUBJECT,
    _subject_from_config,
    build_parser,
    configure_logging,
    report,
)  # noqa: F401
from ._errors import (  # noqa: F401
    CorpusBusyError,
    CorpusReplayError,
    CorpusSchemaError,
    ReplayError,
)
from ._history import (
    _corpus_id,
    _select_games,
    _validate_run,
    diff_corpus,
    progress,
    reconcile_interrupted_runs,
    write_run_history,
)
from ._persistence import (
    _persist_game,
    _remove_game_for_rebuild,
    _validate_persisted_game,
    load_state_ids,
    persist_fixture,  # noqa: F401
    remove_game_occurrences,
)  # noqa: F401
from ._replay import (  # noqa: F401
    STATE_FIELDS,
    build_fixture,
    build_states,
    fingerprint_game,
    replay_game,
)
from ._schema import SCHEMA_VERSION, ensure_corpus_schema, initialize_corpus  # noqa: F401

ROOT = Path(__file__).resolve().parents[2]


def publish(
    connection: sqlite3.Connection,
    subject_uuid: str = DEFAULT_SUBJECT,
    *,
    output: TextIO | None = None,
    logger: logging.Logger | None = None,
) -> dict[str, object]:
    """Atomically reconcile and publish the selected corpus."""

    try:
        ensure_corpus_schema(connection)
        corpus_id = _corpus_id(connection, subject_uuid)
        reconcile_interrupted_runs(connection, corpus_id)
        run_id = write_run_history(connection, corpus_id, "running")
    except sqlite3.OperationalError as error:
        if "locked" in str(error).lower() or "busy" in str(error).lower():
            raise CorpusBusyError(CorpusBusyError.MESSAGE) from error
        raise
    stream = output or sys.stdout
    started = time.monotonic()
    try:
        connection.execute("BEGIN IMMEDIATE")
        accepted, excluded = _select_games(connection, subject_uuid)
        new, changed, removed, unchanged = diff_corpus(connection, subject_uuid)
        for game_uuid in removed:
            remove_game_occurrences(connection, game_uuid, corpus_id)
        for game_uuid in changed:
            connection.execute(
                "DELETE FROM corpus_game WHERE corpus_id = ? AND game_uuid = ?",
                (corpus_id, game_uuid),
            )
            _remove_game_for_rebuild(connection, game_uuid)
        state_ids = load_state_ids(connection)
        ordered_positions = 0
        last_progress = 0.0
        work_ids = sorted(new + changed)
        for completed, game_uuid in enumerate(work_ids, start=1):
            occurrences, fingerprint = replay_game(connection, game_uuid)
            _persist_game(connection, corpus_id, game_uuid, occurrences, fingerprint, state_ids)
            now = time.monotonic()
            is_tty = bool(getattr(stream, "isatty", lambda: False)())
            if (
                is_tty
                or completed == len(work_ids)
                or completed % 100 == 0
                or now - last_progress >= 10
            ):
                progress(completed, len(work_ids), completed, started, stream)
                last_progress = now
        for game_uuid in unchanged:
            occurrences, _ = replay_game(connection, game_uuid)
            _validate_persisted_game(connection, game_uuid, occurrences)
        ordered_positions = connection.execute(
            "SELECT COUNT(*) FROM position_occurrence o JOIN corpus_game cg "
            "ON cg.game_uuid = o.game_uuid WHERE cg.corpus_id = ?",
            (corpus_id,),
        ).fetchone()[0]
        if not work_ids:
            progress(0, 0, 0, started, stream)
        if bool(getattr(stream, "isatty", lambda: False)()):
            print(file=stream)
        state_ids = load_state_ids(connection)
        unique_states, validation = _validate_run(
            connection,
            corpus_id,
            subject_uuid,
            accepted,
            excluded,
            ordered_positions,
            state_ids,
        )
        connection.commit()
        result = {
            "run_id": run_id,
            "accepted_games": len(accepted),
            "excluded_games": len(excluded),
            "new_games": len(new),
            "changed_games": len(changed),
            "removed_games": len(removed),
            "unchanged_games": len(unchanged),
            "ordered_positions": ordered_positions,
            "unique_states": unique_states,
            "validation": validation,
        }
        history_values = {key: value for key, value in result.items() if key != "run_id"}
        write_run_history(connection, corpus_id, "success", run_id=run_id, **history_values)
        if logger:
            logger.info("Published corpus: %s", validation)
        return result
    except KeyboardInterrupt as error:
        connection.rollback()
        write_run_history(
            connection,
            corpus_id,
            "interrupted",
            run_id=run_id,
            validation="publication rolled back",
            details="KeyboardInterrupt during corpus publication",
        )
        raise error
    except sqlite3.OperationalError as error:
        connection.rollback()
        if "locked" not in str(error).lower() and "busy" not in str(error).lower():
            write_run_history(
                connection,
                corpus_id,
                "failed",
                run_id=run_id,
                validation="publication rolled back",
                details=str(error)[:500],
            )
            raise
        try:
            write_run_history(
                connection,
                corpus_id,
                "failed",
                run_id=run_id,
                validation="publication rolled back",
                details=CorpusBusyError.MESSAGE,
            )
        except sqlite3.Error:
            connection.rollback()
        raise CorpusBusyError(CorpusBusyError.MESSAGE) from error
    except Exception as error:
        connection.rollback()
        write_run_history(
            connection,
            corpus_id,
            "failed",
            run_id=run_id,
            validation="publication rolled back",
            details=str(error)[:500],
        )
        raise


def run_extraction(
    connection: sqlite3.Connection,
    subject_uuid: str = DEFAULT_SUBJECT,
    *,
    output: TextIO | None = None,
    logger: logging.Logger | None = None,
) -> dict[str, object]:
    """Run one incremental extraction and atomically publish it."""

    return publish(connection, subject_uuid, output=output, logger=logger)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.init and args.report:
        print("--init and --report cannot be combined", file=sys.stderr)
        return 1
    try:
        subject_uuid = args.subject or _subject_from_config(args.config)
        if args.report:
            report(args.db)
            return 0
        logger = configure_logging(DEFAULT_LOG)
        if args.init:
            initialize_corpus(args.db, subject_uuid, logger)
            return 0
        connection = sqlite3.connect(args.db, timeout=0)
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            run_extraction(connection, subject_uuid, logger=logger)
        finally:
            connection.close()
        return 0
    except (OSError, RuntimeError, sqlite3.Error, CorpusReplayError) as error:
        logger = logging.getLogger("chess_com_corpus")
        if logger.handlers:
            logger.error("Corpus operation failed: %s", error)
        elif args.report:
            print(f"Corpus report failed: {error}", file=sys.stderr)
        elif args.init:
            print(f"Corpus initialization failed: {error}", file=sys.stderr)
        else:
            print(f"Corpus extraction failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
