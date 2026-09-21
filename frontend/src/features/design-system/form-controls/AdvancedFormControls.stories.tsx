import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../../styles/cmt-tokens.css";
import "../../../styles/cmt-typescale.css";
import { Button } from "../Button";
import { CheckboxGroup } from "./CheckboxGroup";
import { Fieldset } from "./Fieldset";
import { Form } from "./Form";
import { NumberField } from "./NumberField";
import { OtpField } from "./OtpField";
import { Slider } from "./Slider";
import { Switch } from "./Switch";
import { Toggle } from "./Toggle";
import { ToggleGroup } from "./ToggleGroup";

const meta = {
  title: "Production/Design System/Base UI/Advanced Form Controls",
  tags: ["status-production"],
  parameters: { layout: "centered" },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

export const CheckboxGroupExample: Story = {
  render: () => (
    <CheckboxGroup
      label="Study focus"
      description="Select one or more themes."
      defaultValue={["tactics"]}
      options={[
        { value: "tactics", label: "Tactics", description: "Forcing moves and combinations" },
        { value: "openings", label: "Openings", description: "Saved repertoire branches" },
        { value: "endgames", label: "Endgames", description: "Technical positions" },
      ]}
    />
  ),
};

export const FieldsetExample: Story = {
  render: () => (
    <Fieldset legend="Board settings" description="These preferences apply to every board.">
      <Switch label="Show coordinates" defaultChecked />
      <Switch label="Animate moves" />
    </Fieldset>
  ),
};

export const FormExample: Story = {
  render: () => (
    <Form aria-label="Example form" onFormSubmit={() => undefined}>
      <NumberField label="Daily goal" defaultValue={10} min={1} max={100} />
      <Button type="submit">Save goal</Button>
    </Form>
  ),
};

export const NumberFieldExample: Story = {
  render: () => (
    <NumberField
      label="Engine depth"
      description="Higher values take longer to calculate."
      defaultValue={18}
      min={1}
      max={40}
    />
  ),
};

export const OtpFieldExample: Story = {
  render: () => (
    <OtpField
      label="Verification code"
      description="Enter the six digits sent to your device."
      length={6}
    />
  ),
};

export const SliderExample: Story = {
  render: () => (
    <div style={{ width: "20rem" }}>
      <Slider label="Evaluation window" defaultValue={[-3, 3]} min={-10} max={10} />
    </div>
  ),
};

export const SwitchExample: Story = {
  render: () => (
    <Switch
      label="Auto-advance"
      description="Continue to the next move after a correct answer."
      defaultChecked
    />
  ),
};

export const ToggleExample: Story = {
  render: () => <Toggle defaultPressed>Pin variation</Toggle>,
};

export const ToggleGroupExample: Story = {
  render: () => (
    <ToggleGroup
      aria-label="Board overlays"
      defaultValue={["arrows"]}
      multiple
      options={[
        { value: "arrows", label: "Arrows" },
        { value: "squares", label: "Squares" },
        { value: "coordinates", label: "Coordinates" },
      ]}
    />
  ),
};
