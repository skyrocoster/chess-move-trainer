import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import RepertoireBuilderWorkspace from "./RepertoireBuilderWorkspace";
import {
  expectActiveSessionHistoryEntry,
  expectPositionReachFrequency,
  expectPositionSquares,
  expectPreferredMoveState,
  expectSessionHistory,
  expectSingleStagedStatus,
} from "./repertoireBuilderStoryAssertions";
import { expectNoHorizontalOverflow, selectCurrentUtcDate } from "./repertoireBuilderStoryHelpers";
import { assignedWorkspace, constrainedViewport, workspace } from "./repertoireBuilderStoryRender";
import { storyCandidateAnalysisClient } from "../viewer/viewerStoryHelpers";

const meta = {
  title: "Application/Repertoire Builder/Workspace",
  component: RepertoireBuilderWorkspace,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof RepertoireBuilderWorkspace>;

export default meta;
type Story = StoryObj<typeof meta>;

export const AssignedBoardPlay: Story = {
  name: "Preferred move - board plays the saved move",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { initialState: "assigned" },
      { overall_exists: true, white_count: 5, black_count: 1 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "saved");
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent(
      "Current saved choice: e4 (e2e4)",
    );
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expectPositionSquares(canvasElement, "e4", 1);
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await expectActiveSessionHistoryEntry(canvasElement, "Initial position");
    await expect(canvas.getByTestId("session-status")).toHaveTextContent("My move staged: e4.");

    async function expectMatchingStagedPanel() {
      await expectPreferredMoveState(canvasElement, "matching");
      await expect(canvas.getByTestId("staged-move")).toHaveTextContent("Staged move: e4 (e2e4)");
      await expect(canvas.getByTestId("effective-date")).toHaveTextContent(
        "Effective from 2026-01-01",
      );
      await expect(canvas.getByRole("button", { name: "Remove" })).toBeVisible();
      await expect(canvas.getByTestId("saved-move")).toBeVisible();
      await expectPositionSquares(canvasElement, "e2", 0);
      await expectPositionSquares(canvasElement, "e4", 1);
    }

    await expectMatchingStagedPanel();
  },
};

export const UnsavedPlayedConstrained: Story = {
  name: "Preferred move - staged replacement alternative, constrained",
  parameters: constrainedViewport,
  render: () => assignedWorkspace({ analysisClient: storyCandidateAnalysisClient(["d2d4"]) }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "saved");
    await userEvent.click(await canvas.findByRole("button", { name: "1. d4" }));
    await expectPreferredMoveState(canvasElement, "replacement");
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("Staged move: d4 (d2d4)");
    await expect(canvas.getByRole("button", { name: "Save" })).toBeEnabled();
    await expect(canvas.getByRole("button", { name: "Effective date: 2026-01-01" })).toBeVisible();
    await expect(canvas.getByTestId("session-origin")).toHaveTextContent("Current Ply 0");
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await expectPositionReachFrequency(canvasElement, "available", "White", "5 / 10 games", "50%");
    await expectNoHorizontalOverflow(canvasElement);
  },
};

export const AssignedToday: Story = {
  name: "Preferred move - persisted current UTC date shows Today",
  render: () =>
    assignedWorkspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { effectiveAt: new Date().toISOString() },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "saved");
    await expect(canvas.getByTestId("effective-date")).toHaveTextContent("Effective from Today");
    await expect(
      canvas.getByRole("button", { name: /Effective date: \d{4}-\d{2}-\d{2}/ }),
    ).toBeVisible();
  },
};

export const EditReplacement: Story = {
  name: "Preferred move - Save replacement",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["d2d4"]) },
      { initialState: "assigned" },
      { overall_exists: true, white_count: 5, black_count: 1 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("saved-move")).toBeVisible();
    await userEvent.click(await canvas.findByRole("button", { name: "1. d4" }));
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("Staged move: d4 (d2d4)");
    await expectPositionSquares(canvasElement, "d2", 0);
    await expectPositionSquares(canvasElement, "d4", 1);
    await expect(canvas.getByTestId("session-origin")).toHaveTextContent("Current Ply 0");
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await userEvent.click(canvas.getByRole("button", { name: "Save" }));
    await expect(canvas.getByTestId("session-status")).toHaveTextContent("Preferred move saved.");
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent(
      "Current saved choice: d4 (d2d4)",
    );
    await expectPositionSquares(canvasElement, "d2", 1);
    await expectPositionSquares(canvasElement, "d4", 0);
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await expect(canvas.getByRole("button", { name: "Effective date: 2026-08-29" })).toBeVisible();
  },
};

export const DatedAdd: Story = {
  name: "Preferred move - selected UTC date persists after Save",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { initialState: "unassigned" },
      { overall_exists: true, white_count: 3, black_count: 2 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expectSingleStagedStatus(canvasElement);
    const date = await selectCurrentUtcDate(canvasElement);
    await expect(canvas.getByRole("button", { name: `Effective date: ${date}` })).toBeVisible();
    await expect(canvas.getByTestId("effective-date")).toHaveTextContent("Effective from Today");
    await userEvent.click(canvas.getByRole("button", { name: "Save" }));
    await expect(canvas.getByTestId("session-status")).toHaveTextContent("Preferred move saved.");
    await expectPositionSquares(canvasElement, "e2", 1);
    await expectPositionSquares(canvasElement, "e4", 0);
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await expect(canvas.getByRole("button", { name: `Effective date: ${date}` })).toBeVisible();
    await expect(canvas.getByTestId("effective-date")).toHaveTextContent("Effective from Today");
  },
};

export const MutationFailure: Story = {
  name: "Preferred move - failed Save retains staged move and date",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { initialState: "unassigned", putFailure: "future_effective_time" },
      { overall_exists: true, white_count: 3, black_count: 2 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    const date = await selectCurrentUtcDate(canvasElement);
    await userEvent.click(canvas.getByRole("button", { name: "Save" }));
    const alert = canvas.getByRole("alert");
    await expect(alert).toHaveRole("alert");
    await expect(alert).toHaveTextContent("The selected date cannot be in the future.");
    await expect(canvas.getAllByRole("alert")).toHaveLength(1);
    await expectSingleStagedStatus(canvasElement);
    const status = canvas.getByTestId("session-status");
    await expect(status).toHaveAttribute("data-testid", "session-status");
    await expect(status).toHaveRole("status");
    await expect(status).toHaveAttribute("aria-live", "polite");
    await expectPositionSquares(canvasElement, "e2", 0);
    await expectPositionSquares(canvasElement, "e4", 1);
    await expect(canvas.getByTestId("session-origin")).toHaveTextContent("Current Ply 0");
    await expect(canvas.getByRole("button", { name: `Effective date: ${date}` })).toBeVisible();
  },
};

export const RemoveConfirmation: Story = {
  name: "Preferred move - confirmed Remove clears date",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { initialState: "assigned" },
      { overall_exists: true, white_count: 5, black_count: 1 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await expect(canvas.getByTestId("saved-move")).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Remove" }));
    const dialog = await body.findByRole("alertdialog", { name: "Remove preferred move?" });
    await expect(dialog).toBeVisible();
    await userEvent.click(within(dialog).getByRole("button", { name: "Cancel" }));
    await expect(canvas.getByTestId("saved-move")).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Remove" }));
    const openDialog = await body.findByRole("alertdialog", { name: "Remove preferred move?" });
    await userEvent.click(within(openDialog).getByRole("button", { name: "Remove" }));
    await expect(canvas.getByText("Preferred move removed.")).toBeVisible();
    await expect(canvas.queryByTestId("saved-move")).not.toBeInTheDocument();
    await expect(canvas.queryByTestId("effective-date")).not.toBeInTheDocument();
    await expect(canvas.queryByRole("button", { name: /Effective date/ })).not.toBeInTheDocument();
  },
};
