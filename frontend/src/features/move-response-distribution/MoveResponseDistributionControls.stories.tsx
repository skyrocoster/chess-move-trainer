import { fn } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { MoveResponseDistributionControls } from "./MoveResponseDistributionControls";

const replies = [
  {
    rank: 1,
    child_uci: "e2e4",
    san: "e4",
    occurrence_count: 4,
    percentage: 40,
    percentageLabel: "40%",
    accessibleLabel: "e4, 4 occurrences, 40% of outgoing move occurrences",
  },
];

const meta = {
  title: "Application/Move Response Distribution/Controls",
  component: MoveResponseDistributionControls,
  decorators: [
    (Story) => (
      <div className="dark" style={{ background: "var(--md-sys-color-surface-container)" }}>
        <Story />
      </div>
    ),
  ],
  args: {
    replies,
    tail: [],
    other: null,
    otherExpanded: false,
    tailId: "other-replies",
    selectedUci: null,
    onMoveSelect: fn(),
    onOtherToggle: fn(),
  },
} satisfies Meta<typeof MoveResponseDistributionControls>;

export default meta;
type Story = StoryObj<typeof meta>;

export const CommonReplies: Story = {};
