import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import {
  StoryHarnessPromotionPicker,
  type StoryHarnessPromotionPickerProps,
} from "./StoryHarnessPromotionPicker";

const meta = {
  title: "Documentation/Demos/Promotion Picker",
  component: StoryHarnessPromotionPicker,
  decorators: [
    (Story) => (
      <div style={{ background: "var(--md-sys-color-background)" }}>
        <Story />
      </div>
    ),
  ],
  parameters: {
    layout: "centered",
    docs: {
      description: {
        component:
          "Storybook-only demonstration fixture for the production promotion picker and its board integration.",
      },
    },
  },
} satisfies Meta<typeof StoryHarnessPromotionPicker>;

export default meta;

type Story = StoryObj<typeof meta>;

const defaultArgs: StoryHarnessPromotionPickerProps = {
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
    onCommit: fn(),
  },
  play: async ({ args, canvasElement }) => {
    const body = within(canvasElement.ownerDocument.body);
    const dialog = await body.findByRole("dialog", { name: "Choose a promotion piece" });
    const choices = within(dialog);
    await expect(choices.getByRole("button", { name: "Promote to queen" })).toHaveFocus();
    await userEvent.tab();
    await expect(choices.getByRole("button", { name: "Promote to rook" })).toHaveFocus();
    await userEvent.keyboard("{Enter}");
    await expect(args.onCommit).toHaveBeenCalledTimes(1);
    await expect(args.onCommit).toHaveBeenCalledWith(
      expect.objectContaining({
        move: expect.objectContaining({ from: "e7", to: "e8", promotion: "r" }),
        history: [expect.stringContaining("e8=R")],
      }),
    );
  },
};

export const NativeKeyboardPromotionInitiation: Story = {
  name: "Promotion initiation browser fixture",
  args: {
    color: "w",
    presentation: "drawer",
    initiallyPending: false,
  },
};

export const Cancellation: Story = {
  name: "Escape cancellation",
  args: {
    ...defaultArgs,
    presentation: "drawer",
    onCancel: fn(),
  },
  play: async ({ args, canvasElement }) => {
    const body = within(canvasElement.ownerDocument.body);
    await body.findByRole("dialog", { name: "Choose a promotion piece" });
    await userEvent.keyboard("{Escape}");
    await expect(args.onCancel).toHaveBeenCalledTimes(1);
    await expect(
      body.queryByRole("dialog", { name: "Choose a promotion piece" }),
    ).not.toBeInTheDocument();
  },
};

export const StaleAndIllegalRejection: Story = {
  name: "Pending selection for rejection browser proof",
  args: {
    ...defaultArgs,
    presentation: "popover",
  },
};

export const ForcedColorsAndReducedMotion: Story = {
  name: "Media emulation browser fixture",
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
