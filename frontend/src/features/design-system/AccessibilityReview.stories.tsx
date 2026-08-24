import "../../styles/cmt-tokens.css";

import type { Meta, StoryObj } from "@storybook/react-vite";

import { AccessibilityReview } from "./AccessibilityReview";

const meta = {
  title: "Documentation/Reviews/Responsive Accessibility",
  component: AccessibilityReview,
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component:
          "Storybook-only review fixture for responsive layout, feedback states, focus treatment, and accessibility checks.",
      },
    },
  },
} satisfies Meta<typeof AccessibilityReview>;

export default meta;

type Story = StoryObj<typeof meta>;

export const ResponsiveAccessibilityReview: Story = {};
