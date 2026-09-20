import { useMemo, useState } from "react";
import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { expect, userEvent, waitFor, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { storyCandidateAnalysisClient } from "../analysis/analysisStoryClients";
import RepertoireBuilderWorkspace from "./RepertoireBuilderWorkspace";
import { PREFERRED_MOVE_SOURCE_FEN } from "./preferredMoveStoryFixtures";
import {
  expectDateFreePreferredPanel,
  expectPreferredActions,
  expectPreferredMoveState,
} from "./repertoireBuilderStoryAssertions";
import { workspace } from "./repertoireBuilderStoryRender";
import {
  type StoryPreferredMoveRequest,
  storyPreferredMoveClient,
  storyPreferredMoveDateWindow,
} from "./repertoireBuilderStoryHelpers";

function CleanPreferredTimelineStory() {
  const [requests, setRequests] = useState<StoryPreferredMoveRequest[]>([]);
  const preferredMoveClient = useMemo(
    () =>
      storyPreferredMoveClient({
        relationship: "empty",
        onRequest: (request) => setRequests((current) => [...current, request]),
      }),
    [],
  );

  return (
    <>
      {workspace(
        { preferredMoveClient, analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
        {},
        { observedInGames: false, distinctGameCount: 0, totalGameCount: 0 },
      )}
      <output data-testid="clean-preferred-request-log" hidden>
        {JSON.stringify(requests)}
      </output>
    </>
  );
}

const meta = {
  title: "Production/Application/Repertoire Builder/Workspace/Preferred Move",
  tags: ["status-production"],
  component: RepertoireBuilderWorkspace,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof RepertoireBuilderWorkspace>;

export default meta;
type Story = StoryObj<typeof meta>;

export const CleanPreferredTimelineNovelParent: Story = {
  name: "Clean preferred timeline and novel parent",
  render: () => <CleanPreferredTimelineStory />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const requestLog = canvas.getByTestId("clean-preferred-request-log");
    const { today, tomorrow } = storyPreferredMoveDateWindow();
    const expectedFen = PREFERRED_MOVE_SOURCE_FEN;

    await expectPreferredMoveState(canvasElement, "empty");
    await expect(canvas.getByText("Never seen as White")).toBeVisible();
    await expect(
      canvas.queryByText("This position isn't in your corpus, so it can't be saved yet."),
    ).not.toBeInTheDocument();
    await expectPreferredActions(canvasElement, []);
    await expectDateFreePreferredPanel(canvasElement);
    await expect(requestLog).toHaveTextContent(
      JSON.stringify([{ method: "GET", fen: expectedFen, from: today, until: tomorrow }]),
    );

    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expectPreferredMoveState(canvasElement, "first-choice");
    await expect(canvas.getByRole("button", { name: "Save e4" })).toBeEnabled();
    await userEvent.click(canvas.getByRole("button", { name: "Save e4" }));
    await waitFor(() =>
      expect(canvas.getByTestId("branch-status")).toHaveTextContent("Preferred move saved."),
    );
    await expectPreferredMoveState(canvasElement, "matching");
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent(/^Saved\s*e4\s*e2e4$/);
    // A save issues exactly one PUT and then refreshes. The refresh is one or
    // more GETs: invalidation plus the refresh-key refetch can each trigger a
    // read, and TanStack dedup behavior may vary across patch upgrades, so
    // assert the mutation sequence rather than an exact GET count.
    await waitFor(() => {
      const logged = JSON.parse(requestLog.textContent ?? "[]") as StoryPreferredMoveRequest[];
      expect(logged[0]).toEqual({ method: "GET", fen: expectedFen, from: today, until: tomorrow });
      expect(logged.filter((request) => request.method !== "GET")).toEqual([
        { method: "PUT", fen: expectedFen, move_uci: "e2e4", effective_from: today },
      ]);
      expect(logged.filter((request) => request.method === "GET").length).toBeGreaterThanOrEqual(2);
    });

    await userEvent.click(canvas.getByRole("button", { name: "Remove" }));
    const dialog = await within(canvasElement.ownerDocument.body).findByRole("alertdialog", {
      name: "Remove preferred move?",
    });
    await userEvent.click(within(dialog).getByRole("button", { name: "Remove" }));
    await waitFor(() =>
      expect(canvas.getByTestId("branch-status")).toHaveTextContent("Preferred move removed."),
    );
    await expectPreferredMoveState(canvasElement, "first-choice");
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("None yet");
    await expect(canvas.getByTestId("selected-move")).toHaveTextContent(/^Selected\s*e4\s*e2e4$/);
    await expectPreferredActions(canvasElement, ["Save e4"]);
    await expectDateFreePreferredPanel(canvasElement);
    // Same tolerance as the post-save check: exactly one PUT and one DELETE,
    // with one or more refreshing GETs around them.
    await waitFor(() => {
      const logged = JSON.parse(requestLog.textContent ?? "[]") as StoryPreferredMoveRequest[];
      expect(logged[0]).toEqual({ method: "GET", fen: expectedFen, from: today, until: tomorrow });
      expect(logged.filter((request) => request.method !== "GET")).toEqual([
        { method: "PUT", fen: expectedFen, move_uci: "e2e4", effective_from: today },
        { method: "DELETE", fen: expectedFen, effective_from: today },
      ]);
      expect(logged.filter((request) => request.method === "GET").length).toBeGreaterThanOrEqual(3);
    });
  },
};
