"""Export the approved clean OpenAPI contract.

Derives the contract from the real FastAPI application schema, filters it to the
explicitly approved allow-list, and writes deterministic JSON. Fails closed if the
filtered result would contain any other path, operation, or schema.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.main import create_app  # noqa: E402

# The only operations approved for the exported clean contract. Adding an entry
# here is a settled API-contract decision and must return to the coordinator.
APPROVED_OPERATIONS: dict[str, set[str]] = {
    "/api/health": {"get"},
    "/api/games": {"get"},
    "/api/games/{game_uuid}": {"get"},
    "/api/openings": {"get"},
    "/api/openings/{opening_key}": {"get"},
    "/api/positions/insight": {"get"},
    "/api/analysis": {"get"},
    "/api/analysis-requests": {"post"},
    "/api/preferred-moves": {"delete", "get", "put"},
}

SCHEMA_REF_PREFIX = "#/components/schemas/"


class ExportError(RuntimeError):
    """Raised when the filtered contract would violate the approved allow-list."""


def _collect_schema_refs(node: Any, refs: set[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref":
                if not isinstance(value, str) or not value.startswith(SCHEMA_REF_PREFIX):
                    raise ExportError(f"unsupported $ref outside approved schema components: {value!r}")
                refs.add(value[len(SCHEMA_REF_PREFIX) :])
            else:
                _collect_schema_refs(value, refs)
    elif isinstance(node, list):
        for item in node:
            _collect_schema_refs(item, refs)


def build_contract() -> dict[str, Any]:
    """Build the approved clean contract from the real app schema without mutating it."""
    app = create_app()
    spec = app.openapi()

    missing_paths = sorted(set(APPROVED_OPERATIONS) - set(spec.get("paths", {})))
    if missing_paths:
        raise ExportError(f"approved paths absent from the app schema: {missing_paths}")

    filtered_paths: dict[str, Any] = {}
    for path, approved_methods in APPROVED_OPERATIONS.items():
        path_item = spec["paths"][path]
        unexpected = sorted(set(path_item) - approved_methods)
        if unexpected:
            raise ExportError(
                f"non-approved members on {path} path item (add to the explicit allow-list "
                f"only after coordinator approval): {unexpected}"
            )
        filtered_paths[path] = {method: path_item[method] for method in sorted(approved_methods)}

    refs: set[str] = set()
    _collect_schema_refs(filtered_paths, refs)

    schemas = spec.get("components", {}).get("schemas", {})
    processed_refs: set[str] = set()
    while pending_refs := refs - processed_refs:
        for name in sorted(pending_refs):
            processed_refs.add(name)
            if name in schemas:
                _collect_schema_refs(schemas[name], refs)

    missing_schemas = sorted(refs - set(schemas))
    if missing_schemas:
        raise ExportError(f"referenced schemas absent from the app schema: {missing_schemas}")

    return {
        "openapi": spec["openapi"],
        "info": spec.get("info", {}),
        "paths": filtered_paths,
        "components": {"schemas": {name: schemas[name] for name in sorted(refs)}},
    }


def export_contract(output_path: Path) -> None:
    """Write the deterministic clean contract JSON to ``output_path``."""
    contract = build_contract()
    unexpected_paths = sorted(set(contract["paths"]) - set(APPROVED_OPERATIONS))
    if unexpected_paths:
        raise ExportError(f"unexpected paths in filtered contract: {unexpected_paths}")
    payload = json.dumps(contract, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(payload, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_path", type=Path, help="destination for the exported contract JSON")
    args = parser.parse_args(argv)
    export_contract(args.output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
