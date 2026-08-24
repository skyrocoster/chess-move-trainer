import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../styles/cmt-typescale.css";
import { TypescaleSpecimen } from "./TypescaleSpecimen";

const meta = {
  title: "Design System/Documentation/Typography",
  component: TypescaleSpecimen,
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component: "Storybook-only documentation specimen for the production typography scale.",
      },
    },
  },
} satisfies Meta<typeof TypescaleSpecimen>;

export default meta;

type Story = StoryObj<typeof meta>;

export const CompleteTypescale: Story = {};
