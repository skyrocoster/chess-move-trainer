"""Enforce small handwritten application and workflow modules."""

from __future__ import annotations

import argparse
from pathlib import Path

SOURCE_SUFFIXES = {".py", ".ts", ".tsx"}
EXCLUDED_NAMES = {
    "package-lock.json",
    "tsconfig.json",
    "tsconfig.app.json",
    "tsconfig.node.json",
    "vite.config.ts",
    "vitest.config.ts",
    "playwright.config.ts",
    "eslint.config.js",
}
SKIP_DIRECTORIES = {".git", ".venv", "node_modules", "__pycache__", "dist", "build"}


def is_test(path: Path) -> bool:
    value = path.as_posix()
    return path.name.startswith("test_") or ".test." in path.name or "/tests/" in value


def source_files() -> list[Path]:
    roots = [Path("backend"), Path("frontend/src"), Path("scripts")]
    return [
        path
        for root in roots
        for path in root.rglob("*")
        if path.suffix in SOURCE_SUFFIXES
        and not any(part in SKIP_DIRECTORIES for part in path.parts)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-max", type=int, required=True)
    parser.add_argument("--test-max", type=int, required=True)
    args = parser.parse_args()
    failures: list[str] = []
    paths = source_files()
    for path in paths:
        if path.name in EXCLUDED_NAMES:
            continue
        limit = args.test_max if is_test(path) else args.source_max
        count = len(path.read_text(encoding="utf-8").splitlines())
        if count > limit:
            failures.append(f"{path}: {count} lines (maximum {limit})")
    if failures:
        print("\n".join(failures))
        return 1
    print(f"Source-size check passed for {len(paths)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
