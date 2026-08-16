import "../../styles/cmt-tokens.css";

import type { Meta, StoryObj } from "@storybook/react-vite";

import { AccessibilityReview } from "./AccessibilityReview";

const meta = {
  title: "Acceptance/ResponsiveAccessibilityReview",
  component: AccessibilityReview,
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta<typeof AccessibilityReview>;

export default meta;

type Story = StoryObj<typeof meta>;

export const ResponsiveAccessibilityReview: Story = {};
