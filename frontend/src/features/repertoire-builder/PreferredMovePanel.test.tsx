import userEvent from "@testing-library/user-event";
import { cleanup, render, screen, within } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it, vi } from "vitest";

import { PREFERRED_MOVE_DATE_UNAVAILABLE } from "./preferredMoveWorkflowState";
import { PreferredMovePanel, type PreferredMovePanelProps } from "./PreferredMovePanel";
import type { RepertoirePositionModel, RepertoireSelectedMoveFact } from "./repertoireWorkflowModel";

afterEach(() => cleanup());

const here = dirname(fileURLToPath(import.meta.url));
const panelCss = readFileSync(join(here, "PreferredMovePanel.module.css"), "utf8");
const SOURCE_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const SELECTED_E4: RepertoireSelectedMoveFact = {
  transition: { parentFEN: SOURCE_FEN, outgoingUCI: "e2e4" },
  san: "e4",
  uci: "e2e4",
};
const SELECTED_D4: RepertoireSelectedMoveFact = {
  transition: { parentFEN: SOURCE_FEN, outgoingUCI: "d2d4" },
  san: "d4",
  uci: "d2d4",
};
const SAVED_FACT = {
  move: { san: "e4", uci: "e2e4" },
  effectiveAt: "2026-08-29T00:00:00.000Z",
  sourceFen: SOURCE_FEN,
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
    selected: null,
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
  return model({ savedPresence: "present", saved: SAVED_FACT, relationship: "saved", ...overrides });
}

function actionLabels(panel: HTMLElement): string[] {
  return within(panel)
    .queryAllByRole("button")
    .map((button) => button.textContent?.trim() ?? "")
    .filter((label) => label === "Matches saved" || label === "Remove" || label.startsWith("Save "));
}

describe("PreferredMovePanel selected-transition composition", () => {
  it.each([
    ["empty", model(), []],
    ["first choice", model({ selected: SELECTED_D4, relationship: "first-choice" }), ["Save d4"]],
    ["saved", savedModel(), ["Remove"]],
    [
      "replacement",
      savedModel({ selected: SELECTED_D4, comparison: "different", relationship: "replacement" }),
      ["Save d4", "Remove"],
    ],
    [
      "matching",
      savedModel({ selected: SELECTED_E4, comparison: "matching", relationship: "matching" }),
      ["Matches saved", "Remove"],
    ],
  ] as const)("renders the %s reading with exact action visibility", (_name, fixture, actions) => {
    render(<PreferredMovePanel {...panelArgs({ model: fixture })} />);

    const panel = screen.getByRole("region", { name: "Preferred move" });
    expect(actionLabels(panel)).toEqual(actions);
    expect(within(panel).getByTestId("saved-move")).toHaveTextContent("Saved");
    expect(within(panel).getByTestId("selected-move")).toHaveTextContent("Selected");
    expect(within(panel).getByRole("region", { name: "Selected move" })).toBeVisible();
  });

  it("does not expose a selected transition or save action at Ply 0", () => {
    render(<PreferredMovePanel {...panelArgs()} />);

    const panel = screen.getByRole("region", { name: "Preferred move" });
    expect(within(panel).getByText("No move selected")).toBeVisible();
    expect(within(panel).getByText("Play a legal move to select the first saved choice.")).toBeVisible();
    expect(within(panel).queryByTestId("preferred-actions")).not.toBeInTheDocument();
  });

  it("keeps the saved choice playable only as an explicit action", async () => {
    const user = userEvent.setup();
    const onPlaySavedMove = vi.fn();
    render(<PreferredMovePanel {...panelArgs({ model: savedModel(), onPlaySavedMove })} />);

    const saved = screen.getByRole("button", {
      name: "Current saved choice: e4; play this move.",
    });
    await user.click(saved);
    expect(onPlaySavedMove).toHaveBeenCalledOnce();
  });

  it("does not make a saved choice actionable on the opponent turn", async () => {
    const user = userEvent.setup();
    const onPlaySavedMove = vi.fn();
    render(<PreferredMovePanel {...panelArgs({ model: savedModel({ ownTurn: false }), onPlaySavedMove })} />);

    const panel = screen.getByRole("region", { name: "Preferred move" });
    expect(within(panel).queryByRole("button", { name: /Current saved choice/ })).not.toBeInTheDocument();
    await user.click(within(panel).getByRole("region", { name: "Current saved choice" }));
    expect(onPlaySavedMove).not.toHaveBeenCalled();
  });

  it("retains the effective-date contract without rendering date UI", () => {
    const onActivate = vi.fn();
    const onDateChange = vi.fn();
    render(
      <PreferredMovePanel
        {...panelArgs({
          model: savedModel({ selected: SELECTED_D4, comparison: "different", relationship: "replacement" }),
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
    expect(within(panel).queryByTestId("effective-date")).not.toBeInTheDocument();
    expect(within(panel).queryByRole("button", { name: /effective date/i })).not.toBeInTheDocument();
    expect(onActivate).not.toHaveBeenCalled();
    expect(onDateChange).not.toHaveBeenCalled();
  });

  it("gates unknown, unsavable, and error conditions", async () => {
    const onRetry = vi.fn();
    render(
      <PreferredMovePanel
        {...panelArgs({
          model: model({ savedPresence: "unknown", relationship: "unknown", saveability: "unknown" }),
          preferredError: "preferred_move_unavailable",
          onRetry,
        })}
      />,
    );
    const errorPanel = screen.getByRole("region", { name: "Preferred move" });
    expect(within(errorPanel).getByRole("alert")).toHaveTextContent(
      "Preferred move data is unavailable. Try again.",
    );
    await userEvent.setup().click(within(errorPanel).getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledOnce();
    expect(within(errorPanel).queryByTestId("preferred-actions")).not.toBeInTheDocument();

    cleanup();
    render(
      <PreferredMovePanel
        {...panelArgs({ model: model({ saveability: "unsavable", selected: SELECTED_D4, relationship: "first-choice" }) })}
      />,
    );
    expect(screen.getByText("This position isn't in your corpus, so it can't be saved yet.")).toBeVisible();
    expect(screen.queryByRole("button", { name: "Save d4" })).not.toBeInTheDocument();
  });

  it("keeps the selected fact visible and disables persistence during a mutation", () => {
    render(
      <PreferredMovePanel
        {...panelArgs({
          model: savedModel({ selected: SELECTED_D4, comparison: "different", relationship: "replacement" }),
          mutation: "save",
        })}
      />,
    );

    const panel = screen.getByRole("region", { name: "Preferred move" });
    expect(within(panel).getByText("d4")).toBeVisible();
    expect(within(panel).getByRole("button", { name: "Save d4" })).toBeDisabled();
    expect(within(panel).getByRole("button", { name: "Remove" })).toBeDisabled();
  });

  it("retains responsive relationship order and accessibility styles", () => {
    render(
      <PreferredMovePanel
        {...panelArgs({
          model: savedModel({ selected: SELECTED_D4, comparison: "different", relationship: "replacement" }),
        })}
      />,
    );

    const panel = screen.getByRole("region", { name: "Preferred move" });
    const savedBox = screen.getByTestId("saved-move");
    const relationship = savedBox.parentElement;
    if (!(relationship instanceof HTMLElement)) throw new Error("The relationship layout is missing.");
    expect(relationship.children).toHaveLength(3);
    expect(relationship.children[2]).toHaveAttribute("data-testid", "selected-move");
    expect(panelCss).toContain("container-name: preferred-move-panel;");
    expect(panelCss).toContain("@container preferred-move-panel (max-width: 40rem)");
    expect(panelCss).toContain("@media (forced-colors: active)");
    expect(panelCss).toContain("overflow-wrap: anywhere;");
  });
});
