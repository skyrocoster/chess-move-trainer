import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { StatusPage } from "./StatusPage";

const meta = {
  title: "Application/Status/Status Page",
  component: StatusPage,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof StatusPage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <main
      style={{
        minHeight: "100vh",
        padding: "var(--cmt-spacing-24)",
        background: "var(--md-sys-color-background)",
        color: "var(--md-sys-color-on-background)",
      }}
    >
      <StatusPage />
    </main>
  ),
};
