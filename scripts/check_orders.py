#!/usr/bin/env python
"""Strict checker for canonical, lossless work-order artifacts.

The frontier coordinator supplies a structured compile packet. ``new_order.py`` renders
that packet without inference; this checker validates both the packet and the rendered
artifact. Ordinary agents invoke this script and read its output. They do not read it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
ORDERS_ROOT = REPO_ROOT / "docs" / "plans" / "active"
ORDER_PATH_RE = re.compile(
    r"^docs/plans/active/(?P<feature>[a-z0-9]+(?:-[a-z0-9]+)*)/orders/"
    r"(?P<number>\d{2})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)
PACKET_RE = re.compile(
    r"\n## Canonical compile packet\n\n```json\n(?P<packet>.*?)\n```\n",
    re.DOTALL,
)
STATUS_RE = re.compile(r"^STATUS:\s*(.+)$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"<[^>]+>|\b(?:TODO|TBD)\b", re.IGNORECASE)
VALID_STRENGTHS = {"Light", "Standard", "High"}
RESULT_KEYS = (
    "DEVIATIONS",
    "PROOF RESULTS",
    "DIRTY PATHS",
    "AUTHORIZATION AUDIT",
    "ATTEMPTS",
    "ESCALATION",
)


class OrderError:
    """One actionable checker finding, compatible with ``check_docs.py``."""

    def __init__(self, file: str, message: str, fix: str, severity: str = "error") -> None:
        self.file = file
        self.message = message
        self.fix = fix
        self.severity = severity

    def __str__(self) -> str:
        return f"{self.file}: {self.message}\n    fix: {self.fix}"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalise_path(raw: str) -> str:
    """Normalize separators and one leading ``./`` without eating root dots."""
    value = raw.strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value


def _canonical_order_path(value: str) -> re.Match[str] | None:
    return ORDER_PATH_RE.fullmatch(normalise_path(value))


def discover_orders(orders_root: Path | None = None) -> list[Path]:
    """Discover only canonical nested active work orders."""
    root = orders_root if orders_root is not None else ORDERS_ROOT
    if not root.exists():
        return []
    found: list[Path] = []
    for candidate in sorted(root.glob("*/orders/[0-9][0-9]-*.md")):
        if candidate.is_file() and _canonical_order_path(_rel(candidate)):
            found.append(candidate)
    return found


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _contains_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return bool(PLACEHOLDER_RE.search(value))
    if isinstance(value, list):
        return any(_contains_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_placeholder(item) for item in value.values())
    return False


def _valid_repo_path(value: Any) -> bool:
    if not _is_nonempty_string(value):
        return False
    path = normalise_path(value)
    if path.startswith(("/", "~")) or re.match(r"^[A-Za-z]:", path):
        return False
    parts = Path(path).parts
    return bool(parts) and ".." not in parts and path == Path(path).as_posix()


def _string_list(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(_is_nonempty_string(item) for item in value)
    )


def validate_packet(
    packet: Any,
    *,
    source: str = "<packet>",
    check_files: bool = True,
    status: str = "PENDING",
) -> list[OrderError]:
    """Validate the canonical compile packet without altering any supplied value."""
    findings: list[OrderError] = []

    def fail(message: str, fix: str) -> None:
        findings.append(OrderError(source, message, fix))

    if not isinstance(packet, dict):
        fail("Compile packet must be a JSON object", "Supply one object with the canonical fields")
        return findings

    required = {
        "output_path",
        "identity",
        "depends_on",
        "required_strength",
        "authorization",
        "context",
        "known_facts",
        "actions",
        "proof",
        "acceptance_handoff",
        "exclusions",
        "escalate_if",
    }
    missing = sorted(required - set(packet))
    extra = sorted(set(packet) - required)
    if missing:
        fail(f"Packet is missing fields: {', '.join(missing)}", "Add every canonical packet field")
    if extra:
        fail(f"Packet has unknown fields: {', '.join(extra)}", "Remove fields outside the canonical schema")
    if missing:
        return findings

    output = packet.get("output_path")
    output_match = _canonical_order_path(output) if isinstance(output, str) else None
    if not output_match:
        fail(
            "output_path must be docs/plans/active/<feature>/orders/<NN>-<slug>.md",
            "Supply the exact canonical nested output path",
        )

    identity = packet.get("identity")
    if not isinstance(identity, dict) or set(identity) != {"number", "slug", "title", "goal"}:
        fail("identity must contain exactly number, slug, title, and goal", "Use the canonical identity object")
    else:
        number, slug = identity.get("number"), identity.get("slug")
        if not isinstance(number, str) or not re.fullmatch(r"\d{2}", number):
            fail("identity.number must be two digits", "Use a value such as 01")
        if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            fail("identity.slug must be lowercase kebab-case", "Use a canonical filename slug")
        for field in ("title", "goal"):
            if not _is_nonempty_string(identity.get(field)):
                fail(f"identity.{field} must be non-empty", f"State the order {field}")
        if output_match and (number != output_match.group("number") or slug != output_match.group("slug")):
            fail("identity number/slug contradict output_path", "Make identity and the exact output filename agree")

    depends = packet.get("depends_on")
    if not _string_list(depends, allow_empty=True):
        fail("depends_on must be an array of canonical order paths", "Use [] or exact nested order paths")
        depends = []
    else:
        for dependency in depends:
            if not _canonical_order_path(dependency):
                fail(f"Dependency is not a canonical order path: {dependency}", "Use a nested active order path")
            elif normalise_path(dependency) == normalise_path(str(output)):
                fail("Order depends on itself", "Remove the self-dependency")
            elif check_files and not (REPO_ROOT / normalise_path(dependency)).is_file():
                fail(f"Dependency does not exist: {dependency}", "Compile the dependency first or remove it")

    strength = packet.get("required_strength")
    if not isinstance(strength, dict) or set(strength) != {"level", "reason"}:
        fail("required_strength must contain exactly level and reason", "Use the canonical strength object")
    else:
        level, reason = strength.get("level"), strength.get("reason")
        if level not in VALID_STRENGTHS:
            fail("required_strength.level must be Light, Standard, or High", "Choose one supported level")
        if level != "Light" and not _is_nonempty_string(reason):
            fail("Standard/High strength requires a reason", "Explain why Light is insufficient")
        if level == "Light" and reason is not None and not _is_nonempty_string(reason):
            fail("Light strength reason must be null or non-empty", "Use null when no reason is needed")

    authorization = packet.get("authorization")
    auth_sets: dict[str, set[str]] = {"creates": set(), "edits": set(), "removes": set()}
    if not isinstance(authorization, dict) or set(authorization) != set(auth_sets):
        fail("authorization must contain exactly creates, edits, and removes", "Use the canonical authorization object")
    else:
        for kind in auth_sets:
            values = authorization.get(kind)
            if not _string_list(values, allow_empty=True):
                fail(f"authorization.{kind} must be an array of paths", "Use [] or exact repo-relative paths")
                continue
            for path in values:
                normalized = normalise_path(path)
                if not _valid_repo_path(path):
                    fail(f"Invalid authorization path: {path}", "Use an unambiguous repo-relative path")
                    continue
                if normalized in auth_sets[kind]:
                    fail(f"Duplicate authorization path in {kind}: {path}", "List each path once")
                auth_sets[kind].add(normalized)
        for left, right in (("creates", "edits"), ("creates", "removes"), ("edits", "removes")):
            overlap = sorted(auth_sets[left] & auth_sets[right])
            if overlap:
                fail(
                    f"Contradictory authorization in {left}/{right}: {', '.join(overlap)}",
                    "Authorize each path for exactly one lifecycle operation",
                )
        if not any(auth_sets.values()):
            fail("authorization names no paths", "Authorize at least one create, edit, or remove path")
        if check_files:
            compile_time = status == "COMPILE"
            for path in sorted(auth_sets["edits"]):
                if not (REPO_ROOT / path).is_file():
                    fail(f"Authorized edit path does not exist: {path}", "Correct the path or authorize it as a create")
            for path in sorted(auth_sets["removes"]):
                if compile_time and not (REPO_ROOT / path).exists():
                    fail(f"Authorized remove path does not exist: {path}", "Correct the path or remove the authorization")
            for path in sorted(auth_sets["creates"]):
                if compile_time and (REPO_ROOT / path).exists():
                    fail(f"Authorized create path already exists: {path}", "Authorize it as an edit or choose a new path")

    context = packet.get("context")
    if not isinstance(context, list):
        fail("context must be an array", "Use [] or structured context inputs")
    else:
        for index, entry in enumerate(context, 1):
            prefix = f"context[{index}]"
            if not isinstance(entry, dict) or set(entry) != {"path", "scope", "purpose"}:
                fail(f"{prefix} must contain exactly path, scope, and purpose", "Use the canonical context object")
                continue
            path = normalise_path(entry.get("path", "")) if isinstance(entry.get("path"), str) else ""
            if not _valid_repo_path(entry.get("path")):
                fail(f"{prefix}.path is invalid", "Use an exact repo-relative context path")
                continue
            resolved = REPO_ROOT / path
            may_be_removed = path in auth_sets["removes"] and status != "PENDING"
            if check_files and not resolved.is_file() and not may_be_removed:
                fail(f"Context path does not exist: {path}", "Correct the path or remove the context entry")
            if not _is_nonempty_string(entry.get("purpose")):
                fail(f"{prefix}.purpose must be non-empty", "Explain why this context is needed")
            scope = entry.get("scope")
            if not isinstance(scope, dict) or scope.get("kind") not in {"anchor", "lines", "whole_file"}:
                fail(f"{prefix}.scope.kind must be anchor, lines, or whole_file", "Use a canonical context scope")
                continue
            kind = scope["kind"]
            if kind == "whole_file":
                if set(scope) != {"kind"}:
                    fail(f"{prefix} whole_file scope has extra fields", "Use only {'kind': 'whole_file'}")
            elif kind == "anchor":
                if set(scope) != {"kind", "value"} or not _is_nonempty_string(scope.get("value")):
                    fail(f"{prefix} anchor scope requires one value", "Supply the exact anchor string")
                elif check_files and resolved.is_file() and scope["value"] not in resolved.read_text(encoding="utf-8", errors="replace"):
                    fail(f"Context anchor is absent from {path}: {scope['value']}", "Refresh the exact anchor")
            else:
                if set(scope) != {"kind", "start", "end", "anchor"}:
                    fail(f"{prefix} lines scope requires start, end, and anchor", "Use the canonical line scope")
                    continue
                start, end, anchor = scope.get("start"), scope.get("end"), scope.get("anchor")
                if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
                    fail(f"{prefix} has an invalid line range", "Use positive inclusive start/end lines")
                if not _is_nonempty_string(anchor):
                    fail(f"{prefix} line scope requires an anchor", "Supply exact text inside the range")
                elif check_files and resolved.is_file() and isinstance(start, int) and isinstance(end, int):
                    lines = resolved.read_text(encoding="utf-8", errors="replace").splitlines()
                    if end > len(lines) or not any(anchor in line for line in lines[start - 1 : end]):
                        fail(f"Context line anchor is not inside {path}:{start}-{end}", "Refresh the range and anchor")

    known_facts = packet.get("known_facts")
    if not _string_list(known_facts):
        fail("known_facts must be a non-empty string array", "State the settled facts the executor trusts")

    actions = packet.get("actions")
    referenced: set[str] = set()
    if not isinstance(actions, list) or not actions:
        fail("actions must be a non-empty array", "Supply ordered structured actions")
    else:
        authorized = set().union(*auth_sets.values())
        for index, action in enumerate(actions, 1):
            prefix = f"actions[{index}]"
            if not isinstance(action, dict) or action.get("kind") not in {"file", "non_file"}:
                fail(f"{prefix}.kind must be file or non_file", "Use a structured action")
                continue
            if not _is_nonempty_string(action.get("instruction")):
                fail(f"{prefix}.instruction must be non-empty", "State the settled action")
            paths = action.get("paths")
            if action["kind"] == "file":
                if set(action) != {"kind", "paths", "instruction"} or not _string_list(paths):
                    fail(f"{prefix} file action requires paths and instruction", "Name one or more authorized paths")
                    continue
                for path in paths:
                    normalized = normalise_path(path)
                    referenced.add(normalized)
                    if normalized not in authorized:
                        fail(f"Action path is not authorized: {path}", "Add exact authorization or remove it from the action")
            else:
                if set(action) != {"kind", "operation", "paths", "instruction"}:
                    fail(f"{prefix} non_file action has invalid fields", "Use kind, operation, paths, and instruction")
                if paths != []:
                    fail(f"{prefix} non_file action must have paths: []", "Move file work to a file action")
                if not isinstance(action.get("operation"), str) or not re.fullmatch(r"[a-z][a-z0-9_]*", action["operation"]):
                    fail(f"{prefix}.operation must be machine-readable snake_case", "Name the exact non-file operation")
        unused = sorted(set().union(*auth_sets.values()) - referenced)
        if unused:
            fail(f"Authorized paths have no file action: {', '.join(unused)}", "Reference every authorization in an action")

    proof = packet.get("proof")
    if not isinstance(proof, list) or not proof:
        fail("proof must be a non-empty array", "Supply exact executor proof commands")
    else:
        for index, entry in enumerate(proof, 1):
            if not isinstance(entry, dict) or set(entry) != {"cwd", "command", "purpose"}:
                fail(f"proof[{index}] must contain exactly cwd, command, and purpose", "Use a canonical proof entry")
                continue
            if not _valid_repo_path(entry.get("cwd")) and entry.get("cwd") != ".":
                fail(f"proof[{index}].cwd is invalid", "Use . or an exact repo-relative directory")
            elif check_files and not (REPO_ROOT / normalise_path(entry["cwd"])).is_dir():
                fail(f"Proof cwd does not exist: {entry['cwd']}", "Use an existing repo-relative directory")
            for field in ("command", "purpose"):
                if not _is_nonempty_string(entry.get(field)):
                    fail(f"proof[{index}].{field} must be non-empty", f"Supply the exact proof {field}")

    handoff = packet.get("acceptance_handoff")
    if not isinstance(handoff, dict) or set(handoff) != {"coordinator", "validator"}:
        fail("acceptance_handoff must contain coordinator and validator", "Use the canonical handoff object")
    else:
        coordinator = handoff.get("coordinator")
        if not isinstance(coordinator, dict) or set(coordinator) != {"requirements"} or not _string_list(coordinator.get("requirements")):
            fail("Coordinator acceptance requirements are required", "Provide a non-empty requirements array")
        validator = handoff.get("validator")
        if validator is not None and (
            not isinstance(validator, dict)
            or set(validator) != {"requirements"}
            or not _string_list(validator.get("requirements"))
        ):
            fail("validator must be null or contain non-empty requirements", "Do not use a fake validator placeholder")

    for field in ("exclusions", "escalate_if"):
        if not _string_list(packet.get(field)):
            fail(f"{field} must be a non-empty string array", f"State explicit {field.replace('_', ' ')}")

    if _contains_placeholder(packet):
        fail("Packet contains an unresolved placeholder", "Replace TODO/TBD/ellipsis/template markers with settled values")
    return findings


def _json_block(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, ensure_ascii=False)


def render_compiled(packet: dict[str, Any]) -> str:
    """Render immutable, human-readable compile-envelope sections."""
    identity = packet["identity"]
    strength = packet["required_strength"]
    strength_text = strength["level"] + (f" — {strength['reason']}" if strength["reason"] else "")
    lines = [
        f"# WORK ORDER {identity['number']} — {identity['title']}",
        "",
        f"- **OUTPUT:** `{packet['output_path']}`",
        f"- **GOAL:** {identity['goal']}",
        f"- **REQUIRED STRENGTH:** {strength_text}",
        "- **DEPENDS ON:** " + (", ".join(f"`{item}`" for item in packet["depends_on"]) or "none"),
        "",
        "## Authorization",
    ]
    for title, key in (("Creates", "creates"), ("Edits", "edits"), ("Removes", "removes")):
        lines += ["", f"### {title}"]
        values = packet["authorization"][key]
        lines += [*(f"- `{value}`" for value in values)] if values else ["- none"]
    lines += ["", "## Context inputs"]
    if packet["context"]:
        for index, entry in enumerate(packet["context"], 1):
            scope = entry["scope"]
            if scope["kind"] == "whole_file":
                scope_text = "whole file"
            elif scope["kind"] == "anchor":
                scope_text = f"anchor `{scope['value']}`"
            else:
                scope_text = f"lines {scope['start']}-{scope['end']}, anchor `{scope['anchor']}`"
            lines += [f"{index}. `{entry['path']}` — {scope_text}", f"   - Purpose: {entry['purpose']}"]
    else:
        lines.append("- none")
    lines += ["", "## Known facts", *(f"- {fact}" for fact in packet["known_facts"])]
    lines += ["", "## Ordered actions"]
    for index, action in enumerate(packet["actions"], 1):
        if action["kind"] == "file":
            target = ", ".join(f"`{path}`" for path in action["paths"])
            lines.append(f"{index}. **file** ({target}) — {action['instruction']}")
        else:
            lines.append(f"{index}. **non-file `{action['operation']}`** — {action['instruction']}")
    lines += ["", "## Exact proof commands"]
    for index, proof in enumerate(packet["proof"], 1):
        lines += [
            "",
            f"### Proof {index} — {proof['purpose']}",
            f"Working directory: `{proof['cwd']}`",
            "",
            "```text",
            proof["command"],
            "```",
        ]
    lines += ["", "## Acceptance handoff", "", "### Coordinator"]
    lines += [f"- {item}" for item in packet["acceptance_handoff"]["coordinator"]["requirements"]]
    lines += ["", "### Validator"]
    validator = packet["acceptance_handoff"]["validator"]
    lines += [f"- {item}" for item in validator["requirements"]] if validator else ["- none"]
    lines += ["", "## Exclusions", *(f"- {item}" for item in packet["exclusions"])]
    lines += ["", "## Escalate if", *(f"- {item}" for item in packet["escalate_if"])]
    lines += ["", "## Canonical compile packet", "", "```json", _json_block(packet), "```", ""]
    return "\n".join(lines)


def render_order(packet: dict[str, Any]) -> str:
    return render_compiled(packet) + (
        "STATUS: PENDING\n\n"
        "EXECUTOR RESULT:\n"
        "- DEVIATIONS: none\n"
        "- PROOF RESULTS: pending\n"
        "- DIRTY PATHS: pending\n"
        "- AUTHORIZATION AUDIT: pending\n"
        "- ATTEMPTS: 0\n"
        "- ESCALATION: none\n"
    )


def extract_packet(text: str) -> tuple[dict[str, Any] | None, str | None]:
    match = PACKET_RE.search(text)
    if not match:
        return None, "Missing canonical compile packet JSON block"
    try:
        packet = json.loads(match.group("packet"))
    except json.JSONDecodeError as error:
        return None, f"Canonical compile packet is invalid JSON: {error}"
    return packet, None


def _validate_executor_result(text: str, source: str) -> list[OrderError]:
    findings: list[OrderError] = []
    status_match = STATUS_RE.search(text)
    if not status_match:
        return [OrderError(source, "Missing STATUS", "Append the canonical executor result block")]
    status = status_match.group(1).strip()
    if status not in {"PENDING", "DONE"} and not re.fullmatch(r"(?:FAILED|BLOCKED) - .+", status):
        findings.append(OrderError(source, f"Invalid STATUS: {status}", "Use PENDING, DONE, FAILED - reason, or BLOCKED - reason"))
    tail = text[status_match.end() :]
    if not tail.startswith("\n\nEXECUTOR RESULT:\n"):
        findings.append(OrderError(source, "Missing EXECUTOR RESULT block", "Use the deterministic executor result shape"))
        return findings
    values: dict[str, str] = {}
    for key in RESULT_KEYS:
        match = re.search(rf"^- {re.escape(key)}:\s*(.*)$", tail, re.MULTILINE)
        if not match:
            findings.append(OrderError(source, f"Missing executor result field: {key}", "Restore every canonical result field"))
        else:
            values[key] = match.group(1).strip()
    if status == "PENDING":
        expected = {
            "DEVIATIONS": "none",
            "PROOF RESULTS": "pending",
            "DIRTY PATHS": "pending",
            "AUTHORIZATION AUDIT": "pending",
            "ATTEMPTS": "0",
            "ESCALATION": "none",
        }
        for key, value in expected.items():
            if values.get(key) != value:
                findings.append(OrderError(source, f"PENDING result field {key} must be {value}", "Restore the compiled placeholder"))
    else:
        for key in RESULT_KEYS:
            if not values.get(key) or values.get(key) == "pending":
                findings.append(OrderError(source, f"Completed result field is not filled: {key}", "Record truthful executor evidence"))
        if values.get("ATTEMPTS") and not values["ATTEMPTS"].isdigit():
            findings.append(OrderError(source, "ATTEMPTS must be an integer", "Record the number of repair attempts"))
    return findings


def lint_order(order_path: Path, strict: bool = True) -> list[OrderError]:
    """Strictly validate one canonical order; ``strict`` remains API-compatible."""
    del strict
    source = _rel(order_path)
    try:
        text = order_path.read_text(encoding="utf-8")
    except OSError as error:
        return [OrderError(source, f"Cannot read order: {error}", "Restore the order file")]
    packet, packet_error = extract_packet(text)
    if packet_error or packet is None:
        return [OrderError(source, packet_error or "Missing packet", "Regenerate with new_order.py")]
    status_match = STATUS_RE.search(text)
    status = (status_match.group(1).strip().split(" - ", 1)[0] if status_match else "PENDING")
    findings = validate_packet(packet, source=source, check_files=True, status=status)
    output = packet.get("output_path") if isinstance(packet, dict) else None
    if isinstance(output, str) and normalise_path(output) != source:
        findings.append(OrderError(source, "Artifact path contradicts packet output_path", "Move or regenerate the order at its authoritative path"))
    compiled = render_compiled(packet) if not validate_packet(packet, source=source, check_files=False) else None
    envelope = compiled.split("\nSTATUS:", 1)[0] if compiled is not None else None
    if envelope is not None and not text.startswith(envelope):
        findings.append(OrderError(source, "Rendered compile-envelope sections do not match the canonical packet", "Regenerate; do not hand-edit compiled sections"))
    findings.extend(_validate_executor_result(text, source))
    return findings


def lint_orders(
    orders_root: Path | None = None,
    paths: list[Path] | None = None,
    strict: bool = True,
    include_warnings: bool = False,
) -> list[OrderError]:
    """Validate selected orders or discover the canonical active order tree."""
    del strict, include_warnings
    orders = list(paths) if paths is not None else discover_orders(orders_root)
    findings: list[OrderError] = []
    packets: dict[str, dict[str, Any]] = {}
    for order in orders:
        findings.extend(lint_order(order))
        try:
            packet, _ = extract_packet(order.read_text(encoding="utf-8"))
        except OSError:
            packet = None
        if isinstance(packet, dict) and isinstance(packet.get("output_path"), str):
            packets[normalise_path(packet["output_path"])] = packet
    for path, packet in packets.items():
        for dependency in packet.get("depends_on", []):
            normalized = normalise_path(dependency)
            if normalized not in packets and not (REPO_ROOT / normalized).is_file():
                findings.append(OrderError(path, f"Dependency is not present: {dependency}", "Compile or include the dependency"))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Strictly validate canonical work orders.")
    parser.add_argument("paths", nargs="*", help="specific canonical order files")
    args = parser.parse_args(argv)
    paths = [REPO_ROOT / normalise_path(path) for path in args.paths] if args.paths else None
    findings = lint_orders(paths=paths)
    if findings:
        for finding in findings:
            print(finding)
        print(f"\n{len(findings)} work-order contract failure(s).")
        return 1
    count = len(paths) if paths is not None else len(discover_orders())
    print(f"Work-order contract: all checks pass ({count} order{'s' if count != 1 else ''}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
