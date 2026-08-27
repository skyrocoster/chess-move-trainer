import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import { afterEach, describe, expect, it } from "vitest";

import { EvalBar, type EvalBarProps } from "./EvalBar";

expect.extend(matchers);

afterEach(() => cleanup());

type ExpectedDisplay = Pick<EvalBarProps, "orientation" | "state" | "value" | "accessibleValue">;

function expectDisplay(expected: ExpectedDisplay) {
  const meter = screen.getByRole("meter", { name: "Evaluation" });

  expect(meter).toHaveAttribute("data-state", expected.state);
  expect(meter).toHaveAttribute("data-orientation", expected.orientation);
  expect(meter).toHaveAttribute("aria-valuemin", "0");
  expect(meter).toHaveAttribute("aria-valuemax", "100");
  expect(meter).toHaveAttribute("aria-valuenow", String(expected.value));
  expect(meter).toHaveAttribute("aria-valuetext", expected.accessibleValue);
  expect(screen.getByText(expected.accessibleValue, { exact: true })).toBeVisible();

  return meter;
}

describe("EvalBar", () => {
  it("always reserves a neutral accessible meter before analysis", async () => {
    const user = userEvent.setup();
    const { container } = render(
      <EvalBar
        orientation="white"
        state="neutral"
        value={50}
        accessibleValue="No analysis yet; evaluation neutral."
      />,
    );
    const meter = expectDisplay({
      orientation: "white",
      state: "neutral",
      value: 50,
      accessibleValue: "No analysis yet; evaluation neutral.",
    });

    await user.tab();
    expect(document.activeElement).not.toBe(meter);
    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });

  it.each([
    ["unavailable", "Evaluation unavailable; evaluation neutral."],
    ["stale without a retained candidate", "No analysis yet; evaluation neutral."],
    ["failed without a retained candidate", "Analysis failed; evaluation neutral."],
  ] as const)("preserves the %s neutral fallback", (_sourceState, accessibleValue) => {
    render(
      <EvalBar orientation="white" state="neutral" value={50} accessibleValue={accessibleValue} />,
    );
    expectDisplay({ orientation: "white", state: "neutral", value: 50, accessibleValue });
  });

  it.each([
    ["queued", "white", "Analysis queued; evaluation pending."],
    ["running", "black", "Analysis running; evaluation pending."],
  ] as const)(
    "shows the %s pending state without inventing an evaluation",
    (_queueState, orientation, accessibleValue) => {
      render(
        <EvalBar
          orientation={orientation}
          state="pending"
          value={50}
          accessibleValue={accessibleValue}
        />,
      );
      expectDisplay({ orientation, state: "pending", value: 50, accessibleValue });
    },
  );

  it.each([
    ["CP", 51.7, "best-line evaluation +0.34."],
    ["negative CP", 48.3, "best-line evaluation -0.34."],
    ["positive mate", 100, "best-line evaluation +M3."],
    ["negative mate", 0, "best-line evaluation -M2."],
    ["mate given", 100, "best-line evaluation +M."],
  ] as const)("shows the completed %s display value", (_scoreKind, value, accessibleValue) => {
    render(
      <EvalBar
        orientation="black"
        state="best-line"
        value={value}
        accessibleValue={accessibleValue}
      />,
    );
    expectDisplay({ orientation: "black", state: "best-line", value, accessibleValue });
  });

  it.each([
    ["stale", "Stale best-line evaluation +0.34."],
    ["failed", "Stale best-line evaluation +0.34."],
  ] as const)("retains the candidate display for %s analysis", (_sourceState, accessibleValue) => {
    render(
      <EvalBar
        orientation="white"
        state="best-line"
        value={51.7}
        accessibleValue={accessibleValue}
      />,
    );
    expectDisplay({ orientation: "white", state: "best-line", value: 51.7, accessibleValue });
  });

  it.each([
    ["minimum", -25, 0],
    ["maximum", 125, 100],
  ] as const)(
    "keeps the controlled meter's %s value within its range",
    (_bound, value, clampedValue) => {
      render(
        <EvalBar
          orientation="white"
          state="best-line"
          value={value}
          accessibleValue="best-line evaluation at a controlled range boundary."
        />,
      );
      const meter = expectDisplay({
        orientation: "white",
        state: "best-line",
        value: clampedValue,
        accessibleValue: "best-line evaluation at a controlled range boundary.",
      });

      expect(meter).toHaveAttribute("aria-valuenow", String(clampedValue));
    },
  );

  it("has no focused accessibility violations for a pending display", async () => {
    const { container } = render(
      <EvalBar
        orientation="black"
        state="pending"
        value={50}
        accessibleValue="Analysis running; evaluation pending."
      />,
    );

    expectDisplay({
      orientation: "black",
      state: "pending",
      value: 50,
      accessibleValue: "Analysis running; evaluation pending.",
    });
    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });
});
