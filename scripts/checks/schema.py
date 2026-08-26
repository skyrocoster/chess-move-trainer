"""Database schema freshness and regeneration checks."""

from __future__ import annotations

import sys

from scripts.checks.steps import REPO_ROOT, SCHEMA_FIX_COMMAND

# Late import so the module loads even when the database package is absent.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from data.database import dump_schema  # noqa: E402


def regenerate_schema() -> bool:
    try:
        dump_schema.write_schema(dump_schema.OUT_PATH)
    except OSError as exc:
        print("--- Database schema regeneration failed ---", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return False
    print(f"Regenerated database schema: {dump_schema.OUT_PATH}")
    return True


def check_schema_freshness() -> bool:
    fresh_render = dump_schema.render_schema()
    try:
        is_current = dump_schema.OUT_PATH.read_text(encoding="utf-8") == fresh_render
    except FileNotFoundError:
        is_current = False
    if is_current:
        print(f"Passed: Database schema freshness ({dump_schema.OUT_PATH})")
        return True
    print(
        f"Database schema is missing or stale: {dump_schema.OUT_PATH}. "
        f"Run {SCHEMA_FIX_COMMAND} to regenerate it.",
        file=sys.stderr,
    )
    return False
