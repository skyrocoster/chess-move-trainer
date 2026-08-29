import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import ViewerWorkspace from "./ViewerWorkspace";
import styles from "./Stage1Story.module.css";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "./viewerFixtures";
import { PROMOTION_GAME } from "./viewerStoryFixtures";
import {
  candidatePromotionInteractionPlay,
  completeGameLookup,
  storyCandidateAnalysisClient,
  submit,
} from "./viewerStoryHelpers";

const meta = {
  title: "Application/Viewer/Workspace Analysis",
  component: ViewerWorkspace,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof ViewerWorkspace>;

export default meta;
type Story = StoryObj<typeof meta>;

const frame = (children: React.ReactNode) => <main className={styles.frame}>{children}</main>;

export const CandidateActivation: Story = {
  name: "Controlled candidate activation",
  args: {
    lookup: completeGameLookup(),
    analysisClient: storyCandidateAnalysisClient(),
  },
  render: (args) => frame(<ViewerWorkspace {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await expect(canvas.getByText("Analysis complete")).toBeVisible();

    const bestLine = canvas.getByRole("button", { name: "1. e4" });
    await expect(canvas.getAllByRole("button", { name: /^1\./ })).toHaveLength(5);
    await expect(bestLine.querySelectorAll("button")).toHaveLength(0);

    await bestLine.focus();
    await userEvent.keyboard("{Enter}");
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    );
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("1. e4");
    await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
    await expect(canvas.getByRole("group", { name: /ply 0, Black at the bottom/ })).toBeVisible();
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    );

    await userEvent.click(
      within(canvas.getByTestId("interactive-board-adapter")).getByRole("button", {
        name: "Reset",
      }),
    );
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      VIEWER_GAME.positions[0].fen,
    );
    const alternativeLine = canvas.getByRole("button", { name: "1. d4" });
    await userEvent.click(alternativeLine);
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1",
    );
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("1. d4");
  },
};

export const CandidateSurface: Story = {
  name: "Controlled candidate surface",
  args: {
    lookup: completeGameLookup(),
    analysisClient: storyCandidateAnalysisClient(),
  },
  render: (args) => frame(<ViewerWorkspace {...args} />),
  play: async ({ canvasElement }) => {
    await submit(within(canvasElement), VIEWER_GAME_UUID, "0");
  },
};

export const CandidatePromotion: Story = {
  name: "Controlled promotion candidate",
  args: {
    lookup: completeGameLookup(PROMOTION_GAME),
    analysisClient: storyCandidateAnalysisClient(["e7e8q", "e7e8r", "e7e8b", "e7e8n"]),
  },
  render: (args) => frame(<ViewerWorkspace {...args} />),
  play: candidatePromotionInteractionPlay,
};

export const CandidatePromotionSurface: Story = {
  name: "Controlled promotion candidate surface",
  args: {
    lookup: completeGameLookup(PROMOTION_GAME),
    analysisClient: storyCandidateAnalysisClient(["e7e8q", "e7e8r", "e7e8b", "e7e8n"]),
  },
  render: (args) => frame(<ViewerWorkspace {...args} />),
  play: async ({ canvasElement }) => {
    await submit(within(canvasElement), VIEWER_GAME_UUID, "0");
  },
};
