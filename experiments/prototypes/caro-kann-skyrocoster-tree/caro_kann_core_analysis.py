"""Build a deterministic, core-only coverage analysis from the existing tree JSON.

This is noncanonical exploratory work.  It reads ``caro_kann_tree.json`` as an
authoritative source and writes a structured analysis plus a readable report.
It does not read the database, import the tree builder, or run a chess engine.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_SOURCE = EXPERIMENT_DIR / "caro_kann_tree.json"
DEFAULT_JSON_OUTPUT = EXPERIMENT_DIR / "caro_kann_core_analysis.json"
DEFAULT_MARKDOWN_OUTPUT = EXPERIMENT_DIR / "caro_kann_core_analysis.md"

ROOT_TOTAL = 3358
MIN_SUPPORT_GAMES = 20
STRICT_LOCAL_THRESHOLD = 10.0
EXPECTED_NODE_COUNT = 229
EXPECTED_EXPANDED_COUNT = 106
EXPECTED_STOPPED_COUNT = 123
EXPECTED_MAX_DEPTH = 16
PERCENT_DECIMALS = 2
ROOT_PREFIX_SAN = ["e4", "c6"]

STOP_BELOW_SUPPORT = "below_min_support_20_games"
STOP_NO_QUALIFYING = "no_individual_move_above_10pct_local"
STOP_NO_NEXT = "no_recorded_next_move"

BASE_BUCKETS = (
    ("less_common_moves", "less-common moves"),
    ("ended_or_no_next", "ended/no-next"),
    (STOP_BELOW_SUPPORT, "below-20 stop"),
)


def fail(message: str) -> None:
    raise SystemExit(f"Source validation failed: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def pct(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(100.0 * numerator / denominator, PERCENT_DECIMALS)


def format_line(sans: list[str]) -> str:
    parts: list[str] = []
    for index, san in enumerate(sans):
        if index % 2 == 0:
            parts.append(f"{index // 2 + 1}.")
        parts.append(san)
    return " ".join(parts)


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, ensure_ascii=True) + "\n"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered)


def copy_edge(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "san": edge["san"],
        "uci": edge["uci"],
        "count": edge["count"],
        "local_pct": edge["local_pct"],
        "cumulative_pct": edge["cumulative_pct"],
    }


def validate_edge(edge: dict[str, Any], games_with_next: int, root_total: int) -> None:
    require(
        set(edge) == {"san", "uci", "count", "local_pct", "cumulative_pct"}, "edge schema changed"
    )
    require(isinstance(edge["san"], str) and edge["san"], "edge SAN is empty")
    require(isinstance(edge["uci"], str) and edge["uci"], "edge UCI is empty")
    require(isinstance(edge["count"], int) and edge["count"] > 0, "edge count is invalid")
    require(
        edge["local_pct"] == pct(edge["count"], games_with_next),
        f"local percentage mismatch for {edge['san']}",
    )
    require(
        edge["cumulative_pct"] == pct(edge["count"], root_total),
        f"cumulative percentage mismatch for {edge['san']}",
    )


def validate_node(
    node: dict[str, Any],
    parent: dict[str, Any] | None,
    all_nodes: list[tuple[dict[str, Any], dict[str, Any] | None]],
    seen_ids: set[str],
    root_total: int,
) -> None:
    node_id = node.get("node_id")
    require(isinstance(node_id, str) and node_id not in seen_ids, "node IDs are not unique")
    seen_ids.add(node_id)
    all_nodes.append((node, parent))

    sans = node["moves_san"]
    ucis = node["moves_uci"]
    require(isinstance(sans, list) and isinstance(ucis, list), f"{node_id} prefixes are not lists")
    require(len(sans) == len(ucis) == node["ply"], f"{node_id} prefix length disagrees with ply")
    require(node["line"] == format_line(sans), f"{node_id} complete line is not canonical")
    require(
        node_id == "n" + hashlib.sha256("\x1f".join(sans).encode("utf-8")).hexdigest()[:16],
        f"{node_id} ID disagrees with prefix",
    )
    require(node["side_to_move"] in {"white", "black"}, f"{node_id} side to move is invalid")
    require(len(node["fen"].split()) == 6, f"{node_id} does not contain a six-field FEN")
    require(node["games"] > 0 and node["games"] <= root_total, f"{node_id} game count is invalid")

    outcomes = node["outcomes"]
    require(
        set(outcomes) == {"win", "draw", "loss", "unknown"}, f"{node_id} outcome schema changed"
    )
    require(sum(outcomes.values()) == node["games"], f"{node_id} outcomes do not reconcile")
    classifiable = outcomes["win"] + outcomes["draw"] + outcomes["loss"]
    require(node["classifiable_games"] == classifiable, f"{node_id} classifiable count is invalid")
    require(
        node["raw_win_pct"] == pct(outcomes["win"], classifiable),
        f"{node_id} raw win percentage is invalid",
    )
    require(
        node["chess_score_pct"] == pct(2 * outcomes["win"] + outcomes["draw"], 2 * classifiable),
        f"{node_id} chess score percentage is invalid",
    )

    observed = node["observed_next_moves"]
    require(isinstance(observed, list), f"{node_id} observed moves are not a list")
    for edge in observed:
        validate_edge(edge, node["games_with_next"], root_total)
    require(
        sum(edge["count"] for edge in observed) == node["games_with_next"],
        f"{node_id} next-move counts do not reconcile",
    )
    require(
        node["games_with_next"] + node["games_without_next"] == node["games"],
        f"{node_id} ended/no-next count does not reconcile",
    )
    require(
        [(-edge["count"], edge["san"]) for edge in observed]
        == sorted((-edge["count"], edge["san"]) for edge in observed),
        f"{node_id} observed moves are not deterministically ordered",
    )

    children = node["children"]
    require(isinstance(children, list), f"{node_id} children are not a list")
    child_by_san: dict[str, dict[str, Any]] = {}
    for child in children:
        arrival = child["arrived_via"]
        require(isinstance(arrival, dict), f"{child['node_id']} has no arrival edge")
        validate_edge(arrival, node["games_with_next"], root_total)
        require(arrival["san"] not in child_by_san, f"{node_id} has duplicate child SAN")
        child_by_san[arrival["san"]] = child
        require(
            child["games"] == arrival["count"], f"{child['node_id']} count disagrees with arrival"
        )
        require(child["ply"] == node["ply"] + 1, f"{child['node_id']} is not the next ply")
        require(
            child["moves_san"] == [*sans, arrival["san"]], f"{child['node_id']} SAN prefix changed"
        )
        require(
            child["moves_uci"] == [*ucis, arrival["uci"]], f"{child['node_id']} UCI prefix changed"
        )
        require(
            child["arrived_via"]
            == next(edge for edge in observed if edge["san"] == arrival["san"]),
            f"{child['node_id']} arrival is not the source edge",
        )

    require(
        [(-child["arrived_via"]["count"], child["arrived_via"]["san"]) for child in children]
        == sorted(
            (-child["arrived_via"]["count"], child["arrived_via"]["san"]) for child in children
        ),
        f"{node_id} children are not deterministically ordered",
    )

    other = node["other_moves"]
    other_by_san: dict[str, dict[str, Any]] = {}
    if other is not None:
        moves = other["moves"]
        require(moves, f"{node_id} has an empty other-moves group")
        require(other["move_count"] == len(moves), f"{node_id} other-moves count is invalid")
        require(
            other["games"] == sum(edge["count"] for edge in moves),
            f"{node_id} other-moves games are invalid",
        )
        require(
            other["games"] <= node["games_with_next"], f"{node_id} other-moves exceed next games"
        )
        require(
            other["local_pct"] == pct(other["games"], node["games_with_next"]),
            f"{node_id} other-moves local percentage is invalid",
        )
        require(
            other["cumulative_pct"] == pct(other["games"], root_total),
            f"{node_id} other-moves cumulative percentage is invalid",
        )
        for edge in moves:
            validate_edge(edge, node["games_with_next"], root_total)
            require(edge["san"] not in other_by_san, f"{node_id} has duplicate other SAN")
            other_by_san[edge["san"]] = edge
        require(
            [(-edge["count"], edge["san"]) for edge in moves]
            == sorted((-edge["count"], edge["san"]) for edge in moves),
            f"{node_id} other moves are not deterministically ordered",
        )

    observed_by_san = {edge["san"]: edge for edge in observed}
    require(len(observed_by_san) == len(observed), f"{node_id} observed SAN is not unique")
    require(
        set(child_by_san) | set(other_by_san) == set(observed_by_san),
        f"{node_id} branches do not cover observed moves",
    )
    require(not set(child_by_san) & set(other_by_san), f"{node_id} child and other moves overlap")
    require(
        sum(child["games"] for child in children) + (other["games"] if other else 0)
        == node["games_with_next"],
        f"{node_id} child and other games do not reconcile",
    )

    qualifying = {edge["san"] for edge in observed if 10 * edge["count"] > node["games_with_next"]}
    eligible = node["games"] >= MIN_SUPPORT_GAMES and node["games_with_next"] > 0 and qualifying
    if node["expansion"] == "expanded":
        require(
            node["stop_reason"] is None and eligible and set(child_by_san) == qualifying,
            f"{node_id} expansion state is invalid",
        )
    elif node["expansion"] == "stopped":
        expected_reason = (
            STOP_BELOW_SUPPORT
            if node["games"] < MIN_SUPPORT_GAMES
            else STOP_NO_NEXT
            if not node["games_with_next"]
            else STOP_NO_QUALIFYING
        )
        require(
            not children and not eligible and node["stop_reason"] == expected_reason,
            f"{node_id} stop state is invalid",
        )
    else:
        fail(f"{node_id} has an unknown expansion marker")

    if parent is None:
        require(node["arrived_via"] is None, "root has an arrival edge")
    else:
        arrival = node["arrived_via"]
        require(arrival is not None, f"{node_id} is missing its arrival context")
        require(node["ply"] == parent["ply"] + 1, f"{node_id} arrival ply is not adjacent")

    for child in children:
        validate_node(child, node, all_nodes, seen_ids, root_total)


def validate_source(
    source: dict[str, Any],
) -> tuple[list[tuple[dict[str, Any], dict[str, Any] | None]], dict[str, Any]]:
    require(
        source.get("schema") == "caro-kann-history-tree/v1",
        "source schema/version is not caro-kann-history-tree/v1",
    )
    thresholds = source.get("thresholds", {})
    require(
        thresholds.get("min_games_to_expand_node") == MIN_SUPPORT_GAMES,
        "minimum support metadata changed",
    )
    require(
        thresholds.get("expand_single_move_when_local_pct_strictly_above")
        == STRICT_LOCAL_THRESHOLD,
        "strict >10% metadata changed",
    )
    require(
        thresholds.get("percent_precision_decimals") == PERCENT_DECIMALS,
        "percentage precision metadata changed",
    )

    generated_from = source.get("generated_from", {})
    require(generated_from.get("player_color") == "black", "source player color metadata changed")
    require(generated_from.get("rules_filter") == "chess", "source rules metadata changed")
    require(
        generated_from.get("username_resolved_case_insensitively") == "Skyrocoster",
        "source player metadata changed",
    )
    root_cohort = source.get("root_cohort", {})
    root = source.get("tree")
    require(isinstance(root, dict), "source tree is missing")
    require(root_cohort.get("total_games") == ROOT_TOTAL, "root denominator is not 3,358")
    require(root["games"] == ROOT_TOTAL, "tree root games are not 3,358")
    require(
        root["moves_san"] == ROOT_PREFIX_SAN and root["ply"] == 2,
        "source root prefix is not exactly 1. e4 c6",
    )

    all_nodes: list[tuple[dict[str, Any], dict[str, Any] | None]] = []
    validate_node(root, None, all_nodes, set(), ROOT_TOTAL)
    stats = source.get("stats", {})
    expanded_count = sum(node["expansion"] == "expanded" for node, _parent in all_nodes)
    stopped_count = sum(node["expansion"] == "stopped" for node, _parent in all_nodes)
    stop_counts: dict[str, int] = defaultdict(int)
    for node, _parent in all_nodes:
        if node["stop_reason"] is not None:
            stop_counts[node["stop_reason"]] += 1
    require(len(all_nodes) == EXPECTED_NODE_COUNT, "source node count is not 229")
    require(expanded_count == EXPECTED_EXPANDED_COUNT, "source expanded-node count is not 106")
    require(stopped_count == EXPECTED_STOPPED_COUNT, "source stopped-node count is not 123")
    require(
        max(node["ply"] for node, _parent in all_nodes) == EXPECTED_MAX_DEPTH,
        "source maximum depth is not 16",
    )
    require(
        stats.get("real_position_nodes") == EXPECTED_NODE_COUNT, "source stats node count changed"
    )
    require(
        stats.get("expanded_nodes") == EXPECTED_EXPANDED_COUNT,
        "source stats expanded count changed",
    )
    require(
        stats.get("stopped_nodes") == EXPECTED_STOPPED_COUNT, "source stats stopped count changed"
    )
    require(
        stats.get("max_depth_plies") == EXPECTED_MAX_DEPTH, "source stats maximum depth changed"
    )
    source_stop_counts = stats.get("stop_reason_counts", {})
    require(
        {
            reason: source_stop_counts.get(reason, 0)
            for reason in set(source_stop_counts) | set(stop_counts)
        }
        == {
            reason: stop_counts.get(reason, 0)
            for reason in set(source_stop_counts) | set(stop_counts)
        },
        "source stop-reason stats do not match nodes",
    )
    require(root_cohort.get("total_games") == root["games"], "root metadata and tree disagree")
    require(
        root_cohort.get("games_with_immediate_next") == root["games_with_next"],
        "root next-move metadata changed",
    )
    require(
        root_cohort.get("games_ended_or_no_next") == root["games_without_next"],
        "root ended metadata changed",
    )
    return all_nodes, root


def bucket_name_for_stop(reason: str) -> tuple[str, str]:
    if reason == STOP_BELOW_SUPPORT:
        return STOP_BELOW_SUPPORT, "below-20 stop"
    if reason == STOP_NO_NEXT:
        return "ended_or_no_next", "ended/no-next"
    if reason == STOP_NO_QUALIFYING:
        return (
            "stop_no_individual_move_above_10pct_local",
            "stopped: no individual move above 10% locally",
        )
    return f"stop_reason_{reason}", f"source stop reason: {reason}"


def make_bucket_order(
    all_nodes: list[tuple[dict[str, Any], dict[str, Any] | None]],
) -> list[tuple[str, str]]:
    buckets = list(BASE_BUCKETS)
    extra_reasons = sorted(
        {
            node["stop_reason"]
            for node, _parent in all_nodes
            if node["stop_reason"] not in {None, STOP_BELOW_SUPPORT, STOP_NO_NEXT}
        }
    )
    buckets.extend(bucket_name_for_stop(reason) for reason in extra_reasons)
    return buckets


def build_funnel(
    all_nodes: list[tuple[dict[str, Any], dict[str, Any] | None]],
    root_total: int,
    bucket_order: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    by_depth: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for node, _parent in all_nodes:
        by_depth[node["ply"]].append(node)
    depths = sorted(by_depth)
    require(
        depths == list(range(2, EXPECTED_MAX_DEPTH + 1)), "source has a gap in represented plies"
    )

    rows: list[dict[str, Any]] = []
    for depth in depths:
        nodes = by_depth[depth]
        represented = sum(node["games"] for node in nodes)
        continuing = 0
        bucket_games = {key: 0 for key, _label in bucket_order}
        ended_expanded = 0
        stopped_no_next = 0
        for node in nodes:
            if node["expansion"] == "expanded":
                child_games = sum(child["games"] for child in node["children"])
                continuing += child_games
                if node["other_moves"] is not None:
                    bucket_games["less_common_moves"] += node["other_moves"]["games"]
                bucket_games["ended_or_no_next"] += node["games_without_next"]
                ended_expanded += node["games_without_next"]
            else:
                key, _label = bucket_name_for_stop(node["stop_reason"])
                bucket_games[key] += node["games"]
                if node["stop_reason"] == STOP_NO_NEXT:
                    stopped_no_next += node["games"]
        attrition = sum(bucket_games.values())
        require(
            represented == continuing + attrition, f"funnel row at ply {depth} does not reconcile"
        )
        buckets: list[dict[str, Any]] = []
        for key, label in bucket_order:
            bucket: dict[str, Any] = {
                "bucket": key,
                "label": label,
                "games": bucket_games[key],
                "root_coverage_percent": pct(bucket_games[key], root_total),
            }
            if key == "ended_or_no_next":
                bucket["source_breakdown"] = {
                    "expanded_node_games_without_next": ended_expanded,
                    "stopped_no_recorded_next_move": stopped_no_next,
                }
            buckets.append(bucket)
        rows.append(
            {
                "ply": depth,
                "represented_node_count": len(nodes),
                "expanded_node_count": sum(node["expansion"] == "expanded" for node in nodes),
                "stopped_node_count": sum(node["expansion"] == "stopped" for node in nodes),
                "represented_games": represented,
                "root_coverage_percent": pct(represented, root_total),
                "continuing_games": continuing,
                "continuing_root_coverage_percent": pct(continuing, root_total),
                "attrition_buckets": buckets,
                "reconciliation": {
                    "continuing_plus_attrition_games": continuing + attrition,
                    "matches_represented_games": True,
                },
            }
        )
    return rows


def build_branch_context(
    all_nodes: list[tuple[dict[str, Any], dict[str, Any] | None]],
) -> list[dict[str, Any]]:
    branches: list[dict[str, Any]] = []
    for child, parent in all_nodes:
        if parent is None:
            continue
        arrival = child["arrived_via"]
        branches.append(
            {
                "parent_node_id": parent["node_id"],
                "parent_line": parent["line"],
                "parent_prefix_san": list(parent["moves_san"]),
                "parent_prefix_uci": list(parent["moves_uci"]),
                "child_node_id": child["node_id"],
                "child_line": child["line"],
                "child_prefix_san": list(child["moves_san"]),
                "child_prefix_uci": list(child["moves_uci"]),
                "move_san": arrival["san"],
                "move_uci": arrival["uci"],
                "games": arrival["count"],
                "local_pct": arrival["local_pct"],
                "cumulative_pct": arrival["cumulative_pct"],
                "child_fen": child["fen"],
                "child_side_to_move": child["side_to_move"],
            }
        )
    branches.sort(
        key=lambda branch: (
            len(branch["child_prefix_san"]),
            branch["child_line"],
            branch["child_node_id"],
        )
    )
    return branches


def build_stopped_line(
    node: dict[str, Any], parent: dict[str, Any] | None, rank: int, root_total: int
) -> dict[str, Any]:
    arrival = node["arrived_via"]
    require(
        parent is not None and arrival is not None,
        f"stopped node {node['node_id']} has no arrival context",
    )
    return {
        "rank": rank,
        "rank_basis": {
            "games": node["games"],
            "complete_line": node["line"],
            "ordering": "games descending, then complete line ascending",
        },
        "node_id": node["node_id"],
        "complete_line": node["line"],
        "fen": node["fen"],
        "side_to_move": node["side_to_move"],
        "moves_san": list(node["moves_san"]),
        "moves_uci": list(node["moves_uci"]),
        "games": node["games"],
        "root_coverage_percent": pct(node["games"], root_total),
        "w_d_l_unknown": {
            "win": node["outcomes"]["win"],
            "draw": node["outcomes"]["draw"],
            "loss": node["outcomes"]["loss"],
            "unknown": node["outcomes"]["unknown"],
        },
        "raw_win_pct": node["raw_win_pct"],
        "chess_score_pct": node["chess_score_pct"],
        "stop_reason": node["stop_reason"],
        "arrival_context": {
            "parent_node_id": parent["node_id"],
            "parent_line": parent["line"],
            "parent_prefix_san": list(parent["moves_san"]),
            "parent_prefix_uci": list(parent["moves_uci"]),
            "move_san": arrival["san"],
            "move_uci": arrival["uci"],
            "games": arrival["count"],
            "local_pct": arrival["local_pct"],
            "cumulative_pct": arrival["cumulative_pct"],
        },
    }


def build_analysis(source_path: Path, source: dict[str, Any]) -> dict[str, Any]:
    all_nodes, root = validate_source(source)
    root_total = root["games"]
    bucket_order = make_bucket_order(all_nodes)
    funnel = build_funnel(all_nodes, root_total, bucket_order)
    branches = build_branch_context(all_nodes)

    stopped_nodes = [(node, parent) for node, parent in all_nodes if node["expansion"] == "stopped"]
    stopped_nodes.sort(key=lambda item: (-item[0]["games"], item[0]["line"], item[0]["node_id"]))
    stopped_lines = [
        build_stopped_line(node, parent, rank, root_total)
        for rank, (node, parent) in enumerate(stopped_nodes, start=1)
    ]
    require(
        len(stopped_lines) == EXPECTED_STOPPED_COUNT, "analysis did not retain all stopped lines"
    )

    top_ten = stopped_lines[:10]
    top_references = [
        {
            "rank": line["rank"],
            "node_id": line["node_id"],
            "complete_line": line["complete_line"],
            "games": line["games"],
            "root_coverage_percent": line["root_coverage_percent"],
        }
        for line in top_ten
    ]
    first_split_children = [child for child in root["children"]]
    first_split_games = sum(child["games"] for child in first_split_children)
    source_bytes = source_path.read_bytes()
    source_hash = hashlib.sha256(source_bytes).hexdigest()

    return {
        "schema": "caro-kann-core-analysis/v1",
        "source": {
            "filename": source_path.name,
            "schema": source["schema"],
            "sha256": source_hash,
            "root_total_games": root_total,
            "thresholds": {
                "minimum_games": MIN_SUPPORT_GAMES,
                "local_move_threshold_percent": STRICT_LOCAL_THRESHOLD,
                "threshold_rule": "strictly above 10%",
            },
            "stats": {
                "real_position_nodes": EXPECTED_NODE_COUNT,
                "expanded_nodes": EXPECTED_EXPANDED_COUNT,
                "stopped_nodes": EXPECTED_STOPPED_COUNT,
                "maximum_depth_plies": EXPECTED_MAX_DEPTH,
            },
        },
        "tier": "core",
        "metadata": {
            "implemented_tiers": ["core"],
            "future_tier_intent": {
                "core": "current high-support, currently implemented coverage",
                "secondary": "future lower-priority but still useful coverage",
                "long-tail": "future descriptive coverage of rare lines",
            },
            "coverage_note": "Core is the current analysis tier, not total repertoire coverage.",
        },
        "definitions": {
            "root_coverage_percent": "games divided by the 3,358-game root cohort",
            "branch_local_pct": "edge games divided by the parent node's games_with_next",
            "branch_cumulative_pct": "edge games divided by the 3,358-game root cohort",
            "funnel_rule": "A row represents disjoint source nodes at one ply; it has no aggregate local percentage.",
            "attrition_rule": "Expanded other_moves are less-common moves; expanded games_without_next and stopped no-next nodes are ended/no-next; other stopped nodes use their full games under the named stop bucket.",
            "outcome_rule": "W-D-L and historical percentages are context only and do not rank or explain a line.",
        },
        "root_context": {
            "node_id": root["node_id"],
            "complete_line": root["line"],
            "moves_san": list(root["moves_san"]),
            "moves_uci": list(root["moves_uci"]),
            "fen": root["fen"],
            "side_to_move": root["side_to_move"],
            "games": root["games"],
        },
        "coverage_funnel": funnel,
        "branch_context": branches,
        "stopped_lines": stopped_lines,
        "top_10": {
            "ranking_rule": "games descending, then deterministic complete-line ascending tie-break; outcomes never affect rank",
            "references": top_references,
            "records": top_ten,
        },
        "summary": {
            "first_post_root_split": {
                "description": "Qualifying child lines immediately after 1. e4 c6",
                "core_games": first_split_games,
                "root_coverage_percent": pct(first_split_games, root_total),
                "child_node_ids": [child["node_id"] for child in first_split_children],
            },
            "all_stopped_line_count": len(stopped_lines),
            "no_engine_run": True,
            "future_tiers_implemented": False,
        },
    }


def md_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}%"


def md_count(value: int) -> str:
    return f"{value:,}"


def bucket_values(row: dict[str, Any]) -> dict[str, int]:
    return {bucket["bucket"]: bucket["games"] for bucket in row["attrition_buckets"]}


def build_markdown(payload: dict[str, Any]) -> str:
    source = payload["source"]
    summary = payload["summary"]
    first_split = summary["first_post_root_split"]
    lines: list[str] = [
        "# Caro-Kann core coverage analysis",
        "",
        "This is deterministic, noncanonical exploratory analysis of the authoritative `caro_kann_tree.json`.",
        "It summarizes the current **core** tier only; it does not claim to cover the whole repertoire.",
        "",
        "## Scope and interpretation",
        "",
        f"The first post-root split keeps {md_count(first_split['core_games'])} games, "
        f"or {md_pct(first_split['root_coverage_percent'])} of all {md_count(source['root_total_games'])} root games. "
        "That is the roughly 70% current core at the first post-root split, not total repertoire coverage.",
        "",
        "`% at this position` is a local percentage on one exact branch edge: edge games divided by "
        "the parent position's games with a recorded next move. `% of all root games` divides by the "
        f"full {md_count(source['root_total_games'])}-game root cohort. Funnel rows intentionally do not "
        "invent an aggregate local percentage for a whole ply.",
        "",
        "The funnel counts disjoint real source nodes at each represented ply. Continuing games are "
        "qualifying expanded child nodes. The remainder is assigned once: expanded grouped `other_moves` "
        "are less-common moves; expanded games without a next move and stopped no-next nodes are ended/no-next; "
        "a stopped node's full games go into its named stop bucket.",
        "",
        "## Coverage funnel",
        "",
    ]
    bucket_order = [
        bucket["bucket"] for bucket in payload["coverage_funnel"][0]["attrition_buckets"]
    ]
    bucket_labels = {
        bucket["bucket"]: bucket["label"]
        for bucket in payload["coverage_funnel"][0]["attrition_buckets"]
    }
    headers = [
        "Ply",
        "Represented",
        "Root coverage",
        "Continuing",
        *[bucket_labels[key] for key in bucket_order],
        "Reconciles",
    ]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _header in headers) + " |")
    for row in payload["coverage_funnel"]:
        values = bucket_values(row)
        cells = [
            str(row["ply"]),
            md_count(row["represented_games"]),
            md_pct(row["root_coverage_percent"]),
            md_count(row["continuing_games"]),
            *[md_count(values[key]) for key in bucket_order],
            "yes" if row["reconciliation"]["matches_represented_games"] else "no",
        ]
        lines.append("| " + " | ".join(cells) + " |")
    lines.extend(
        [
            "",
            "The below-20 rule is applied when a qualifying child is reached: that child appears in the "
            "next ply's represented coverage, then its full games are counted as below-20 stop attrition. "
            "All 123 stopped exact lines remain in the JSON output.",
            "",
            "## Top 10 stopped exact lines",
            "",
            "These lines are ranked only by games descending, then complete-line order. W-D-L, raw win, and "
            "chess score are historical context only; they do not imply causation or affect rank.",
            "",
            "| Rank | Games | Root coverage | W-D-L / unknown | Raw win | Chess score | Stop reason | Complete line |",
            "| ---: | ---: | ---: | :--- | ---: | ---: | :--- | :--- |",
        ]
    )
    for line in payload["top_10"]["records"]:
        outcomes = line["w_d_l_unknown"]
        wdl = f"{outcomes['win']}-{outcomes['draw']}-{outcomes['loss']} / {outcomes['unknown']}"
        lines.append(
            f"| {line['rank']} | {md_count(line['games'])} | {md_pct(line['root_coverage_percent'])} | "
            f"{wdl} | {md_pct(line['raw_win_pct'])} | {md_pct(line['chess_score_pct'])} | "
            f"`{line['stop_reason']}` | {line['complete_line']} |"
        )
    lines.extend(
        [
            "",
            f"The JSON contains all {payload['summary']['all_stopped_line_count']} stopped exact lines, with "
            "complete SAN/UCI prefixes, node IDs, six-field FENs, side to move, arrival context, counts, "
            "root percentages, outcomes, and stop reasons.",
            "",
            "## Output and limits",
            "",
            f"- Source: `{source['filename']}` (`{source['schema']}`); root denominator: {md_count(source['root_total_games'])} games.",
            f"- Tier marker: `{payload['tier']}`. Future core/secondary/long-tail tier intent is recorded, but only core is implemented here.",
            "- No database was read and no engine was run. Positions are references for possible later engine work only.",
            "- The structured output contains branch-local percentages only on exact branch/edge records; funnel percentages are root-cohort coverage.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8"))
    payload = build_analysis(args.source, source)
    dump_json(args.output, payload)
    markdown = build_markdown(payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    with args.markdown_output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(markdown)
    print(
        f"Core analysis: {payload['summary']['first_post_root_split']['core_games']} games "
        f"({md_pct(payload['summary']['first_post_root_split']['root_coverage_percent'])}) at the first post-root split"
    )
    print(f"Funnel rows: {len(payload['coverage_funnel'])} (plies 2-{EXPECTED_MAX_DEPTH})")
    print(f"Stopped exact lines: {payload['summary']['all_stopped_line_count']}")
    print(f"Wrote JSON: {args.output}")
    print(f"Wrote Markdown: {args.markdown_output}")


if __name__ == "__main__":
    main()
