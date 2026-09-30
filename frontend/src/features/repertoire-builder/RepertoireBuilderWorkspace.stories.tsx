import { useMemo, useState } from "react";
import { expect, userEvent, waitFor, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import {
  storyCandidateAnalysisClient,
  storySelectedPositionAnalysisClient,
  type StoryAnalysisLifecycleEvent,
} from "../analysis/analysisStoryClients";
import { GAME, GAME_UUID } from "../game/gameFixtures";
import { storyViewport } from "../../storybook/viewports";
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
  verifyStandardWorkspace,
} from "./repertoireBuilderStoryAssertions";
import { workspace } from "./repertoireBuilderStoryRender";
import {
  STORY_BLACK_SUBJECT_GAME_DETAIL,
  STORY_PROMOTION_GAME_DETAIL,
  expectNoHorizontalOverflow,
  loadGame,
  storyGameClient,
} from "./repertoireBuilderStoryHelpers";

const meta = {
  title: "Production/Application/Repertoire Builder/Workspace/Core",
  tags: ["status-production"],
  component: RepertoireBuilderWorkspace,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof RepertoireBuilderWorkspace>;

export default meta;
type Story = StoryObj<typeof meta>;

const STARTING_FEN = GAME.positions[0].fen;
const STAGED_E4_FEN = GAME.positions[1].fen;
const stagedIdentityClient = storyCandidateAnalysisClient(["e2e4"]);
const stagedObservedFens: string[] = [];
const stagedIdentityObserve = stagedIdentityClient.observe;
stagedIdentityClient.observe = async (fen, signal) => {
  stagedObservedFens.push(fen);
  return stagedIdentityObserve(fen, signal);
};

function SelectedPositionAnalysisLifecycleStory() {
  const [events, setEvents] = useState<StoryAnalysisLifecycleEvent[]>([]);
  const analysisClient = useMemo(
    () =>
      storySelectedPositionAnalysisClient((event) => setEvents((current) => [...current, event])),
    [],
  );
  const summary = events
    .map(({ operation, state, hasResult }) => `${operation}:${state}${hasResult ? "+result" : ""}`)
    .join(" | ");

  return (
    <>
      {workspace({ analysisClient })}
      <output data-testid="analysis-lifecycle-proof" hidden>
        observations: {events.filter(({ operation }) => operation === "observe").length}; requests:{" "}
        {events.filter(({ operation }) => operation === "request").length}; request quality:{" "}
        {events
          .filter(({ operation }) => operation === "request")
          .map(({ quality }) => quality ?? "none")
          .join(", ") || "none"}
        ; states: {summary}
      </output>
    </>
  );
}

export const Wide: Story = {
  name: "Standard starting position — Wide",
  parameters: storyViewport("workspace-wide-1280"),
  render: () => workspace(),
  play: async ({ canvasElement }) => verifyStandardWorkspace(canvasElement),
};

export const Constrained: Story = {
  name: "Standard starting position — Constrained",
  parameters: storyViewport("constrained-412"),
  render: () => workspace(),
  play: async ({ canvasElement }) => verifyStandardWorkspace(canvasElement, "narrow"),
};

export const Medium: Story = {
  name: "Standard starting position — Medium",
  parameters: storyViewport("workspace-medium-800"),
  render: () => workspace(),
  play: async ({ canvasElement }) => {
    await verifyStandardWorkspace(canvasElement, "medium");
    const canvas = within(canvasElement);
    const stage = canvas.getByTestId("repertoire-workspace-stage");
    const boardRow = canvas.getByTestId("repertoire-responsive-board-row");
    const lowerGroup = canvas.getByTestId("repertoire-responsive-medium-group");
    await expect(boardRow).toContainElement(canvas.getByTestId("repertoire-board-lane"));
    await expect(lowerGroup).toContainElement(canvas.getByTestId("repertoire-session-lane"));
    await expect(lowerGroup).toContainElement(canvas.getByTestId("repertoire-engine-lane"));
    await expect(lowerGroup).not.toContainElement(canvas.getByTestId("repertoire-board-lane"));
    await expect(stage).toContainElement(boardRow);
  },
};
export const StoredPrefixBlackSubject: Story = {
  name: "Stored prefix through selected ply — Black subject",
  render: () =>
    workspace({
      gameClient: storyGameClient(STORY_BLACK_SUBJECT_GAME_DETAIL),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await loadGame(canvas, GAME_UUID);
    await userEvent.click(await canvas.findByRole("button", { name: "Black, move 1, e5" }));
    await expect(
      canvas.getByRole("group", {
        name: `Chess board: game ${GAME_UUID}, ply 2, Black at the bottom`,
      }),
    ).toBeVisible();
    await expectSessionHistory(canvasElement, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(canvasElement, "Black, move 1, e5");
    await expectPreferredMoveState(canvasElement, "first-choice");
    await expectPositionReachFrequency(canvasElement, "available", "Black", "2 / 10 games", "20%");
    await expect(await sharedPositionSummary(canvasElement)).toHaveTextContent(
      "OrientationBlack at the bottom",
    );
  },
};
export const StagedMy: Story = {
  name: "Local line — staged my move",
  render: () => {
    stagedObservedFens.length = 0;
    return workspace({ analysisClient: stagedIdentityClient });
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const meter = canvas.getByRole("meter", { name: "Evaluation" });
    await expect(meter).toHaveAttribute("data-state", "best-line");
    await expect(meter).toHaveAttribute("aria-valuetext", "Best-line evaluation +0.34.");
    await expect(stagedObservedFens).toContain(STARTING_FEN);
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expectSessionBoundary(canvasElement);
    await expectSingleStagedStatus(canvasElement);
    await expectPositionSquares(canvasElement, "e2", 0);
    await expectPositionSquares(canvasElement, "e4", 1);
    await expectSessionHistory(canvasElement, ["Initial position", "White, move 1, e4"]);
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 1, e4");
    await expect(meter).toHaveAttribute("aria-valuetext", "Best-line evaluation +0.34.");
    await waitFor(() => expect(stagedObservedFens).toContain(STAGED_E4_FEN));
    await expectPreferredMoveState(canvasElement, "first-choice");
    await expect(canvas.getByTestId("selected-move")).toHaveTextContent(/^Selected\s*e4\s*e2e4$/);
    await expectPositionReachFrequency(canvasElement, "available", "White", "3 / 10 games", "30%");
  },
};

export const SelectedPositionAnalysisLifecycle: Story = {
  name: "Selected-position analysis lifecycle — observe, request, poll, navigate",
  render: () => <SelectedPositionAnalysisLifecycleStory />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const analysis = canvas.getByRole("region", { name: "Analysis" });
    const analysisQueries = within(analysis);
    const status = analysisQueries.getByRole("status");
    const proof = canvas.getByTestId("analysis-lifecycle-proof");

    await expect(status).toHaveTextContent("Analysis available on request");
    await expect(analysisQueries.queryByRole("button", { name: "1. d4" })).not.toBeInTheDocument();
    await expect(proof).toHaveTextContent("observations: 1; requests: 0");
    await expect(proof).toHaveTextContent("request quality: none");

    await userEvent.click(analysisQueries.getByRole("button", { name: "Analyze position" }));
    await expect(status).toHaveTextContent(/Analysis (queued|running)/);
    await expect(analysisQueries.getByRole("button", { name: "1. d4" })).toBeVisible();
    await expect(proof).toHaveTextContent("requests: 1");
    await expect(proof).toHaveTextContent("request quality: browser");

    await waitFor(() => expect(status).toHaveTextContent("Analysis running"));
    await expect(analysisQueries.getByRole("button", { name: "1. d4" })).toBeVisible();
    await expect(proof).toHaveTextContent("observe:running+result");

    await waitFor(() => expect(status).toHaveTextContent("Analysis complete"));
    await expect(analysisQueries.getByRole("button", { name: "1. e4" })).toBeVisible();
    await expect(
      analysisQueries.getByRole("button", { name: "Upgrade to full analysis" }),
    ).toBeVisible();
    await expect(
      analysisQueries.queryByRole("button", { name: "Update analysis" }),
    ).not.toBeInTheDocument();
    await expect(
      analysisQueries.queryByRole("button", { name: "Retry analysis" }),
    ).not.toBeInTheDocument();

    await userEvent.click(
      analysisQueries.getByRole("button", { name: "Upgrade to full analysis" }),
    );
    await expect(status).toHaveTextContent(/Analysis (queued|running)/);
    await expect(analysisQueries.getByRole("button", { name: "1. d4" })).toBeVisible();
    await expect(proof).toHaveTextContent("request quality: browser, tool");
    await waitFor(() => expect(status).toHaveTextContent("Analysis complete"));
    await expect(analysisQueries.getByRole("button", { name: "1. d4" })).toBeVisible();

    await userEvent.click(analysisQueries.getByRole("button", { name: "1. e4" }));
    await expect(canvas.getByTestId("branch-status")).toHaveTextContent("Move played locally: e4.");
    await expectSessionHistory(canvasElement, ["Initial position", "White, move 1, e4"]);
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 1, e4");
    await waitFor(() => expect(proof).toHaveTextContent("observe:not_requested"));
  },
};

export const OpponentImmediate: Story = {
  name: "Local line — immediate opponent move",
  render: () =>
    workspace({
      analysisClient: storyCandidateAnalysisClient(["g1f3"]),
      gameClient: storyGameClient(STORY_BLACK_SUBJECT_GAME_DETAIL),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await loadGame(canvas, GAME_UUID);
    await userEvent.click(await canvas.findByRole("button", { name: "Black, move 1, e5" }));
    await userEvent.click(await canvas.findByRole("button", { name: "2. Nf3" }));
    await expectSessionHistory(canvasElement, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 2, Nf3");
    await expectPreferredMoveState(canvasElement, "empty");
    await expectPositionReachFrequency(canvasElement, "available", "Black", "2 / 10 games", "20%");
  },
};

export const ConstrainedStoredPrefixAndLocalLine: Story = {
  name: "Stored prefix and local line — Constrained",
  parameters: storyViewport("constrained-412"),
  render: () =>
    workspace({
      analysisClient: storyCandidateAnalysisClient(["g1f3"]),
      gameClient: storyGameClient(STORY_BLACK_SUBJECT_GAME_DETAIL),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await loadGame(canvas, GAME_UUID);
    await userEvent.click(await canvas.findByRole("button", { name: "Black, move 1, e5" }));
    await userEvent.click(await canvas.findByRole("button", { name: "2. Nf3" }));
    await expectSessionHistory(canvasElement, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 2, Nf3");
    await expectPreferredMoveState(canvasElement, "empty");
    await expectPositionReachFrequency(canvasElement, "available", "Black", "2 / 10 games", "20%");
    await expectNoHorizontalOverflow(canvasElement);
  },
};

export const CandidateActivation: Story = {
  name: "Candidate — Best line uses local move path",
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
    await expect(canvas.getByTestId("branch-status")).toHaveTextContent("Move played locally: e4.");
    await expectPreferredMoveState(canvasElement, "empty");
    await expectPositionReachFrequency(canvasElement, "available", "Black", "2 / 10 games", "20%");
  },
};

export const NavigationAndReplacement: Story = {
  name: "Navigation — local history and replacement truncation",
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
  name: "Flip — preserves FEN and cancels pending staging",
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
    await expect(canvas.getByTestId("branch-status")).toHaveTextContent(
      "Flipped to Black at the bottom.",
    );
    await expect(await sharedPositionSummary(canvasElement)).toHaveTextContent(
      "OrientationBlack at the bottom",
    );
    await expectPositionSquares(canvasElement, "e2", 0);
    await expectPositionSquares(canvasElement, "e4", 1);
    await expectSessionHistory(canvasElement, ["Initial position", "White, move 1, e4"]);
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 1, e4");
  },
};
export const Promotion: Story = {
  name: "Promotion — selected piece stages a child preview",
  render: () =>
    workspace({
      analysisClient: storyCandidateAnalysisClient(["e7e8q"]),
      gameClient: storyGameClient(STORY_PROMOTION_GAME_DETAIL),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await loadGame(canvas, GAME_UUID);
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
    await expectSessionHistory(canvasElement, ["Initial position", "White, move 1, e8=N"]);
  },
};
export const KeyboardAndAccessibility: Story = {
  name: "Keyboard and accessibility — bounded workspace",
  parameters: storyViewport("constrained-412"),
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
    await expect(canvas.getByRole("button", { name: "White, move 1, e4" })).toHaveFocus();
    await expectPositionSquares(canvasElement, "e2", 0);
    await expectPositionSquares(canvasElement, "e4", 1);
    await expectNoHorizontalOverflow(canvasElement);
    await expectPreferredMoveState(canvasElement, "first-choice");
    await expectPositionReachFrequency(canvasElement, "available", "White", "3 / 10 games", "30%");
  },
};
export const Accessibility: Story = {
  name: "Accessibility — semantic controls and no overflow",
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

export const ResponseDistributionIntegration: Story = {
  name: "Response distribution — integrated move flow",
  render: () =>
    workspace({
      gameClient: storyGameClient(STORY_BLACK_SUBJECT_GAME_DETAIL),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const engineLane = canvas.getByTestId("repertoire-engine-lane");
    const analysisTab = within(engineLane).getByRole("tab", { name: "Analysis" });
    const responsesTab = within(engineLane).getByRole("tab", { name: "Move responses" });
    await expect(analysisTab).toHaveAttribute("aria-selected", "true");
    await loadGame(canvas, GAME_UUID);
    await userEvent.click(await canvas.findByRole("button", { name: "Black, move 1, e5" }));
    await userEvent.click(responsesTab);

    const distribution = canvas.getByTestId("move-response-distribution");
    const distributionQueries = within(distribution);
    await expect(distribution).toHaveAttribute("data-state", "available");
    await expect(
      distributionQueries.getByText("Black repertoire colour", { exact: true }),
    ).toBeVisible();
    await expect(
      distributionQueries.getByRole("button", { name: /Nf3, 4 occurrences, 33.3%/ }),
    ).toBeVisible();
    await expect(
      distributionQueries.getByText(
        "12 outgoing move occurrences observed in 10 matching Black repertoire games.",
      ),
    ).toBeVisible();
    await expect(distributionQueries.queryByText("Queen's Pawn Game")).not.toBeInTheDocument();

    const other = distributionQueries.getByRole("button", { name: /Show other replies/ });
    await userEvent.click(other);
    await expect(other).toHaveAttribute("aria-expanded", "true");
    await expect(
      distributionQueries.getByRole("button", { name: /Bc4, 1 occurrences, 8.3%/ }),
    ).toBeVisible();
    await userEvent.click(other);
    await expect(other).toHaveAttribute("aria-expanded", "false");
    await userEvent.click(analysisTab);
    await expect(canvas.getByTestId("tabs-panel-move-responses")).toHaveAttribute("hidden");
    await expectNoHorizontalOverflow(canvasElement);
  },
};
