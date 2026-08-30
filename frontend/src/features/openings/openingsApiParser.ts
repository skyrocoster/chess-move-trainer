import type {
  OpeningLineLibraryErrorCode,
  OpeningLineLibraryErrorResponse,
  OpeningLineLibraryFilterDeclaration,
  OpeningLineLibraryFilterOption,
  OpeningLineLibraryFilterType,
  OpeningLineLibraryNode,
  OpeningLineLibraryResponse,
  OpeningLineLibraryScalar,
  OpeningLineLibrarySortDeclaration,
} from "./openingsApi";

type JsonRecord = Record<string, unknown>;
type ParsedNodeBase = {
  id: string;
  child_ids: readonly string[];
  disabled: boolean;
  disabled_reason: string | null;
  metadata: Readonly<Record<string, OpeningLineLibraryScalar>>;
};

export class OpeningLineLibraryContractError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "OpeningLineLibraryContractError";
  }
}

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasExactKeys(value: JsonRecord, keys: readonly string[]): boolean {
  return Object.keys(value).sort().join(",") === [...keys].sort().join(",");
}

function contractFailure(message: string): never {
  throw new OpeningLineLibraryContractError(message);
}

function stringValue(value: unknown, field: string): string {
  return typeof value === "string" ? value : contractFailure(`${field} must be a string`);
}

function booleanValue(value: unknown, field: string): boolean {
  return typeof value === "boolean" ? value : contractFailure(`${field} must be a boolean`);
}

function scalarValue(value: unknown, field: string): OpeningLineLibraryScalar {
  if (value === null || typeof value === "string" || typeof value === "boolean") return value;
  if (typeof value === "number" && Number.isFinite(value)) return value;
  return contractFailure(`${field} must be a JSON scalar`);
}

function nullableString(value: unknown, field: string): string | null {
  return value === null ? null : stringValue(value, field);
}

function stringArray(value: unknown, field: string): string[] {
  if (!Array.isArray(value)) contractFailure(`${field} must be an array`);
  return value.map((item, index) => stringValue(item, `${field}[${index}]`));
}

function scalarRecord(value: unknown, field: string): Record<string, OpeningLineLibraryScalar> {
  if (!isRecord(value)) contractFailure(`${field} must be an object`);
  return Object.fromEntries(
    Object.entries(value).map(([key, item]) => [key, scalarValue(item, `${field}.${key}`)]),
  );
}

function nodeBase(value: JsonRecord, field: string): ParsedNodeBase {
  return {
    id: stringValue(value.id, `${field}.id`),
    child_ids: stringArray(value.child_ids, `${field}.child_ids`),
    disabled: booleanValue(value.disabled, `${field}.disabled`),
    disabled_reason: nullableString(value.disabled_reason, `${field}.disabled_reason`),
    metadata: scalarRecord(value.metadata, `${field}.metadata`),
  };
}

function validateDisabledState(node: ParsedNodeBase, field: string): void {
  if (node.disabled && !node.disabled_reason)
    contractFailure(`${field} disabled nodes require a reason`);
  if (!node.disabled && node.disabled_reason !== null) {
    contractFailure(`${field} enabled nodes cannot declare a disabled reason`);
  }
}

const NODE_KEYS = [
  "id",
  "kind",
  "child_ids",
  "disabled",
  "disabled_reason",
  "metadata",
  "selectable",
] as const;
const REFERENCE_KEYS = [...NODE_KEYS, "target_id"] as const;

function parseNode(value: unknown, field: string): OpeningLineLibraryNode {
  if (!isRecord(value) || typeof value.kind !== "string") {
    contractFailure(`${field} must declare a node kind`);
  }

  if (value.kind === "group") {
    if (!hasExactKeys(value, NODE_KEYS)) contractFailure(`${field} has an invalid group shape`);
    const base = nodeBase(value, field);
    validateDisabledState(base, field);
    return {
      ...base,
      kind: "group",
      selectable: booleanValue(value.selectable, `${field}.selectable`),
    };
  }

  if (value.kind === "line") {
    if (!hasExactKeys(value, NODE_KEYS)) contractFailure(`${field} has an invalid line shape`);
    const base = nodeBase(value, field);
    validateDisabledState(base, field);
    if (value.selectable !== true) contractFailure(`${field}.selectable must be true for lines`);
    if (base.child_ids.length > 0) contractFailure(`${field} lines cannot have children`);
    return { ...base, kind: "line", selectable: true };
  }

  if (value.kind === "reference") {
    if (!hasExactKeys(value, REFERENCE_KEYS))
      contractFailure(`${field} has an invalid reference shape`);
    const base = nodeBase(value, field);
    if (base.disabled || base.disabled_reason !== null) {
      contractFailure(`${field} references cannot be disabled`);
    }
    if (base.child_ids.length > 0) contractFailure(`${field} references cannot have children`);
    if (value.selectable !== false)
      contractFailure(`${field}.selectable must be false for references`);
    return {
      ...base,
      kind: "reference",
      selectable: false,
      target_id: stringValue(value.target_id, `${field}.target_id`),
    };
  }

  contractFailure(`${field}.kind is not supported`);
}

const FILTER_TYPES = ["search", "select", "multiselect", "toggle", "range", "custom"] as const;

function parseFilterType(value: unknown, field: string): OpeningLineLibraryFilterType {
  if (typeof value === "string" && (FILTER_TYPES as readonly string[]).includes(value)) {
    return value as OpeningLineLibraryFilterType;
  }
  return contractFailure(`${field}.type is not supported`);
}

function parseFilterOption(value: unknown, field: string): OpeningLineLibraryFilterOption {
  if (!isRecord(value) || !hasExactKeys(value, ["value", "label"])) {
    contractFailure(`${field} has an invalid option shape`);
  }
  return {
    value: stringValue(value.value, `${field}.value`),
    label: stringValue(value.label, `${field}.label`),
  };
}

function parseFilter(value: unknown, field: string): OpeningLineLibraryFilterDeclaration {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, [
      "key",
      "label",
      "type",
      "options",
      "range_start",
      "range_end",
      "metadata",
    ])
  ) {
    contractFailure(`${field} has an invalid filter shape`);
  }
  const type = parseFilterType(value.type, field);
  if (!Array.isArray(value.options)) contractFailure(`${field}.options must be an array`);
  const options = value.options.map((option, index) =>
    parseFilterOption(option, `${field}.options[${index}]`),
  );
  const rangeStart = scalarValue(value.range_start, `${field}.range_start`);
  const rangeEnd = scalarValue(value.range_end, `${field}.range_end`);

  if (
    (type === "search" || type === "toggle") &&
    (options.length > 0 || rangeStart !== null || rangeEnd !== null)
  ) {
    contractFailure(`${field} cannot declare options or a range`);
  }
  if (
    (type === "select" || type === "multiselect") &&
    (options.length === 0 || rangeStart !== null || rangeEnd !== null)
  ) {
    contractFailure(`${field} requires options and no range`);
  }
  if (
    type === "range" &&
    (options.length > 0 || rangeStart === null || rangeEnd === null || rangeStart === rangeEnd)
  ) {
    contractFailure(`${field} requires distinct range bounds and no options`);
  }
  if (type === "custom" && options.length > 0 && (rangeStart !== null || rangeEnd !== null)) {
    contractFailure(`${field} cannot declare options and a range together`);
  }

  return {
    key: stringValue(value.key, `${field}.key`),
    label: stringValue(value.label, `${field}.label`),
    type,
    options,
    range_start: rangeStart,
    range_end: rangeEnd,
    metadata: scalarRecord(value.metadata, `${field}.metadata`),
  };
}

function parseSort(value: unknown, field: string): OpeningLineLibrarySortDeclaration {
  if (!isRecord(value) || !hasExactKeys(value, ["key", "label", "default", "direction"])) {
    contractFailure(`${field} has an invalid sort shape`);
  }
  const direction =
    value.direction === "asc" || value.direction === "desc" ? value.direction : null;
  if (direction === null) contractFailure(`${field}.direction is not supported`);
  return {
    key: stringValue(value.key, `${field}.key`),
    label: stringValue(value.label, `${field}.label`),
    default: booleanValue(value.default, `${field}.default`),
    direction,
  };
}

function nullableNonnegativeInteger(value: unknown, field: string): number | null {
  if (value === null) return null;
  if (typeof value === "number" && Number.isInteger(value) && value >= 0) return value;
  return contractFailure(`${field} must be a nonnegative integer or null`);
}

function validateGraph(response: OpeningLineLibraryResponse): void {
  const nodeIds = new Set(Object.keys(response.nodes));
  if (new Set(response.roots).size !== response.roots.length)
    contractFailure("roots must be unique");
  response.roots.forEach((root) => {
    if (!nodeIds.has(root)) contractFailure("roots must address nodes");
  });

  for (const [id, node] of Object.entries(response.nodes)) {
    if (node.id !== id) contractFailure("nodes must be keyed by each node's id");
    node.child_ids.forEach((child) => {
      if (!nodeIds.has(child)) contractFailure("child_ids must address nodes");
    });
    if (node.kind === "reference") {
      if (!nodeIds.has(node.target_id)) contractFailure("reference target_id must address a node");
      if (response.nodes[node.target_id]?.kind === "reference") {
        contractFailure("references must target canonical nodes");
      }
    }
  }

  const visiting = new Set<string>();
  const visited = new Set<string>();
  const visit = (id: string): void => {
    if (visiting.has(id)) contractFailure("normalized child graph must be acyclic");
    if (visited.has(id)) return;
    visiting.add(id);
    response.nodes[id].child_ids.forEach(visit);
    visiting.delete(id);
    visited.add(id);
  };
  nodeIds.forEach(visit);
}

export function parseOpeningLineLibraryResponse(value: unknown): OpeningLineLibraryResponse {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, [
      "roots",
      "nodes",
      "filters",
      "filter_apply_mode",
      "sorts",
      "selection_limit",
    ])
  ) {
    contractFailure("opening Line Library response has an invalid shape");
  }
  const roots = stringArray(value.roots, "roots");
  if (!isRecord(value.nodes)) contractFailure("nodes must be an object");
  const nodes = Object.fromEntries(
    Object.entries(value.nodes).map(([id, node]) => [id, parseNode(node, `nodes.${id}`)]),
  );
  if (!Array.isArray(value.filters)) contractFailure("filters must be an array");
  if (!Array.isArray(value.sorts)) contractFailure("sorts must be an array");
  const filter_apply_mode =
    value.filter_apply_mode === "immediate" || value.filter_apply_mode === "explicit"
      ? value.filter_apply_mode
      : contractFailure("filter_apply_mode is not supported");
  const filters = value.filters.map((filter, index) => parseFilter(filter, `filters[${index}]`));
  const sorts = value.sorts.map((sort, index) => parseSort(sort, `sorts[${index}]`));
  if (new Set(filters.map((filter) => filter.key)).size !== filters.length) {
    contractFailure("filter keys must be unique");
  }
  if (new Set(sorts.map((sort) => sort.key)).size !== sorts.length) {
    contractFailure("sort keys must be unique");
  }
  if (sorts.filter((sort) => sort.default).length > 1)
    contractFailure("at most one sort may be default");

  const response: OpeningLineLibraryResponse = {
    roots,
    nodes,
    filters,
    filter_apply_mode,
    sorts,
    selection_limit: nullableNonnegativeInteger(value.selection_limit, "selection_limit"),
  };
  validateGraph(response);
  return response;
}

function isErrorCode(value: unknown): value is OpeningLineLibraryErrorCode {
  return (
    value === "invalid_filter" ||
    value === "line_library_unavailable" ||
    value === "unexpected_failure"
  );
}

export function parseOpeningLineLibraryError(
  value: unknown,
): OpeningLineLibraryErrorResponse | null {
  if (!isRecord(value) || !hasExactKeys(value, ["code", "message"])) return null;
  return isErrorCode(value.code) && typeof value.message === "string"
    ? { code: value.code, message: value.message }
    : null;
}

export function openingLineLibraryFailureFromHttp(
  status: number,
  value: unknown,
): { status: OpeningLineLibraryErrorCode; message: string } {
  const error = parseOpeningLineLibraryError(value);
  const expectedStatus =
    error?.code === "invalid_filter"
      ? 422
      : error?.code === "line_library_unavailable"
        ? 503
        : error?.code === "unexpected_failure"
          ? 500
          : null;
  if (error && status === expectedStatus) return { status: error.code, message: error.message };
  return { status: "unexpected_failure", message: "Unable to serve opening Line Library" };
}
