import type {
  LineLibraryData,
  LineLibraryFilterDefinition,
  LineLibraryFilterValue,
  LineLibraryFilterValues,
  LineLibraryNode,
  LineLibraryNodeKind,
  LineLibrarySelectionMode,
  LineLibrarySelectionState,
} from "./lineLibraryTypes";

export const LINE_LIBRARY_ROOT_ID = "__line-library-root__";

export type LineLibraryTreeItem =
  | { kind: "root"; id: typeof LINE_LIBRARY_ROOT_ID }
  | LineLibraryNode;

export function isSelectableNode(node: LineLibraryNode): boolean {
  return (
    node.kind !== "reference" &&
    node.disabled !== true &&
    node.selectable !== false &&
    node.selection?.selectable !== false
  );
}

function childrenFor(data: LineLibraryData, id: string): readonly string[] {
  return id === LINE_LIBRARY_ROOT_ID ? data.roots : (data.nodes[id]?.child_ids ?? []);
}

export function getVisibleNodeIds(
  data: LineLibraryData | null,
  visibleNodeIds?: readonly string[],
): Set<string> {
  if (!data) return new Set();
  if (visibleNodeIds) {
    return new Set(visibleNodeIds.filter((id) => Boolean(data.nodes[id])));
  }

  const visible = new Set<string>();
  const visit = (id: string, path: Set<string>) => {
    if (path.has(id) || visible.has(id) || !data.nodes[id]) return;
    visible.add(id);
    const nextPath = new Set(path).add(id);
    for (const childId of data.nodes[id].child_ids) visit(childId, nextPath);
  };
  for (const rootId of data.roots) visit(rootId, new Set());
  return visible;
}

export function getVisibleChildren(
  data: LineLibraryData | null,
  id: string,
  visibleIds: ReadonlySet<string>,
): string[] {
  if (!data) return [];
  return childrenFor(data, id).filter((childId) => visibleIds.has(childId));
}

export function getVisibleDescendantLineIds(
  data: LineLibraryData | null,
  nodeId: string,
  visibleIds: ReadonlySet<string>,
): string[] {
  if (!data) return [];
  const result: string[] = [];
  const visited = new Set<string>();
  const visit = (id: string) => {
    if (visited.has(id) || !visibleIds.has(id)) return;
    visited.add(id);
    const node = data.nodes[id];
    if (!node) return;
    if (node.kind === "line") {
      if (isSelectableNode(node)) result.push(id);
      return;
    }
    for (const childId of node.child_ids) visit(childId);
  };
  for (const childId of childrenFor(data, nodeId)) visit(childId);
  return result;
}

export function getResolvedConcreteIds(
  data: LineLibraryData | null,
  selectedIds: readonly string[],
  visibleIds: ReadonlySet<string>,
): string[] {
  if (!data) return [];
  const resolved = new Set<string>();
  for (const id of selectedIds) {
    const node = data.nodes[id];
    if (!node || !visibleIds.has(id) || !isSelectableNode(node)) continue;
    if (node.kind === "line") {
      resolved.add(id);
    } else if (node.kind === "group") {
      for (const lineId of getVisibleDescendantLineIds(data, id, visibleIds)) {
        resolved.add(lineId);
      }
    }
  }
  return [...resolved];
}

export function getSelectionState(
  data: LineLibraryData | null,
  node: LineLibraryNode,
  selectedIds: ReadonlySet<string>,
  visibleIds: ReadonlySet<string>,
): LineLibrarySelectionState {
  if (node.kind !== "group") return selectedIds.has(node.id) ? "checked" : "unchecked";
  const descendants = getVisibleDescendantLineIds(data, node.id, visibleIds);
  if (descendants.length === 0) return "unchecked";
  const selectedCount = descendants.filter((id) => selectedIds.has(id)).length;
  if (selectedCount === 0) return "unchecked";
  if (selectedCount === descendants.length) return "checked";
  return "indeterminate";
}

export function normalizeSelection(
  data: LineLibraryData | null,
  selectedIds: readonly string[],
  visibleIds: ReadonlySet<string>,
  mode: LineLibrarySelectionMode,
): string[] {
  if (!data) return [];
  const valid = [...new Set(selectedIds)].filter((id) => {
    const node = data.nodes[id];
    return Boolean(node && visibleIds.has(id) && isSelectableNode(node));
  });
  return mode === "single" ? valid.slice(0, 1) : valid;
}

function ancestorGroups(
  data: LineLibraryData,
  lineId: string,
  visibleIds: ReadonlySet<string>,
): string[] {
  const result: string[] = [];
  const visit = (parentId: string, path: Set<string>) => {
    if (path.has(parentId)) return;
    const parent = data.nodes[parentId];
    if (!parent) return;
    for (const childId of parent.child_ids) {
      if (!visibleIds.has(childId)) continue;
      if (childId === lineId) {
        if (parent.kind === "group") result.push(parent.id);
        return;
      }
      const child = data.nodes[childId];
      if (child?.kind === "group") {
        visit(child.id, new Set(path).add(parentId));
        if (result.includes(child.id) && parent.kind === "group") result.push(parent.id);
      }
    }
  };
  for (const rootId of data.roots) visit(rootId, new Set());
  return [...new Set(result)];
}

export function toggleNodeSelection(
  data: LineLibraryData | null,
  node: LineLibraryNode,
  currentIds: readonly string[],
  visibleIds: ReadonlySet<string>,
  mode: LineLibrarySelectionMode,
): string[] {
  if (!data || !isSelectableNode(node) || !visibleIds.has(node.id)) return [...currentIds];
  if (mode === "single") return currentIds.includes(node.id) ? [] : [node.id];

  const current = new Set(currentIds);
  if (node.kind === "group") {
    const descendantIds = getVisibleDescendantLineIds(data, node.id, visibleIds);
    if (descendantIds.length === 0) return [...currentIds];
    const isChecked = descendantIds.every((id) => current.has(id));
    if (isChecked) {
      current.delete(node.id);
      for (const id of descendantIds) current.delete(id);
    } else {
      current.add(node.id);
      for (const id of descendantIds) current.add(id);
    }
    return [...current];
  }

  if (current.has(node.id)) {
    current.delete(node.id);
    for (const groupId of ancestorGroups(data, node.id, visibleIds)) current.delete(groupId);
  } else {
    current.add(node.id);
  }
  return [...current];
}

export function getFilterDefaults(
  definitions: readonly LineLibraryFilterDefinition[],
  supplied: LineLibraryFilterValues | undefined,
): LineLibraryFilterValues {
  const values: Record<string, LineLibraryFilterValue> = {};
  for (const definition of definitions) {
    const fallback = definition.kind === "boolean" ? false : "";
    values[definition.id] = definition.default_value ?? fallback;
  }
  return { ...values, ...supplied };
}

export function selectionLimitAllows(
  data: LineLibraryData | null,
  selectedIds: readonly string[],
  visibleIds: ReadonlySet<string>,
): boolean {
  const limit = data?.selection_limit;
  return limit == null || getResolvedConcreteIds(data, selectedIds, visibleIds).length <= limit;
}

export function getNodeKindLabel(kind: LineLibraryNodeKind): string {
  return kind === "group" ? "Group" : kind === "line" ? "Line" : "Reference";
}
