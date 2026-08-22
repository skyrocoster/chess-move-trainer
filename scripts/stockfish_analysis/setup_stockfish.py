"""Explicit Stockfish 18 setup or external executable verification command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.features.analysis.errors import StockfishSetupError  # noqa: E402
from backend.app.features.analysis.provisioning import (  # noqa: E402
    DEFAULT_INSTALL_DIR,
    provision_stockfish,
    verify_override,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Explicitly provision pinned Stockfish 18 or verify an override."
    )
    parser.add_argument(
        "--executable",
        type=Path,
        help="verify this explicit executable instead of downloading or installing",
    )
    parser.add_argument("--timeout", type=float, default=60.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = (
            verify_override(args.executable)
            if args.executable
            else provision_stockfish(timeout=args.timeout)
        )
        print(f"executable: {result.executable}")
        print(f"binary_sha256: {result.identity.binary_sha256}")
        print(f"reported_name: {result.identity.reported_name}")
        if result.archive_sha256:
            print(f"archive_sha256: {result.archive_sha256}")
            print(f"install_dir: {DEFAULT_INSTALL_DIR}")
        return 0
    except (OSError, StockfishSetupError) as error:
        print(f"Stockfish setup failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
