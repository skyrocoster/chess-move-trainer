import type {
  LineLibraryData,
  LineLibraryFilterValues,
} from "../design-system/line-library/lineLibraryTypes";
import {
  openingLineLibraryResponseToData,
  parseOpeningLineLibraryResponse,
  type OpeningLineLibraryNode,
  type OpeningLineLibraryResponse,
} from "./openingsApi";

/** Synthetic in-memory fixtures only. IDs, names, ECO values, and corpus matches are not production data. */
export const SYNTHETIC_FIXTURE_NOTICE =
  "Synthetic in-memory fixture only — IDs and values are not authoritative production data.";

const ROOT_ID = "synthetic-opening-root";
const FAMILY_ID = "synthetic-opening-family";
const DEEP_BRANCH_ID = "synthetic-deep-opening-branch";
const SICILIAN_ID = "synthetic-line-sicilian";
const CARO_KANN_ID = "synthetic-line-caro-kann";
const ENGLISH_ID = "synthetic-line-english";
const DISABLED_ID = "synthetic-line-disabled";
const REFERENCE_ID = "synthetic-transposition-reference";

const syntheticFilters = [
  {
    key: "search",
    label: "Search",
    type: "search" as const,
    options: [],
    range_start: null,
    range_end: null,
    metadata: {},
  },
  {
    key: "eco",
    label: "ECO code/range",
    type: "range" as const,
    options: [],
    range_start: "A00",
    range_end: "E99",
    metadata: { value_kind: "eco" },
  },
  {
    key: "appears_in_my_games",
    label: "Appears in my games",
    type: "toggle" as const,
    options: [],
    range_start: null,
    range_end: null,
    metadata: { scope: "fixed accepted corpus (synthetic simulation)" },
  },
] as const;

const syntheticNodes: Readonly<Record<string, OpeningLineLibraryNode>> = {
  [ROOT_ID]: {
    id: ROOT_ID,
    kind: "group",
    child_ids: [FAMILY_ID, ENGLISH_ID],
    disabled: false,
    disabled_reason: null,
    metadata: { name: "Synthetic opening library", eco: "A00", move_sequence: "" },
    selectable: true,
  },
  [FAMILY_ID]: {
    id: FAMILY_ID,
    kind: "group",
    child_ids: [SICILIAN_ID, DEEP_BRANCH_ID, REFERENCE_ID],
    disabled: false,
    disabled_reason: null,
    metadata: { name: "Synthetic central family", eco: "B00", move_sequence: "e4" },
    selectable: true,
  },
  [DEEP_BRANCH_ID]: {
    id: DEEP_BRANCH_ID,
    kind: "group",
    child_ids: [CARO_KANN_ID, DISABLED_ID],
    disabled: false,
    disabled_reason: null,
    metadata: { name: "Synthetic arbitrary-depth branch", eco: "B00", move_sequence: "e4 e5" },
    selectable: true,
  },
  [SICILIAN_ID]: {
    id: SICILIAN_ID,
    kind: "line",
    child_ids: [],
    disabled: false,
    disabled_reason: null,
    metadata: { name: "Synthetic Sicilian branch", eco: "B20", move_sequence: "e4 c5" },
    selectable: true,
  },
  [CARO_KANN_ID]: {
    id: CARO_KANN_ID,
    kind: "line",
    child_ids: [],
    disabled: false,
    disabled_reason: null,
    metadata: { name: "Synthetic Caro-Kann branch", eco: "B10", move_sequence: "e4 c6" },
    selectable: true,
  },
  [ENGLISH_ID]: {
    id: ENGLISH_ID,
    kind: "line",
    child_ids: [],
    disabled: false,
    disabled_reason: null,
    metadata: { name: "Synthetic English branch", eco: "A10", move_sequence: "c4" },
    selectable: true,
  },
  [DISABLED_ID]: {
    id: DISABLED_ID,
    kind: "line",
    child_ids: [],
    disabled: true,
    disabled_reason: "Synthetic fixture: unavailable in this result",
    metadata: { name: "Synthetic unavailable branch", eco: "C00", move_sequence: "d4 d5" },
    selectable: true,
  },
  [REFERENCE_ID]: {
    id: REFERENCE_ID,
    kind: "reference",
    child_ids: [],
    disabled: false,
    disabled_reason: null,
    metadata: { name: "Synthetic transposition reference", eco: "B20", move_sequence: "e4 c5" },
    selectable: false,
    target_id: SICILIAN_ID,
  },
};

export const SYNTHETIC_ACCEPTED_CORPUS_LINE_IDS = new Set([SICILIAN_ID, CARO_KANN_ID]);

export const SYNTHETIC_OPENING_RESPONSE: OpeningLineLibraryResponse = {
  roots: [ROOT_ID],
  nodes: syntheticNodes,
  filters: syntheticFilters,
  filter_apply_mode: "immediate",
  sorts: [{ key: "default", label: "Synthetic backend order", default: true, direction: "asc" }],
  selection_limit: null,
};

/** A separate synthetic declaration used to show the generic maximum-selection behavior. */
export const SYNTHETIC_LIMITED_OPENING_RESPONSE: OpeningLineLibraryResponse = {
  ...SYNTHETIC_OPENING_RESPONSE,
  selection_limit: 1,
};

export const SYNTHETIC_INITIAL_FILTERS: LineLibraryFilterValues = {
  search: "",
  eco: "",
  appears_in_my_games: false,
};

const SYNTHETIC_NODE_ORDER = [
  ROOT_ID,
  FAMILY_ID,
  SICILIAN_ID,
  DEEP_BRANCH_ID,
  CARO_KANN_ID,
  DISABLED_ID,
  REFERENCE_ID,
  ENGLISH_ID,
];

function metadataText(node: OpeningLineLibraryNode): string {
  return [node.metadata.name, node.metadata.eco, node.metadata.move_sequence]
    .filter((value): value is string => typeof value === "string")
    .join(" ")
    .toLowerCase();
}

function ecoRange(value: unknown): { from: string; to: string } | null {
  if (typeof value !== "string" || value.trim() === "") return null;
  const parts = value.split(":").map((part) => part.trim().toUpperCase());
  if (parts.length > 2 || parts.some((part) => !/^[A-E][0-9]{2}$/.test(part))) return null;
  return { from: parts[0], to: parts[1] ?? parts[0] };
}

function lineMatches(node: OpeningLineLibraryNode, filters: LineLibraryFilterValues): boolean {
  if (node.kind !== "line") return false;
  const search = typeof filters.search === "string" ? filters.search.trim().toLowerCase() : "";
  if (search !== "" && !metadataText(node).includes(search)) return false;
  const range = ecoRange(filters.eco);
  const eco = typeof node.metadata.eco === "string" ? node.metadata.eco : "";
  if (range !== null && (eco < range.from || eco > range.to)) return false;
  if (filters.appears_in_my_games === true && !SYNTHETIC_ACCEPTED_CORPUS_LINE_IDS.has(node.id))
    return false;
  return true;
}

export function syntheticOpeningResponseForFilters(
  response: OpeningLineLibraryResponse = SYNTHETIC_OPENING_RESPONSE,
  filters: LineLibraryFilterValues = SYNTHETIC_INITIAL_FILTERS,
): OpeningLineLibraryResponse {
  const matchingLines = new Set(
    Object.values(response.nodes)
      .filter((node) => lineMatches(node, filters))
      .map((node) => node.id),
  );
  const include = (id: string): boolean => {
    const node = response.nodes[id];
    if (!node) return false;
    if (node.kind === "line") return matchingLines.has(id);
    if (node.kind === "reference") return matchingLines.has(node.target_id);
    return node.child_ids.some(include);
  };
  const includedRoots = response.roots.filter(include);
  const included = new Set<string>();
  const collect = (id: string): void => {
    if (included.has(id) || !include(id)) return;
    included.add(id);
    response.nodes[id].child_ids.forEach(collect);
  };
  includedRoots.forEach(collect);

  const orderedIds = [...included].sort(
    (left, right) => SYNTHETIC_NODE_ORDER.indexOf(left) - SYNTHETIC_NODE_ORDER.indexOf(right),
  );
  const nodes = Object.fromEntries(
    orderedIds.map((id) => {
      const node = response.nodes[id];
      return [
        id,
        node.kind === "group"
          ? { ...node, child_ids: node.child_ids.filter((childId) => included.has(childId)) }
          : node,
      ];
    }),
  );
  return { ...response, roots: includedRoots, nodes };
}

export function syntheticOpeningDataForFilters(
  filters: LineLibraryFilterValues = SYNTHETIC_INITIAL_FILTERS,
  response: OpeningLineLibraryResponse = SYNTHETIC_OPENING_RESPONSE,
): LineLibraryData {
  return openingLineLibraryResponseToData(
    parseOpeningLineLibraryResponse(syntheticOpeningResponseForFilters(response, filters)),
  );
}

export const SYNTHETIC_OPENING_DATA = syntheticOpeningDataForFilters();
export const SYNTHETIC_EMPTY_DATA = openingLineLibraryResponseToData(
  parseOpeningLineLibraryResponse({ ...SYNTHETIC_OPENING_RESPONSE, roots: [], nodes: {} }),
);
