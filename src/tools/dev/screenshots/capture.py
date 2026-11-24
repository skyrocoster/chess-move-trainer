"""Programmatic UI screenshot capture for human and AI review.

``capture()`` is the public entry point. It resolves targets, writes a bounded
request for the Playwright driver, runs it, and returns the manifest that
describes every PNG plus the console and network problems seen on the page.
The command never starts the development stack; callers reuse the shared
services described in ``docs/DEVELOPMENT_SERVICES.md``.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

from tools.dev.config import REPOSITORY_ROOT, SCREENSHOTS_DIR
from tools.dev.screenshots.catalog import (
    DEFAULT_BASE_URL,
    EXPECTED_HTTP_ERRORS,
    ResolvedTarget,
    Viewport,
    normalize_base_url,
    parse_viewports,
    resolve_targets,
)


class ScreenshotError(RuntimeError):
    """A screenshot run could not be prepared or completed."""


@dataclass(frozen=True)
class CaptureRun:
    """The result of one screenshot run."""

    directory: Path
    manifest_path: Path
    manifest: dict

    @property
    def screenshots(self) -> list[dict]:
        """Return one entry per requested target and viewport."""
        return self.manifest.get("screenshots", [])

    @property
    def summary(self) -> dict:
        """Return the aggregate counts for the run."""
        return self.manifest.get("summary", {})

    @property
    def ok(self) -> bool:
        """Return whether every requested screenshot was written."""
        return self.summary.get("failed", 0) == 0


def capture(
    targets: list[str] | tuple[str, ...] | str | None = None,
    *,
    base_url: str = DEFAULT_BASE_URL,
    all_targets: bool = False,
    output_dir: str | Path | None = None,
    viewports: list[str] | tuple[str, ...] | str | None = None,
    full_page: bool = False,
    wait_for: str = "",
    wait_ms: int = 250,
    timeout_ms: int = 30_000,
    selector: str = "",
    check_reachable: bool = True,
    on_start: Callable[[], None] | None = None,
) -> CaptureRun:
    """Capture screenshots and return the manifest describing them.

    Args:
        targets: Named targets, ``/routes``, ``http(s)`` URLs, or
            ``label=/route`` entries. Defaults to the home page.
        base_url: Origin used for named and ``/route`` targets.
        all_targets: Capture every named target instead of explicit values.
        output_dir: Destination directory. Defaults to a timestamped directory
            under ``build/screenshots``.
        viewports: Preset names or ``WIDTHxHEIGHT`` values; comma-separated and
            repeated values are accepted.
        full_page: Capture the whole scrollable page instead of the visible
            viewport. The viewport default keeps long list pages reviewable.
        wait_for: Optional CSS selector to wait for after navigation.
        wait_ms: Extra settle time after the page becomes idle.
        timeout_ms: Navigation, selector and screenshot timeout per capture.
        selector: Capture only the first element matching this CSS selector.
        check_reachable: Probe each target origin first and fail with service
            guidance instead of a browser navigation error.
        on_start: Optional callback invoked after validation and just before the
            browser starts. Useful for CLI progress messages.
    """
    if wait_ms < 0:
        raise ValueError("wait_ms must be non-negative.")
    if wait_ms > 60_000:
        raise ValueError("wait_ms must be at most 60000.")
    if not 1_000 <= timeout_ms <= 120_000:
        raise ValueError("timeout_ms must be between 1000 and 120000.")
    base = normalize_base_url(base_url)
    viewport_list = parse_viewports(viewports)
    resolved = resolve_targets(targets or (), base_url=base, all_targets=all_targets)

    if check_reachable:
        _require_reachable(target.url for target in resolved)
    resolved, skipped = _resolve_ids(resolved)

    directory = _run_directory(output_dir)
    jobs = _jobs(
        resolved,
        viewport_list,
        directory=directory,
        full_page=full_page,
        wait_for=wait_for,
        wait_ms=wait_ms,
        timeout_ms=timeout_ms,
        selector=selector,
    )
    request = {
        "version": 1,
        "run_id": directory.name,
        "base_url": base,
        "repository_root": str(REPOSITORY_ROOT),
        "output_dir": str(directory),
        "relative_output_dir": _relative(directory),
        "viewports": [
            {"name": viewport.name, "width": viewport.width, "height": viewport.height}
            for viewport in viewport_list
        ],
        "full_page": full_page,
        "wait_for": wait_for,
        "wait_ms": wait_ms,
        "timeout_ms": timeout_ms,
        "selector": selector,
        "expected_http_errors": [rule.to_dict() for rule in EXPECTED_HTTP_ERRORS],
        "skipped": skipped,
        "jobs": jobs,
    }
    request_path = directory / "request.json"
    try:
        request_path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
    except OSError as error:
        raise ScreenshotError(
            f"Could not write the screenshot request at {request_path}: {error}"
        ) from error

    driver = Path(__file__).with_name("driver.mjs")
    if not driver.is_file():
        raise ScreenshotError(f"The Playwright driver is missing at {driver}.")
    node = shutil.which("node")
    if node is None:
        raise ScreenshotError(
            "Node.js is required for screenshots. Install Node 24 and run `npm ci`"
            " in the repository root."
        )

    if on_start is not None:
        on_start()
    _run_driver(
        [node, str(driver), str(request_path)],
        timeout=_driver_timeout(len(jobs), timeout_ms=timeout_ms, wait_ms=wait_ms),
    )

    manifest_path = directory / "manifest.json"
    manifest = _read_manifest(manifest_path)
    return CaptureRun(directory=directory, manifest_path=manifest_path, manifest=manifest)


def _resolve_ids(
    targets: list[ResolvedTarget],
) -> tuple[list[ResolvedTarget], list[dict]]:
    """Fill ``{id}`` placeholders with one read-only GET per API URL per run.

    Returns the targets that can be captured and a ``skipped`` list for targets
    whose list endpoint is empty or whose ``requires`` gate is not met (campaign
    data can legitimately be small or empty). An
    HTTP error or an unusable response raises a named ``ScreenshotError``.
    """
    cache: dict[str, list] = {}
    ready: list[ResolvedTarget] = []
    skipped: list[dict] = []
    for target in targets:
        lookup = target.resolve
        gate = target.requires
        if gate is not None:
            gate_url = f"{_origin(target.url)}{gate.api}"
            if gate_url not in cache:
                cache[gate_url] = _fetch_list(gate_url, target.name)
            if len(cache[gate_url]) < gate.minimum:
                skipped.append(
                    {
                        "name": target.name,
                        "reason": (
                            f"{gate.api} has {len(cache[gate_url])} entries;"
                            f" needs at least {gate.minimum}"
                        ),
                    }
                )
                continue
        if lookup is None:
            ready.append(target)
            continue
        api_url = f"{_origin(target.url)}{lookup.api}"
        if api_url not in cache:
            cache[api_url] = _fetch_list(api_url, target.name)
        items = cache[api_url]
        chosen = _pick(items, lookup.match)
        if chosen is None:
            reason = (
                f"{lookup.api} returned no entries"
                if not items
                else f"no entry in {lookup.api} matches {lookup.match!r}"
            )
            skipped.append({"name": target.name, "reason": reason})
            continue
        ready.append(replace(target, url=target.url.replace("{id}", str(chosen["id"]))))
    return ready, skipped


def _pick(items: list, match: str) -> dict | None:
    needle = match.casefold()
    for item in items:
        label = str(item.get("name") or item.get("title") or "")
        if not needle or needle in label.casefold():
            return item
    return None


def _fetch_list(api_url: str, target_name: str) -> list[dict]:
    """GET a list endpoint and validate that every item has an integer id."""
    request = urllib.request.Request(
        api_url, headers={"User-Agent": "sg-screenshot/1"}, method="GET"
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        error.close()
        raise ScreenshotError(
            f"Target {target_name!r}: GET {api_url} failed with HTTP {error.code}."
        ) from error
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
        raise ScreenshotError(
            f"Target {target_name!r}: GET {api_url} failed ({getattr(error, 'reason', error)})."
        ) from error
    if not isinstance(payload, list) or not all(
        isinstance(item, dict) and isinstance(item.get("id"), int) for item in payload
    ):
        raise ScreenshotError(
            f"Target {target_name!r}: GET {api_url} did not return a list of entries with ids."
        )
    return payload


def _run_directory(output_dir: str | Path | None) -> Path:
    if output_dir is not None:
        directory = Path(output_dir).expanduser()
        if not directory.is_absolute():
            directory = REPOSITORY_ROOT / directory
        _ensure_directory(directory)
        return directory
    _ensure_directory(SCREENSHOTS_DIR)
    run_id = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    directory = SCREENSHOTS_DIR / run_id
    suffix = 2
    while directory.exists():
        directory = SCREENSHOTS_DIR / f"{run_id}-{suffix}"
        suffix += 1
    _ensure_directory(directory)
    return directory


def _ensure_directory(directory: Path) -> None:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise ScreenshotError(
            f"Could not create the screenshot directory {directory}: {error}"
        ) from error


def _jobs(
    targets: list[ResolvedTarget],
    viewports: list[Viewport],
    *,
    directory: Path,
    full_page: bool,
    wait_for: str,
    wait_ms: int,
    timeout_ms: int,
    selector: str,
) -> list[dict]:
    jobs: list[dict] = []
    for target in targets:
        for viewport in viewports:
            suffix = "" if len(viewports) == 1 else f"--{viewport.name}"
            path = directory / f"{target.name}{suffix}.png"
            jobs.append(
                {
                    "name": target.name,
                    "url": target.url,
                    "description": target.description,
                    "file": str(path),
                    "relative_file": _relative(path),
                    "viewport": {
                        "name": viewport.name,
                        "width": viewport.width,
                        "height": viewport.height,
                    },
                    "full_page": bool(full_page and not selector),
                    "wait_for": wait_for,
                    "wait_ms": wait_ms,
                    "timeout_ms": timeout_ms,
                    "selector": selector,
                    "actions": [action.to_dict() for action in target.actions],
                    "expects_writes": target.expects_writes,
                }
            )
    return jobs


def _driver_timeout(job_count: int, *, timeout_ms: int, wait_ms: int) -> float:
    """Return a finite deadline that covers every job plus browser startup."""
    per_job = timeout_ms / 1000 + wait_ms / 1000 + 20.0
    return min(1_800.0, max(60.0, job_count * per_job + 30.0))


def _run_driver(command: list[str], *, timeout: float) -> None:
    if timeout <= 0:
        raise ValueError("screenshot driver timeout must be finite and positive")
    creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    try:
        process = subprocess.Popen(
            command,
            cwd=str(REPOSITORY_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creation_flags,
            start_new_session=os.name != "nt",
        )
    except OSError as error:
        raise ScreenshotError(f"Could not start the screenshot driver: {error}") from error
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as error:
        _terminate(process)
        raise ScreenshotError(
            f"Screenshot capture exceeded its {timeout:g}s hard deadline. The browser"
            " process tree was terminated."
        ) from error
    if process.returncode != 0:
        detail = (stderr or stdout).strip()
        hint = ""
        if "Executable doesn't exist" in detail and "playwright install" not in detail.lower():
            hint = " Run `npx playwright install chromium` once on this machine."
        raise ScreenshotError(
            f"Screenshot capture failed (exit {process.returncode}). {_tail(detail)}{hint}"
        )


def _terminate(process: subprocess.Popen) -> None:
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                capture_output=True,
                timeout=60,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
    else:
        try:
            os.killpg(os.getpgid(process.pid), 9)
        except OSError:
            pass
    try:
        process.kill()
    except OSError:
        pass
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        pass


def _read_manifest(path: Path) -> dict:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ScreenshotError(
            f"The screenshot driver did not write a manifest at {path}."
        ) from error
    except (OSError, json.JSONDecodeError) as error:
        raise ScreenshotError(
            f"Could not read the screenshot manifest at {path}: {error}"
        ) from error
    if not isinstance(manifest, dict) or manifest.get("version") != 1:
        raise ScreenshotError(f"Unsupported screenshot manifest at {path}.")
    if not isinstance(manifest.get("screenshots"), list):
        raise ScreenshotError(f"The screenshot manifest at {path} has no screenshot entries.")
    if not isinstance(manifest.get("summary"), dict):
        raise ScreenshotError(f"The screenshot manifest at {path} has no summary.")
    return manifest


def _require_reachable(urls) -> None:
    origins = sorted({_origin(url) for url in urls})
    for origin in origins:
        request = urllib.request.Request(
            origin,
            headers={"User-Agent": "sg-screenshot/1"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                response.read(1)
        except urllib.error.HTTPError as error:
            # Any HTTP answer proves the server is listening.
            error.close()
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            reason = getattr(error, "reason", error)
            raise ScreenshotError(
                f"The UI at {origin} is not reachable ({reason}). Start the shared"
                " services with `uv run --no-sync sg dev start`, or pass a reachable"
                " --base-url or URL."
            ) from error


def _origin(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"Screenshot URL must be http(s): {url!r}")
    return f"{parsed.scheme}://{parsed.netloc}"


def _relative(path: Path) -> str:
    try:
        return path.relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _tail(text: str, limit: int = 1_500) -> str:
    collapsed = " ".join((text or "").split())
    if len(collapsed) <= limit:
        return collapsed
    return "…" + collapsed[-limit:]
