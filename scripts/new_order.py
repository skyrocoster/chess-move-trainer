#!/usr/bin/env python
"""Render one canonical work order from one lossless JSON compile packet.

Ordinary agents invoke this script and inspect stdout. They do not read its source.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_orders_for_new_order", Path(__file__).resolve().parent / "check_orders.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


co = _load_checker()


class PacketTransportError(Exception):
    pass


def load_packet(source: str) -> dict[str, Any]:
    try:
        if source == "-":
            packet = json.load(sys.stdin)
        else:
            with Path(source).open(encoding="utf-8") as handle:
                packet = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise PacketTransportError(str(error)) from error
    if not isinstance(packet, dict):
        raise PacketTransportError("compile packet must be a JSON object")
    return packet


def _path(value: str) -> str:
    return co.normalise_path(value)


def normalise_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Normalize path separators only; never rewrite commands or prose."""
    normalized = json.loads(json.dumps(packet, ensure_ascii=False))
    if isinstance(normalized.get("output_path"), str):
        normalized["output_path"] = _path(normalized["output_path"])
    if isinstance(normalized.get("depends_on"), list):
        normalized["depends_on"] = [_path(value) for value in normalized["depends_on"]]
    authorization = normalized.get("authorization")
    if isinstance(authorization, dict):
        for key in ("creates", "edits", "removes"):
            if isinstance(authorization.get(key), list):
                authorization[key] = [_path(value) for value in authorization[key]]
    if isinstance(normalized.get("context"), list):
        for entry in normalized["context"]:
            if isinstance(entry, dict) and isinstance(entry.get("path"), str):
                entry["path"] = _path(entry["path"])
    if isinstance(normalized.get("actions"), list):
        for action in normalized["actions"]:
            if isinstance(action, dict) and isinstance(action.get("paths"), list):
                action["paths"] = [_path(value) for value in action["paths"]]
    if isinstance(normalized.get("proof"), list):
        for proof in normalized["proof"]:
            if isinstance(proof, dict) and isinstance(proof.get("cwd"), str):
                proof["cwd"] = _path(proof["cwd"]) or "."
    return normalized


def build(
    packet: dict[str, Any], completed: bool = False, prior_text: str = ""
) -> tuple[Path, str]:
    normalized = normalise_packet(packet)
    findings = co.validate_packet(
        normalized,
        source="<compile packet>",
        check_files=True,
        status="DONE" if completed else "COMPILE",
    )
    if findings:
        raise ValueError("\n".join(str(finding) for finding in findings))
    target = REPO_ROOT / normalized["output_path"]
    text = co.render_order(normalized)
    if completed and "\nSTATUS:" in prior_text:
        text = text.split("\nSTATUS:", 1)[0] + prior_text[prior_text.index("\nSTATUS:") :]
    return target, text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render one canonical order from a structured JSON compile packet."
    )
    parser.add_argument("--packet", required=True, help="JSON file path, or - for stdin")
    parser.add_argument("--force", action="store_true", help="overwrite the exact output_path")
    parser.add_argument(
        "--completed",
        action="store_true",
        help="rematerialize a completed order while preserving its executor result",
    )
    args = parser.parse_args(argv)
    try:
        packet = load_packet(args.packet)
    except PacketTransportError as error:
        print(f"TRANSPORT ERROR: {error}", file=sys.stderr)
        return 2
    try:
        prior_text = ""
        if args.completed:
            target = REPO_ROOT / normalise_packet(packet)["output_path"]
            if target.exists():
                prior_text = target.read_text(encoding="utf-8")
        target, text = build(packet, completed=args.completed, prior_text=prior_text)
    except ValueError as error:
        print(f"REFUSED:\n{error}")
        return 1
    if target.exists() and not args.force:
        print(f"REFUSED: {co._rel(target)} already exists; pass --force to overwrite")
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        findings = co.lint_order(temporary)
        # The temporary filename intentionally differs from output_path; ignore only that
        # placement diagnostic while retaining every structural diagnostic.
        findings = [
            finding
            for finding in findings
            if "Artifact path contradicts packet output_path" not in finding.message
        ]
        if findings:
            raise ValueError("\n".join(str(finding) for finding in findings))
        temporary.replace(target)
    except (OSError, ValueError) as error:
        temporary.unlink(missing_ok=True)
        print(f"REFUSED: rendered order failed validation:\n{error}")
        return 1
    identity = packet.get("identity", {})
    print(
        f"wrote {co._rel(target)} — WORK ORDER {identity.get('number', '?')} "
        f"{identity.get('slug', '?')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
