import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { completeGameLookup, storyCandidateAnalysisClient } from "../viewer/viewerStoryHelpers";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "../viewer/viewerFixtures";
import { PROMOTION_GAME } from "../viewer/viewerStoryFixtures";
import RepertoireBuilderWorkspace from "./RepertoireBuilderWorkspace";
import {
  expectActiveSessionHistoryEntry,
  expectPositionReachFrequency,
  expectPositionSquares,
  expectPreferredMoveState,
  expectSessionHistory,
  expectSessionBoundary,
  expectSingleStagedStatus,
  sharedPositionSummary,
} from "./repertoireBuilderStoryAssertions";
import { BLACK_SUBJECT_GAME, constrainedViewport, workspace } from "./repertoireBuilderStoryRender";
import { expectNoHorizontalOverflow, loadGame } from "./repertoireBuilderStoryHelpers";

const meta = {
  title: "Application/Repertoire Builder/Workspace",
  component: RepertoireBuilderWorkspace,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof RepertoireBuilderWorkspace>;

export default meta;
type Story = StoryObj<typeof meta>;

const STARTING_FEN = VIEWER_GAME.positions[0].fen;
const STAGED_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";
const stagedIdentityClient = storyCandidateAnalysisClient(["e2e4"]);
const stagedObservedFens: string[] = [];
const stagedIdentityObserve = stagedIdentityClient.observe;
stagedIdentityClient.observe = async (fen, signal) => {
  stagedObservedFens.push(fen);
  return stagedIdentityObserve(fen, signal);
};

async function verifyStandardWorkspace(canvasElement: HTMLElement) {
  const canvas = within(canvasElement);
  await expect(canvas.getByRole("heading", { name: "Repertoire Builder", level: 1 })).toBeVisible();
  const board = canvas.getByRole("group", {
    name: "Chess board: standard starting position, White at the bottom",
  });
  const stage = canvas.getByTestId("board-eval-stage");
  const rail = canvas.getByTestId("board-eval-rail-shell");
  const meter = canvas.getByRole("meter", { name: "Evaluation" });
  await expect(board).toBeVisible();
  await expect(stage).toContainElement(board);
  await expect(stage).toContainElement(rail);
  await expect(meter).toHaveAttribute("data-state", "neutral");
  await expect(meter).toHaveAttribute("data-orientation", "white");
  await expect(meter).toHaveAttribute("aria-valuetext", "No analysis yet; evaluation neutral.");
  const descriptionRow = canvas.getByTestId("position-description-row");
  if (board.contains(descriptionRow)) {
    throw new Error("The position description is still inside the repertoire board container.");
  }
  const description = canvas.getByRole("button", { name: "Position description" });
  await expect(description).toHaveAttribute("aria-expanded", "false");
  await userEvent.click(description);
  await expect(await sharedPositionSummary(canvasElement)).toHaveTextContent(
    "OrientationWhite at the bottom",
  );
  description.focus();
  await expect(description).toHaveFocus();
  await expectSessionBoundary(canvasElement);
  await expectPreferredMoveState(canvasElement, "no-saved");
  await expectPositionReachFrequency(canvasElement, "available", "White", "3 / 10 games", "30%");
  await expectNoHorizontalOverflow(canvasElement);
}

export const Wide: Story = {
  name: "Standard starting position - Wide",
  render: () => workspace(),
  play: async ({ canvasElement }) => verifyStandardWorkspace(canvasElement),
};
export const Constrained: Story = {
  name: "Standard starting position - Constrained",
  parameters: constrainedViewport,
  render: () => workspace(),
  play: async ({ canvasElement }) => verifyStandardWorkspace(canvasElement),
};
export const StoredPrefixBlackSubject: Story = {
  name: "Stored prefix through selected Ply - Black subject",
  render: () =>
    workspace({
      lookup: completeGameLookup(BLACK_SUBJECT_GAME),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await loadGame(canvas, VIEWER_GAME_UUID, "2");
    await expect(
      canvas.getByRole("group", {
        name: `Chess board: game ${VIEWER_GAME_UUID}, ply 2, Black at the bottom`,
      }),
    ).toBeVisible();
    await expect(canvas.getByTestId("session-origin")).toHaveTextContent(
      `complete prefix through Ply 2. Current Ply 2`,
    );
    await expectSessionHistory(canvasElement, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
    ]);
    await expectActiveSessionHistoryEntry(canvasElement, "Black, move 1, e5");
    await expectPreferredMoveState(canvasElement, "no-saved");
    await expectPositionReachFrequency(canvasElement, "available", "Black", "2 / 10 games", "20%");
    await expect(await sharedPositionSummary(canvasElement)).toHaveTextContent(
      "OrientationBlack at the bottom",
    );
  },
};
export const StagedMy: Story = {
  name: "Local line - staged my move",
  render: () => {
    stagedObservedFens.length = 0;
    return workspace({ analysisClient: stagedIdentityClient });
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const meter = canvas.getByRole("meter", { name: "Evaluation" });
    await expect(meter).toHaveAttribute("data-state", "best-line");
    await expect(meter).toHaveAttribute("aria-valuetext", "best-line evaluation +0.34.");
    await expect(stagedObservedFens).toContain(STARTING_FEN);
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expectSessionBoundary(canvasElement);
    await expectSingleStagedStatus(canvasElement);
    await expectPositionSquares(canvasElement, "e2", 0);
    await expectPositionSquares(canvasElement, "e4", 1);
    await expect(canvas.getByTestId("session-origin")).toHaveTextContent("Current Ply 0");
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await expectActiveSessionHistoryEntry(canvasElement, "Initial position");
    await expect(meter).toHaveAttribute("aria-valuetext", "best-line evaluation +0.34.");
    await expect(stagedObservedFens).toContain(STAGED_E4_FEN);
    await expect(canvas.getByRole("button", { name: "1. e4" })).toBeVisible();
    await expectPreferredMoveState(canvasElement, "unsaved-played");
    await expect(canvas.getByTestId("played-move")).toHaveTextContent("Played move: e4 (e2e4)");
    await expectPositionReachFrequency(canvasElement, "available", "White", "3 / 10 games", "30%");
  },
};

export const OpponentImmediate: Story = {
  name: "Local line - immediate opponent move",
  render: () =>
    workspace({
      analysisClient: storyCandidateAnalysisClient(["g1f3"]),
      lookup: completeGameLookup(BLACK_SUBJECT_GAME),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await loadGame(canvas, VIEWER_GAME_UUID, "2");
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
    await expectPreferredMoveState(canvasElement, "no-saved");
    await expectPositionReachFrequency(canvasElement, "available", "Black", "2 / 10 games", "20%");
  },
};

export const ConstrainedStoredPrefixAndLocalLine: Story = {
  name: "Stored prefix and local line - Constrained",
  parameters: constrainedViewport,
  render: () =>
    workspace({
      analysisClient: storyCandidateAnalysisClient(["g1f3"]),
      lookup: completeGameLookup(BLACK_SUBJECT_GAME),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await loadGame(canvas, VIEWER_GAME_UUID, "2");
    await userEvent.click(await canvas.findByRole("button", { name: "2. Nf3" }));
    await expectSessionHistory(canvasElement, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 2, Nf3");
    await expect(canvas.getByTestId("session-origin")).toHaveTextContent("Current Ply 3");
    await expectPreferredMoveState(canvasElement, "no-saved");
    await expectPositionReachFrequency(canvasElement, "available", "Black", "2 / 10 games", "20%");
    await expectNoHorizontalOverflow(canvasElement);
  },
};

export const CandidateActivation: Story = {
  name: "Candidate - Best line uses local move path",
  render: () =>
    workspace({
      analysisClient: storyCandidateAnalysisClient(["e2e4"]),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expectPositionSquares(canvasElement, "e2", 0);
    await expectPositionSquares(canvasElement, "e4", 1);
    await expectSessionHistory(canvasElement, ["Initial position", "White, move 1, e4"]);
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 1, e4");
    await expect(canvas.getByTestId("session-status")).toHaveTextContent(
      "Opponent move played locally: e4.",
    );
    await expectPreferredMoveState(canvasElement, "no-saved");
    await expectPositionReachFrequency(canvasElement, "available", "Black", "2 / 10 games", "20%");
  },
};

export const NavigationAndReplacement: Story = {
  name: "Navigation - local history and replacement truncation",
  render: () =>
    workspace({
      analysisClient: storyCandidateAnalysisClient(["e2e4", "e7e5", "e7e6"]),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
    await userEvent.click(await canvas.findByRole("button", { name: "1... e5" }));
    await expectSessionHistory(canvasElement, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
    ]);
    await expectActiveSessionHistoryEntry(canvasElement, "Black, move 1, e5");

    await userEvent.click(canvas.getByRole("button", { name: "Previous" }));
    await expectSessionHistory(canvasElement, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
    ]);
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 1, e4");
    await expect(canvas.getByRole("button", { name: "Next" })).toBeEnabled();
    await userEvent.click(await canvas.findByRole("button", { name: "1... e6" }));
    await expectSessionHistory(canvasElement, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e6",
    ]);
    await expectActiveSessionHistoryEntry(canvasElement, "Black, move 1, e6");
    await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
  },
};
export const FlipCancellation: Story = {
  name: "Flip - preserves FEN and cancels pending staging",
  render: () =>
    workspace({
      analysisClient: storyCandidateAnalysisClient(["e2e4"]),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expectSingleStagedStatus(canvasElement);
    await expectPositionSquares(canvasElement, "e2", 0);
    await expectPositionSquares(canvasElement, "e4", 1);
    await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
    await expect(canvas.getByTestId("session-status")).toHaveTextContent(
      "Flipped to Black at the bottom.",
    );
    await expect(await sharedPositionSummary(canvasElement)).toHaveTextContent(
      "OrientationBlack at the bottom",
    );
    await expectPositionSquares(canvasElement, "e2", 1);
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expectPositionSquares(canvasElement, "e4", 1);
    await expectSessionHistory(canvasElement, ["Initial position", "White, move 1, e4"]);
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 1, e4");
  },
};
export const Promotion: Story = {
  name: "Promotion - selected piece stages a child preview",
  render: () =>
    workspace({
      analysisClient: storyCandidateAnalysisClient(["e7e8q"]),
      lookup: completeGameLookup(PROMOTION_GAME),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await loadGame(canvas, VIEWER_GAME_UUID, "0");
    const description = canvas.getByRole("button", { name: "Position description" });
    await userEvent.click(description);
    await expect(description).toHaveAttribute("aria-expanded", "true");
    await userEvent.click(await canvas.findByRole("button", { name: /1\. e8=Q/ }));
    await expect(body.getByRole("dialog", { name: "Choose a promotion piece" })).toBeVisible();
    await expectPositionSquares(canvasElement, "e7", 1);
    await userEvent.keyboard("{Escape}");
    await expect(
      body.queryByRole("dialog", { name: "Choose a promotion piece" }),
    ).not.toBeInTheDocument();
    await expectPositionSquares(canvasElement, "e7", 1);
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await userEvent.click(await canvas.findByRole("button", { name: /1\. e8=Q/ }));
    await expect(body.getByRole("dialog", { name: "Choose a promotion piece" })).toBeVisible();
    await userEvent.click(body.getByRole("button", { name: "Promote to knight" }));
    await expectPositionSquares(canvasElement, "e7", 0);
    await expectPositionSquares(canvasElement, "e8", 1);
    await expect(
      (await sharedPositionSummary(canvasElement)).querySelector(
        '[data-position-side="w"] [data-position-piece="n"]',
      ),
    ).toBeTruthy();
    await expect(canvas.getByTestId("session-origin")).toHaveTextContent("Current Ply 0");
    await expectSessionHistory(canvasElement, ["Initial position"]);
  },
};
export const KeyboardAndAccessibility: Story = {
  name: "Keyboard and accessibility - bounded workspace",
  parameters: constrainedViewport,
  render: () =>
    workspace({
      analysisClient: storyCandidateAnalysisClient(["e2e4"]),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("toolbar", { name: "Board controls" })).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Previous" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Flip" })).toBeEnabled();
    const candidate = await canvas.findByRole("button", { name: "1. e4" });
    candidate.focus();
    await userEvent.keyboard("{Enter}");
    await expectSessionBoundary(canvasElement);
    await expectSingleStagedStatus(canvasElement);
    await expect(candidate).toHaveFocus();
    await expectPositionSquares(canvasElement, "e2", 0);
    await expectPositionSquares(canvasElement, "e4", 1);
    await expectNoHorizontalOverflow(canvasElement);
    await expectPreferredMoveState(canvasElement, "unsaved-played");
    await expectPositionReachFrequency(canvasElement, "available", "White", "3 / 10 games", "30%");
  },
};
export const Accessibility: Story = {
  name: "Accessibility - semantic controls and no overflow",
  render: () => workspace(),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("group", { name: /Chess board:/ })).toBeVisible();
    await expect(canvas.getByRole("toolbar", { name: "Board controls" })).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Position description" })).toHaveAttribute(
      "aria-expanded",
      "false",
    );
    await expectNoHorizontalOverflow(canvasElement);
  },
};
export const UnassignedSavable: Story = {
  name: "Preferred move - unassigned, seen, and Add",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { initialState: "unassigned" },
      { overall_exists: true, white_count: 3, black_count: 2 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "no-saved");
    await expectPositionReachFrequency(canvasElement, "available", "White", "3 / 10 games", "30%");
    await expect(canvas.getByText("Seen in 3 games as White")).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Add" })).toBeDisabled();
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expectSingleStagedStatus(canvasElement);
    await expectPositionSquares(canvasElement, "e2", 0);
    await expectPositionSquares(canvasElement, "e4", 1);
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await userEvent.click(canvas.getByRole("button", { name: "Add" }));
    await expect(canvas.getByText("Preferred move added.")).toBeVisible();
    await expectPreferredMoveState(canvasElement, "saved");
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("e4");
    await expectPositionSquares(canvasElement, "e2", 1);
    await expectPositionSquares(canvasElement, "e4", 0);
    await expect(canvas.getByTestId("session-origin")).toHaveTextContent("Current Ply 0");
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await expect(canvas.getByRole("button", { name: "Effective date: 2026-08-29" })).toBeVisible();
  },
};
export const ZeroPersonalCount: Story = {
  name: "Preferred move - zero personal count remains savable",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { initialState: "unassigned" },
      { overall_exists: true, white_count: 0, black_count: 4 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPositionReachFrequency(canvasElement, "available", "White", "0 / 10 games", "0%");
    await expect(canvas.getByText("Never seen as White")).toBeVisible();
    await expect(
      canvas.queryByText("This position cannot be saved because it is not in the corpus."),
    ).not.toBeInTheDocument();
    await expect(canvas.getByRole("button", { name: "Add" })).toBeDisabled();
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expect(canvas.getByRole("button", { name: "Add" })).toBeEnabled();
    await expectPreferredMoveState(canvasElement, "unsaved-played");
  },
};
export const AbsentUnsavable: Story = {
  name: "Preferred move - absent overall and unsavable",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { initialState: "unassigned" },
      { overall_exists: false, white_count: 0, black_count: 0 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "no-saved");
    await expectPositionReachFrequency(canvasElement, "absent", "White");
    await expect(canvas.getByText("Never seen as White")).toBeVisible();
    await expect(
      canvas.getByText("This position cannot be saved because it is not in the corpus."),
    ).toBeVisible();
    await expect(canvas.queryByRole("button", { name: "Add" })).not.toBeInTheDocument();
    await expect(
      canvas.queryByRole("button", { name: "Effective date: Choose date" }),
    ).not.toBeInTheDocument();
  },
};
export const AssignedReadOnly: Story = {
  name: "Preferred move - assigned read-only own turn",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { initialState: "assigned" },
      { overall_exists: true, white_count: 5, black_count: 1 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "saved");
    await expect(canvas.getByText("Seen in 5 games as White")).toBeVisible();
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("Saved move: e4 (e2e4)");
    await expect(canvas.getByRole("button", { name: "Edit" })).toBeEnabled();
    await expect(canvas.getByRole("button", { name: "Play saved move" })).toBeEnabled();
    await expect(canvas.queryByRole("button", { name: "Add" })).not.toBeInTheDocument();
    await userEvent.click(canvas.getByRole("button", { name: "Play saved move" }));
    await expectPositionSquares(canvasElement, "e4", 1);
    await expectSessionHistory(canvasElement, ["Initial position", "White, move 1, e4"]);
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 1, e4");
    await expect(canvas.getByTestId("session-status")).toHaveTextContent(
      "Saved move played locally: e4.",
    );
    await expectPreferredMoveState(canvasElement, "matching-played");
    await expect(canvas.getByTestId("played-move")).toHaveTextContent("Played move: e4 (e2e4)");
    await expect(canvas.queryByTestId("saved-move")).not.toBeInTheDocument();
  },
};
