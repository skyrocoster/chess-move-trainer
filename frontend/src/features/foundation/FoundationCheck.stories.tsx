import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, userEvent, within } from "storybook/test";
import { FoundationCheck } from "./FoundationCheck";

const meta = {
  title: "Foundation/Development-only CSS Check",
  component: FoundationCheck,
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta<typeof FoundationCheck>;

export default meta;

type Story = StoryObj<typeof meta>;

export const GlobalAndModuleCSS: Story = {};

export const CollapsibleInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole("button", { name: "Toggle structural proof" });
    const panel = canvas.getByText("Base UI Collapsible panel is visible when expanded.");

    await expect(trigger).toHaveAttribute("aria-expanded", "false");
    await expect(panel).not.toBeVisible();

    trigger.focus();
    await expect(trigger).toHaveFocus();
    await userEvent.keyboard("{Enter}");
    await expect(trigger).toHaveAttribute("aria-expanded", "true");
    await expect(panel).toBeVisible();

    await userEvent.click(trigger);
    await expect(trigger).toHaveAttribute("aria-expanded", "false");
    await expect(panel).not.toBeVisible();
  },
};

export const LucideSemanticIcon: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const control = canvas.getByRole("button", { name: "Foundation icon proof" });

    await expect(control).toBeVisible();
    await expect(control).toHaveAccessibleName("Foundation icon proof");
  },
};

export const ContainedFailure: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const fallback = canvas.getByText(
      "Boundary contained the deliberate development-only render failure.",
    );

    await expect(fallback).toBeVisible();
  },
};
