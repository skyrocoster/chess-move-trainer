import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import {
  PreferredMoveChoiceBox,
  PreferredMoveConsequence,
  PreferredMoveConnector,
  PreferredMoveDate,
  PreferredMoveValue,
} from "./PreferredMovePrimitives";

const meta = {
  title: "Application/Repertoire Builder/Preferred Move Primitives",
  parameters: { layout: "fullscreen" },
  render: () => (
    <main
      style={{
        minHeight: "100vh",
        padding: "var(--cmt-spacing-24)",
        display: "grid",
        gap: "var(--cmt-spacing-24)",
        justifyContent: "start",
        alignContent: "start",
        backgroundColor: "var(--md-sys-color-surface)",
        color: "var(--md-sys-color-on-surface)",
      }}
    >
      <div style={{ display: "grid", gap: "var(--cmt-spacing-8)", justifyItems: "start" }}>
        <PreferredMoveChoiceBox
          label="Current saved choice"
          tone="saved"
          move={{ san: "e4", uci: "e2e4" }}
          effectiveDate={new Date("2026-08-29T00:00:00Z")}
        />
        <PreferredMoveConnector label="replace" />
        <PreferredMoveChoiceBox
          label="Staged move"
          tone="proposal"
          move={{ san: "d4", uci: "d2d4" }}
        />
        <PreferredMoveConsequence kind="replacement" stagedSan="d4" savedSan="e4" />
        <PreferredMoveConsequence kind="first-choice" stagedSan="d4" />
        <PreferredMoveConsequence kind="matching" savedSan="e4" />
      </div>
      <div style={{ display: "grid", gap: "var(--cmt-spacing-8)", justifyItems: "start" }}>
        <PreferredMoveValue san="Nf3" uci="g1f3" />
        <PreferredMoveDate value={null} onChange={fn()} />
      </div>
    </main>
  ),
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primitives: Story = {
  name: "Choice boxes, connector, consequences, and date primitive",
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("region", { name: "Current saved choice" })).toBeVisible();
    await expect(canvas.getByRole("region", { name: "Staged move" })).toBeVisible();
    await expect(canvas.getByText("Save d4 to replace e4.")).toBeVisible();
    await expect(canvas.getByText("Save d4 as the current saved choice.")).toBeVisible();
    await expect(canvas.getByText("e4 is already the current saved choice.")).toBeVisible();
    await expect(canvas.getByText("Nf3")).toBeVisible();
    await expect(
      canvas.getByRole("button", { name: "Change effective date: Choose date" }),
    ).toBeVisible();
  },
};

export const AlternateTones: Story = {
  name: "Empty and matching tones",
  render: () => (
    <main
      style={{
        minHeight: "100vh",
        padding: "var(--cmt-spacing-24)",
        display: "grid",
        gap: "var(--cmt-spacing-24)",
        justifyContent: "start",
        alignContent: "start",
        backgroundColor: "var(--md-sys-color-surface)",
        color: "var(--md-sys-color-on-surface)",
      }}
    >
      <PreferredMoveChoiceBox label="Current saved choice" tone="empty" />
      <PreferredMoveChoiceBox
        label="Staged move"
        tone="matching"
        move={{ san: "e4", uci: "e2e4" }}
      />
    </main>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("No saved choice yet.")).toBeVisible();
    await expect(canvas.getByText("e4")).toBeVisible();
  },
};

export const InteractiveSavedChoice: Story = {
  name: "Saved choice activates as a button",
  render: () => (
    <main
      style={{
        minHeight: "100vh",
        padding: "var(--cmt-spacing-24)",
        backgroundColor: "var(--md-sys-color-surface)",
        color: "var(--md-sys-color-on-surface)",
      }}
    >
      <PreferredMoveChoiceBox
        label="Current saved choice"
        tone="saved"
        move={{ san: "e4", uci: "e2e4" }}
        onActivate={fn()}
        activationLabel="Current saved choice: e4; play and stage this move."
      />
    </main>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const savedChoice = canvas.getByRole("button", {
      name: "Current saved choice: e4; play and stage this move.",
    });
    await userEvent.click(savedChoice);
    await expect(savedChoice).toBeEnabled();
  },
};
