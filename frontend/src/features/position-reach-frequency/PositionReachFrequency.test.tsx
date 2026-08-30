import { cleanup, render, screen } from "@testing-library/react";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import { afterEach, describe, expect, it } from "vitest";

import type { PositionContextResponse } from "../viewer/positionContextApi";
import { PositionReachFrequency } from "./PositionReachFrequency";

expect.extend(matchers);

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function context(overrides: Partial<PositionContextResponse> = {}): PositionContextResponse {
  return {
    fen: FEN,
    overall_exists: true,
    white_count: 2,
    black_count: 3,
    white_total: 5,
    black_total: 7,
    ...overrides,
  };
}

afterEach(() => cleanup());

describe("PositionReachFrequency", () => {
  it("renders the selected colour's exact fraction, percentage, and proportional meter", () => {
    render(<PositionReachFrequency context={context()} selectedColor="white" />);

    expect(screen.getByRole("heading", { name: "Position reach frequency" })).toBeVisible();
    expect(screen.getByText("White repertoire colour", { exact: true })).toBeVisible();
    expect(screen.getByText("2 / 5 games", { exact: true })).toBeVisible();
    expect(screen.getByText("40%", { exact: true })).toBeVisible();

    const meter = screen.getByRole("meter", { name: "Position reach frequency as White" });
    expect(meter).toHaveAttribute("aria-valuenow", "40");
    expect(meter).toHaveAttribute("aria-valuemin", "0");
    expect(meter).toHaveAttribute("aria-valuemax", "100");
    expect(meter).toHaveAttribute("aria-valuetext", "2 of 5 games as White; 40% reached.");
    expect(screen.getByTestId("position-reach-indicator")).toHaveStyle({ inlineSize: "40%" });
  });

  it("renders Black values when Black is explicitly selected", () => {
    render(<PositionReachFrequency context={context()} selectedColor="black" />);

    expect(screen.getByText("Black repertoire colour", { exact: true })).toBeVisible();
    expect(screen.getByText("3 / 7 games", { exact: true })).toBeVisible();
    expect(screen.getByText("42.9%", { exact: true })).toBeVisible();
    expect(
      screen.getByRole("meter", { name: "Position reach frequency as Black" }),
    ).toHaveAttribute("aria-valuetext", "3 of 7 games as Black; 42.9% reached.");
  });

  it("renders an existing zero count as an available zero meter", () => {
    render(
      <PositionReachFrequency
        context={context({ white_count: 0 })}
        selectedColor="white"
      />,
    );

    expect(screen.getByTestId("position-reach-indicator")).toBeInTheDocument();
    expect(screen.getByText("0 / 5 games", { exact: true })).toBeVisible();
    expect(screen.getByText("0%", { exact: true })).toBeVisible();
    expect(screen.getByRole("meter")).toHaveAttribute(
      "aria-valuetext",
      "0 of 5 games as White; 0% reached.",
    );
  });

  it("renders absent and unavailable states without a frequency meter", () => {
    const { rerender } = render(
      <PositionReachFrequency
        context={context({ overall_exists: false, white_count: 0, black_count: 0 })}
        selectedColor="white"
      />,
    );
    expect(screen.getByText("This position is not present in the accepted game data for White.")).toBeVisible();
    expect(screen.queryByRole("meter")).not.toBeInTheDocument();
    expect(screen.queryByText(/0%|0 \/ /)).not.toBeInTheDocument();

    rerender(<PositionReachFrequency context={null} selectedColor="white" />);
    expect(screen.getByText("Position reach data is unavailable.")).toBeVisible();
    expect(screen.queryByRole("meter")).not.toBeInTheDocument();
  });

  it("remains accessible inside a constrained-width container", async () => {
    const { container } = render(
      <div style={{ inlineSize: "160px" }}>
        <PositionReachFrequency context={context()} selectedColor="white" />
      </div>,
    );

    expect(screen.getByRole("meter", { name: "Position reach frequency as White" })).toBeVisible();
    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });
});
