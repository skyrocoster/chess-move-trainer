import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, within } from "storybook/test";

import type { PositionContextResponse } from "../viewer/positionContextApi";
import { RepertoireSessionPanel, type RepertoireSessionPanelProps } from "./RepertoireSessionPanel";
import type { RepertoirePositionModel } from "./repertoireWorkflowModel";

const SOURCE_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const POSITION_CONTEXT: PositionContextResponse = {
  fen: SOURCE_FEN,
  overall_exists: true,
  white_count: 3,
  black_count: 2,
  white_total: 10,
  black_total: 10,
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
    staged: null,
    comparison: "not-applicable",
    relationship: "empty",
    ...overrides,
  };
}

function panelArgs(
  overrides: Partial<RepertoireSessionPanelProps> = {},
): RepertoireSessionPanelProps {
  return {
    sessionStatus: "My move staged: e4.",
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
    await expect(canvas.getByTestId("session-status")).toHaveTextContent("My move staged: e4.");
  },
};

export const SessionFactsOnly: Story = {
  name: "Session facts without move history",
  args: panelArgs({ sessionStatus: "No local moves yet." }),
};

export const FrequencyZero: Story = {
  args: panelArgs({ positionContext: { ...POSITION_CONTEXT, white_count: 0 } }),
};

export const FrequencyAbsent: Story = {
  args: panelArgs({ positionContext: { ...POSITION_CONTEXT, overall_exists: false } }),
};

export const FrequencyUnavailable: Story = {
  args: panelArgs({ positionContext: null }),
};
