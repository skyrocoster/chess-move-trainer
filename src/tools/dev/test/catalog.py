"""Load and validate the authoritative test-domain catalogue.

``tests/catalog/domains.toml`` attaches static metadata (primary domain,
subdomain, owner, purpose and fixture profile) to test files by path glob. Case
identity for pytest and Playwright is discovered from those frameworks; Vitest
is discovered as a file group because its runner does not expose
a bounded, reliable list command on this project.

A test file must match exactly one domain or subdomain. ``sg test list`` fails
loudly when a file matches none or several, so a new test cannot silently land
outside the catalogue.
"""

from __future__ import annotations

import fnmatch
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from tools.dev.config import (
    CATALOG_PATH,
    E2E_DIR,
    FIXTURE_PROFILES,
    FRONTEND_API_TEST,
    FRONTEND_DIR,
    FRONTEND_TEST_ROOT,
    LAYER_ROOTS,
    REPOSITORY_ROOT,
)


class CatalogError(RuntimeError):
    """Raised when the catalogue is missing, malformed or inconsistent."""


@dataclass(frozen=True)
class Subdomain:
    """One subdomain of a domain, with its file globs."""

    key: str
    paths: tuple[str, ...]
    default_fixture: str | None = None


@dataclass(frozen=True)
class Domain:
    """One primary domain: the invariant owner for its test files."""

    key: str
    title: str
    owner: str
    purpose: str
    paths: tuple[str, ...]
    tags: tuple[str, ...]
    default_fixture: str
    subdomains: dict[str, Subdomain] = field(default_factory=dict)


@dataclass(frozen=True)
class TestFile:
    """Static metadata attached to one test source file."""

    path: str
    layer: str
    domain: str
    subdomain: str | None
    fixture: str
    owner: str
    purpose: str
    tags: tuple[str, ...]

    @property
    def domain_path(self) -> str:
        """Return the dotted domain path used in test ids."""
        return f"{self.domain}.{self.subdomain}" if self.subdomain else self.domain


class Catalog:
    """The parsed catalogue with ordered path matching."""

    def __init__(self, *, path: Path, data: dict) -> None:
        self.path = path
        self.meta = data.get("meta", {})
        domains: dict[str, Domain] = {}
        for key, raw in data.get("domains", {}).items():
            subdomains = {
                sub_key: Subdomain(
                    key=sub_key,
                    paths=tuple(sub_raw.get("paths", ())),
                    default_fixture=sub_raw.get("default_fixture"),
                )
                for sub_key, sub_raw in raw.get("subdomains", {}).items()
            }
            domains[key] = Domain(
                key=key,
                title=raw.get("title", key),
                owner=raw.get("owner", ""),
                purpose=raw.get("purpose", ""),
                paths=tuple(raw.get("paths", ())),
                tags=tuple(raw.get("tags", ())),
                default_fixture=raw.get("default_fixture", "none"),
                subdomains=subdomains,
            )
        self.domains = domains
        self._validate_structure()

    def _validate_structure(self) -> None:
        for domain in self.domains.values():
            if domain.default_fixture not in FIXTURE_PROFILES:
                raise CatalogError(
                    f"domain {domain.key!r} has unsupported fixture {domain.default_fixture!r}"
                )
            for subdomain in domain.subdomains.values():
                if (
                    subdomain.default_fixture is not None
                    and subdomain.default_fixture not in FIXTURE_PROFILES
                ):
                    raise CatalogError(
                        f"domain {domain.key}.{subdomain.key!r} has unsupported fixture"
                        f" {subdomain.default_fixture!r}"
                    )

    def matches(self, relative_path: str) -> list[tuple[Domain, Subdomain | None]]:
        """Return every (domain, subdomain) whose globs match a file path."""
        normalised = relative_path.replace("\\", "/")
        matches: list[tuple[Domain, Subdomain | None]] = []
        for domain in self.domains.values():
            for subdomain in domain.subdomains.values():
                if _matches(normalised, subdomain.paths):
                    matches.append((domain, subdomain))
            if _matches(normalised, domain.paths):
                matches.append((domain, None))
        return matches

    def domain_for_file(self, relative_path: str) -> TestFile | None:
        """Return the assigned metadata for a test file, or ``None``."""
        matches = self.matches(relative_path)
        if not matches:
            return None
        domain, subdomain = matches[0]
        fixture = (subdomain.default_fixture if subdomain else None) or domain.default_fixture
        return TestFile(
            path=relative_path.replace("\\", "/"),
            layer=layer_for_path(relative_path),
            domain=domain.key,
            subdomain=subdomain.key if subdomain else None,
            fixture=fixture,
            owner=domain.owner,
            purpose=domain.purpose,
            tags=domain.tags,
        )

    def validate(self, relative_paths: list[str]) -> list[str]:
        """Return validation problems for the given test source files."""
        problems: list[str] = []
        for relative in relative_paths:
            matches = self.matches(relative)
            if not matches:
                problems.append(f"{relative}: no domain matches this test file")
            elif len(matches) > 1:
                owners = ", ".join(
                    f"{domain.key}.{subdomain.key}" if subdomain else domain.key
                    for domain, subdomain in matches
                )
                problems.append(f"{relative}: matches multiple domains ({owners})")
        return problems


def _matches(relative_path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatchcase(relative_path, pattern) for pattern in patterns)


def layer_for_path(relative_path: str) -> str:
    """Return the execution layer for a repository-relative file path."""
    normalised = relative_path.replace("\\", "/")
    if normalised == FRONTEND_API_TEST:
        return "frontend-api"
    if normalised.startswith(FRONTEND_TEST_ROOT):
        return "frontend"
    for prefix, layer in LAYER_ROOTS:
        if normalised.startswith(prefix):
            return layer
    return "unknown"


def load_catalog(path: Path = CATALOG_PATH) -> Catalog:
    """Load and structurally validate the catalogue file."""
    if not path.is_file():
        raise CatalogError(f"Test catalogue not found: {path}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise CatalogError(f"Test catalogue is not valid TOML: {error}") from error
    return Catalog(path=path, data=data)


def repository_root() -> Path:
    """Return the repository root (kept here for testability)."""
    return REPOSITORY_ROOT


def frontend_relative(path: Path) -> str:
    """Return a frontend-relative path for a Vitest file filter."""
    return str(path.relative_to(FRONTEND_DIR)).replace("\\", "/")


def e2e_relative(path: Path) -> str:
    """Return an e2e-relative path for a Playwright file filter."""
    return str(path.relative_to(E2E_DIR)).replace("\\", "/")
