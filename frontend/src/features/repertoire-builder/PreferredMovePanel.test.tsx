import userEvent from "@testing-library/user-event";
import { cleanup, render, screen, within } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it, vi } from "vitest";

import { PREFERRED_MOVE_DATE_UNAVAILABLE } from "./preferredMoveWorkflowState";
import { PreferredMovePanel, type PreferredMovePanelProps } from "./PreferredMovePanel";
import type { PositionPickerMoveRecord } from "./positionPickerSession";
import type { RepertoirePositionModel } from "./repertoireWorkflowModel";

afterEach(() => {
  cleanup();
});

const here = dirname(fileURLToPath(import.meta.url));
const panelCss = readFileSync(join(here, "PreferredMovePanel.module.css"), "utf8");

const SOURCE_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const SAVED_MOVE = { san: "e4", uci: "e2e4" };
const SAVED_FACT = {
  move: SAVED_MOVE,
  effectiveAt: "2026-08-29T00:00:00.000Z",
  sourceFen: SOURCE_FEN,
};
const STAGED_MOVE: PositionPickerMoveRecord = {
  sourceSquare: "d2",
  targetSquare: "d4",
  color: "white",
  san: "d4",
  position: { ply: 1, fen: "after-d4", san: "d4" },
};

function model(overrides: Partial<RepertoirePositionModel> = {}): RepertoirePositionModel {
  return {
    sourceFen: SOURCE_FEN,
    bottomColor: "white",
    ownTurn: true,
    personalCount: 0,
    contextMessage: "Never seen as White",
    saveability: "savable",
    savedPresence: "absent",
    saved: null,
    staged: null,
    comparison: "not-applicable",
    relationship: "empty",
    ...overrides,
  };
}

function panelArgs(overrides: Partial<PreferredMovePanelProps> = {}): PreferredMovePanelProps {
  return {
    model: model(),
    date: null,
    mutation: null,
    preferredLoading: false,
    preferredError: null,
    contextLoading: false,
    contextError: null,
    workflowError: null,
    onSave: vi.fn(),
    onPlaySavedMove: vi.fn(),
    onRemove: vi.fn(),
    onRetry: vi.fn(),
    ...overrides,
  };
}

function savedModel(overrides: Partial<RepertoirePositionModel> = {}): RepertoirePositionModel {
  return model({
    savedPresence: "present",
    saved: SAVED_FACT,
    relationship: "saved",
    ...overrides,
  });
}

function stagedFact(move = STAGED_MOVE) {
  return { move, uci: `${move.sourceSquare}${move.targetSquare}${move.promotion ?? ""}` };
}

function relationshipActionLabels(panel: HTMLElement): string[] {
  return within(panel)
    .queryAllByRole("button")
    .map((button) => button.textContent?.trim() ?? "")
    .filter((label) => label === "Matches saved" || label === "Remove" || label.startsWith("Save "));
}

describe("PreferredMovePanel relationship composition", () => {
  it.each([
    ["empty", model(), []],
    [
      "first choice",
      model({
        staged: stagedFact({ ...STAGED_MOVE, san: "e4", targetSquare: "e4" }),
        relationship: "first-choice",
      }),
      ["Save e4"],
    ],
    ["saved", savedModel(), ["Remove"]],
    [
      "replacement",
      savedModel({ staged: stagedFact(), comparison: "different", relationship: "replacement" }),
      ["Save d4", "Remove"],
    ],
    [
      "matching",
      savedModel({
        staged: stagedFact({ ...STAGED_MOVE, sourceSquare: "e2", targetSquare: "e4", san: "e4" }),
        comparison: "matching",
        relationship: "matching",
      }),
      ["Matches saved", "Remove"],
    ],
  ] as const)("renders the %s reading with exact action visibility and order", (name, fixture, actions) => {
    render(<PreferredMovePanel {...panelArgs({ model: fixture })} />);

    const panel = screen.getByRole("region", { name: "Preferred move" });
    expect(relationshipActionLabels(panel)).toEqual(actions);
    const footer = within(panel).queryByTestId("preferred-actions");
    if (actions.length > 0) {
      expect(footer).toBeInTheDocument();
      expect(within(footer as HTMLElement).getAllByRole("button").map((button) => button.textContent?.trim())).toEqual(
        actions,
      );
    } else {
      expect(footer).not.toBeInTheDocument();
    }
    expect(within(panel).getByTestId("saved-move")).toHaveTextContent("Saved");
    expect(within(panel).getByTestId("staged-move")).toHaveTextContent("Staged");
    expect(within(panel).queryByText("Saved:", { exact: true })).not.toBeInTheDocument();
    expect(within(panel).queryByText("Staged:", { exact: true })).not.toBeInTheDocument();
    expect(within(panel).getByTestId("saved-move")).toBeVisible();
    expect(within(panel).getByRole("region", { name: "Staged move" })).toBeVisible();
    expect(within(panel).queryByRole("button", { name: "Add" })).not.toBeInTheDocument();
    expect(within(panel).queryByRole("button", { name: "Edit" })).not.toBeInTheDocument();
  });

  it("retains a populated effective-date contract without rendering date UI", () => {
    const onActivate = vi.fn();
    const onDateChange = vi.fn();

    render(
      <PreferredMovePanel
        {...panelArgs({
          model: savedModel({
            staged: stagedFact(),
            comparison: "different",
            relationship: "replacement",
          }),
          date: new Date("2026-08-29T00:00:00.000Z"),
          onDateChange,
          dateEdit: {
            available: false,
            reason: PREFERRED_MOVE_DATE_UNAVAILABLE,
            onActivate,
            onChange: onDateChange,
          },
        })}
      />,
    );

    const panel = screen.getByRole("region", { name: "Preferred move" });
    expect(within(panel).getByTestId("saved-move")).toHaveTextContent("e2e4");
    expect(within(panel).queryByTestId("effective-date")).not.toBeInTheDocument();
    expect(within(panel).queryByRole("button", { name: /effective date/i })).not.toBeInTheDocument();
    expect(within(panel).queryByText("2026")).not.toBeInTheDocument();
    expect(within(panel).queryByText(PREFERRED_MOVE_DATE_UNAVAILABLE, { exact: true })).not.toBeInTheDocument();
    expect(onActivate).not.toHaveBeenCalled();
    expect(onDateChange).not.toHaveBeenCalled();
    expect(within(panel).queryAllByText(/Stage a legal move/)).toHaveLength(0);

    cleanup();
    render(<PreferredMovePanel {...panelArgs({ model: savedModel() })} />);
    const emptyPanel = screen.getByRole("region", { name: "Preferred move" });
    expect(
      within(emptyPanel).getAllByText("Stage a move to propose replacing e4"),
    ).toHaveLength(1);
    expect(within(emptyPanel).queryAllByText(/Stage a legal move/)).toHaveLength(0);
  });

  it("renders both empty boxes and exactly one first-choice instruction without actions", () => {
    render(<PreferredMovePanel {...panelArgs()} />);

    const panel = screen.getByRole("region", { name: "Preferred move" });
    expect(within(panel).getByText("None yet")).toBeVisible();
    expect(within(panel).getByText("No move staged")).toBeVisible();
    expect(within(panel).getByText("Stage a legal move to propose the first saved choice.")).toBeVisible();
    expect(within(panel).queryAllByText(/Stage a legal move/)).toHaveLength(1);
    expect(within(panel).queryByTestId("preferred-actions")).not.toBeInTheDocument();
  });

  it("makes an assigned saved box a focused pointer, Enter, and Space staging control", async () => {
    const user = userEvent.setup();
    const onPlaySavedMove = vi.fn();
    const onSave = vi.fn();
    const onRemove = vi.fn();
    render(
      <PreferredMovePanel
        {...panelArgs({
          model: savedModel(),
          date: new Date("2026-08-29T00:00:00.000Z"),
          onPlaySavedMove,
          onSave,
          onRemove,
        })}
      />,
    );

    const savedBox = screen.getByRole("button", {
      name: "Current saved choice: e4; play and stage this move.",
    });
    await user.tab();
    expect(savedBox).toHaveFocus();
    await user.keyboard("{Enter}");
    await user.keyboard(" ");
    await user.click(savedBox);

    expect(onPlaySavedMove).toHaveBeenCalledTimes(3);
    expect(onSave).not.toHaveBeenCalled();
    expect(onRemove).not.toHaveBeenCalled();
    expect(savedBox).toHaveAttribute("type", "button");
    expect(savedBox.querySelector("[data-testid=effective-date]")).toBeNull();
  });

  it("does not make the saved box clickable on the opponent turn", async () => {
    const user = userEvent.setup();
    const onPlaySavedMove = vi.fn();
    render(
      <PreferredMovePanel
        {...panelArgs({ model: savedModel({ ownTurn: false }), onPlaySavedMove })}
      />,
    );

    const panel = screen.getByRole("region", { name: "Preferred move" });
    expect(within(panel).getByRole("region", { name: "Current saved choice" })).toBeVisible();
    expect(
      within(panel).queryByRole("button", {
        name: "Current saved choice: e4; play and stage this move.",
      }),
    ).not.toBeInTheDocument();
    expect(relationshipActionLabels(panel)).toEqual([]);
    await user.click(within(panel).getByRole("region", { name: "Current saved choice" }));
    expect(onPlaySavedMove).not.toHaveBeenCalled();
  });

  it("keeps the deferred date contract request-free while rendering no date UI", () => {
    const onActivate = vi.fn();
    const onDateChange = vi.fn();
    const onSave = vi.fn();
    render(
      <PreferredMovePanel
        {...panelArgs({
          model: savedModel(),
          date: new Date("2026-08-29T00:00:00.000Z"),
          onDateChange,
          dateEdit: {
            available: false,
            reason: PREFERRED_MOVE_DATE_UNAVAILABLE,
            onActivate,
            onChange: onDateChange,
          },
          onSave,
        })}
      />,
    );

    expect(screen.queryByRole("button", { name: "Change effective date" })).not.toBeInTheDocument();
    expect(screen.queryByTestId("effective-date")).not.toBeInTheDocument();
    expect(screen.queryByText(PREFERRED_MOVE_DATE_UNAVAILABLE, { exact: true })).not.toBeInTheDocument();
    expect(onActivate).not.toHaveBeenCalled();
    expect(onDateChange).not.toHaveBeenCalled();
    expect(screen.getByTestId("saved-move")).toHaveTextContent("e2e4");
  });

  it("retains the saved fact and restores focus through Remove confirmation", async () => {
    const user = userEvent.setup();
    const onRemove = vi.fn();
    render(<PreferredMovePanel {...panelArgs({ model: savedModel(), onRemove })} />);

    const remove = screen.getByRole("button", { name: "Remove" });
    await user.click(remove);
    const dialog = await screen.findByRole("alertdialog", { name: "Remove preferred move?" });
    expect(screen.getByTestId("saved-move")).toBeVisible();
    await user.click(within(dialog).getByRole("button", { name: "Cancel" }));
    expect(remove).toHaveFocus();
    expect(onRemove).not.toHaveBeenCalled();

    await user.click(remove);
    const openDialog = await screen.findByRole("alertdialog", { name: "Remove preferred move?" });
    await user.click(within(openDialog).getByRole("button", { name: "Remove" }));
    expect(onRemove).toHaveBeenCalledOnce();
    expect(screen.getByRole("button", { name: /Current saved choice: e4/ })).toBeVisible();
  });

  it("gates unknown, unsavable, and error conditions without alternate layouts", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    render(
      <PreferredMovePanel
        {...panelArgs({
          model: model({
            savedPresence: "unknown",
            relationship: "unknown",
            saveability: "unknown",
          }),
          preferredError: "preferred_move_unavailable",
          onRetry,
        })}
      />,
    );
    const errorPanel = screen.getByRole("region", { name: "Preferred move" });
    expect(within(errorPanel).getByRole("alert")).toHaveTextContent(
      "Preferred move data is unavailable. Try again.",
    );
    expect(within(errorPanel).getByRole("button", { name: "Retry" })).toBeVisible();
    await user.click(within(errorPanel).getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledOnce();
    expect(within(errorPanel).queryByText("None yet")).not.toBeInTheDocument();
    expect(within(errorPanel).getByText("Saved choice unavailable.")).toBeVisible();
    expect(within(errorPanel).queryByTestId("preferred-actions")).not.toBeInTheDocument();

    cleanup();
    render(
      <PreferredMovePanel
        {...panelArgs({
          model: model({
            saveability: "unsavable",
            staged: stagedFact(),
            relationship: "first-choice",
          }),
        })}
      />,
    );
    const blockedPanel = screen.getByRole("region", { name: "Preferred move" });
    expect(within(blockedPanel).getByTestId("preferred-status")).toHaveTextContent("Not in Corpus");
    expect(
      within(blockedPanel).getByText(
        "This position isn't in your corpus, so it can't be saved yet.",
      ),
    ).toBeVisible();
    expect(within(blockedPanel).queryByRole("button", { name: "Save" })).not.toBeInTheDocument();
    expect(within(blockedPanel).queryByRole("button", { name: /effective date/i })).not.toBeInTheDocument();
  });

  it("keeps facts visible and disables persistence controls during a mutation", () => {
    render(
      <PreferredMovePanel
        {...panelArgs({
          model: savedModel({
            staged: stagedFact(),
            comparison: "different",
            relationship: "replacement",
          }),
          mutation: "save",
        })}
      />,
    );

    const panel = screen.getByRole("region", { name: "Preferred move" });
    expect(within(panel).getByTestId("core-information")).toHaveTextContent("Saving preferred move...");
    expect(within(panel).getByRole("button", { name: "Save d4" })).toBeDisabled();
    expect(within(panel).queryByRole("button", { name: /effective date/i })).not.toBeInTheDocument();
    expect(within(panel).getByRole("button", { name: "Remove" })).toBeDisabled();
    expect(within(panel).getByRole("button", { name: /Current saved choice: e4/ })).toBeVisible();
    expect(within(panel).getByText("d4")).toBeVisible();
    expect(within(panel).getAllByText("Saving preferred move...", { exact: true })).toHaveLength(1);
  });

  it("keeps an assigned saved move and Remove available when the position is not in corpus", () => {
    render(
      <PreferredMovePanel
        {...panelArgs({
          model: savedModel({
            saveability: "unsavable",
            staged: stagedFact(),
            comparison: "different",
            relationship: "replacement",
          }),
        })}
      />,
    );

    const panel = screen.getByRole("region", { name: "Preferred move" });
    expect(within(panel).getByTestId("preferred-status")).toHaveTextContent("Not in Corpus");
    expect(
      within(panel).getByText("This position isn't in your corpus, so it can't be saved yet."),
    ).toBeVisible();
    expect(within(panel).getByTestId("saved-move")).toHaveTextContent("e4");
    expect(within(panel).getByTestId("staged-move")).toHaveTextContent("d4");
    expect(within(panel).queryByRole("button", { name: "Save" })).not.toBeInTheDocument();
    expect(within(panel).queryByRole("button", { name: /effective date/i })).not.toBeInTheDocument();
    expect(within(panel).getByRole("button", { name: "Remove" })).toBeEnabled();
  });

  it("keeps responsive relationship order and accessibility styles token-backed", () => {
    render(
      <PreferredMovePanel
        {...panelArgs({
          model: savedModel({
            staged: stagedFact(),
            comparison: "different",
            relationship: "replacement",
          }),
        })}
      />,
    );

    const panel = screen.getByRole("region", { name: "Preferred move" });
    const savedBox = screen.getByTestId("saved-move");
    const relationship = savedBox.parentElement;
    if (!(relationship instanceof HTMLElement))
      throw new Error("The relationship layout is missing.");
    expect(relationship.children).toHaveLength(3);
    expect(savedBox).toBe(relationship.children[0]);
    expect(relationship.children[1]).toHaveAttribute("aria-hidden", "true");
    expect(relationship.children[2]).toHaveAttribute("data-testid", "staged-move");
    expect(panelCss).toContain("block-size: 256px;");
    expect(panelCss).toContain("block-size: 360px;");
    expect(panelCss).toContain("block-size: 88px;");
    expect(panelCss).toContain("grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);");
    expect(panelCss).toContain("grid-template-columns: minmax(0, 1fr);");
    expect(panelCss).toContain("container-name: preferred-move-panel;");
    expect(panelCss).toContain("container-type: inline-size;");
    expect(panelCss).toContain("@container preferred-move-panel (max-width: 40rem)");
    expect(panelCss).toContain("justify-content: flex-start;");
    expect(panelCss).toContain("@media (forced-colors: active)");
    expect(panelCss).toContain("@media (prefers-reduced-motion: reduce)");
    expect(panelCss).toContain("overflow-wrap: anywhere;");
    expect(panelCss).toContain("border-radius: 999px;");
    expect(panelCss).toContain("background: var(--cmt-warning-container);");
    expect(panelCss).toContain("background: var(--cmt-success-container);");
    expect(panelCss).toContain("@container preferred-move-panel (max-width: 40rem)");
    expect(panelCss).toContain("flex-direction: column;");
    expect(panelCss).toContain("transform: rotate(90deg);");
    expect(panelCss).toContain(
      "outline: var(--cmt-focus-ring-width) solid var(--cmt-focus-ring-color);",
    );
  });
});
