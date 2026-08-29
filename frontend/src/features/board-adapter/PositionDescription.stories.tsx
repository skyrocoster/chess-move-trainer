import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { PositionDescription } from "./PositionDescription";
import { createPositionModel } from "./positionDescriptionModel";

const RICH_FEN = "rn1qk2r/1bp1bpp1/pp1ppn1p/8/4PB2/2NP1NP1/PPPQ1PBP/R3K2R b KQkq e3 0 8";

const meta = {
  title: "Application/Board/Position Description",
  component: PositionDescription,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof PositionDescription>;

export default meta;
type Story = StoryObj<typeof meta>;

export const RichBlackOrientation: Story = {
  name: "Rich position disclosure",
  args: {
    model: createPositionModel(RICH_FEN, "black"),
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole("button", { name: "Position description" });

    await expect(trigger).toHaveAttribute("aria-expanded", "false");
    await expect(canvasElement.querySelector("[data-position-summary]")).not.toBeInTheDocument();

    await userEvent.click(trigger);

    await expect(trigger).toHaveAttribute("aria-expanded", "true");
    const summary = canvasElement.querySelector("[data-position-summary]");
    if (!(summary instanceof HTMLElement)) {
      throw new Error("The expanded position summary is missing.");
    }
    await expect(summary).toBeVisible();
    await expect(summary).toHaveTextContent("OrientationBlack at the bottom");
    await expect(summary).toHaveTextContent("Side to moveBlack");
    await expect(summary.querySelectorAll('[data-position-side="w"]')).toHaveLength(1);
    await expect(summary.querySelectorAll('[data-position-side="b"]')).toHaveLength(1);
    await expect(
      summary.querySelectorAll('[data-position-side="b"][data-position-side-to-move="true"]'),
    ).toHaveLength(1);
    await expect(
      summary.querySelectorAll(
        '[data-position-side="w"] [data-position-piece="k"] [data-position-square="e1"]',
      ),
    ).toHaveLength(1);
    await expect(
      summary.querySelectorAll(
        '[data-position-side="b"] [data-position-piece="k"] [data-position-square="e8"]',
      ),
    ).toHaveLength(1);
    await expect(summary.querySelectorAll("[data-position-fact]")).toHaveLength(5);
    await expect(summary).toHaveTextContent("Castling · White K + Q");
    await expect(summary).toHaveTextContent("Castling · Black K + Q");
    await expect(summary).toHaveTextContent("En-passant target e3");
    await expect(summary).toHaveTextContent("Halfmove clock 0");
    await expect(summary).toHaveTextContent("Fullmove 8");
  },
};
