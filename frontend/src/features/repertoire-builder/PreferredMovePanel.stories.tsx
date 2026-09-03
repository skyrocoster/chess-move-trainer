import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import { PreferredMovePanel, type PreferredMovePanelProps } from "./PreferredMovePanel";
import {
  preferredMoveRelationshipFixtures,
  preferredMoveStoryModel,
  type PreferredMoveRelationship,
} from "./preferredMoveStoryFixtures";

function panelArgs(
  relationship: PreferredMoveRelationship,
  overrides: Partial<PreferredMovePanelProps> = {},
): PreferredMovePanelProps {
  return {
    model: preferredMoveStoryModel(relationship),
    date:
      relationship === "empty" || relationship === "first-choice"
        ? null
        : new Date("2026-01-01T00:00:00.000Z"),
    mutation: null,
    preferredLoading: false,
    preferredError: null,
    contextLoading: false,
    contextError: null,
    workflowError: null,
    onSave: fn(),
    onPlaySavedMove: fn(),
    onRemove: fn(),
    ...overrides,
  };
}

const meta = {
  title: "Application/Repertoire Builder/Preferred Move Panel",
  component: PreferredMovePanel,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof PreferredMovePanel>;

export default meta;
type Story = StoryObj<typeof meta>;

async function expectBoxes(canvasElement: HTMLElement, relationship: PreferredMoveRelationship) {
  const canvas = within(canvasElement);
  const fixture = preferredMoveRelationshipFixtures[relationship];
  const saved = fixture.saved
    ? canvas.getByRole("button", { name: /Current saved choice: e4/ })
    : canvas.getByRole("region", { name: "Current saved choice" });
  const staged = canvas.getByRole("region", { name: "Staged move" });
  await expect(saved).toBeVisible();
  await expect(staged).toBeVisible();
  if (fixture.saved) await expect(saved).toHaveTextContent(fixture.saved.move.san);
  else await expect(saved).toHaveTextContent("None yet");
  if (fixture.staged) await expect(staged).toHaveTextContent(fixture.staged.move.san);
  else if (relationship === "saved") {
    await expect(staged).toHaveTextContent("Stage a move to propose replacing e4");
  } else await expect(staged).toHaveTextContent("No move staged");
}

async function expectPanelDimensions(canvasElement: HTMLElement) {
  const panel = canvasElement.querySelector('section[aria-labelledby="preferred-move-heading"]');
  if (!(panel instanceof HTMLElement)) throw new Error("The preferred move panel is missing.");
  const isNarrow = canvasElement.ownerDocument.defaultView?.matchMedia("(max-width: 40rem)").matches;
  const actions = panel.querySelector('[data-testid="preferred-actions"]');
  const compatibilityShell = actions instanceof HTMLElement && actions.getBoundingClientRect().height > 100;
  const panelHeight = panel.getBoundingClientRect().height;
  if (isNarrow) {
    await expect(panelHeight).toBeGreaterThanOrEqual(360);
  } else {
    await expect(panelHeight).toBe(compatibilityShell ? 325 : 256);
  }
  for (const element of [panel.querySelector('[class*="relationship"]'), actions]) {
    if (element instanceof HTMLElement) {
      await expect(element.getBoundingClientRect().bottom).toBeLessThanOrEqual(
        panel.getBoundingClientRect().bottom,
      );
    }
  }
  await expect(within(panel).getByTestId("saved-move").getBoundingClientRect().height).toBe(88);
  await expect(within(panel).getByTestId("staged-move").getBoundingClientRect().height).toBe(88);
}

async function expectNoPanelOverflow(canvasElement: HTMLElement) {
  const panel = canvasElement.querySelector('section[aria-labelledby="preferred-move-heading"]');
  if (!(panel instanceof HTMLElement)) throw new Error("The preferred move panel is missing.");
  const panelRect = panel.getBoundingClientRect();
  await expect(panel.scrollWidth).toBeLessThanOrEqual(panel.clientWidth);
  await expect(canvasElement.ownerDocument.documentElement.scrollWidth).toBeLessThanOrEqual(
    canvasElement.ownerDocument.documentElement.clientWidth,
  );
  const escaped = [...panel.querySelectorAll<HTMLElement>("*")].filter((element) => {
    if (element.getClientRects().length === 0) return false;
    const rect = element.getBoundingClientRect();
    return (
      rect.left < panelRect.left - 0.5 ||
      rect.right > panelRect.right + 0.5 ||
      rect.top < panelRect.top - 0.5 ||
      rect.bottom > panelRect.bottom + 0.5
    );
  });
  if (escaped.length > 0) {
    throw new Error(
      `Preferred move content escapes its panel: ${escaped
        .map((element) => element.textContent?.trim().replace(/\s+/g, " "))
        .join(" | ")}`,
    );
  }
}

async function expectFooterActions(canvasElement: HTMLElement, actions: readonly string[]) {
  const footer = canvasElement.querySelector('[data-testid="preferred-actions"]');
  if (actions.length === 0) {
    await expect(footer).not.toBeInTheDocument();
    return;
  }
  if (!(footer instanceof HTMLElement)) throw new Error("The preferred move action footer is missing.");
  await expect(
    within(footer)
      .getAllByRole("button")
      .map((button) => button.textContent?.trim() ?? ""),
  ).toEqual(actions);
}

async function expectDateFreePanel(canvasElement: HTMLElement) {
  const panel = canvasElement.querySelector('section[aria-labelledby="preferred-move-heading"]');
  if (!(panel instanceof HTMLElement)) throw new Error("The preferred move panel is missing.");
  const scoped = within(panel);
  await expect(scoped.queryByTestId("effective-date")).not.toBeInTheDocument();
  await expect(scoped.queryByTestId("calendar-date-popup")).not.toBeInTheDocument();
  await expect(scoped.queryByRole("button", { name: /effective date/i })).not.toBeInTheDocument();
  await expect(panel).not.toHaveTextContent(/effective date/i);
  await expect(panel).not.toHaveTextContent(
    /\b\d{4}-\d{2}-\d{2}\b|\b(?:\d{1,2} )?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?: \d{1,2},?)? \d{4}\b/,
  );
}

export const EmptyEmpty: Story = {
  name: "Relationship - empty saved and staged boxes",
  args: panelArgs("empty"),
  play: async ({ canvasElement }) => {
    await expectBoxes(canvasElement, "empty");
    await expectPanelDimensions(canvasElement);
    await expectNoPanelOverflow(canvasElement);
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("status")).toHaveTextContent("Ready to stage");
    await expect(
      canvas.getByText("Stage a legal move to propose the first saved choice."),
    ).toBeVisible();
    await expectFooterActions(canvasElement, []);
    await expectDateFreePanel(canvasElement);
  },
};

export const FirstChoice: Story = {
  name: "Relationship - first choice",
  args: panelArgs("first-choice"),
  play: async ({ canvasElement, args }) => {
    await expectBoxes(canvasElement, "first-choice");
    await expectPanelDimensions(canvasElement);
    await expectNoPanelOverflow(canvasElement);
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("status")).toHaveTextContent("Ready to save");
    await expect(canvas.getByText("Saved", { exact: true })).toBeVisible();
    await expect(canvas.getByText("Staged", { exact: true })).toBeVisible();
    await expectFooterActions(canvasElement, ["Save e4"]);
    await expect(canvas.getByRole("button", { name: "Save e4" })).toBeEnabled();
    await expectDateFreePanel(canvasElement);
    await userEvent.click(canvas.getByRole("button", { name: "Save e4" }));
    await expect(args.onSave).toHaveBeenCalledOnce();
  },
};

export const SavedNoStage: Story = {
  name: "Relationship - saved choice with no staged move",
  args: panelArgs("saved"),
  play: async ({ canvasElement }) => {
    await expectBoxes(canvasElement, "saved");
    await expectPanelDimensions(canvasElement);
    await expectNoPanelOverflow(canvasElement);
    const canvas = within(canvasElement);
    await expectFooterActions(canvasElement, ["Remove"]);
    await expectDateFreePanel(canvasElement);
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeEnabled();
    await expect(canvas.queryByRole("button", { name: /^Save / })).not.toBeInTheDocument();
  },
};

export const Replacement: Story = {
  name: "Relationship - differing staged replacement",
  args: panelArgs("replacement"),
  play: async ({ canvasElement }) => {
    await expectBoxes(canvasElement, "replacement");
    await expectPanelDimensions(canvasElement);
    await expectNoPanelOverflow(canvasElement);
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("status")).toHaveTextContent("Ready to save");
    await expectFooterActions(canvasElement, ["Save d4", "Remove"]);
    await expect(canvas.getByRole("button", { name: "Save d4" })).toBeEnabled();
    await expectDateFreePanel(canvasElement);
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeEnabled();
  },
};

export const Matching: Story = {
  name: "Relationship - staged move matches saved choice",
  args: panelArgs("matching"),
  play: async ({ canvasElement }) => {
    await expectBoxes(canvasElement, "matching");
    await expectPanelDimensions(canvasElement);
    await expectNoPanelOverflow(canvasElement);
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("status")).toHaveTextContent("Already saved");
    await expectFooterActions(canvasElement, ["Matches saved", "Remove"]);
    await expect(canvas.getByRole("button", { name: "Matches saved" })).toBeDisabled();
    await expectDateFreePanel(canvasElement);
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeEnabled();
  },
};

export const UnsavableGate: Story = {
  name: "Gate - unsavable position",
  args: {
    ...panelArgs("first-choice"),
    model: preferredMoveStoryModel("first-choice", { saveability: "unsavable" }),
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("preferred-status")).toHaveTextContent("Not in Corpus");
    await expect(
      canvas.getByRole("heading", { name: "Preferred move" }),
    ).toBeVisible();
    await expect(
      canvas.getByText("This position isn't in your corpus, so it can't be saved yet."),
    ).toBeVisible();
    await expectFooterActions(canvasElement, []);
    await expectNoPanelOverflow(canvasElement);
    await expect(canvas.queryByRole("button", { name: /^Save / })).not.toBeInTheDocument();
    await expectDateFreePanel(canvasElement);
  },
};

export const OpponentTurnGate: Story = {
  name: "Gate - opponent turn keeps the relationship read-only",
  args: { ...panelArgs("saved"), model: preferredMoveStoryModel("saved", { ownTurn: false }) },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getByText("Wait for your turn to stage or save a preferred move."),
    ).toBeVisible();
    await expect(canvas.getByRole("region", { name: "Current saved choice" })).toBeVisible();
    await expect(
      canvas.queryByRole("button", { name: /play and stage this move/ }),
    ).not.toBeInTheDocument();
    await expectFooterActions(canvasElement, []);
    await expectNoPanelOverflow(canvasElement);
    await expectDateFreePanel(canvasElement);
  },
};

export const Loading: Story = {
  name: "Gate - loading keeps the same shell",
  args: {
    ...panelArgs("empty"),
    model: preferredMoveStoryModel("empty", {
      savedPresence: "unknown",
      relationship: "unknown",
      comparison: "unknown",
      saveability: "unknown",
      contextMessage: null,
    }),
    preferredLoading: true,
    contextLoading: true,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getByRole("heading", { name: "Preferred move" }),
    ).toBeVisible();
    await expect(canvas.getByTestId("preferred-status")).toHaveTextContent(
      "Loading saved choice...",
    );
    await expect(canvas.getByText("Loading position context...")).toBeVisible();
    await expectFooterActions(canvasElement, []);
    await expectNoPanelOverflow(canvasElement);
    await expectDateFreePanel(canvasElement);
  },
};

export const ReadError: Story = {
  name: "Gate - typed read errors retain the shell",
  args: {
    ...panelArgs("empty"),
    model: preferredMoveStoryModel("empty", {
      savedPresence: "unknown",
      relationship: "unknown",
      comparison: "unknown",
      saveability: "unknown",
      contextMessage: null,
    }),
    preferredError: "preferred_move_unavailable",
    contextError: "position_context_unavailable",
    onRetry: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getAllByRole("alert")).toHaveLength(2);
    await expect(canvas.getByText("Saved choice unavailable.")).toBeVisible();
    await userEvent.click(canvas.getAllByRole("button", { name: "Retry" })[0]!);
    await expect(args.onRetry).toHaveBeenCalledOnce();
    await expectNoPanelOverflow(canvasElement);
    await expectDateFreePanel(canvasElement);
  },
};

export const MutationPending: Story = {
  name: "Feedback - pending replacement retains both facts",
  args: {
    ...panelArgs("replacement"),
    mutation: "save",
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("core-information")).toHaveTextContent("Saving preferred move...");
    await expectFooterActions(canvasElement, ["Save d4", "Remove"]);
    await expectNoPanelOverflow(canvasElement);
    await expect(canvas.getByRole("button", { name: "Save d4" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeDisabled();
    await expectDateFreePanel(canvasElement);
    await expect(canvas.getByRole("button", { name: /play and stage this move/ })).toBeVisible();
    await expect(canvas.getByText("d4")).toBeVisible();
  },
};

const LONG_CONTEXT =
  "Seen in 6,183 games as White · long corpus metadata retained for responsive overflow review";

function promotionStagedModel(relationship: "first-choice" | "replacement") {
  const base = preferredMoveStoryModel(relationship);
  if (!base.staged) throw new Error("The promotion overflow fixture needs a staged move.");
  return {
    ...base,
    contextMessage: LONG_CONTEXT,
    staged: {
      ...base.staged,
      uci: "e7e8q",
      move: { ...base.staged.move, san: "e8=Q+" },
    },
  };
}

function savedPromotionModel() {
  const base = preferredMoveStoryModel("saved");
  if (!base.saved) throw new Error("The promotion guidance fixture needs a saved move.");
  return {
    ...base,
    contextMessage: LONG_CONTEXT,
    saved: {
      ...base.saved,
      move: { ...base.saved.move, san: "e8=Q+", uci: "e7e8q" },
    },
  };
}

function overflowViewport(width: 640 | 480 | 412) {
  const name = `preferred-move-${width}`;
  return {
    viewport: {
      defaultViewport: name,
      options: {
        [name]: {
          name: `${width}px preferred move overflow review`,
          styles: { width: `${width}px`, height: "900px" },
        },
      },
    },
  };
}

async function expectPromotionOverflowCase(canvasElement: HTMLElement) {
  const canvas = within(canvasElement);
  await expect(canvas.getByTestId("preferred-context")).toHaveTextContent(LONG_CONTEXT);
  await expect(canvas.getByTestId("staged-move")).toHaveTextContent(/^Staged\s*e8=Q\+\s*e7e8q$/);
  await expect(canvas.getByRole("button", { name: "Save e8=Q+" })).toBeEnabled();
  await expectFooterActions(canvasElement, ["Save e8=Q+", "Remove"]);
  await expectNoPanelOverflow(canvasElement);
  await expectDateFreePanel(canvasElement);
}

export const OverflowLongCopyDesktop: Story = {
  name: "Overflow - long metadata and promotion copy at desktop",
  args: {
    ...panelArgs("replacement"),
    model: promotionStagedModel("replacement"),
  },
  play: async ({ canvasElement }) => {
    await expectPromotionOverflowCase(canvasElement);
    const panel = canvasElement.querySelector('section[aria-labelledby="preferred-move-heading"]');
    if (!(panel instanceof HTMLElement)) throw new Error("The preferred move panel is missing.");
    await expect(panel.getBoundingClientRect().height).toBeGreaterThanOrEqual(256);
  },
};

export const OverflowLongCopy640: Story = {
  name: "Overflow - long metadata and promotion copy at 640px",
  parameters: overflowViewport(640),
  args: {
    ...panelArgs("replacement"),
    model: promotionStagedModel("replacement"),
  },
  play: async ({ canvasElement }) => {
    await expectPromotionOverflowCase(canvasElement);
    const panel = canvasElement.querySelector('section[aria-labelledby="preferred-move-heading"]');
    if (!(panel instanceof HTMLElement)) throw new Error("The preferred move panel is missing.");
    await expect(panel.getBoundingClientRect().height).toBeGreaterThanOrEqual(360);
  },
};

export const OverflowLongCopy480: Story = {
  name: "Overflow - long metadata and promotion copy at 480px",
  parameters: overflowViewport(480),
  args: {
    ...panelArgs("replacement"),
    model: promotionStagedModel("replacement"),
  },
  play: async ({ canvasElement }) => {
    await expectPromotionOverflowCase(canvasElement);
    const panel = canvasElement.querySelector('section[aria-labelledby="preferred-move-heading"]');
    if (!(panel instanceof HTMLElement)) throw new Error("The preferred move panel is missing.");
    await expect(panel.getBoundingClientRect().height).toBeGreaterThanOrEqual(360);
  },
};

export const OverflowLongCopy412: Story = {
  name: "Overflow - long metadata and promotion copy at 412px",
  parameters: overflowViewport(412),
  args: {
    ...panelArgs("replacement"),
    model: promotionStagedModel("replacement"),
  },
  play: async ({ canvasElement }) => {
    await expectPromotionOverflowCase(canvasElement);
    const panel = canvasElement.querySelector('section[aria-labelledby="preferred-move-heading"]');
    if (!(panel instanceof HTMLElement)) throw new Error("The preferred move panel is missing.");
    await expect(panel.getBoundingClientRect().height).toBeGreaterThanOrEqual(360);
  },
};

export const OverflowReplacementGuidance: Story = {
  name: "Overflow - long replacement guidance remains visible",
  parameters: overflowViewport(412),
  args: {
    ...panelArgs("saved"),
    model: savedPromotionModel(),
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getByText("Stage a move to propose replacing e8=Q+", { exact: true }),
    ).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeEnabled();
    await expectNoPanelOverflow(canvasElement);
    await expectDateFreePanel(canvasElement);
  },
};
