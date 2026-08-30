import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { MoveHistory } from "./MoveHistory";
import type { MoveHistoryInput, Ply } from "./moveHistoryTypes";

const HISTORY: MoveHistoryInput = {
  initialPosition: { ply: 0 },
  moves: [
    { ply: 1, san: "e4" },
    { ply: 2, san: "e5" },
    { ply: 3, san: "Nf3" },
    { ply: 4, san: "Nc6" },
    { ply: 5, san: "Bb5" },
    { ply: 6, san: "a6" },
    { ply: 7, san: "Ba4" },
    { ply: 8, san: "Nf6" },
  ],
};

const meta = {
  title: "Shared/Move History",
  component: MoveHistory,
  parameters: { layout: "fullscreen" },
  args: { ...HISTORY, activePly: 0, onActivePlyChange: () => {} },
} satisfies Meta<typeof MoveHistory>;

export default meta;
type Story = StoryObj<typeof meta>;

function frame(children: React.ReactNode, constrained = false) {
  return (
    <main
      style={{
        boxSizing: "border-box",
        minHeight: "100vh",
        padding: "var(--cmt-spacing-24)",
        background: "var(--md-sys-color-background)",
        color: "var(--md-sys-color-on-background)",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: constrained ? "20rem" : "36rem",
          margin: "0 auto",
        }}
      >
        {children}
      </div>
    </main>
  );
}

function ControlledMoveHistory() {
  const [activePly, setActivePly] = useState<Ply>(0);

  return (
    <div>
      <MoveHistory
        {...HISTORY}
        activePly={activePly}
        ariaLabel="Interactive move history"
        onActivePlyChange={setActivePly}
      />
      <p aria-label="Active Ply" role="status">
        Active Ply: {activePly}
      </p>
    </div>
  );
}

export const Interactive: Story = {
  render: () => frame(<ControlledMoveHistory />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const initial = canvas.getByRole("button", { name: "Initial position" });
    const e4 = canvas.getByRole("button", { name: "White, move 1, e4" });
    const e5 = canvas.getByRole("button", { name: "Black, move 1, e5" });
    const finalMove = canvas.getByRole("button", { name: "Black, move 4, Nf6" });
    const activePly = canvas.getByRole("status", { name: "Active Ply" });

    await expect(initial).toHaveAttribute("aria-current", "step");
    await expect(activePly).toHaveTextContent("Active Ply: 0");

    await userEvent.click(e5);
    await expect(activePly).toHaveTextContent("Active Ply: 2");
    await expect(e5).toHaveAttribute("aria-current", "step");
    await expect(e5).toHaveFocus();

    await userEvent.keyboard("{ArrowLeft}");
    await expect(activePly).toHaveTextContent("Active Ply: 1");
    await expect(e4).toHaveAttribute("aria-current", "step");
    await expect(e4).toHaveFocus();

    await userEvent.keyboard("{ArrowRight}");
    await expect(activePly).toHaveTextContent("Active Ply: 2");
    await expect(e5).toHaveFocus();

    await userEvent.keyboard("{Home}");
    await expect(activePly).toHaveTextContent("Active Ply: 0");
    await expect(initial).toHaveAttribute("aria-current", "step");
    await expect(initial).toHaveFocus();

    await userEvent.keyboard("{End}");
    await expect(activePly).toHaveTextContent("Active Ply: 8");
    await expect(finalMove).toHaveAttribute("aria-current", "step");
    await expect(finalMove).toHaveFocus();
  },
};

export const Constrained: Story = {
  name: "Constrained width",
  render: () => frame(<ControlledMoveHistory />, true),
};
