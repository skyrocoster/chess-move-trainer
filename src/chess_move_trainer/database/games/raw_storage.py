"""Validation, merge, and atomic publication for raw Chess.com month files."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any
from uuid import UUID


class RawMonthError(RuntimeError):
    """Raised when a raw month cannot be validated or published safely."""


def validate_month_envelope(candidate: object) -> list[dict[str, Any]]:
    """Return games when candidate passes the exact object/list/unique-UUID gate."""

    if not isinstance(candidate, dict):
        raise RawMonthError("month response must be a JSON object")
    games = candidate.get("games")
    if not isinstance(games, list):
        raise RawMonthError("month response must contain a top-level games list")

    seen: set[UUID] = set()
    typed_games: list[dict[str, Any]] = []
    for index, game in enumerate(games):
        if not isinstance(game, dict):
            raise RawMonthError(f"game at index {index} must be a JSON object")
        value = game.get("uuid")
        if not isinstance(value, str):
            raise RawMonthError(f"game at index {index} must contain a valid UUID")
        try:
            game_uuid = UUID(value)
        except ValueError as error:
            raise RawMonthError(f"game at index {index} must contain a valid UUID") from error
        if str(game_uuid) != value.lower():
            raise RawMonthError(f"game at index {index} must contain a canonical UUID")
        if game_uuid in seen:
            raise RawMonthError(f"month response contains duplicate game UUID {value}")
        seen.add(game_uuid)
        typed_games.append(game)
    return typed_games


def merge_current_month(
    local_envelope: object, remote_envelope: object
) -> dict[str, Any]:
    """Merge a valid current response over a valid local month by game UUID."""

    local_games = validate_month_envelope(local_envelope)
    remote_games = validate_month_envelope(remote_envelope)
    assert isinstance(remote_envelope, dict)

    merged_games = list(local_games)
    positions = {UUID(game["uuid"]): index for index, game in enumerate(merged_games)}
    for game in remote_games:
        game_uuid = UUID(game["uuid"])
        position = positions.get(game_uuid)
        if position is None:
            positions[game_uuid] = len(merged_games)
            merged_games.append(game)
        else:
            merged_games[position] = game

    merged = dict(remote_envelope)
    merged["games"] = merged_games
    validate_month_envelope(merged)
    return merged


def load_month(path: Path) -> dict[str, Any]:
    """Read and validate an existing raw month file."""

    try:
        candidate = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RawMonthError(f"could not read raw month {path}: {error}") from error
    validate_month_envelope(candidate)
    assert isinstance(candidate, dict)
    return candidate


def publish_month(
    target: Path,
    candidate: object,
    *,
    replace_existing: bool,
    replace: Callable[[Path, Path], None] | None = None,
) -> None:
    """Validate fully, then publish through a flushed same-directory temporary file."""

    validate_month_envelope(candidate)
    if not replace_existing and target.exists():
        raise RawMonthError(f"historical month already exists: {target}")

    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=target.parent,
        prefix=f".{target.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    replace_operation = replace if replace is not None else _atomic_replace
    try:
        payload = json.dumps(candidate, ensure_ascii=False, indent=2) + "\n"
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as temporary_file:
            temporary_file.write(payload)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        descriptor = -1
        if not replace_existing and target.exists():
            raise RawMonthError(f"historical month already exists: {target}")
        replace_operation(temporary, target)
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)
        raise


def _atomic_replace(source: Path, target: Path) -> None:
    os.replace(source, target)
