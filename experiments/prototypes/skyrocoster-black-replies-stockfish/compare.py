"""Compare Skyrocoster's exact-line Black replies with a fresh Stockfish search."""

from __future__ import annotations

import argparse
import io
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import chess
import chess.engine
import chess.pgn


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATABASE = ROOT / "data" / "database" / "chess_games.db"
DEFAULT_ENGINE = ROOT / "data" / "stockfish" / "stockfish-windows-x86-64-avx2.exe"
TARGET_PREFIX = ("e4", "c6", "Nc3", "d5", "exd5", "cxd5", "d4", "Nc6", "Nf3")
ENGINE_NODES = 200_000
ENGINE_MULTIPV = 5
ENGINE_OPTIONS = {"Threads": 1, "Hash": 128, "UCI_ShowWDL": True}
TINY_SAMPLE_MAX = 2
TARGET_PLY = len(TARGET_PREFIX)


@dataclass(frozen=True)
class PlayerIdentity:
    uuid: str
    username: str
    corpus_id: int


@dataclass(frozen=True)
class GameRecord:
    game_uuid: str
    pgn: str
    white_result: str | None
    black_result: str | None


@dataclass(frozen=True)
class MatchedGame:
    record: GameRecord
    reply: str | None


@dataclass(frozen=True)
class PersonalReply:
    move: str
    games: int
    wins: int
    draws: int
    losses: int


@dataclass(frozen=True)
class EngineReply:
    rank: int
    move: str
    score: str
    wdl: tuple[int, int, int]


def target_board() -> chess.Board:
    board = chess.Board()
    for san in TARGET_PREFIX:
        board.push_san(san)
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
        raise SystemExit(f"No tracked-corpus player matches username {username!r}.")
    if len(rows) > 1:
        matches = ", ".join(f"{row[1]} ({row[0]})" for row in rows)
        raise SystemExit(f"Ambiguous tracked-corpus username {username!r}: {matches}")
    uuid, selected_username, corpus_id = rows[0]
    return PlayerIdentity(str(uuid), str(selected_username), int(corpus_id))


def qualifying_games(connection: sqlite3.Connection, identity: PlayerIdentity) -> list[GameRecord]:
    rows = connection.execute(
        """
        SELECT g.uuid, g.pgn, g.white_result, g.black_result
        FROM corpus_game AS cg
        JOIN games AS g ON g.uuid = cg.game_uuid
        WHERE cg.corpus_id = ?
          AND cg.rules = 'chess'
          AND g.black_player_uuid = ?
        ORDER BY g.uuid
        """,
        (identity.corpus_id, identity.uuid),
    ).fetchall()
    return [
        GameRecord(
            game_uuid=str(game_uuid),
            pgn=str(pgn),
            white_result=None if white_result is None else str(white_result),
            black_result=None if black_result is None else str(black_result),
        )
        for game_uuid, pgn, white_result, black_result in rows
    ]


def validate_prefix(record: GameRecord, expected_fen: str) -> tuple[bool, str | None, str]:
    """Replay only the needed adjacent mainline plies and validate them legally."""
    try:
        game = chess.pgn.read_game(io.StringIO(record.pgn))
        if game is None:
            return False, None, "PGN produced no game"
        board = game.board()
        standard_fen = chess.Board().fen(en_passant="fen")
        if board.fen(en_passant="fen") != standard_fen:
            return False, None, "non-standard initial position"
        moves = iter(game.mainline_moves())
        for expected_san in TARGET_PREFIX:
            move = next(moves, None)
            if move is None:
                return False, None, "game ended before complete prefix"
            if not board.is_legal(move):
                return False, None, "illegal move in prefix"
            if board.san(move) != expected_san:
                return False, None, "SAN prefix mismatch"
            board.push(move)
        if board.fen(en_passant="fen") != expected_fen:
            return False, None, "rule-aware target state mismatch"

        reply_move = next(moves, None)
        if reply_move is None:
            return True, None, "matched without an immediate reply"
        if not board.is_legal(reply_move):
            return False, None, "illegal immediate reply"
        return True, board.san(reply_move), "matched with an immediate reply"
    except (IndexError, ValueError, chess.IllegalMoveError) as error:
        return False, None, f"PGN replay error: {error}"


def match_corpus(
    records: list[GameRecord], expected_fen: str
) -> tuple[list[MatchedGame], dict[str, int]]:
    matches: list[MatchedGame] = []
    seen_occurrences: set[tuple[str, int]] = set()
    rejected: defaultdict[str, int] = defaultdict(int)
    for record in records:
        matched, reply, reason = validate_prefix(record, expected_fen)
        if not matched:
            rejected[reason] += 1
            continue
        occurrence = (record.game_uuid, TARGET_PLY)
        if occurrence in seen_occurrences:
            rejected["duplicate same-game occurrence"] += 1
            continue
        seen_occurrences.add(occurrence)
        matches.append(MatchedGame(record, reply))
    return matches, dict(rejected)


def black_outcome(record: GameRecord) -> str:
    if record.black_result == "win" and record.white_result != "win":
        return "win"
    if record.white_result == "win" and record.black_result != "win":
        return "loss"
    if record.white_result != "win" and record.black_result != "win":
        return "draw"
    raise SystemExit(
        f"Cannot normalize whole-game result for matched game {record.game_uuid}: "
        f"white_result={record.white_result!r}, black_result={record.black_result!r}"
    )


def personal_report(matches: list[MatchedGame]) -> list[PersonalReply]:
    buckets: defaultdict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for match in matches:
        if match.reply is None:
            continue
        bucket = buckets[match.reply]
        bucket[0] += 1
        outcome = black_outcome(match.record)
        bucket[{"win": 1, "draw": 2, "loss": 3}[outcome]] += 1
    replies = [
        PersonalReply(move, values[0], values[1], values[2], values[3])
        for move, values in buckets.items()
    ]
    replies.sort(key=lambda reply: (-reply.games, reply.move))
    return replies


def score_label(score: chess.engine.PovScore) -> str:
    black_score = score.pov(chess.BLACK)
    mate = black_score.mate()
    if mate is not None:
        return f"mate {mate:+d} (Black perspective)"
    return f"cp {black_score.score():+d} (Black perspective)"


def black_wdl(info: chess.engine.InfoDict) -> tuple[int, int, int]:
    raw_wdl = info.get("wdl")
    if raw_wdl is None:
        raise RuntimeError("Stockfish returned no WDL; UCI_ShowWDL was not available")
    relative_wdl = raw_wdl.pov(chess.BLACK) if hasattr(raw_wdl, "pov") else raw_wdl
    try:
        wins, draws, losses = relative_wdl
    except (TypeError, ValueError) as error:
        raise RuntimeError(f"Stockfish returned an unusable WDL value: {raw_wdl!r}") from error
    return int(wins), int(draws), int(losses)


def analyze_with_stockfish(
    board: chess.Board, engine_path: Path
) -> tuple[dict[str, str], list[EngineReply]]:
    if not engine_path.is_file():
        raise SystemExit(
            f"Stockfish binary not found: {engine_path}. "
            "Expected the installed Stockfish 18 binary at data/stockfish/."
        )

    engine: chess.engine.SimpleEngine | None = None
    shutdown_errors: list[str] = []
    try:
        try:
            engine = chess.engine.SimpleEngine.popen_uci(str(engine_path))
        except (OSError, chess.engine.EngineError) as error:
            raise SystemExit(
                f"Could not start Stockfish at {engine_path}: {error}. "
                "Check that the installed executable is runnable."
            ) from error
        missing = [name for name in ENGINE_OPTIONS if name not in engine.options]
        if missing:
            raise RuntimeError(f"Stockfish is missing required UCI options: {', '.join(missing)}")
        engine.configure(ENGINE_OPTIONS)
        infos = engine.analyse(
            board,
            chess.engine.Limit(nodes=ENGINE_NODES),
            multipv=ENGINE_MULTIPV,
            game=object(),
        )
        if isinstance(infos, dict):
            infos = [infos]
        ordered_infos = sorted(infos, key=lambda info: int(info.get("multipv", 999)))
        if len(ordered_infos) < ENGINE_MULTIPV:
            raise RuntimeError(
                f"Stockfish returned {len(ordered_infos)} lines; expected {ENGINE_MULTIPV}"
            )
        replies: list[EngineReply] = []
        for rank, info in enumerate(ordered_infos[:ENGINE_MULTIPV], start=1):
            principal_variation = info.get("pv", [])
            if not principal_variation:
                raise RuntimeError(f"Stockfish returned no principal variation for rank {rank}")
            move = principal_variation[0]
            if not board.is_legal(move):
                raise RuntimeError(f"Stockfish returned an illegal first move for rank {rank}")
            replies.append(
                EngineReply(
                    rank=rank,
                    move=board.san(move),
                    score=score_label(info["score"]),
                    wdl=black_wdl(info),
                )
            )
        return dict(engine.id), replies
    except (RuntimeError, chess.engine.EngineError, OSError) as error:
        raise SystemExit(f"Stockfish analysis failed: {error}") from error
    finally:
        if engine is not None:
            try:
                engine.quit()
            except Exception as error:  # noqa: BLE001 - shutdown must be attempted
                shutdown_errors.append(f"quit: {error}")
            try:
                engine.close()
            except Exception as error:  # noqa: BLE001 - shutdown must be attempted
                shutdown_errors.append(f"close: {error}")
            if shutdown_errors:
                raise SystemExit(
                    "Stockfish did not shut down cleanly: " + "; ".join(shutdown_errors)
                )


def format_line() -> str:
    numbered: list[str] = []
    for index, move in enumerate(TARGET_PREFIX):
        if index % 2 == 0:
            numbered.append(f"{index // 2 + 1}. {move}")
        else:
            numbered[-1] += f" {move}"
    return " ".join(numbered)


def print_personal_table(replies: list[PersonalReply]) -> None:
    print("PERSONAL_REPLY_TABLE:")
    if not replies:
        print("  (no immediate Black replies)")
        return
    for reply in replies:
        raw_win = 100 * reply.wins / reply.games
        chess_score = 100 * (reply.wins + 0.5 * reply.draws) / reply.games
        tiny = "TINY_SAMPLE" if reply.games <= TINY_SAMPLE_MAX else ""
        print(
            f"  {reply.move}: games={reply.games} W-D-L={reply.wins}-{reply.draws}-{reply.losses} "
            f"raw_win={raw_win:.2f}% chess_score={chess_score:.2f}% {tiny}".rstrip()
        )


def format_wdl(wdl: tuple[int, int, int]) -> str:
    return f"{wdl[0]}-{wdl[1]}-{wdl[2]}"


def print_engine_table(engine_id: dict[str, str], replies: list[EngineReply], path: Path) -> None:
    print(f"ENGINE_ID: {engine_id.get('name', 'unknown')} by {engine_id.get('author', 'unknown')}")
    print(f"ENGINE_BINARY: {path}")
    print("ENGINE_SETTINGS: nodes=200000 MultiPV=5 Threads=1 Hash=128 MiB UCI_ShowWDL=true")
    print("ENGINE_ANALYSIS: fresh process; exact target FEN; no result persistence")
    print("ENGINE_TOP_5_BLACK_PERSPECTIVE:")
    for reply in replies:
        print(f"  #{reply.rank} {reply.move}: score={reply.score} WDL={format_wdl(reply.wdl)}")


def print_overlap(engine_replies: list[EngineReply], personal: list[PersonalReply]) -> None:
    engine_by_move = {reply.move: reply for reply in engine_replies}
    personal_by_move = {reply.move: reply for reply in personal}
    ordered_moves = [reply.move for reply in engine_replies]
    ordered_moves.extend(sorted(set(personal_by_move) - set(engine_by_move)))
    print("PERSONAL_ENGINE_OVERLAP:")
    for move in ordered_moves:
        engine_reply = engine_by_move.get(move)
        personal_reply = personal_by_move.get(move)
        if engine_reply is None:
            engine_text = "PERSONAL_OUTSIDE_TOP_5"
        else:
            engine_text = (
                f"engine_rank=#{engine_reply.rank} engine_score={engine_reply.score} "
                f"engine_WDL={format_wdl(engine_reply.wdl)}"
            )
        personal_text = (
            f"personal_games={personal_reply.games}"
            if personal_reply is not None
            else "ENGINE_ONLY"
        )
        print(f"  {move}: {engine_text} {personal_text}")


def print_interpretation(personal: list[PersonalReply], engine: list[EngineReply]) -> None:
    print("INTERPRETATION:")
    if not personal:
        print("  No personal immediate reply was available for the matched games.")
        return
    most_frequent = personal[0]
    first_engine = engine[0].move
    chess_score = (most_frequent.wins + 0.5 * most_frequent.draws) / most_frequent.games
    if chess_score > 0.5:
        direction = "positive"
    elif chess_score < 0.5:
        direction = "negative"
    else:
        direction = "neutral"
    print(
        f"  Most frequent personal reply: {most_frequent.move} "
        f"({most_frequent.games} games; W-D-L={most_frequent.wins}-{most_frequent.draws}-"
        f"{most_frequent.losses})."
    )
    print(
        f"  Aligns with Stockfish first choice ({first_engine}): {'yes' if most_frequent.move == first_engine else 'no'}."
    )
    print(f"  Its historical whole-game outcome is {direction} by chess score ({chess_score:.2%}).")
    print(
        "  This describes frequency and outcomes separately from engine strength; it is not causal move-quality evidence."
    )
    print("  Small replies are flagged above and should not be called wrong from results alone.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    parser.add_argument("--username", default="Skyrocoster")
    args = parser.parse_args()
    if not args.database.is_file():
        raise SystemExit(f"Database not found: {args.database}")
    if not args.engine.is_file():
        raise SystemExit(
            f"Stockfish binary not found: {args.engine}. "
            "Expected the installed Stockfish 18 binary at data/stockfish/."
        )

    target = target_board()
    target_fen = target.fen(en_passant="fen")
    uri = f"{args.database.resolve().as_uri()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        connection.execute("PRAGMA query_only = ON")
        identity = resolve_identity(connection, args.username)
        records = qualifying_games(connection, identity)
        if not records:
            raise SystemExit(
                f"No qualifying chess games found with {identity.username!r} as Black."
            )
        matches, rejected = match_corpus(records, target_fen)

    personal = personal_report(matches)
    engine_id, engine_replies = analyze_with_stockfish(target, args.engine)

    print("EXPERIMENT: Skyrocoster historical Black replies versus Stockfish")
    print(f"PLAYER_USERNAME: {identity.username}")
    print(f"PLAYER_UUID: {identity.uuid}")
    print(f"CORPUS_ID: {identity.corpus_id}")
    print(f"TARGET_LINE: {format_line()}")
    print(f"TARGET_FEN: {target_fen}")
    print(f"QUALIFYING_BLACK_GAMES: {len(records)}")
    print(f"MATCHED_EXACT_PREFIX_GAMES: {len(matches)}")
    print(f"MATCHED_EXACT_PREFIX_OCCURRENCES: {len(matches)}")
    print(
        f"MATCHED_GAMES_WITH_IMMEDIATE_REPLY: {sum(match.reply is not None for match in matches)}"
    )
    print(f"MATCHED_GAMES_WITHOUT_IMMEDIATE_REPLY: {sum(match.reply is None for match in matches)}")
    print(
        "MATCH_RULE: complete SAN prefix from standard initial position; adjacent same-game mainline plies"
    )
    print("TRANSPOSITIONS: excluded by exact-prefix matching; no position-only search")
    print(f"DUPLICATE_OCCURRENCES_EXCLUDED: {rejected.get('duplicate same-game occurrence', 0)}")
    print("REPLAY_REJECTIONS:")
    for reason, count in sorted(rejected.items()):
        if reason != "duplicate same-game occurrence":
            print(f"  {count}: {reason}")
    print_personal_table(personal)
    print_engine_table(engine_id, engine_replies, args.engine)
    print_overlap(engine_replies, personal)
    print_interpretation(personal, engine_replies)
    print(
        "LIMITATIONS: one user-specified line; whole-game outcomes are descriptive, not causal; tiny samples are unstable; node-limited engine analysis is not a personal playing-strength estimate."
    )
    print(
        "ENGINE_SHUTDOWN: clean quit/close attempted in finally; no database/cache/output-file writes"
    )


if __name__ == "__main__":
    main()
