import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { CheckboxGroup } from "./CheckboxGroup";
import { Field } from "./Field";
import { Fieldset } from "./Fieldset";
import { Form } from "./Form";
import { NumberField } from "./NumberField";
import { OtpField } from "./OtpField";
import { Slider } from "./Slider";
import { Switch } from "./Switch";
import { TextInput } from "./TextInput";
import { Toggle } from "./Toggle";
import { ToggleGroup } from "./ToggleGroup";

afterEach(cleanup);

describe("advanced form controls", () => {
  it("manages a labeled checkbox group", async () => {
    const user = userEvent.setup();
    const onValueChange = vi.fn();
    render(
      <CheckboxGroup
        label="Study focus"
        options={[
          { value: "tactics", label: "Tactics" },
          { value: "endgames", label: "Endgames" },
        ]}
        onValueChange={onValueChange}
      />,
    );

    await user.click(screen.getByText("Tactics"));
    expect(onValueChange).toHaveBeenLastCalledWith(["tactics"]);
  });

  it("groups controls in a native fieldset", () => {
    render(
      <Fieldset legend="Board settings" description="Applied to the analysis board.">
        <input aria-label="Coordinates" />
      </Fieldset>,
    );

    expect(screen.getByRole("group", { name: "Board settings" })).toBeVisible();
    expect(screen.getByText("Applied to the analysis board.")).toBeVisible();
  });

  it("submits Base UI form values", async () => {
    const user = userEvent.setup();
    const onFormSubmit = vi.fn();
    render(
      <Form aria-label="Profile" onFormSubmit={onFormSubmit}>
        <Field label="Display name" name="displayName">
          <TextInput name="displayName" defaultValue="Knight Rider" />
        </Field>
        <button type="submit">Save</button>
      </Form>,
    );

    await user.click(screen.getByRole("button", { name: "Save" }));
    expect(onFormSubmit).toHaveBeenCalledWith(
      { displayName: "Knight Rider" },
      expect.objectContaining({ event: expect.any(Event) }),
    );
  });

  it("increments a number field", async () => {
    const user = userEvent.setup();
    const onValueChange = vi.fn();
    render(<NumberField label="Depth" defaultValue={5} onValueChange={onValueChange} />);

    await user.click(screen.getByRole("button", { name: "Increase value" }));
    expect(onValueChange).toHaveBeenLastCalledWith(6);
  });

  it("renders one accessible OTP slot per requested character", () => {
    render(<OtpField label="Verification code" length={4} />);
    expect(screen.getAllByRole("textbox")).toHaveLength(4);
    expect(screen.getByRole("textbox", { name: "Verification code" })).toBeInTheDocument();
    expect(screen.getByLabelText("Character 4 of 4")).toBeInTheDocument();
  });

  it("renders single and range sliders from the same API", () => {
    const single = render(<Slider label="Volume" defaultValue={40} />);
    expect(screen.getAllByRole("slider")).toHaveLength(1);

    single.unmount();
    render(<Slider label="Evaluation window" defaultValue={[-2, 2]} />);
    expect(screen.getAllByRole("slider")).toHaveLength(2);
  });

  it("toggles a labeled switch", async () => {
    const user = userEvent.setup();
    const onCheckedChange = vi.fn();
    render(<Switch label="Show coordinates" onCheckedChange={onCheckedChange} />);

    await user.click(screen.getByText("Show coordinates"));
    expect(onCheckedChange).toHaveBeenLastCalledWith(true);
  });

  it("supports stand-alone and grouped toggles", async () => {
    const user = userEvent.setup();
    const onPressedChange = vi.fn();
    const onValueChange = vi.fn();
    render(
      <>
        <Toggle onPressedChange={onPressedChange}>Pin line</Toggle>
        <ToggleGroup
          aria-label="Board overlays"
          options={[
            { value: "arrows", label: "Arrows" },
            { value: "squares", label: "Squares" },
          ]}
          multiple
          onValueChange={onValueChange}
        />
      </>,
    );

    await user.click(screen.getByRole("button", { name: "Pin line" }));
    expect(onPressedChange).toHaveBeenLastCalledWith(true);
    await user.click(screen.getByRole("button", { name: "Arrows" }));
    expect(onValueChange).toHaveBeenLastCalledWith(["arrows"]);
  });
});
