from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE_ROOTS = (
    ROOT / "AGENTS.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "PLAN_TEMPLATE.md",
    ROOT / "docs" / "MASTER_PLAN_TEMPLATE.md",
    ROOT / ".opencode",
    ROOT / "scripts" / "check.py",
    ROOT / "scripts" / "check_size.py",
    ROOT / "experiments",
)
LEGACY_REFERENCES = tuple(
    "".join(parts)
    for parts in (
        ("check", "_docs.py"),
        ("check", "_orders.py"),
        ("new", "_order.py"),
        ("order", "_check.py"),
        ("stage", "_check.py"),
        ("force", "-ship-stage"),
        ("coordinator", "-order-author"),
        ("implement", "-order"),
        ("implement", "-quick"),
        ("validate", "-order"),
        ("validate", "-stage"),
        ("validate", "-plan"),
        ("correct", "-order"),
        ("coordinator", "-validator"),
        ("deliver", "-direct"),
        ("write-focused", "-plan"),
        ("plan", "-stage"),
        ("scout", "-case"),
    )
)


def text_files(root: Path):
    if root.is_file():
        yield root
        return
    skipped = {".git", ".venv", "node_modules", "__pycache__", "dist", "build"}
    for path in root.rglob("*"):
        if any(part in skipped for part in path.parts):
            continue
        if path.is_file() and path.suffix in {".md", ".py", ".json", ".ts", ".tsx"}:
            yield path


def test_live_workflow_has_no_legacy_references() -> None:
    test_path = Path(__file__).resolve()
    findings = []
    for root in LIVE_ROOTS:
        for path in text_files(root):
            if path == test_path:
                continue
            text = path.read_text(encoding="utf-8")
            for term in LEGACY_REFERENCES:
                if term in text:
                    findings.append(f"{path.relative_to(ROOT)} contains {term}")
    assert findings == []
