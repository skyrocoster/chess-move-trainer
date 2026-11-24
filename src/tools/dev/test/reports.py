"""Persisted run reports for ``sg test``.

Every ``run`` or profile invocation writes ``build/test-results/<run-id>/`` with
a machine-readable ``summary.json`` plus the runner artifacts (pytest/Vitest
JUnit XML and the Playwright JSON report). ``sg test failures`` and
``sg test report --last`` read the newest run. Soft budgets warn; the hard
per-command deadlines remain the enforcement mechanism.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from tools.dev.config import TEST_RESULTS_DIR
from tools.dev.test.artifacts import (
    CaseOutcome,
    parse_junit,
    parse_playwright,
    trim_message,
)

RUN_ROOT = TEST_RESULTS_DIR
UNIT_WARN_SECONDS = 1.0
FOCUSED_WARN_SECONDS = 15.0
SLOW_CASE_REPORT_LIMIT = 15


@dataclass
class CommandRecord:
    """One finished runner command and everything known about its run."""

    label: str
    backend: str
    args: tuple[str, ...]
    exit_code: int
    duration_seconds: float
    timeout_seconds: float
    case_count: int = 0
    case_ids: tuple[str, ...] = ()
    timed_out: bool = False
    allow_failure: bool = False
    artifacts: dict[str, str] = field(default_factory=dict)
    outcomes: list[CaseOutcome] = field(default_factory=list)
    first_error: str = ""

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0 or self.allow_failure

    @property
    def failures(self) -> list[CaseOutcome]:
        return [outcome for outcome in self.outcomes if outcome.failed]

    def to_json(self) -> dict:
        payload = {
            "label": self.label,
            "backend": self.backend,
            "args": list(self.args),
            "exit_code": self.exit_code,
            "duration_seconds": round(self.duration_seconds, 4),
            "timeout_seconds": self.timeout_seconds,
            "case_count": self.case_count,
            "timed_out": self.timed_out,
        }
        if self.artifacts:
            payload["artifacts"] = dict(self.artifacts)
        if self.first_error:
            payload["first_error"] = self.first_error
        if self.outcomes:
            payload["outcomes"] = [outcome.to_json() for outcome in self.outcomes]
        if self.failures:
            payload["failures"] = [outcome.to_json() for outcome in self.failures]
        return payload


@dataclass
class RunReport:
    """One bounded ``sg test`` invocation, persisted on disk."""

    run_id: str
    directory: Path
    request: dict
    started_at: str
    budget_seconds: float | None = None
    records: list[CommandRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    status: str = "running"
    finished_at: str = ""
    duration_seconds: float = 0.0
    selection_seconds: float = 0.0
    soft_budget_exceeded: bool = False
    _started_monotonic: float = 0.0

    @classmethod
    def start(
        cls,
        *,
        request: dict,
        budget_seconds: float | None = None,
        selection_seconds: float = 0.0,
    ) -> "RunReport":
        slug = str(request.get("command", "run")).replace(" ", "-")
        base = time.strftime("%Y%m%d-%H%M%S") + f"-{slug}"
        directory = RUN_ROOT / base
        suffix = 2
        while directory.exists():
            directory = RUN_ROOT / f"{base}-{suffix}"
            suffix += 1
        report = cls(
            run_id=directory.name,
            directory=directory,
            request=dict(request),
            started_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            budget_seconds=budget_seconds,
            selection_seconds=selection_seconds,
        )
        directory.mkdir(parents=True)
        report._started_monotonic = time.monotonic()
        return report

    @property
    def total_seconds(self) -> float:
        return self.duration_seconds + self.selection_seconds

    def abandon(self) -> None:
        try:
            entries = list(self.directory.iterdir())
        except FileNotFoundError:
            return
        if not entries:
            self.directory.rmdir()

    def add_command(
        self,
        command,
        exit_code: int,
        duration_seconds: float,
        *,
        timed_out: bool,
        outcomes: list[CaseOutcome],
        cases: list,
        first_error: str = "",
    ) -> CommandRecord:
        for outcome in outcomes:
            resolved = resolve_case(outcome, cases)
            if resolved is not None:
                outcome.logical_id = resolved.id
                outcome.speed = resolved.speed
        record = CommandRecord(
            label=command.label,
            backend=command.backend,
            args=tuple(command.args),
            exit_code=exit_code,
            duration_seconds=duration_seconds,
            timeout_seconds=command.timeout,
            case_count=len(cases),
            case_ids=tuple(case.id for case in cases),
            timed_out=timed_out,
            allow_failure=command.allow_failure,
            artifacts=dict(command.artifacts),
            outcomes=outcomes,
            first_error=first_error,
        )
        self.records.append(record)
        return record

    def finalize(self) -> None:
        self.finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.duration_seconds = time.monotonic() - self._started_monotonic
        failed = [record for record in self.records if not record.succeeded]
        self.status = "failed" if failed else "passed"
        if self.budget_seconds is not None and self.total_seconds > self.budget_seconds:
            self.soft_budget_exceeded = True
            self.warnings.append(
                f"soft budget exceeded: {self.total_seconds:.1f}s > {self.budget_seconds:g}s"
            )
        for record in self.records:
            if record.timed_out:
                self.warnings.append(
                    f"{record.label}: exceeded its {record.timeout_seconds:g}s hard deadline"
                )
            for outcome in record.outcomes:
                warn = (
                    FOCUSED_WARN_SECONDS
                    if outcome.speed in ("focused", "slow")
                    else UNIT_WARN_SECONDS
                )
                if outcome.duration_seconds > warn:
                    self.warnings.append(
                        f"slow case ({outcome.duration_seconds:.1f}s):"
                        f" {outcome.logical_id or outcome.display}"
                    )

    def write(self) -> None:
        payload = {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "duration_seconds": round(self.duration_seconds, 4),
            "selection_seconds": round(self.selection_seconds, 4),
            "total_seconds": round(self.total_seconds, 4),
            "request": self.request,
            "soft_budget_seconds": self.budget_seconds,
            "soft_budget_exceeded": self.soft_budget_exceeded,
            "warnings": self.warnings,
            "commands": [record.to_json() for record in self.records],
        }
        (self.directory / "summary.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )


def parse_artifact(command, directory: Path) -> list[CaseOutcome]:
    """Parse whichever standard artifact one command produced."""
    if "junit" in command.artifacts:
        return parse_junit(directory / command.artifacts["junit"])
    if "playwright" in command.artifacts:
        return parse_playwright(directory / command.artifacts["playwright"])
    return []


def resolve_case(outcome: CaseOutcome, cases: list):
    """Resolve one artifact outcome to a discovered selection unit."""
    for case in cases:
        if outcome.selector and outcome.selector == case.selector:
            return case
    selector_matches = [
        case for case in cases if outcome.selector and case.selector.endswith(outcome.selector)
    ]
    if len(selector_matches) == 1:
        return selector_matches[0]
    if outcome.file:
        normalised = outcome.file.replace("\\", "/")
        for case in cases:
            if normalised == case.source or normalised.endswith("/" + case.source):
                return case
    if outcome.name:
        matches = [case for case in cases if case.selector.endswith(outcome.name)]
        if len(matches) == 1:
            return matches[0]
    sources = {case.source for case in cases}
    if len(sources) == 1:
        return cases[0]
    return None


def latest_run() -> Path | None:
    """Return the newest directory containing a summary, or ``None``."""
    if not RUN_ROOT.is_dir():
        return None
    candidates = sorted(
        (path for path in RUN_ROOT.iterdir() if (path / "summary.json").is_file()),
        key=lambda path: path.name,
    )
    return candidates[-1] if candidates else None


def load_summary(directory: Path) -> dict | None:
    try:
        return json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def rerun_command(logical_id: str) -> str:
    return f"sg test run --id {logical_id}" if logical_id else "sg test run --id <case>"


def format_report(summary: dict) -> list[str]:
    """Return the concise human summary of one run."""
    lines = [
        f"run:      {summary.get('run_id', '')}",
        f"status:   {summary.get('status', '')} in {summary.get('total_seconds', 0):.1f}s"
        f" (selection {summary.get('selection_seconds', 0):.1f}s)",
        f"request:  {_request_text(summary.get('request', {}))}",
    ]
    budget = summary.get("soft_budget_seconds")
    if budget is not None:
        lines.append(
            f"budget:   {budget:g}s"
            + (" (exceeded)" if summary.get("soft_budget_exceeded") else " (within)")
        )
    lines.append("commands:")
    for record in summary.get("commands", []):
        outcome = "pass" if record.get("exit_code") == 0 else "fail"
        if record.get("timed_out"):
            outcome = "timeout"
        lines.append(
            f"  {record.get('duration_seconds', 0):7.1f}s  {outcome:7}"
            f"  {record.get('case_count', 0):>3} unit(s)  {record.get('label', '')}"
        )
        if record.get("first_error"):
            lines.append(f"             first error: {record['first_error']}")
    warnings = summary.get("warnings", [])
    if warnings:
        lines.append("warnings:")
        lines.extend(f"  - {warning}" for warning in warnings)
    slowest = _slowest_cases(summary)
    if slowest:
        lines.append("slowest cases:")
        for outcome in slowest:
            lines.append(
                f"  {outcome.get('duration_seconds', 0):7.1f}s  "
                f"{outcome.get('logical_id') or outcome.get('display', '')}"
            )
    return lines


def format_failures(summary: dict) -> list[str]:
    """Return the newest run's failures and exact rerun commands."""
    failures = [
        outcome for record in summary.get("commands", []) for outcome in record.get("failures", [])
    ]
    if not failures:
        return [f"run: {summary.get('run_id', '')}", "No failures recorded."]
    lines = [f"run: {summary.get('run_id', '')}", f"failed: {len(failures)}"]
    for outcome in failures:
        identifier = outcome.get("logical_id") or outcome.get("display", "")
        lines.append(f"- {identifier}")
        if outcome.get("message"):
            lines.append(f"  {trim_message(str(outcome['message']))}")
        lines.append(f"  rerun: {rerun_command(outcome.get('logical_id', ''))}")
    return lines


def _slowest_cases(summary: dict) -> list[dict]:
    outcomes = [
        outcome for record in summary.get("commands", []) for outcome in record.get("outcomes", [])
    ]
    outcomes = [
        outcome for outcome in outcomes if outcome.get("duration_seconds", 0) > UNIT_WARN_SECONDS
    ]
    outcomes.sort(key=lambda outcome: outcome.get("duration_seconds", 0), reverse=True)
    return outcomes[:SLOW_CASE_REPORT_LIMIT]


def _request_text(request: dict) -> str:
    parts = [f"{key}={value}" for key, value in request.items() if value not in ("", None, False)]
    return " ".join(parts) or "run"
