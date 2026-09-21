import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { Accordion } from "./Accordion";
import { Avatar } from "./Avatar";
import { ScrollArea } from "./ScrollArea";
import { Separator } from "./Separator";

const meta = {
  title: "Production/Design System/Base UI/Content Primitives",
  tags: ["status-production"],
  parameters: { layout: "centered" },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

export const AccordionExample: Story = {
  render: () => (
    <div style={{ width: "min(34rem, 90vw)" }}>
      <Accordion
        defaultValue={["purpose"]}
        items={[
          {
            value: "purpose",
            summary: "What should I train?",
            content: "Choose a repertoire branch and recall the saved move before revealing it.",
          },
          {
            value: "review",
            summary: "When should I review it?",
            content: "Return when the move is due or after adding a new branch.",
          },
        ]}
      />
    </div>
  ),
};

export const AvatarExamples: Story = {
  render: () => (
    <div style={{ display: "flex", alignItems: "center", gap: "var(--cmt-spacing-16)" }}>
      <Avatar alt="Alex Morgan" fallback="AM" size="sm" />
      <Avatar alt="Chess coach" fallback="CC" />
    </div>
  ),
};

export const ScrollAreaExample: Story = {
  render: () => (
    <ScrollArea
      aria-label="Move history"
      style={{ width: "20rem", height: "10rem" }}
      orientation="vertical"
    >
      <div style={{ padding: "var(--cmt-spacing-16)" }}>
        {Array.from({ length: 12 }, (_, index) => (
          <p key={index}>Move {index + 1}: candidate line</p>
        ))}
      </div>
    </ScrollArea>
  ),
};

export const SeparatorExample: Story = {
  render: () => (
    <div style={{ display: "grid", gap: "var(--cmt-spacing-16)", width: "20rem" }}>
      <span>Position</span>
      <Separator />
      <span>Engine lines</span>
    </div>
  ),
};
