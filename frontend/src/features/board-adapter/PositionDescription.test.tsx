import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { PositionDescription } from "./PositionDescription";
import { createPositionModel } from "./positionDescriptionModel";

const RICH_FEN = "rn1qk2r/1bp1bpp1/pp1ppn1p/8/4PB2/2NP1NP1/PPPQ1PBP/R3K2R b KQkq e3 0 8";

afterEach(() => {
  cleanup();
});

describe("PositionDescription", () => {
  it("renders the shared rich summary with its stable presentation markers", () => {
    const { container } = render(
      <PositionDescription model={createPositionModel(RICH_FEN, "black")} />,
    );

    expect(screen.getByRole("button", { name: "Position description" })).toHaveAttribute(
      "aria-expanded",
      "false",
    );

    fireEvent.click(screen.getByRole("button", { name: "Position description" }));

    const summary = container.querySelector("[data-position-summary]");
    expect(summary).toBeInTheDocument();
    expect(summary).toHaveTextContent("OrientationBlack at the bottom");
    expect(summary).toHaveTextContent("Side to moveBlack");
    expect(summary).toHaveTextContent("Castling · White K + Q");
    expect(summary).toHaveTextContent("Castling · Black K + Q");
    expect(summary).toHaveTextContent("En-passant target e3");
    expect(summary?.querySelectorAll('[data-position-side="w"]')).toHaveLength(1);
    expect(summary?.querySelectorAll('[data-position-side="b"]')).toHaveLength(1);
    expect(summary?.querySelectorAll('[data-position-square="e1"]')).toHaveLength(1);
    expect(summary?.querySelectorAll("[data-position-fact]")).toHaveLength(5);
  });
});
