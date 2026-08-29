"""Storybook coverage report — checks that every component has a story."""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path

from scripts.checks.steps import REPO_ROOT

FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
STORYBOOK_CONFIG = REPO_ROOT / "frontend" / ".storybook" / "main.ts"

# Components to exclude from the "missing story" report.
# These are infrastructure / entry-point files, not UI components.
_EXCLUDED_COMPONENTS = {"main.tsx", "App.tsx"}

# File suffixes to skip when scanning for components.
_COMPONENT_SKIP_SUFFIXES = (".test.tsx", ".spec.tsx", ".test.ts", ".spec.ts")

# Exported declarations that mark a .tsx file as a UI component. Helper modules
# (test helpers, story render helpers) export plain functions and constants but
# no PascalCase component, so they are not "components" for coverage purposes.
_COMPONENT_EXPORT_RE = re.compile(
    r"export\s+(?:default\s+)?function\s+[A-Z]|export\s+default\s+[A-Z]"
)


def _exports_component(path: Path) -> bool:
    """Return True when a .tsx file exports a component declaration."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return True
    return bool(_COMPONENT_EXPORT_RE.search(text))


def _parse_story_globs(config_path: Path) -> list[tuple[str, str]]:
    """Extract and normalise glob patterns from .storybook/main.ts.

    Returns a list of ``(dir_prefix, file_pattern)`` tuples ready for
    matching.  ``dir_prefix`` is the directory portion up to (but not
    including) the ``**`` wildcard; ``file_pattern`` is the filename glob
    after the last ``**/`` separator.  Patterns are relative to
    ``frontend/``.
    """
    text = config_path.read_text(encoding="utf-8")
    match = re.search(r"stories\s*:\s*\[(.*?)\]", text, re.DOTALL)
    if not match:
        return []
    block = match.group(1)
    raw = re.findall(r'"([^"]+)"', block)
    result: list[tuple[str, str]] = []
    for pattern in raw:
        normalised = re.sub(r"^\.\.\/src\/", "src/", pattern)
        # Expand POSIX extglob @(a|b) → {a,b} then split into pairs.
        normalised = re.sub(
            r"@\(([^)]+)\)",
            lambda m: "{" + m.group(1).replace("|", ",") + "}",
            normalised,
        )
        # Split on ** to get dir prefix and file glob.
        parts = normalised.split("**/")
        if len(parts) == 2:
            dir_prefix = parts[0]  # e.g. "src/features/design-system/"
            file_glob = parts[1]  # e.g. "stories.{ts,tsx}"
            # Expand {ts,tsx} into individual file patterns.
            brace_match = re.match(r"(.+)\.\{([^}]+)\}$", file_glob)
            if brace_match:
                stem_part = brace_match.group(1)
                extensions = brace_match.group(2).split(",")
                for ext in extensions:
                    result.append((dir_prefix, f"{stem_part}.{ext}"))
            else:
                result.append((dir_prefix, file_glob))
    return result


def _story_matches_globs(
    rel_path: str,
    globs: list[tuple[str, str]],
) -> bool:
    """Check if a relative story path matches any of the normalised globs."""
    for dir_prefix, file_glob in globs:
        if not rel_path.startswith(dir_prefix):
            continue
        filename = rel_path[len(dir_prefix) :]
        if fnmatch.fnmatch(filename, file_glob):
            return True
    return False


def check_storybook_coverage() -> bool:
    """Report components without stories, story/component mismatches, and undiscovered stories.

    This is a soft check — it always returns ``True`` so the check suite never
    fails on coverage gaps.  Problems are printed to stdout for the developer
    to review.
    """
    if not STORYBOOK_CONFIG.is_file():
        print("Skipped: Storybook coverage (no .storybook/main.ts)")
        return True

    # --- collect stories -------------------------------------------------
    story_files = set(FRONTEND_SRC.rglob("*.stories.tsx"))
    story_stems = {s.stem.replace(".stories", ""): s for s in story_files}

    # --- collect components ----------------------------------------------
    component_files: dict[str, Path] = {}
    for path in FRONTEND_SRC.rglob("*.tsx"):
        if path in story_files:
            continue
        if path.name in _EXCLUDED_COMPONENTS:
            continue
        if any(path.name.endswith(sfx) for sfx in _COMPONENT_SKIP_SUFFIXES):
            continue
        if not _exports_component(path):
            continue
        component_files[path.stem] = path

    # --- match by stem ---------------------------------------------------
    missing: list[Path] = []
    mismatches: list[Path] = []
    for stem, comp_path in sorted(component_files.items()):
        if stem in story_stems:
            continue
        # Check whether a story exists but with a different name (mismatch).
        # Approximate by checking whether any story in the same directory
        # imports the component by name.
        same_dir_stories = [s for s in story_files if s.parent == comp_path.parent]
        covered = False
        for sf in same_dir_stories:
            try:
                head = sf.read_text(encoding="utf-8")[:2000]
            except OSError:
                continue
            if comp_path.stem in head:
                covered = True
                break
        if covered:
            mismatches.append(comp_path)
        else:
            missing.append(comp_path)

    # --- check glob coverage against .storybook/main.ts ------------------
    globs = _parse_story_globs(STORYBOOK_CONFIG)
    undiscovered: list[Path] = []
    if globs:
        for sf in sorted(story_files):
            rel = sf.relative_to(REPO_ROOT / "frontend").as_posix()
            if not _story_matches_globs(rel, globs):
                undiscovered.append(sf)

    # --- report ----------------------------------------------------------
    if not missing and not mismatches and not undiscovered:
        return True

    sections: list[str] = []
    if missing:
        lines = [f"  {p.relative_to(FRONTEND_SRC)}" for p in missing]
        sections.append("Components without stories:\n" + "\n".join(lines))
    if mismatches:
        lines = [
            f"  {p.relative_to(FRONTEND_SRC)} (covered by differently-named story)"
            for p in mismatches
        ]
        sections.append("Name mismatches (story name != component name):\n" + "\n".join(lines))
    if undiscovered:
        lines = [f"  {p.relative_to(FRONTEND_SRC)}" for p in undiscovered]
        sections.append("Stories not matched by .storybook/main.ts globs:\n" + "\n".join(lines))

    print("Storybook coverage gaps:\n" + "\n\n".join(sections))
    return True
