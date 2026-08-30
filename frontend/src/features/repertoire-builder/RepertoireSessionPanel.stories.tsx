import { expect, fn, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { ReactNode } from "react";
import { useState } from "react";

import type { CalendarDateValue } from "../design-system/CalendarDate";
import type { PositionContextResponse } from "../viewer/positionContextApi";
import type { PositionPickerMoveRecord } from "./positionPickerSession";
import { RepertoireSessionPanel, type RepertoireSessionPanelProps } from "./RepertoireSessionPanel";
import {
  expectActiveSessionHistoryEntry,
  expectPositionReachFrequency,
  expectPreferredMoveState,
  expectSessionHistory,
} from "./repertoireBuilderStoryAssertions";
import type { RepertoirePositionModel } from "./repertoireWorkflowModel";
import { constrainedViewport } from "./repertoireBuilderStoryRender";
import { expectNoHorizontalOverflow } from "./repertoireBuilderStoryHelpers";

const SAVABLE_MODEL: RepertoirePositionModel = {
  bottomColor: "white",
  personalCount: 3,
  contextMessage: "Seen in 3 games as White",
  saveability: "savable",
  state: "no-saved",
  savedMove: null,
  savedMoveVisible: false,
  effectiveAt: null,
  lastPlayedMove: null,
  lastPlayedPreferredMove: null,
};

const SAVED_MODEL: RepertoirePositionModel = {
  ...SAVABLE_MODEL,
  state: "saved",
  savedMove: { san: "e4", uci: "e2e4" },
  savedMoveVisible: true,
  effectiveAt: "2025-01-15T00:00:00.000Z",
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

const PLAYED_MOVE: PositionPickerMoveRecord = {
  ...STAGED_MOVE,
  position: { ...STAGED_MOVE.position, ply: 1 },
};

const MATCHING_PLAYED_MODEL: RepertoirePositionModel = {
  ...SAVABLE_MODEL,
  state: "matching-played",
  effectiveAt: "2025-01-15T00:00:00.000Z",
  lastPlayedMove: PLAYED_MOVE,
  lastPlayedPreferredMove: {
    fen: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    state: "assigned",
    move: { san: "e4", uci: "e2e4" },
    effective_at: "2025-01-15T00:00:00.000Z",
  },
};

const UNSAVED_PLAYED_MODEL: RepertoirePositionModel = {
  ...SAVABLE_MODEL,
  state: "unsaved-played",
  lastPlayedMove: PLAYED_MOVE,
  lastPlayedPreferredMove: {
    fen: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    state: "unassigned",
    move: null,
    effective_at: null,
  },
};

const POSITION_CONTEXT: PositionContextResponse = {
  fen: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  overall_exists: true,
  white_count: 3,
  black_count: 2,
  white_total: 10,
  black_total: 10,
};

function panelCallbacks(): Pick<
  RepertoireSessionPanelProps,
  | "onDateChange"
  | "onAdd"
  | "onEdit"
  | "onSave"
  | "onCancelEdit"
  | "onPlaySavedMove"
  | "onRemove"
  | "onActivePlyChange"
> {
  return {
    onDateChange: fn(),
    onAdd: fn(),
    onEdit: fn(),
    onSave: fn(),
    onCancelEdit: fn(),
    onPlaySavedMove: fn(),
    onRemove: fn(),
    onActivePlyChange: fn(),
  };
}

function panelArgs(
  overrides: Partial<RepertoireSessionPanelProps> = {},
): RepertoireSessionPanelProps {
  return {
    initialPosition: { ply: 0 },
    moves: [
      { ply: 1, san: "e4" },
      { ply: 2, san: "e5" },
      { ply: 3, san: "Nf3" },
    ],
    activePly: 3,
    sessionStatus: "My move staged: e4.",
    model: SAVABLE_MODEL,
    positionContext: POSITION_CONTEXT,
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

function SessionPanelFixture(args: RepertoireSessionPanelProps) {
  const [activePly, setActivePly] = useState(args.activePly ?? args.initialPosition?.ply ?? 0);
  return shell(
    <RepertoireSessionPanel
      {...args}
      activePly={activePly}
      onActivePlyChange={(ply) => {
        setActivePly(ply);
        args.onActivePlyChange?.(ply);
      }}
    />,
  );
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
  render: (args) => <SessionPanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("repertoire-session")).toBeVisible();
    await expectSessionHistory(canvasElement, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 2, Nf3");
    const status = canvas.getByTestId("session-status");
    await expect(status).toHaveAttribute("data-testid", "session-status");
    await expect(status).toHaveRole("status");
    await expect(status).toHaveAttribute("aria-live", "polite");
    await expect(status).toHaveTextContent("My move staged: e4.");
    await expect(canvas.getByRole("heading", { name: "Preferred move" })).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Add" })).toBeVisible();
    await expectPreferredMoveState(canvasElement, "no-saved");
    await expectPositionReachFrequency(canvasElement, "available", "White", "3 / 10 games", "30%");
    const entry = canvas.getByRole("button", { name: "Black, move 1, e5" });
    await userEvent.click(entry);
    await expectActiveSessionHistoryEntry(canvasElement, "Black, move 1, e5");
    await expect(entry).toHaveFocus();
  },
};

export const EmptyHistory: Story = {
  name: "Empty local history and status",
  args: panelArgs({
    moves: [],
    activePly: 0,
    sessionStatus: "No local moves yet.",
    stagedMove: null,
  }),
  render: (args) => <SessionPanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectSessionHistory(canvasElement, ["Initial position"]);
    await expectActiveSessionHistoryEntry(canvasElement, "Initial position");
    await expect(canvas.getByTestId("session-status")).toHaveTextContent("No local moves yet.");
    await expect(canvas.getByRole("heading", { name: "Preferred move" })).toBeVisible();
    await expectPreferredMoveState(canvasElement, "no-saved");
    await expectPositionReachFrequency(canvasElement, "available", "White", "3 / 10 games", "30%");
  },
};

export const ConstrainedLocalLineSession: Story = {
  name: "Constrained stored prefix and local line",
  parameters: constrainedViewport,
  args: panelArgs({ activePly: 2, sessionStatus: "Moved to the stored prefix." }),
  render: (args) => <SessionPanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    await expectSessionHistory(canvasElement, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(canvasElement, "Black, move 1, e5");
    await expectPositionReachFrequency(canvasElement, "available", "White", "3 / 10 games", "30%");
    await expectNoHorizontalOverflow(canvasElement);
  },
};

export const SavedMove: Story = {
  name: "Saved move - persisted date and explicit actions",
  args: panelArgs({
    model: SAVED_MODEL,
    activePly: 0,
    moves: [],
    sessionStatus: "Saved move is ready.",
    stagedMove: null,
    date: new Date("2025-01-15T00:00:00.000Z"),
    draftMode: "idle",
  }),
  render: (args) => <SessionPanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "saved");
    await expect(canvas.getByTestId("saved-move")).toHaveTextContent("Saved move: e4 (e2e4)");
    await expect(canvas.getByTestId("effective-date")).toHaveTextContent(
      "Effective from 2025-01-15",
    );
    await expect(canvas.getByRole("button", { name: "Edit" })).toBeEnabled();
    await expect(canvas.getByRole("button", { name: "Play saved move" })).toBeEnabled();
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeEnabled();
  },
};

export const MatchingPlayed: Story = {
  name: "Matching played - focused preferred move with Today",
  args: panelArgs({
    model: MATCHING_PLAYED_MODEL,
    activePly: 1,
    moves: [{ ply: 1, san: "e4" }],
    sessionStatus: "Saved move played locally: e4.",
    stagedMove: null,
    sideToMove: "black",
    date: new Date(),
    draftMode: "idle",
  }),
  render: (args) => <SessionPanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "matching-played");
    await expect(canvas.getByTestId("played-move")).toHaveTextContent("Played move: e4 (e2e4)");
    await expect(canvas.getByText("This move matches your preferred move.")).toBeVisible();
    await expect(canvas.getByTestId("effective-date")).toHaveTextContent("Effective from Today");
    await expectActiveSessionHistoryEntry(canvasElement, "White, move 1, e4");
    await expect(canvas.getByRole("button", { name: "Edit" })).toBeEnabled();
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeEnabled();
  },
};

export const UnsavedPlayed: Story = {
  name: "Unsaved played - focused local move and Add action",
  args: panelArgs({
    model: UNSAVED_PLAYED_MODEL,
    activePly: 0,
    moves: [],
    sessionStatus: "My move staged: e4.",
    stagedMove: PLAYED_MOVE,
    date: null,
    draftMode: "idle",
  }),
  render: (args) => <SessionPanelFixture {...args} />,
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await expectPreferredMoveState(canvasElement, "unsaved-played");
    await expect(canvas.getByTestId("played-move")).toHaveTextContent("Played move: e4 (e2e4)");
    await expect(canvas.getByText("This move is not saved as your preferred move.")).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Add" })).toBeEnabled();
    await userEvent.click(canvas.getByRole("button", { name: "Add" }));
    await expect(args.onAdd).toHaveBeenCalledTimes(1);
  },
};

export const FrequencyZero: Story = {
  name: "Position reach frequency - available zero",
  args: panelArgs({
    positionContext: { ...POSITION_CONTEXT, white_count: 0 },
  }),
  render: (args) => <SessionPanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    await expectPositionReachFrequency(canvasElement, "available", "White", "0 / 10 games", "0%");
  },
};

export const FrequencyAbsent: Story = {
  name: "Position reach frequency - absent position",
  args: panelArgs({
    positionContext: { ...POSITION_CONTEXT, overall_exists: false },
  }),
  render: (args) => <SessionPanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    await expectPositionReachFrequency(canvasElement, "absent", "White");
    await expect(
      within(canvasElement).getByText(/not present in the accepted game data/),
    ).toBeVisible();
  },
};

export const FrequencyUnavailable: Story = {
  name: "Position reach frequency - unavailable position",
  args: panelArgs({ positionContext: null }),
  render: (args) => <SessionPanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    await expectPositionReachFrequency(canvasElement, "unavailable", "White");
    await expect(
      within(canvasElement).getByText("Position reach data is unavailable."),
    ).toBeVisible();
  },
};
