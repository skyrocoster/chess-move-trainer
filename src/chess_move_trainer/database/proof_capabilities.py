"""Real-reader capability proof while retaining only aggregate facts."""
from __future__ import annotations

from pathlib import Path

import chess
from sqlalchemy import text

from .connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from .games.reading import GameReadRepository
from .openings.recognition import lookup_fen, replay_pgn
from .openings.source import load_opening_sources
from .schema import _assert_compatible_schema
from .statistics import MoveResponseDistributionReader, PositionContextReader
from .proof_models import DirectCapabilities, DirectPreflightError
from .proof_opening_helpers import (
    _board_for_moves,
    _find_nested_routes,
    _find_transposition_pair,
    _opening_label,
    _pgn_for_moves,
    _positive_scalar,
)


def _collect_opening_capabilities(
    database_path: Path,
    opening_source_dir: Path,
) -> dict[str, object]:
    routes = load_opening_sources(opening_source_dir)
    transposition_route, transposed_moves = _find_transposition_pair(routes)
    exact = replay_pgn(database_path, _pgn_for_moves(transposition_route.moves_uci))
    transposed = replay_pgn(database_path, _pgn_for_moves(transposed_moves))
    route_match_proven = any(
        item.eco == transposition_route.eco
        and item.name == transposition_route.name
        and item.match == "route"
        for item in exact.recognized
    )
    transposition_match_proven = any(
        item.eco == transposition_route.eco
        and item.name == transposition_route.name
        and item.match == "transposition"
        for item in transposed.recognized
    )

    prefix, deep = _find_nested_routes(routes)
    partial = replay_pgn(database_path, _pgn_for_moves(prefix.moves_uci))
    deep_result = replay_pgn(database_path, _pgn_for_moves(deep.moves_uci))
    ordered_recognitions = tuple(item.ply for item in deep_result.recognized)
    if not ordered_recognitions or ordered_recognitions != tuple(sorted(ordered_recognitions)):
        raise DirectPreflightError("real opening recognitions are not ordered")
    future_variation_excluded = not any(
        item.eco == deep.eco and item.name == deep.name for item in partial.recognized
    )

    board = chess.Board()
    for move_uci in deep.moves_uci:
        board.push(chess.Move.from_uci(move_uci))
    departure = None
    for move in board.legal_moves:
        departed = replay_pgn(
            database_path,
            _pgn_for_moves((*deep.moves_uci, move.uci())),
        )
        if departed.current == deep_result.current:
            departure = departed
            break
    current_after_departure = (
        departure is not None
        and deep_result.current is not None
        and departure.current == deep_result.current
    )

    fields = deep.endpoint_fen.split()
    if len(fields) != 6:
        raise DirectPreflightError("pinned opening endpoint is not a complete FEN")
    clockless = lookup_fen(database_path, deep.endpoint_fen)
    clock_changed = lookup_fen(
        database_path,
        " ".join((*fields[:4], "99", "120")),
    )
    fen_clock_insensitive = tuple(
        (item.ply, item.eco, item.name, item.match)
        for item in clockless.recognized
    ) == tuple(
        (item.ply, item.eco, item.name, item.match)
        for item in clock_changed.recognized
    )

    if not route_match_proven or not transposition_match_proven:
        raise DirectPreflightError(
            "real opening recognition did not distinguish route and transposition"
        )
    if not current_after_departure or not fen_clock_insensitive or not future_variation_excluded:
        raise DirectPreflightError("real opening recognition meanings were not all proven")
    return {
        "opening_ordered_recognition_count": len(deep_result.recognized),
        "opening_current_after_departure": current_after_departure,
        "opening_route_match_proven": route_match_proven,
        "opening_transposition_match_proven": transposition_match_proven,
        "opening_fen_clock_insensitive": fen_clock_insensitive,
        "opening_future_variation_excluded": future_variation_excluded,
    }


def collect_direct_capabilities(
    database_path: str | Path,
    opening_source_dir: str | Path,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> DirectCapabilities:
    """Exercise real readers while retaining only bounded aggregate facts."""

    path = Path(database_path).expanduser().resolve(strict=False)
    source_dir = Path(opening_source_dir).expanduser().resolve(strict=False)
    try:
        with _open_connection(path, "read-only", lock_timeout) as connection:
            _assert_compatible_schema(connection, lock_timeout)
            game_id = _positive_scalar(
                connection.execute(
                    text(
                        """
                        SELECT g.dg_game_id
                        FROM datasource_game AS g
                        JOIN derived_game_position AS o
                          ON o.datasource_game_id = g.dg_game_id
                        GROUP BY g.dg_game_id
                        ORDER BY g.dg_game_id
                        LIMIT 1
                        """
                    )
                ).scalar_one_or_none()
            )
            context_position_id = _positive_scalar(
                connection.execute(
                    text(
                        """
                        SELECT o.derived_position_id
                        FROM derived_game_position AS o
                        JOIN datasource_game AS g
                          ON g.dg_game_id = o.datasource_game_id
                        GROUP BY o.derived_position_id
                        HAVING COUNT(DISTINCT CASE
                                   WHEN g.dg_trainer_color = 'white'
                                   THEN g.dg_game_id END) > 0
                           AND COUNT(DISTINCT CASE
                                   WHEN g.dg_trainer_color = 'black'
                                   THEN g.dg_game_id END) > 0
                        ORDER BY o.derived_position_id
                        LIMIT 1
                        """
                    )
                ).scalar_one_or_none()
            )
            actor_position_id = _positive_scalar(
                connection.execute(
                    text(
                        """
                        SELECT o.derived_position_id
                        FROM derived_game_position AS o
                        JOIN datasource_game AS g
                          ON g.dg_game_id = o.datasource_game_id
                        JOIN derived_position AS p
                          ON p.dp_position_id = o.derived_position_id
                        WHERE o.dgp_move_uci IS NOT NULL
                        GROUP BY o.derived_position_id
                        HAVING SUM(CASE
                                   WHEN (p.dp_side_to_move = 'w'
                                         AND g.dg_trainer_color = 'white')
                                     OR (p.dp_side_to_move = 'b'
                                         AND g.dg_trainer_color = 'black')
                                   THEN 1 ELSE 0 END) > 0
                           AND SUM(CASE
                                   WHEN (p.dp_side_to_move = 'w'
                                         AND g.dg_trainer_color = 'black')
                                     OR (p.dp_side_to_move = 'b'
                                         AND g.dg_trainer_color = 'white')
                                   THEN 1 ELSE 0 END) > 0
                        ORDER BY o.derived_position_id
                        LIMIT 1
                        """
                    )
                ).scalar_one_or_none()
            )
            final_position_id = _positive_scalar(
                connection.execute(
                    text(
                        """
                        SELECT o.derived_position_id
                        FROM derived_game_position AS o
                        WHERE o.dgp_move_uci IS NULL
                        GROUP BY o.derived_position_id
                        ORDER BY o.derived_position_id
                        LIMIT 1
                        """
                    )
                ).scalar_one_or_none()
            )
    except Exception as error:
        if isinstance(error, DirectPreflightError):
            raise
        raise DirectPreflightError(
            "real direct-capability inputs could not be selected"
        ) from error

    game = GameReadRepository(path, lock_timeout=lock_timeout).read(game_id)
    if game is None or not game.occurrences:
        raise DirectPreflightError("real direct game reconstruction returned no game")
    final_occurrence = game.occurrences[-1]
    if (
        tuple(item.ply for item in game.occurrences)
        != tuple(range(len(game.occurrences)))
        or final_occurrence.ply != len(game.occurrences) - 1
        or final_occurrence.move_uci is not None
        or any(item.move_uci is None for item in game.occurrences[:-1])
    ):
        raise DirectPreflightError(
            "real game occurrences are not ordered with one final occurrence"
        )
    metadata_complete = (
        game.game_id > 0
        and bool(game.source_url)
        and bool(game.original_pgn)
        and game.trainer_color in ("white", "black")
        and bool(game.trainer_chesscom_uuid)
    )

    context_reader = PositionContextReader(path, lock_timeout=lock_timeout)
    context_all = context_reader.read(context_position_id)
    context_white = context_reader.read(context_position_id, "white")
    context_black = context_reader.read(context_position_id, "black")

    distribution_reader = MoveResponseDistributionReader(path, lock_timeout=lock_timeout)
    actor_distribution = distribution_reader.read(actor_position_id)
    final_distribution = distribution_reader.read(final_position_id)
    actor_outgoing_count = sum(actor_distribution.outgoing_moves.values())
    actor_my_choice_count = sum(actor_distribution.my_choices.values())
    actor_opponent_count = sum(actor_distribution.opponent_responses.values())
    if (
        actor_distribution.occurrence_count <= 0
        or actor_distribution.final_occurrence_count < 0
        or actor_distribution.played_occurrence_count != actor_outgoing_count
        or actor_my_choice_count + actor_opponent_count != actor_outgoing_count
        or actor_my_choice_count <= 0
        or actor_opponent_count <= 0
        or final_distribution.final_occurrence_count <= 0
        or final_distribution.played_occurrence_count
        != sum(final_distribution.outgoing_moves.values())
    ):
        raise DirectPreflightError(
            "real direct statistics did not preserve actor and final-occurrence meanings"
        )

    opening_facts = _collect_opening_capabilities(path, source_dir)
    return DirectCapabilities(
        real_game_metadata_complete=metadata_complete,
        real_game_occurrence_count=len(game.occurrences),
        real_game_final_occurrence_present=final_occurrence.move_uci is None,
        context_all_game_count=context_all.distinct_game_count,
        context_white_game_count=context_white.distinct_game_count,
        context_black_game_count=context_black.distinct_game_count,
        actor_occurrence_count=actor_distribution.occurrence_count,
        actor_played_occurrence_count=actor_distribution.played_occurrence_count,
        actor_final_occurrence_count=actor_distribution.final_occurrence_count,
        actor_outgoing_move_kind_count=len(actor_distribution.outgoing_moves),
        actor_my_choice_count=actor_my_choice_count,
        actor_opponent_response_count=actor_opponent_count,
        final_position_final_occurrence_count=final_distribution.final_occurrence_count,
        **opening_facts,
    )

