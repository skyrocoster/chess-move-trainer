import type { ComponentProps, ReactNode } from "react";
import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { Game } from "../viewer/gameModel";
import {
  completeGameLookup,
  storyAnalysisClient,
  storyCandidateAnalysisClient,
} from "../viewer/viewerStoryHelpers";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "../viewer/viewerFixtures";
import { PROMOTION_GAME } from "../viewer/viewerStoryFixtures";
import RepertoireBuilderWorkspace from "./RepertoireBuilderWorkspace";
import {
  expectNoHorizontalOverflow,
  loadGame,
  selectCurrentUtcDate,
  storyPositionContextClient,
  storyPreferredMoveClient,
  type StoryPositionContextOptions,
  type StoryPreferredMoveOptions,
} from "./repertoireBuilderStoryHelpers";

const meta = {
  title: "Application/Repertoire Builder/Workspace",
  component: RepertoireBuilderWorkspace,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof RepertoireBuilderWorkspace>;

export default meta;
type Story = StoryObj<typeof meta>;

export const BLACK_SUBJECT_GAME: Game = { ...VIEWER_GAME, subject_color: "black" };

const constrainedViewport = {
  viewport: {
    defaultViewport: "cmt-repertoire-constrained",
    options: {
      "cmt-repertoire-constrained": {
        name: "Constrained workspace",
        styles: { width: "412px", height: "915px" },
      },
    },
  },
};

function frame(children: ReactNode) {
  return <main>{children}</main>;
}

export function workspace(
  props: ComponentProps<typeof RepertoireBuilderWorkspace> = {},
  preferredOptions: StoryPreferredMoveOptions = {},
  contextOptions: StoryPositionContextOptions = {},
) {
  const analysisClient = props.analysisClient ?? storyAnalysisClient();
  const preferredMoveClient =
    props.preferredMoveClient ?? storyPreferredMoveClient(preferredOptions);
  const positionContextClient =
    props.positionContextClient ?? storyPositionContextClient(contextOptions);
  return frame(
    <RepertoireBuilderWorkspace
      {...props}
      analysisClient={analysisClient}
      preferredMoveClient={preferredMoveClient}
      positionContextClient={positionContextClient}
    />,
  );
}

async function verifyStandardWorkspace(canvasElement: HTMLElement) {
  const canvas = within(canvasElement);
  await expect(canvas.getByRole("heading", { name: "Repertoire Builder", level: 1 })).toBeVisible();
  await expect(
    canvas.getByRole("group", {
      name: "Chess board: standard starting position, White at the bottom",
    }),
  ).toBeVisible();
  await expect(canvas.getByTestId("position-summary")).toHaveTextContent(
    "Orientation: White at the bottom. Side to move: White.",
  );

  const description = canvas.getByRole("button", { name: "Position description" });
  description.focus();
  await expect(description).toHaveFocus();
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
    await expect(canvas.getByTestId("session-san-history")).toHaveTextContent("1. e4 1... e5");
    await expect(canvas.getByTestId("position-summary")).toHaveTextContent(
      "Orientation: Black at the bottom. Side to move: White.",
    );
  },
};

export const StagedMy: Story = {
  name: "Local line - staged my move",
  render: () =>
    workspace({
      analysisClient: storyCandidateAnalysisClient(["e2e4"]),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const startingFen = canvas.getByTestId("current-fen").textContent;
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("My move staged: e4.");
    await expect(canvas.getByTestId("current-fen")).toHaveTextContent(startingFen ?? "");
    await expect(canvas.getByTestId("session-san-history")).toHaveTextContent("No local moves yet");
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
    await expect(canvas.queryByTestId("staged-move")).not.toBeInTheDocument();
    await expect(canvas.getByTestId("session-status")).toHaveTextContent(
      "Opponent move played locally: Nf3.",
    );
    await expect(canvas.getByTestId("session-san-history")).toHaveTextContent(
      "1. e4 1... e5 2. Nf3",
    );
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
    const startingFen = canvas.getByTestId("current-fen").textContent;
    await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expect(canvas.getByTestId("current-fen")).not.toHaveTextContent(startingFen ?? "");
    await expect(canvas.getByTestId("session-san-history")).toHaveTextContent("1. e4");
    await expect(canvas.queryByTestId("staged-move")).not.toBeInTheDocument();
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
    await expect(canvas.getByTestId("session-san-history")).toHaveTextContent("1. e4 1... e5");

    await userEvent.click(canvas.getByRole("button", { name: "Previous" }));
    await expect(canvas.getByTestId("session-san-history")).toHaveTextContent("1. e4");
    await expect(canvas.getByRole("button", { name: "Next" })).toBeEnabled();
    await userEvent.click(await canvas.findByRole("button", { name: "1... e6" }));
    await expect(canvas.getByTestId("session-san-history")).toHaveTextContent("1. e4 1... e6");
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
    const stagedFen = canvas.getByTestId("current-fen").textContent;
    await expect(canvas.getByTestId("staged-move")).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
    await expect(canvas.queryByTestId("staged-move")).not.toBeInTheDocument();
    await expect(canvas.getByTestId("current-fen")).toHaveTextContent(stagedFen ?? "");
    await expect(canvas.getByTestId("position-summary")).toHaveTextContent(
      "Orientation: Black at the bottom. Side to move: White.",
    );
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expect(canvas.getByTestId("session-san-history")).toHaveTextContent("1. e4");
  },
};

export const Promotion: Story = {
  name: "Promotion - existing picker commits a local move",
  render: () =>
    workspace({
      analysisClient: storyCandidateAnalysisClient(["e7e8q"]),
      lookup: completeGameLookup(PROMOTION_GAME),
    }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await loadGame(canvas, VIEWER_GAME_UUID, "0");
    await userEvent.click(canvas.getByRole("button", { name: "Flip" }));
    await userEvent.click(await canvas.findByRole("button", { name: /1\. e8=Q/ }));
    await expect(body.getByRole("dialog", { name: "Choose a promotion piece" })).toBeVisible();
    await expect(canvas.getByTestId("current-fen")).toHaveTextContent(
      PROMOTION_GAME.positions[0].fen,
    );
    await userEvent.click(body.getByRole("button", { name: "Promote to knight" }));
    await expect(canvas.getByTestId("current-fen")).toHaveTextContent(
      "k3N3/8/8/8/8/8/8/4K3 b - - 0 1",
    );
    await expect(canvas.getByTestId("session-san-history")).toHaveTextContent("1. e8=N");
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
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("My move staged: e4.");
    await expect(candidate).toHaveFocus();
    await expectNoHorizontalOverflow(canvasElement);
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
      "true",
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
    await expect(canvas.getByText("Seen in 3 games as White")).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Add" })).toBeDisabled();
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("e4");
    await userEvent.click(canvas.getByRole("button", { name: "Add" }));
    await expect(canvas.getByText("Preferred move added.")).toBeVisible();
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("e4");
    await expect(canvas.getByRole("button", { name: "Effective date: Choose date" })).toBeVisible();
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
    await expect(canvas.getByText("Never seen as White")).toBeVisible();
    await expect(
      canvas.queryByText("This position cannot be saved because it is not in the corpus."),
    ).not.toBeInTheDocument();
    await expect(canvas.getByRole("button", { name: "Add" })).toBeDisabled();
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await expect(canvas.getByRole("button", { name: "Add" })).toBeEnabled();
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
    await expect(canvas.getByText("Seen in 5 games as White")).toBeVisible();
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("Saved move: e4 (e2e4)");
    await expect(canvas.getByRole("button", { name: "Edit" })).toBeEnabled();
    await expect(canvas.getByRole("button", { name: "Play saved move" })).toBeEnabled();
    await expect(canvas.queryByRole("button", { name: "Add" })).not.toBeInTheDocument();
    await userEvent.click(canvas.getByRole("button", { name: "Play saved move" }));
    await expect(canvas.getByTestId("current-fen")).toHaveTextContent("4P3");
    await expect(canvas.getByTestId("session-san-history")).toHaveTextContent("1. e4");
    await expect(canvas.getByTestId("session-status")).toHaveTextContent(
      "Saved move played locally: e4.",
    );
    await expect(canvas.queryByTestId("saved-move")).not.toBeInTheDocument();
  },
};

export const EditReplacement: Story = {
  name: "Preferred move - Edit and Save replacement",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["d2d4"]) },
      { initialState: "assigned" },
      { overall_exists: true, white_count: 5, black_count: 1 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("saved-move")).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Edit" }));
    await userEvent.click(await canvas.findByRole("button", { name: "1. d4" }));
    await expect(canvas.getByTestId("replacement-move")).toHaveTextContent("d4");
    await userEvent.click(canvas.getByRole("button", { name: "Save replacement" }));
    await expect(canvas.getByText("Preferred move replaced.")).toBeVisible();
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("Saved move: d4 (d2d4)");
    await expect(canvas.getByRole("button", { name: "Effective date: Choose date" })).toBeVisible();
  },
};

export const DatedAdd: Story = {
  name: "Preferred move - selected UTC date clears after Add",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { initialState: "unassigned" },
      { overall_exists: true, white_count: 3, black_count: 2 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const date = await selectCurrentUtcDate(canvasElement);
    await expect(canvas.getByRole("button", { name: `Effective date: ${date}` })).toBeVisible();
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await userEvent.click(canvas.getByRole("button", { name: "Add" }));
    await expect(canvas.getByText("Preferred move added.")).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Effective date: Choose date" })).toBeVisible();
  },
};

export const MutationFailure: Story = {
  name: "Preferred move - failed Add retains staged move and date",
  render: () =>
    workspace(
      { analysisClient: storyCandidateAnalysisClient(["e2e4"]) },
      { initialState: "unassigned", putFailure: "future_effective_time" },
      { overall_exists: true, white_count: 3, black_count: 2 },
    ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const date = await selectCurrentUtcDate(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "1. e4" }));
    await userEvent.click(canvas.getByRole("button", { name: "Add" }));
    await expect(canvas.getByRole("alert")).toHaveTextContent(
      "The selected date cannot be in the future.",
    );
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("e4");
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
    await expect(canvas.getByRole("button", { name: "Effective date: Choose date" })).toBeVisible();
  },
};
