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
const primitiveCss = readFileSync(join(here, "PreferredMovePrimitives.module.css"), "utf8");

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
    .filter((label) => ["Save", "Change effective date", "Remove"].includes(label));
}

describe("PreferredMovePanel relationship composition", () => {
  it.each([
    ["empty", model(), [], []],
    [
      "first choice",
      model({
        staged: stagedFact({ ...STAGED_MOVE, san: "e4", targetSquare: "e4" }),
        relationship: "first-choice",
      }),
      ["Save", "Change effective date"],
      ["Save e4 as the current saved choice."],
    ],
    ["saved", savedModel(), ["Change effective date", "Remove"], []],
    [
      "replacement",
      savedModel({ staged: stagedFact(), comparison: "different", relationship: "replacement" }),
      ["Save", "Change effective date", "Remove"],
      ["Save d4 to replace e4."],
    ],
    [
      "matching",
      savedModel({
        staged: stagedFact({ ...STAGED_MOVE, sourceSquare: "e2", targetSquare: "e4", san: "e4" }),
        comparison: "matching",
        relationship: "matching",
      }),
      ["Change effective date", "Remove"],
      ["e4 is already the current saved choice."],
    ],
  ] as const)(
    "renders the %s reading with exact action visibility and order",
    (name, fixture, actions, consequences) => {
      render(<PreferredMovePanel {...panelArgs({ model: fixture })} />);

      const panel = screen.getByRole("region", { name: "What is saved, and what is staged?" });
      expect(relationshipActionLabels(panel)).toEqual(actions);
      expect(within(panel).getByText("Current saved choice", { exact: true })).toBeVisible();
      expect(within(panel).getByText("Staged move", { exact: true })).toBeVisible();
      expect(
        within(panel).queryByText("Current saved choice:", { exact: true }),
      ).not.toBeInTheDocument();
      expect(within(panel).queryByText("Staged move:", { exact: true })).not.toBeInTheDocument();
      expect(panel.querySelectorAll('[data-testid="preferred-consequence"]')).toHaveLength(
        consequences.length,
      );
      consequences.forEach((text) => expect(within(panel).getByText(text)).toBeVisible());
      expect(within(panel).getByTestId("saved-move")).toBeVisible();
      expect(within(panel).getByRole("region", { name: "Staged move" })).toBeVisible();
      expect(within(panel).queryByRole("button", { name: "Add" })).not.toBeInTheDocument();
      expect(within(panel).queryByRole("button", { name: "Edit" })).not.toBeInTheDocument();
    },
  );

  it("keeps one confirmed date, one consequence, and one empty staged explanation", () => {
    render(
      <PreferredMovePanel
        {...panelArgs({
          model: savedModel({
            staged: stagedFact(),
            comparison: "different",
            relationship: "replacement",
          }),
          date: new Date("2026-08-29T00:00:00.000Z"),
        })}
      />,
    );

    const panel = screen.getByRole("region", { name: "What is saved, and what is staged?" });
    expect(within(panel).getAllByTestId("effective-date")).toHaveLength(1);
    expect(within(panel).getByTestId("effective-date")).toHaveTextContent("2026-08-29");
    expect(within(panel).getAllByTestId("preferred-consequence")).toHaveLength(1);
    expect(within(panel).queryAllByText(/Stage a legal move/)).toHaveLength(0);

    cleanup();
    render(<PreferredMovePanel {...panelArgs({ model: savedModel() })} />);
    const emptyPanel = screen.getByRole("region", { name: "What is saved, and what is staged?" });
    expect(
      within(emptyPanel).getAllByText("Stage a legal move to propose replacing e4."),
    ).toHaveLength(1);
    expect(within(emptyPanel).queryAllByText(/Stage a legal move/)).toHaveLength(1);
    expect(within(emptyPanel).queryByTestId("preferred-consequence")).not.toBeInTheDocument();
  });

  it("renders both empty boxes and exactly one first-choice instruction without actions", () => {
    render(<PreferredMovePanel {...panelArgs()} />);

    const panel = screen.getByRole("region", { name: "What is saved, and what is staged?" });
    expect(within(panel).getByText("No saved choice yet.")).toBeVisible();
    expect(within(panel).getByText("No move staged.")).toBeVisible();
    expect(
      within(panel).getByText("Stage a legal move to propose the first saved choice."),
    ).toBeVisible();
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
    expect(savedBox.querySelector("[data-testid=effective-date]")).not.toBeNull();
  });

  it("does not make the saved box clickable on the opponent turn", async () => {
    const user = userEvent.setup();
    const onPlaySavedMove = vi.fn();
    render(
      <PreferredMovePanel
        {...panelArgs({ model: savedModel({ ownTurn: false }), onPlaySavedMove })}
      />,
    );

    const panel = screen.getByRole("region", { name: "What is saved, and what is staged?" });
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

  it("keeps the deferred date action disabled, described, and request-free", async () => {
    const user = userEvent.setup();
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

    const dateButton = screen.getByRole("button", { name: "Change effective date" });
    expect(dateButton).toBeDisabled();
    expect(dateButton).toHaveAccessibleDescription(PREFERRED_MOVE_DATE_UNAVAILABLE);
    expect(screen.getByText(PREFERRED_MOVE_DATE_UNAVAILABLE, { exact: true })).toBeVisible();
    await user.click(dateButton);
    expect(onActivate).not.toHaveBeenCalled();
    expect(onDateChange).not.toHaveBeenCalled();
    expect(screen.queryByTestId("calendar-date-popup")).not.toBeInTheDocument();
    expect(screen.getByTestId("effective-date")).toHaveTextContent("2026-08-29");
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
    const errorPanel = screen.getByRole("region", { name: "What is saved, and what is staged?" });
    expect(within(errorPanel).getByRole("alert")).toHaveTextContent(
      "Preferred move data is unavailable. Try again.",
    );
    expect(within(errorPanel).getByRole("button", { name: "Retry" })).toBeVisible();
    await user.click(within(errorPanel).getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledOnce();
    expect(within(errorPanel).queryByText("No saved choice yet.")).not.toBeInTheDocument();
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
    const blockedPanel = screen.getByRole("region", { name: "What is saved, and what is staged?" });
    expect(
      within(blockedPanel).getByText(
        "This position cannot be saved because it is not in the corpus.",
      ),
    ).toBeVisible();
    expect(within(blockedPanel).queryByRole("button", { name: "Save" })).not.toBeInTheDocument();
    expect(
      within(blockedPanel).queryByRole("button", { name: "Change effective date" }),
    ).not.toBeInTheDocument();
    expect(within(blockedPanel).queryByTestId("preferred-consequence")).not.toBeInTheDocument();
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

    const panel = screen.getByRole("region", { name: "What is saved, and what is staged?" });
    expect(within(panel).getByRole("status")).toHaveTextContent("Saving preferred move...");
    expect(within(panel).getByRole("button", { name: "Save" })).toBeDisabled();
    expect(within(panel).getByRole("button", { name: "Change effective date" })).toBeDisabled();
    expect(within(panel).getByRole("button", { name: "Remove" })).toBeDisabled();
    expect(within(panel).getByRole("button", { name: /Current saved choice: e4/ })).toBeVisible();
    expect(within(panel).getByText("d4")).toBeVisible();
    expect(within(panel).getAllByText("Saving preferred move...", { exact: true })).toHaveLength(1);
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

    const panel = screen.getByRole("region", { name: "What is saved, and what is staged?" });
    const savedBox = screen.getByTestId("saved-move");
    const relationship = savedBox.parentElement;
    if (!(relationship instanceof HTMLElement))
      throw new Error("The relationship layout is missing.");
    expect(relationship.children).toHaveLength(3);
    expect(savedBox).toBe(relationship.children[0]);
    expect(relationship.children[1]).toHaveAttribute("aria-hidden", "true");
    expect(relationship.children[2]).toHaveAttribute("data-testid", "staged-move");
    const consequenceIcon = within(panel).getByTestId("preferred-consequence").querySelector("svg");
    expect(consequenceIcon).toHaveAttribute("aria-hidden", "true");
    expect(consequenceIcon).toHaveAttribute("focusable", "false");
    expect(panelCss).toContain("grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);");
    expect(panelCss).toContain("grid-template-columns: minmax(0, 1fr);");
    expect(panelCss).toContain("container-name: preferred-move-panel;");
    expect(panelCss).toContain("container-type: inline-size;");
    expect(panelCss).toContain("@container preferred-move-panel (max-width: 40rem)");
    expect(panelCss).toContain("justify-content: flex-start;");
    expect(panelCss).toContain("flex: 1 1 100%;");
    expect(panelCss).toContain("@media (forced-colors: active)");
    expect(panelCss).toContain("@media (prefers-reduced-motion: reduce)");
    expect(primitiveCss).toContain("overflow-wrap: anywhere;");
    expect(primitiveCss).toContain("border-radius: 50%;");
    expect(primitiveCss).toContain("background: var(--cmt-warning-accent);");
    expect(primitiveCss).toContain("background: var(--cmt-success-accent);");
    expect(primitiveCss).toContain("@container preferred-move-panel (max-width: 40rem)");
    expect(primitiveCss).toContain("flex-direction: column;");
    expect(primitiveCss).toContain("transform: rotate(90deg);");
    expect(primitiveCss).toContain(
      "outline: var(--cmt-focus-ring-width) solid var(--cmt-focus-ring-color);",
    );
  });
});
