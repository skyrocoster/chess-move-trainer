import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import ViewerWorkspace from "./ViewerWorkspace";
import styles from "./Stage1Story.module.css";
import {
  CASTLING_GAME,
  EN_PASSANT_GAME,
  PROMOTION_GAME,
  TERMINAL_GAME,
} from "./viewerStoryFixtures";
import { VIEWER_GAME_UUID } from "./viewerFixtures";
import {
  branchPromotionInteractionPlay,
  completeGameLookup,
  keyboardMove,
  storyAnalysisClient,
  submit,
} from "./viewerStoryHelpers";

const meta = {
  title: "Application/Viewer/Workspace",
  component: ViewerWorkspace,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof ViewerWorkspace>;

export default meta;
type Story = StoryObj<typeof meta>;

const frame = (children: React.ReactNode) => <main className={styles.frame}>{children}</main>;

export const BranchPromotion: Story = {
  name: "Branch - promotion fixture",
  args: { lookup: completeGameLookup(PROMOTION_GAME) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await expect(canvas.getByText("Ply 0 of 0")).toBeVisible();
    await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(
      PROMOTION_GAME.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      PROMOTION_GAME.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
  },
};

export const BranchPromotionInteraction: Story = {
  name: "Branch - promotion interaction",
  args: { lookup: completeGameLookup(PROMOTION_GAME) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: branchPromotionInteractionPlay,
};

export const BranchCastling: Story = {
  name: "Branch - castling fixture",
  args: { lookup: completeGameLookup(CASTLING_GAME) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await expect(canvas.getByText("Ply 0 of 0")).toBeVisible();
    await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(
      CASTLING_GAME.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      CASTLING_GAME.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
  },
};

export const BranchEnPassant: Story = {
  name: "Branch - en-passant fixture",
  args: { lookup: completeGameLookup(EN_PASSANT_GAME) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await expect(canvas.getByText("Ply 0 of 0")).toBeVisible();
    await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(
      EN_PASSANT_GAME.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      EN_PASSANT_GAME.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
  },
};

export const BranchTerminal: Story = {
  name: "Branch - terminal fixture",
  args: { lookup: completeGameLookup(TERMINAL_GAME) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await expect(canvas.getByText("Ply 0 of 0")).toBeVisible();
    await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(
      TERMINAL_GAME.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      TERMINAL_GAME.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
  },
};

export const BranchReplacementDiscard: Story = {
  name: "Branch - replacement discards line",
  args: { lookup: completeGameLookup() },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await keyboardMove(canvasElement, "e2", "{ArrowUp}{ArrowUp}");
    await expect(canvas.getByTestId("branch-san")).not.toHaveTextContent("No branch moves yet");
    await userEvent.clear(canvas.getByLabelText(/Ply/));
    await userEvent.type(canvas.getByLabelText(/Ply/), "1");
    await userEvent.click(canvas.getByRole("button", { name: "Load game" }));
    await expect(canvas.getByText("Ply 1 of 3")).toBeVisible();
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
  },
};
