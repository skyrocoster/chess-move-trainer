import { expect, fn, userEvent, waitFor, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import ViewerWorkspace from "./ViewerWorkspace";
import type { AnalysisClient } from "./analysisApi";
import type { Game } from "./gameModel";
import type { GameLookup, GameLookupFailure } from "./positionApi";
import styles from "./Stage1Story.module.css";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "./viewerFixtures";

const meta = {
  title: "Application/Viewer/Workspace",
  component: ViewerWorkspace,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof ViewerWorkspace>;

export default meta;
type Story = StoryObj<typeof meta>;

const frame = (children: React.ReactNode) => <main className={styles.frame}>{children}</main>;
const constrained = (children: React.ReactNode) => (
  <main className={styles.frame}>
    <div className={styles.constrained}>{children}</div>
  </main>
);

function completeGameLookup(game: Game = VIEWER_GAME): GameLookup {
  return fn(async (_uuid, initialPly) => ({
    status: "success" as const,
    game: { ...game, initial_ply: initialPly ?? 0 },
  }));
}

function failureLookup(status: GameLookupFailure): GameLookup {
  return fn(async () => ({ status }));
}

function storyAnalysisClient(): AnalysisClient {
  return {
    observe: fn(async (fen) => ({
      status: "success" as const,
      data: { fen, eligibility: "missing" as const, result: null, status: null, terminal: false },
    })),
    enqueue: fn(async () => {
      throw new Error("Stage 1 workspace stories do not exercise analysis actions");
    }),
    status: fn(async () => ({
      status: "success" as const,
      data: {
        fen: VIEWER_GAME.positions[0].fen,
        state: null,
        completed_at: null,
        error_code: null,
      },
    })),
  };
}

const pendingLookup: GameLookup = () => new Promise(() => {});
const blackGame: Game = { ...VIEWER_GAME, subject_color: "black" };
const promotionGame: Game = {
  game_uuid: VIEWER_GAME_UUID,
  initial_ply: 0,
  subject_color: "white",
  source_url: "https://www.chess.com/game/live/140399891142",
  positions: [
    {
      ply: 0,
      fen: "k7/4P3/8/8/8/8/8/4K3 w - - 0 1",
      san: null,
    },
  ],
};
const singlePositionGame = (fen: string): Game => ({
  ...VIEWER_GAME,
  positions: [{ ply: 0, fen, san: null }],
});
const castlingGame = singlePositionGame("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1");
const enPassantGame = singlePositionGame("4k3/3p4/8/4P3/8/8/8/4K3 b - - 0 1");
const terminalGame = singlePositionGame("7k/5Q2/p5K1/8/8/8/8/8 b - - 0 1");
const unsafeGame: Game = {
  ...VIEWER_GAME,
  source_url: "https://example.com/game/live/unsafe",
};

async function submit(canvas: ReturnType<typeof within>, uuid = VIEWER_GAME_UUID, ply?: string) {
  await userEvent.type(canvas.getByLabelText("Game UUID"), uuid);
  if (ply !== undefined) {
    await userEvent.type(canvas.getByLabelText(/Ply/), ply);
  }
  await userEvent.click(canvas.getByRole("button", { name: "Load game" }));
}

async function keyboardMove(canvasElement: HTMLElement, sourceSquare: string, arrows: string) {
  const piece = canvasElement.querySelector<HTMLElement>(
    `[data-square="${sourceSquare}"] [aria-roledescription="draggable"]`,
  );
  if (!piece) {
    throw new Error(`Unable to start a keyboard move from ${sourceSquare}.`);
  }

  piece.focus();
  await userEvent.keyboard("{Enter}");
  for (const arrow of arrows.match(/\{[^}]+\}/g) ?? []) {
    await userEvent.keyboard(arrow);
  }
  await userEvent.keyboard("{Enter}");
}

const loadingPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  await submit(canvas);
  await expect(canvas.getByText("Loading the complete game...")).toBeVisible();
  await expect(canvas.getByRole("button", { name: "Load game" })).toBeDisabled();
  await expect(canvas.getByRole("button", { name: "Previous" })).toBeDisabled();
  await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
  await expect(canvas.getByRole("button", { name: "Reset" })).toBeEnabled();
  await expect(canvas.getByRole("img", { name: /standard starting position/ })).toBeVisible();
};

const initialPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  await submit(canvas, VIEWER_GAME_UUID, "0");
  const contextButton = canvas.getByRole("button", { name: "Game Context" });
  const sourceLink = canvas.getByRole("link", { name: "Chess.com game" });
  const analysis = await canvas.findByText("Analysis available on request");
  await expect(canvas.getByText("Ply 0 of 3")).toBeVisible();
  await expect(
    canvas.getByText("Ply 0 of 3: Initial position", { exact: true }),
  ).toBeInTheDocument();
  await expect(canvas.getByText("Initial position")).toBeVisible();
  await expect(canvas.getByRole("button", { name: "Previous" })).toBeDisabled();
  await expect(canvas.getByRole("button", { name: "Next" })).toBeEnabled();
  await expect(contextButton).toHaveAttribute("aria-expanded", "true");
  await expect(sourceLink.compareDocumentPosition(analysis)).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  await userEvent.click(contextButton);
  await expect(contextButton).toHaveAttribute("aria-expanded", "false");
  await expect(canvas.queryByText("Analysis available on request")).not.toBeInTheDocument();
  await userEvent.click(contextButton);
  await expect(canvas.getByText("Analysis available on request")).toBeVisible();
};

const intermediatePlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  await submit(canvas, VIEWER_GAME_UUID, "1");
  await expect(canvas.getByText("Ply 1 of 3")).toBeVisible();
  await expect(canvas.getByRole("button", { name: "Previous" })).toBeEnabled();
  await expect(canvas.getByRole("button", { name: "Next" })).toBeEnabled();
  await userEvent.click(canvas.getByRole("button", { name: "Next" }));
  await expect(canvas.getByText("Ply 2 of 3")).toBeVisible();
  await expect(canvas.getByText("Ply 2 of 3: e5", { exact: true })).toBeInTheDocument();
};

const finalPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  await submit(canvas, VIEWER_GAME_UUID, "3");
  await expect(canvas.getByText("Ply 3 of 3")).toBeVisible();
  await expect(canvas.getByRole("button", { name: "Previous" })).toBeEnabled();
  await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
};

export const Wide: Story = {
  name: "Empty - Wide",
  args: { lookup: completeGameLookup() },
  render: () =>
    frame(<ViewerWorkspace lookup={completeGameLookup()} analysisClient={storyAnalysisClient()} />),
};

export const Constrained: Story = {
  name: "Empty - Constrained",
  args: { lookup: completeGameLookup() },
  render: () =>
    constrained(
      <ViewerWorkspace lookup={completeGameLookup()} analysisClient={storyAnalysisClient()} />,
    ),
};

export const LoadingWide: Story = {
  name: "Loading - Wide",
  args: { lookup: pendingLookup },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: loadingPlay,
};

export const LoadingConstrained: Story = {
  name: "Loading - Constrained",
  args: { lookup: pendingLookup },
  render: (args) =>
    constrained(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: loadingPlay,
};

export const InitialBoundary: Story = {
  name: "Initial boundary",
  args: { lookup: completeGameLookup() },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: initialPlay,
};

export const IntermediateTraversal: Story = {
  name: "Intermediate traversal",
  args: { lookup: completeGameLookup() },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: intermediatePlay,
};

export const FinalBoundary: Story = {
  name: "Final boundary",
  args: { lookup: completeGameLookup() },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: finalPlay,
};

export const BlackSubject: Story = {
  name: "Success - Black subject",
  args: { lookup: completeGameLookup(blackGame) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: initialPlay,
};

export const UnsafeSource: Story = {
  name: "Success - Unsafe source unavailable",
  args: { lookup: completeGameLookup(unsafeGame) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas);
    await expect(canvas.getByText("Source unavailable")).toBeVisible();
    await expect(canvas.queryByRole("link", { name: "Chess.com game" })).not.toBeInTheDocument();
  },
};

function failureStory(status: GameLookupFailure): Story {
  const heading =
    status === "game_not_found"
      ? "Game not found"
      : status === "position_not_found"
        ? "Position not found"
        : status === "corpus_unavailable"
          ? "Corpus unavailable"
          : status === "game_unavailable"
            ? "Game unavailable"
            : "Unable to load game";
  return {
    args: { lookup: failureLookup(status) },
    render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
    play: async ({ canvasElement }) => {
      const canvas = within(canvasElement);
      await submit(canvas);
      await expect(canvas.getByRole("heading", { name: heading, level: 2 })).toBeVisible();
    },
  };
}

export const GameNotFound: Story = {
  name: "Game not found - Wide",
  ...failureStory("game_not_found"),
};
export const PositionNotFound: Story = {
  name: "Position not found - Wide",
  ...failureStory("position_not_found"),
};
export const CorpusUnavailable: Story = {
  name: "Corpus unavailable - Wide",
  ...failureStory("corpus_unavailable"),
};
export const GameUnavailable: Story = {
  name: "Game unavailable - Wide",
  ...failureStory("game_unavailable"),
};
export const UnableToLoadGame: Story = {
  name: "Unable to load game - Wide",
  ...failureStory("unexpected_failure"),
};

export const ReplacementFailure: Story = {
  name: "Replacement failure preserves prior game",
  render: () => {
    let calls = 0;
    const lookup: GameLookup = async (_uuid, initialPly) => {
      calls += 1;
      return calls === 1
        ? { status: "success", game: { ...VIEWER_GAME, initial_ply: initialPly ?? 0 } }
        : { status: "game_unavailable" };
    };
    return frame(<ViewerWorkspace lookup={lookup} analysisClient={storyAnalysisClient()} />);
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "1");
    await expect(canvas.getByText("Ply 1 of 3")).toBeVisible();
    await userEvent.clear(canvas.getByLabelText(/Ply/));
    await userEvent.type(canvas.getByLabelText(/Ply/), "2");
    await userEvent.click(canvas.getByRole("button", { name: "Load game" }));
    await expect(canvas.getByRole("heading", { name: "Game unavailable", level: 2 })).toBeVisible();
    await expect(canvas.getByText("Ply 1 of 3")).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Next" })).toBeEnabled();
  },
};

export const Reset: Story = {
  name: "Reset returns to empty state",
  args: { lookup: completeGameLookup() },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas);
    await expect(canvas.getByText("Ply 0 of 3")).toBeVisible();
    const loaderForm = canvas.getByLabelText("Game UUID").closest("form");
    if (!loaderForm) {
      throw new Error("Game Loader form was not rendered");
    }
    await userEvent.click(within(loaderForm).getByRole("button", { name: "Reset" }));
    await expect(canvas.getAllByText("No game loaded")).toHaveLength(2);
    await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
  },
};

export const BranchFromInitialPosition: Story = {
  name: "Branch - empty at initial position",
  args: { lookup: completeGameLookup() },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    const branch = within(canvas.getByTestId("interactive-board-adapter"));
    await expect(canvas.getByText("Ply 0 of 3")).toBeVisible();
    await expect(canvas.getByText("Initial position")).toBeVisible();
    await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(
      VIEWER_GAME.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      VIEWER_GAME.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
    await expect(branch.getByRole("button", { name: "Undo" })).toBeDisabled();
    await expect(branch.getByRole("button", { name: "Reset" })).toBeDisabled();
  },
};

export const BranchNavigationGate: Story = {
  name: "Branch - navigation gated",
  args: { lookup: completeGameLookup() },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await expect(canvas.getByText("Ply 0 of 3")).toBeVisible();
    await keyboardMove(canvasElement, "e2", "{ArrowUp}{ArrowUp}");
    await expect(canvas.getByTestId("branch-san")).not.toHaveTextContent("No branch moves yet");
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    );
    await expect(canvas.getByTestId("branch-status")).toHaveTextContent(
      "Branch move committed: e3.",
    );
    await expect(canvas.getByRole("button", { name: "Previous" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
    await expect(canvas.getByText("Initial position")).toBeVisible();
  },
};

export const BranchPromotion: Story = {
  name: "Branch - promotion fixture",
  args: { lookup: completeGameLookup(promotionGame) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await expect(canvas.getByText("Ply 0 of 0")).toBeVisible();
    await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(
      promotionGame.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      promotionGame.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
  },
};

const branchPromotionInteractionPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  const body = within(canvasElement.ownerDocument.body);
  await submit(canvas, VIEWER_GAME_UUID, "0");
  await expect(canvas.getByText("Ply 0 of 0")).toBeVisible();
  await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(
    promotionGame.positions[0].fen,
  );
  await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
    promotionGame.positions[0].fen,
  );

  await keyboardMove(canvasElement, "e7", "{ArrowUp}{ArrowUp}");
  await waitFor(() =>
    expect(body.getByRole("dialog", { name: "Choose a promotion piece" })).toBeVisible(),
  );
  await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
    promotionGame.positions[0].fen,
  );
  await userEvent.keyboard("{Escape}");
  await expect(body.queryByRole("dialog")).not.toBeInTheDocument();
  await expect(canvas.getByTestId("branch-status")).toHaveTextContent(
    "Promotion cancelled; the captured position is unchanged.",
  );

  await keyboardMove(canvasElement, "e7", "{ArrowUp}{ArrowUp}");
  await waitFor(() =>
    expect(body.getByRole("dialog", { name: "Choose a promotion piece" })).toBeVisible(),
  );
  await userEvent.click(body.getByRole("button", { name: "Promote to knight" }));
  await expect(canvas.getByTestId("branch-san")).toHaveTextContent("1. e8=N");
  await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
    "k3N3/8/8/8/8/8/8/4K3 b - - 0 1",
  );
};

export const BranchPromotionInteraction: Story = {
  name: "Branch - promotion interaction",
  args: { lookup: completeGameLookup(promotionGame) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: branchPromotionInteractionPlay,
};

export const BranchCastling: Story = {
  name: "Branch - castling fixture",
  args: { lookup: completeGameLookup(castlingGame) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await expect(canvas.getByText("Ply 0 of 0")).toBeVisible();
    await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(
      castlingGame.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      castlingGame.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
  },
};

export const BranchEnPassant: Story = {
  name: "Branch - en-passant fixture",
  args: { lookup: completeGameLookup(enPassantGame) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await expect(canvas.getByText("Ply 0 of 0")).toBeVisible();
    await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(
      enPassantGame.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      enPassantGame.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
  },
};

export const BranchTerminal: Story = {
  name: "Branch - terminal fixture",
  args: { lookup: completeGameLookup(terminalGame) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await expect(canvas.getByText("Ply 0 of 0")).toBeVisible();
    await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(
      terminalGame.positions[0].fen,
    );
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      terminalGame.positions[0].fen,
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
