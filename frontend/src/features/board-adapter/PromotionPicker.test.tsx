import * as axe from "axe-core";
import { Chess } from "chess.js";
import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useEffect, useRef, useState } from "react";
import { afterEach, describe, expect, it } from "vitest";
import axeMatchers from "@chialab/vitest-axe";

import { PromotionPicker, type PromotionPiece, usePromotionController } from "./PromotionPicker";

expect.extend(axeMatchers);

const PROMOTION_FEN = "k7/4P3/8/8/8/8/8/4K3 w - - 0 1";

afterEach(cleanup);

function ControllerHarness({
  color = "w",
  presentation = "popover",
}: {
  color?: "w" | "b";
  presentation?: "popover" | "drawer";
}) {
  const chessRef = useRef<Chess | null>(null);
  if (!chessRef.current) {
    chessRef.current = new Chess(PROMOTION_FEN);
  }
  const chess = chessRef.current;
  const sourceRef = useRef<HTMLButtonElement | null>(null);
  const [committed, setCommitted] = useState("");
  const [rejection, setRejection] = useState("");
  const [cancelCount, setCancelCount] = useState(0);
  const [mutationCount, setMutationCount] = useState(0);
  const controller = usePromotionController({
    chess,
    onCommit: ({ move, fen }) => setCommitted(`${move.san}|${fen}`),
    onReject: setRejection,
  });
  const { requestPromotion } = controller;

  useEffect(() => {
    requestPromotion("e7", "e8", sourceRef.current);
  }, [requestPromotion]);

  return (
    <div>
      <button ref={sourceRef} type="button" data-testid="source-pawn">
        Original pawn e7
      </button>
      <button
        type="button"
        data-testid="open-picker"
        onClick={() => controller.requestPromotion("e7", "e8", sourceRef.current)}
      >
        Open picker
      </button>
      <button
        type="button"
        data-testid="request-illegal"
        onClick={() => controller.requestPromotion("e7", "e5", sourceRef.current)}
      >
        Request illegal target
      </button>
      <button
        type="button"
        data-testid="mutate-position"
        onClick={() => {
          chess.move({ from: "e1", to: "f2" });
          setMutationCount((count) => count + 1);
        }}
      >
        Mutate position
      </button>
      <button
        type="button"
        data-testid="select-invalid"
        onClick={() => controller.selectPromotion("x" as PromotionPiece)}
      >
        Select invalid promotion
      </button>
      <output data-testid="pending-state">
        {controller.pending
          ? `${controller.pending.sourceSquare}->${controller.pending.targetSquare}`
          : "none"}
      </output>
      <output data-testid="chess-fen">{chess.fen()}</output>
      <output data-testid="chess-history">{chess.history().join(",")}</output>
      <output data-testid="committed">{committed}</output>
      <output data-testid="rejection">{rejection}</output>
      <output data-testid="cancel-count">{cancelCount}</output>
      <output data-testid="mutation-count">{mutationCount}</output>
      <PromotionPicker
        pending={controller.pending}
        color={color}
        sourceElement={controller.sourceElement}
        presentation={presentation}
        onSelect={controller.selectPromotion}
        onCancel={() => {
          setCancelCount((count) => count + 1);
          controller.cancelPromotion();
        }}
      />
    </div>
  );
}

function ControllerOnlyHarness() {
  const chessRef = useRef<Chess | null>(null);
  if (!chessRef.current) {
    chessRef.current = new Chess(PROMOTION_FEN);
  }
  const chess = chessRef.current;
  const sourceRef = useRef<HTMLButtonElement | null>(null);
  const [rejection, setRejection] = useState("");
  const controller = usePromotionController({ chess, onReject: setRejection });
  const { requestPromotion } = controller;

  useEffect(() => {
    requestPromotion("e7", "e8", sourceRef.current);
  }, [requestPromotion]);

  return (
    <div>
      <button ref={sourceRef} type="button">
        Source pawn
      </button>
      <button
        type="button"
        data-testid="mutate-controller-position"
        onClick={() => chess.move({ from: "e1", to: "f2" })}
      >
        Mutate controller position
      </button>
      <button
        type="button"
        data-testid="select-controller-invalid"
        onClick={() => controller.selectPromotion("x" as PromotionPiece)}
      >
        Select controller invalid
      </button>
      <output data-testid="controller-pending">
        {controller.pending
          ? `${controller.pending.sourceSquare}->${controller.pending.targetSquare}`
          : "none"}
      </output>
      <output data-testid="controller-fen">{chess.fen()}</output>
      <output data-testid="controller-history">{chess.history().join(",")}</output>
      <output data-testid="controller-rejection">{rejection}</output>
    </div>
  );
}

async function openPicker(presentation: "popover" | "drawer" = "popover", color: "w" | "b" = "w") {
  render(<ControllerHarness color={color} presentation={presentation} />);
  return screen.findByRole("dialog", { name: "Choose a promotion piece" });
}

describe("PromotionPicker", () => {
  it.each([
    ["queen", "Q"],
    ["rook", "R"],
    ["bishop", "B"],
    ["knight", "N"],
  ] as const)("commits the selected %s through chess.js", async (name, promotion) => {
    const user = userEvent.setup();
    const dialog = await openPicker();

    await user.click(within(dialog).getByRole("button", { name: `Promote to ${name}` }));

    expect(screen.getByTestId("pending-state")).toHaveTextContent("none");
    expect(screen.getByTestId("committed")).toHaveTextContent(`e8=${promotion}`);
    expect(screen.getByTestId("chess-history")).toHaveTextContent(`e8=${promotion}`);
    const promotionPiece = { queen: "q", rook: "r", bishop: "b", knight: "n" }[name];
    const expectedMove = new Chess(PROMOTION_FEN).move({
      from: "e7",
      to: "e8",
      promotion: promotionPiece,
    });
    expect(screen.getByTestId("chess-fen")).toHaveTextContent(expectedMove.after);
    expect(screen.getByTestId("committed")).toHaveTextContent(
      `${expectedMove.san}|${expectedMove.after}`,
    );
  });

  it("keeps the pawn and state unchanged while a promotion is pending", async () => {
    const dialog = await openPicker();

    expect(within(dialog).getByRole("group", { name: "Promotion pieces" })).toBeInTheDocument();
    expect(screen.getByTestId("pending-state")).toHaveTextContent("e7->e8");
    expect(screen.getByTestId("chess-fen")).toHaveTextContent(PROMOTION_FEN);
    expect(screen.getByTestId("chess-history")).toHaveTextContent("");
    expect(screen.getByTestId("source-pawn")).toBeInTheDocument();
  });

  it("uses board-consistent glyphs for a black promotion", async () => {
    const dialog = await openPicker("popover", "b");

    expect(within(dialog).getByRole("button", { name: "Promote to queen" })).toHaveTextContent("♛");
    expect(within(dialog).getByRole("button", { name: "Promote to rook" })).toHaveTextContent("♜");
    expect(within(dialog).getByRole("button", { name: "Promote to bishop" })).toHaveTextContent(
      "♝",
    );
    expect(within(dialog).getByRole("button", { name: "Promote to knight" })).toHaveTextContent(
      "♞",
    );
  });

  it("rejects an illegal target without opening or mutating chess.js", async () => {
    const user = userEvent.setup();
    await openPicker();
    await user.keyboard("{Escape}");
    await user.click(screen.getByTestId("request-illegal"));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByTestId("pending-state")).toHaveTextContent("none");
    expect(screen.getByTestId("chess-fen")).toHaveTextContent(PROMOTION_FEN);
    expect(screen.getByTestId("chess-history")).toHaveTextContent("");
  });

  it("rejects a stale source position without adding a promotion move", async () => {
    const user = userEvent.setup();
    render(<ControllerOnlyHarness />);
    await user.click(screen.getByTestId("mutate-controller-position"));
    await user.click(screen.getByTestId("select-controller-invalid"));

    expect(screen.getByTestId("controller-pending")).toHaveTextContent("none");
    expect(screen.getByTestId("controller-rejection")).toHaveTextContent("stale");
    expect(screen.getByTestId("controller-history")).toHaveTextContent("Kf2");
    expect(screen.getByTestId("controller-fen")).not.toHaveTextContent("e8=Q");
  });

  it("rejects an invalid promotion value without mutating chess.js", async () => {
    const user = userEvent.setup();
    render(<ControllerOnlyHarness />);
    await user.click(screen.getByTestId("select-controller-invalid"));

    expect(screen.getByTestId("controller-pending")).toHaveTextContent("none");
    expect(screen.getByTestId("controller-rejection")).toHaveTextContent("illegal");
    expect(screen.getByTestId("controller-fen")).toHaveTextContent(PROMOTION_FEN);
    expect(screen.getByTestId("controller-history")).toHaveTextContent("");
  });

  it.each([
    ["Escape", async (user: ReturnType<typeof userEvent.setup>) => user.keyboard("{Escape}")],
    [
      "popover outside press",
      async (user: ReturnType<typeof userEvent.setup>) =>
        user.click(screen.getByTestId("promotion-popover-backdrop")),
    ],
  ] as const)("cancels through %s and restores source focus", async (_name, dismiss) => {
    const user = userEvent.setup();
    await openPicker();
    await dismiss(user);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByTestId("cancel-count")).toHaveTextContent("1");
    expect(screen.getByTestId("source-pawn")).toHaveFocus();
    expect(screen.getByTestId("chess-fen")).toHaveTextContent(PROMOTION_FEN);
    expect(screen.getByTestId("chess-history")).toHaveTextContent("");
  });

  it("cancels through the drawer backdrop and restores source focus", async () => {
    const user = userEvent.setup();
    await openPicker("drawer");
    await user.click(screen.getByTestId("promotion-drawer-backdrop"));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByTestId("cancel-count")).toHaveTextContent("1");
    expect(screen.getByTestId("source-pawn")).toHaveFocus();
    expect(screen.getByTestId("chess-fen")).toHaveTextContent(PROMOTION_FEN);
  });

  it("supports keyboard selection with clear accessible names and a live announcement", async () => {
    const user = userEvent.setup();
    const dialog = await openPicker();

    expect(within(dialog).getByRole("heading", { name: "Choose a promotion piece" })).toBeVisible();
    expect(within(dialog).getByRole("status")).toHaveTextContent("White pawn from e7 to e8");
    expect(within(dialog).getByRole("button", { name: "Promote to queen" })).toHaveFocus();

    await user.tab();
    expect(within(dialog).getByRole("button", { name: "Promote to rook" })).toHaveFocus();
    await user.keyboard("{Enter}");
    expect(screen.getByTestId("committed")).toHaveTextContent("e8=R");
  });

  it("passes a focused axe check for both presentation primitives", async () => {
    const popoverDialog = await openPicker();
    expect(await axe.run(popoverDialog)).toHaveNoViolations();
    cleanup();

    const drawerDialog = await openPicker("drawer");
    expect(await axe.run(drawerDialog)).toHaveNoViolations();
  });
});
