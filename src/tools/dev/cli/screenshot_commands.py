"""The ``sg screenshot`` command for UI review captures."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from tools.dev.console import echo, fail
from tools.dev.screenshots import CaptureRun, ScreenshotError, capture
from tools.dev.screenshots.catalog import (
    DEFAULT_BASE_URL,
    TARGETS,
    VIEWPORT_GROUPS,
    VIEWPORTS,
)


def screenshot_command(
    targets: list[str] | None = typer.Argument(
        None,
        help=(
            "Named target, /route, http(s) URL, or label=/route. With no values,"
            " captures the home page."
        ),
    ),
    all_targets: bool = typer.Option(
        False,
        "--all",
        help="Capture every named application target.",
    ),
    list_targets: bool = typer.Option(
        False,
        "--list",
        help="List named targets and viewports without capturing.",
    ),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL,
        "--base-url",
        help="Origin used for named targets and /routes.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        help="Output directory. Defaults to a timestamped build/screenshots/<run-id>.",
    ),
    viewport: list[str] = typer.Option(
        ["desktop"],
        "--viewport",
        help=("Preset, group (review) or WIDTHxHEIGHT; repeat or separate values with commas."),
    ),
    full_page: bool = typer.Option(
        False,
        "--full-page/--viewport-only",
        help="Capture the whole scrollable page instead of only the viewport.",
    ),
    wait_for: str = typer.Option(
        "",
        "--wait-for",
        help="Visible CSS selector to wait for before each capture.",
    ),
    wait_ms: int = typer.Option(
        250,
        "--wait-ms",
        help="Extra settle time in milliseconds after the page becomes idle.",
    ),
    timeout_ms: int = typer.Option(
        30_000,
        "--timeout-ms",
        help="Per-capture navigation, selector and screenshot timeout.",
    ),
    selector: str = typer.Option(
        "",
        "--selector",
        help="Capture only the first visible element matching this CSS selector.",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help=(
            "Exit non-zero when pages log console, page or network/HTTP errors, or attempt"
            " a blocked write the target does not expect."
        ),
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Print the manifest JSON only (for other tools and agents).",
    ),
) -> None:
    """Capture screenshots plus a manifest of console and network problems."""
    if list_targets:
        _list_targets(json_output=json_output)
        return

    def announce_progress() -> None:
        echo("Capturing screenshots with Playwright Chromium...", err=True)

    try:
        run = capture(
            targets or (),
            base_url=base_url,
            all_targets=all_targets,
            output_dir=output,
            viewports=viewport,
            full_page=full_page,
            wait_for=wait_for,
            wait_ms=wait_ms,
            timeout_ms=timeout_ms,
            selector=selector,
            on_start=None if json_output else announce_progress,
        )
    except (ScreenshotError, ValueError) as error:
        fail(str(error))

    if json_output:
        echo(json.dumps(run.manifest, indent=2))
    else:
        _print_run(run)

    failed = run.summary.get("failed", 0)
    if failed:
        fail(
            f"{failed} screenshot(s) failed. Inspect {run.manifest_path} and the errors above.",
            code=1,
        )
    if strict:
        issues = _strict_issues(run.summary)
        if issues:
            fail(
                "Strict screenshot check failed: "
                + ", ".join(f"{count} {label}" for label, count in issues)
                + f". Inspect {run.manifest_path}.",
                code=1,
            )


def _list_targets(*, json_output: bool) -> None:
    if json_output:
        echo(
            json.dumps(
                {
                    "targets": [
                        {
                            "name": target.name,
                            "path": target.path,
                            "description": target.description,
                            "actions": [action.to_dict() for action in target.actions],
                        }
                        for target in TARGETS.values()
                    ],
                    "viewport_groups": {
                        name: list(members) for name, members in VIEWPORT_GROUPS.items()
                    },
                    "viewports": [
                        {
                            "name": viewport.name,
                            "width": viewport.width,
                            "height": viewport.height,
                        }
                        for viewport in VIEWPORTS.values()
                    ],
                },
                indent=2,
            )
        )
        return
    width = max(len(target.name) for target in TARGETS.values())
    for target in TARGETS.values():
        steps = f" [{len(target.actions)} action(s)]" if target.actions else ""
        echo(f"  {target.name:<{width}}  {target.path:<16} {target.description}{steps}")
    echo(
        "Viewports: "
        + ", ".join(
            f"{viewport.name} {viewport.width}x{viewport.height}" for viewport in VIEWPORTS.values()
        )
    )
    echo(
        "Viewport groups: "
        + ", ".join(f"{name} = {', '.join(members)}" for name, members in VIEWPORT_GROUPS.items())
    )


def _print_run(run: CaptureRun) -> None:
    summary = run.summary
    seconds = (run.manifest.get("duration_ms", 0) or 0) / 1000
    echo(
        f"Captured {summary.get('captured', 0)}/{summary.get('requested', 0)}"
        f" screenshot(s) in {seconds:.1f}s"
    )
    for screenshot in run.screenshots:
        status = "FAILED" if screenshot.get("error") else "ok"
        line = (
            f"  {status:<6} {screenshot.get('name', '')} @"
            f" {screenshot.get('viewport', '')}  {screenshot.get('relative_file', '')}"
        )
        if not screenshot.get("error") and screenshot.get("width") and screenshot.get("height"):
            line += f"  {screenshot['width']}x{screenshot['height']}"
        echo(line)
        if screenshot.get("error"):
            echo(f"         {screenshot['error']}", err=True)
        for write in screenshot.get("blocked_writes", []):
            echo(f"         blocked {write.get('method')} {write.get('url')}")
    issues = _issues(summary)
    echo(
        "Issues: "
        + (", ".join(f"{count} {label}" for label, count in issues) if issues else "none")
    )
    expected_http = int(summary.get("expected_http_errors", 0) or 0)
    expected_console = int(summary.get("expected_console_errors", 0) or 0)
    if expected_http or expected_console:
        echo(
            "Expected optional-state 404s: "
            f"{expected_http} response(s), {expected_console} console log(s)"
        )
    for skipped in run.manifest.get("skipped", []):
        echo(f"  SKIPPED {skipped.get('name', '')}: {skipped.get('reason', '')}")
    if summary.get("blocked_writes"):
        echo(f"Blocked writes (read-only guard): {summary['blocked_writes']}")
    echo(f"Manifest: {run.manifest_path}")


def _issues(summary: dict) -> list[tuple[str, int]]:
    labels = (
        ("console_errors", "console error(s)"),
        ("page_errors", "page error(s)"),
        ("failed_requests", "failed request(s)"),
        ("http_errors", "HTTP error(s)"),
    )
    issues = [(label, int(summary.get(key, 0) or 0)) for key, label in labels if summary.get(key)]
    return issues


def _strict_issues(summary: dict) -> list[tuple[str, int]]:
    issues = _issues(summary)
    unexpected = int(summary.get("unexpected_blocked_writes", 0) or 0)
    if unexpected:
        issues.append(("unexpected blocked write(s)", unexpected))
    return issues
