import { expect, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { ReactNode } from "react";

import type { CalendarDateValue } from "../design-system/CalendarDate";
import type { PositionPickerMoveRecord } from "./positionPickerSession";
import { RepertoireSessionPanel, type RepertoireSessionPanelProps } from "./RepertoireSessionPanel";
import type { RepertoirePositionModel } from "./repertoireWorkflowModel";

const SAVABLE_MODEL: RepertoirePositionModel = {
  bottomColor: "white",
  personalCount: 3,
  contextMessage: "Seen in 3 games as White",
  saveability: "savable",
  savedMove: null,
  savedMoveVisible: false,
};

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

function panelCallbacks(): Pick<
  RepertoireSessionPanelProps,
  "onDateChange" | "onAdd" | "onEdit" | "onSave" | "onCancelEdit" | "onPlaySavedMove" | "onRemove"
> {
  return {
    onDateChange: () => {},
    onAdd: () => {},
    onEdit: () => {},
    onSave: () => {},
    onCancelEdit: () => {},
    onPlaySavedMove: () => {},
    onRemove: () => {},
  };
}

function panelArgs(
  overrides: Partial<RepertoireSessionPanelProps> = {},
): RepertoireSessionPanelProps {
  return {
    sanHistory: "1. e4 1... e5",
    sessionStatus: "My move staged: e4.",
    model: SAVABLE_MODEL,
    sideToMove: "white",
    stagedMove: STAGED_MOVE,
    draftMode: "idle",
    date: null as CalendarDateValue,
    mutation: null,
    preferredLoading: false,
    preferredError: null,
    contextLoading: false,
    contextError: null,
    workflowError: null,
    ...panelCallbacks(),
    ...overrides,
  };
}

function shell(children: ReactNode) {
  return (
    <main
      style={{
        minBlockSize: "100vh",
        padding: "var(--cmt-spacing-32)",
        background: "var(--md-sys-color-background)",
        color: "var(--md-sys-color-on-background)",
      }}
    >
      <div style={{ maxInlineSize: "42rem" }}>{children}</div>
    </main>
  );
}

const meta = {
  title: "Application/Repertoire Builder/Session Panel",
  component: RepertoireSessionPanel,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof RepertoireSessionPanel>;

export default meta;
type Story = StoryObj<typeof meta>;

export const LocalLineSession: Story = {
  name: "Local history, status, and preferred panel",
  args: panelArgs(),
  render: (args) => shell(<RepertoireSessionPanel {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("repertoire-session")).toBeVisible();
    await expect(canvas.getByTestId("session-san-history")).toHaveTextContent("1. e4 1... e5");
    await expect(canvas.getByTestId("session-status")).toHaveRole("status");
    await expect(canvas.getByTestId("session-status")).toHaveTextContent("My move staged: e4.");
    await expect(canvas.getByRole("heading", { name: "Preferred move" })).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Add" })).toBeVisible();
  },
};

export const EmptyHistory: Story = {
  name: "Empty local history and status",
  args: panelArgs({
    sanHistory: "",
    sessionStatus: "No local moves yet.",
    stagedMove: null,
  }),
  render: (args) => shell(<RepertoireSessionPanel {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("session-san-history")).toHaveTextContent("No local moves yet");
    await expect(canvas.getByTestId("session-status")).toHaveTextContent("No local moves yet.");
    await expect(canvas.getByRole("heading", { name: "Preferred move" })).toBeVisible();
  },
};
