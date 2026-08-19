import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import type { ReactNode } from "react";

import { Disclosure } from "./Disclosure";

const meta = {
  title: "DesignSystem/Disclosure",
  component: Disclosure,
  args: {
    summary: "Disclosure",
  },
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta<typeof Disclosure>;

export default meta;
type Story = StoryObj<typeof meta>;

const shell = (children: ReactNode) => (
  <main
    style={{
      display: "flex",
      flexDirection: "column",
      gap: "var(--cmt-spacing-24)",
      padding: "var(--cmt-spacing-32)",
      minHeight: "100vh",
      backgroundColor: "var(--md-sys-color-surface)",
      color: "var(--md-sys-color-on-surface)",
      fontFamily: "system-ui",
    }}
  >
    {children}
  </main>
);

const LONG_CONTENT = Array.from(
  { length: 12 },
  (_, index) =>
    `Temporary context note number ${index + 1}: more analysis content could be placed here.`,
);

export const CollapsedByDefault: Story = {
  render: () =>
    shell(
      <Disclosure summary="Position picker">
        <p style={{ margin: "var(--cmt-spacing-16)" }}>
          The collapsible body. Closed until the summary is activated.
        </p>
      </Disclosure>,
    ),
};

export const OpenByDefault: Story = {
  render: () =>
    shell(
      <Disclosure summary="Loaded position" defaultOpen>
        <p style={{ margin: "var(--cmt-spacing-16)" }}>
          The collapsible body, rendered open on first paint.
        </p>
      </Disclosure>,
    ),
};

export const WithLongContent: Story = {
  render: () =>
    shell(
      <Disclosure summary="Context" defaultOpen>
        <ul
          style={{
            margin: 0,
            padding: "0 var(--cmt-spacing-16) var(--cmt-spacing-16) var(--cmt-spacing-32)",
          }}
        >
          {LONG_CONTENT.map((note) => (
            <li key={note} style={{ marginBlockStart: "var(--cmt-spacing-8)" }}>
              {note}
            </li>
          ))}
        </ul>
      </Disclosure>,
    ),
};
