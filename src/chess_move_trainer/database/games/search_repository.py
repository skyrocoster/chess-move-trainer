"""Game search repository and loaders."""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cmp_to_key
from pathlib import Path

from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..positions import canonicalize_fen
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .search_errors import (
    GameSearchError,
    GameSearchSchemaError,
    GameSearchStorageError,
    GameSearchValidationError,
)
from .search_filters import _compare_games, _coverage_state
from .search_loaders import _load_games
from .search_models import (
    DeepestOpening,
    GameCoverage,
    GameSearchPage,
    GameSearchQuery,
    GameSummary,
    _GameData,
)
from .search_validation import (
    _in_datetime_bounds,
    _opening_api_key,
    _parse_opening_key,
    _required_int,
    _required_text,
)


@dataclass(frozen=True, slots=True)
class _GameAggregates:
    """Per-game counts computed by one grouped SQL pass."""

    occurrence_count: int
    length_plies: int
    distinct_position_count: int
    analyzed_position_count: int
    preferred_position_count: int


class GameSearchRepository:
    """Search normalized games using one explicit read-only schema-v1 path."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database_path = Path(database_path)
        self._lock_timeout = lock_timeout

    def search(self, query: GameSearchQuery | None = None) -> GameSearchPage:
        """Return the finite page matching every supplied query filter."""

        request = GameSearchQuery() if query is None else query
        if not isinstance(request, GameSearchQuery):
            raise GameSearchValidationError("query must be a GameSearchQuery")
        filters = _sql_filter_clauses(request)
        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                games = _load_games(connection)
                aggregates = _aggregate_games(connection, filters)
                opening_filter_ids: list[int] | None = None
                if request.opening_key is not None and request.opening_match == "deepest":
                    opening_filter_ids = sorted(aggregates)
                deepest_by_game = (
                    _load_deepest_openings(connection, games, opening_filter_ids)
                    if opening_filter_ids is not None
                    else {}
                )
        except SchemaIncompatibleError as error:
            raise GameSearchSchemaError(str(error)) from error
        except GameSearchError:
            raise
        except Exception as error:
            raise GameSearchStorageError("games could not be read") from error

        matched = [
            (game_id, games[game_id], aggregates[game_id])
            for game_id in aggregates
            if _matches_aggregates(games[game_id], aggregates[game_id], request)
        ]
        if opening_filter_ids is not None:
            assert request.opening_key is not None
            filtered: list[tuple[int, _GameData, _GameAggregates]] = []
            for game_id, game, aggregate in matched:
                per_game = deepest_by_game.get(game_id)
                if per_game and _select_deepest(per_game).key == request.opening_key:
                    filtered.append((game_id, game, aggregate))
            matched = filtered
        summaries = [
            (game_id, _summarize_aggregates(game, aggregate, None))
            for game_id, game, aggregate in matched
        ]
        summaries.sort(
            key=cmp_to_key(lambda left, right: _compare_games(left[1], right[1], request.sort))
        )

        total = len(summaries)
        total_pages = math.ceil(total / request.page_size)
        start = (request.page - 1) * request.page_size
        page_entries = summaries[start : start + request.page_size]
        if opening_filter_ids is not None:
            page_deepest = {game_id: deepest_by_game[game_id] for game_id, _summary in page_entries}
        elif page_entries:
            try:
                with _open_connection(
                    self._database_path, "read-only", self._lock_timeout
                ) as connection:
                    _assert_compatible_schema(connection, self._lock_timeout)
                    page_deepest = _load_deepest_openings(
                        connection, games, [game_id for game_id, _summary in page_entries]
                    )
            except SchemaIncompatibleError as error:
                raise GameSearchSchemaError(str(error)) from error
            except GameSearchError:
                raise
            except Exception as error:
                raise GameSearchStorageError("games could not be read") from error
        else:
            page_deepest = {}
        page_items = tuple(
            _summarize_aggregates(
                games[game_id],
                aggregates[game_id],
                _select_deepest(page_deepest[game_id]) if page_deepest.get(game_id) else None,
            )
            for game_id, _summary in page_entries
        )
        return GameSearchPage(
            items=page_items,
            page=request.page,
            page_size=request.page_size,
            total=total,
            total_pages=total_pages,
            has_next=request.page < total_pages,
        )

    read = search
    query = search


def search_games(
    database_path: str | Path,
    query: GameSearchQuery | None = None,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> GameSearchPage:
    """Search one explicit database path without exposing a connection handle."""

    return GameSearchRepository(database_path, lock_timeout=lock_timeout).search(query)


@dataclass(frozen=True, slots=True)
class _SqlFilters:
    """WHERE fragments and parameters derived from one validated query."""

    clauses: tuple[str, ...]
    params: dict[str, object]


def _sql_filter_clauses(query: GameSearchQuery) -> _SqlFilters:
    """Translate provably safe scalar and EXISTS filters into SQL."""

    clauses: list[str] = []
    params: dict[str, object] = {}

    def _scalar(column: str, name: str, value: object) -> None:
        if value is not None:
            clauses.append(f"{column} = :{name}")
            params[name] = value

    def _bounds(column: str, name: str, lower: object, upper: object) -> None:
        if lower is not None:
            clauses.append(f"{column} >= :{name}_min")
            params[f"{name}_min"] = lower
        if upper is not None:
            clauses.append(f"{column} <= :{name}_max")
            params[f"{name}_max"] = upper

    _scalar("g.dg_trainer_color", "trainer_color", query.trainer_color)
    _scalar("g.dg_trainer_outcome", "trainer_outcome", query.trainer_outcome)
    _bounds(
        "g.dg_trainer_rating", "trainer_rating", query.trainer_rating_min, query.trainer_rating_max
    )
    _bounds(
        "g.dg_opponent_rating",
        "opponent_rating",
        query.opponent_rating_min,
        query.opponent_rating_max,
    )
    _scalar("g.dg_opponent_chesscom_uuid", "opponent_uuid", query.opponent_chesscom_uuid)
    _scalar("g.dg_time_class", "time_class", query.time_class)
    _scalar("g.dg_time_control_source", "time_control", query.time_control)

    if query.contains_fen is not None:
        expected = canonicalize_fen(query.contains_fen)
        clauses.append(
            """EXISTS (
                SELECT 1
                FROM derived_game_position AS o2
                JOIN derived_position AS p2
                  ON p2.dp_position_id = o2.derived_position_id
                WHERE o2.datasource_game_id = g.dg_game_id
                  AND p2.dp_placement = :contains_placement
                  AND p2.dp_side_to_move = :contains_side
                  AND p2.dp_castling_rights = :contains_castling
                  AND p2.dp_legal_en_passant = :contains_en_passant
            )"""
        )
        params.update(
            {
                "contains_placement": expected.placement,
                "contains_side": expected.side_to_move,
                "contains_castling": expected.castling_rights,
                "contains_en_passant": expected.legal_en_passant,
            }
        )
    if query.move_fen is not None:
        assert query.move_uci is not None
        expected = canonicalize_fen(query.move_fen)
        clauses.append(
            """EXISTS (
                SELECT 1
                FROM derived_game_position AS o2
                JOIN derived_position AS p2
                  ON p2.dp_position_id = o2.derived_position_id
                WHERE o2.datasource_game_id = g.dg_game_id
                  AND p2.dp_placement = :move_placement
                  AND p2.dp_side_to_move = :move_side
                  AND p2.dp_castling_rights = :move_castling
                  AND p2.dp_legal_en_passant = :move_en_passant
                  AND o2.dgp_move_uci = :move_uci
            )"""
        )
        params.update(
            {
                "move_placement": expected.placement,
                "move_side": expected.side_to_move,
                "move_castling": expected.castling_rights,
                "move_en_passant": expected.legal_en_passant,
                "move_uci": query.move_uci,
            }
        )
    if query.opening_key is not None and query.opening_match == "reached":
        eco, name = _parse_opening_key(query.opening_key)
        clauses.append(
            """EXISTS (
                SELECT 1
                FROM derived_game_position AS gp
                JOIN derived_opening_route AS r
                  ON r.derived_position_id = gp.derived_position_id
                JOIN datasource_opening AS o
                  ON o.do_opening_id = r.datasource_opening_id
                WHERE gp.datasource_game_id = g.dg_game_id
                  AND o.do_eco = :opening_eco
                  AND o.do_name = :opening_name
            )"""
        )
        params.update({"opening_eco": eco, "opening_name": name})
    return _SqlFilters(clauses=tuple(clauses), params=params)


def _aggregate_games(connection: object, filters: _SqlFilters) -> dict[int, _GameAggregates]:
    # Three join-driven grouped passes replace per-row EXISTS probes: the base
    # pass scans occurrences once, while the coverage passes drive from the
    # much smaller analysis/preferred tables. No schema or index change.
    # Stored components are trusted as canonical (and typed by schema NOT NULL
    # plus TEXT affinity), so occurrence identity is the position id, which the
    # UNIQUE component constraint keeps in 1:1 correspondence with the
    # four-field canonical position.
    where = f"WHERE {' AND '.join(filters.clauses)}" if filters.clauses else ""
    try:
        base_rows = connection.execute(
            text(
                f"""
                SELECT g.dg_game_id,
                       COUNT(o.derived_position_id),
                       COALESCE(MAX(o.dgp_ply), 0),
                       COUNT(DISTINCT o.derived_position_id)
                FROM datasource_game AS g
                LEFT JOIN derived_game_position AS o
                  ON o.datasource_game_id = g.dg_game_id
                {where}
                GROUP BY g.dg_game_id
                ORDER BY g.dg_game_id
                """
            ),
            filters.params,
        ).all()
        analyzed_rows = connection.execute(
            text(
                """
                SELECT o.datasource_game_id, COUNT(DISTINCT o.derived_position_id)
                FROM derived_game_position AS o
                JOIN derived_analysis_result AS a
                  ON a.derived_position_id = o.derived_position_id
                GROUP BY o.datasource_game_id
                """
            )
        ).all()
        preferred_rows = connection.execute(
            text(
                """
                SELECT o.datasource_game_id, COUNT(DISTINCT o.derived_position_id)
                FROM derived_game_position AS o
                JOIN datasource_preferred_move_period AS m
                  ON m.derived_position_id = o.derived_position_id
                GROUP BY o.datasource_game_id
                """
            )
        ).all()
    except GameSearchError:
        raise
    except Exception as error:
        raise GameSearchStorageError("games could not be read") from error
    aggregates: dict[int, _GameAggregates] = {}
    try:
        analyzed = {_required_int(row[0], "coverage game id"): row[1] for row in analyzed_rows}
        preferred = {_required_int(row[0], "coverage game id"): row[1] for row in preferred_rows}
        for row in base_rows:
            game_id = _required_int(row[0], "game id")
            if game_id in aggregates:
                raise GameSearchStorageError("game identifiers are duplicated")
            aggregates[game_id] = _GameAggregates(
                occurrence_count=_required_int(row[1], "occurrence count"),
                length_plies=_required_int(row[2], "length plies"),
                distinct_position_count=_required_int(row[3], "distinct position count"),
                analyzed_position_count=_required_int(
                    analyzed.get(game_id, 0), "analyzed position count"
                ),
                preferred_position_count=_required_int(
                    preferred.get(game_id, 0), "preferred position count"
                ),
            )
    except GameSearchError:
        raise
    except (IndexError, TypeError, ValueError) as error:
        raise GameSearchStorageError("game aggregate row is malformed") from error
    return aggregates


def _load_deepest_openings(
    connection: object,
    games: dict[int, _GameData],
    game_ids: list[int] | None,
) -> dict[int, dict[str, tuple[str, str, int]]]:
    if game_ids is not None and not game_ids:
        return {}
    chunks: list[list[int]] = []
    if game_ids is None:
        chunks.append([])
    else:
        seen: set[int] = set()
        current: list[int] = []
        for game_id in game_ids:
            if game_id in seen:
                continue
            seen.add(game_id)
            current.append(game_id)
            if len(current) >= 500:
                chunks.append(current)
                current = []
        if current:
            chunks.append(current)
    opening_matches: dict[int, dict[str, tuple[str, str, int]]] = {}
    try:
        for chunk in chunks:
            predicate = ""
            if chunk:
                # Chunk entries are integer game identifiers already validated by
                # _load_games, so formatting them here cannot inject SQL text.
                predicate = (
                    f"WHERE gp.datasource_game_id IN ({', '.join(str(value) for value in chunk)})"
                )
            rows = connection.execute(
                text(
                    f"""
                    SELECT gp.datasource_game_id, o.do_eco, o.do_name, MAX(gp.dgp_ply)
                    FROM derived_game_position AS gp
                    JOIN derived_opening_route AS r
                      ON r.derived_position_id = gp.derived_position_id
                    JOIN datasource_opening AS o
                      ON o.do_opening_id = r.datasource_opening_id
                    {predicate}
                    GROUP BY gp.datasource_game_id, o.do_eco, o.do_name
                    """
                )
            ).all()
            for row in rows:
                game_id = _required_int(row[0], "opening game id")
                if game_id not in games:
                    raise ValueError("opening occurrence references an unknown game")
                ply = _required_int(row[3], "opening ply")
                eco = _required_text(row[1], "opening ECO")
                name = _required_text(row[2], "opening name")
                key = _opening_api_key(eco, name)
                per_game = opening_matches.setdefault(game_id, {})
                prior = per_game.get(key)
                if prior is None or ply > prior[2]:
                    per_game[key] = (eco, name, ply)
    except GameSearchError:
        raise
    except (IndexError, TypeError, ValueError) as error:
        raise GameSearchStorageError("opening row is malformed") from error
    return opening_matches


def _select_deepest(
    opening_matches: dict[str, tuple[str, str, int]],
) -> DeepestOpening:
    key, (eco, name, ply) = min(opening_matches.items(), key=lambda item: (-item[1][2], item[0]))
    return DeepestOpening(key=key, eco=eco, name=name, ply=ply)


def _matches_aggregates(
    game: _GameData,
    aggregates: _GameAggregates,
    query: GameSearchQuery,
) -> bool:
    if not _in_datetime_bounds(game.started_at_utc, query.started_at_from, query.started_at_to):
        return False
    if not _in_datetime_bounds(game.ended_at_utc, query.ended_at_from, query.ended_at_to):
        return False
    if query.termination_reason is not None and (
        game.termination_reason is None
        or game.termination_reason.strip().casefold() != query.termination_reason
    ):
        return False
    if query.min_length_plies is not None and aggregates.length_plies < query.min_length_plies:
        return False
    if query.max_length_plies is not None and aggregates.length_plies > query.max_length_plies:
        return False
    if query.analysis_coverage is not None and (
        _coverage_state(aggregates.distinct_position_count, aggregates.analyzed_position_count)
        != query.analysis_coverage
    ):
        return False
    if query.preferred_coverage is not None and (
        _coverage_state(aggregates.distinct_position_count, aggregates.preferred_position_count)
        != query.preferred_coverage
    ):
        return False
    return True


def _summarize_aggregates(
    game: _GameData,
    aggregates: _GameAggregates,
    deepest: DeepestOpening | None,
) -> GameSummary:
    return GameSummary(
        game_uuid=game.game_uuid,
        source_url=game.source_url,
        trainer_color=game.trainer_color,
        trainer_chesscom_uuid=game.trainer_chesscom_uuid,
        opponent_chesscom_uuid=game.opponent_chesscom_uuid,
        trainer_rating=game.trainer_rating,
        opponent_rating=game.opponent_rating,
        started_at_utc=game.started_at_utc,
        ended_at_utc=game.ended_at_utc,
        trainer_outcome=game.trainer_outcome,
        termination_reason=game.termination_reason,
        time_control=game.time_control,
        time_class=game.time_class,
        occurrence_count=aggregates.occurrence_count,
        length_plies=aggregates.length_plies,
        deepest_opening=deepest,
        coverage=GameCoverage(
            distinct_position_count=aggregates.distinct_position_count,
            analyzed_position_count=aggregates.analyzed_position_count,
            preferred_position_count=aggregates.preferred_position_count,
            analysis_coverage=_coverage_state(
                aggregates.distinct_position_count, aggregates.analyzed_position_count
            ),
            preferred_coverage=_coverage_state(
                aggregates.distinct_position_count, aggregates.preferred_position_count
            ),
        ),
    )
