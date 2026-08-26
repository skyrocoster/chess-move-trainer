import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { BoardControl } from "./BoardControl";

afterEach(() => cleanup());

describe("BoardControl", () => {
  it("is visible and disabled when no game is loaded", () => {
    render(<BoardControl />);

    const toolbar = screen.getByRole("toolbar", { name: "Board controls" });
    expect(toolbar).toBeVisible();
    expect(within(toolbar).getAllByRole("button")).toHaveLength(2);
    expect(screen.getByText("No game loaded")).toBeVisible();
    const previous = screen.getByRole("button", { name: "Previous" });
    const next = screen.getByRole("button", { name: "Next" });
    expect(previous).toBeDisabled();
    expect(previous).not.toHaveAttribute("aria-disabled");
    expect(previous.querySelector("svg")).toHaveClass("lucide-chevron-left");
    expect(next).toBeDisabled();
    expect(next).not.toHaveAttribute("aria-disabled");
    expect(next.querySelector("svg")).toHaveClass("lucide-chevron-right");
  });

  it("enforces explicit initial and final direction capabilities", () => {
    const { rerender } = render(<BoardControl hasGame canGoPrevious={false} canGoNext />);

    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();

    rerender(<BoardControl hasGame canGoPrevious canGoNext={false} />);
    expect(screen.getByRole("button", { name: "Previous" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
  });

  it("calls one native action for each enabled direction capability", async () => {
    const onPrevious = vi.fn();
    const onNext = vi.fn();
    const user = userEvent.setup();
    render(
      <BoardControl hasGame canGoPrevious canGoNext onPrevious={onPrevious} onNext={onNext} />,
    );

    await user.click(screen.getByRole("button", { name: "Previous" }));
    await user.click(screen.getByRole("button", { name: "Next" }));
    expect(onPrevious).toHaveBeenCalledOnce();
    expect(onNext).toHaveBeenCalledOnce();

    cleanup();
    render(<BoardControl hasGame canGoPrevious={false} canGoNext={false} />);
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
  });

  it("gates captured-game traversal when both direction capabilities are unavailable", () => {
    render(<BoardControl hasGame canGoPrevious={false} canGoNext={false} />);

    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
  });
});
