import "../../../styles/cmt-tokens.css";
import "../../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { useState, type ReactNode } from "react";

import { LineLibraryFilters } from "./LineLibraryFilters";
import type {
  LineLibraryFilterDefinition,
  LineLibraryFilterValue,
  LineLibraryFilterValues,
} from "./lineLibraryTypes";

const definitions: LineLibraryFilterDefinition[] = [
  { id: "query", label: "Search", kind: "search", placeholder: "Find a line" },
  {
    id: "scope",
    label: "Scope",
    kind: "select",
    options: [
      { value: "all", label: "All" },
      { value: "recent", label: "Recent" },
    ],
  },
  { id: "only-selectable", label: "Only selectable", kind: "boolean" },
];

const meta = {
  title: "Design System/Components/Line Library Filters",
  component: LineLibraryFilters,
  parameters: { layout: "fullscreen" },
  args: {
    definitions,
    values: { query: "", scope: "", "only-selectable": false },
    mode: "explicit",
    onChange: fn(),
    onApply: fn(),
    disabled: false,
  },
} satisfies Meta<typeof LineLibraryFilters>;

export default meta;
type Story = StoryObj<typeof meta>;

function shell(children: ReactNode) {
  return (
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
}

interface FilterFixtureProps {
  mode: "immediate" | "explicit";
  initial?: LineLibraryFilterValues;
}

function FilterFixture({ mode, initial }: FilterFixtureProps) {
  const [values, setValues] = useState<LineLibraryFilterValues>(
    initial ?? { query: "", scope: "", "only-selectable": false },
  );

  const handleChange = (id: string, value: LineLibraryFilterValue) => {
    setValues((prev) => ({ ...prev, [id]: value }));
  };

  return (
    <LineLibraryFilters
      definitions={definitions}
      values={values}
      mode={mode}
      onChange={handleChange}
      onApply={fn()}
      disabled={false}
    />
  );
}

export const ExplicitApply: Story = {
  render: () =>
    shell(
      <div style={{ maxInlineSize: "40rem" }}>
        <FilterFixture mode="explicit" />
      </div>,
    ),
};

export const ImmediateApply: Story = {
  render: () =>
    shell(
      <div style={{ maxInlineSize: "40rem" }}>
        <FilterFixture mode="immediate" />
      </div>,
    ),
};

export const Disabled: Story = {
  render: () =>
    shell(
      <div style={{ maxInlineSize: "40rem" }}>
        <LineLibraryFilters
          definitions={definitions}
          values={{ query: "queen", scope: "recent", "only-selectable": true }}
          mode="explicit"
          onChange={fn()}
          onApply={fn()}
          disabled
        />
      </div>,
    ),
};
