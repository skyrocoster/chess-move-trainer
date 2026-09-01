import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import {
  completeGameLookup,
  storyAnalysisClient,
  storyCandidateAnalysisClient,
} from "../viewer/viewerStoryHelpers";
import { VIEWER_GAME_UUID } from "../viewer/viewerFixtures";
import RepertoireBuilderWorkspace from "./RepertoireBuilderWorkspace";
import {
  expectActiveSessionHistoryEntry,
  expectPreferredActions,
  expectPreferredMoveState,
  expectSessionHistory,
} from "./repertoireBuilderStoryAssertions";
import { BLACK_SUBJECT_GAME, workspace } from "./repertoireBuilderStoryRender";
import { loadGame } from "./repertoireBuilderStoryHelpers";

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
      { overall_exists: false, white_count: 0, black_count: 0 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "empty");
    await expect(
      canvas.getByText("This position cannot be saved because it is not in the corpus."),
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
        lookup: completeGameLookup(BLACK_SUBJECT_GAME),
      },
      { relationship: "saved", putFailure: "unexpected_failure" },
      { overall_exists: true, white_count: 5, black_count: 2 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await loadGame(canvas, VIEWER_GAME_UUID, "2");
    const description = canvas.getByRole("button", { name: "Position description" });
    await userEvent.click(description);
    await expect(description).toHaveAttribute("aria-expanded", "true");
    await expect(
      canvas.getByTestId("position-description-row").querySelector("[data-position-summary]"),
    ).toHaveTextContent("OrientationBlack at the bottom");
    await expect(canvas.getByTestId("saved-move")).toBeVisible();
    await userEvent.click(await canvas.findByRole("button", { name: "2. Nf3" }));
    await expect(canvas.getByTestId("session-status")).toHaveTextContent(
      "Opponent move played locally: Nf3.",
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
  render: () =>
    workspace(
      { lookup: completeGameLookup(BLACK_SUBJECT_GAME) },
      { relationship: "saved" },
      { overall_exists: true, white_count: 5, black_count: 2 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await loadGame(canvas, VIEWER_GAME_UUID, "2");
    await expect(
      canvas.getByText("Wait for your turn to stage or save a preferred move."),
    ).toBeVisible();
    await expectPreferredActions(canvasElement, []);
    await expect(
      canvas.queryByRole("button", { name: /play and stage this move/ }),
    ).not.toBeInTheDocument();
  },
};
