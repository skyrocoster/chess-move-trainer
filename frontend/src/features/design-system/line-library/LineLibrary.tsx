import {
  hotkeysCoreFeature,
  selectionFeature,
  syncDataLoaderFeature,
  type SetStateFn,
} from "@headless-tree/core";
import { useTree } from "@headless-tree/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Button } from "../Button";
import { LineLibraryFilters } from "./LineLibraryFilters";
import { LineLibraryTree } from "./LineLibraryTree";
import styles from "./LineLibrary.module.css";
import {
  getFilterDefaults,
  getResolvedConcreteIds,
  getVisibleChildren,
  getVisibleNodeIds,
  LINE_LIBRARY_ROOT_ID,
  normalizeSelection,
  selectionLimitAllows,
  toggleNodeSelection,
  type LineLibraryTreeItem,
} from "./lineLibraryUtils";
import type {
  LineLibraryCommitDescription,
  LineLibraryData,
  LineLibraryFilterValue,
  LineLibraryFilterValues,
  LineLibraryNode,
  LineLibraryProps,
  LineLibrarySelectionChangeDetails,
  LineLibrarySelectionDescription,
} from "./lineLibraryTypes";

function sameIds(left: readonly string[], right: readonly string[]): boolean {
  return left.length === right.length && left.every((id, index) => id === right[index]);
}

function nodeName(node: LineLibraryNode, getNodeName?: (node: LineLibraryNode) => string): string {
  return getNodeName?.(node) ?? node.id;
}

function selectionDescription(
  data: LineLibraryData | null,
  selectedIds: readonly string[],
  visibleIds: ReadonlySet<string>,
): LineLibrarySelectionDescription {
  return {
    selectedIds: [...selectedIds],
    selectedGroupIds: selectedIds.filter((id) => data?.nodes[id]?.kind === "group"),
    resolvedConcreteIds: getResolvedConcreteIds(data, selectedIds, visibleIds),
  };
}

export function LineLibrary({
  data = null,
  loading = false,
  status,
  error = null,
  onRetry,
  shell = "panel",
  title = "Line Library",
  description,
  emptyMessage = "No lines match the current result.",
  loadingMessage = "Loading lines…",
  ariaLabel = "Line Library",
  selectionMode = "multiple",
  selectedIds: selectedIdsProp,
  defaultSelectedIds = [],
  onSelectionChange,
  expandedIds: expandedIdsProp,
  defaultExpandedIds,
  focusedId: focusedIdProp,
  defaultFocusedId = null,
  visibleNodeIds,
  filterValues: filterValuesProp,
  defaultFilterValues,
  filterApplyMode: filterApplyModeProp,
  onFiltersChange,
  onFilterDraftChange,
  onReferenceNavigate,
  rowSlots,
  renderRow,
  getNodeLabel = (node) => node.id,
  getNodeName,
  onCommit,
  commitLabel = "Apply selection",
  onSelectionLimitReached,
  className,
  ...rest
}: LineLibraryProps) {
  const [lastSuccessfulData, setLastSuccessfulData] = useState<LineLibraryData | null>(data);
  const [uncontrolledSelectedIds, setUncontrolledSelectedIds] = useState<string[]>([
    ...defaultSelectedIds,
  ]);
  const [uncontrolledExpandedIds, setUncontrolledExpandedIds] = useState<string[]>(() =>
    defaultExpandedIds
      ? [...defaultExpandedIds]
      : (data?.roots.filter((id) => data.nodes[id]?.kind === "group") ?? []),
  );
  const [uncontrolledFocusedId, setUncontrolledFocusedId] = useState<string | null>(
    defaultFocusedId,
  );
  const [uncontrolledFilters, setUncontrolledFilters] = useState<LineLibraryFilterValues>({});
  const [uncontrolledAppliedFilters, setUncontrolledAppliedFilters] =
    useState<LineLibraryFilterValues>({});
  const selectionActionRef = useRef<(id: string) => void>(() => undefined);
  const selectionReasonRef = useRef<LineLibrarySelectionChangeDetails["reason"]>("user");
  const defaultExpansionAppliedRef = useRef(Boolean(defaultExpandedIds || data));

  const statusLoading = loading || status === "loading";
  const hasError = Boolean(error) || status === "error";
  const errorMessage =
    error ?? (status === "error" ? "The Line Library could not be loaded." : null);

  useEffect(() => {
    if (data && !statusLoading && !hasError) setLastSuccessfulData(data);
  }, [data, hasError, statusLoading]);

  useEffect(() => {
    if (
      defaultExpansionAppliedRef.current ||
      !data ||
      data.roots.length === 0 ||
      statusLoading ||
      hasError
    ) {
      return;
    }
    setUncontrolledExpandedIds(data.roots.filter((id) => data.nodes[id]?.kind === "group"));
    defaultExpansionAppliedRef.current = true;
  }, [data, hasError, statusLoading]);

  const renderedData = data ?? lastSuccessfulData;
  const visibleIds = useMemo(
    () => getVisibleNodeIds(renderedData, visibleNodeIds),
    [renderedData, visibleNodeIds],
  );
  const visibleIdsKey = [...visibleIds].join("\u0000");
  const definitions = renderedData?.filters ?? [];
  const filterApplyMode = filterApplyModeProp ?? renderedData?.filter_apply_mode ?? "immediate";
  const initialFilters = useMemo(
    () => getFilterDefaults(definitions, defaultFilterValues),
    [defaultFilterValues, definitions],
  );

  useEffect(() => {
    if (definitions.length === 0) return;
    if (Object.keys(uncontrolledFilters).length === 0) setUncontrolledFilters(initialFilters);
    if (Object.keys(uncontrolledAppliedFilters).length === 0)
      setUncontrolledAppliedFilters(initialFilters);
  }, [definitions.length, initialFilters, uncontrolledAppliedFilters, uncontrolledFilters]);

  useEffect(() => {
    if (filterValuesProp) {
      setUncontrolledFilters({ ...initialFilters, ...filterValuesProp });
      setUncontrolledAppliedFilters({ ...initialFilters, ...filterValuesProp });
    }
  }, [filterValuesProp, initialFilters]);

  const activeFilters = filterValuesProp ?? uncontrolledAppliedFilters;
  const draftFilters = filterValuesProp ?? uncontrolledFilters;
  const selectedSource =
    selectedIdsProp !== undefined ? [...selectedIdsProp] : uncontrolledSelectedIds;
  const selectedIds = useMemo(
    () => normalizeSelection(renderedData, selectedSource, visibleIds, selectionMode),
    [renderedData, selectedSource, selectionMode, visibleIdsKey],
  );
  const expandedIds =
    expandedIdsProp !== undefined ? [...expandedIdsProp] : uncontrolledExpandedIds;
  const focusedId = focusedIdProp !== undefined ? focusedIdProp : uncontrolledFocusedId;
  const selectionDisabled = statusLoading || hasError;

  const commitSelection = useCallback(
    (nextIds: readonly string[], reason: LineLibrarySelectionChangeDetails["reason"]) => {
      const safeIds = normalizeSelection(renderedData, nextIds, visibleIds, selectionMode);
      if (!selectionLimitAllows(renderedData, safeIds, visibleIds)) {
        const limit = renderedData?.selection_limit;
        if (limit != null) onSelectionLimitReached?.(limit);
        return;
      }
      const current =
        selectedIdsProp !== undefined ? [...selectedIdsProp] : uncontrolledSelectedIds;
      if (!sameIds(current, safeIds) && selectedIdsProp === undefined)
        setUncontrolledSelectedIds(safeIds);
      if (!sameIds(current, safeIds) || !sameIds(nextIds, safeIds)) {
        onSelectionChange?.(safeIds, {
          ...selectionDescription(renderedData, safeIds, visibleIds),
          reason,
        });
      }
    },
    [
      onSelectionChange,
      onSelectionLimitReached,
      renderedData,
      selectedIdsProp,
      selectionMode,
      uncontrolledSelectedIds,
      visibleIdsKey,
    ],
  );

  useEffect(() => {
    if (!renderedData || selectionDisabled) return;
    if (!sameIds(selectedSource, selectedIds)) commitSelection(selectedIds, "data");
  }, [commitSelection, renderedData, selectedIds, selectedSource, selectionDisabled]);

  const setTreeSelectedIds: SetStateFn<string[]> = useCallback(
    (next) => {
      const current =
        selectedIdsProp !== undefined ? [...selectedIdsProp] : uncontrolledSelectedIds;
      commitSelection(
        typeof next === "function" ? next(current) : next,
        selectionReasonRef.current,
      );
    },
    [commitSelection, selectedIdsProp, uncontrolledSelectedIds],
  );

  const currentTreeData = renderedData;
  const tree = useTree<LineLibraryTreeItem>({
    rootItemId: LINE_LIBRARY_ROOT_ID,
    dataLoader: {
      getItem: (id) =>
        id === LINE_LIBRARY_ROOT_ID
          ? { id: LINE_LIBRARY_ROOT_ID, kind: "root" }
          : (currentTreeData?.nodes[id] ?? { id, kind: "reference", child_ids: [] }),
      getChildren: (id) => getVisibleChildren(currentTreeData, id, visibleIds),
    },
    features: [syncDataLoaderFeature, selectionFeature, hotkeysCoreFeature],
    state: {
      selectedItems: selectedIds,
      expandedItems: expandedIds,
      focusedItem: focusedId,
    },
    setSelectedItems: setTreeSelectedIds,
    setExpandedItems: (next) => {
      const current =
        expandedIdsProp !== undefined ? [...expandedIdsProp] : uncontrolledExpandedIds;
      const value = typeof next === "function" ? next(current) : next;
      if (expandedIdsProp === undefined) setUncontrolledExpandedIds(value);
    },
    setFocusedItem: (next) => {
      const current = focusedIdProp !== undefined ? focusedIdProp : uncontrolledFocusedId;
      const value = typeof next === "function" ? next(current) : next;
      if (focusedIdProp === undefined) setUncontrolledFocusedId(value);
    },
    isItemFolder: (item) =>
      item.getItemData().kind === "group" || item.getId() === LINE_LIBRARY_ROOT_ID,
    getItemName: (item) => {
      const itemData = item.getItemData();
      return itemData.kind === "root" ? ariaLabel : nodeName(itemData, getNodeName);
    },
    hotkeys: {
      toggleSelectedItem: {
        hotkey: "Space",
        preventDefault: true,
        handler: (_, instance) => selectionActionRef.current(instance.getFocusedItem().getId()),
      },
      customToggleSelectedItem: {
        hotkey: "Control+Space",
        preventDefault: true,
        handler: (_, instance) => selectionActionRef.current(instance.getFocusedItem().getId()),
      },
    },
    ignoreHotkeysOnInputs: true,
  });

  const toggleSelection = useCallback(
    (node: LineLibraryNode) => {
      if (selectionDisabled) return;
      const next = toggleNodeSelection(renderedData, node, selectedIds, visibleIds, selectionMode);
      if (!selectionLimitAllows(renderedData, next, visibleIds)) {
        const limit = renderedData?.selection_limit;
        if (limit != null) onSelectionLimitReached?.(limit);
        return;
      }
      selectionReasonRef.current = "user";
      tree.setSelectedItems(next);
    },
    [commitSelection, renderedData, selectedIds, selectionDisabled, selectionMode, visibleIdsKey],
  );
  selectionActionRef.current = (id) => {
    const node = renderedData?.nodes[id];
    if (node) toggleSelection(node);
  };

  useEffect(() => {
    if (!renderedData) return;
    tree.rebuildTree();
  }, [tree, renderedData, visibleIdsKey]);

  const onFilterChange = useCallback(
    (id: string, value: LineLibraryFilterValue) => {
      const next = { ...draftFilters, [id]: value };
      setUncontrolledFilters(next);
      onFilterDraftChange?.(next);
      if (filterApplyMode === "immediate") {
        setUncontrolledAppliedFilters(next);
        onFiltersChange?.(next);
      }
    },
    [draftFilters, filterApplyMode, onFilterDraftChange, onFiltersChange],
  );
  const applyFilters = useCallback(() => {
    setUncontrolledAppliedFilters(draftFilters);
    onFiltersChange?.(draftFilters);
  }, [draftFilters, onFiltersChange]);

  const commitDescription: LineLibraryCommitDescription = {
    ...selectionDescription(renderedData, selectedIds, visibleIds),
    filters: activeFilters,
  };
  const visibleRoots = renderedData
    ? getVisibleChildren(renderedData, LINE_LIBRARY_ROOT_ID, visibleIds)
    : [];
  const shellClassName = [
    styles.library,
    shell === "embedded" ? styles.embedded : styles.panel,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      {...rest}
      className={shellClassName}
      aria-busy={statusLoading ? "true" : undefined}
      data-line-library-shell={shell}
      data-stale={renderedData && (statusLoading || hasError) ? "true" : undefined}
    >
      {title || description ? (
        <header className={styles.header}>
          {title ? <h2 className={styles.title}>{title}</h2> : null}
          {description ? <p className={styles.description}>{description}</p> : null}
        </header>
      ) : null}
      <LineLibraryFilters
        definitions={definitions}
        values={draftFilters}
        mode={filterApplyMode}
        onChange={onFilterChange}
        onApply={applyFilters}
        disabled={false}
      />
      {statusLoading && renderedData ? (
        <div className={styles.status} role="status">
          Updating results. Selection is temporarily unavailable.
        </div>
      ) : null}
      {hasError && renderedData ? (
        <div className={styles.error} role="alert">
          <span>{errorMessage}</span>
          {onRetry ? (
            <Button type="button" size="sm" variant="secondary" onClick={onRetry}>
              Retry
            </Button>
          ) : null}
        </div>
      ) : null}
      {!renderedData && statusLoading ? (
        <div className={styles.status} role="status">
          {loadingMessage}
        </div>
      ) : null}
      {!renderedData && hasError ? (
        <div className={styles.error} role="alert">
          <span>{errorMessage}</span>
          {onRetry ? (
            <Button type="button" size="sm" variant="secondary" onClick={onRetry}>
              Retry
            </Button>
          ) : null}
        </div>
      ) : null}
      {renderedData && visibleRoots.length === 0 && !statusLoading && !hasError ? (
        <div className={styles.empty} role="status">
          {emptyMessage}
        </div>
      ) : null}
      {renderedData && visibleRoots.length > 0 ? (
        <LineLibraryTree
          data={renderedData}
          visibleIds={visibleIds}
          tree={tree}
          selectedIds={selectedIds}
          selectionMode={selectionMode}
          selectionDisabled={selectionDisabled}
          getNodeLabel={getNodeLabel}
          getNodeName={getNodeName}
          rowSlots={rowSlots}
          renderRow={renderRow}
          onToggleSelection={toggleSelection}
          onReferenceNavigate={onReferenceNavigate}
        />
      ) : null}
      {onCommit ? (
        <div className={styles.commitBar}>
          <Button
            type="button"
            onClick={() => onCommit(commitDescription)}
            disabled={selectionDisabled}
          >
            {commitLabel}
          </Button>
        </div>
      ) : null}
    </div>
  );
}

export type {
  LineLibraryCommitDescription,
  LineLibraryData,
  LineLibraryFilterDefinition,
  LineLibraryFilterValues,
  LineLibraryNode,
  LineLibraryProps,
  LineLibraryRowContext,
  LineLibraryRowSlots,
} from "./lineLibraryTypes";
