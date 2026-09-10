import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { storyAnalysisClient, storyCandidateAnalysisClient } from "../analysis/analysisStoryClients";
import { GAME_UUID } from "../game/gameFixtures";
import RepertoireBuilderWorkspace from "./RepertoireBuilderWorkspace";
import {
  expectActiveSessionHistoryEntry,
  expectPreferredActions,
  expectPreferredMoveState,
  expectSessionHistory,
} from "./repertoireBuilderStoryAssertions";
import { workspace } from "./repertoireBuilderStoryRender";
import {
  STORY_BLACK_SUBJECT_GAME_DETAIL,
  loadGame,
  storyGameClient,
} from "./repertoireBuilderStoryHelpers";

const meta = {
  title: "Application/Repertoire Builder/Workspace",
  component: RepertoireBuilderWorkspace,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof RepertoireBuilderWorkspace>;

export default meta;
type Story = StoryObj<typeof meta>;

export const ReadErrors: Story = {
  name: "Preferred move - read errors are announced safely",
  render: () =>
    workspace(
      { analysisClient: storyAnalysisClient() },
      { readFailure: "preferred_move_unavailable" },
      { failure: "position_context_unavailable" },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const alerts = await canvas.findAllByRole("alert");
    await expect(alerts).toHaveLength(2);
    for (const alert of alerts) {
      await expect(alert).toHaveRole("alert");
    }
    await expect(alerts[0]).toHaveTextContent("Preferred move data is unavailable. Try again.");
    await expect(alerts[1]).toHaveTextContent("Position context is temporarily unavailable.");
    await expect(canvas.queryByRole("button", { name: "Save" })).not.toBeInTheDocument();
  },
};

export const UnsavableGate: Story = {
  name: "Preferred move - unsavable position remains in the same shell",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { relationship: "empty" },
      { observedInGames: false },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "empty");
    await expect(
      canvas.getByText("This position isn't in your corpus, so it can't be saved yet."),
    ).toBeVisible();
    await expectPreferredActions(canvasElement, []);
    await expect(canvas.queryByRole("button", { name: "Save" })).not.toBeInTheDocument();
    await expect(
      canvas.queryByRole("button", { name: "Change effective date" }),
    ).not.toBeInTheDocument();
    await expect(canvas.queryByRole("button", { name: "Remove" })).not.toBeInTheDocument();
  },
};

export const LoadingGate: Story = {
  name: "Preferred move - loading keeps the relationship shell",
  render: () => workspace({}, { relationship: "empty", pendingRead: true }, { pending: true }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "unknown");
    await expect(canvas.getByTestId("preferred-status")).toHaveTextContent(
      "Loading saved choice...",
    );
    await expectPreferredActions(canvasElement, []);
  },
};

export const OpponentLocalOnly: Story = {
  name: "Preferred move - opponent turn stays local-only",
  render: () =>
    workspace(
      {
        analysisClient: storyCandidateAnalysisClient(["g1f3"]),
        gameClient: storyGameClient(STORY_BLACK_SUBJECT_GAME_DETAIL),
      },
      { relationship: "saved", putFailure: "unexpected_failure" },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await loadGame(canvas, GAME_UUID);
    const description = canvas.getByRole("button", { name: "Position description" });
    await userEvent.click(description);
    await expect(description).toHaveAttribute("aria-expanded", "true");
    await expect(
      canvas.getByTestId("position-description-row").querySelector("[data-position-summary]"),
    ).toHaveTextContent("OrientationBlack at the bottom");
    await expect(canvas.getByTestId("saved-move")).toBeVisible();
    await userEvent.click(await canvas.findByRole("button", { name: "White, move 1, e4" }));
    await userEvent.click(await canvas.findByRole("button", { name: "Black, move 1, e5" }));
    await userEvent.click(await canvas.findByRole("button", { name: "2. Nf3" }));
    await expect(canvas.getByTestId("session-status")).toHaveTextContent(
      "Move played locally: Nf3.",
    );
    await expectSessionHistory(canvasElement, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 2, Nf3");
    await expect(canvas.queryByRole("alert")).not.toBeInTheDocument();
  },
};

export const OpponentTurnGate: Story = {
  name: "Preferred move - opponent turn is a read-only gate",
  render: () => workspace({}, { relationship: "saved" }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
    await expect(
      canvas.getByText("Wait for your turn to select or save a preferred move."),
    ).toBeVisible();
    await expectPreferredActions(canvasElement, []);
    await expect(
      canvas.queryByRole("button", { name: /play this move/ }),
    ).not.toBeInTheDocument();
  },
};
