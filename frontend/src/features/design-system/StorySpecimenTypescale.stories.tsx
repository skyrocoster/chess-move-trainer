import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../styles/cmt-typescale.css";
import { StorySpecimenTypescale } from "./StorySpecimenTypescale";

const meta = {
  title: "Design System/Documentation/Typography",
  component: StorySpecimenTypescale,
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component: "Storybook-only documentation specimen for the production typography scale.",
      },
    },
  },
} satisfies Meta<typeof StorySpecimenTypescale>;

export default meta;

type Story = StoryObj<typeof meta>;

export const CompleteTypescale: Story = {};
