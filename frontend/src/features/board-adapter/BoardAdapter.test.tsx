import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import type { ComponentProps } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { BoardAdapter, STARTING_FEN } from "./BoardAdapter";

const { shouldThrow } = vi.hoisted(() => ({ shouldThrow: { value: false } }));

vi.mock("react-chessboard", async () => {
  const actual = await vi.importActual<typeof import("react-chessboard")>("react-chessboard");

  return {
    ...actual,
    Chessboard: (props: Parameters<typeof actual.Chessboard>[0]) => {
      if (shouldThrow.value) {
        throw new Error("Test-only react-chessboard render failure");
      }

      return <actual.Chessboard {...props} />;
    },
  };
});

expect.extend(matchers);

const RICH_FEN = "rn1qk2r/1bp1bpp1/pp1ppn1p/8/4PB2/2NP1NP1/PPPQ1PBP/R3K2R b KQkq e3 0 8";

afterEach(() => {
  cleanup();
  shouldThrow.value = false;
  vi.restoreAllMocks();
});

beforeEach(() => {
  shouldThrow.value = false;
});

function renderStartingPosition(props: Partial<ComponentProps<typeof BoardAdapter>> = {}) {
  return render(<BoardAdapter fen={STARTING_FEN} label="Starting position" {...props} />);
}

describe("BoardAdapter", () => {
  it("renders the default white, coordinate-visible static graphic", () => {
    const { container } = renderStartingPosition();
    const graphic = screen.getByRole("img", { name: "Starting position" });

    expect(graphic).toHaveAttribute("data-board-visual");
    expect(graphic).toHaveAttribute("aria-describedby");
    expect(graphic.querySelectorAll("[data-square] span").length).toBeGreaterThan(0);
    expect(graphic.querySelectorAll('[role="button"]')).toHaveLength(0);
    expect(graphic.querySelectorAll('[aria-roledescription="draggable"]')).toHaveLength(0);
    expect(graphic.querySelectorAll("[tabindex]")).toHaveLength(0);
    expect(container.querySelectorAll('[role="button"]')).toHaveLength(0);
  });

  it("keeps the rich fixture state in the generated description", () => {
    renderStartingPosition({ fen: RICH_FEN, label: "Rich position" });
    const graphic = screen.getByRole("img", { name: "Rich position" });
    const description = document.getElementById(graphic.getAttribute("aria-describedby") ?? "");

    expect(description).toHaveTextContent(
      "Orientation: White at the bottom. Side to move: Black. Occupied squares in stable FEN order: black rook at a8, black knight at b8, black queen at d8, black king at e8, black rook at h8, black bishop at b7, black pawn at c7, black bishop at e7, black pawn at f7, black pawn at g7, black pawn at a6, black pawn at b6, black pawn at d6, black pawn at e6, black knight at f6, black pawn at h6, white pawn at e4, white bishop at f4, white knight at c3, white pawn at d3, white knight at f3, white pawn at g3, white pawn at a2, white pawn at b2, white pawn at c2, white queen at d2, white pawn at f2, white bishop at g2, white pawn at h2, white rook at a1, white king at e1, white rook at h1.",
    );
    expect(description).toHaveTextContent(
      "Castling rights: White may castle kingside and queenside; Black may castle kingside and queenside. En-passant target: e3. Halfmove clock: 0. Fullmove number: 8.",
    );
  });

  it("supports Black orientation without changing inventory order", () => {
    renderStartingPosition({ orientation: "black", label: "Black-side position" });
    const graphic = screen.getByRole("img", { name: "Black-side position" });
    const description = document.getElementById(graphic.getAttribute("aria-describedby") ?? "");

    expect(description).toHaveTextContent("Orientation: Black at the bottom.");
    expect(description?.textContent?.indexOf("black rook at a8")).toBeLessThan(
      description?.textContent?.indexOf("white rook at a1") ?? -1,
    );
  });

  it("supports hidden coordinates and bounded sizing", () => {
    const { container } = renderStartingPosition({ showCoordinates: false });
    const graphic = screen.getByRole("img", { name: "Starting position" });

    expect(graphic.querySelectorAll("[data-square] span")).toHaveLength(0);
    expect(container.querySelector('[class*="boardGraphic"]')).toBeInTheDocument();
    expect(container.querySelector('[class*="adapter"]')).toBeInTheDocument();
  });

  it("updates controlled presentation props while preserving its description association", () => {
    const { rerender } = renderStartingPosition({ label: "Controlled position" });
    const initialGraphic = screen.getByRole("img", { name: "Controlled position" });
    const descriptionId = initialGraphic.getAttribute("aria-describedby");

    expect(descriptionId).toBeTruthy();
    expect(document.getElementById(descriptionId ?? "")).toHaveTextContent(
      "Orientation: White at the bottom. Side to move: White.",
    );

    rerender(<BoardAdapter fen={STARTING_FEN} label="Updated controlled position" />);

    const updatedGraphic = screen.getByRole("img", { name: "Updated controlled position" });
    expect(updatedGraphic).toHaveAttribute("aria-describedby", descriptionId);
    expect(document.getElementById(descriptionId ?? "")).toHaveTextContent(
      "Orientation: White at the bottom. Side to move: White.",
    );
  });

  it("gives each static instance a unique matching description id", () => {
    render(
      <>
        <BoardAdapter fen={STARTING_FEN} label="First position" />
        <BoardAdapter fen={RICH_FEN} label="Second position" />
      </>,
    );

    const firstGraphic = screen.getByRole("img", { name: "First position" });
    const secondGraphic = screen.getByRole("img", { name: "Second position" });
    const firstDescriptionId = firstGraphic.getAttribute("aria-describedby");
    const secondDescriptionId = secondGraphic.getAttribute("aria-describedby");

    expect(firstDescriptionId).toBeTruthy();
    expect(secondDescriptionId).toBeTruthy();
    expect(firstDescriptionId).not.toBe(secondDescriptionId);
    expect(document.getElementById(firstDescriptionId ?? "")).toHaveTextContent(
      "Side to move: White.",
    );
    expect(document.getElementById(secondDescriptionId ?? "")).toHaveTextContent(
      "Side to move: Black.",
    );
  });

  it("keeps the assistive description while the disclosure is collapsed or expanded", () => {
    renderStartingPosition();
    const graphic = screen.getByRole("img", { name: "Starting position" });
    const descriptionId = graphic.getAttribute("aria-describedby");
    const trigger = screen.getByRole("button", { name: "Position description" });

    expect(trigger).toHaveAttribute("aria-expanded", "false");
    expect(descriptionId).toBeTruthy();
    fireEvent.click(trigger);
    expect(trigger).toHaveAttribute("aria-expanded", "true");
    expect(graphic).toHaveAttribute("aria-describedby", descriptionId);
  });

  it("uses the shared unavailable presentation for invalid and unrenderable positions", () => {
    const invalid = render(<BoardAdapter fen={` ${STARTING_FEN}`} label="Invalid position" />);
    expect(screen.getByText("Position unavailable")).toBeVisible();
    expect(invalid.container.querySelector('[role="img"]')).not.toBeInTheDocument();
    cleanup();

    shouldThrow.value = true;
    const errorSpy = vi.spyOn(console, "error").mockImplementation(() => undefined);
    const failure = render(<BoardAdapter fen={STARTING_FEN} label="Failure position" />);
    expect(screen.getByText("Position unavailable")).toBeVisible();
    expect(failure.container.querySelector('[role="img"]')).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /retry/i })).not.toBeInTheDocument();
    errorSpy.mockRestore();
  });

  it("has no focused axe violations at the adapter boundary", async () => {
    const { container } = renderStartingPosition();
    const results = await axe.run({ include: [container] });

    expect(results).toHaveNoViolations();
  });
});
