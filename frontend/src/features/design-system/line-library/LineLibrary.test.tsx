import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { LineLibrary } from "./LineLibrary";
import type { LineLibraryData } from "./lineLibraryTypes";

afterEach(() => cleanup());

if (typeof window !== "undefined" && !("PointerEvent" in window)) {
  Object.defineProperty(window, "PointerEvent", { value: globalThis.MouseEvent });
}

const data: LineLibraryData = {
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

const renderLibrary = (props: Partial<React.ComponentProps<typeof LineLibrary>> = {}) =>
  render(
    <LineLibrary
      data={data}
      defaultExpandedIds={["group-a", "nested", "group-b"]}
      getNodeLabel={(node) => node.id.replace("-", " ")}
      getNodeName={(node) => node.id}
      {...props}
    />,
  );

describe("LineLibrary", () => {
  it("renders a configurable panel, structured slots, and Headless Tree hierarchy", () => {
    renderLibrary({
      shell: "embedded",
      title: "Choose lines",
      rowSlots: { leading: ({ node }) => <span data-testid={`slot-${node.id}`}>slot</span> },
    });

    expect(screen.getByRole("heading", { name: "Choose lines" })).toBeVisible();
    expect(screen.getByRole("tree")).toHaveAttribute("aria-multiselectable", "true");
    expect(screen.getByRole("treeitem", { name: "group-a" })).toBeVisible();
    expect(screen.getByRole("treeitem", { name: "line-2" })).toBeVisible();
    expect(screen.getByTestId("slot-line-1")).toBeVisible();
    expect(screen.getByTestId("slot-reference-1")).toBeVisible();
    expect(screen.getByTestId("slot-group-a").closest("[data-line-library-shell]")).toHaveAttribute(
      "data-line-library-shell",
      "embedded",
    );
  });

  it("selects groups through visible eligible descendants and reports a generic commit", async () => {
    const user = userEvent.setup();
    const onCommit = vi.fn();
    renderLibrary({ onCommit });

    await user.click(screen.getByRole("checkbox", { name: "Select group-a" }));
    expect(screen.getByRole("checkbox", { name: "Select group-a" })).toBeChecked();
    expect(screen.getByRole("checkbox", { name: "Select line-1" })).toBeChecked();
    expect(screen.getByRole("checkbox", { name: "Select line-2" })).toBeChecked();
    expect(screen.queryByRole("checkbox", { name: "Select reference-1" })).toBeNull();
    expect(screen.getByText("Unavailable in this result")).toBeVisible();

    await user.click(screen.getByRole("button", { name: "Apply selection" }));
    expect(onCommit).toHaveBeenCalledWith({
      selectedIds: ["group-a", "line-1", "line-2"],
      selectedGroupIds: ["group-a"],
      resolvedConcreteIds: ["line-1", "line-2"],
      filters: { query: "", scope: "" },
    });
  });

  it("shows tri-state groups, refuses disabled/reference selection, and navigates references", async () => {
    const user = userEvent.setup();
    const onNavigate = vi.fn();
    renderLibrary({ onReferenceNavigate: onNavigate });

    await user.click(screen.getByRole("checkbox", { name: "Select line-1" }));
    expect(screen.getByRole("checkbox", { name: "Select group-a" })).toHaveAttribute(
      "data-indeterminate",
    );
    expect(screen.getByRole("treeitem", { name: "disabled-1" })).toHaveAttribute(
      "aria-disabled",
      "true",
    );

    await user.click(screen.getByRole("button", { name: "Target: line-1" }));
    expect(onNavigate).toHaveBeenCalledWith("reference-1", "line-1", data.nodes["reference-1"]);
  });

  it("enforces the declared concrete selection maximum without truncating a group", async () => {
    const user = userEvent.setup();
    const onLimit = vi.fn();
    renderLibrary({ onSelectionLimitReached: onLimit });

    await user.click(screen.getByRole("checkbox", { name: "Select group-a" }));
    await user.click(screen.getByRole("checkbox", { name: "Select line-3" }));

    expect(screen.getByRole("checkbox", { name: "Select line-3" })).not.toBeChecked();
    expect(onLimit).toHaveBeenCalledWith(2);
  });

  it("recomputes selection when the visible result removes leaves", async () => {
    const user = userEvent.setup();
    const onSelectionChange = vi.fn();
    const { rerender } = renderLibrary({
      selectedIds: ["group-a", "line-1", "line-2"],
      onSelectionChange,
    });

    rerender(
      <LineLibrary
        data={data}
        visibleNodeIds={["group-a", "line-1"]}
        defaultExpandedIds={["group-a"]}
        selectedIds={["group-a", "line-1", "line-2"]}
        onSelectionChange={onSelectionChange}
        getNodeName={(node) => node.id}
      />,
    );

    await waitFor(() =>
      expect(onSelectionChange).toHaveBeenCalledWith(
        ["group-a", "line-1"],
        expect.objectContaining({
          reason: "data",
          selectedGroupIds: ["group-a"],
          resolvedConcreteIds: ["line-1"],
        }),
      ),
    );
    expect(screen.queryByRole("treeitem", { name: "line-2" })).toBeNull();
    void user;
  });

  it("keeps the last successful tree while loading or failed and disables selection", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    const { rerender } = renderLibrary({ onRetry });

    rerender(<LineLibrary data={null} loading error="Refresh failed" onRetry={onRetry} />);
    expect(screen.getByRole("treeitem", { name: "group-a" })).toBeVisible();
    expect(screen.getByRole("alert")).toHaveTextContent("Refresh failed");
    expect(screen.getByRole("treeitem", { name: "line-1" })).toHaveAttribute(
      "aria-disabled",
      "true",
    );
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("supports explicit filter submission and controlled selection", async () => {
    const user = userEvent.setup();
    const onFiltersChange = vi.fn();
    const { rerender } = renderLibrary({ onFiltersChange });

    await user.type(screen.getByRole("searchbox", { name: "Search" }), "queen");
    expect(onFiltersChange).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Apply filters" }));
    expect(onFiltersChange).toHaveBeenLastCalledWith({ query: "queen", scope: "" });

    const onSelectionChange = vi.fn();
    rerender(
      <LineLibrary
        data={data}
        defaultExpandedIds={["group-a"]}
        selectedIds={[]}
        onSelectionChange={onSelectionChange}
        getNodeName={(node) => node.id}
      />,
    );
    await user.click(screen.getByRole("checkbox", { name: "Select line-1" }));
    expect(onSelectionChange).toHaveBeenCalledWith(
      ["line-1"],
      expect.objectContaining({ resolvedConcreteIds: ["line-1"] }),
    );
  });

  it("provides initial loading and empty states and keeps tree keyboard focus", async () => {
    const user = userEvent.setup();
    const { rerender } = render(<LineLibrary loading title="Loading library" />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading lines");

    rerender(<LineLibrary data={{ roots: [], nodes: {} }} />);
    expect(screen.getByRole("status")).toHaveTextContent("No lines match");

    rerender(
      <LineLibrary data={data} defaultExpandedIds={["group-a"]} getNodeName={(node) => node.id} />,
    );
    const first = screen.getByRole("treeitem", { name: "group-a" });
    const second = screen.getByRole("treeitem", { name: "line-1" });
    first.focus();
    await user.keyboard("{ArrowDown}");
    await waitFor(() => expect(second).toHaveFocus());
    fireEvent.keyDown(second, { key: "Enter", code: "Enter" });
    expect(screen.getByRole("checkbox", { name: "Select line-1" })).toBeChecked();
  });
});
