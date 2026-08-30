import { cleanup, render, screen } from "@testing-library/react";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import { afterEach, describe, expect, it } from "vitest";

import { PositionContext } from "./PositionContext";
import type { PositionContextResponse } from "./positionContextApi";

expect.extend(matchers);

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function context(overrides: Partial<PositionContextResponse> = {}): PositionContextResponse {
  return {
    fen: FEN,
    overall_exists: true,
    white_count: 2,
    black_count: 1,
    white_total: 3,
    black_total: 2,
    ...overrides,
  };
}

afterEach(() => cleanup());

describe("PositionContext", () => {
  it("shows the accepted White and Black distinct-game scopes", () => {
    render(<PositionContext context={context()} />);

    expect(screen.getByText("Seen in 2 games as White", { exact: true })).toBeVisible();
    expect(screen.getByText("Seen in 1 games as Black", { exact: true })).toBeVisible();
    expect(screen.getByRole("group", { name: "Position recurrence" })).toBeVisible();
  });

  it("shows Never seen for zero counts and absent overall positions", () => {
    const { rerender } = render(
      <PositionContext context={context({ white_count: 0, black_count: 0 })} />,
    );

    expect(screen.getByText("Never seen as White", { exact: true })).toBeVisible();
    expect(screen.getByText("Never seen as Black", { exact: true })).toBeVisible();
    expect(screen.queryByText(/Seen in/)).not.toBeInTheDocument();

    rerender(
      <PositionContext
        context={context({ overall_exists: false, white_count: 4, black_count: 3 })}
      />,
    );
    expect(screen.getByText("Never seen as White", { exact: true })).toBeVisible();
    expect(screen.getByText("Never seen as Black", { exact: true })).toBeVisible();
  });

  it("renders no loading or error treatment without a successful context", () => {
    const { container } = render(<PositionContext context={null} />);

    expect(container).toBeEmptyDOMElement();
    expect(screen.queryByText(/Position context/i)).not.toBeInTheDocument();
  });

  it("has no focused accessibility violations", async () => {
    const { container } = render(<PositionContext context={context()} />);

    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });
});
