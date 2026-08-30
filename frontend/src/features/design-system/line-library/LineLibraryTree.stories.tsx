import "../../../styles/cmt-tokens.css";
import "../../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { useState, type ReactNode } from "react";
import {
  hotkeysCoreFeature,
  selectionFeature,
  syncDataLoaderFeature,
  type SetStateFn,
} from "@headless-tree/core";
import { useTree } from "@headless-tree/react";

import { LineLibraryTree } from "./LineLibraryTree";
import type { LineLibraryData, LineLibraryNode } from "./lineLibraryTypes";
import {
  getVisibleChildren,
  getVisibleNodeIds,
  LINE_LIBRARY_ROOT_ID,
  type LineLibraryTreeItem,
} from "./lineLibraryUtils";

const sampleData: LineLibraryData = {
  roots: ["group-a", "group-b"],
  nodes: {
    "group-a": { id: "group-a", kind: "group", child_ids: ["line-1", "nested", "reference-1"] },
    nested: { id: "nested", kind: "group", child_ids: ["line-2", "disabled-1"] },
    "line-1": { id: "line-1", kind: "line", child_ids: [] },
    "line-2": { id: "line-2", kind: "line", child_ids: [] },
    "disabled-1": {
      id: "disabled-1",
      kind: "line",
      child_ids: [],
      disabled: true,
      disabled_reason: "Unavailable in this result",
    },
    "reference-1": {
      id: "reference-1",
      kind: "reference",
      child_ids: [],
      reference_target: "line-1",
    },
    "group-b": { id: "group-b", kind: "group", child_ids: ["line-3"] },
    "line-3": { id: "line-3", kind: "line", child_ids: [] },
  },
};

const DEFAULT_EXPANDED = ["group-a", "nested", "group-b"];

const meta = {
  title: "Design System/Components/Line Library Tree",
  parameters: { layout: "fullscreen" },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

function shell(children: ReactNode) {
  return (
    <main
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "var(--cmt-spacing-24)",
        padding: "var(--cmt-spacing-32)",
        minHeight: "100vh",
        backgroundColor: "var(--md-sys-color-surface)",
        color: "var(--md-sys-color-on-surface)",
        fontFamily: "system-ui",
      }}
    >
      <div style={{ maxInlineSize: "40rem" }}>{children}</div>
    </main>
  );
}

function TreeFixture({ initialSelected = [] }: { initialSelected?: string[] }) {
  const [selectedIds, setSelectedIds] = useState<string[]>(initialSelected);
  const [expandedIds, setExpandedIds] = useState<string[]>(DEFAULT_EXPANDED);
  const visibleIds = getVisibleNodeIds(sampleData, undefined);

  const tree = useTree<LineLibraryTreeItem>({
    rootItemId: LINE_LIBRARY_ROOT_ID,
    dataLoader: {
      getItem: (id) =>
        id === LINE_LIBRARY_ROOT_ID
          ? { id: LINE_LIBRARY_ROOT_ID, kind: "root" }
          : (sampleData.nodes[id] ?? { id, kind: "reference", child_ids: [] }),
      getChildren: (id) => getVisibleChildren(sampleData, id, visibleIds),
    },
    features: [syncDataLoaderFeature, selectionFeature, hotkeysCoreFeature],
    state: {
      selectedItems: selectedIds,
      expandedItems: expandedIds,
      focusedItem: null,
    },
    setSelectedItems: ((next) =>
      setSelectedIds((prev) => (typeof next === "function" ? next(prev) : next))) as SetStateFn<
      string[]
    >,
    setExpandedItems: ((next) =>
      setExpandedIds((prev) => (typeof next === "function" ? next(prev) : next))) as SetStateFn<
      string[]
    >,
    setFocusedItem: () => undefined,
    isItemFolder: (item) =>
      item.getItemData().kind === "group" || item.getId() === LINE_LIBRARY_ROOT_ID,
    getItemName: (item) => {
      const data = item.getItemData();
      return data.kind === "root" ? "Line Library" : data.id;
    },
    ignoreHotkeysOnInputs: true,
  });

  const toggleSelection = (node: LineLibraryNode) => {
    setSelectedIds((prev) =>
      prev.includes(node.id) ? prev.filter((id) => id !== node.id) : [...prev, node.id],
    );
  };

  return (
    <LineLibraryTree
      data={sampleData}
      visibleIds={visibleIds}
      tree={tree}
      selectedIds={selectedIds}
      selectionMode="multiple"
      selectionDisabled={false}
      getNodeLabel={(node) => node.id.replace("-", " ")}
      onToggleSelection={toggleSelection}
      onReferenceNavigate={fn()}
    />
  );
}

export const Default: Story = {
  render: () => shell(<TreeFixture />),
};

export const WithSelection: Story = {
  render: () => shell(<TreeFixture initialSelected={["line-1", "line-2"]} />),
};
