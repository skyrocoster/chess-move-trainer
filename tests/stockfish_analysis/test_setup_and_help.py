from __future__ import annotations

import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from backend.app.features.analysis import provisioning
from backend.app.features.analysis.engine import EngineIdentity
from backend.app.features.analysis.errors import StockfishSetupError


def _archive(path: Path, members: dict[str, bytes]) -> str:
    with zipfile.ZipFile(path, "w") as archive:
        for name, value in members.items():
            archive.writestr(name, value)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fake_verifier(path: Path) -> EngineIdentity:
    checksum = hashlib.sha256(path.read_bytes()).hexdigest()
    return EngineIdentity("Stockfish 18 fake", "18", checksum)


def test_pinned_setup_is_checksum_first_atomic_and_cleans_staging(
    tmp_path: Path, monkeypatch
) -> None:
    install = tmp_path / "stockfish"

    def download(url: str, target: Path, timeout: float) -> None:
        assert url == provisioning.STOCKFISH_URL
        assert timeout == 7
        checksum = _archive(target, {"stockfish/stockfish-windows-x86-64-avx2.exe": b"fake"})
        monkeypatch.setattr(provisioning, "STOCKFISH_ARCHIVE_SHA256", checksum)

    result = provisioning.provision_stockfish(
        install_dir=install, timeout=7, downloader=download, verifier=_fake_verifier
    )

    assert result.executable.is_file()
    assert (install / "install.json").is_file()
    assert result.archive_sha256 == provisioning.STOCKFISH_ARCHIVE_SHA256
    assert not list(tmp_path.glob(".stockfish-stage-*"))


def test_checksum_failure_happens_before_extraction_and_cleans_everything(
    tmp_path: Path, monkeypatch
) -> None:
    install = tmp_path / "stockfish"
    extracted = False

    def download(_url: str, target: Path, _timeout: float) -> None:
        target.write_bytes(b"wrong archive")

    def extraction_spy(_archive_path: Path, _destination: Path) -> None:
        nonlocal extracted
        extracted = True

    monkeypatch.setattr(provisioning, "_extract_safely", extraction_spy)
    with pytest.raises(StockfishSetupError, match="checksum mismatch"):
        provisioning.provision_stockfish(
            install_dir=install, downloader=download, verifier=_fake_verifier
        )

    assert not extracted
    assert not install.exists()
    assert not list(tmp_path.glob(".stockfish-stage-*"))


@pytest.mark.parametrize("unsafe_name", ["../escape.exe", "/absolute.exe", "C:/drive.exe"])
def test_safe_extraction_refuses_traversal_and_absolute_paths(
    tmp_path: Path, unsafe_name: str
) -> None:
    archive = tmp_path / "unsafe.zip"
    _archive(archive, {unsafe_name: b"unsafe"})

    with pytest.raises(StockfishSetupError, match="unsafe"):
        provisioning._extract_safely(archive, tmp_path / "output")

    assert not (tmp_path / "escape.exe").exists()


def test_setup_failure_after_extraction_removes_payload_and_stage(
    tmp_path: Path, monkeypatch
) -> None:
    install = tmp_path / "stockfish"

    def download(_url: str, target: Path, _timeout: float) -> None:
        checksum = _archive(target, {"stockfish/stockfish.exe": b"fake"})
        monkeypatch.setattr(provisioning, "STOCKFISH_ARCHIVE_SHA256", checksum)

    def failed_verifier(_path: Path) -> EngineIdentity:
        raise RuntimeError("bad reported version")

    with pytest.raises(StockfishSetupError, match="failed safely"):
        provisioning.provision_stockfish(
            install_dir=install, downloader=download, verifier=failed_verifier
        )
    assert not install.exists()
    assert not list(tmp_path.glob(".stockfish-stage-*"))


def test_explicit_override_verifies_identity_and_checksum_without_install(tmp_path: Path) -> None:
    executable = tmp_path / "external.exe"
    executable.write_bytes(b"external fake")

    result = provisioning.verify_override(executable, verifier=_fake_verifier)

    assert result.executable == executable.resolve()
    assert result.archive_sha256 is None
    assert result.identity.binary_sha256 == hashlib.sha256(b"external fake").hexdigest()


@pytest.mark.parametrize(
    "script_name, expected",
    [
        ("setup_stockfish.py", "--executable"),
        ("benchmark_stockfish.py", "--executable"),
        ("analyze_positions.py", "--engine"),
    ],
)
def test_cli_help_is_import_safe_and_non_mutating(
    tmp_path: Path, script_name: str, expected: str
) -> None:
    script = Path(__file__).resolve().parents[2] / "scripts" / "stockfish_analysis" / script_name
    before = set(tmp_path.iterdir())
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert expected in result.stdout
    assert set(tmp_path.iterdir()) == before
