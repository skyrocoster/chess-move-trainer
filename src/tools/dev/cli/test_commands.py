"""The ``test`` command group: discover, inspect and run tests by domain."""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict

import typer

from tools.dev.console import echo, fail
from tools.dev.test import profiles, reports
from tools.dev.test.catalog import Catalog, load_catalog
from tools.dev.test.discovery import (
    DiscoveryResult,
    TestCase,
    discover,
    summarize,
    validate_catalog_files,
)
from tools.dev.test.runner import describe, dry_run, execute
from tools.dev.test.selection import SelectionError, preflight, resolve

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="List, inspect and run tests by approved domain or profile.",
)


def _load() -> tuple[Catalog, DiscoveryResult]:
    """Load the catalogue, discover units and report validation problems."""
    catalog = load_catalog()
    problems = validate_catalog_files(catalog)
    discovery = discover(catalog)
    problems.extend(discovery.problems)
    summarize(problems, discovery.notes)
    return catalog, discovery


def _cases_by_domain(cases: list[TestCase], domain: str, layer: str) -> list[TestCase]:
    return [
        case
        for case in cases
        if (not domain or case.domain == domain or f"{case.domain}.{case.subdomain}" == domain)
        and (not layer or case.layer == layer)
    ]


def _units(count: int) -> str:
    return f"{count} unit(s)"


@app.command("list", help="Show the grouped domain tree with discovered unit counts.")
def list_command(
    domain: str = typer.Option("", "--domain", help="Only this domain or dotted subdomain."),
    layer: str = typer.Option("", "--layer", help="Only this execution layer."),
    tree: bool = typer.Option(False, "--tree", help="Also show each file and its unit count."),
    json_output: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """List discovered tests grouped by domain and layer."""
    catalog, discovery = _load()
    cases = _cases_by_domain(discovery.cases, domain, layer)
    if json_output:
        echo(json.dumps(_catalog_json(catalog, cases), indent=2))
        return
    if not cases:
        fail(f"No tests match domain={domain!r} layer={layer!r}.")
    counts = Counter(case.layer for case in cases)
    layers = ", ".join(f"{name}: {count}" for name, count in sorted(counts.items()))
    echo(f"{_units(len(cases))} [{layers}]")
    grouped = defaultdict(list)
    for case in cases:
        grouped[case.domain].append(case)
    for domain_key in _ordered_domains(catalog, grouped):
        domain_cases = grouped[domain_key]
        title = catalog.domains[domain_key].title
        subdomains = sorted({case.subdomain for case in domain_cases if case.subdomain})
        suffix = f" ({len(subdomains)} subdomain(s))" if subdomains else ""
        echo(f"\n{domain_key} - {title}{suffix}")
        by_layer = Counter(case.layer for case in domain_cases)
        echo(
            "  layers: " + ", ".join(f"{name}: {count}" for name, count in sorted(by_layer.items()))
        )
        if tree:
            by_source = Counter(case.source for case in domain_cases)
            for source, count in sorted(by_source.items()):
                echo(f"    {count:>4}  {source}")


@app.command("show", help="Show a domain, subdomain, file group or exact test id.")
def show_command(
    target: str = typer.Argument(..., help="Domain, dotted subdomain, group id or exact case id."),
) -> None:
    """Show ownership, purpose, counts and the exact run command."""
    catalog, discovery = _load()
    if target in catalog.domains:
        _show_domain(catalog, discovery, target)
        return
    parent = _dotted_domains(catalog).get(target)
    if parent is not None:
        _show_domain(catalog, discovery, parent, subdomain=target.rsplit(".", 1)[-1])
        return
    matches = [case for case in discovery.cases if case.id == target]
    if not matches and "::" not in target:
        matches = [case for case in discovery.cases if case.id.split("::", 1)[0] == target]
    if not matches:
        prefix = target.split("::", 1)[0]
        close = sorted(case.id for case in discovery.cases if prefix in case.id)[:5]
        hint = f" Close matches: {', '.join(close)}" if close else ""
        fail(f"No domain or test id matches {target!r}.{hint}")
    if len(matches) > 1:
        layers = Counter(case.layer for case in matches)
        echo(f"group:   {target}")
        echo(
            f"units:   {len(matches)} ["
            + ", ".join(f"{key}: {value}" for key, value in sorted(layers.items()))
            + "]"
        )
        echo(f"sources: {', '.join(sorted({case.source for case in matches}))}")
        echo(f"run:     sg test run --id {target}")
        return
    case = matches[0]
    echo(f"id:      {case.id}")
    echo(f"runner:  {case.backend}   layer: {case.layer}")
    echo(
        f"domain:  {case.domain}.{case.subdomain}" if case.subdomain else f"domain:  {case.domain}"
    )
    echo(f"source:  {case.source}")
    echo(f"fixture: {case.fixture}   speed: {case.speed}")
    if case.real_data:
        echo("safety:  reads the live database; run only via `sg test profiles real-data`")
    if case.needs_services:
        echo("safety:  needs healthy development services (sg dev start)")
    echo(f"run:     sg test run --id {case.id}")


def _show_domain(
    catalog: Catalog, discovery: DiscoveryResult, key: str, subdomain: str | None = None
) -> None:
    domain = catalog.domains[key]
    cases = [
        case
        for case in discovery.cases
        if case.domain == key and (subdomain is None or case.subdomain == subdomain)
    ]
    echo(f"{key}" + (f".{subdomain}" if subdomain else "") + f" - {domain.title}")
    echo(f"owner:   {domain.owner}")
    echo(f"purpose: {domain.purpose}")
    echo(f"tags:    {', '.join(domain.tags) or '-'}")
    echo(f"fixture: {domain.default_fixture}")
    if not subdomain:
        subdomain_counts = Counter(case.subdomain for case in cases)
        for sub_key in domain.subdomains:
            echo(f"  {sub_key}: {subdomain_counts[sub_key]} unit(s)")
    by_layer = Counter(case.layer for case in cases)
    echo("layers:  " + ", ".join(f"{name}: {count}" for name, count in sorted(by_layer.items())))
    echo(f"run:     sg test run --domain {key}")
    if subdomain:
        echo(f"run:     sg test run --domain {key}.{subdomain}")


@app.command("run", help="Run exactly the selected tests with a safety preflight.")
def run_command(
    test_id: str = typer.Option("", "--id", help="Exact logical test id or file group id."),
    domain: str = typer.Option("", "--domain", help="Domain or dotted subdomain."),
    layer: str = typer.Option("", "--layer", help="Execution layer."),
    dry_run_flag: bool = typer.Option(False, "--dry-run", help="Print commands without running."),
) -> None:
    """Resolve, preflight and run a selection, persisting a report."""
    started = time.monotonic()
    catalog, discovery = _load()
    selection_seconds = time.monotonic() - started
    try:
        cases = resolve(cases=discovery.cases, test_id=test_id, domain=domain, layer=layer)
        preflight(cases, allow_real_data=False)
    except SelectionError as error:
        fail(str(error))
    echo(f"Selected: {describe(cases)}")
    if dry_run_flag:
        dry_run(cases, catalog, allow_real_data=False)
        return
    report = execute(
        cases,
        catalog,
        request={"command": "run", "id": test_id, "domain": domain, "layer": layer},
        selection_seconds=selection_seconds,
    )
    _finish(report)


@app.command("profiles", help="Run an approved profile: quick, smoke, full, e2e or real-data.")
def profiles_command(
    name: str = typer.Argument(..., help=f"One of: {', '.join(profiles.PROFILES)}."),
    dry_run_flag: bool = typer.Option(False, "--dry-run", help="Print commands without running."),
) -> None:
    """Run one approved profile with its budget and safety policy."""
    if name not in profiles.PROFILES:
        fail(f"Unknown profile {name!r}. Choose one of: {', '.join(profiles.PROFILES)}.")
    started = time.monotonic()
    catalog, discovery = _load()
    selection_seconds = time.monotonic() - started
    profile = profiles.PROFILES[name]
    cases = profiles.select(discovery.cases, name)
    if not cases:
        fail(f"Profile {name!r} resolved to zero units.")
    try:
        preflight(cases, allow_real_data=profile.allow_real_data)
    except SelectionError as error:
        fail(str(error))
    echo(f"Profile: {profile.name} - {profile.description}")
    echo(f"Selected: {describe(cases)}")
    if dry_run_flag:
        dry_run(
            cases,
            catalog,
            allow_real_data=profile.allow_real_data,
            budget_seconds=profile.budget_seconds,
        )
        return
    report = execute(
        cases,
        catalog,
        request={"command": name},
        budget_seconds=profile.budget_seconds,
        allow_real_data=profile.allow_real_data,
        selection_seconds=selection_seconds,
    )
    _finish(report)


@app.command("failures", help="Show the newest run's failures and exact rerun commands.")
def failures_command(
    run_id: str = typer.Option("", "--run", help="Explicit run id under build/test-results."),
) -> None:
    """Read the newest (or named) persisted run and list its failures."""
    summary = _latest_summary() if not run_id else _summary_for(run_id)
    for line in reports.format_failures(summary):
        echo(line)


@app.command("report", help="Show a persisted run summary and its artifacts.")
def report_command(
    run_id: str = typer.Option("", "--run", help="Explicit run id under build/test-results."),
    last: bool = typer.Option(False, "--last", help="Newest run (the default)."),
) -> None:
    """Print the concise summary of one run."""
    del last  # both spellings select the newest run unless --run is explicit
    summary = _latest_summary() if not run_id else _summary_for(run_id)
    for line in reports.format_report(summary):
        echo(line)
    echo(f"artifacts: {reports.RUN_ROOT / summary['run_id']}")


@app.command("catalog", help="Validate and emit the machine-readable catalogue.")
def catalog_command(
    json_output: bool = typer.Option(True, "--json/--no-json", help="JSON (default) or a summary."),
) -> None:
    """Emit catalogue metadata, discovered identity and validation state."""
    catalog, discovery = _load()
    if json_output:
        echo(json.dumps(_catalog_json(catalog, discovery.cases), indent=2))
        return
    echo(f"catalogue: {catalog.path}")
    echo(f"domains:   {len(catalog.domains)}")
    echo(f"units:     {len(discovery.cases)}")
    echo("validate:  sg test list")


def _latest_summary() -> dict:
    directory = reports.latest_run()
    if directory is None:
        fail("No recorded runs under build/test-results. Run `sg test profiles quick` first.")
    summary = reports.load_summary(directory)
    if summary is None:
        fail(f"Could not read the run summary at {directory / 'summary.json'}")
    return summary


def _summary_for(run_id: str) -> dict:
    summary = reports.load_summary(reports.RUN_ROOT / run_id)
    if summary is None:
        fail(f"No run summary found at build/test-results/{run_id}/summary.json")
    return summary


def _finish(report: reports.RunReport) -> None:
    echo(f"Status: {report.status} in {report.total_seconds:.1f}s")
    if report.status != "passed":
        fail(f"Test run failed; inspect the report at {report.directory}", code=1)


def _ordered_domains(catalog: Catalog, grouped: dict[str, list[TestCase]]) -> list[str]:
    return [key for key in catalog.domains if key in grouped]


def _dotted_domains(catalog: Catalog) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, domain in catalog.domains.items():
        for sub_key in domain.subdomains:
            result[f"{key}.{sub_key}"] = key
    return result


def _catalog_json(catalog: Catalog, cases: list[TestCase]) -> dict:
    domains = {}
    for key, domain in catalog.domains.items():
        domains[key] = {
            "title": domain.title,
            "owner": domain.owner,
            "purpose": domain.purpose,
            "tags": list(domain.tags),
            "default_fixture": domain.default_fixture,
            "paths": list(domain.paths),
            "subdomains": {
                sub_key: {"paths": list(sub.paths), "default_fixture": sub.default_fixture}
                for sub_key, sub in domain.subdomains.items()
            },
        }
    return {
        "meta": catalog.meta,
        "domains": domains,
        "profiles": {
            key: {
                "description": profile.description,
                "budget_seconds": profile.budget_seconds,
                "allow_real_data": profile.allow_real_data,
            }
            for key, profile in profiles.PROFILES.items()
        },
        "cases": [
            {
                "id": case.id,
                "backend": case.backend,
                "layer": case.layer,
                "domain": case.domain,
                "subdomain": case.subdomain,
                "source": case.source,
                "fixture": case.fixture,
                "speed": case.speed,
                "real_data": case.real_data,
                "manual": case.manual,
                "needs_services": case.needs_services,
                "available": case.available,
            }
            for case in cases
        ],
    }
