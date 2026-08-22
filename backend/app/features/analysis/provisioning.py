"""Explicit, pinned, checksum-first Stockfish provisioning without import effects."""

from __future__ import annotations

import json
import os
import shutil
import stat
import tempfile
import time
import urllib.request
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .engine import EngineIdentity, inspect_stockfish_executable, sha256_file
from .errors import StockfishSetupError

STOCKFISH_TAG = "sf_18"
STOCKFISH_ASSET = "stockfish-windows-x86-64-avx2.zip"
STOCKFISH_ARCHIVE_SHA256 = "6f6c272ebd6ea594377715235c8a7326f75940ef4f4f856f45106028fe6ae900"
STOCKFISH_URL = (
    f"https://github.com/official-stockfish/Stockfish/releases/download/"
    f"{STOCKFISH_TAG}/{STOCKFISH_ASSET}"
)
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_INSTALL_DIR = REPOSITORY_ROOT / "data" / "stockfish"
MAX_ARCHIVE_BYTES = 150 * 1024 * 1024
MAX_EXTRACTED_BYTES = 500 * 1024 * 1024


@dataclass(frozen=True)
class ProvisionedStockfish:
    executable: Path
    archive_sha256: str | None
    identity: EngineIdentity


def _download(url: str, target: Path, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    request = urllib.request.Request(url, headers={"User-Agent": "ChessMoveTrainer-MP09/1"})
    try:
        with (
            urllib.request.urlopen(request, timeout=timeout) as response,
            target.open("xb") as output,
        ):
            total = 0
            while block := response.read(1024 * 1024):
                total += len(block)
                if total > MAX_ARCHIVE_BYTES or time.monotonic() > deadline:
                    raise StockfishSetupError(
                        "Stockfish archive download exceeded its safety bound"
                    )
                output.write(block)
    except StockfishSetupError:
        raise
    except Exception as error:
        raise StockfishSetupError(f"pinned Stockfish download failed: {error}") from error


def _safe_member(info: zipfile.ZipInfo) -> PurePosixPath:
    if "\\" in info.filename:
        raise StockfishSetupError("archive member uses unsafe path separators")
    path = PurePosixPath(info.filename)
    mode = info.external_attr >> 16
    if (
        not info.filename
        or path.is_absolute()
        or ".." in path.parts
        or ":" in path.parts[0]
        or stat.S_ISLNK(mode)
        or info.flag_bits & 1
    ):
        raise StockfishSetupError(f"unsafe archive member refused: {info.filename!r}")
    return path


def _extract_safely(archive: Path, destination: Path) -> None:
    try:
        with zipfile.ZipFile(archive) as source:
            members = source.infolist()
            if sum(member.file_size for member in members) > MAX_EXTRACTED_BYTES:
                raise StockfishSetupError("Stockfish archive exceeds extracted-size safety bound")
            for info in members:
                relative = _safe_member(info)
                target = destination.joinpath(*relative.parts)
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with source.open(info) as input_file, target.open("xb") as output_file:
                    shutil.copyfileobj(input_file, output_file)
    except StockfishSetupError:
        raise
    except (OSError, zipfile.BadZipFile) as error:
        raise StockfishSetupError(f"safe Stockfish extraction failed: {error}") from error


def verify_override(
    executable: Path,
    *,
    verifier: Callable[[Path], EngineIdentity] = inspect_stockfish_executable,
) -> ProvisionedStockfish:
    resolved = executable.resolve(strict=True)
    try:
        identity = verifier(resolved)
    except Exception as error:
        raise StockfishSetupError(f"Stockfish executable verification failed: {error}") from error
    if identity.binary_sha256 != sha256_file(resolved):
        raise StockfishSetupError("verified executable checksum changed during inspection")
    return ProvisionedStockfish(resolved, None, identity)


def provision_stockfish(
    *,
    install_dir: Path = DEFAULT_INSTALL_DIR,
    timeout: float = 60.0,
    downloader: Callable[[str, Path, float], None] = _download,
    verifier: Callable[[Path], EngineIdentity] = inspect_stockfish_executable,
) -> ProvisionedStockfish:
    """Download only when explicitly called, then safely and atomically install."""

    if timeout <= 0:
        raise StockfishSetupError("download timeout must be positive")
    if install_dir.exists():
        raise StockfishSetupError(f"refusing to replace existing Stockfish install: {install_dir}")
    install_dir.parent.mkdir(parents=True, exist_ok=True)
    stage_path = Path(tempfile.mkdtemp(prefix=".stockfish-stage-", dir=install_dir.parent))
    try:
        archive = stage_path / STOCKFISH_ASSET
        downloader(STOCKFISH_URL, archive, timeout)
        archive_checksum = sha256_file(archive)
        if archive_checksum != STOCKFISH_ARCHIVE_SHA256:
            raise StockfishSetupError(
                "archive checksum mismatch: expected "
                f"{STOCKFISH_ARCHIVE_SHA256}, got {archive_checksum}"
            )
        extracted = stage_path / "extracted"
        extracted.mkdir()
        _extract_safely(archive, extracted)
        executables = [
            path
            for path in extracted.rglob("*.exe")
            if path.is_file() and path.name.lower().startswith("stockfish")
        ]
        if len(executables) != 1:
            raise StockfishSetupError("archive must contain exactly one Stockfish executable")
        payload = stage_path / "install"
        payload.mkdir()
        installed_executable = payload / executables[0].name
        shutil.copy2(executables[0], installed_executable)
        identity = verifier(installed_executable)
        if identity.binary_sha256 != sha256_file(installed_executable):
            raise StockfishSetupError("installed executable checksum changed during verification")
        metadata = {
            "archive_sha256": archive_checksum,
            "asset": STOCKFISH_ASSET,
            "binary_sha256": identity.binary_sha256,
            "reported_name": identity.reported_name,
            "tag": STOCKFISH_TAG,
            "version": identity.version,
        }
        (payload / "install.json").write_text(
            json.dumps(metadata, sort_keys=True, indent=2) + "\n", encoding="ascii"
        )
        os.replace(payload, install_dir)
        return ProvisionedStockfish(
            install_dir / installed_executable.name, archive_checksum, identity
        )
    except StockfishSetupError:
        raise
    except Exception as error:
        raise StockfishSetupError(f"Stockfish setup failed safely: {error}") from error
    finally:
        shutil.rmtree(stage_path, ignore_errors=True)
