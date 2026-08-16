import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../styles/cmt-typescale.css";
import { TypescaleSpecimen } from "./TypescaleSpecimen";

const meta = {
  title: "DesignSystem/CompleteTypescale",
  component: TypescaleSpecimen,
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta<typeof TypescaleSpecimen>;

export default meta;

type Story = StoryObj<typeof meta>;

export const CompleteTypescale: Story = {};
