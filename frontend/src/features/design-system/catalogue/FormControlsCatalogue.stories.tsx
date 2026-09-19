import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";

import { Button } from "../Button";
import { Autocomplete } from "../form-controls/Autocomplete";
import { Combobox } from "../form-controls/Combobox";
import { Field } from "../form-controls/Field";
import { RadioGroup } from "../form-controls/RadioGroup";
import { Select } from "../form-controls/Select";
import { TextInput } from "../form-controls/TextInput";
import type { DropdownOptionDefinition } from "../form-controls/private/DropdownParts";
import { storyViewport } from "../../../storybook/viewports";
import { DemoRow, FamilyPage } from "./FamilyPage";
import styles from "./catalogue.module.css";

const meta = {
  title: "Reference/Catalogue/Actions and Form Controls",
  tags: ["status-reference"],
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta;

export default meta;

type Story = StoryObj<typeof meta>;

const OPTIONS: DropdownOptionDefinition[] = [
  { value: "openings-a", label: "Openings" },
  { value: "repertoire", label: "Repertoire" },
  { value: "practice", label: "Practice" },
  {
    value: "rich-option",
    label: "Rich option",
    disabled: true,
    content: {
      primary: "Rich option",
      secondary: "option with secondary copy",
      trailing: "E60",
    },
  },
];

const RADIO_OPTIONS = [
  { value: "white", label: "White subject" },
  { value: "black", label: "Black subject", description: "Fitted from Black's reply" },
];

function shell(children: React.ReactNode) {
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
      }}
    >
      {children}
    </main>
  );
}

function ControlledSelectHarness() {
  const [value, setValue] = useState<string | null>("repertoire");
  return (
    <Select
      ariaLabel="Analysis mode"
      options={OPTIONS}
      value={value}
      onValueChange={setValue}
    />
  );
}

function ControlledSelectLoadingHarness() {
  const [value, setValue] = useState<string | null>(null);
  return (
    <Select ariaLabel="Loading analysis mode" options={OPTIONS} loading value={value} onValueChange={setValue} />
  );
}

function ControlledSelectEmptyHarness() {
  const [value, setValue] = useState<string | null>(null);
  return (
    <Select
      ariaLabel="Empty analysis mode"
      options={[]}
      emptyContent="No analysis modes found."
      value={value}
      onValueChange={setValue}
    />
  );
}

function ControlledComboboxHarness() {
  const [value, setValue] = useState<string | null>(null);
  return (
    <Combobox ariaLabel="Opening search" options={OPTIONS} value={value} onValueChange={setValue} />
  );
}

function ControlledAutocompleteHarness() {
  const [value, setValue] = useState<string>("repertoire");
  return (
    <Autocomplete ariaLabel="Opening suggestion" options={OPTIONS} value={value} onValueChange={setValue} />
  );
}

export const Docs: Story = {
  render: () => (
    <FamilyPage
      family="Actions and Form Controls"
      intro={
        <>
          The shared controls in features/design-system and their Base UI behavior layer. Existing
          production coverage lives in the Production/Design System stories; the demos below fill
          the gaps for controls that previously had no stories. All form controls compose Base UI
          primitives (no native-only fallbacks), and validation state stays outside the controls.
        </>
      }
      caution="There is currently no shared Checkbox component in the design system. Checkbox-like behavior inside features is composed locally. There is also no standalone Toolbar component; Base UI's Toolbar is used inside feature components such as BoardControl."
      sections={[
        {
          heading: "Button",
          body: (
            <>
              Token-driven button built on the Base UI headless Button primitive. Three variants
              (primary, secondary, ghost) across two sizes (md, sm), plus the disabled state.
              Interactive by nature; the existing story shows the full matrix.
            </>
          ),
          links: [
            {
              label: "Production/Design System/Components/Button — Variant Matrix",
              storyId: "production-design-system-components-button--variant-matrix",
            },
          ],
        },
        {
          heading: "Field",
          body: (
            <>
              Presentation-only field scaffolding around the Base UI Field: label (with an optional
              required mark), optional description, optional error text, and disabled/invalid
              wiring. It owns no validation timing or form state; pass the error and invalid props
              from the caller. The Base Field association connects the label, description, and
              error to the child control for accessibility.
            </>
          ),
        },
        {
          heading: "TextInput",
          body: (
            <>
              Base UI Input wrapped in a shared frame with optional leading and trailing slots and
              an invalid state. Standard input types (text, search, email, url, tel, password) are
              supported; combine with Field for labels, descriptions, and errors.
            </>
          ),
        },
        {
          heading: "Select, Combobox, Autocomplete",
          body: (
            <>
              Dropdown controls sharing one presentation: Select for plain choice lists, Combobox
              for filterable search with typed input and a clear action, Autocomplete for free
              text backed by suggestions. All three accept loading (options hidden with a loading
              message) and empty states, and the popup options can be rich compositions via
              DropdownOptionContent. Note the Base UI popup renders in a portal, so popup styling
              is visible only while a popup is open. Provide ariaLabel on every control: the
              controls rely on it for the accessible name.
            </>
          ),
        },
        {
          heading: "RadioGroup",
          body: (
            <>
              Base UI Radio Group with two appearance names: segmented (inline toggle bar for a
              small choice set) and stacked (vertical list that can carry a second description
              line). Provide the required ariaLabel (the group's accessible name). The group is
              required by default (required=true) and options may be individually disabled.
            </>
          ),
        },
        {
          heading: "Toolbar usage",
          body: (
            <>
              The Board control strip is composed from Base UI Toolbar inside the board adapter
              feature. It is not a reusable shared control today; see its existing stories for the
              keyboard and constrained variants.
            </>
          ),
          links: [
            {
              label: "Production/Application/Board/Board Controls — KeyboardToolbar",
              storyId: "production-application-board-board-controls--keyboard-toolbar",
              note: "toolbar behavior in the real production context",
            },
          ],
        },
        {
          heading: "Demos",
          body: "Rendered with the actual production components and the FormControls styles.",
          links: [
            {
              label: "Field States",
              storyId: "reference-catalogue-actions-and-form-controls--field-states",
            },
            {
              label: "TextInput States",
              storyId: "reference-catalogue-actions-and-form-controls--text-input-states",
            },
            {
              label: "Select States",
              storyId: "reference-catalogue-actions-and-form-controls--select-states",
            },
            {
              label: "Select Loading and Empty",
              storyId: "reference-catalogue-actions-and-form-controls--select-loading-and-empty",
            },
            {
              label: "Combobox States",
              storyId: "reference-catalogue-actions-and-form-controls--combobox-states",
            },
            {
              label: "Autocomplete States",
              storyId: "reference-catalogue-actions-and-form-controls--autocomplete-states",
            },
            {
              label: "RadioGroup States",
              storyId: "reference-catalogue-actions-and-form-controls--radio-group-states",
            },
            {
              label: "Narrow Viewport",
              storyId: "reference-catalogue-actions-and-form-controls--narrow-viewport",
              note: "the under-560px behavior of the shared control styles",
            },
          ],
        },
      ]}
    />
  ),
};

export const FieldStates: Story = {
  render: () =>
    shell(
      <div className={styles.demoStack}>
        <DemoRow caption="Default with a description">
          <Field
            label="Analysis mode"
            description="How the position should be evaluated."
            htmlFor="catalogue-description-input"
          >
            <TextInput id="catalogue-description-input" aria-label="Analysis mode" />
          </Field>
        </DemoRow>
        <DemoRow caption="Required with mark">
          <Field label="Opening name" required htmlFor="catalogue-required-input">
            <TextInput id="catalogue-required-input" aria-label="Opening name" />
          </Field>
        </DemoRow>
        <DemoRow caption="Invalid with visible error text">
          <Field
            label="FEN"
            htmlFor="catalogue-invalid-input"
            invalid
            error="Not a valid FEN string."
          >
            <TextInput id="catalogue-invalid-input" invalid value="not-a-fen" readOnly />
          </Field>
        </DemoRow>
        <DemoRow caption="Disabled">
          <Field label="FEN" htmlFor="catalogue-disabled-input" disabled>
            <TextInput id="catalogue-disabled-input" disabled />
          </Field>
        </DemoRow>
      </div>,
    ),
};

export const TextInputStates: Story = {
  render: () =>
    shell(
      <div className={styles.demoStack}>
        <DemoRow caption="Default">
          <div className={styles.demoControlWrap}>
            <TextInput aria-label="Default text input" />
          </div>
        </DemoRow>
        <DemoRow caption="Search type with leading icon and trailing action">
          <div className={styles.demoControlWrap}>
            <TextInput
              type="search"
              aria-label="Search source"
              leading={
                <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
                  <circle cx="10" cy="10" r="7" fill="none" stroke="currentColor" strokeWidth="2" />
                  <path d="M15.5 15.5 21 21" stroke="currentColor" strokeWidth="2" />
                </svg>
              }
              trailing={<Button size="sm">Filter</Button>}
            />
          </div>
        </DemoRow>
        <DemoRow caption="Invalid">
          <div className={styles.demoControlWrap}>
            <TextInput aria-label="Invalid input example" invalid value="not-a-fen" readOnly />
          </div>
        </DemoRow>
        <DemoRow caption="Disabled">
          <div className={styles.demoControlWrap}>
            <TextInput aria-label="Disabled input example" disabled />
          </div>
        </DemoRow>
      </div>,
    ),
};

export const SelectStates: Story = {
  render: () =>
    shell(
      <div className={styles.demoStack}>
        <DemoRow caption="Default (interactive: open, choose, clear of the popup)">
          <div className={styles.demoControlWrap}>
            <ControlledSelectHarness />
          </div>
        </DemoRow>
        <DemoRow caption="Disabled">
          <div className={styles.demoControlWrap}>
            <Select
              ariaLabel="Disabled select"
              options={OPTIONS}
              value="repertoire"
              onValueChange={() => undefined}
              disabled
            />
          </div>
        </DemoRow>
        <DemoRow caption="Read-only">
          <div className={styles.demoControlWrap}>
            <Select
              ariaLabel="Read-only select"
              options={OPTIONS}
              value="repertoire"
              onValueChange={() => undefined}
              readOnly
            />
          </div>
        </DemoRow>
      </div>,
    ),
};

export const SelectLoadingAndEmpty: Story = {
  render: () =>
    shell(
      <div className={styles.demoStack}>
        <DemoRow caption="Loading (options replaced by a loading message in the popup)">
          <div className={styles.demoControlWrap}>
            <ControlledSelectLoadingHarness />
          </div>
        </DemoRow>
        <DemoRow caption="Empty (popup shows the caller's empty message)">
          <div className={styles.demoControlWrap}>
            <ControlledSelectEmptyHarness />
          </div>
        </DemoRow>
      </div>,
    ),
};

export const ComboboxStates: Story = {
  render: () =>
    shell(
      <div className={styles.demoStack}>
        <DemoRow caption="Default (interactive: type to filter, clear, or choose an option)">
          <div className={styles.demoControlWrap}>
            <ControlledComboboxHarness />
          </div>
        </DemoRow>
        <DemoRow caption="Loading">
          <div className={styles.demoControlWrap}>
            <Combobox
              ariaLabel="Loading combobox"
              options={OPTIONS}
              loading
              value={null}
              onValueChange={() => undefined}
            />
          </div>
        </DemoRow>
        <DemoRow caption="Disabled with a selected value">
          <div className={styles.demoControlWrap}>
            <Combobox
              ariaLabel="Disabled combobox"
              options={OPTIONS}
              value="repertoire"
              disabled
              onValueChange={() => undefined}
            />
          </div>
        </DemoRow>
      </div>,
    ),
};

export const AutocompleteStates: Story = {
  render: () =>
    shell(
      <div className={styles.demoStack}>
        <DemoRow caption="Default (interactive: pick a suggestion or keep typing)">
          <div className={styles.demoControlWrap}>
            <ControlledAutocompleteHarness />
          </div>
        </DemoRow>
        <DemoRow caption="Loading">
          <div className={styles.demoControlWrap}>
            <Autocomplete
              ariaLabel="Loading autocomplete"
              options={OPTIONS}
              loading
              value=""
              onValueChange={() => undefined}
            />
          </div>
        </DemoRow>
        <DemoRow caption="Disabled">
          <div className={styles.demoControlWrap}>
            <Autocomplete
              ariaLabel="Disabled autocomplete"
              options={OPTIONS}
              value="repertoire"
              disabled
              onValueChange={() => undefined}
            />
          </div>
        </DemoRow>
      </div>,
    ),
};

export const RadioGroupStates: Story = {
  render: () =>
    shell(
      <div className={styles.demoStack}>
        <DemoRow caption="Segmented (selected: White subject)">
          <RadioGroup
            ariaLabel="Subject side segmented"
            appearance="segmented"
            options={RADIO_OPTIONS.slice(0, 2)}
            value="white"
            onValueChange={() => undefined}
          />
        </DemoRow>
        <DemoRow caption="Stacked with descriptions and one disabled option">
          <RadioGroup
            ariaLabel="Subject side stacked"
            appearance="stacked"
            options={RADIO_OPTIONS.map((option, index) =>
              index === 1 ? { ...option, disabled: true } : option,
            )}
            value="black"
            onValueChange={() => undefined}
          />
        </DemoRow>
        <DemoRow caption="Disabled group">
          <RadioGroup
            ariaLabel="Disabled subject side"
            options={RADIO_OPTIONS.slice(0, 2)}
            value="white"
            disabled
            onValueChange={() => undefined}
          />
        </DemoRow>
      </div>,
    ),
};

export const NarrowViewport: Story = {
  parameters: storyViewport("constrained-412"),
  render: () =>
    shell(
      <div className={styles.demoStack}>
        <DemoRow caption="Field with required TextInput at the constrained width">
          <Field label="Opening name" required htmlFor="catalogue-narrow-input">
            <TextInput id="catalogue-narrow-input" aria-label="Narrow opening name" />
          </Field>
        </DemoRow>
        <DemoRow caption="Select at the constrained width (opens a popup)">
          <ControlledSelectHarness />
        </DemoRow>
        <DemoRow caption="Segmented RadioGroup at the constrained width">
          <RadioGroup
            ariaLabel="Narrow subject side"
            options={RADIO_OPTIONS.slice(0, 2)}
            value="white"
            onValueChange={() => undefined}
          />
        </DemoRow>
      </div>,
    ),
};
