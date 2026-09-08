"""One-command SETUP-02 export-and-generate orchestrator.

Usage (repository root, no running backend required):

    python scripts/api/generate_client.py           # regenerate the checked-in client
    python scripts/api/generate_client.py --check   # fail on any byte change

Exports the real health-only OpenAPI contract with the accepted
``scripts/api/export_contract.py`` exporter into a temporary file, regenerates
the checked-in TypeScript client with the installed ``@hey-api/openapi-ts``
generator under a finite child-process timeout, and republishes the contract as
``frontend/src/api/generated/openapi.json``. Output cleaning is confined to
``frontend/src/api/generated/`` by the generator configuration, so the
handwritten ``frontend/src/api/client.ts`` can never be overwritten.

``--check`` snapshots SHA-256 hashes of every file under the generated
directory, performs the identical export-and-generate pipeline, and fails with
exit code 1 if any byte changed (hash comparison, not a git diff).
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SCRIPTS_API_DIR = REPO_ROOT / "scripts" / "api"
if str(SCRIPTS_API_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_API_DIR))

from export_contract import export_contract  # noqa: E402

FRONTEND_DIR = REPO_ROOT / "frontend"
GENERATED_DIR = FRONTEND_DIR / "src" / "api" / "generated"
CONTRACT_NAME = "openapi.json"
GENERATOR_BIN = REPO_ROOT / "node_modules" / "@hey-api" / "openapi-ts" / "bin" / "run.js"
CONFIG_NAME = "openapi-ts.config.ts"

# Finite child-process timeout for one generator run. Must stay below the
# finite wrapper timeouts used by the Plan proof commands (180 s).
GENERATOR_TIMEOUT_SECONDS = 150.0
KILL_EXIT_CODE = 124


def _snapshot_hashes() -> dict[str, str]:
    """SHA-256 map of every file under the generated directory, by relative path."""
    if not GENERATED_DIR.is_dir():
        return {}
    hashes: dict[str, str] = {}
    for path in sorted(GENERATED_DIR.rglob("*")):
        if path.is_file():
            rel = path.relative_to(GENERATED_DIR).as_posix()
            hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def _run_generator(input_path: Path) -> None:
    """Run the generator child with cwd=frontend/ under a finite timeout."""
    command = [
        "node",
        str(GENERATOR_BIN),
        "-f",
        CONFIG_NAME,
        "-i",
        str(input_path),
    ]
    try:
        process = subprocess.Popen(command, cwd=FRONTEND_DIR)
    except FileNotFoundError as exc:
        raise RuntimeError(f"generator command not found: {exc.filename}") from exc
    try:
        return_code = process.wait(timeout=GENERATOR_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            capture_output=True,
            timeout=10.0,
        )
        process.wait(timeout=10.0)
        raise RuntimeError(
            f"generator exceeded {GENERATOR_TIMEOUT_SECONDS:g}s and was terminated"
        ) from None
    if return_code != 0:
        raise RuntimeError(f"generator exited with status {return_code}")


def _export_and_generate() -> None:
    """Export the contract to a temp file, generate, and republish the contract."""
    with tempfile.TemporaryDirectory(prefix="setup02-") as tmp:
        contract_path = Path(tmp) / CONTRACT_NAME
        export_contract(contract_path)
        _run_generator(contract_path)
        GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(contract_path, GENERATED_DIR / CONTRACT_NAME)


def _check() -> int:
    """Byte-identical regeneration check driven by file hashes."""
    before = _snapshot_hashes()
    if not before:
        print(
            "check failed: no generated files found under "
            f"{GENERATED_DIR.relative_to(REPO_ROOT).as_posix()}; run generate_client.py first",
            file=sys.stderr,
        )
        return 1
    try:
        _export_and_generate()
    except RuntimeError as exc:
        print(f"check failed: {exc}", file=sys.stderr)
        return 1
    after = _snapshot_hashes()

    changed = sorted(
        name for name in set(before) & set(after) if before[name] != after[name]
    )
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    if changed or added or removed:
        for name in changed:
            print(f"check failed: bytes changed: {name}", file=sys.stderr)
        for name in added:
            print(f"check failed: unexpected new file: {name}", file=sys.stderr)
        for name in removed:
            print(f"check failed: missing file: {name}", file=sys.stderr)
        return 1
    print(f"check passed: byte-identical regeneration of {len(after)} files")
    return 0


def main(argv: list[str] | None = None) -> int:
    check = argv is not None and "--check" in argv
    if not check:
        try:
            _export_and_generate()
        except RuntimeError as exc:
            print(f"generation failed: {exc}", file=sys.stderr)
            return 1
        files = sum(1 for path in GENERATED_DIR.rglob("*") if path.is_file())
        print(f"generated client checked in at src/api/generated/ ({files} files)")
        return 0
    return _check()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
