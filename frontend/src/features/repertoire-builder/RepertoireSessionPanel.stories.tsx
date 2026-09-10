import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, within } from "storybook/test";

import type { PositionContextResponse } from "../position-context/positionContextApi";
import { RepertoireSessionPanel, type RepertoireSessionPanelProps } from "./RepertoireSessionPanel";
import type { RepertoirePositionModel } from "./repertoireWorkflowModel";

const SOURCE_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const POSITION_CONTEXT: PositionContextResponse = {
  fen: SOURCE_FEN,
  trainerColor: "white",
  observedInGames: true,
  distinctGameCount: 3,
  totalGameCount: 10,
};

function model(overrides: Partial<RepertoirePositionModel> = {}): RepertoirePositionModel {
  return {
    sourceFen: SOURCE_FEN,
    bottomColor: "white",
    ownTurn: true,
    personalCount: 3,
    contextMessage: "Seen in 3 games as White",
    saveability: "savable",
    savedPresence: "absent",
    saved: null,
    selected: null,
    comparison: "not-applicable",
    relationship: "empty",
    ...overrides,
  };
}

function panelArgs(
  overrides: Partial<RepertoireSessionPanelProps> = {},
): RepertoireSessionPanelProps {
  return {
    sessionStatus: "Move played locally: e4.",
    model: model(),
    positionContext: POSITION_CONTEXT,
    date: null,
    mutation: null,
    preferredLoading: false,
    preferredError: null,
    contextLoading: false,
    contextError: null,
    workflowError: null,
    onDateChange: fn(),
    onSave: fn(),
    onPlaySavedMove: fn(),
    onRemove: fn(),
    ...overrides,
  };
}

const meta = {
  title: "Application/Repertoire Builder/Session Panel",
  component: RepertoireSessionPanel,
  parameters: { layout: "fullscreen" },
  render: (args) => (
    <main
      style={{
        minHeight: "100vh",
        padding: "var(--cmt-spacing-24)",
        backgroundColor: "var(--md-sys-color-surface)",
        color: "var(--md-sys-color-on-surface)",
      }}
    >
      <RepertoireSessionPanel {...args} />
    </main>
  ),
} satisfies Meta<typeof RepertoireSessionPanel>;

export default meta;
type Story = StoryObj<typeof meta>;

export const LocalLineSession: Story = {
  args: panelArgs(),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("repertoire-session")).toBeVisible();
    await expect(canvas.getByTestId("session-status")).toHaveTextContent("Move played locally: e4.");
  },
};

export const SessionFactsOnly: Story = {
  name: "Session facts without move history",
  args: panelArgs({ sessionStatus: "No local moves yet." }),
};

export const FrequencyZero: Story = {
  name: "Frequency - observed position with zero selected-color experience",
  args: panelArgs({
    positionContext: { ...POSITION_CONTEXT, distinctGameCount: 0 },
    model: model({ personalCount: 0, contextMessage: "Never seen as White" }),
  }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("0 / 10 games", { exact: true })).toBeVisible();
    await expect(canvas.getByText("0%", { exact: true })).toBeVisible();
    await expect(canvas.getByText("Never seen as White")).toBeVisible();
  },
};

export const FrequencyAbsent: Story = {
  name: "Frequency - globally unseen position",
  args: panelArgs({
    positionContext: { ...POSITION_CONTEXT, observedInGames: false, distinctGameCount: 0, totalGameCount: 0 },
    model: model({ personalCount: 0, contextMessage: "Never seen as White", saveability: "unsavable" }),
  }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getByText("This position is not present in the accepted game data for White."),
    ).toBeVisible();
    await expect(canvas.queryByRole("meter", { name: /Position reach frequency/ })).not.toBeInTheDocument();
    await expect(canvas.queryByText(/0 \/ 10 games|0%/)).not.toBeInTheDocument();
  },
};

export const FrequencyUnavailable: Story = {
  name: "Frequency - no position reach data",
  args: panelArgs({ positionContext: null }),
  play: async ({ canvasElement }) => {
    await expect(
      within(canvasElement).getByText("Position reach data is unavailable."),
    ).toBeVisible();
  },
};
