"""Deterministic Caro-Kann history tree for Skyrocoster as Black.

Noncanonical exploration: reads the tracked-corpus SQLite database read-only, keeps
tracked games where the case-insensitively resolved player was Black and play began
exactly 1. e4 c6, and grows an exact-move-prefix tree branching on both colors. Every
real position node reports counts, whole-game outcomes, a six-field FEN, and a machine
readable stop reason. The JSON is engine-ready for later Stockfish use; this script
never launches an engine.
"""

import argparse
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from itertools import groupby
from pathlib import Path

import chess

MIN_SUPPORT_GAMES = 20
PCT_DECIMALS = 2
ROOT_PREFIX = ("e4", "c6")
KNOWN_DRAW_CODES = frozenset(
    {"agreed", "repetition", "insufficient", "stalemate", "50move", "timevsinsufficient"}
)
STOP_MIN_SUPPORT = "below_min_support_20_games"
STOP_NO_QUALIFYING_MOVE = "no_individual_move_above_10pct_local"
STOP_NO_NEXT_MOVE = "no_recorded_next_move"
STOP_TEXT = {
    STOP_MIN_SUPPORT: "stopped: reached by fewer than 20 games (minimum support)",
    STOP_NO_QUALIFYING_MOVE: "stopped: no single immediate move exceeds 10% locally",
    STOP_NO_NEXT_MOVE: "stopped: no game at this position has a recorded next move",
}
EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[2]
DEFAULT_DATABASE = REPO_ROOT / "data" / "database" / "chess_games.db"
DEFAULT_OUTPUT = EXPERIMENT_DIR / "caro_kann_tree.json"
INITIAL_STATE_FIELDS = tuple(chess.Board().fen(en_passant="fen").split()[:4])
OCCURRENCE_QUERY = """
SELECT cg.game_uuid, g.black_result, g.white_result, po.ply, po.san, po.uci,
       po.halfmove_clock, po.fullmove_number,
       ps.placement, ps.side_to_move, ps.castling, ps.en_passant
FROM corpus_game AS cg JOIN games AS g ON g.uuid = cg.game_uuid
JOIN position_occurrence AS po ON po.game_uuid = cg.game_uuid
JOIN position_state AS ps ON ps.state_id = po.state_id
WHERE cg.corpus_id = ? AND cg.rules = 'chess'
  AND g.black_player_uuid = ? AND g.white_player_uuid <> ?
ORDER BY cg.game_uuid, po.ply
"""


def pct(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(100.0 * numerator / denominator, PCT_DECIMALS)


def node_id_for(sans: list[str] | tuple[str, ...]) -> str:
    joined = "\x1f".join(sans)
    return "n" + hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def format_line(sans: list[str] | tuple[str, ...]) -> str:
    parts: list[str] = []
    for index, san in enumerate(sans):
        if index % 2 == 0:
            parts.append(f"{index // 2 + 1}.")
        parts.append(san)
    return " ".join(parts)


def classify_outcome(black_result: str, white_result: str) -> str:
    """Whole-game result from Black's view; unclassifiable pairs stay 'unknown'."""
    black_won, white_won = black_result == "win", white_result == "win"
    if black_won != white_won:
        return "win" if black_won else "loss"
    if black_result in KNOWN_DRAW_CODES and white_result in KNOWN_DRAW_CODES:
        return "draw"
    return "unknown"


def display_database_path(database: Path) -> str:
    resolved = database.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


@dataclass(frozen=True)
class GameRecord:
    sans: tuple[str, ...]
    ucis: tuple[str, ...]
    outcome: str


@dataclass
class TreeContext:
    games: list[GameRecord]
    root_total: int
    node_count: int = 0
    expanded_count: int = 0
    max_depth: int = 0

    def __post_init__(self) -> None:
        self.stop_reasons: dict[str, int] = dict.fromkeys(
            (STOP_MIN_SUPPORT, STOP_NO_QUALIFYING_MOVE, STOP_NO_NEXT_MOVE), 0
        )


def resolve_corpus_player(connection: sqlite3.Connection, username: str) -> tuple[str, str, int]:
    """Case-insensitive metadata lookup returning (player_uuid, exact name, corpus_id)."""
    rows = connection.execute(
        """
        SELECT p.uuid, p.username, c.corpus_id
        FROM players AS p JOIN corpus AS c ON c.subject_player_uuid = p.uuid
        WHERE p.username COLLATE NOCASE = ?
        ORDER BY p.uuid
        """,
        (username,),
    ).fetchall()
    if not rows:
        raise SystemExit(f"No tracked corpus backs a player named {username!r}.")
    if len(rows) > 1:
        listed = ", ".join(sorted(f"{row[1]} ({row[0]})" for row in rows))
        raise SystemExit(f"Ambiguous corpus-backed username {username!r}: {listed}")
    player_uuid, resolved_username, corpus_id = rows[0]
    return str(player_uuid), str(resolved_username), int(corpus_id)


def validate_game(rows: list[tuple]) -> GameRecord | None:
    def corrupted(detail: str) -> SystemExit:
        return SystemExit(f"Corpus data rejected for game {rows[0][0]}: {detail}")

    plies = [row[3] for row in rows]
    if plies != list(range(len(rows))):
        raise corrupted("occurrence plies are missing or not adjacent from ply 0")
    head = rows[0]
    if head[4:8] != (None, None, 0, 1):
        raise corrupted("ply 0 must store no move and start both clocks")
    if tuple(head[8:12]) != INITIAL_STATE_FIELDS:
        raise corrupted("ply 0 state is not the standard initial position")
    board = chess.Board()
    sans: list[str] = []
    ucis: list[str] = []
    for _uuid, black_result, white_result, ply, san, uci, clock, number, *state in rows[1:]:
        try:
            move = board.parse_san(san)
        except ValueError as error:
            raise corrupted(f"ply {ply} SAN {san!r} does not parse: {error}") from error
        if board.san(move) != san or move.uci() != uci:
            raise corrupted(f"ply {ply} stored SAN/UCI {san!r}/{uci!r} is not canonical")
        board.push(move)
        if (
            tuple(board.fen(en_passant="fen").split()[:4]) != tuple(state)
            or board.halfmove_clock != clock
            or board.fullmove_number != number
        ):
            raise corrupted(f"ply {ply} stored rules state disagrees with replay")
        sans.append(san)
        ucis.append(uci)
    if tuple(sans[: len(ROOT_PREFIX)]) != ROOT_PREFIX:
        return None
    return GameRecord(tuple(sans), tuple(ucis), classify_outcome(rows[0][1], rows[0][2]))


def load_validated_games(
    connection: sqlite3.Connection, corpus_id: int, player_uuid: str
) -> tuple[int, list]:
    rows = connection.execute(OCCURRENCE_QUERY, (corpus_id, player_uuid, player_uuid)).fetchall()
    cohort: list[GameRecord] = []
    for _game_uuid, grouped in groupby(rows, key=lambda row: row[0]):
        record = validate_game(list(grouped))
        if record is not None:
            cohort.append(record)
    return len({row[0] for row in rows}), cohort


def build_node(
    path: list[tuple[str, str]],
    board: chess.Board,
    members: list[int],
    arrival: dict | None,
    ctx: TreeContext,
) -> dict:
    sans = [san for san, _uci in path]
    depth = len(sans)
    games_here = len(members)
    outcomes = {"win": 0, "draw": 0, "loss": 0, "unknown": 0}
    next_slots: dict[str, list] = {}
    members_by_next: dict[str, list[int]] = {}
    for index in members:
        record = ctx.games[index]
        outcomes[record.outcome] += 1
        if len(record.sans) > depth:
            san = record.sans[depth]
            slot = next_slots.get(san)
            if slot is None:
                next_slots[san] = [1, record.ucis[depth]]
                members_by_next[san] = [index]
            else:
                slot[0] += 1
                members_by_next[san].append(index)
    games_with_next = sum(slot[0] for slot in next_slots.values())
    classifiable = games_here - outcomes["unknown"]
    ordered = sorted(next_slots.items(), key=lambda item: (-item[1][0], item[0]))

    def edge_entry(san: str, slot: list) -> dict:
        return {
            "san": san,
            "uci": slot[1],
            "count": slot[0],
            "local_pct": pct(slot[0], games_with_next),
            "cumulative_pct": pct(slot[0], ctx.root_total),
        }

    # Strictly greater than 10%, expressed in exact integer math (no float rounding).
    def qualifies(count: int) -> bool:
        return 10 * count > games_with_next

    observed = [edge_entry(san, slot) for san, slot in ordered]
    expanding = (
        games_here >= MIN_SUPPORT_GAMES
        and games_with_next > 0
        and any(qualifies(slot[0]) for slot in next_slots.values())
    )
    children: list[dict] = []
    other_entries: list[dict] = []
    stop_reason = None
    for san, slot in ordered:
        entry = edge_entry(san, slot)
        if expanding and qualifies(slot[0]):
            board.push(board.parse_san(san))
            child = build_node([*path, (san, slot[1])], board, members_by_next[san], entry, ctx)
            board.pop()
            children.append(child)
        else:
            other_entries.append(entry)
    other_moves = None
    if other_entries:
        other_games = sum(entry["count"] for entry in other_entries)
        other_moves = {
            "move_count": len(other_entries),
            "games": other_games,
            "local_pct": pct(other_games, games_with_next),
            "cumulative_pct": pct(other_games, ctx.root_total),
            "moves": other_entries,
        }
    if expanding:
        ctx.expanded_count += 1
    elif games_here < MIN_SUPPORT_GAMES:
        stop_reason = STOP_MIN_SUPPORT
    elif games_with_next == 0:
        stop_reason = STOP_NO_NEXT_MOVE
    else:
        stop_reason = STOP_NO_QUALIFYING_MOVE
    if stop_reason is not None:
        ctx.stop_reasons[stop_reason] += 1
    ucis = [uci for _san, uci in path]
    node = {
        "node_id": node_id_for(sans),
        "line": format_line(sans),
        "moves_san": sans,
        "moves_uci": ucis,
        "ply": depth,
        "side_to_move": "white" if board.turn == chess.WHITE else "black",
        "fen": board.fen(en_passant="fen"),
        "games": games_here,
        "outcomes": outcomes,
        "classifiable_games": classifiable,
        "raw_win_pct": pct(outcomes["win"], classifiable),
        "chess_score_pct": pct(2 * outcomes["win"] + outcomes["draw"], 2 * classifiable),
        "games_with_next": games_with_next,
        "games_without_next": games_here - games_with_next,
        "arrived_via": arrival,
        "observed_next_moves": observed,
        "expansion": "expanded" if expanding else "stopped",
        "stop_reason": stop_reason,
        "children": children,
        "other_moves": other_moves,
    }
    ctx.node_count += 1
    ctx.max_depth = max(ctx.max_depth, depth)
    return node


def verify_node(node: dict, root_total: int) -> None:
    def bad(detail: str) -> None:
        raise SystemExit(f"node {node['node_id']} ({node['line']}): {detail}")

    outcomes = node["outcomes"]
    observed = node["observed_next_moves"]
    children = node["children"]
    games, with_next = node["games"], node["games_with_next"]
    classifiable = outcomes["win"] + outcomes["draw"] + outcomes["loss"]
    if sum(outcomes.values()) != games or classifiable != node["classifiable_games"]:
        bad("outcome totals do not reconcile")
    expected = (
        pct(outcomes["win"], classifiable),
        pct(2 * outcomes["win"] + outcomes["draw"], 2 * classifiable),
    )
    if (node["raw_win_pct"], node["chess_score_pct"]) != expected:
        bad("percentage fields disagree with raw counts")
    if (
        sum(e["count"] for e in observed) != with_next
        or with_next + node["games_without_next"] != games
    ):
        bad("next-move counts or ended/no-next split do not reconcile")
    for entry in observed:
        if entry["local_pct"] != pct(entry["count"], with_next) or entry["cumulative_pct"] != pct(
            entry["count"], root_total
        ):
            bad(f"percentage mismatch on edge {entry['san']}")
    edge_keys = [(-e["count"], e["san"]) for e in observed]
    child_keys = [(-c["arrived_via"]["count"], c["arrived_via"]["san"]) for c in children]
    if edge_keys != sorted(edge_keys) or child_keys != sorted(child_keys):
        bad("children or observed moves violate deterministic ordering")
    observed_by_san = {entry["san"]: entry for entry in observed}
    qualifying = {e["san"] for e in observed if 10 * e["count"] > with_next}
    child_by_san = {child["arrived_via"]["san"]: child for child in children}
    if len(observed_by_san) != len(observed) or len(child_by_san) != len(children):
        bad("duplicate SAN entries prevent exact branch reconciliation")
    for san, child in child_by_san.items():
        arrival = child["arrived_via"]
        if observed_by_san.get(san) != arrival or child["games"] != arrival["count"]:
            bad(f"child edge does not match observed move {san}")

    other = node["other_moves"]
    other_by_san: dict[str, dict] = {}
    if other is not None:
        moves = other["moves"]
        other_by_san = {entry["san"]: entry for entry in moves}
        if not moves or len(other_by_san) != len(moves):
            bad("other_moves is empty or contains duplicate SAN entries")
        if other["move_count"] != len(moves) or other["games"] != sum(
            entry["count"] for entry in moves
        ):
            bad("other_moves counts do not reconcile")
        if other["games"] > with_next:
            bad("other_moves exceeds games_with_next")
        if other["local_pct"] != pct(other["games"], with_next) or other["cumulative_pct"] != pct(
            other["games"], root_total
        ):
            bad("other_moves percentage fields disagree with their denominators")
        other_keys = [(-entry["count"], entry["san"]) for entry in moves]
        if other_keys != sorted(other_keys):
            bad("other_moves constituents violate deterministic ordering")
        for entry in moves:
            if (
                entry["san"] not in observed_by_san
                or entry["san"] in child_by_san
                or entry != observed_by_san[entry["san"]]
            ):
                bad(f"other_moves contains an unobserved or expanded move {entry['san']}")
            if entry["local_pct"] != pct(entry["count"], with_next) or entry[
                "cumulative_pct"
            ] != pct(entry["count"], root_total):
                bad(f"percentage mismatch on grouped edge {entry['san']}")

    represented = set(child_by_san) | set(other_by_san)
    if represented != set(observed_by_san):
        bad("expanded children and grouped moves do not cover observed moves exactly")
    if sum(child["games"] for child in children) + (other["games"] if other else 0) != with_next:
        bad("expanded children plus grouped moves do not reconcile to games_with_next")

    eligible = games >= MIN_SUPPORT_GAMES and with_next > 0 and bool(qualifying)
    if node["expansion"] == "expanded":
        if node["stop_reason"] is not None or not eligible or set(child_by_san) != qualifying:
            bad("expanded-node eligibility or qualifying-edge reconciliation failed")
    elif node["expansion"] == "stopped":
        reason = node["stop_reason"]
        expected_reason = (
            STOP_MIN_SUPPORT
            if games < MIN_SUPPORT_GAMES
            else STOP_NO_NEXT_MOVE
            if with_next == 0
            else STOP_NO_QUALIFYING_MOVE
        )
        if children or eligible or reason != expected_reason:
            bad(f"stopped-node state inconsistent (stop_reason={reason!r})")
    else:
        bad(f"unknown expansion marker {node['expansion']!r}")
    has_unexpanded = bool(set(observed_by_san) - set(child_by_san))
    if (other is not None) != has_unexpanded:
        bad("unexpanded move data has inconsistent other_moves presence")
    board = chess.Board()
    for san, uci in zip(node["moves_san"], node["moves_uci"]):
        move = board.parse_san(san)
        if move.uci() != uci:
            bad(f"move-list SAN/UCI disagreement at {san}")
        board.push(move)
    reparsed = chess.Board(node["fen"])
    side_ok = "white" if reparsed.turn == chess.WHITE else "black"
    if (
        board.fen(en_passant="fen") != node["fen"]
        or reparsed.fen(en_passant="fen") != node["fen"]
        or side_ok != node["side_to_move"]
        or node["node_id"] != node_id_for(node["moves_san"])
    ):
        bad("FEN round-trip, side to move, or stable node-id validation failed")
    for child in children:
        verify_node(child, root_total)


def build_payload(
    username: str,
    player_uuid: str,
    corpus_id: int,
    database_display: str,
    validated: int,
    root: dict,
    ctx: TreeContext,
) -> dict:
    return {
        "schema": "caro-kann-history-tree/v1",
        "description": (
            f"Exact-prefix history tree of tracked-corpus games in which {username} played "
            "Black and play began 1. e4 c6; descriptive whole-game outcomes, not move quality."
        ),
        "generated_from": {
            "database": database_display,
            "access_mode": "read-only sqlite URI (mode=ro)",
            "corpus_id": corpus_id,
            "username_resolved_case_insensitively": username,
            "player_uuid": player_uuid,
            "player_color": "black",
            "rules_filter": "chess",
            "candidate_black_games_fully_validated": validated,
            "root_cohort_rule": (
                "Tracked-corpus games with the resolved player as Black whose first two plies "
                "are exactly e4 then c6 from the standard initial position; exact prefixes "
                "preserved, transposing orders stay separate."
            ),
        },
        "thresholds": {
            "min_games_to_expand_node": MIN_SUPPORT_GAMES,
            "expand_single_move_when_local_pct_strictly_above": 10.0,
            "percent_precision_decimals": PCT_DECIMALS,
        },
        "definitions": {
            "node_id": "n + first 16 hex chars of sha256 over the U+001F-joined SAN prefix",
            "local_pct": "edge count / games_with_next at the parent node",
            "cumulative_pct": "edge count / root cohort total games",
            "raw_win_pct": "wins / classifiable_games (win+draw+loss)",
            "chess_score_pct": "(wins + 0.5*draws) / classifiable_games",
            "outcomes": f"whole-game results from {username}'s Black perspective",
            "denominator_note": (
                "games ending at a node stay in its outcomes and games_without_next and are "
                "excluded only from next-move (local_pct) denominators"
            ),
            "stop_reasons": STOP_TEXT,
        },
        "root_cohort": {
            "total_games": root["games"],
            "outcomes": root["outcomes"],
            "classifiable_games": root["classifiable_games"],
            "raw_win_pct": root["raw_win_pct"],
            "chess_score_pct": root["chess_score_pct"],
            "games_with_immediate_next": root["games_with_next"],
            "games_ended_or_no_next": root["games_without_next"],
        },
        "stats": {
            "real_position_nodes": ctx.node_count,
            "expanded_nodes": ctx.expanded_count,
            "stopped_nodes": ctx.node_count - ctx.expanded_count,
            "stop_reason_counts": dict(ctx.stop_reasons),
            "max_depth_plies": ctx.max_depth,
        },
        "tree": root,
    }


def fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.{PCT_DECIMALS}f}"


def print_tree(node: dict, indent: str = "") -> None:
    tag = "ROOT" if node["arrived_via"] is None else node["node_id"]
    outcomes = node["outcomes"]
    side = "White" if node["side_to_move"] == "white" else "Black"
    tail = (
        f"  {STOP_TEXT[node['stop_reason']]}"
        if node["stop_reason"]
        else "  expanded below: every single move strictly above 10% locally"
    )
    print(
        f"{indent}[{tag}] {node['line']}\n"
        f"{indent}  node_id={node['node_id']} | ply={node['ply']} | games={node['games']}\n"
        f"{indent}  FEN: {node['fen']} ({side} to move)\n"
        f"{indent}  Whole games here: W-D-L {outcomes['win']}-{outcomes['draw']}-"
        f"{outcomes['loss']} (unclassified {outcomes['unknown']}) | "
        f"raw win {fmt(node['raw_win_pct'])}% | score {fmt(node['chess_score_pct'])}%\n"
        f"{indent}  Have a recorded next move: {node['games_with_next']} | "
        f"ended or none recorded: {node['games_without_next']}\n"
        f"{indent}{tail}"
    )
    rows: list[tuple[dict, dict | None]] = [(c, c["arrived_via"]) for c in node["children"]]
    if node["other_moves"] is not None:
        rows.append((node["other_moves"], None))
    for index, (payload, via) in enumerate(rows):
        last = index == len(rows) - 1
        branch = "`-- " if last else "|-- "
        child_indent = f"{indent}{'   ' if last else '|  '}  "
        if via is not None:
            print(
                f"{indent}{branch}{via['san']} ({via['uci']}): {via['count']} games | "
                f"{fmt(via['local_pct'])}% at this position | "
                f"{fmt(via['cumulative_pct'])}% of all root games"
            )
            print_tree(payload, child_indent + "   ")
        else:
            print(
                f"{indent}{branch}other moves: {payload['move_count']} move kind(s), "
                f"{payload['games']} games | {fmt(payload['local_pct'])}% at this position | "
                f"{fmt(payload['cumulative_pct'])}% of all root games"
            )
            moves = payload["moves"]
            for start in range(0, len(moves), 4):
                listing = ", ".join(
                    f"{e['san']} ({e['uci']})={e['count']}" for e in moves[start : start + 4]
                )
                print(f"{child_indent}    {listing}")


def print_header(username: str, corpus_id: int, database_display: str, root_total: int) -> None:
    bar = "=" * 72
    print(bar)
    print("CARO-KANN HISTORY TREE - noncanonical exploration (read-only, no engine)")
    print("-" * 72)
    print(f"Player      : {username} (matched case-insensitively), playing Black")
    print(f"Corpus      : tracked corpus {corpus_id} in {database_display}")
    print(f"Root cohort : tracked games starting exactly 1. e4 c6 -> {root_total} games")
    print("Branching   : White and Black both branch; exact prefixes; transposing orders")
    print("              stay separate. Expansion: children require >= 20 games at the")
    print("              node AND some single immediate move strictly above 10% locally;")
    print("              no depth limit.")
    print("Outcomes    : whole-game results from Skyrocoster's side; descriptive, not")
    print("              move-quality claims.")
    print("% legend    : '% at this position' = share of games at one node that made that")
    print("              immediate move (games with no recorded next move are excluded")
    print("              from that base); '% of all root games' = share of the full cohort.")
    print(bar)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--username", default="Skyrocoster")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    connection = sqlite3.connect(f"{args.database.resolve().as_uri()}?mode=ro", uri=True)
    try:
        player_uuid, username, corpus_id = resolve_corpus_player(connection, args.username)
        validated, cohort = load_validated_games(connection, corpus_id, player_uuid)
    finally:
        connection.close()
    if not cohort:
        raise SystemExit("No tracked game with this player as Black began exactly 1. e4 c6.")
    root_ucis = cohort[0].ucis[: len(ROOT_PREFIX)]
    if any(r.ucis[: len(ROOT_PREFIX)] != root_ucis for r in cohort):
        raise SystemExit("Root UCI disagreement between cohort games.")
    board = chess.Board()
    for san in ROOT_PREFIX:
        board.push(board.parse_san(san))
    ctx = TreeContext(games=cohort, root_total=len(cohort))
    root_path = list(zip(ROOT_PREFIX, root_ucis))
    root = build_node(root_path, board, list(range(len(cohort))), None, ctx)
    if root["moves_san"] != list(ROOT_PREFIX) or root["games"] != len(cohort):
        raise SystemExit("Root cohort exactness check failed.")
    verify_node(root, ctx.root_total)
    database_display = display_database_path(args.database)
    payload = build_payload(
        username, player_uuid, corpus_id, database_display, validated, root, ctx
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n"
    )
    print_header(username, corpus_id, database_display, ctx.root_total)
    print_tree(root)
    reasons = ", ".join(f"{key}={value}" for key, value in ctx.stop_reasons.items())
    print(
        f"\nSummary: {ctx.node_count} real position nodes | {ctx.expanded_count} expanded | "
        f"{ctx.node_count - ctx.expanded_count} stopped\nStop reasons: {reasons}\n"
        f"Maximum tree depth: {ctx.max_depth} plies\nWrote JSON: {args.output}"
    )


if __name__ == "__main__":
    main()
