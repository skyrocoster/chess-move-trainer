export {
  OpeningLineLibraryContractError,
  openingLineLibraryFailureFromHttp,
  parseOpeningLineLibraryError,
  parseOpeningLineLibraryResponse,
} from "./openingsApiParser";
import type {
  LineLibraryData,
  LineLibraryFilterKind,
} from "../design-system/line-library/lineLibraryTypes";

export type OpeningLineLibraryScalar = string | number | boolean | null;
export type OpeningLineLibraryFilterType =
  | "search"
  | "select"
  | "multiselect"
  | "toggle"
  | "range"
  | "custom";
export type OpeningLineLibraryNodeKind = "group" | "line" | "reference";

export interface OpeningLineLibraryFilterOption {
  value: string;
  label: string;
}

export interface OpeningLineLibraryFilterDeclaration {
  key: string;
  label: string;
  type: OpeningLineLibraryFilterType;
  options: readonly OpeningLineLibraryFilterOption[];
  range_start: OpeningLineLibraryScalar;
  range_end: OpeningLineLibraryScalar;
  metadata: Readonly<Record<string, OpeningLineLibraryScalar>>;
}

export interface OpeningLineLibrarySortDeclaration {
  key: string;
  label: string;
  default: boolean;
  direction: "asc" | "desc";
}

interface OpeningLineLibraryNodeBase {
  id: string;
  child_ids: readonly string[];
  disabled: boolean;
  disabled_reason: string | null;
  metadata: Readonly<Record<string, OpeningLineLibraryScalar>>;
}

export interface OpeningLineLibraryGroupNode extends OpeningLineLibraryNodeBase {
  kind: "group";
  selectable: boolean;
}

export interface OpeningLineLibraryLineNode extends OpeningLineLibraryNodeBase {
  kind: "line";
  selectable: true;
}

export interface OpeningLineLibraryReferenceNode extends OpeningLineLibraryNodeBase {
  kind: "reference";
  selectable: false;
  target_id: string;
}

export type OpeningLineLibraryNode =
  | OpeningLineLibraryGroupNode
  | OpeningLineLibraryLineNode
  | OpeningLineLibraryReferenceNode;

export interface OpeningLineLibraryResponse {
  roots: readonly string[];
  nodes: Readonly<Record<string, OpeningLineLibraryNode>>;
  filters: readonly OpeningLineLibraryFilterDeclaration[];
  filter_apply_mode: "immediate" | "explicit";
  sorts: readonly OpeningLineLibrarySortDeclaration[];
  selection_limit: number | null;
}

export type OpeningLineLibraryErrorCode =
  | "invalid_filter"
  | "line_library_unavailable"
  | "unexpected_failure";

export interface OpeningLineLibraryErrorResponse {
  code: OpeningLineLibraryErrorCode;
  message: string;
}

export type OpeningLineLibraryFailure = {
  status: OpeningLineLibraryErrorCode;
  message: string;
};

export type OpeningLineLibraryResult =
  | { status: "success"; data: OpeningLineLibraryResponse }
  | OpeningLineLibraryFailure;

function filterKind(type: OpeningLineLibraryFilterType): LineLibraryFilterKind {
  if (type === "search") return "search";
  if (type === "toggle") return "boolean";
  if (type === "select" || type === "multiselect") return "select";
  return "text";
}

export function openingLineLibraryResponseToData(
  response: OpeningLineLibraryResponse,
): LineLibraryData {
  const nodes = Object.fromEntries(
    Object.entries(response.nodes).map(([id, node]) => [
      id,
      {
        id: node.id,
        kind: node.kind,
        child_ids: node.child_ids,
        disabled: node.disabled,
        disabled_reason: node.disabled_reason,
        selectable: node.selectable,
        metadata: node.metadata,
        ...(node.kind === "reference" ? { reference_target: node.target_id } : {}),
      },
    ]),
  );
  return {
    roots: response.roots,
    nodes,
    filters: response.filters.map((filter) => ({
      id: filter.key,
      label: filter.label,
      kind: filterKind(filter.type),
      options: filter.options,
    })),
    filter_apply_mode: response.filter_apply_mode,
    sorts: response.sorts.map((sort) => ({
      id: sort.key,
      label: sort.label,
      direction: sort.direction === "asc" ? "ascending" : "descending",
    })),
    selection_limit: response.selection_limit,
  };
}
