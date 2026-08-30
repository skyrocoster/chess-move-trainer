import { Checkbox } from "@base-ui/react/checkbox";
import type { ItemInstance, TreeInstance } from "@headless-tree/core";
import type { CSSProperties, KeyboardEvent, MouseEvent, ReactNode } from "react";
import styles from "./LineLibrary.module.css";
import {
  getNodeKindLabel,
  getSelectionState,
  getVisibleDescendantLineIds,
  isSelectableNode,
  type LineLibraryTreeItem,
} from "./lineLibraryUtils";
import type {
  LineLibraryData,
  LineLibraryNode,
  LineLibraryProps,
  LineLibraryRowContext,
} from "./lineLibraryTypes";

export interface LineLibraryTreeProps {
  data: LineLibraryData;
  visibleIds: ReadonlySet<string>;
  tree: TreeInstance<LineLibraryTreeItem>;
  selectedIds: readonly string[];
  selectionMode: "single" | "multiple";
  selectionDisabled: boolean;
  getNodeLabel: (node: LineLibraryNode) => ReactNode;
  getNodeName?: (node: LineLibraryNode) => string;
  rowSlots?: LineLibraryProps["rowSlots"];
  renderRow?: LineLibraryProps["renderRow"];
  onToggleSelection: (node: LineLibraryNode) => void;
  onReferenceNavigate?: LineLibraryProps["onReferenceNavigate"];
}

function nodeName(node: LineLibraryNode, getNodeName?: (node: LineLibraryNode) => string): string {
  return getNodeName?.(node) ?? node.id;
}

export function LineLibraryTree({
  data,
  visibleIds,
  tree,
  selectedIds,
  selectionMode,
  selectionDisabled,
  getNodeLabel,
  getNodeName,
  rowSlots,
  renderRow,
  onToggleSelection,
  onReferenceNavigate,
}: LineLibraryTreeProps) {
  const selectedSet = new Set(selectedIds);
  const items = tree.getItems();

  return (
    <div
      {...tree.getContainerProps("Line Library hierarchy")}
      className={styles.tree}
      aria-multiselectable={selectionMode === "multiple" ? "true" : undefined}
    >
      {items.map((item: ItemInstance<LineLibraryTreeItem>) => {
        const node = item.getItemData();
        if (node.kind === "root") return null;

        const label = nodeName(node, getNodeName);
        const selectable = isSelectableNode(node);
        const descendants = getVisibleDescendantLineIds(data, node.id, visibleIds);
        const state = getSelectionState(data, node, selectedSet, visibleIds);
        const headlessProps = item.getProps() as Record<string, unknown>;
        const level = item.getItemMeta().level;
        const rowContext: LineLibraryRowContext = {
          node,
          label,
          level,
          isExpanded: item.isExpanded(),
          isFolder: item.isFolder(),
          isSelected: selectedSet.has(node.id),
          selectionState: state,
          selectable,
          disabled: node.disabled === true,
          visibleDescendantLineIds: descendants,
          referenceTarget: node.reference_target ?? null,
          toggleSelection: () => onToggleSelection(node),
          toggleExpanded: () => (item.isExpanded() ? item.collapse() : item.expand()),
        };
        const rowStyle = { "--line-library-level": level } as CSSProperties;
        const checkboxDisabled =
          selectionDisabled || !selectable || (node.kind === "group" && descendants.length === 0);
        const disabledReason = node.disabled_reason;

        const onRowClick = (event: MouseEvent<HTMLDivElement>) => {
          item.setFocused();
          if (!selectionDisabled && selectable) onToggleSelection(node);
          if (node.kind === "group" && !event.defaultPrevented) rowContext.toggleExpanded();
        };

        const onRowKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
          if (event.key === "Enter") {
            event.preventDefault();
            item.setFocused();
            if (!selectionDisabled && selectable) onToggleSelection(node);
          }
        };

        return (
          <div
            {...headlessProps}
            key={node.id}
            className={styles.treeItem}
            style={rowStyle}
            aria-selected={selectedSet.has(node.id) ? "true" : "false"}
            aria-disabled={
              node.disabled === true ||
              selectionDisabled ||
              (node.kind === "group" && descendants.length === 0)
                ? "true"
                : undefined
            }
            data-node-id={node.id}
            data-node-kind={node.kind}
            data-selection-state={state}
            onClick={onRowClick}
            onKeyDown={onRowKeyDown}
          >
            <span className={styles.row}>
              <span className={styles.disclosure} aria-hidden="true">
                {node.kind === "group" ? (item.isExpanded() ? "▾" : "▸") : ""}
              </span>
              {selectable ? (
                <Checkbox.Root
                  className={styles.checkbox}
                  checked={state === "checked"}
                  indeterminate={state === "indeterminate"}
                  disabled={checkboxDisabled}
                  aria-label={`Select ${label}`}
                  onClick={(event) => event.stopPropagation()}
                  onCheckedChange={() => onToggleSelection(node)}
                >
                  <Checkbox.Indicator className={styles.checkboxIndicator}>✓</Checkbox.Indicator>
                </Checkbox.Root>
              ) : null}
              {rowSlots?.leading?.(rowContext)}
              <span className={styles.rowContent}>
                {renderRow ? (
                  renderRow(rowContext)
                ) : (
                  <>
                    <span className={styles.primaryLabel}>
                      {rowSlots?.content?.(rowContext) ?? getNodeLabel(node)}
                    </span>
                    <span className={styles.kindLabel}>{getNodeKindLabel(node.kind)}</span>
                    {rowSlots?.secondary?.(rowContext)}
                  </>
                )}
                {disabledReason ? (
                  <span className={styles.disabledReason}>{disabledReason}</span>
                ) : null}
              </span>
              {node.kind === "reference" && node.reference_target ? (
                onReferenceNavigate ? (
                  <button
                    type="button"
                    className={styles.referenceButton}
                    disabled={selectionDisabled || node.disabled === true}
                    onClick={(event) => {
                      event.stopPropagation();
                      onReferenceNavigate(node.id, node.reference_target!, node);
                    }}
                  >
                    Target: {node.reference_target}
                  </button>
                ) : (
                  <span className={styles.referenceTarget}>Target: {node.reference_target}</span>
                )
              ) : null}
              {rowSlots?.trailing?.(rowContext)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
