import type { Meta, StoryObj } from "@storybook/react-vite";

import { PromotionPickerDemo, type PromotionPickerDemoProps } from "./PromotionPickerDemo";

const meta = {
  title: "Board Adapter/Promotion Picker",
  component: PromotionPickerDemo,
  parameters: {
    layout: "centered",
  },
} satisfies Meta<typeof PromotionPickerDemo>;

export default meta;

type Story = StoryObj<typeof meta>;

const defaultArgs: PromotionPickerDemoProps = {
  color: "w",
  initiallyPending: true,
};

export const WideAnchoredPicker: Story = {
  name: "Wide anchored popover",
  args: {
    ...defaultArgs,
    presentation: "popover",
  },
};

export const ConstrainedDrawer: Story = {
  name: "Constrained drawer bottom sheet",
  args: {
    ...defaultArgs,
    presentation: "drawer",
  },
};

export const KeyboardSelection: Story = {
  name: "Keyboard selection",
  args: {
    ...defaultArgs,
    presentation: "popover",
  },
};

export const NativeKeyboardPromotionInitiation: Story = {
  name: "Native keyboard promotion initiation",
  args: {
    color: "w",
    presentation: "drawer",
    initiallyPending: false,
  },
};

export const Cancellation: Story = {
  name: "Escape, outside, and backdrop cancellation",
  args: {
    ...defaultArgs,
    presentation: "drawer",
  },
};

export const StaleAndIllegalRejection: Story = {
  name: "Stale and illegal rejection state",
  args: {
    ...defaultArgs,
    presentation: "popover",
  },
};

export const ForcedColorsAndReducedMotion: Story = {
  name: "Forced colors and reduced motion",
  args: {
    ...defaultArgs,
    presentation: "drawer",
  },
  parameters: {
    backgrounds: { default: "dark" },
    docs: {
      description: {
        story:
          "Review this state with forced colors and prefers-reduced-motion emulation enabled in the browser.",
      },
    },
  },
};
