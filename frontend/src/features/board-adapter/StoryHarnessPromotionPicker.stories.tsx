import type { Meta, StoryObj } from "@storybook/react-vite";

import { StoryHarnessPromotionPicker } from "./StoryHarnessPromotionPicker";

const meta = {
  title: "Documentation/Demos/Promotion Picker Harness",
  component: StoryHarnessPromotionPicker,
  decorators: [
    (Story) => (
      <div style={{ background: "var(--md-sys-color-background)" }}>
        <Story />
      </div>
    ),
  ],
  parameters: { layout: "centered" },
} satisfies Meta<typeof StoryHarnessPromotionPicker>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    color: "w",
    presentation: "popover",
    initiallyPending: false,
  },
};
