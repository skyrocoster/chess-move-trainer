import * as axe from "axe-core";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { useState } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import axeMatchers from "@chialab/vitest-axe";

import { MoveHistory } from "./MoveHistory";
import type { MoveHistoryActivePlyChange, MoveHistoryInput, Ply } from "./moveHistoryTypes";

expect.extend(axeMatchers);

const HISTORY: MoveHistoryInput = {
  initialPosition: { ply: 0 },
  moves: [
    { ply: 1, san: "e4" },
    { ply: 2, san: "e5" },
    { ply: 3, san: "Nf3" },
  ],
};

const here = dirname(fileURLToPath(import.meta.url));
const moduleCss = readFileSync(join(here, "MoveHistory.module.css"), "utf8");

afterEach(cleanup);

function renderHistory(
  activePly: Ply = 0,
  onActivePlyChange: MoveHistoryActivePlyChange = vi.fn<MoveHistoryActivePlyChange>(),
) {
  return render(
    <MoveHistory {...HISTORY} activePly={activePly} onActivePlyChange={onActivePlyChange} />,
  );
}

function ControlledHistory() {
  const [activePly, setActivePly] = useState<Ply>(0);

  return (
    <>
      <MoveHistory {...HISTORY} activePly={activePly} onActivePlyChange={setActivePly} />
      <output data-testid="active-ply">{activePly}</output>
    </>
  );
}

describe("MoveHistory", () => {
  it("renders numbered White and Black columns with one active move", () => {
    renderHistory();

    expect(screen.getByRole("navigation", { name: "Move history" })).toBeVisible();
    expect(screen.getByRole("columnheader", { name: "#" })).toBeVisible();
    expect(screen.getByRole("columnheader", { name: "White" })).toBeVisible();
    expect(screen.getByRole("columnheader", { name: "Black" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Initial position" })).toHaveAttribute(
      "aria-current",
      "step",
    );
    expect(screen.getByRole("button", { name: "White, move 1, e4" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Black, move 1, e5" })).toBeVisible();
    expect(screen.getByRole("button", { name: "White, move 2, Nf3" })).toBeVisible();
    expect(screen.queryByText(/Ply/)).not.toBeInTheDocument();
    expect(
      screen.getAllByRole("button").filter((button) => button.hasAttribute("aria-current")),
    ).toHaveLength(1);
  });

  it("selects a move by click and synchronizes controlled active state", async () => {
    const user = userEvent.setup();
    render(<ControlledHistory />);

    await user.click(screen.getByRole("button", { name: "Black, move 1, e5" }));

    expect(screen.getByTestId("active-ply")).toHaveTextContent("2");
    expect(screen.getByRole("button", { name: "Black, move 1, e5" })).toHaveAttribute(
      "aria-current",
      "step",
    );
    expect(screen.getByRole("button", { name: "Initial position" })).not.toHaveAttribute(
      "aria-current",
    );
  });

  it("selects previous, next, Home, and End through the controlled callback", async () => {
    const user = userEvent.setup();
    const onActivePlyChange = vi.fn<MoveHistoryActivePlyChange>();
    renderHistory(1, onActivePlyChange);
    const active = screen.getByRole("button", { name: "White, move 1, e4" });
    active.focus();

    await user.keyboard("{ArrowRight}");
    await user.keyboard("{ArrowLeft}");
    await user.keyboard("{Home}");
    await user.keyboard("{End}");

    expect(onActivePlyChange.mock.calls.map(([ply]) => ply)).toEqual([2, 0, 0, 3]);
  });

  it("moves focus to the newly controlled active row and preserves focus on the initial row", async () => {
    const { rerender } = renderHistory(0);
    const initial = screen.getByRole("button", { name: "Initial position" });
    initial.focus();

    rerender(
      <MoveHistory
        {...HISTORY}
        activePly={2}
        onActivePlyChange={vi.fn<MoveHistoryActivePlyChange>()}
      />,
    );
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Black, move 1, e5" })).toHaveFocus(),
    );
  });

  it("scrolls the active row into view when it changes", async () => {
    const originalScrollIntoView = HTMLElement.prototype.scrollIntoView;
    const scrollIntoView = vi.fn();
    Object.defineProperty(HTMLElement.prototype, "scrollIntoView", {
      configurable: true,
      value: scrollIntoView,
    });

    try {
      const { rerender } = renderHistory(0);
      expect(scrollIntoView).toHaveBeenCalledWith({ behavior: "auto", block: "nearest" });
      scrollIntoView.mockClear();

      rerender(
        <MoveHistory
          {...HISTORY}
          activePly={3}
          onActivePlyChange={vi.fn<MoveHistoryActivePlyChange>()}
        />,
      );
      await waitFor(() =>
        expect(scrollIntoView).toHaveBeenCalledWith({ behavior: "auto", block: "nearest" }),
      );
    } finally {
      if (originalScrollIntoView) {
        Object.defineProperty(HTMLElement.prototype, "scrollIntoView", {
          configurable: true,
          value: originalScrollIntoView,
        });
      } else {
        delete (HTMLElement.prototype as Partial<HTMLElement>).scrollIntoView;
      }
    }
  });

  it("keeps reduced-motion and forced-colour treatments in the local module", () => {
    expect(moduleCss).toContain("@media (prefers-reduced-motion: reduce)");
    expect(moduleCss).toContain("scroll-behavior: auto;");
    expect(moduleCss).toContain("@media (forced-colors: active)");
    expect(moduleCss).toContain("tbody tr:nth-child(odd)");
    expect(moduleCss).toContain("background: Canvas;");
    expect(moduleCss).toContain("background: Highlight;");
  });

  it("has no axe violations", async () => {
    const { container } = renderHistory();

    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });
});
