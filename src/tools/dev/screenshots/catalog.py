"""Named screenshot targets and viewport presets for ``sg screenshot``.

The target list is the small, stable surface a reviewer needs: the public app
routes that render without a known database id. Arbitrary routes and full URLs
are accepted by :func:`resolve_targets`, so this mapping never has to mirror
the router exhaustively.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from urllib.parse import urlparse

DEFAULT_BASE_URL = "http://127.0.0.1:8444"

_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")
_SIZE_PATTERN = re.compile(r"(\d{2,5})x(\d{2,5})")


ACTION_KINDS = ("fill", "click", "press", "wait_for", "scroll")

# Captures must never commit anything. A click whose name starts with one of
# these words is rejected when the catalog is imported.
_COMMIT_WORDS = re.compile(
    r"^\s*(create|save|done|delete|remove|submit|confirm|update|apply|import(?!\s*/\s*export\b)|publish)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Locator:
    """Semantic address of one element, matching how Playwright tests find things.

    Exactly one of ``role`` (optionally with an accessible ``name``), ``label``,
    ``text`` or ``css`` is set. ``css`` is an escape hatch for elements with no
    accessible role, label or text. Matching is exact (``exact=False`` allows a
    substring) and must be unique unless ``nth`` picks one match (zero-based).
    """

    role: str = ""
    name: str = ""
    label: str = ""
    text: str = ""
    css: str = ""
    exact: bool = True
    nth: int | None = None

    def __post_init__(self) -> None:
        chosen = [key for key in ("role", "label", "text", "css") if getattr(self, key)]
        if len(chosen) != 1:
            raise ValueError(
                "A locator needs exactly one of role, label, text or css; got "
                f"{', '.join(chosen) or 'none'}."
            )
        if self.name and not self.role:
            raise ValueError("A locator name is only valid together with a role.")
        if self.nth is not None and self.nth < 0:
            raise ValueError("A locator nth is zero-based and must not be negative.")

    def to_dict(self) -> dict:
        """Return the non-default fields for ``request.json``."""
        data: dict = {key: getattr(self, key) for key in ("role", "name", "label", "text", "css")}
        data = {key: value for key, value in data.items() if value}
        if not self.exact:
            data["exact"] = False
        if self.nth is not None:
            data["nth"] = self.nth
        return data


@dataclass(frozen=True)
class Action:
    """One declarative step run on the page before the screenshot.

    ``fill`` needs a target and ``text``; ``click``, ``wait_for`` and ``scroll`` (brings
    the element to the top of its scrolling area, changing nothing) need a target;
    ``press`` needs a ``key`` (a Playwright key name such as ``Enter``).
    """

    kind: str
    target: Locator | None = None
    text: str = ""
    key: str = ""
    optional: bool = False  # click only: skipped when the target is not visible (layout differs)

    def __post_init__(self) -> None:
        if self.kind not in ACTION_KINDS:
            raise ValueError(
                f"Unknown action kind {self.kind!r}. Use one of: {', '.join(ACTION_KINDS)}."
            )
        if self.optional and self.kind != "click":
            raise ValueError("Only a click action can be optional.")
        if self.kind == "press":
            if not self.key or self.target is not None or self.text:
                raise ValueError("A press action needs only a key.")
            return
        if self.target is None:
            raise ValueError(f"A {self.kind} action needs a target.")
        if self.key:
            raise ValueError(f"A {self.kind} action does not take a key.")
        if self.kind != "fill" and self.text:
            raise ValueError(f"A {self.kind} action does not take text.")
        if self.kind == "click":
            label = self.target.name or self.target.text or self.target.label
            if _COMMIT_WORDS.match(label) or (
                self.target.css
                and re.search(r"create|save|done|delete|submit", self.target.css, re.IGNORECASE)
            ):
                raise ValueError(
                    f"A click on {label or self.target.css!r} looks like a commit action;"
                    " screenshot actions must not save, create or delete."
                )

    def to_dict(self) -> dict:
        """Return the JSON form read by ``driver.mjs``."""
        data: dict = {"kind": self.kind}
        if self.target is not None:
            data["target"] = self.target.to_dict()
        if self.kind == "fill":
            data["text"] = self.text
        if self.kind == "press":
            data["key"] = self.key
        if self.optional:
            data["optional"] = True
        return data


@dataclass(frozen=True)
class ResolveId:
    """A read-only lookup that fills the ``{id}`` placeholder in a target path.

    ``api`` is a GET-able list endpoint on the capture origin (for example
    ``/api/games``). The first item is used, or the first whose ``name`` or
    ``title`` contains ``match``. An empty list skips the target.
    """

    api: str
    match: str = ""

    def __post_init__(self) -> None:
        if not self.api.startswith("/api/") or "?" in self.api:
            raise ValueError(f"ResolveId api {self.api!r} must be a /api/... path.")


@dataclass(frozen=True)
class Requires:
    """A data gate: the target is skipped unless ``api`` lists enough entries.

    Read-only GET, shared with ``ResolveId`` lookups through the per-run cache.
    """

    api: str
    minimum: int = 1

    def __post_init__(self) -> None:
        if not self.api.startswith("/api/") or "?" in self.api:
            raise ValueError(f"Requires api {self.api!r} must be a /api/... path.")
        if self.minimum < 1:
            raise ValueError("Requires minimum must be at least 1.")


@dataclass(frozen=True)
class CatalogTarget:
    """One named application route, optionally with UI actions to reach a state."""

    name: str
    path: str
    description: str = ""
    actions: tuple[Action, ...] = ()
    expects_writes: bool = False  # page load legitimately attempts a (blocked) write
    resolve: ResolveId | None = None  # looks up the real id for ``{id}`` in ``path``
    requires: Requires | None = None  # skip the target when the data is not there

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", self.name):
            raise ValueError(f"Catalog target name {self.name!r} must be a lowercase slug.")
        if not self.path.startswith("/"):
            raise ValueError(f"Catalog target {self.name!r} path must start with '/'.")
        if not isinstance(self.actions, tuple) or not all(
            isinstance(action, Action) for action in self.actions
        ):
            raise ValueError(f"Catalog target {self.name!r} actions must be a tuple of Action.")
        if (self.resolve is not None) != ("{id}" in self.path):
            raise ValueError(
                f"Catalog target {self.name!r} needs both a resolve lookup and an {{id}}"
                " placeholder."
            )


@dataclass(frozen=True)
class ExpectedHttpError:
    """A response the application contract treats as an empty state, not a failure.

    ``--strict`` fails on console and HTTP errors. A request for an optional record
    can legitimately answer 404 and be rendered as empty, but Chromium still logs
    the failed resource. These narrow rules are recorded separately in the manifest.
    """

    method: str
    path_pattern: str
    status: int
    reason: str

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "path": self.path_pattern,
            "status": self.status,
            "reason": self.reason,
        }


# No route in this app answers a read with an expected 404 yet, so nothing is exempt.
EXPECTED_HTTP_ERRORS: tuple[ExpectedHttpError, ...] = ()


@dataclass(frozen=True)
class ResolvedTarget:
    """A target with the URL it will be captured at."""

    name: str
    url: str
    description: str = ""
    actions: tuple[Action, ...] = ()
    expects_writes: bool = False
    resolve: ResolveId | None = None
    requires: Requires | None = None


@dataclass(frozen=True)
class Viewport:
    """A named browser viewport."""

    name: str
    width: int
    height: int



def _heading(selector: str) -> tuple[Action, ...]:
    """Wait until a page's main heading is visible so a capture never shows a loading state."""
    return (Action("wait_for", Locator(css=selector)),)


# Keep this order for ``sg screenshot --all`` and for the target listing.
TARGETS: dict[str, CatalogTarget] = {
    target.name: target
    for target in (
        CatalogTarget("home", "/", "Status page.", _heading("#status-heading")),
        CatalogTarget(
            "repertoire", "/repertoire", "Repertoire Builder.", _heading("h1")
        ),
        CatalogTarget(
            "trainer", "/trainer", "Trainer Practice.", _heading("#trainer-practice-heading")
        ),
        CatalogTarget("analysis", "/analysis", "Analysis overview.", _heading("#analysis-overview-heading")),
        CatalogTarget(
            "not-found",
            "/this-route-does-not-exist",
            "Page-not-found view for an unmatched route.",
            _heading("h1"),
        ),
    )
}

# Router paths (as written in frontend/src/App.tsx) that have no catalog target.
# A test fails when a route has neither a target nor an entry here, and when an
# entry here names a route that no longer exists.
ROUTE_EXEMPTIONS: dict[str, str] = {
    "*": "Wildcard; the not-found target captures an unmatched path.",
}

VIEWPORTS: dict[str, Viewport] = {
    viewport.name: viewport
    for viewport in (
        Viewport("desktop", 1440, 900),
        Viewport("wide", 1920, 1080),
        Viewport("laptop", 1280, 800),
        Viewport("tablet", 820, 1180),
        Viewport("mobile", 390, 844),
        Viewport("surface", 1368, 912),
        Viewport("surface-portrait", 912, 1368),
    )
}

# Named sets of viewports, expanded wherever viewports are parsed. ``review`` is
# the size set required by docs/design-system.md.
VIEWPORT_GROUPS: dict[str, tuple[str, ...]] = {
    "review": ("surface", "surface-portrait", "mobile"),
}


def normalize_base_url(value: str) -> str:
    """Return a base URL with a scheme and without a trailing slash."""
    candidate = (value or "").strip() or DEFAULT_BASE_URL
    if "://" not in candidate:
        candidate = f"http://{candidate}"
    parsed = urlparse(candidate)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(
            f"Invalid base URL {value!r}. Use an http(s) URL such as {DEFAULT_BASE_URL}."
        )
    if parsed.query or parsed.fragment:
        raise ValueError("The base URL must not include a query string or fragment.")
    return candidate.rstrip("/")


def parse_viewport(value: str) -> Viewport:
    """Parse a viewport preset or an explicit ``WIDTHxHEIGHT`` value."""
    candidate = (value or "").strip().lower()
    preset = VIEWPORTS.get(candidate)
    if preset is not None:
        return preset
    match = _SIZE_PATTERN.fullmatch(candidate)
    if not match:
        names = ", ".join([*VIEWPORTS, *VIEWPORT_GROUPS])
        raise ValueError(
            f"Unknown viewport {value!r}. Use a preset or group ({names}) or WIDTHxHEIGHT,"
            " for example 1280x800."
        )
    width, height = (int(part) for part in match.groups())
    if not (200 <= width <= 10_000 and 200 <= height <= 10_000):
        raise ValueError("Viewport dimensions must be between 200 and 10000 pixels.")
    return Viewport(f"{width}x{height}", width, height)


def parse_viewports(values: list[str] | tuple[str, ...] | str | None) -> list[Viewport]:
    """Parse comma-separated and repeated viewport values, keeping unique sizes."""
    if isinstance(values, str):
        values = [values]
    parsed: list[Viewport] = []
    seen: set[tuple[int, int]] = set()
    for value in values or ("desktop",):
        for part in str(value).split(","):
            if not part.strip():
                continue
            group = VIEWPORT_GROUPS.get(part.strip().lower())
            members = [VIEWPORTS[name] for name in group] if group else [parse_viewport(part)]
            for viewport in members:
                key = (viewport.width, viewport.height)
                if key in seen:
                    continue
                seen.add(key)
                parsed.append(viewport)
    if not parsed:
        raise ValueError("At least one viewport is required.")
    return parsed


def resolve_targets(
    values: list[str] | tuple[str, ...] | str | None,
    *,
    base_url: str = DEFAULT_BASE_URL,
    all_targets: bool = False,
) -> list[ResolvedTarget]:
    """Resolve names, routes, URLs and ``label=value`` entries to capture targets.

    ``--all`` selects every named target and cannot be combined with explicit
    values. With no values the home page is captured. Repeated URLs are
    ignored; different URLs that produce the same label are numbered so their
    screenshot files never collide.
    """
    base = normalize_base_url(base_url)
    if isinstance(values, str):
        values = [values]
    requested = [value for value in (values or ()) if value]
    if all_targets and requested:
        raise ValueError("Use --all or explicit targets, not both.")
    if all_targets:
        candidates = [_from_catalog(target, base) for target in TARGETS.values()]
    elif not requested:
        home = TARGETS["home"]
        candidates = [_from_catalog(home, base)]
    else:
        candidates = [_resolve_one(value, base) for value in requested]

    # Two states of one route differ by their actions; only exact repeats collapse.
    deduplicated: list[ResolvedTarget] = []
    seen_keys: set[tuple[str, tuple[Action, ...]]] = set()
    for target in candidates:
        key = (target.url, target.actions)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduplicated.append(target)

    resolved: list[ResolvedTarget] = []
    seen_names: set[str] = set()
    for target in deduplicated:
        name = target.name
        suffix = 2
        while name in seen_names:
            name = f"{target.name}-{suffix}"
            suffix += 1
        seen_names.add(name)
        resolved.append(replace(target, name=name))
    return resolved


def _from_catalog(target: CatalogTarget, base: str) -> ResolvedTarget:
    return ResolvedTarget(
        target.name,
        _target_url(base, target.path),
        target.description,
        target.actions,
        target.expects_writes,
        target.resolve,
        target.requires,
    )


def _resolve_one(value: str, base: str) -> ResolvedTarget:
    label, candidate = _split_label(value.strip())
    if candidate in TARGETS:
        return replace(
            _from_catalog(TARGETS[candidate], base),
            name=_clean_name(label) or TARGETS[candidate].name,
        )
    if candidate.startswith(("http://", "https://")):
        parsed = urlparse(candidate)
        if not parsed.netloc:
            raise ValueError(f"Invalid URL {candidate!r}.")
        return ResolvedTarget(_clean_name(label) or _url_name(candidate), candidate)
    if candidate.startswith("/"):
        return ResolvedTarget(
            _clean_name(label) or _path_name(candidate),
            _target_url(base, candidate),
        )
    known = ", ".join(TARGETS)
    raise ValueError(
        f"Unknown screenshot target {value!r}. Use one of: {known}; or pass a /route,"
        " an http(s) URL, or label=/route."
    )


def _split_label(value: str) -> tuple[str, str]:
    """Split ``label=/route`` or ``label=http://...`` without touching query strings."""
    if value.startswith(("http://", "https://")):
        return "", value
    if "=" not in value:
        return "", value
    label, _, candidate = value.partition("=")
    if candidate.startswith(("http://", "https://", "/")):
        return label.strip(), candidate.strip()
    return "", value


def _target_url(base: str, path: str) -> str:
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{base}{path}" if path != "/" else f"{base}/"


def _path_name(path: str) -> str:
    """Name a route after its last segment and, if present, its query."""
    route, _, query = path.partition("?")
    parts = [part for part in route.split("/") if part]
    name = _clean_name(parts[-1] if parts else "home") or "home"
    query_slug = _clean_name(query.split("#")[0].replace("=", "-").replace("&", "-"))
    return f"{name}--{query_slug}"[:80] if query_slug else name


def _url_name(url: str) -> str:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    candidate = parts[-1] if parts else (parsed.hostname or "page")
    stem = candidate.rsplit(".", 1)[0] if "." in candidate else candidate
    return _clean_name(stem) or "page"


def _clean_name(value: str) -> str:
    slug = _SLUG_PATTERN.sub("-", value.lower()).strip("-")
    return slug[:80]
