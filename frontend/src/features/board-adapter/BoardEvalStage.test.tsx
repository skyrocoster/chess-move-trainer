import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useState } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { BoardEvalStage } from "./BoardEvalStage";

type ResizeObserverInstance = {
  observe: ReturnType<typeof vi.fn>;
  disconnect: ReturnType<typeof vi.fn>;
  trigger: () => void;
};

const resizeObservers: ResizeObserverInstance[] = [];

class ResizeObserverMock {
  private readonly callback: ResizeObserverCallback;
  readonly observe = vi.fn();
  readonly disconnect = vi.fn();

  constructor(callback: ResizeObserverCallback) {
    this.callback = callback;
    resizeObservers.push(this as unknown as ResizeObserverInstance);
  }

  trigger() {
    this.callback([], this as unknown as ResizeObserver);
  }
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  resizeObservers.length = 0;
});

beforeEach(() => {
  vi.stubGlobal("ResizeObserver", ResizeObserverMock);
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockImplementation(function (
    this: HTMLElement,
  ) {
    if (this.matches("[data-board-visual]")) {
      const height = Number(this.getAttribute("data-height"));
      return { height, width: height, top: 0, right: height, bottom: height, left: 0 } as DOMRect;
    }
    return { height: 0, width: 0, top: 0, right: 0, bottom: 0, left: 0 } as DOMRect;
  });
});

function display() {
  return {
    state: "neutral" as const,
    value: 50,
    shortValue: "0.00",
    accessibleValue: "No analysis yet; evaluation neutral.",
  };
}

function BoardFixture() {
  const [height, setHeight] = useState(240);
  const [version, setVersion] = useState("first");

  return (
    <>
      <BoardEvalStage orientation="white" display={display()}>
        <div
          key={version}
          data-board-visual
          data-height={height}
          data-testid={`board-${version}`}
        />
      </BoardEvalStage>
      <button type="button" onClick={() => setHeight(300)}>
        Resize board
      </button>
      <button type="button" onClick={() => setVersion("replacement")}>
        Replace board
      </button>
    </>
  );
}

describe("BoardEvalStage", () => {
  it("measures the marked visual, applies its border-box height, observes resize, and cleans up", async () => {
    const { unmount } = render(<BoardFixture />);
    const railShell = screen.getByTestId("board-eval-rail-shell");
    expect(screen.getByTestId("board-eval-stage")).toHaveAttribute("data-board-staged", "true");

    await waitFor(() => expect(railShell.style.blockSize).toBe("240px"));
    expect(resizeObservers).toHaveLength(1);
    expect(resizeObservers[0].observe).toHaveBeenCalledWith(screen.getByTestId("board-first"));

    fireEvent.click(screen.getByRole("button", { name: "Resize board" }));
    resizeObservers[0].trigger();
    await waitFor(() => expect(railShell.style.blockSize).toBe("300px"));

    unmount();
    expect(resizeObservers[0].disconnect).toHaveBeenCalledOnce();
  });

  it("rebinds measurement when React replaces the actual board visual", async () => {
    render(<BoardFixture />);
    const railShell = screen.getByTestId("board-eval-rail-shell");
    await waitFor(() => expect(railShell.style.blockSize).toBe("240px"));

    fireEvent.click(screen.getByRole("button", { name: "Replace board" }));
    await waitFor(() => expect(railShell.style.blockSize).toBe("240px"));
    expect(screen.getByTestId("board-replacement")).toBeInTheDocument();
    expect(resizeObservers).toHaveLength(2);
    expect(resizeObservers[0].disconnect).toHaveBeenCalledOnce();
    expect(resizeObservers[1].observe).toHaveBeenCalledWith(
      screen.getByTestId("board-replacement"),
    );
  });
});
