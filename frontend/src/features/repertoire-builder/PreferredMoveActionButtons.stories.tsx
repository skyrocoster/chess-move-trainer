import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import { RemovePreferredMoveButton, SavePreferredMoveButton } from "./PreferredMoveActionButtons";
import { PreferredMoveActionLayout } from "./PreferredMovePrimitives";

const meta = {
  title: "Application/Repertoire Builder/Preferred Move Action Buttons",
  parameters: { layout: "fullscreen" },
  render: () => (
    <main
      style={{
        minHeight: "100vh",
        padding: "var(--cmt-spacing-24)",
        backgroundColor: "var(--md-sys-color-surface)",
        color: "var(--md-sys-color-on-surface)",
      }}
    >
      <PreferredMoveActionLayout>
        <SavePreferredMoveButton onClick={fn()} />
        <RemovePreferredMoveButton onClick={fn()} />
      </PreferredMoveActionLayout>
    </main>
  ),
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

export const ActionButtons: Story = {
  name: "Save and Remove action buttons",
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const save = canvas.getByRole("button", { name: "Save" });
    const remove = canvas.getByRole("button", { name: "Remove" });
    await expect(save).toBeEnabled();
    await expect(remove).toBeEnabled();
    await userEvent.click(save);
    await expect(save).toBeEnabled();
  },
};

export const PendingSave: Story = {
  name: "Pending Save keeps its accessible label and disables",
  render: () => (
    <main
      style={{
        minHeight: "100vh",
        padding: "var(--cmt-spacing-24)",
        backgroundColor: "var(--md-sys-color-surface)",
        color: "var(--md-sys-color-on-surface)",
      }}
    >
      <PreferredMoveActionLayout>
        <SavePreferredMoveButton pending onClick={fn()} />
      </PreferredMoveActionLayout>
    </main>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const save = canvas.getByRole("button", { name: "Save" });
    await expect(save).toBeDisabled();
    await expect(save).toHaveAttribute("aria-busy", "true");
  },
};
