import type { Meta, StoryObj } from "@storybook/react-vite";
import { TokenOverview } from "./TokenOverview";

const meta = {
  title: "DesignSystem/TokenOverview",
  component: TokenOverview,
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta<typeof TokenOverview>;

export default meta;

type Story = StoryObj<typeof meta>;

export const FixedDarkTokenSource: Story = {};
