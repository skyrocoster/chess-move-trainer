import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { expect, userEvent, waitFor, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { storyCandidateAnalysisClient } from "../viewer/viewerStoryHelpers";
import { completeGameLookup } from "../viewer/viewerStoryHelpers";
import { VIEWER_GAME_UUID } from "../viewer/viewerFixtures";
import { PROMOTION_GAME } from "../viewer/viewerStoryFixtures";
import RepertoireBuilderWorkspace from "./RepertoireBuilderWorkspace";
import {
  expectActiveSessionHistoryEntry,
  expectDeferredDateAction,
  expectNoPreferredActions,
  expectPositionReachFrequency,
  expectPositionSquares,
  expectPreferredActions,
  expectPreferredMoveState,
  expectSessionHistory,
  expectStagedStatus,
} from "./repertoireBuilderStoryAssertions";
import { constrainedViewport, assignedWorkspace, workspace } from "./repertoireBuilderStoryRender";
import { expectNoHorizontalOverflow, loadGame } from "./repertoireBuilderStoryHelpers";

const meta = {
  title: "Application/Repertoire Builder/Workspace",
  component: RepertoireBuilderWorkspace,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof RepertoireBuilderWorkspace>;

export default meta;
type Story = StoryObj<typeof meta>;

export const SavedNoStage: Story = {
  name: "Preferred move - saved choice with no staged move",
  render: () => assignedWorkspace(),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "saved");
    await expect(
      canvas.getByRole("button", { name: "Current saved choice: e4; play and stage this move." }),
    ).toBeEnabled();
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("No move staged.");
    await expectPreferredActions(canvasElement, ["Change effective date", "Remove"]);
    await expectDeferredDateAction(canvasElement);
  },
};

export const FirstChoice: Story = {
  name: "Preferred move - first-choice staged proposal",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { relationship: "first-choice" },
      { overall_exists: true, white_count: 3, black_count: 2 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expectPreferredMoveState(canvasElement, "first-choice");
    await expectStagedStatus(canvasElement, "e4");
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("No saved choice yet.");
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("Staged move: e4 (e2e4)");
    await expectPreferredActions(canvasElement, ["Save", "Change effective date"]);
    await expectDeferredDateAction(canvasElement);
    await expectSessionHistory(canvasElement, ["Initial position"]);
  },
};

export const ReplacementConstrained: Story = {
  name: "Preferred move - differing staged replacement at 412px",
  parameters: constrainedViewport,
  render: () => assignedWorkspace({ analysisClient: storyCandidateAnalysisClient(["d2d4"]) }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "1. d4" }));
    await expectPreferredMoveState(canvasElement, "replacement");
    await expectStagedStatus(canvasElement, "d4");
    await expect(canvas.getByText("Save d4 to replace e4.")).toBeVisible();
    await expectPreferredActions(canvasElement, ["Save", "Change effective date", "Remove"]);
    await expectDeferredDateAction(canvasElement);
    await expectPositionReachFrequency(canvasElement, "available", "White", "5 / 10 games", "50%");
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await expectNoHorizontalOverflow(canvasElement);
  },
};

export const Matching: Story = {
  name: "Preferred move - matching staged move",
  render: () => assignedWorkspace({ analysisClient: storyCandidateAnalysisClient(["e2e4"]) }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expectPreferredMoveState(canvasElement, "matching");
    await expect(canvas.getByText("e4 is already the current saved choice.")).toBeVisible();
    await expectPreferredActions(canvasElement, ["Change effective date", "Remove"]);
    await expect(canvas.queryByRole("button", { name: "Save" })).not.toBeInTheDocument();
    await expectDeferredDateAction(canvasElement);
    await expectSessionHistory(canvasElement, ["Initial position"]);
  },
};

export const SavedBoxKeyboard: Story = {
  name: "Preferred move - saved box pointer, Enter, and Space stage locally",
  render: () => assignedWorkspace({ analysisClient: storyCandidateAnalysisClient(["d2d4"]) }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const savedBox = canvas.getByRole("button", {
      name: "Current saved choice: e4; play and stage this move.",
    });
    await userEvent.click(await canvas.findByRole("button", { name: "1. d4" }));
    await expectPreferredMoveState(canvasElement, "replacement");
    await savedBox.focus();
    await expect(savedBox).toHaveFocus();
    await userEvent.keyboard("{Enter}");
    await expectPreferredMoveState(canvasElement, "matching");
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("Staged move: e4 (e2e4)");
    await expectPositionSquares(canvasElement, "e2", 0);
    await expectPositionSquares(canvasElement, "e4", 1);
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await expectActiveSessionHistoryEntry(canvasElement, "Initial position");
    await expect(canvas.getByTestId("session-status")).toHaveTextContent(
      "Saved move staged locally: e4.",
    );
    await savedBox.focus();
    await userEvent.keyboard(" ");
    await expectPreferredMoveState(canvasElement, "matching");
    await expect(canvas.getByTestId("session-status")).toHaveTextContent(
      "Saved move staged locally: e4.",
    );
  },
};

export const SaveReplacement: Story = {
  name: "Preferred move - Save refreshes before clearing the proposal",
  render: () => assignedWorkspace({ analysisClient: storyCandidateAnalysisClient(["d2d4"]) }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "1. d4" }));
    await userEvent.click(canvas.getByRole("button", { name: "Save" }));
    await waitFor(() =>
      expect(canvas.getByTestId("session-status")).toHaveTextContent("Preferred move saved."),
    );
    await expectPreferredMoveState(canvasElement, "saved");
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent(
      "Current saved choice: d4 (d2d4)",
    );
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("No move staged.");
    await expectPositionSquares(canvasElement, "d2", 1);
    await expectPositionSquares(canvasElement, "d4", 0);
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await expectPreferredActions(canvasElement, ["Change effective date", "Remove"]);
  },
};

export const RemoveRetainsStaging: Story = {
  name: "Preferred move - Remove retains staged replacement",
  render: () => assignedWorkspace({ analysisClient: storyCandidateAnalysisClient(["d2d4"]) }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await userEvent.click(await canvas.findByRole("button", { name: "1. d4" }));
    await userEvent.click(await canvas.findByRole("button", { name: "Remove" }));
    const dialog = await body.findByRole("alertdialog", { name: "Remove preferred move?" });
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("Current saved choice: e4");
    await userEvent.click(within(dialog).getByRole("button", { name: "Cancel" }));
    await expect(canvas.getByRole("button", { name: "Remove" })).toHaveFocus();
    await userEvent.click(canvas.getByRole("button", { name: "Remove" }));
    const confirmedDialog = await body.findByRole("alertdialog", {
      name: "Remove preferred move?",
    });
    await userEvent.click(within(confirmedDialog).getByRole("button", { name: "Remove" }));
    await expect(canvas.getByText("Preferred move removed.")).toBeVisible();
    await expectPreferredMoveState(canvasElement, "first-choice");
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("No saved choice yet.");
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("Staged move: d4 (d2d4)");
    await expectPreferredActions(canvasElement, ["Save", "Change effective date"]);
    await expectDeferredDateAction(canvasElement);
    await expectSessionHistory(canvasElement, ["Initial position"]);
  },
};

export const PendingSave: Story = {
  name: "Preferred move - pending Save retains confirmed and staged facts",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["d2d4"]) },
      { relationship: "saved", pendingMutation: "save" },
      { overall_exists: true, white_count: 5, black_count: 1 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "1. d4" }));
    await userEvent.click(canvas.getByRole("button", { name: "Save" }));
    await expect(canvas.getByTestId("session-status")).toHaveTextContent("My move staged: d4.");
    await expect(canvas.getByText("Saving preferred move...")).toBeVisible();
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("Current saved choice: e4");
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("Staged move: d4 (d2d4)");
    await expect(canvas.getByRole("button", { name: "Save" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Change effective date" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeDisabled();
    await expectSessionHistory(canvasElement, ["Initial position"]);
  },
};

export const PendingRemove: Story = {
  name: "Preferred move - pending Remove retains the saved choice",
  render: () => assignedWorkspace({}, { pendingMutation: "remove" }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await userEvent.click(await canvas.findByRole("button", { name: "Remove" }));
    const dialog = await body.findByRole("alertdialog", { name: "Remove preferred move?" });
    await userEvent.click(within(dialog).getByRole("button", { name: "Remove" }));
    await expect(canvas.getByText("Removing preferred move...")).toBeVisible();
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("Current saved choice: e4");
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Change effective date" })).toBeDisabled();
  },
};

export const SaveFailureRetention: Story = {
  name: "Preferred move - failed Save retains both facts",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["d2d4"]) },
      { relationship: "saved", putFailure: "unexpected_failure" },
      { overall_exists: true, white_count: 5, black_count: 1 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "1. d4" }));
    await userEvent.click(canvas.getByRole("button", { name: "Save" }));
    await expect(canvas.getByRole("alert")).toHaveTextContent(
      "The preferred move could not be updated. Try again.",
    );
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("Current saved choice: e4");
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("Staged move: d4 (d2d4)");
    await expectPreferredActions(canvasElement, ["Save", "Change effective date", "Remove"]);
  },
};

export const RemoveFailureRetention: Story = {
  name: "Preferred move - failed Remove retains the saved choice",
  render: () => assignedWorkspace({}, { removeFailure: "unexpected_failure" }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await userEvent.click(await canvas.findByRole("button", { name: "Remove" }));
    const dialog = await body.findByRole("alertdialog", { name: "Remove preferred move?" });
    await userEvent.click(within(dialog).getByRole("button", { name: "Remove" }));
    await expect(canvas.getByRole("alert")).toHaveTextContent(
      "The preferred move could not be updated. Try again.",
    );
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("Current saved choice: e4");
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeEnabled();
  },
};

export const PromotionPreferred: Story = {
  name: "Preferred move - promotion stages the canonical move",
  render: () =>
    workspace(
      {
        analysisClient: storyCandidateAnalysisClient(["e7e8q"]),
        lookup: completeGameLookup(PROMOTION_GAME),
      },
      { relationship: "empty" },
      { overall_exists: true, white_count: 1, black_count: 1 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await loadGame(canvas, VIEWER_GAME_UUID, "0");
    await userEvent.click(await canvas.findByRole("button", { name: "1. e8=Q+" }));
    await expect(body.getByRole("dialog", { name: "Choose a promotion piece" })).toBeVisible();
    await userEvent.click(body.getByRole("button", { name: "Promote to knight" }));
    await expectPreferredMoveState(canvasElement, "first-choice");
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("Staged move: e8=N (e7e8n)");
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("No saved choice yet.");
    await expect(canvas.getByRole("button", { name: "Save" })).toBeEnabled();
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await expectPositionSquares(canvasElement, "e7", 0);
    await expectPositionSquares(canvasElement, "e8", 1);
  },
};

export const AccessibilityAndResponsive: Story = {
  name: "Preferred move - focus, accessibility, and no overflow",
  parameters: constrainedViewport,
  render: () => assignedWorkspace({ analysisClient: storyCandidateAnalysisClient(["d2d4"]) }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const savedBox = canvas.getByRole("button", {
      name: "Current saved choice: e4; play and stage this move.",
    });
    await savedBox.focus();
    await expect(savedBox).toHaveFocus();
    await expect(savedBox).toHaveAttribute("type", "button");
    await expectNoPreferredActions(canvasElement);
    await expectDeferredDateAction(canvasElement);
    await expectNoHorizontalOverflow(canvasElement);
  },
};
