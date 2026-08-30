import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { ReactNode } from "react";
import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import type { CalendarDateValue } from "../design-system/CalendarDate";
import { PreferredMovePanel, type PreferredMovePanelProps } from "./PreferredMovePanel";
import type { PositionPickerMoveRecord } from "./positionPickerSession";
import type { RepertoirePositionModel } from "./repertoireWorkflowModel";

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

const ASSIGNED_MODEL: RepertoirePositionModel = {
  ...SAVABLE_MODEL,
  state: "saved",
  savedMove: { san: "e4", uci: "e2e4" },
  savedMoveVisible: true,
  effectiveAt: "2025-01-15T00:00:00.000Z",
};

const UNSAVABLE_MODEL: RepertoirePositionModel = {
  ...SAVABLE_MODEL,
  personalCount: 0,
  contextMessage: "Never seen as White",
  saveability: "unsavable",
};

const LOADING_MODEL: RepertoirePositionModel = {
  ...SAVABLE_MODEL,
  contextMessage: null,
  saveability: "unknown",
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

const MATCHING_PLAYED_MODEL: RepertoirePositionModel = {
  ...SAVABLE_MODEL,
  state: "matching-played",
  effectiveAt: "2025-01-15T00:00:00.000Z",
  lastPlayedMove: STAGED_MOVE,
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
  lastPlayedMove: STAGED_MOVE,
  lastPlayedPreferredMove: {
    fen: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    state: "unassigned",
    move: null,
    effective_at: null,
  },
};

const REPLACEMENT_MOVE: PositionPickerMoveRecord = {
  sourceSquare: "d2",
  targetSquare: "d4",
  color: "white",
  san: "d4",
  position: {
    ply: 1,
    fen: "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1",
    san: "d4",
  },
};

const FIXED_DATE = new Date("2025-01-15T00:00:00.000Z");

type PanelCallbacks = Pick<
  PreferredMovePanelProps,
  "onDateChange" | "onAdd" | "onEdit" | "onSave" | "onCancelEdit" | "onPlaySavedMove" | "onRemove"
>;

function panelCallbacks(): PanelCallbacks {
  return {
    onDateChange: fn(),
    onAdd: fn(),
    onEdit: fn(),
    onSave: fn(),
    onCancelEdit: fn(),
    onPlaySavedMove: fn(),
    onRemove: fn(),
  };
}

function panelArgs(overrides: Partial<PreferredMovePanelProps> = {}): PreferredMovePanelProps {
  return {
    model: SAVABLE_MODEL,
    sideToMove: "white",
    stagedMove: null,
    draftMode: "add",
    date: null,
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

function PanelFixture(args: PreferredMovePanelProps) {
  const [date, setDate] = useState<CalendarDateValue>(args.date);
  const handleDateChange = (value: CalendarDateValue) => {
    setDate(value);
    args.onDateChange(value);
  };

  return shell(<PreferredMovePanel {...args} date={date} onDateChange={handleDateChange} />);
}

const meta = {
  title: "Application/Repertoire Builder/Preferred Move Panel",
  component: PreferredMovePanel,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof PreferredMovePanel>;

export default meta;
type Story = StoryObj<typeof meta>;

export const UnassignedSavable: Story = {
  name: "Unassigned savable - staged move and effective date",
  args: panelArgs({ model: SAVABLE_MODEL, stagedMove: STAGED_MOVE, date: FIXED_DATE }),
  render: (args) => <PanelFixture {...args} />,
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await expect(canvas.getByRole("button", { name: "Effective date: 2025-01-15" })).toBeVisible();
    await expect(canvas.getByText("Staged move: e4 (e2e4)")).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Effective date: 2025-01-15" }));
    const calendar = await body.findByRole("dialog", { name: "Effective date" });
    await userEvent.click(within(calendar).getByRole("button", { name: "Clear date" }));
    await expect(args.onDateChange).toHaveBeenCalledWith(null);
    await expect(canvas.getByRole("button", { name: "Effective date: Choose date" })).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Add" }));
    await expect(args.onAdd).toHaveBeenCalledTimes(1);
  },
};

export const AssignedSaved: Story = {
  name: "Assigned saved move - edit, play, and confirm removal",
  args: panelArgs({ model: ASSIGNED_MODEL, draftMode: "idle", date: FIXED_DATE }),
  render: (args) => <PanelFixture {...args} />,
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("region", { name: "Preferred move" })).toHaveAttribute(
      "data-state",
      "saved",
    );
    await expect(canvas.getByTestId("effective-date")).toHaveTextContent(
      "Effective from 2025-01-15",
    );
    const body = within(canvasElement.ownerDocument.body);
    await userEvent.click(canvas.getByRole("button", { name: "Edit" }));
    await expect(args.onEdit).toHaveBeenCalledTimes(1);
    await userEvent.click(canvas.getByRole("button", { name: "Play saved move" }));
    await expect(args.onPlaySavedMove).toHaveBeenCalledTimes(1);
    await userEvent.click(canvas.getByRole("button", { name: "Remove" }));
    const firstDialog = await body.findByRole("alertdialog", { name: "Remove preferred move?" });
    await userEvent.click(within(firstDialog).getByRole("button", { name: "Cancel" }));
    await expect(args.onRemove).not.toHaveBeenCalled();
    await userEvent.click(canvas.getByRole("button", { name: "Remove" }));
    const secondDialog = await body.findByRole("alertdialog", { name: "Remove preferred move?" });
    await userEvent.click(within(secondDialog).getByRole("button", { name: "Remove" }));
    await expect(args.onRemove).toHaveBeenCalledTimes(1);
  },
};

export const EditReplacement: Story = {
  name: "Edit replacement - staged marker and explicit actions",
  args: panelArgs({ model: ASSIGNED_MODEL, draftMode: "edit", stagedMove: REPLACEMENT_MOVE }),
  render: (args) => <PanelFixture {...args} />,
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("replacement-move")).toHaveTextContent("Staged move: d4");
    await userEvent.click(canvas.getByRole("button", { name: "Save replacement" }));
    await expect(args.onSave).toHaveBeenCalledTimes(1);
    await userEvent.click(canvas.getByRole("button", { name: "Cancel edit" }));
    await expect(args.onCancelEdit).toHaveBeenCalledTimes(1);
  },
};

export const Unsavable: Story = {
  name: "Unsavable - corpus warning without save controls",
  args: panelArgs({ model: UNSAVABLE_MODEL, stagedMove: STAGED_MOVE }),
  render: (args) => <PanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getByText("This position cannot be saved because it is not in the corpus."),
    ).toBeVisible();
    await expect(canvas.queryByRole("button", { name: "Add" })).not.toBeInTheDocument();
    await expect(
      canvas.queryByRole("button", { name: "Effective date: Choose date" }),
    ).not.toBeInTheDocument();
  },
};

export const MatchingPlayed: Story = {
  name: "Matching played - last-played focus and persisted date",
  args: panelArgs({
    model: MATCHING_PLAYED_MODEL,
    sideToMove: "black",
    stagedMove: null,
    draftMode: "idle",
    date: new Date("2025-01-15T00:00:00.000Z"),
  }),
  render: (args) => <PanelFixture {...args} />,
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("region", { name: "Preferred move" })).toHaveAttribute(
      "data-state",
      "matching-played",
    );
    await expect(canvas.getByTestId("played-move")).toHaveTextContent("Played move: e4 (e2e4)");
    await expect(canvas.getByText("This move matches your preferred move.")).toBeVisible();
    await expect(canvas.getByTestId("effective-date")).toHaveTextContent(
      "Effective from 2025-01-15",
    );
    await userEvent.click(canvas.getByRole("button", { name: "Edit" }));
    await expect(args.onEdit).toHaveBeenCalledTimes(1);
  },
};

export const UnsavedPlayed: Story = {
  name: "Unsaved played - last-played focus and explicit Add",
  args: panelArgs({
    model: UNSAVED_PLAYED_MODEL,
    stagedMove: STAGED_MOVE,
    draftMode: "idle",
    date: null,
  }),
  render: (args) => <PanelFixture {...args} />,
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("region", { name: "Preferred move" })).toHaveAttribute(
      "data-state",
      "unsaved-played",
    );
    await expect(canvas.getByTestId("played-move")).toHaveTextContent("Played move: e4 (e2e4)");
    await expect(canvas.getByText("This move is not saved as your preferred move.")).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Add" })).toBeEnabled();
    await userEvent.click(canvas.getByRole("button", { name: "Add" }));
    await expect(args.onAdd).toHaveBeenCalledTimes(1);
  },
};

export const AssignedToday: Story = {
  name: "Assigned saved move - current UTC date shows Today",
  args: panelArgs({ model: ASSIGNED_MODEL, draftMode: "idle", date: new Date() }),
  render: (args) => <PanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("effective-date")).toHaveTextContent("Effective from Today");
    await expect(
      canvas.getByRole("button", { name: /Effective date: \d{4}-\d{2}-\d{2}/ }),
    ).toBeVisible();
  },
};

export const Loading: Story = {
  name: "Loading - context pending and controls hidden",
  args: panelArgs({ model: LOADING_MODEL, preferredLoading: true, contextLoading: true }),
  render: (args) => <PanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("Loading position context...")).toBeVisible();
    await expect(canvas.queryByRole("button", { name: "Add" })).not.toBeInTheDocument();
    await expect(canvas.queryByRole("button", { name: "Edit" })).not.toBeInTheDocument();
    await expect(canvas.queryByRole("button", { name: /Effective date:/ })).not.toBeInTheDocument();
  },
};

export const ErrorFeedback: Story = {
  name: "Error feedback - preferred, context, and workflow alerts",
  args: panelArgs({
    model: LOADING_MODEL,
    preferredError: "preferred_move_unavailable",
    contextError: "position_context_unavailable",
    workflowError: "unexpected_failure",
  }),
  render: (args) => <PanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    const alerts = within(canvasElement).getAllByRole("alert");
    await expect(alerts).toHaveLength(3);
    for (const alert of alerts) {
      await expect(alert).toHaveRole("alert");
    }
    await expect(alerts[0]).toHaveTextContent("Preferred move data is unavailable. Try again.");
    await expect(alerts[1]).toHaveTextContent("Position context is temporarily unavailable.");
    await expect(alerts[2]).toHaveTextContent(
      "The preferred move could not be updated. Try again.",
    );
  },
};

export const SavingMutation: Story = {
  name: "Saving mutation - status and disabled mutation actions",
  args: panelArgs({
    model: ASSIGNED_MODEL,
    draftMode: "edit",
    stagedMove: REPLACEMENT_MOVE,
    mutation: "save",
  }),
  render: (args) => <PanelFixture {...args} />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const status = canvas.getByRole("status");
    await expect(status).toHaveRole("status");
    await expect(status).toHaveAttribute("aria-live", "polite");
    await expect(status).toHaveTextContent("Saving preferred move...");
    await expect(canvas.getByRole("button", { name: "Save replacement" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Cancel edit" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeDisabled();
  },
};
