import type { Meta, StoryObj } from "@storybook/react-vite";
import { TokenOverview } from "./TokenOverview";

const meta = {
  title: "Design System/Documentation/Tokens",
  component: TokenOverview,
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component: "Storybook-only documentation fixture for the fixed production token source.",
      },
    },
  },
} satisfies Meta<typeof TokenOverview>;

export default meta;

type Story = StoryObj<typeof meta>;

export const FixedDarkTokenSource: Story = {};
