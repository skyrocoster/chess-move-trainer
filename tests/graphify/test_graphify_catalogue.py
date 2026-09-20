from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

import pytest

from src.tools import graphify_catalogue as catalogue

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_generator_is_owned_by_src_tools_and_resolves_repository_root() -> None:
    assert Path(catalogue.__file__).resolve() == PROJECT_ROOT / "src/tools/graphify_catalogue.py"
    assert catalogue.REPOSITORY_ROOT == PROJECT_ROOT
    assert not (PROJECT_ROOT / "tools/graphify_catalogue.py").exists()
    assert Path(catalogue.__file__).resolve().parent != PROJECT_ROOT / "src/chess_move_trainer"


def _artifact_fixture(output: Path, *, unsafe_path: str | None = None) -> bytes:
    output.mkdir(parents=True, exist_ok=True)
    graph: dict[str, object] = {"built_at_commit": "old-commit", "nodes": []}
    if unsafe_path is not None:
        graph["nodes"] = [{"file_path": unsafe_path}]
    analysis = {"communities": [], "built_at_commit": "old-commit"}
    manifest = {
        "files": {
            "chess_move_trainer/example.py": {
                "mtime": 1,
                "seen": True,
                "ast_hash": "ast-before",
                "semantic_hash": "semantic-before",
            }
        }
    }
    (output / "graph.json").write_text(json.dumps(graph), encoding="utf-8")
    (output / ".graphify_analysis.json").write_text(json.dumps(analysis), encoding="utf-8")
    manifest_bytes = (json.dumps(manifest, indent=2) + "\n").encode()
    (output / "manifest.json").write_bytes(manifest_bytes)
    (output / "GRAPH_REPORT.md").write_text(
        "# Graph\n\nBuilt from commit: old-commit\nRun `git rev-parse HEAD` to refresh.\n",
        encoding="utf-8",
    )
    (output / "graph.html").write_text(
        "<html><body>Built from commit: old-commit</body></html>", encoding="utf-8"
    )
    return manifest_bytes


def test_six_layer_map_includes_complete_src_core_worker_package() -> None:
    assert [(layer.name, layer.source_root, layer.output_dir) for layer in catalogue.LAYERS] == [
        ("repository", ".", "docs/graphify/repository"),
        ("backend", "backend", "docs/graphify/backend"),
        ("frontend", "frontend", "docs/graphify/frontend"),
        ("core-data", "src", "docs/graphify/core-data"),
        ("tests", "tests", "docs/graphify/tests"),
        ("agent-workflow", ".opencode", "docs/graphify/agent-workflow"),
    ]


def test_commands_use_code_only_no_label_and_application_interpreter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[dict[str, object]] = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append({"command": command, **kwargs})
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(catalogue.subprocess, "run", fake_run)
    output = tmp_path / "bundle"
    layer = catalogue.LAYERS[3]
    catalogue.run_graphify(layer, "extract", output, tmp_path)
    catalogue.run_graphify(layer, "cluster-only", output, tmp_path)

    assert calls[0]["command"] == [
        sys.executable,
        "-m",
        "graphify",
        "extract",
        "src",
        "--code-only",
    ]
    assert calls[1]["command"] == [
        sys.executable,
        "-m",
        "graphify",
        "cluster-only",
        "src",
        "--no-label",
    ]
    assert calls[0]["env"]["GRAPHIFY_OUT"] == str(output.resolve())  # type: ignore[index]
    assert calls[0]["env"]["PYTHONHASHSEED"] == "0"  # type: ignore[index]
    assert calls[0]["timeout"] == 900
    assert "--semantic" not in calls[0]["command"]
    assert "--api" not in calls[0]["command"]


def test_graphify_failure_is_finite_reported_and_stops_before_next_operation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def fail_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command[3])
        return subprocess.CompletedProcess(command, 17, "child stdout", "child stderr")

    monkeypatch.setattr(catalogue.subprocess, "run", fail_run)
    with pytest.raises(catalogue.GraphifyError) as raised:
        catalogue.run_graphify(catalogue.LAYERS[0], "extract", Path("bundle"), PROJECT_ROOT)

    message = str(raised.value)
    assert calls == ["extract"]
    assert "repository" in message
    assert "child stdout" in message
    assert "child stderr" in message
    assert "--code-only" in message


def test_catalogue_stops_at_failing_layer(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[tuple[str, str]] = []

    def fake_run(layer: catalogue.LayerSpec, action: str, output: Path, root: Path) -> None:
        calls.append((layer.name, action))
        if action == "extract" and layer.name == "repository":
            output.mkdir(parents=True, exist_ok=True)
            (output / "graph.json").write_text(json.dumps({"nodes": []}), encoding="utf-8")
        if layer.name == "backend":
            raise catalogue.GraphifyError("controlled backend failure")

    monkeypatch.setattr(catalogue, "run_graphify", fake_run)
    monkeypatch.setattr(catalogue, "normalize_and_validate", lambda output, source: None)
    with pytest.raises(catalogue.GraphifyError, match="controlled backend failure"):
        catalogue.generate_catalogue(tmp_path)
    assert calls == [
        ("repository", "extract"),
        ("repository", "cluster-only"),
        ("backend", "extract"),
    ]


def test_provenance_is_normalized_atomically_and_manifest_is_preserved(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    manifest_before = _artifact_fixture(output)
    catalogue.normalize_and_validate(output, "src")

    graph = json.loads((output / "graph.json").read_text(encoding="utf-8"))
    analysis = json.loads((output / ".graphify_analysis.json").read_text(encoding="utf-8"))
    assert graph["built_at_commit"] is None
    assert graph["graphify_provenance"] == catalogue.PROVENANCE
    assert analysis["graphify_provenance"] == catalogue.PROVENANCE
    report = (output / "GRAPH_REPORT.md").read_text(encoding="utf-8")
    html = (output / "graph.html").read_text(encoding="utf-8")
    assert "Built from commit" not in report
    assert "git rev-parse HEAD" not in report
    assert catalogue.REPORT_FRESHNESS in report
    assert catalogue.REFRESH_COMMAND in report
    assert "graphify update ." not in report
    assert "Run `manifest.json for per-file content hashes`" not in report
    assert catalogue.PROVENANCE_NOTE in report
    assert catalogue.HTML_PROVENANCE_COMMENT in html
    assert (output / "manifest.json").read_bytes() == manifest_before
    assert not list(output.glob("*.tmp"))


def test_artifact_contract_rejects_missing_and_unexpected_entries(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    _artifact_fixture(output)
    (output / "manifest.json").unlink()
    with pytest.raises(catalogue.GraphifyError, match="missing required artifacts"):
        catalogue.normalize_and_validate(output, "src")

    _artifact_fixture(output)
    (output / "unexpected.txt").write_text("no", encoding="utf-8")
    with pytest.raises(catalogue.GraphifyError, match="unexpected final artifacts"):
        catalogue.normalize_and_validate(output, "src")


def test_tracked_data_is_allowed_but_runtime_data_is_rejected_without_database_access(
    tmp_path: Path,
) -> None:
    output = tmp_path / "tracked-data-bundle"
    _artifact_fixture(output, unsafe_path="data/chess-com/supported.json")
    catalogue.normalize_and_validate(output, "src")
    graph = json.loads((output / "graph.json").read_text(encoding="utf-8"))
    assert graph["nodes"][0]["file_path"] == "data/chess-com/supported.json"

    output = tmp_path / "runtime-data-bundle"
    _artifact_fixture(output, unsafe_path="../data/database/chess.db")
    with pytest.raises(catalogue.GraphifyError, match="Parent traversal"):
        catalogue.normalize_and_validate(output, "src")

    _artifact_fixture(output, unsafe_path="data/database/chess.db")
    with pytest.raises(catalogue.GraphifyError, match="Runtime-data path"):
        catalogue.normalize_and_validate(output, "src")


def test_allowlist_cleanup_removes_known_tree_but_refuses_unknown_content(tmp_path: Path) -> None:
    legacy = tmp_path / "graphify-out"
    _artifact_fixture(legacy)
    (legacy / ".graphify_root").write_text(str(tmp_path), encoding="utf-8")
    (legacy / "cache").mkdir()
    (legacy / "cache" / "known.tmp").write_text("cache", encoding="utf-8")
    catalogue.safe_remove_legacy_output(legacy)
    assert not legacy.exists()

    blocked = tmp_path / "blocked-graphify-out"
    _artifact_fixture(blocked)
    marker = blocked / "unknown.txt"
    marker.write_text("preserve me", encoding="utf-8")
    with pytest.raises(catalogue.GraphifyError, match="Unknown Graphify output file"):
        catalogue.safe_remove_legacy_output(blocked)
    assert marker.exists()


def _single_layer_catalogue(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    extracted_graph: dict[str, object],
    *,
    cluster_writer: object | None = None,
    report_override: str | None = None,
) -> list[str]:
    output = tmp_path / catalogue.LAYERS[3].output_dir
    _artifact_fixture(output)
    catalogue.normalize_and_validate(output, "src")
    if report_override is not None:
        (output / "GRAPH_REPORT.md").write_text(report_override, encoding="utf-8")
    calls: list[str] = []

    def fake_run(layer: catalogue.LayerSpec, action: str, destination: Path, root: Path) -> None:
        calls.append(action)
        if action == "extract":
            (destination / "graph.json").write_text(json.dumps(extracted_graph), encoding="utf-8")
        elif cluster_writer is not None:
            cluster_writer(destination)

    monkeypatch.setattr(catalogue, "LAYERS", (catalogue.LAYERS[3],))
    monkeypatch.setattr(catalogue, "run_graphify", fake_run)
    catalogue.generate_catalogue(tmp_path)
    return calls


def test_unchanged_canonical_graph_preserves_derived_bytes_without_clustering(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    output = tmp_path / catalogue.LAYERS[3].output_dir
    _artifact_fixture(output)
    catalogue.normalize_and_validate(output, "src")
    prior_bytes = {
        name: (output / name).read_bytes()
        for name in (".graphify_analysis.json", "GRAPH_REPORT.md", "graph.html")
    }

    calls: list[str] = []

    def fake_run(layer: catalogue.LayerSpec, action: str, destination: Path, root: Path) -> None:
        calls.append(action)
        if action == "extract":
            (destination / "graph.json").write_text(
                json.dumps(
                    {
                        "built_at_commit": "new-commit",
                        "nodes": [],
                    }
                ),
                encoding="utf-8",
            )
            (destination / ".graphify_analysis.json").write_text("varied", encoding="utf-8")
            (destination / "GRAPH_REPORT.md").write_text("varied", encoding="utf-8")
            (destination / "graph.html").write_text("varied", encoding="utf-8")
        else:
            pytest.fail("unchanged graph entered clustering")

    monkeypatch.setattr(catalogue, "LAYERS", (catalogue.LAYERS[3],))
    monkeypatch.setattr(catalogue, "run_graphify", fake_run)
    catalogue.generate_catalogue(tmp_path)

    assert calls == ["extract"]
    for name, content in prior_bytes.items():
        assert (output / name).read_bytes() == content
    report = (output / "GRAPH_REPORT.md").read_text(encoding="utf-8")
    assert catalogue.REPORT_FRESHNESS in report
    assert "graphify update ." not in report
    assert "Run `manifest.json for per-file content hashes`" not in report


def test_substantive_graph_change_recomputes_and_normalizes_derived_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def write_clustered_output(destination: Path) -> None:
        (destination / ".graphify_analysis.json").write_text(
            json.dumps({"communities": ["changed"]}), encoding="utf-8"
        )
        (destination / "GRAPH_REPORT.md").write_text(
            "# Changed\nBuilt from commit: child\nRun `git rev-parse HEAD`.\n",
            encoding="utf-8",
        )
        (destination / "graph.html").write_text(
            "<html>Built from commit: child</html>", encoding="utf-8"
        )

    calls = _single_layer_catalogue(
        monkeypatch,
        tmp_path,
        {"built_at_commit": "new-commit", "nodes": [{"name": "new-node"}]},
        cluster_writer=write_clustered_output,
    )

    assert calls == ["extract", "cluster-only"]
    output = tmp_path / "docs/graphify/core-data"
    analysis = json.loads((output / ".graphify_analysis.json").read_text(encoding="utf-8"))
    graph = json.loads((output / "graph.json").read_text(encoding="utf-8"))
    report = (output / "GRAPH_REPORT.md").read_text(encoding="utf-8")
    html = (output / "graph.html").read_text(encoding="utf-8")
    assert graph["nodes"] == [{"name": "new-node"}]
    assert graph["built_at_commit"] is None
    assert analysis["communities"] == ["changed"]
    assert analysis["graphify_provenance"] == catalogue.PROVENANCE
    assert "Built from commit" not in report
    assert "git rev-parse HEAD" not in report
    assert catalogue.HTML_PROVENANCE_COMMENT in html


def test_provenance_only_graph_differences_do_not_recompute_clustering(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls = _single_layer_catalogue(
        monkeypatch,
        tmp_path,
        {
            "built_at_commit": "another-commit",
            "graphify_provenance": "another provenance",
            "nodes": [],
        },
    )

    assert calls == ["extract"]


def test_unchanged_graph_repairs_legacy_report_guidance_without_clustering(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    legacy_report = (
        "# Graph\n\n## Graph Freshness\n"
        "- Run `manifest.json for per-file content hashes` and compare to check "
        "if the graph is stale.\n"
        "- Run `graphify update .` after code changes (no API cost).\n\n"
        f"{catalogue.PROVENANCE_NOTE}\n"
    )
    calls = _single_layer_catalogue(
        monkeypatch,
        tmp_path,
        {"built_at_commit": "new-commit", "nodes": []},
        report_override=legacy_report,
    )

    assert calls == ["extract"]
    report = (tmp_path / "docs/graphify/core-data/GRAPH_REPORT.md").read_text(encoding="utf-8")
    assert catalogue.REPORT_FRESHNESS in report
    assert "git rev-parse HEAD" not in report
    assert "Run `manifest.json for per-file content hashes`" not in report
    assert "graphify update ." not in report


def test_ignore_rules_are_narrow_and_exclude_graphify_outputs() -> None:
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    graphifyignore = (PROJECT_ROOT / ".graphifyignore").read_text(encoding="utf-8")
    assert "/graphify-out/" in gitignore
    assert "docs/graphify/**/cache/" in gitignore
    assert "!.opencode/commands/" in gitignore
    assert "!.opencode/commands/commit.md" in gitignore
    assert "!.opencode/**" not in gitignore
    assert "/docs/graphify/" in graphifyignore
    assert "/graphify-out/" in graphifyignore


def _assert_relative_catalogue_path(value: str) -> None:
    normalized = value.replace("\\", "/")
    assert not normalized.startswith(("/", "//"))
    assert not (len(normalized) > 1 and normalized[1] == ":")
    assert not PurePosixPath(normalized).is_absolute()
    assert ".." not in PurePosixPath(normalized).parts


def _graph_path_values(value: object) -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if (
                isinstance(key, str)
                and key.lower() in catalogue.PATH_KEYS
                and isinstance(child, str)
            ):
                paths.append(child)
            paths.extend(_graph_path_values(child))
    elif isinstance(value, list):
        for child in value:
            paths.extend(_graph_path_values(child))
    return paths


def test_real_catalogue_has_six_exact_five_artifact_bundles() -> None:
    for layer in catalogue.LAYERS:
        output = PROJECT_ROOT / layer.output_dir
        assert output.is_dir()
        assert {entry.name for entry in output.iterdir()} == set(catalogue.REQUIRED_ARTIFACTS)

        graph = json.loads((output / "graph.json").read_text(encoding="utf-8"))
        analysis = json.loads((output / ".graphify_analysis.json").read_text(encoding="utf-8"))
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        assert graph["built_at_commit"] is None
        assert graph["graphify_provenance"] == catalogue.PROVENANCE
        assert analysis["graphify_provenance"] == catalogue.PROVENANCE
        assert isinstance(manifest, dict) and manifest

        for source_path in _graph_path_values(graph) + _graph_path_values(analysis):
            _assert_relative_catalogue_path(source_path)
        for source_path, record in manifest.items():
            _assert_relative_catalogue_path(source_path)
            assert {"mtime", "seen", "ast_hash", "semantic_hash"} <= set(record)
            assert record["ast_hash"] and record["semantic_hash"]

        report = (output / "GRAPH_REPORT.md").read_text(encoding="utf-8")
        html = (output / "graph.html").read_text(encoding="utf-8")
        generated_text = "\n".join(
            (report, html, json.dumps(graph), json.dumps(analysis), json.dumps(manifest))
        ).lower()
        assert catalogue.PROVENANCE in generated_text
        assert catalogue.REPORT_FRESHNESS in report
        assert "built from commit" not in generated_text
        assert "git rev-parse head" not in generated_text
        assert "git rev-parse HEAD" not in report
        assert "Run `manifest.json for per-file content hashes`" not in report
        assert "graphify update ." not in report
        assert "docs/graphify/" not in generated_text
        assert "data/database/" not in generated_text
        assert "data/stockfish/" not in generated_text
        assert str(PROJECT_ROOT.resolve()).replace("\\", "/").lower() not in generated_text

    core_manifest = json.loads(
        (PROJECT_ROOT / "docs/graphify/core-data/manifest.json").read_text(encoding="utf-8")
    )
    assert any(path.startswith("chess_move_trainer/") for path in core_manifest)
    assert any(path.startswith("chess_move_trainer/database/") for path in core_manifest)
    assert any(path.endswith(".sql") for path in core_manifest)


def test_stage_two_signpost_is_a_thin_bundle_index() -> None:
    readme = (PROJECT_ROOT / "docs/graphify/README.md").read_text(encoding="utf-8")
    bundles = (
        "repository",
        "backend",
        "frontend",
        "core-data",
        "tests",
        "agent-workflow",
    )
    for bundle in bundles:
        assert f"]({bundle}/GRAPH_REPORT.md)" in readme
    assert "AGENTS.md" in readme
    assert "src/tools/graphify_catalogue.py" in readme
    assert len(readme.splitlines()) <= 20


def test_stage_two_authority_and_commit_fail_closed_ordering() -> None:
    agents = (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    commit = (PROJECT_ROOT / ".opencode/commands/commit.md").read_text(encoding="utf-8")
    assert "docs/graphify/README.md" in agents
    assert "orientation, dependency tracing, ownership discovery" in agents
    assert "source code, this `AGENTS.md`, and active Plans remain authoritative" in agents
    assert "complete `src/` core/worker package" in agents
    assert "never live database" in agents
    assert commit.index("src/tools/graphify_catalogue.py") < commit.index("git status")
    assert commit.index("git status") < commit.index("git diff")
    assert commit.index("git diff") < commit.index("git add -A")
    assert commit.index("git add -A") < commit.index("git commit")
    assert "timeout 10800s" in commit
    assert "10810000" in commit
    assert "failed layer and exact command" in commit
    assert "Do not continue to repository review, staging, or committing" in commit
