import { expect, fn, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { useCallback, useMemo, useState, type ReactNode } from "react";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { LineLibrary, type LineLibraryProps } from "../design-system/line-library/LineLibrary";
import type {
  LineLibraryCommitDescription,
  LineLibraryFilterValues,
  LineLibraryNode,
} from "../design-system/line-library/lineLibraryTypes";
import {
  SYNTHETIC_EMPTY_DATA,
  SYNTHETIC_FIXTURE_NOTICE,
  SYNTHETIC_INITIAL_FILTERS,
  SYNTHETIC_LIMITED_OPENING_RESPONSE,
  SYNTHETIC_OPENING_DATA,
  SYNTHETIC_OPENING_RESPONSE,
  syntheticOpeningDataForFilters,
} from "./openingLineLibraryFixtures";
import type { OpeningLineLibraryResponse } from "./openingsApi";

const meta = {
  title: "Application/Openings/Opening Line Library",
  component: LineLibrary,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof LineLibrary>;

export default meta;
type Story = StoryObj<typeof meta>;

function frame(children: ReactNode) {
  return (
    <main
      style={{
        minBlockSize: "100vh",
        padding: "var(--cmt-spacing-32)",
        background: "var(--md-sys-color-background)",
        color: "var(--md-sys-color-on-background)",
      }}
    >
      <div style={{ maxInlineSize: "58rem", marginInline: "auto" }}>{children}</div>
    </main>
  );
}

function nodeName(node: LineLibraryNode): string {
  return typeof node.metadata?.name === "string" ? node.metadata.name : node.id;
}

const openingRowSlots: LineLibraryProps["rowSlots"] = {
  leading: ({ node }) => (
    <span aria-hidden="true" style={{ color: "var(--md-sys-color-primary)" }}>
      {node.kind === "group" ? "◇" : node.kind === "reference" ? "↪" : "•"}
    </span>
  ),
  content: ({ label }) => <span>{label}</span>,
  secondary: ({ node }) => {
    const eco = node.metadata?.eco;
    const moves = node.metadata?.move_sequence;
    return node.kind === "reference" ? (
      <span>synthetic pointer; canonical target remains selectable</span>
    ) : (
      <span>
        {typeof eco === "string" ? eco : "Synthetic family"}
        {typeof moves === "string" && moves ? ` · ${moves}` : ""}
      </span>
    );
  },
  trailing: ({ node }) =>
    node.disabled ? (
      <span>synthetic disabled state</span>
    ) : node.kind === "line" ? (
      <span>opening line</span>
    ) : null,
};

interface SyntheticOpeningBrowserProps {
  response?: OpeningLineLibraryResponse;
  initialFilters?: LineLibraryFilterValues;
  onCommit?: (description: LineLibraryCommitDescription) => void;
  onSelectionLimitReached?: (limit: number) => void;
  title?: ReactNode;
  description?: ReactNode;
  shell?: LineLibraryProps["shell"];
}

function SyntheticOpeningBrowser({
  response = SYNTHETIC_OPENING_RESPONSE,
  initialFilters = SYNTHETIC_INITIAL_FILTERS,
  onCommit,
  onSelectionLimitReached,
  title = "Synthetic opening picker",
  description = SYNTHETIC_FIXTURE_NOTICE,
  shell = "panel",
}: SyntheticOpeningBrowserProps) {
  const [filters, setFilters] = useState<LineLibraryFilterValues>(initialFilters);
  const data = useMemo(
    () => syntheticOpeningDataForFilters(filters, response),
    [filters, response],
  );
  const handleFiltersChange = useCallback((next: LineLibraryFilterValues) => setFilters(next), []);

  return frame(
    <LineLibrary
      data={data}
      shell={shell}
      title={title}
      description={description}
      ariaLabel="Synthetic opening Line Library"
      defaultExpandedIds={[
        "synthetic-opening-root",
        "synthetic-opening-family",
        "synthetic-deep-opening-branch",
      ]}
      filterValues={filters}
      onFiltersChange={handleFiltersChange}
      rowSlots={openingRowSlots}
      getNodeName={nodeName}
      getNodeLabel={nodeName}
      onReferenceNavigate={() => undefined}
      onCommit={onCommit}
      onSelectionLimitReached={onSelectionLimitReached}
    />,
  );
}

export const BrowserSelectionAndCommit: Story = {
  name: "Synthetic hierarchy, keyboard selection, and generic commit",
  args: { onCommit: fn() },
  render: (args) => <SyntheticOpeningBrowser onCommit={args.onCommit} />,
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const sicilian = canvas.getByRole("treeitem", { name: /Synthetic Sicilian branch/ });
    sicilian.focus();
    await userEvent.keyboard("{Enter}");
    await expect(
      canvas.getByRole("checkbox", { name: /Select Synthetic Sicilian branch/ }),
    ).toBeChecked();
    await userEvent.click(canvas.getByRole("button", { name: "Apply selection" }));
    await expect(args.onCommit).toHaveBeenCalledWith(
      expect.objectContaining({ resolvedConcreteIds: ["synthetic-line-sicilian"] }),
    );
  },
};

export const TextSearchScenario: Story = {
  name: "Approved filter - text search",
  render: () => <SyntheticOpeningBrowser />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.type(canvas.getByRole("searchbox", { name: "Search" }), "Caro");
    await expect(
      canvas.getByRole("treeitem", { name: /Synthetic Caro-Kann branch/ }),
    ).toBeVisible();
    await expect(
      canvas.queryByRole("treeitem", { name: /Synthetic Sicilian branch/ }),
    ).not.toBeInTheDocument();
    await expect(
      canvas.queryByRole("treeitem", { name: /Synthetic English branch/ }),
    ).not.toBeInTheDocument();
  },
};

export const EcoRangeScenario: Story = {
  name: "Approved filter - ECO code/range",
  render: () => <SyntheticOpeningBrowser />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const eco = canvas.getByRole("textbox", { name: "ECO code/range" });
    await userEvent.type(eco, "B00:B99");
    await expect(canvas.getByRole("treeitem", { name: /Synthetic Sicilian branch/ })).toBeVisible();
    await expect(
      canvas.getByRole("treeitem", { name: /Synthetic Caro-Kann branch/ }),
    ).toBeVisible();
    await expect(
      canvas.queryByRole("treeitem", { name: /Synthetic English branch/ }),
    ).not.toBeInTheDocument();
  },
};

export const AcceptedCorpusScenario: Story = {
  name: "Approved filter - appears in my games (fixed accepted corpus simulation)",
  render: () => (
    <SyntheticOpeningBrowser
      description={`${SYNTHETIC_FIXTURE_NOTICE} The checkbox simulates the fixed accepted corpus selected by SUBJECT_PLAYER_UUID; it is not an authenticated user lookup.`}
    />
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("checkbox", { name: "Appears in my games" }));
    await expect(canvas.getByRole("treeitem", { name: /Synthetic Sicilian branch/ })).toBeVisible();
    await expect(
      canvas.getByRole("treeitem", { name: /Synthetic Caro-Kann branch/ }),
    ).toBeVisible();
    await expect(
      canvas.queryByRole("treeitem", { name: /Synthetic English branch/ }),
    ).not.toBeInTheDocument();
  },
};

export const DisabledAndTranspositionReference: Story = {
  name: "Synthetic disabled row and non-selectable transposition reference",
  render: () => <SyntheticOpeningBrowser />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("Synthetic fixture: unavailable in this result")).toBeVisible();
    await expect(
      canvas.getByRole("treeitem", { name: /Synthetic unavailable branch/ }),
    ).toHaveAttribute("aria-disabled", "true");
    await expect(
      canvas.queryByRole("checkbox", { name: /Select Synthetic transposition reference/ }),
    ).not.toBeInTheDocument();
    await expect(
      canvas.getByRole("button", { name: "Target: synthetic-line-sicilian" }),
    ).toBeVisible();
  },
};

export const DeclaredSyntheticSelectionLimit: Story = {
  name: "Synthetic backend-declared selection limit",
  args: { onSelectionLimitReached: fn() },
  render: (args) => (
    <SyntheticOpeningBrowser
      response={SYNTHETIC_LIMITED_OPENING_RESPONSE}
      onSelectionLimitReached={args.onSelectionLimitReached}
    />
  ),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(
      canvas.getByRole("checkbox", { name: /Select Synthetic central family/ }),
    );
    await expect(args.onSelectionLimitReached).toHaveBeenCalledWith(1);
    await expect(
      canvas.getByRole("checkbox", { name: /Select Synthetic Sicilian branch/ }),
    ).not.toBeChecked();
  },
};

export const InitialLoading: Story = {
  name: "Synthetic provider loading before first result",
  render: () =>
    frame(
      <LineLibrary
        data={null}
        loading
        title="Synthetic opening picker"
        description={SYNTHETIC_FIXTURE_NOTICE}
        ariaLabel="Synthetic opening Line Library"
      />,
    ),
  play: async ({ canvasElement }) => {
    await expect(within(canvasElement).getByRole("status")).toHaveTextContent("Loading lines");
  },
};

export const StaleRefresh: Story = {
  name: "Synthetic provider stale refresh",
  render: () =>
    frame(
      <LineLibrary
        data={SYNTHETIC_OPENING_DATA}
        loading
        title="Synthetic opening picker"
        description={SYNTHETIC_FIXTURE_NOTICE}
        defaultExpandedIds={[
          "synthetic-opening-root",
          "synthetic-opening-family",
          "synthetic-deep-opening-branch",
        ]}
        rowSlots={openingRowSlots}
        getNodeName={nodeName}
        getNodeLabel={nodeName}
      />,
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("status")).toHaveTextContent("Updating results");
    await expect(
      canvas.getByRole("treeitem", { name: /Synthetic Sicilian branch/ }),
    ).toHaveAttribute("aria-disabled", "true");
  },
};

export const FailureAndRetry: Story = {
  name: "Synthetic provider failure with retry",
  args: { onRetry: fn() },
  render: (args) => <FailureFixture onRetry={args.onRetry} />,
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("alert")).toHaveTextContent(
      "Synthetic provider failed during refresh",
    );
    await userEvent.click(canvas.getByRole("button", { name: "Retry" }));
    await expect(args.onRetry).toHaveBeenCalledOnce();
    await expect(canvas.queryByRole("alert")).not.toBeInTheDocument();
    await expect(canvas.getByRole("treeitem", { name: /Synthetic Sicilian branch/ })).toBeVisible();
  },
};

function FailureFixture({ onRetry }: { onRetry?: () => void }) {
  const [failed, setFailed] = useState(true);
  return frame(
    <LineLibrary
      data={SYNTHETIC_OPENING_DATA}
      error={failed ? "Synthetic provider failed during refresh" : null}
      onRetry={() => {
        setFailed(false);
        onRetry?.();
      }}
      title="Synthetic opening picker"
      description={SYNTHETIC_FIXTURE_NOTICE}
      defaultExpandedIds={[
        "synthetic-opening-root",
        "synthetic-opening-family",
        "synthetic-deep-opening-branch",
      ]}
      rowSlots={openingRowSlots}
      getNodeName={nodeName}
      getNodeLabel={nodeName}
    />,
  );
}

export const EmptyResult: Story = {
  name: "Synthetic provider empty result",
  render: () =>
    frame(
      <LineLibrary
        data={SYNTHETIC_EMPTY_DATA}
        title="Synthetic opening picker"
        description={SYNTHETIC_FIXTURE_NOTICE}
        ariaLabel="Synthetic opening Line Library"
      />,
    ),
  play: async ({ canvasElement }) => {
    await expect(within(canvasElement).getByRole("status")).toHaveTextContent("No lines match");
  },
};
