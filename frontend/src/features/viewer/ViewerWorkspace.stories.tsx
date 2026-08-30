import { expect, fn, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import ViewerWorkspace from "./ViewerWorkspace";
import type { Game } from "./gameModel";
import type { GameLookup } from "./positionApi";
import type { PositionContextClient, PositionContextResponse } from "./positionContextApi";
import styles from "./Stage1Story.module.css";
import { VIEWER_GAME, VIEWER_GAME_UUID, UNSAFE_SOURCE_GAME } from "./viewerFixtures";
import {
  CASTLING_GAME,
  EN_PASSANT_GAME,
  PROMOTION_GAME,
  TERMINAL_GAME,
} from "./viewerStoryFixtures";
import {
  completeGameLookup,
  branchPromotionInteractionPlay,
  finalPlay,
  keyboardMove,
  pendingLookup,
  storyAnalysisClient,
  submit,
} from "./viewerStoryHelpers";

function storyPositionContextClient(
  valuesFor: (fen: string) => Omit<PositionContextResponse, "fen"> = () => ({
    overall_exists: true,
    white_count: 2,
    black_count: 1,
    white_total: 10,
    black_total: 10,
  }),
): PositionContextClient {
  return fn(async (fen) => ({
    status: "success" as const,
    data: { fen, ...valuesFor(fen) },
  }));
}

function viewerPositionContext(fen: string): Omit<PositionContextResponse, "fen"> {
  const index = VIEWER_GAME.positions.findIndex((position) => position.fen === fen);
  return {
    overall_exists: true,
    white_count: index + 2,
    black_count: index + 1,
    white_total: 10,
    black_total: 10,
  };
}
const positionContextClient = storyPositionContextClient(viewerPositionContext);
const blackGame: Game = { ...VIEWER_GAME, subject_color: "black" };
const unavailablePositionContextClient: PositionContextClient = fn(async () => ({
  status: "position_context_unavailable" as const,
}));
const branchPositionContextClient = storyPositionContextClient((fen) =>
  fen === VIEWER_GAME.positions[0].fen
    ? {
        overall_exists: true,
        white_count: 2,
        black_count: 1,
        white_total: 10,
        black_total: 10,
      }
    : {
        overall_exists: true,
        white_count: 7,
        black_count: 6,
        white_total: 10,
        black_total: 10,
      },
);
const meta = {
  title: "Application/Viewer/Workspace",
  component: ViewerWorkspace,
  parameters: { layout: "fullscreen" },
  args: { positionContextClient },
} satisfies Meta<typeof ViewerWorkspace>;
export default meta;
type Story = StoryObj<typeof meta>;
const frame = (children: React.ReactNode) => <main className={styles.frame}>{children}</main>;
const constrained = (children: React.ReactNode) => (
  <main className={styles.frame}>
    <div className={styles.constrained}>{children}</div>
  </main>
);
const loadingPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  await submit(canvas);
  await expect(canvas.getByText("Loading the complete game...")).toBeVisible();
  await expect(canvas.getByRole("button", { name: "Load game" })).toBeDisabled();
  await expect(canvas.getByRole("button", { name: "Previous" })).toBeDisabled();
  await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
  await expect(canvas.getByRole("button", { name: "Reset" })).toBeEnabled();
  await expect(canvas.getByRole("img", { name: /standard starting position/ })).toBeVisible();
  await expect(
    canvas.queryByRole("heading", { name: "Position reach frequency" }),
  ).not.toBeInTheDocument();
};
const initialPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  await submit(canvas, VIEWER_GAME_UUID, "0");
  const board = canvas.getByRole("group", { name: /ply 0,/ });
  const meter = canvas.getByRole("meter", { name: "Evaluation" });
  const initialOrientation = meter.getAttribute("data-orientation") ?? "white";
  const contextButton = canvas.getByRole("button", { name: "Game Context" });
  const history = within(canvas.getByRole("navigation", { name: "Move history" }));
  const sourceLink = canvas.getByRole("link", { name: "Chess.com game" });
  const analysis = await canvas.findByText("Analysis available on request");
  const initial = history.getByRole("button", { name: "Initial position" });
  await expect(canvas.getByText("Ply 0 of 3")).toBeVisible();
  await expect(
    canvas.getByText("Ply 0 of 3: Initial position", { exact: true }),
  ).toBeInTheDocument();
  await expect(initial).toBeVisible();
  await expect(initial).toHaveAttribute("aria-current", "step");
  await expect(await canvas.findByText("2 / 10 games", { exact: true })).toBeVisible();
  await expect(canvas.getByText("White repertoire colour", { exact: true })).toBeVisible();
  await expect(
    canvas.getByRole("meter", { name: "Position reach frequency as White" }),
  ).toBeVisible();
  await expect(canvas.getByRole("button", { name: "Previous" })).toBeDisabled();
  await expect(canvas.getByRole("button", { name: "Next" })).toBeEnabled();
  await expect(board).toHaveAttribute("aria-label", expect.stringContaining("at the bottom"));
  await expect(meter).toHaveAttribute("data-orientation", initialOrientation);
  const currentFen = canvas.getByTestId("branch-current-fen").textContent;
  await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
  await expect(meter).toHaveAttribute(
    "data-orientation",
    initialOrientation === "white" ? "black" : "white",
  );
  await expect(board).toHaveAttribute(
    "aria-label",
    expect.stringContaining(
      initialOrientation === "white" ? "Black at the bottom" : "White at the bottom",
    ),
  );
  await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(currentFen ?? "");
  await expect(canvas.getByText("Ply 0 of 3: Initial position", { exact: true })).toBeVisible();
  await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
  await expect(contextButton).toHaveAttribute("aria-expanded", "true");
  await expect(sourceLink.compareDocumentPosition(analysis)).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  await userEvent.click(contextButton);
  await expect(contextButton).toHaveAttribute("aria-expanded", "false");
  await expect(canvas.getByText("Analysis available on request")).toBeVisible();
  await userEvent.click(contextButton);
  await expect(canvas.getByText("Analysis available on request")).toBeVisible();
};
const intermediatePlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  await submit(canvas, VIEWER_GAME_UUID, "1");
  await expect(canvas.getByText("Ply 1 of 3")).toBeVisible();
  await expect(canvas.getByText("3 / 10 games", { exact: true })).toBeVisible();
  await expect(canvas.getByText("White repertoire colour", { exact: true })).toBeVisible();
  const history = within(canvas.getByRole("navigation", { name: "Move history" }));
  const e4 = history.getByRole("button", { name: "White, move 1, e4" });
  const e5 = history.getByRole("button", { name: "Black, move 1, e5" });
  await expect(e4).toHaveAttribute("aria-current", "step");
  const currentFen = canvas.getByTestId("branch-current-fen").textContent;
  await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
  await expect(canvas.getByRole("group", { name: /ply 1, Black at the bottom/ })).toBeVisible();
  await expect(canvas.getByText("3 / 10 games", { exact: true })).toBeVisible();
  await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(currentFen ?? "");
  await expect(canvas.getByRole("button", { name: "Previous" })).toBeEnabled();
  await expect(canvas.getByRole("button", { name: "Next" })).toBeEnabled();
  await userEvent.click(e5);
  await expect(canvas.getByText("Ply 2 of 3")).toBeVisible();
  await expect(canvas.getByText("4 / 10 games", { exact: true })).toBeVisible();
  await expect(e5).toHaveAttribute("aria-current", "step");
  await expect(e5).toHaveFocus();
  await expect(canvas.getByText("Ply 2 of 3: e5", { exact: true })).toBeInTheDocument();
  await userEvent.keyboard("{Home}");
  await expect(history.getByRole("button", { name: "Initial position" })).toHaveAttribute(
    "aria-current",
    "step",
  );
  await expect(history.getByRole("button", { name: "Initial position" })).toHaveFocus();
  await expect(canvas.getByText("Ply 0 of 3")).toBeVisible();
  await userEvent.keyboard("{End}");
  const finalMove = history.getByRole("button", { name: "White, move 2, Nf3" });
  await expect(finalMove).toHaveAttribute("aria-current", "step");
  await expect(finalMove).toHaveFocus();
  await expect(canvas.getByText("Ply 3 of 3: Nf3", { exact: true })).toBeInTheDocument();
};

const blackSubjectPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  await submit(canvas, VIEWER_GAME_UUID, "0");
  await expect(canvas.getByRole("group", { name: /ply 0, Black at the bottom/ })).toBeVisible();
  await expect(canvas.getByText("Black repertoire colour", { exact: true })).toBeVisible();
  await expect(canvas.getByText("1 / 10 games", { exact: true })).toBeVisible();
  await expect(
    canvas.getByRole("meter", { name: "Position reach frequency as Black" }),
  ).toBeVisible();
  await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
  await expect(canvas.getByRole("group", { name: /ply 0, White at the bottom/ })).toBeVisible();
  await expect(canvas.getByText("Black repertoire colour", { exact: true })).toBeVisible();
  await expect(canvas.getByText("1 / 10 games", { exact: true })).toBeVisible();
  await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
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
export const LoadedConstrained: Story = {
  name: "Loaded - Constrained",
  args: { lookup: completeGameLookup() },
  render: (args) =>
    constrained(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas);
    await expect(canvas.getByText("Ply 0 of 3", { exact: true })).toBeVisible();
    await expect(canvas.getByRole("navigation", { name: "Move history" })).toBeVisible();
    await expect(canvas.getByText("2 / 10 games", { exact: true })).toBeVisible();
  },
};
export const SeenCounts: Story = {
  name: "Reach frequency - selected colour updates",
  args: { lookup: completeGameLookup() },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await expect(canvas.getByRole("heading", { name: "Position reach frequency" })).toBeVisible();
    await expect(canvas.getByText("2 / 10 games", { exact: true })).toBeVisible();
    await expect(canvas.getByText("White repertoire colour", { exact: true })).toBeVisible();
  const history = within(canvas.getByRole("navigation", { name: "Move history" }));
    const e4 = history.getByRole("button", { name: "White, move 1, e4" });
    await userEvent.click(e4);
    await expect(canvas.getByText("Ply 1 of 3", { exact: true })).toBeVisible();
    await expect(e4).toHaveAttribute("aria-current", "step");
    await expect(e4).toHaveFocus();
    await expect(canvas.getByText("3 / 10 games", { exact: true })).toBeVisible();
    await userEvent.keyboard("{Home}");
    await expect(history.getByRole("button", { name: "Initial position" })).toHaveFocus();
  },
};
export const ZeroCounts: Story = {
  name: "Reach frequency - zero count",
  args: {
    lookup: completeGameLookup(),
    positionContextClient: storyPositionContextClient(() => ({
      overall_exists: true,
      white_count: 0,
      black_count: 0,
      white_total: 10,
      black_total: 10,
    })),
  },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas);
    await expect(canvas.getByText("0 / 10 games", { exact: true })).toBeVisible();
    await expect(canvas.getByText("White repertoire colour", { exact: true })).toBeVisible();
  },
};
export const AbsentPosition: Story = {
  name: "Reach frequency - absent position",
  args: {
    lookup: completeGameLookup(),
    positionContextClient: storyPositionContextClient(() => ({
      overall_exists: false,
      white_count: 4,
      black_count: 3,
      white_total: 10,
      black_total: 10,
    })),
  },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas);
    await expect(
      canvas.getByText(
        "This position is not present in the accepted game data for White.",
        { exact: true },
      ),
    ).toBeVisible();
    await expect(
      canvas.queryByRole("meter", { name: /Position reach frequency/ }),
    ).not.toBeInTheDocument();
  },
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
  play: blackSubjectPlay,
};
export const ReachUnavailable: Story = {
  name: "Success - Position reach unavailable",
  args: {
    lookup: completeGameLookup(),
    positionContextClient: unavailablePositionContextClient,
  },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas);
    await expect(canvas.getByText("Ply 0 of 3", { exact: true })).toBeVisible();
    await expect(canvas.getByText("Position reach data is unavailable.")).toBeVisible();
    await expect(
      canvas.queryByRole("meter", { name: /Position reach frequency/ }),
    ).not.toBeInTheDocument();
    await expect(canvas.getByRole("navigation", { name: "Move history" })).toBeVisible();
  },
};
export const ReachForcedColors: Story = {
  name: "Media emulation - reach frequency forced colors",
  args: { lookup: completeGameLookup() },
  render: (args) =>
    constrained(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas);
    await expect(canvas.getByRole("heading", { name: "Position reach frequency" })).toBeVisible();
    await expect(canvas.getByText("2 / 10 games", { exact: true })).toBeVisible();
    await expect(canvas.getByRole("meter", { name: "Position reach frequency as White" })).toBeVisible();
  },
};
export const UnsafeSource: Story = {
  name: "Success - Unsafe source unavailable",
  args: { lookup: completeGameLookup(UNSAFE_SOURCE_GAME) },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas);
    await expect(canvas.getByText("Source unavailable")).toBeVisible();
    await expect(canvas.queryByRole("link", { name: "Chess.com game" })).not.toBeInTheDocument();
  },
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
    return frame(
      <ViewerWorkspace
        lookup={lookup}
        analysisClient={storyAnalysisClient()}
        positionContextClient={positionContextClient}
      />,
    );
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "1");
    await expect(canvas.getByText("Ply 1 of 3")).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
    await expect(canvas.getByRole("group", { name: /ply 1, Black at the bottom/ })).toBeVisible();
    await userEvent.clear(canvas.getByLabelText(/Ply/));
    await userEvent.type(canvas.getByLabelText(/Ply/), "2");
    await userEvent.click(canvas.getByRole("button", { name: "Load game" }));
    await expect(canvas.getByRole("heading", { name: "Game unavailable", level: 2 })).toBeVisible();
    await expect(canvas.getByText("Ply 1 of 3")).toBeVisible();
    await expect(canvas.getByRole("group", { name: /ply 1, Black at the bottom/ })).toBeVisible();
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
    await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
    await expect(canvas.getByRole("group", { name: /ply 0, Black at the bottom/ })).toBeVisible();
    const loaderForm = canvas.getByLabelText("Game UUID").closest("form");
    if (!loaderForm) {
      throw new Error("Game Loader form was not rendered");
    }
    await userEvent.click(within(loaderForm).getByRole("button", { name: "Reset" }));
    await expect(canvas.getAllByText("No game loaded")).toHaveLength(2);
    await expect(
      canvas.getByRole("img", { name: /standard starting position, White at the bottom/ }),
    ).toBeVisible();
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
    await expect(canvas.getByRole("button", { name: "Initial position" })).toBeVisible();
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
  args: { lookup: completeGameLookup(), positionContextClient: branchPositionContextClient },
  render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await submit(canvas, VIEWER_GAME_UUID, "0");
    await expect(canvas.getByText("Ply 0 of 3")).toBeVisible();
    await expect(canvas.getByText("2 / 10 games", { exact: true })).toBeVisible();
    await keyboardMove(canvasElement, "e2", "{ArrowUp}{ArrowUp}");
    await expect(canvas.getByTestId("branch-san")).not.toHaveTextContent("No branch moves yet");
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    );
    await expect(canvas.getByTestId("branch-status")).toHaveTextContent(
      "Branch move committed: e3.",
    );
    await expect(canvas.getByText("7 / 10 games", { exact: true })).toBeVisible();
    const branchFen = canvas.getByTestId("branch-current-fen").textContent;
    const branchSan = canvas.getByTestId("branch-san").textContent;
    await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
    await expect(canvas.getByRole("group", { name: /ply 0, Black at the bottom/ })).toBeVisible();
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(branchFen ?? "");
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent(branchSan ?? "");
    await expect(canvas.getByRole("button", { name: "Previous" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Initial position" })).toBeVisible();
  },
};
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
