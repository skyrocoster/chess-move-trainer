import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, userEvent, within } from "storybook/test";
import { Search, Sparkles } from "lucide-react";
import { useState, type ReactNode } from "react";

import "../../../styles/cmt-tokens.css";
import "../../../styles/cmt-typescale.css";
import { storyViewport } from "../../../storybook/viewports";
import { Button } from "../Button";
import { Autocomplete } from "./Autocomplete";
import { Combobox } from "./Combobox";
import { Field } from "./Field";
import styles from "./FormControls.module.css";
import { RadioGroup, type RadioOption } from "./RadioGroup";
import { Select } from "./Select";
import { TextInput } from "./TextInput";
import type { DropdownOptionDefinition } from "./private/DropdownParts";

const meta = {
  title: "In Development/Design System/Exploration/Reusable Form Controls",
  tags: ["status-in-development"],
  parameters: { layout: "fullscreen" },
  decorators: [
    (Story) => (
      <main
        style={{
          minHeight: "100vh",
          padding: "var(--cmt-spacing-32)",
          background: "var(--md-sys-color-surface)",
          color: "var(--md-sys-color-on-surface)",
        }}
      >
        <Story />
      </main>
    ),
  ],
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

const RADIO_SHORT: readonly RadioOption[] = [
  { value: "both", label: "Both" },
  { value: "white", label: "White" },
  { value: "black", label: "Black" },
];

const RADIO_LONG: readonly RadioOption[] = [
  { value: "all", label: "All positions", description: "Include every matching training position." },
  { value: "due", label: "Due for review", description: "Only positions scheduled for today or earlier." },
  { value: "new", label: "Unseen positions", description: "Limit the result to positions not trained before." },
];

const OPENINGS: readonly DropdownOptionDefinition[] = [
  opening("B10", "Caro-Kann Defense", "1.e4 c6", "Black", "18 lines"),
  opening("B12", "Caro-Kann Defense: Advance Variation", "1.e4 c6 2.d4 d5 3.e5", "White", "11 lines"),
  opening("B15", "Caro-Kann Defense: Gurgenidze Counterattack", "1.e4 c6 2.d4 d5 3.Nc3 g6", "Black", "4 lines"),
  opening("B18", "Caro-Kann Defense: Classical Variation", "1.e4 c6 2.d4 d5 3.Nc3 dxe4 4.Nxe4 Bf5", "Black", "7 lines"),
  opening("C20", "Italian Game", "1.e4 e5 2.Bc4", "White", "15 lines"),
  opening("D00", "Queen's Pawn Game", "1.d4 d5", "White", "9 lines"),
  opening("E12", "Queen's Indian Defense", "1.d4 Nf6 2.c4 e6 3.Nf3 b6", "Black", "6 lines"),
  opening("A45", "Indian Game", "1.d4 Nf6", "Black", "12 lines"),
];

function opening(
  eco: string,
  name: string,
  preview: string,
  side: "White" | "Black",
  count: string,
): DropdownOptionDefinition {
  return {
    value: `${eco}:${name}`,
    label: `${eco} ${name}`,
    content: {
      leading: <span className={styles.ecoBadge}>{eco}</span>,
      primary: name,
      secondary: preview,
      trailing: (
        <span className={styles.openingMeta}>
          <span className={styles.repertoireBadge} aria-label={`${side} repertoire`}>
            <span aria-hidden="true">{side === "White" ? "♙" : "♟"}</span>
            <span className={styles.repertoireText}>{side}</span>
          </span>
          <span className={styles.openingLineCount}>{count}</span>
        </span>
      ),
    },
  };
}

function section(title: string, children: ReactNode) {
  return (
    <section style={{ display: "grid", gap: "var(--cmt-spacing-16)" }}>
      <h2 style={{ margin: 0, fontSize: "var(--md-sys-typescale-title-medium-size)" }}>{title}</h2>
      {children}
    </section>
  );
}

function grid(children: ReactNode, maxWidth = "68rem") {
  return (
    <div
      style={{
        maxInlineSize: maxWidth,
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 18rem), 1fr))",
        gap: "var(--cmt-spacing-32)",
      }}
    >
      {children}
    </div>
  );
}

function FoundationsFixture() {
  const [query, setQuery] = useState("");
  return grid(
    <>
      {section(
        "Normal with slots",
        <Field label="Opening search" description="Search by name, ECO, or key.">
          <TextInput
            aria-label="Opening search"
            leading={<Search aria-hidden="true" size={18} />}
            trailing={<span className={styles.ecoBadge}>B12</span>}
            placeholder="Try Caro or B12"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.currentTarget.value)}
          />
        </Field>,
      )}
      {section(
        "Required and invalid",
        <Field label="Email" required invalid error="Enter a complete email address.">
          <TextInput aria-label="Email" invalid required type="email" defaultValue="learner@" />
        </Field>,
      )}
      {section(
        "Disabled",
        <Field label="Account URL" disabled description="Unavailable while the account loads.">
          <TextInput aria-label="Account URL" disabled type="url" defaultValue="https://example.test" />
        </Field>,
      )}
      {section(
        "Read-only",
        <Field label="Phone">
          <TextInput aria-label="Phone" readOnly type="tel" defaultValue="+1 555 0100" />
        </Field>,
      )}
    </>,
  );
}

export const FieldAndTextInputStates: Story = {
  render: () => <FoundationsFixture />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("searchbox", { name: "Opening search" }));
    await expect(canvas.getByRole("searchbox", { name: "Opening search" })).toHaveFocus();
    await expect(canvas.getByRole("textbox", { name: "Email" })).toHaveAttribute("aria-invalid", "true");
  },
};

function DropdownFixture() {
  const [selectValue, setSelectValue] = useState<string | null>("daily");
  const [comboValue, setComboValue] = useState<string | null>(OPENINGS[1].value);
  const [autocompleteValue, setAutocompleteValue] = useState("Tactical review");
  const suggestions: readonly DropdownOptionDefinition[] = [
    { value: "daily", label: "Daily review" },
    { value: "tactical", label: "Tactical review" },
    { value: "opening", label: "Opening preparation" },
  ];
  return grid(
    <>
      {section(
        "Select",
        <Field label="Training mode">
          <Select
            ariaLabel="Training mode"
            options={suggestions}
            value={selectValue}
            onValueChange={setSelectValue}
          />
        </Field>,
      )}
      {section(
        "Restricted-value combobox",
        <Field label="Opening">
          <Combobox
            ariaLabel="Opening"
            leading={<Search aria-hidden="true" size={18} />}
            options={OPENINGS}
            preferredPopupWidth="42rem"
            value={comboValue}
            onValueChange={setComboValue}
          />
        </Field>,
      )}
      {section(
        "Free-form autocomplete",
        <Field label="Session name" description="Suggestions are optional; any text is accepted.">
          <Autocomplete
            ariaLabel="Session name"
            options={suggestions}
            value={autocompleteValue}
            onValueChange={setAutocompleteValue}
          />
          <output>Current text: {autocompleteValue}</output>
        </Field>,
      )}
    </>,
  );
}

export const DistinctDropdownSemantics: Story = {
  render: () => <DropdownFixture />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await userEvent.click(canvas.getByRole("combobox", { name: "Opening" }));
    await expect(body.getByRole("option", { name: /B12 Caro-Kann/ })).toBeVisible();
    await userEvent.keyboard("{Escape}");
    const autocomplete = canvas.getByRole("combobox", { name: "Session name" });
    await userEvent.clear(autocomplete);
    await userEvent.type(autocomplete, "My own session");
    await expect(canvas.getByText("Current text: My own session")).toBeVisible();
    await userEvent.keyboard("{Escape}");
  },
};

function RichComboboxFixture({ initial = OPENINGS[1].value }: { initial?: string | null }) {
  const [value, setValue] = useState<string | null>(initial);
  return (
    <div style={{ maxInlineSize: "34rem" }}>
      <Field label="Opening" description="Fixture-backed visual anatomy for review.">
        <Combobox
          ariaLabel="Opening"
          leading={<Search aria-hidden="true" size={18} />}
          options={OPENINGS}
          preferredPopupWidth="46rem"
          value={value}
          onValueChange={setValue}
        />
      </Field>
    </div>
  );
}

export const RichSelectedCombobox: Story = {
  render: () => <RichComboboxFixture />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await userEvent.click(canvas.getByRole("combobox", { name: "Opening" }));
    await expect(body.getByRole("option", { name: /B12 Caro-Kann/ })).toHaveAttribute(
      "data-selected",
    );
  },
};

const CUSTOM_OPTIONS: readonly DropdownOptionDefinition[] = [
  {
    value: "guided",
    label: "Guided review with coach notes",
    customBody: (
      <span className={styles.customOption}>
        <span><Sparkles aria-hidden="true" size={18} /> Guided review</span>
        <strong>12 min</strong>
      </span>
    ),
  },
  { value: "standard", label: "Standard review" },
];

function CustomAndStatusFixture() {
  const [value, setValue] = useState<string | null>("guided");
  return grid(
    <>
      {section(
        "Custom visual body",
        <Combobox
          ariaLabel="Review format"
          options={CUSTOM_OPTIONS}
          value={value}
          onValueChange={setValue}
        />,
      )}
      {section(
        "Loading override",
        <Select
          ariaLabel="Loading repertoire"
          loading
          loadingContent="Loading repertoire choices…"
          options={[]}
          value={null}
          onValueChange={() => undefined}
        />,
      )}
      {section(
        "Empty default",
        <Combobox
          ariaLabel="Empty opening list"
          options={[]}
          value={null}
          onValueChange={() => undefined}
        />,
      )}
      <Button variant="secondary">Ordinary candidate action</Button>
    </>,
  );
}

export const CustomOptionLoadingAndEmpty: Story = {
  render: () => <CustomAndStatusFixture />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await userEvent.click(canvas.getByRole("combobox", { name: "Review format" }));
    await expect(body.getByRole("option", { name: "Guided review with coach notes" })).toBeVisible();
    await userEvent.keyboard("{Escape}");
    await userEvent.click(canvas.getByRole("combobox", { name: "Loading repertoire" }));
    await expect(body.getByText("Loading repertoire choices…")).toBeVisible();
    await userEvent.keyboard("{Escape}");
  },
};

function RadioFixture() {
  const [side, setSide] = useState("both");
  const [scope, setScope] = useState("due");
  return grid(
    <>
      {section(
        "Segmented — explicitly selected",
        <RadioGroup ariaLabel="Repertoire side" options={RADIO_SHORT} value={side} onValueChange={setSide} />,
      )}
      {section(
        "Stacked — explicitly selected",
        <RadioGroup
          appearance="stacked"
          ariaLabel="Training scope"
          options={RADIO_LONG}
          value={scope}
          onValueChange={setScope}
        />,
      )}
    </>,
  );
}

export const RadioGroupAppearances: Story = {
  parameters: storyViewport("panel-breakpoint-640"),
  render: () => <RadioFixture />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("radio", { name: "White" }));
    await expect(canvas.getByRole("radio", { name: "White" })).toBeChecked();
    await expect(canvas.getByRole("radio", { name: /Due for review/ })).toBeChecked();
  },
};

export const NarrowRichPopup: Story = {
  parameters: storyViewport("constrained-412"),
  render: () => <RichComboboxFixture />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await userEvent.click(canvas.getByRole("combobox", { name: "Opening" }));
    await expect(body.getByRole("option", { name: /B12 Caro-Kann/ })).toBeVisible();
  },
};

export const CollisionAndBoundedScroll: Story = {
  parameters: storyViewport("workspace-wide-1280"),
  render: () => (
    <div style={{ maxInlineSize: "34rem", marginInlineStart: "auto", paddingBlockStart: "38rem" }}>
      <RichComboboxFixture initial={null} />
    </div>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await userEvent.click(canvas.getByRole("combobox", { name: "Opening" }));
    const listbox = body.getByRole("listbox");
    await expect(listbox).toBeVisible();
    await expect(listbox.closest("[data-side]")).toHaveAttribute("data-side", "top");
  },
};
