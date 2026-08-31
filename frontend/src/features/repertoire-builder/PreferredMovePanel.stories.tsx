import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import { PreferredMovePanel, type PreferredMovePanelProps } from "./PreferredMovePanel";
import type { PositionPickerMoveRecord } from "./positionPickerSession";
import type { RepertoirePositionModel } from "./repertoireWorkflowModel";

const SOURCE_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const STAGED_MOVE: PositionPickerMoveRecord = {
  sourceSquare: "e2",
  targetSquare: "e4",
  color: "white",
  san: "e4",
  position: {
    ply: 1,
    fen: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    san: "e4",
  },
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
    savedMove: null,
    savedMoveVisible: false,
    stagedMove: null,
    effectiveAt: null,
    ...overrides,
  };
}

function panelArgs(overrides: Partial<PreferredMovePanelProps> = {}): PreferredMovePanelProps {
  return {
    model: model(),
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
  title: "Application/Repertoire Builder/Preferred Move Panel",
  component: PreferredMovePanel,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof PreferredMovePanel>;

export default meta;
type Story = StoryObj<typeof meta>;

export const UnassignedSavable: Story = {
  args: panelArgs({ model: model({ stagedMove: STAGED_MOVE, relationship: "first-choice" }) }),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("staged-move")).toHaveTextContent("Staged move: e4 (e2e4)");
    await userEvent.click(canvas.getByRole("button", { name: "Save" }));
    await expect(args.onSave).toHaveBeenCalledTimes(1);
  },
};

export const AssignedSaved: Story = {
  args: panelArgs({
    model: model({
      savedPresence: "present",
      saved: {
        move: { san: "e4", uci: "e2e4" },
        effectiveAt: "2025-01-15T00:00:00.000Z",
        sourceFen: SOURCE_FEN,
      },
      savedMove: { san: "e4", uci: "e2e4" },
      savedMoveVisible: true,
      relationship: "saved",
      effectiveAt: "2025-01-15T00:00:00.000Z",
    }),
    date: new Date("2025-01-15T00:00:00.000Z"),
  }),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("button", { name: /Current saved choice: e4/ }));
    await expect(args.onPlaySavedMove).toHaveBeenCalledTimes(1);
  },
};

export const Unsavable: Story = {
  args: panelArgs({ model: model({ saveability: "unsavable" }) }),
};

export const Loading: Story = {
  args: panelArgs({
    model: model({
      contextMessage: null,
      saveability: "unknown",
      savedPresence: "unknown",
      relationship: "unknown",
      comparison: "unknown",
    }),
    contextLoading: true,
    preferredLoading: true,
  }),
};

export const ErrorFeedback: Story = {
  args: panelArgs({
    model: model(),
    preferredError: "preferred_move_unavailable",
    contextError: "position_context_unavailable",
    workflowError: "unexpected_failure",
  }),
};
