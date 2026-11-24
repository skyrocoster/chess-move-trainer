"""Parse bounded runner artifacts into per-case outcomes."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CaseOutcome:
    """One case result read from a runner's artifact."""

    display: str
    name: str
    file: str = ""
    selector: str = ""
    failed: bool = False
    skipped: bool = False
    message: str = ""
    duration_seconds: float = 0.0
    logical_id: str = ""
    speed: str = ""

    def to_json(self) -> dict:
        payload = {
            "display": self.display,
            "name": self.name,
            "failed": self.failed,
            "skipped": self.skipped,
            "duration_seconds": round(self.duration_seconds, 4),
        }
        for key in ("file", "selector", "message", "logical_id", "speed"):
            value = getattr(self, key)
            if value:
                payload[key] = value
        return payload


def parse_junit(path: Path) -> list[CaseOutcome]:
    """Return outcomes from a JUnit XML artifact, tolerating partial files."""
    try:
        root = ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError):
        return []
    outcomes: list[CaseOutcome] = []
    for testcase in root.iter("testcase"):
        name = testcase.get("name", "")
        classname = testcase.get("classname", "")
        failure = testcase.find("failure")
        if failure is None:
            failure = testcase.find("error")
        skipped = testcase.find("skipped") is not None
        message = ""
        if failure is not None:
            message = failure.get("message") or (failure.text or "")
        outcomes.append(
            CaseOutcome(
                display=f"{classname} > {name}" if classname else name,
                name=name,
                file=testcase.get("file") or classname,
                selector=name,
                failed=failure is not None,
                skipped=skipped,
                message=trim_message(message),
                duration_seconds=_seconds(testcase.get("time")),
            )
        )
    return outcomes


def parse_playwright(path: Path) -> list[CaseOutcome]:
    """Return outcomes from the Playwright JSON reporter artifact."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    outcomes: list[CaseOutcome] = []
    for suite in payload.get("suites", []):
        _walk_playwright_suite(suite, outcomes)
    return outcomes


def _walk_playwright_suite(suite: dict, outcomes: list[CaseOutcome]) -> None:
    for spec in suite.get("specs", []):
        results = [result for test in spec.get("tests", []) for result in test.get("results", [])]
        statuses = {result.get("status") for result in results}
        failed = spec.get("ok") is False or bool(statuses & {"failed", "timedOut", "interrupted"})
        skipped = bool(results) and statuses <= {"skipped"}
        message = ""
        for result in results:
            errors = result.get("errors") or []
            if errors:
                message = errors[0].get("message", "")
                break
        file = spec.get("file", "")
        line = spec.get("line", 0)
        outcomes.append(
            CaseOutcome(
                display=spec.get("title", ""),
                name=spec.get("title", ""),
                file=file,
                selector=f"tests/e2e/{file}:{line}",
                failed=failed,
                skipped=skipped,
                message=trim_message(message),
                duration_seconds=sum(result.get("duration", 0) for result in results) / 1000.0,
            )
        )
    for child in suite.get("suites", []):
        _walk_playwright_suite(child, outcomes)


def trim_message(message: str, limit: int = 500) -> str:
    """Return the first actionable line of a failure message."""
    collapsed = re.sub(r"\s+", " ", message or "").strip()
    return collapsed if len(collapsed) <= limit else collapsed[: limit - 1] + "…"


def _seconds(value: str | None) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0
