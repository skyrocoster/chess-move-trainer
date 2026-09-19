"""Generate the repository's deterministic Graphify catalogue.

The generator deliberately keeps Graphify behind the application interpreter and
uses only code-only extraction followed by deterministic clustering.  It never
opens the repository database; Graphify's normal ignore handling excludes it.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GRAPHIFY_TIMEOUT_SECONDS = 900
PROVENANCE = "complete pre-commit working tree"
PROVENANCE_NOTE = (
    "This graph represents the complete pre-commit working tree, including local "
    "changes. See manifest.json for per-file content hashes."
)
REFRESH_COMMAND = (
    "timeout 10800s .venv/Scripts/python.exe src/tools/graphify_catalogue.py"
)
REPORT_FRESHNESS = (
    "## Graph Freshness\n"
    "- This report represents the complete pre-commit working tree, including local changes.\n"
    "- See `manifest.json` for per-file content hashes.\n"
    f"- Refresh all layers with `{REFRESH_COMMAND}` (or invoke `/commit`, which runs it first).\n"
)
HTML_PROVENANCE_COMMENT = (
    "<!-- Graphify provenance: complete pre-commit working tree, including local "
    "changes. See manifest.json for per-file content hashes. -->"
)
REQUIRED_ARTIFACTS = (
    "GRAPH_REPORT.md",
    "graph.html",
    "graph.json",
    ".graphify_analysis.json",
    "manifest.json",
)


@dataclass(frozen=True)
class LayerSpec:
    name: str
    source_root: str
    output_dir: str


@dataclass(frozen=True)
class PriorDerivedArtifacts:
    canonical_graph: dict[str, Any]
    analysis: bytes
    report: bytes
    html: bytes


LAYERS = (
    LayerSpec("repository", ".", "docs/graphify/repository"),
    LayerSpec("backend", "backend", "docs/graphify/backend"),
    LayerSpec("frontend", "frontend", "docs/graphify/frontend"),
    LayerSpec("core-data", "src", "docs/graphify/core-data"),
    LayerSpec("tests", "tests", "docs/graphify/tests"),
    LayerSpec("agent-workflow", ".opencode", "docs/graphify/agent-workflow"),
)

KNOWN_EPHEMERAL_FILES = frozenset(
    {
        ".graphify_root",
        ".graphify_stale",
        ".graphify_stale.json",
        ".graphify_query",
        ".graphify_query.json",
        ".graphify_query_stamp",
        ".graphify_labels",
        ".graphify_labels.json",
        ".query_stamp",
        ".query_stamp.json",
        "query_stamp",
        "query_stamp.json",
        "labels.json",
        ".labels.json",
        "community_labels.json",
    }
)
KNOWN_EPHEMERAL_DIRS = frozenset({"cache"})
FORBIDDEN_PATH_RE = re.compile(
    r"(?i)(?:^[\"'`\s(/\\])data(?:[/\\])"
    r"(?:database(?:[/\\])|stockfish(?:[/\\]))"
)
ABSOLUTE_WINDOWS_RE = re.compile(r"(?i)^[a-z]:[/\\]")
PATH_KEYS = frozenset(
    {
        "file",
        "file_name",
        "filename",
        "file_path",
        "filepath",
        "path",
        "relative_path",
        "source_file",
        "source_path",
    }
)


class GraphifyError(RuntimeError):
    """A fail-fast error that identifies the layer and operation involved."""


def _command_text(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def build_graphify_command(action: str, source_root: str) -> list[str]:
    """Build one of the two permitted Graphify commands."""

    if action == "extract":
        return [sys.executable, "-m", "graphify", "extract", source_root, "--code-only"]
    if action == "cluster-only":
        return [
            sys.executable,
            "-m",
            "graphify",
            "cluster-only",
            source_root,
            "--no-label",
        ]
    raise ValueError(f"unsupported Graphify action: {action}")


def _process_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return str(value)


def run_graphify(
    layer: LayerSpec,
    action: str,
    output_dir: Path,
    repository_root: Path = REPOSITORY_ROOT,
) -> None:
    """Run one Graphify operation with the approved environment and timeout."""

    command = build_graphify_command(action, layer.source_root)
    environment = os.environ.copy()
    environment["GRAPHIFY_OUT"] = str(output_dir.resolve())
    environment["PYTHONHASHSEED"] = "0"
    try:
        completed = subprocess.run(
            command,
            cwd=repository_root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=GRAPHIFY_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        stdout = _process_output(error.stdout)
        stderr = _process_output(error.stderr)
        raise GraphifyError(
            f"Graphify layer {layer.name!r} timed out after "
            f"{GRAPHIFY_TIMEOUT_SECONDS}s.\n"
            f"Command: {_command_text(command)}\n"
            f"stdout:\n{stdout}\n"
            f"stderr:\n{stderr}"
        ) from error

    if completed.returncode:
        raise GraphifyError(
            f"Graphify layer {layer.name!r} failed with exit code "
            f"{completed.returncode}.\n"
            f"Command: {_command_text(command)}\n"
            f"stdout:\n{_process_output(completed.stdout)}\n"
            f"stderr:\n{_process_output(completed.stderr)}"
        )


def _known_ephemeral(name: str, is_directory: bool) -> bool:
    if is_directory:
        return name in KNOWN_EPHEMERAL_DIRS
    return name in KNOWN_EPHEMERAL_FILES


def _entry_kind(entry: os.DirEntry[str]) -> str:
    if entry.is_symlink():
        raise GraphifyError(f"Refusing symlink in Graphify output: {entry.path}")
    if entry.is_dir(follow_symlinks=False):
        return "directory"
    if entry.is_file(follow_symlinks=False):
        return "file"
    raise GraphifyError(f"Refusing non-regular Graphify output entry: {entry.path}")


def _validate_known_tree(
    directory: Path,
    allowed_files: frozenset[str],
    allowed_directories: frozenset[str],
) -> None:
    """Validate a complete tree before any allowlisted deletion occurs."""

    if directory.is_symlink():
        raise GraphifyError(f"Refusing symlink Graphify directory: {directory}")
    if not directory.is_dir():
        raise GraphifyError(f"Graphify path is not a directory: {directory}")

    def visit(current: Path, top_level: bool = False) -> None:
        with os.scandir(current) as entries:
            for entry in entries:
                kind = _entry_kind(entry)
                name = entry.name
                if kind == "directory":
                    if top_level and name not in allowed_directories:
                        raise GraphifyError(
                            f"Unknown Graphify output directory refuses cleanup: "
                            f"{entry.path}"
                        )
                    visit(Path(entry.path))
                elif top_level and name not in allowed_files:
                    raise GraphifyError(
                        f"Unknown Graphify output file refuses cleanup: {entry.path}"
                    )

    visit(directory, top_level=True)


def safe_remove_legacy_output(path: Path) -> None:
    """Remove legacy output only after its complete tree passes the allowlist."""

    if not path.exists() and not path.is_symlink():
        return
    _validate_known_tree(
        path,
        frozenset(REQUIRED_ARTIFACTS) | KNOWN_EPHEMERAL_FILES,
        KNOWN_EPHEMERAL_DIRS,
    )
    shutil.rmtree(path)


def _remove_known_entries(directory: Path) -> None:
    """Remove only known Graphify sidecars after the directory is validated."""

    if not directory.exists():
        directory.mkdir(parents=True)
        return
    _validate_known_tree(
        directory,
        frozenset(REQUIRED_ARTIFACTS) | KNOWN_EPHEMERAL_FILES,
        KNOWN_EPHEMERAL_DIRS,
    )
    with os.scandir(directory) as entries:
        for entry in entries:
            kind = _entry_kind(entry)
            if _known_ephemeral(entry.name, kind == "directory"):
                target = Path(entry.path)
                if kind == "directory":
                    shutil.rmtree(target)
                else:
                    target.unlink()


def _assert_safe_path(value: str, label: str) -> None:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ABSOLUTE_WINDOWS_RE.match(value) or normalized.startswith("//"):
        raise GraphifyError(f"Absolute path in generated {label}: {value}")
    if any(part == ".." for part in path.parts):
        raise GraphifyError(f"Parent traversal in generated {label}: {value}")
    lowered = normalized.lower().lstrip("./")
    if lowered.startswith(("data/database/", "data/stockfish/")):
        raise GraphifyError(f"Runtime-data path in generated {label}: {value}")
    if lowered.startswith("docs/graphify/"):
        raise GraphifyError(f"Forbidden generated {label}: {value}")


def _walk_json_paths(value: Any, label: str) -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str) and key.replace("\\", "/").lower().startswith("data/"):
                yield f"{label}.<key>", key
            if isinstance(key, str) and ("/" in key or "\\" in key):
                yield f"{label}.<key>", key
            if isinstance(key, str) and key.lower() in PATH_KEYS and isinstance(child, str):
                yield f"{label}.{key}", child
            yield from _walk_json_paths(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_json_paths(child, f"{label}[{index}]")


def _validate_generated_text(text: str, label: str) -> None:
    normalized = text.replace("\\", "/")
    lowered = normalized.lower()
    if "data/database/chess.db" in lowered or FORBIDDEN_PATH_RE.search(normalized):
        raise GraphifyError(f"Runtime-data path in generated {label}")
    if "docs/graphify/" in lowered:
        raise GraphifyError(f"Self-indexed output path in generated {label}")
    root_text = str(REPOSITORY_ROOT).replace("\\", "/").lower()
    if root_text and root_text in lowered:
        raise GraphifyError(f"Absolute repository path in generated {label}")


def _load_json(path: Path, label: str) -> Any:
    try:
        with path.open(encoding="utf-8") as stream:
            value = json.load(stream)
    except (OSError, json.JSONDecodeError) as error:
        raise GraphifyError(f"Malformed generated {label}: {path}") from error
    for path_label, path_value in _walk_json_paths(value, label):
        _assert_safe_path(path_value, path_label)
    _validate_generated_text(json.dumps(value), label)
    return value


def _validate_artifact_files(output_dir: Path) -> None:
    if not output_dir.is_dir() or output_dir.is_symlink():
        raise GraphifyError(f"Graphify output directory is invalid: {output_dir}")
    names = {entry.name for entry in output_dir.iterdir()}
    required = set(REQUIRED_ARTIFACTS)
    missing = required - names
    extra = names - required
    if missing:
        raise GraphifyError(
            f"Graphify output is missing required artifacts in {output_dir}: "
            f"{sorted(missing)}"
        )
    if extra:
        raise GraphifyError(
            f"Graphify output has unexpected final artifacts in {output_dir}: "
            f"{sorted(extra)}"
        )
    for name in REQUIRED_ARTIFACTS:
        artifact = output_dir / name
        if artifact.is_symlink() or not artifact.is_file():
            raise GraphifyError(f"Graphify artifact is not a regular file: {artifact}")


def _atomic_write_batch(updates: dict[Path, str | bytes]) -> None:
    temporary_paths: list[Path] = []
    try:
        for destination, content in updates.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
            )
            temporary_path = Path(temporary_name)
            temporary_paths.append(temporary_path)
            payload = content if isinstance(content, bytes) else content.encode("utf-8")
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        for temporary_path, destination in zip(temporary_paths, updates):
            os.replace(temporary_path, destination)
        temporary_paths.clear()
    finally:
        for temporary_path in temporary_paths:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def _report_without_stale_commit_claim(report: str) -> str:
    report = re.sub(r"(?im)^.*built from commit.*(?:\n|$)", "", report)
    report = re.sub(
        r"(?im)^.*(?:git rev-parse HEAD|graphify update \.|Run `manifest\.json for per-file content hashes`).*(?:\n|$)",
        "",
        report,
    )
    freshness = re.compile(
        r"(?ims)^## Graph Freshness[ \t]*\r?\n.*?(?=^## |\Z)"
    )
    if freshness.search(report):
        report = freshness.sub(REPORT_FRESHNESS, report, count=1)
    else:
        report = report.rstrip() + "\n\n" + REPORT_FRESHNESS
    if PROVENANCE_NOTE not in report:
        report = report.rstrip() + "\n\n" + PROVENANCE_NOTE + "\n"
    return report


def _html_without_stale_commit_claim(html: str) -> str:
    html = re.sub(r"(?i)built from commit[^<\n]*", "", html)
    html = html.replace("git rev-parse HEAD", "manifest.json for per-file content hashes")
    if HTML_PROVENANCE_COMMENT not in html:
        html = HTML_PROVENANCE_COMMENT + "\n" + html
    return html


def _read_and_validate_bundle(
    output_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    """Read a complete bundle without changing any of its files."""

    _validate_artifact_files(output_dir)
    graph_path = output_dir / "graph.json"
    analysis_path = output_dir / ".graphify_analysis.json"
    manifest_path = output_dir / "manifest.json"
    report_path = output_dir / "GRAPH_REPORT.md"
    html_path = output_dir / "graph.html"

    graph = _load_json(graph_path, "graph.json")
    analysis = _load_json(analysis_path, ".graphify_analysis.json")
    _load_json(manifest_path, "manifest.json")
    try:
        report = report_path.read_text(encoding="utf-8")
        html = html_path.read_text(encoding="utf-8")
    except OSError as error:
        raise GraphifyError(f"Unable to read Graphify report or HTML in {output_dir}") from error
    _validate_generated_text(report, "GRAPH_REPORT.md")
    _validate_generated_text(html, "graph.html")

    if not isinstance(graph, dict) or not isinstance(analysis, dict):
        raise GraphifyError("Graphify graph and analysis artifacts must contain JSON objects")

    return graph, analysis, report, html


def _canonical_graph(graph: dict[str, Any]) -> dict[str, Any]:
    """Remove only the two approved provenance fields before graph comparison."""

    canonical = dict(graph)
    canonical.pop("built_at_commit", None)
    canonical.pop("graphify_provenance", None)
    return canonical


def _capture_prior_derived_artifacts(output_dir: Path) -> PriorDerivedArtifacts | None:
    """Capture a valid normalized bundle before extraction can overwrite it."""

    try:
        graph, analysis, report, html = _read_and_validate_bundle(output_dir)
        if graph.get("built_at_commit") is not None:
            return None
        if graph.get("graphify_provenance") != PROVENANCE:
            return None
        if analysis.get("graphify_provenance") != PROVENANCE:
            return None
        if "built from commit" in report.lower() or "git rev-parse HEAD" in report:
            return None
        if PROVENANCE_NOTE not in report or HTML_PROVENANCE_COMMENT not in html:
            return None
        return PriorDerivedArtifacts(
            canonical_graph=_canonical_graph(graph),
            analysis=(output_dir / ".graphify_analysis.json").read_bytes(),
            report=(output_dir / "GRAPH_REPORT.md").read_bytes(),
            html=(output_dir / "graph.html").read_bytes(),
        )
    except (GraphifyError, OSError, UnicodeError):
        return None


def _restore_prior_derived_artifacts(
    output_dir: Path, prior: PriorDerivedArtifacts
) -> None:
    _atomic_write_batch(
        {
            output_dir / ".graphify_analysis.json": prior.analysis,
            output_dir / "GRAPH_REPORT.md": prior.report,
            output_dir / "graph.html": prior.html,
        }
    )


def _normalize_preserved_derived_artifacts(output_dir: Path) -> None:
    """Apply current report and HTML normalization after restoring prior bytes."""

    report_path = output_dir / "GRAPH_REPORT.md"
    html_path = output_dir / "graph.html"
    try:
        report = report_path.read_text(encoding="utf-8")
        html = html_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise GraphifyError(
            f"Unable to read preserved Graphify report or HTML in {output_dir}"
        ) from error
    _atomic_write_batch(
        {
            report_path: _report_without_stale_commit_claim(report),
            html_path: _html_without_stale_commit_claim(html),
        }
    )


def _normalize_graph_and_validate(output_dir: Path) -> None:
    """Normalize only a newly extracted graph, then validate the full bundle."""

    graph_path = output_dir / "graph.json"
    graph = _load_json(graph_path, "graph.json")
    if not isinstance(graph, dict):
        raise GraphifyError("Graphify graph artifact must contain a JSON object")
    graph["built_at_commit"] = None
    graph["graphify_provenance"] = PROVENANCE
    _atomic_write_batch({graph_path: json.dumps(graph, indent=2, sort_keys=True) + "\n"})
    _read_and_validate_bundle(output_dir)


def normalize_and_validate(output_dir: Path, source_root: str) -> None:
    """Normalize provenance, validate paths, and enforce the five-file contract."""

    graph, analysis, report, html = _read_and_validate_bundle(output_dir)
    graph_path = output_dir / "graph.json"
    analysis_path = output_dir / ".graphify_analysis.json"
    report_path = output_dir / "GRAPH_REPORT.md"
    html_path = output_dir / "graph.html"
    graph["built_at_commit"] = None
    graph["graphify_provenance"] = PROVENANCE
    analysis["graphify_provenance"] = PROVENANCE

    _atomic_write_batch(
        {
            graph_path: json.dumps(graph, indent=2, sort_keys=True) + "\n",
            analysis_path: json.dumps(analysis, indent=2, sort_keys=True) + "\n",
            report_path: _report_without_stale_commit_claim(report),
            html_path: _html_without_stale_commit_claim(html),
        }
    )
    _read_and_validate_bundle(output_dir)


def generate_catalogue(repository_root: Path = REPOSITORY_ROOT) -> None:
    """Generate all layers in order, stopping at the first failure."""

    safe_remove_legacy_output(repository_root / "graphify-out")
    for layer in LAYERS:
        output_dir = repository_root / layer.output_dir
        prior = _capture_prior_derived_artifacts(output_dir)
        _remove_known_entries(output_dir)
        run_graphify(layer, "extract", output_dir, repository_root)
        extracted_graph = _load_json(output_dir / "graph.json", "graph.json")
        if not isinstance(extracted_graph, dict):
            raise GraphifyError("Graphify graph artifact must contain a JSON object")

        if prior is not None and _canonical_graph(extracted_graph) == prior.canonical_graph:
            _remove_known_entries(output_dir)
            _restore_prior_derived_artifacts(output_dir, prior)
            _normalize_preserved_derived_artifacts(output_dir)
            _normalize_graph_and_validate(output_dir)
        else:
            run_graphify(layer, "cluster-only", output_dir, repository_root)
            _remove_known_entries(output_dir)
            normalize_and_validate(output_dir, layer.source_root)


def main() -> int:
    try:
        generate_catalogue()
    except (GraphifyError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
