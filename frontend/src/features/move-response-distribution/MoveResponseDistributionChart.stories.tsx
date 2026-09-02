import { fn } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { MoveResponseDistributionChart } from "./MoveResponseDistributionChart";

const meta = {
  title: "Application/Move Response Distribution/Chart",
  component: MoveResponseDistributionChart,
  decorators: [
    (Story) => (
      <div className="dark">
        <Story />
      </div>
    ),
  ],
  args: {
    replies: [
      {
        rank: 1,
        child_uci: "e2e4",
        san: "e4",
        distinct_game_count: 4,
        opening_name: null,
        percentage: 40,
        percentageLabel: "40%",
        accessibleLabel: "e4, 4 distinct games, 40% of matching games",
      },
    ],
    other: null,
    otherExpanded: false,
    onMoveSelect: fn(),
    onOtherToggle: fn(),
  },
} satisfies Meta<typeof MoveResponseDistributionChart>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Available: Story = {};
