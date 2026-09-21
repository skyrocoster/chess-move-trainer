"""Read-only discovery of trainer blunder occurrences."""

from __future__ import annotations

import math
from functools import cmp_to_key
from pathlib import Path

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .errors import (
    BlunderError,
    BlunderSchemaError,
    BlunderStorageError,
    BlunderValidationError,
)
from .loaders import _load_analyses, _load_occurrences, _load_scoped_games
from .models import BlunderItem, BlunderPage, BlunderPolicy, BlunderQuery
from .scoring import _compare_scored, _score_pair, _validate_transition


class BlunderRepository:
    """Discover trainer blunders through one explicit read-only schema path."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database_path = Path(database_path)
        self._lock_timeout = lock_timeout

    def discover(self, query: BlunderQuery, policy: BlunderPolicy) -> BlunderPage:
        """Return one finite, deterministic page of trainer blunders."""

        if not isinstance(query, BlunderQuery):
            raise BlunderValidationError("query must be a BlunderQuery value")
        if not isinstance(policy, BlunderPolicy):
            raise BlunderValidationError("policy must be a BlunderPolicy value")
        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                return _discover_connection(connection, query, policy)
        except SchemaIncompatibleError as error:
            raise BlunderSchemaError(str(error)) from error
        except BlunderError:
            raise
        except Exception as error:
            raise BlunderStorageError("blunders could not be read") from error


def discover_blunders(
    database_path: str | Path,
    query: BlunderQuery,
    policy: BlunderPolicy,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> BlunderPage:
    """Discover one page of trainer blunders from one explicit database path."""

    return BlunderRepository(database_path, lock_timeout=lock_timeout).discover(query, policy)


def _discover_connection(
    connection: object, query: BlunderQuery, policy: BlunderPolicy
) -> BlunderPage:
    games, examined_game_count, excluded_game_count = _load_scoped_games(connection, query)
    occurrences = _load_occurrences(connection, set(games))
    analyses = _load_analyses(connection, occurrences, games)

    threshold = policy.minimum_expected_score_loss
    found: list[tuple[float, str, str, int, BlunderItem]] = []
    trainer_move_count = 0
    comparable_move_count = 0
    for game_id, scope in games.items():
        ordered = occurrences.get(game_id, ())
        for index in range(len(ordered) - 1):
            before = ordered[index]
            after = ordered[index + 1]
            if after.ply != before.ply + 1:
                continue
            if before.move_uci is None:
                continue
            expected_side = "w" if scope.trainer_color == "white" else "b"
            if before.side_to_move != expected_side:
                continue
            trainer_move_count += 1
            _validate_transition(before, after)
            item = _score_pair(scope, before, after, analyses)
            if item is None:
                continue
            comparable_move_count += 1
            if item[0] >= threshold:
                found.append(item[1])

    found.sort(key=cmp_to_key(_compare_scored))
    total = len(found)
    total_pages = math.ceil(total / query.page_size)
    start = (query.page - 1) * query.page_size
    page_items = tuple(entry[4] for entry in found[start : start + query.page_size])
    return BlunderPage(
        started_at_from=query.started_at_from,
        started_at_to=query.started_at_to,
        policy=policy,
        items=page_items,
        page=query.page,
        page_size=query.page_size,
        total=total,
        total_pages=total_pages,
        has_next=query.page < total_pages,
        trainer_move_count=trainer_move_count,
        comparable_move_count=comparable_move_count,
        skipped_missing_analysis_count=trainer_move_count - comparable_move_count,
        examined_game_count=examined_game_count,
        excluded_game_count=excluded_game_count,
        in_scope_game_count=len(games),
    )


__all__ = ["BlunderRepository", "discover_blunders"]
