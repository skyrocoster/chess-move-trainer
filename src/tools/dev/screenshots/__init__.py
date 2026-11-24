"""Screenshot capture for UI review, available to the CLI and Python callers."""

from __future__ import annotations

from tools.dev.screenshots.capture import CaptureRun, ScreenshotError, capture
from tools.dev.screenshots.catalog import (
    DEFAULT_BASE_URL,
    TARGETS,
    VIEWPORT_GROUPS,
    VIEWPORTS,
    Action,
    CatalogTarget,
    Locator,
    ResolvedTarget,
    Viewport,
    normalize_base_url,
    parse_viewport,
    parse_viewports,
    resolve_targets,
)

__all__ = [
    "DEFAULT_BASE_URL",
    "TARGETS",
    "VIEWPORT_GROUPS",
    "VIEWPORTS",
    "Action",
    "CaptureRun",
    "CatalogTarget",
    "Locator",
    "ResolvedTarget",
    "ScreenshotError",
    "Viewport",
    "capture",
    "normalize_base_url",
    "parse_viewport",
    "parse_viewports",
    "resolve_targets",
]
