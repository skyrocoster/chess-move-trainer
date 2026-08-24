"""Follow a data-derived greedy continuation from a selected Caro-Kann branch."""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import chess
import chess.engine


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATABASE = ROOT / "data" / "database" / "chess_games.db"
DEFAULT_ENGINE = ROOT / "data" / "stockfish" / "stockfish-windows-x86-64-avx2.exe"
TARGET_PREFIX = ("e4", "c6", "d4", "d5", "e5", "c5", "c3", "Nc6", "Nf3")
ENGINE_NODES = 200_000
ENGINE_MULTIPV = 5
ENGINE_OPTIONS = {
    "Threads": 1,
    "Hash": 128,
    "UCI_ShowWDL": True,
}


@dataclass(frozen=True)
class PlayerIdentity:
    uuid: str
    username: str
    corpus_id: int
@dataclass(frozen=True)
class MoveReport:
    target_fen: str
    matched_games: int
    matched_occurrences: int
    games_with_next: int
    occurrences_with_next: int
    counts: list[tuple[str, int]]
@dataclass(frozen=True)
class PersonalReply:
    move: str
    games: int
    wins: int
    draws: int
    losses: int
@dataclass(frozen=True)
class PersonalReport:
    target_fen: str
    matched_games: int
    matched_occurrences: int
    games_with_immediate_reply: int
    replies: list[PersonalReply]
@dataclass(frozen=True)
class EngineReply:
    rank: int
    move: str
    score: str
    wdl: tuple[int, int, int] | None
State = tuple[str, str, str, str]
def line_state_ids(
    connection: sqlite3.Connection, moves: tuple[str, ...]
) -> tuple[list[int], str] | None:
    board = chess.Board()
    states: list[State] = []
    fields = board.fen(en_passant="fen").split()
    states.append(tuple(fields[:4]))
    for move in moves:
        board.push_san(move)
        fields = board.fen(en_passant="fen").split()
        states.append(tuple(fields[:4]))

    state_ids: list[int] = []
    for state in states:
        state_row = connection.execute(
            """
            SELECT state_id
            FROM position_state
            WHERE placement = ?
              AND side_to_move = ?
              AND castling = ?
              AND en_passant = ?
            """,
            state,
        ).fetchone()
        if state_row is None:
            return None
        state_ids.append(int(state_row[0]))
    return state_ids, board.fen(en_passant="fen")
def board_after(moves: tuple[str, ...]) -> chess.Board:
    board = chess.Board()
    for move in moves:
        board.push_san(move)
    return board
def resolve_identity(connection: sqlite3.Connection, username: str) -> PlayerIdentity:
    rows = connection.execute(
        """
        SELECT p.uuid, p.username, c.corpus_id
        FROM players AS p
        JOIN corpus AS c ON c.subject_player_uuid = p.uuid
        WHERE p.username COLLATE NOCASE = ?
        ORDER BY p.uuid
        """,
        (username,),
    ).fetchall()
    if not rows:
        raise SystemExit(f"No corpus-backed player matches username {username!r}.")
    if len(rows) > 1:
        matches = ", ".join(f"{row[1]} ({row[0]})" for row in rows)
        raise SystemExit(f"Ambiguous corpus-backed username {username!r}: {matches}")
    uuid, selected_username, corpus_id = rows[0]
    return PlayerIdentity(str(uuid), str(selected_username), int(corpus_id))
def qualifying_game_count(connection: sqlite3.Connection, identity: PlayerIdentity) -> int:
    return int(
        connection.execute(
            """
            SELECT COUNT(DISTINCT cg.game_uuid)
            FROM corpus_game AS cg
            JOIN games AS g ON g.uuid = cg.game_uuid
            WHERE cg.corpus_id = ?
              AND cg.rules = 'chess'
              AND g.black_player_uuid = ?
              AND g.white_player_uuid <> ?
            """,
            (identity.corpus_id, identity.uuid, identity.uuid),
        ).fetchone()[0]
    )
def prefix_match_sql(
    identity: PlayerIdentity, moves: tuple[str, ...], state_ids: list[int]
) -> tuple[str, list[object]]:
    joins = [
        """
        JOIN position_occurrence AS p0
          ON p0.game_uuid = game.game_uuid
         AND p0.ply = 0
         AND p0.state_id = ?
         AND p0.san IS NULL
         AND p0.halfmove_clock = 0
         AND p0.fullmove_number = 1
        """
    ]
    params: list[object] = [identity.corpus_id, identity.uuid, identity.uuid, state_ids[0]]
    for ply, (move, state_id) in enumerate(zip(moves, state_ids[1:]), start=1):
        joins.append(
            f"""
            JOIN position_occurrence AS p{ply}
              ON p{ply}.game_uuid = game.game_uuid
             AND p{ply}.ply = {ply}
             AND p{ply}.state_id = ?
             AND p{ply}.san = ?
            """
        )
        params.extend((state_id, move))
    query = f"""
        WITH qualifying_games AS (
            SELECT DISTINCT cg.game_uuid
            FROM corpus_game AS cg
            JOIN games AS g ON g.uuid = cg.game_uuid
            WHERE cg.corpus_id = ?
              AND cg.rules = 'chess'
              AND g.black_player_uuid = ?
              AND g.white_player_uuid <> ?
        ), matched AS (
            SELECT game.game_uuid
            FROM qualifying_games AS game
            {''.join(joins)}
        )
    """
    return query, params
def count_prefix_next_moves(
    connection: sqlite3.Connection,
    identity: PlayerIdentity,
    moves: tuple[str, ...],
) -> MoveReport:
    states = line_state_ids(connection, moves)
    if states is None:
        return MoveReport("unavailable", 0, 0, 0, 0, [])
    state_ids, target_fen = states
    match_query, match_params = prefix_match_sql(identity, moves, state_ids)
    next_ply = len(moves) + 1

    matched_games, matched_occurrences, games_with_next, occurrences_with_next = connection.execute(
        match_query
        + """
        SELECT COUNT(DISTINCT occurrence.game_uuid), COUNT(*),
               COUNT(DISTINCT CASE WHEN next_occurrence.san IS NOT NULL
                                   THEN occurrence.game_uuid END),
               COUNT(next_occurrence.san)
        FROM matched AS occurrence
        LEFT JOIN position_occurrence AS next_occurrence
          ON next_occurrence.game_uuid = occurrence.game_uuid
         AND next_occurrence.ply = ?
        """,
        [*match_params, next_ply],
    ).fetchone()
    counts = connection.execute(
        match_query
        + """
        SELECT next_occurrence.san, COUNT(*) AS move_count
        FROM matched AS occurrence
        JOIN position_occurrence AS next_occurrence
          ON next_occurrence.game_uuid = occurrence.game_uuid
         AND next_occurrence.ply = ?
        WHERE next_occurrence.san IS NOT NULL
        GROUP BY next_occurrence.san
        ORDER BY move_count DESC, next_occurrence.san ASC
        """,
        [*match_params, next_ply],
    ).fetchall()
    return MoveReport(
        target_fen=target_fen,
        matched_games=int(matched_games),
        matched_occurrences=int(matched_occurrences),
        games_with_next=int(games_with_next),
        occurrences_with_next=int(occurrences_with_next),
        counts=[(str(move), int(count)) for move, count in counts],
    )
def personal_reply_report(
    connection: sqlite3.Connection, identity: PlayerIdentity, moves: tuple[str, ...]
) -> PersonalReport:
    states = line_state_ids(connection, moves)
    if states is None:
        return PersonalReport("unavailable", 0, 0, 0, [])
    state_ids, target_fen = states
    match_query, match_params = prefix_match_sql(identity, moves, state_ids)
    rows = connection.execute(
        match_query
        + """
        SELECT matched.game_uuid, next_occurrence.san,
               games.black_result, games.white_result
        FROM matched
        JOIN games ON games.uuid = matched.game_uuid
        LEFT JOIN position_occurrence AS next_occurrence
          ON next_occurrence.game_uuid = matched.game_uuid
         AND next_occurrence.ply = ?
        """,
        [*match_params, len(moves) + 1],
    ).fetchall()

    grouped: dict[str, list[int]] = {}
    immediate_games = 0
    for _game_uuid, move, black_result, white_result in rows:
        if move is None:
            continue
        immediate_games += 1
        bucket = grouped.setdefault(str(move), [0, 0, 0, 0])
        bucket[0] += 1
        if black_result == "win":
            bucket[1] += 1
        elif white_result == "win":
            bucket[3] += 1
        else:
            bucket[2] += 1

    replies = [
        PersonalReply(move, games, wins, draws, losses)
        for move, (games, wins, draws, losses) in grouped.items()
    ]
    replies.sort(key=lambda reply: (-reply.games, reply.move))
    return PersonalReport(
        target_fen=target_fen,
        matched_games=len(rows),
        matched_occurrences=len(rows),
        games_with_immediate_reply=immediate_games,
        replies=replies,
    )
def black_score_label(score: chess.engine.PovScore) -> str:
    black_score = score.pov(chess.BLACK)
    mate = black_score.mate()
    if mate is not None:
        return f"mate {mate:+d} (Black perspective)"
    return f"cp {black_score.score():+d} (Black perspective)"
def black_wdl(info: chess.engine.InfoDict) -> tuple[int, int, int] | None:
    raw_wdl = info.get("wdl")
    if raw_wdl is None:
        return None
    relative_wdl = raw_wdl.pov(chess.BLACK) if hasattr(raw_wdl, "pov") else raw_wdl
    try:
        wins, draws, losses = relative_wdl
    except (TypeError, ValueError):
        return None
    return int(wins), int(draws), int(losses)
def analyze_with_stockfish(
    board: chess.Board, engine_path: Path
) -> tuple[dict[str, str], list[EngineReply]]:
    if not engine_path.is_file():
        raise SystemExit(
            f"Stockfish binary not found: {engine_path}. "
            "Restore the repository binary before running this experiment."
        )

    engine: chess.engine.SimpleEngine | None = None
    try:
        engine = chess.engine.SimpleEngine.popen_uci(str(engine_path))
        missing = [name for name in ENGINE_OPTIONS if name not in engine.options]
        if missing:
            raise RuntimeError(f"Stockfish is missing required UCI options: {', '.join(missing)}")
        engine.configure(ENGINE_OPTIONS)
        fresh_game = object()
        infos = engine.analyse(
            board,
            chess.engine.Limit(nodes=ENGINE_NODES),
            multipv=ENGINE_MULTIPV,
            game=fresh_game,
        )
        if isinstance(infos, dict):
            infos = [infos]
        infos = sorted(infos, key=lambda info: int(info.get("multipv", 999)))
        if len(infos) < ENGINE_MULTIPV:
            raise RuntimeError(f"Stockfish returned {len(infos)} lines; expected {ENGINE_MULTIPV}")

        replies: list[EngineReply] = []
        for rank, info in enumerate(infos[:ENGINE_MULTIPV], start=1):
            principal_variation = info.get("pv", [])
            if not principal_variation:
                raise RuntimeError(f"Stockfish returned no principal variation for rank {rank}")
            replies.append(
                EngineReply(
                    rank=rank,
                    move=board.san(principal_variation[0]),
                    score=black_score_label(info["score"]),
                    wdl=black_wdl(info),
                )
            )
        return dict(engine.id), replies
    except (OSError, RuntimeError, chess.engine.EngineError) as error:
        raise SystemExit(f"Stockfish analysis failed: {error}") from error
    finally:
        if engine is not None:
            try:
                engine.quit()
            except (OSError, chess.engine.EngineError):
                pass
def format_line(moves: list[str]) -> str:
    numbered: list[str] = []
    for index, move in enumerate(moves):
        if index % 2 == 0:
            numbered.append(f"{index // 2 + 1}. {move}")
        else:
            numbered[-1] += f" {move}"
    return " ".join(numbered)
def print_counts(label: str, report: MoveReport) -> None:
    print(f"{label}_TARGET_FEN: {report.target_fen}")
    print(f"{label}_MATCHED_GAMES: {report.matched_games}")
    print(f"{label}_MATCHED_OCCURRENCES: {report.matched_occurrences}")
    print(f"{label}_GAMES_WITH_IMMEDIATE_MOVE: {report.games_with_next}")
    print(f"{label}_OCCURRENCES_WITH_IMMEDIATE_MOVE: {report.occurrences_with_next}")
    print(f"{label}_MOVE_COUNTS:")
    for move, count in report.counts:
        print(f"  {move}: {count}")
def format_wdl(wdl: tuple[int, int, int] | None) -> str:
    return "unavailable" if wdl is None else f"{wdl[0]}-{wdl[1]}-{wdl[2]}"
def print_personal_report(report: PersonalReport) -> None:
    print(f"PERSONAL_TARGET_FEN: {report.target_fen}")
    print(f"PERSONAL_MATCHED_GAMES: {report.matched_games}")
    print(f"PERSONAL_MATCHED_OCCURRENCES: {report.matched_occurrences}")
    print(f"PERSONAL_GAMES_WITH_IMMEDIATE_REPLY: {report.games_with_immediate_reply}")
    print("PERSONAL_WHOLE_GAME_OUTCOMES_BLACK_PERSPECTIVE:")
    for reply in report.replies:
        raw_win = reply.wins / reply.games * 100
        chess_score = (reply.wins + 0.5 * reply.draws) / reply.games * 100
        tiny_sample = " [TINY SAMPLE]" if reply.games <= 2 else ""
        print(
            f"  {reply.move}: games={reply.games} W-D-L={reply.wins}-{reply.draws}-{reply.losses} "
            f"raw_win={raw_win:.2f}% chess_score={chess_score:.2f}%{tiny_sample}"
        )
def print_engine_report(
    engine_id: dict[str, str], replies: list[EngineReply], engine_path: Path
) -> None:
    print(f"ENGINE_ID: {engine_id.get('name', 'unknown')} by {engine_id.get('author', 'unknown')}")
    print(f"ENGINE_BINARY: {engine_path}")
    print(
        "ENGINE_SETTINGS: nodes=200000 MultiPV=5 Threads=1 Hash=128 MiB "
        "UCI_ShowWDL=true"
    )
    print("ENGINE_SCORE_PERSPECTIVE: Black; WDL is engine W-D-L on its configured scale")
    print("ENGINE_TOP_5:")
    for reply in replies:
        print(
            f"  #{reply.rank} {reply.move}: score={reply.score} "
            f"WDL={format_wdl(reply.wdl)}"
        )
def print_move_comparison(engine_replies: list[EngineReply], personal: PersonalReport) -> None:
    engine_moves = {reply.move: reply.rank for reply in engine_replies}
    personal_moves = {reply.move: reply.games for reply in personal.replies}
    moves = [reply.move for reply in engine_replies]
    moves.extend(sorted(set(personal_moves) - set(engine_moves)))
    print("MOVE_OVERLAP:")
    for move in moves:
        engine_label = f"engine_rank=#{engine_moves[move]}" if move in engine_moves else "engine_only=no"
        personal_label = (
            f"personal_games={personal_moves[move]}"
            if move in personal_moves
            else "personal_played=no"
        )
        print(f"  {move}: {engine_label} {personal_label}")
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    parser.add_argument("--username", default="Skyrocoster")
    args = parser.parse_args()

    uri = f"{args.database.resolve().as_uri()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        identity = resolve_identity(connection, args.username)
        qualifying_games = qualifying_game_count(connection, identity)
        if qualifying_games == 0:
            raise SystemExit(f"No qualifying Black games found for {identity.username!r}.")

        print("DATA_SOURCE: data/database/chess_games.db (corpus + games + position tables)")
        print(f"PLAYER_USERNAME: {identity.username}")
        print(f"PLAYER_UUID: {identity.uuid}")
        print(f"CORPUS_ID: {identity.corpus_id}")
        print(f"QUALIFYING_BLACK_GAMES: {qualifying_games}")
        prefix = ["e4", "c6", "d4", "d5"]
        print(f"SELECTED_START_LINE: {format_line(prefix)}")

        step = 1
        while True:
            print(f"STEP_{step}: White decision after exact prefix")
            print(f"WHITE_DECISION_PREFIX: {format_line(prefix)}")
            white_report = count_prefix_next_moves(connection, identity, tuple(prefix))
            print_counts("WHITE", white_report)
            if not white_report.counts:
                print("STOP_REASON: data exhaustion before an immediate White move was available")
                break

            white_move, white_count = white_report.counts[0]
            print(f"SELECTED_WHITE_MOVE: {white_move}")
            print(f"SELECTED_WHITE_MOVE_COUNT: {white_count}")
            prefix.append(white_move)

            print(f"BLACK_DECISION_PREFIX: {format_line(prefix)}")
            black_report = count_prefix_next_moves(connection, identity, tuple(prefix))
            print_counts("BLACK_SKYROCOASTER", black_report)
            if not black_report.counts or black_report.occurrences_with_next == 0:
                print("STOP_REASON: data exhaustion before an immediate Black reply was available")
                break

            black_move, black_count = black_report.counts[0]
            denominator = black_report.occurrences_with_next
            share = black_count / denominator
            game_denominator = black_report.games_with_next
            print(f"LEADING_BLACK_REPLY: {black_move}")
            print(f"LEADING_BLACK_REPLY_COUNT: {black_count}")
            print(
                "LEADING_BLACK_REPLY_SHARE: "
                f"{share:.2%} ({black_count}/{denominator} occurrences; "
                f"{black_count}/{game_denominator} games)"
            )
            if black_count * 100 >= denominator * 90:
                print("BLACK_DECISION: CONTINUE (leading reply is at least 90%)")
                prefix.append(black_move)
                step += 1
                continue

            print("BLACK_DECISION: DIVERGENCE (leading reply is below 90%)")
            print(f"DIVERGENCE_AFTER_WHITE_MOVE: {white_move}")
            print(f"OBSERVED_ONLY_BLACK_REPLY: {black_move}")
            print(f"ACCEPTED_LINE_AT_STOP: {format_line(prefix)}")
            print("STOP_REASON: first Black reply distribution below the 90% continuation threshold")
            break

        if tuple(prefix) != TARGET_PREFIX:
            raise SystemExit(
                "The greedy line did not reach the settled comparison position; "
                f"got {format_line(prefix)}"
            )
        target_board = board_after(TARGET_PREFIX)
        personal = personal_reply_report(connection, identity, TARGET_PREFIX)
        print("ENGINE_AND_PERSONAL_COMPARISON_AT_STOP:")
        print(f"TARGET_LINE: {format_line(list(TARGET_PREFIX))}")
        print(f"TARGET_FEN: {target_board.fen(en_passant='fen')}")
        print_personal_report(personal)
        engine_id, engine_replies = analyze_with_stockfish(target_board, args.engine)
        print_engine_report(engine_id, engine_replies, args.engine)
        print_move_comparison(engine_replies, personal)


if __name__ == "__main__":
    main()
