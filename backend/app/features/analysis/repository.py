"""Transactional persistence for complete current analysis results."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass

from .errors import AnalysisBusyError
from .models import (
    AnalysisProfile,
    AnalysisResult,
    PositionKey,
    ResultEligibility,
    canonical_fen,
    position_key_from_fen,
)
from .schema import ANALYSIS_SCHEMA_VERSION, require_analysis_schema


class AnalysisRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def eligibility(self, fen: str, profile: AnalysisProfile) -> ResultEligibility:
        require_analysis_schema(self._connection)
        selected_fen = canonical_fen(fen)
        selected_key = position_key_from_fen(selected_fen)
        row = self._fetch_eligibility_rows((selected_key,)).get(selected_key)
        return self._eligibility_from_row(row, profile)

    def eligibilities(
        self, fens: Sequence[str], profile: AnalysisProfile
    ) -> dict[str, ResultEligibility]:
        """Inspect many exact-FEN identities in bounded read-only queries."""

        require_analysis_schema(self._connection)
        selected_fens = tuple(canonical_fen(fen) for fen in fens)
        selected_keys = tuple(position_key_from_fen(fen) for fen in selected_fens)
        rows = self._fetch_eligibility_rows(selected_keys)
        return {
            fen: self._eligibility_from_row(rows.get(key), profile)
            for fen, key in zip(selected_fens, selected_keys)
        }

    def _fetch_eligibility_rows(
        self, position_keys: Sequence[PositionKey]
    ) -> dict[PositionKey, tuple[object, ...]]:
        found: dict[PositionKey, tuple[object, ...]] = {}
        columns = (
            "position_key, schema_version, profile_id, settings_json, settings_fingerprint, "
            "engine_binary_sha256, engine_name, engine_version"
        )
        for start in range(0, len(position_keys), 500):
            chunk = tuple(position_keys[start : start + 500])
            if not chunk:
                continue
            placeholders = ",".join("?" for _ in chunk)
            found.update(
                {
                    PositionKey(str(row[0])): tuple(row[1:])
                    for row in self._connection.execute(
                        f"SELECT {columns} FROM analysis_result "
                        f"WHERE position_key IN ({placeholders})",
                        chunk,
                    ).fetchall()
                }
            )
        return found

    @staticmethod
    def _eligibility_from_row(
        row: tuple[object, ...] | None, profile: AnalysisProfile
    ) -> ResultEligibility:
        if row is None:
            return ResultEligibility.MISSING
        if tuple(row) == (
            ANALYSIS_SCHEMA_VERSION,
            profile.profile_id,
            profile.settings_json,
            profile.fingerprint,
            profile.engine_binary_sha256,
            profile.engine_name,
            profile.engine_version,
        ):
            return ResultEligibility.ELIGIBLE
        return ResultEligibility.STALE

    def publish(self, result: AnalysisResult) -> None:
        """Atomically publish a completely validated result and all candidate rows."""

        require_analysis_schema(self._connection)
        values = (
            result.position_key,
            result.fen,
            ANALYSIS_SCHEMA_VERSION,
            result.profile.profile_id,
            result.profile.settings_json,
            result.profile.fingerprint,
            result.profile.engine_binary_sha256,
            result.profile.engine_name,
            result.profile.engine_version,
            result.terminal_kind,
            len(result.candidates),
            result.completed_at,
            result.wall_time_ms,
        )
        try:
            _begin_immediate(self._connection)
            updated = self._connection.execute(
                "UPDATE analysis_result SET schema_version=?, profile_id=?, settings_json=?, "
                "settings_fingerprint=?, engine_binary_sha256=?, engine_name=?, engine_version=?, "
                "terminal_kind=?, candidate_count=?, completed_at=?, wall_time_ms=?, fen=? "
                "WHERE position_key=?",
                values[2:] + (result.fen, result.position_key),
            ).rowcount
            if not updated:
                self._connection.execute(
                    "INSERT INTO analysis_result "
                    "(position_key, fen, schema_version, profile_id, settings_json,\n"
                    "settings_fingerprint, "
                    "engine_binary_sha256, engine_name, engine_version, terminal_kind, "
                    "candidate_count, completed_at, wall_time_ms) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    values,
                )
            else:
                self._connection.execute(
                    "DELETE FROM analysis_candidate WHERE position_key = ?", (result.position_key,)
                )
            self._connection.executemany(
                "INSERT INTO analysis_candidate "
                "(position_key, fen, rank, score_kind, score_value, wdl_wins, wdl_draws,\n"
                "wdl_losses, "
                "pv_uci_json, depth, seldepth, nodes, engine_time_ms) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        result.position_key,
                        result.fen,
                        candidate.rank,
                        candidate.score_kind,
                        candidate.score_value,
                        candidate.wdl_wins,
                        candidate.wdl_draws,
                        candidate.wdl_losses,
                        json.dumps(candidate.pv_uci, separators=(",", ":")),
                        candidate.depth,
                        candidate.seldepth,
                        candidate.nodes,
                        candidate.engine_time_ms,
                    )
                    for candidate in result.candidates
                ],
            )
            self._connection.commit()
        except AnalysisBusyError:
            self._connection.rollback()
            raise
        except sqlite3.OperationalError as error:
            self._connection.rollback()
            if _is_busy(error):
                raise AnalysisBusyError(
                    "analysis coordinator could not complete SQLite writer transaction"
                ) from error
            raise
        except Exception:
            self._connection.rollback()
            raise

    def append_batch(
        self,
        *,
        status: str,
        selection_json: str,
        settings_fingerprint: str,
        started_at: str,
        finished_at: str,
        selected_positions: int,
        eligible_positions: int,
        completed_positions: int,
        failed_positions: int,
        details: str | None,
        failures: Sequence["FinalPositionFailure"] = (),
    ) -> int:
        """Append one immutable batch summary and its final failures atomically."""

        require_analysis_schema(self._connection)
        try:
            _begin_immediate(self._connection)
            cursor = self._connection.execute(
                "INSERT INTO analysis_batch_run "
                "(status, selection_json, settings_fingerprint, started_at, finished_at, "
                "selected_positions, eligible_positions, completed_positions, failed_positions, "
                "details) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    status,
                    selection_json,
                    settings_fingerprint,
                    started_at,
                    finished_at,
                    selected_positions,
                    eligible_positions,
                    completed_positions,
                    failed_positions,
                    details,
                ),
            )
            run_id = int(cursor.lastrowid)
            self._connection.executemany(
                "INSERT INTO analysis_position_failure "
                "(run_id, fen, settings_fingerprint, attempts, error_code, details, failed_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        run_id,
                        failure.fen,
                        settings_fingerprint,
                        failure.attempts,
                        failure.error_code,
                        failure.details,
                        failure.failed_at,
                    )
                    for failure in failures
                ],
            )
            self._connection.commit()
            return run_id
        except AnalysisBusyError:
            self._connection.rollback()
            raise
        except sqlite3.OperationalError as error:
            self._connection.rollback()
            if _is_busy(error):
                raise AnalysisBusyError(
                    "analysis coordinator could not append SQLite run record"
                ) from error
            raise
        except Exception:
            self._connection.rollback()
            raise


@dataclass(frozen=True)
class FinalPositionFailure:
    fen: str
    attempts: int
    error_code: str
    details: str
    failed_at: str


def _begin_immediate(connection: sqlite3.Connection) -> None:
    try:
        connection.execute("BEGIN IMMEDIATE")
    except sqlite3.OperationalError as error:
        if _is_busy(error):
            raise AnalysisBusyError(
                "analysis coordinator could not acquire SQLite writer lock"
            ) from error
        raise


def _is_busy(error: sqlite3.Error) -> bool:
    message = str(error).lower()
    return "locked" in message or "busy" in message
