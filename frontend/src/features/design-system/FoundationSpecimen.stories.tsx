import { fireEvent, within } from "@testing-library/react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../styles/cmt-tokens.css";
import { FoundationSpecimen } from "./FoundationSpecimen";

const meta = {
  title: "DesignSystem/Foundations",
  component: FoundationSpecimen,
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta<typeof FoundationSpecimen>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Foundations: Story = {
  play: async ({ canvasElement }) => {
    const focusSpecimen = within(canvasElement).getByRole("button", {
      name: "Focus specimen",
    });
    fireEvent.focus(focusSpecimen);
  },
};
