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
  else await expect(saved).toHaveTextContent("No saved choice yet.");
  if (fixture.staged) await expect(staged).toHaveTextContent(fixture.staged.move.san);
  else await expect(staged).toHaveTextContent("No move staged.");
}

export const EmptyEmpty: Story = {
  name: "Relationship - empty saved and staged boxes",
  args: panelArgs("empty"),
  play: async ({ canvasElement }) => {
    await expectBoxes(canvasElement, "empty");
    const canvas = within(canvasElement);
    await expect(
      canvas.getByText("Stage a legal move to propose the first saved choice."),
    ).toBeVisible();
    await expect(canvas.queryByTestId("preferred-actions")).not.toBeInTheDocument();
  },
};

export const FirstChoice: Story = {
  name: "Relationship - first choice",
  args: panelArgs("first-choice"),
  play: async ({ canvasElement, args }) => {
    await expectBoxes(canvasElement, "first-choice");
    const canvas = within(canvasElement);
    await expect(canvas.getByText("Save e4 as the current saved choice.")).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Save" })).toBeEnabled();
    await expect(canvas.getByRole("button", { name: "Change effective date" })).toBeDisabled();
    await userEvent.click(canvas.getByRole("button", { name: "Save" }));
    await expect(args.onSave).toHaveBeenCalledOnce();
  },
};

export const SavedNoStage: Story = {
  name: "Relationship - saved choice with no staged move",
  args: panelArgs("saved"),
  play: async ({ canvasElement }) => {
    await expectBoxes(canvasElement, "saved");
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("effective-date")).toHaveTextContent("2026-01-01");
    await expect(canvas.getByRole("button", { name: "Change effective date" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeEnabled();
    await expect(canvas.queryByRole("button", { name: "Save" })).not.toBeInTheDocument();
  },
};

export const Replacement: Story = {
  name: "Relationship - differing staged replacement",
  args: panelArgs("replacement"),
  play: async ({ canvasElement }) => {
    await expectBoxes(canvasElement, "replacement");
    const canvas = within(canvasElement);
    await expect(canvas.getByText("Save d4 to replace e4.")).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Save" })).toBeEnabled();
    await expect(canvas.getByRole("button", { name: "Change effective date" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeEnabled();
  },
};

export const Matching: Story = {
  name: "Relationship - staged move matches saved choice",
  args: panelArgs("matching"),
  play: async ({ canvasElement }) => {
    await expectBoxes(canvasElement, "matching");
    const canvas = within(canvasElement);
    await expect(canvas.getByText("e4 is already the current saved choice.")).toBeVisible();
    await expect(canvas.queryByRole("button", { name: "Save" })).not.toBeInTheDocument();
    await expect(canvas.getByRole("button", { name: "Change effective date" })).toBeDisabled();
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
    await expect(
      canvas.getByRole("heading", { name: "What is saved, and what is staged?" }),
    ).toBeVisible();
    await expect(
      canvas.getByText("This position cannot be saved because it is not in the corpus."),
    ).toBeVisible();
    await expect(canvas.queryByRole("button", { name: "Save" })).not.toBeInTheDocument();
    await expect(
      canvas.queryByRole("button", { name: "Change effective date" }),
    ).not.toBeInTheDocument();
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
    await expect(canvas.queryByTestId("preferred-actions")).not.toBeInTheDocument();
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
      canvas.getByRole("heading", { name: "What is saved, and what is staged?" }),
    ).toBeVisible();
    await expect(canvas.getByTestId("preferred-status")).toHaveTextContent(
      "Loading saved choice...",
    );
    await expect(canvas.getByText("Loading position context...")).toBeVisible();
    await expect(canvas.queryByTestId("preferred-actions")).not.toBeInTheDocument();
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
    await expect(canvas.getByRole("status")).toHaveTextContent("Saving preferred move...");
    await expect(canvas.getByRole("button", { name: "Save" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: /play and stage this move/ })).toBeVisible();
    await expect(canvas.getByText("d4")).toBeVisible();
  },
};
