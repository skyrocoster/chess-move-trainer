import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../../styles/cmt-tokens.css";
import "../../../styles/cmt-typescale.css";
import { NavigationMenu } from "../NavigationMenu";
import { ContextMenu } from "./ContextMenu";
import { Menu } from "./Menu";
import { Menubar } from "./Menubar";

const actions = [
  { id: "copy", label: "Copy FEN", shortcut: "Ctrl+C" },
  { id: "separator", separator: true as const },
  { id: "delete", label: "Delete line" },
];

const meta = {
  title: "Production/Design System/Base UI/Menus and Navigation",
  tags: ["status-production"],
  parameters: { layout: "centered" },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

export const MenuExample: Story = {
  render: () => <Menu trigger="Position actions" items={actions} />,
};

export const ContextMenuExample: Story = {
  render: () => (
    <ContextMenu items={actions}>
      <div
        style={{
          padding: "var(--cmt-spacing-32)",
          border: "1px solid var(--md-sys-color-outline-variant)",
        }}
      >
        Right-click this move card
      </div>
    </ContextMenu>
  ),
};

export const MenubarExample: Story = {
  render: () => (
    <Menubar
      aria-label="Editor commands"
      menus={[
        { id: "file", label: "File", items: actions },
        {
          id: "edit",
          label: "Edit",
          items: [
            { id: "undo", label: "Undo", shortcut: "Ctrl+Z" },
            { id: "redo", label: "Redo", shortcut: "Ctrl+Y" },
          ],
        },
      ]}
    />
  ),
};

export const NavigationMenuExample: Story = {
  render: () => (
    <NavigationMenu
      aria-label="Primary"
      items={[
        {
          id: "train",
          label: "Train",
          links: [
            { id: "due", label: "Due moves", href: "#due", description: "Practice today's queue" },
            { id: "browse", label: "Browse", href: "#browse", description: "Choose an opening" },
          ],
        },
        { id: "analysis", label: "Analysis", href: "#analysis" },
      ]}
    />
  ),
};
