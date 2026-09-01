import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RepertoireBoardLane } from "./RepertoireBoardLane";

vi.mock("../board-adapter/InteractiveBoardAdapter", () => ({
  InteractiveBoardAdapter: ({ orientation }: { orientation: string }) => (
    <div data-testid="mock-interactive-board" data-orientation={orientation} />
  ),
}));
vi.mock("../viewer/BoardEvalStage", () => ({
  BoardEvalStage: ({
    children,
    orientation,
  }: {
    children: React.ReactNode;
    orientation: string;
  }) => (
    <div data-testid="mock-board-eval-stage" data-orientation={orientation}>
      {children}
    </div>
  ),
}));
vi.mock("../viewer/BoardControl", () => ({
  BoardControl: ({ onFlip }: { onFlip: () => void }) => (
    <button type="button" onClick={onFlip}>
      Flip
    </button>
  ),
}));
vi.mock("../move-history/MoveHistory", () => ({
  MoveHistory: ({ activePly, ariaLabel, ...props }: { activePly: number; ariaLabel: string }) => (
    <nav {...props} aria-label={ariaLabel} data-active-ply={activePly} />
  ),
}));

afterEach(cleanup);

describe("RepertoireBoardLane", () => {
  it("owns the board, controls, and one controlled move history", () => {
    const onFlip = vi.fn();
    render(
      <RepertoireBoardLane
        orientation="black"
        evaluation={{
          state: "neutral",
          value: 50,
          shortValue: "0.00",
          accessibleValue: "No analysis yet; evaluation neutral.",
        }}
        viewKey="view-1"
        board={{
          branchSnapshot: {
            viewKey: "view-1",
            resetToken: 0,
            originFen: "start",
            currentFen: "start",
            originPly: 0,
            moves: [],
            active: false,
          },
          label: "Board",
          notice: "Ready",
          terminal: null,
          lastMove: null,
          promotionPending: null,
          promotionColor: "b",
          promotionSourceElement: null,
          promotionAnchorElement: null,
          showBranchPanel: false,
          onMoveIntent: vi.fn(),
          onPromotionSelect: vi.fn(),
          onPromotionCancel: vi.fn(),
          onUndo: vi.fn(),
          onReset: vi.fn(),
        }}
        controls={{
          hasGame: true,
          canGoPrevious: false,
          canGoNext: true,
          onPrevious: vi.fn(),
          onNext: vi.fn(),
          onFlip,
        }}
        history={{
          initialPosition: { ply: 0 },
          moves: [{ ply: 1, san: "e4" }],
          activePly: 1,
          onActivePlyChange: vi.fn(),
        }}
      />,
    );

    const lane = screen.getByTestId("repertoire-board-lane");
    expect(within(lane).getByTestId("mock-board-eval-stage")).toBeVisible();
    expect(within(lane).getByTestId("mock-interactive-board")).toHaveAttribute(
      "data-orientation",
      "black",
    );
    expect(within(lane).getByRole("button", { name: "Flip" })).toBeVisible();
    expect(within(lane).getAllByRole("navigation")).toHaveLength(1);
    expect(within(lane).getByRole("navigation")).toHaveAttribute("data-active-ply", "1");
    expect(within(lane).getByRole("navigation")).toHaveAttribute(
      "aria-label",
      "Repertoire move history",
    );
    within(lane).getByRole("button", { name: "Flip" }).click();
    expect(onFlip).toHaveBeenCalledOnce();
  });
});
