import type { ComponentPropsWithoutRef, ReactNode } from "react";

export type LineLibraryNodeKind = "group" | "line" | "reference";
export type LineLibraryFilterApplyMode = "immediate" | "explicit";
export type LineLibrarySelectionMode = "single" | "multiple";
export type LineLibrarySelectionState = "unchecked" | "indeterminate" | "checked";

export type LineLibraryFilterValue = string | number | boolean | null;
export type LineLibraryFilterValues = Readonly<Record<string, LineLibraryFilterValue>>;

export interface LineLibraryNodeSelectionDeclaration {
  selectable?: boolean;
}

export interface LineLibraryNode {
  id: string;
  kind: LineLibraryNodeKind;
  child_ids: readonly string[];
  disabled?: boolean;
  disabled_reason?: string | null;
  selectable?: boolean;
  selection?: LineLibraryNodeSelectionDeclaration;
  reference_target?: string | null;
  metadata?: Readonly<Record<string, unknown>>;
}

export interface LineLibraryFilterOption {
  value: string;
  label: string;
}

export type LineLibraryFilterKind = "text" | "search" | "select" | "boolean";

export interface LineLibraryFilterDefinition {
  id: string;
  label: string;
  kind?: LineLibraryFilterKind;
  placeholder?: string;
  default_value?: LineLibraryFilterValue;
  options?: readonly LineLibraryFilterOption[];
}

export interface LineLibrarySortDeclaration {
  id: string;
  label: string;
  direction?: "ascending" | "descending";
}

export interface LineLibraryData {
  roots: readonly string[];
  nodes: Readonly<Record<string, LineLibraryNode>>;
  filters?: readonly LineLibraryFilterDefinition[];
  filter_apply_mode?: LineLibraryFilterApplyMode;
  sorts?: readonly LineLibrarySortDeclaration[];
  selection_limit?: number | null;
}

export interface LineLibrarySelectionDescription {
  selectedIds: readonly string[];
  selectedGroupIds: readonly string[];
  resolvedConcreteIds: readonly string[];
}

export interface LineLibraryCommitDescription extends LineLibrarySelectionDescription {
  filters: LineLibraryFilterValues;
}

export interface LineLibrarySelectionChangeDetails extends LineLibrarySelectionDescription {
  reason: "user" | "filter" | "data" | "controlled";
}

export interface LineLibraryRowContext {
  node: LineLibraryNode;
  label: string;
  level: number;
  isExpanded: boolean;
  isFolder: boolean;
  isSelected: boolean;
  selectionState: LineLibrarySelectionState;
  selectable: boolean;
  disabled: boolean;
  visibleDescendantLineIds: readonly string[];
  referenceTarget: string | null;
  toggleSelection: () => void;
  toggleExpanded: () => void;
}

export interface LineLibraryRowSlots {
  leading?: (context: LineLibraryRowContext) => ReactNode;
  content?: (context: LineLibraryRowContext) => ReactNode;
  secondary?: (context: LineLibraryRowContext) => ReactNode;
  trailing?: (context: LineLibraryRowContext) => ReactNode;
}

export interface LineLibraryProps
  extends Omit<ComponentPropsWithoutRef<"div">, "children" | "title"> {
  data?: LineLibraryData | null;
  loading?: boolean;
  status?: "loading" | "ready" | "error";
  error?: string | null;
  onRetry?: () => void;
  shell?: "panel" | "embedded";
  title?: ReactNode;
  description?: ReactNode;
  emptyMessage?: ReactNode;
  loadingMessage?: ReactNode;
  ariaLabel?: string;
  selectionMode?: LineLibrarySelectionMode;
  selectedIds?: readonly string[];
  defaultSelectedIds?: readonly string[];
  onSelectionChange?: (
    selectedIds: readonly string[],
    details: LineLibrarySelectionChangeDetails,
  ) => void;
  expandedIds?: readonly string[];
  defaultExpandedIds?: readonly string[];
  focusedId?: string | null;
  defaultFocusedId?: string | null;
  visibleNodeIds?: readonly string[];
  filterValues?: LineLibraryFilterValues;
  defaultFilterValues?: LineLibraryFilterValues;
  filterApplyMode?: LineLibraryFilterApplyMode;
  onFiltersChange?: (filters: LineLibraryFilterValues) => void;
  onFilterDraftChange?: (filters: LineLibraryFilterValues) => void;
  onReferenceNavigate?: (referenceId: string, targetId: string, node: LineLibraryNode) => void;
  rowSlots?: LineLibraryRowSlots;
  renderRow?: (context: LineLibraryRowContext) => ReactNode;
  getNodeLabel?: (node: LineLibraryNode) => ReactNode;
  getNodeName?: (node: LineLibraryNode) => string;
  onCommit?: (description: LineLibraryCommitDescription) => void;
  commitLabel?: string;
  onSelectionLimitReached?: (limit: number) => void;
}
