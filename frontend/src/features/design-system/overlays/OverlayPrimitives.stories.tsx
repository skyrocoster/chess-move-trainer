import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../../styles/cmt-tokens.css";
import "../../../styles/cmt-typescale.css";
import { Button } from "../Button";
import { Dialog } from "./Dialog";
import { PreviewCard } from "./PreviewCard";
import { ToastProvider, useToast } from "./Toast";
import { Tooltip, TooltipProvider } from "./Tooltip";

const meta = {
  title: "Production/Design System/Base UI/Overlays",
  tags: ["status-production"],
  parameters: { layout: "centered" },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

export const DialogExample: Story = {
  render: () => (
    <Dialog
      trigger="Open dialog"
      title="Delete repertoire line?"
      description="This removes the selected branch from your repertoire."
    >
      The training history for other lines is not affected.
    </Dialog>
  ),
};

export const PreviewCardExample: Story = {
  render: () => (
    <PreviewCard href="#openings" trigger="Sicilian Defence">
      <strong>Sicilian Defence</strong>
      <p>Review saved branches beginning with 1. e4 c5.</p>
    </PreviewCard>
  ),
};

function ToastDemo() {
  const toast = useToast();
  return (
    <Button
      onClick={() =>
        toast.add({
          type: "success",
          title: "Line saved",
          description: "The repertoire was updated.",
        })
      }
    >
      Show toast
    </Button>
  );
}

export const ToastExample: Story = {
  render: () => (
    <ToastProvider timeout={0}>
      <ToastDemo />
    </ToastProvider>
  ),
};

export const TooltipExample: Story = {
  render: () => (
    <TooltipProvider delay={200}>
      <Tooltip trigger="?" content="Keyboard shortcuts" />
    </TooltipProvider>
  ),
};
