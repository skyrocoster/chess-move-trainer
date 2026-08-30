import "../../../styles/cmt-tokens.css";
import "../../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import type { ReactNode } from "react";

import { LineLibrary } from "./LineLibrary";
import type { LineLibraryData } from "./lineLibraryTypes";

const sampleData: LineLibraryData = {
  roots: ["group-a", "group-b"],
  filters: [
    { id: "query", label: "Search", kind: "search", placeholder: "Find a line" },
    {
      id: "scope",
      label: "Scope",
      kind: "select",
      options: [
        { value: "all", label: "All" },
        { value: "recent", label: "Recent" },
      ],
    },
    { id: "only-selectable", label: "Only selectable", kind: "boolean" },
  ],
  filter_apply_mode: "explicit",
  selection_limit: 2,
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

const meta = {
  title: "Design System/Components/Line Library",
  component: LineLibrary,
  parameters: { layout: "fullscreen" },
  args: {
    data: sampleData,
    defaultExpandedIds: ["group-a", "nested", "group-b"],
    getNodeLabel: (node) => node.id.replace("-", " "),
    getNodeName: (node) => node.id,
    onSelectionChange: fn(),
    onFiltersChange: fn(),
    onReferenceNavigate: fn(),
    onCommit: fn(),
  },
} satisfies Meta<typeof LineLibrary>;

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
      {children}
    </main>
  );
}

export const Default: Story = {
  render: (args) => shell(<LineLibrary {...args} title="Choose lines" />),
};

export const Loading: Story = {
  args: { data: null, loading: true, error: null },
  render: (args) =>
    shell(<LineLibrary {...args} title="Loading library" loadingMessage="Loading lines…" />),
};

export const Empty: Story = {
  args: { data: { roots: [], nodes: {} } },
  render: (args) =>
    shell(
      <LineLibrary
        {...args}
        title="Line Library"
        emptyMessage="No lines match the current result."
      />,
    ),
};

export const ErrorState: Story = {
  args: {
    data: null,
    error: "The Line Library could not be loaded.",
    onRetry: fn(),
  },
  render: (args) => shell(<LineLibrary {...args} title="Line Library" />),
};
