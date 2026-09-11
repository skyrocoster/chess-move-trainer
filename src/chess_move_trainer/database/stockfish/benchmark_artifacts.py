"""Atomic artifact persistence for benchmarks."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import tempfile
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Protocol

from ..analysis import AnalysisQuality
from ..positions import CanonicalPosition, canonicalize_fen
from .configuration import (
    CONFIGURATION_VERSION,
    MULTI_PV,
    STOCKFISH_NAME,
    STOCKFISH_VERSION,
    StockfishProfile,
)
from .engine import ANALYSIS_WATCHDOG_SECONDS, SearchMetrics, StockfishEngine

BENCHMARK_FORMAT_VERSION: Final[int] = 1
from .benchmark_models import BENCHMARK_FORMAT_VERSION, DEFAULT_ARTIFACT_WRITE_RETRIES, DEFAULT_HASH_SIZES_MB, DEFAULT_NODE_BUDGETS, DEFAULT_REPETITIONS, DEFAULT_SHUFFLE_SEED, DEFAULT_THREAD_COUNTS, _MAX_DIAGNOSTIC_LENGTH, BenchmarkError, BenchmarkInputError


class ArtifactWriter(Protocol):
    """The small persistence seam used by the runner and focused tests."""

    def write_json(self, path: Path, payload: Mapping[str, Any]) -> None: ...

    def write_text(self, path: Path, content: str) -> None: ...

    def append_jsonl(self, path: Path, payload: Mapping[str, Any]) -> None: ...


class AtomicArtifactWriter:
    """Write benchmark artifacts atomically, keeping temporary files local."""

    def write_json(self, path: Path, payload: Mapping[str, Any]) -> None:
        self.write_text(
            path,
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n",
        )

    def write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                temporary.write(content)
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_path, path)
        except BaseException:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except OSError:
                    pass
            raise

    def append_jsonl(self, path: Path, payload: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = (
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        starting_size: int | None = None
        try:
            with path.open("ab") as stream:
                starting_size = stream.tell()
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError:
            if starting_size is not None:
                try:
                    with path.open("r+b") as stream:
                        stream.truncate(starting_size)
                except OSError:
                    pass
            raise


@dataclass(frozen=True, slots=True)
class _ArtifactPaths:
    directory: Path
    manifest: Path
    attempts: Path
    checkpoint: Path
    summary_json: Path
    summary_csv: Path
    status: Path


@dataclass(frozen=True, slots=True)
class _StoredAttempts:
    records: tuple[dict[str, Any], ...]
    successful_job_ids: frozenset[str]
    failed_job_ids: frozenset[str]

def _normalized_directory(path: Path) -> Path:
    try:
        return path.expanduser().resolve(strict=False)
    except (OSError, RuntimeError) as error:
        raise BenchmarkInputError("output directory could not be normalized") from error


def _normalized_file_path(path: Path) -> Path:
    try:
        return path.expanduser().resolve(strict=False)
    except (OSError, RuntimeError) as error:
        raise BenchmarkInputError(f"path could not be normalized: {path}") from error


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(directory.resolve(strict=False))
    except ValueError:
        return False
    return True


def _sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    if not path.is_file():
        raise BenchmarkInputError(f"explicit input path is not a file: {path}")
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise BenchmarkInputError(f"could not read explicit input path: {path}") from error
    return digest.hexdigest()


def _is_transient_artifact_error(error: OSError) -> bool:
    if isinstance(error, PermissionError):
        return True
    return getattr(error, "winerror", None) in {5, 32, 33}


def _bounded_message(error: BaseException) -> str:
    message = str(error).replace("\r", " ").replace("\n", " ").strip()
    return message[:_MAX_DIAGNOSTIC_LENGTH] or error.__class__.__name__

