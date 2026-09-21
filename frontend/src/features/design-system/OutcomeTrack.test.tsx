import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { OutcomeTrack } from "./OutcomeTrack";

afterEach(cleanup);

describe("OutcomeTrack", () => {
  it("renders win/draw/loss shares that fill the track", () => {
    render(
      <OutcomeTrack
        values={{ wins: 7, draws: 2, losses: 3 }}
        accessibleLabel="7 wins, 2 draws, 3 losses"
      />,
    );

    const track = screen.getByRole("img", { name: "7 wins, 2 draws, 3 losses" });
    expect(track).toBeVisible();
    expect(track.children).toHaveLength(3);
  });

  it("omits the unknown segment when unknown is absent so engine WDL is unchanged", () => {
    const { container } = render(
      <OutcomeTrack values={{ wins: 50, draws: 25, losses: 25 }} accessibleLabel="engine WDL" />,
    );

    expect(container.querySelector("[class*='unknown']")).not.toBeInTheDocument();
    expect(screen.getByRole("img", { name: "engine WDL" }).children).toHaveLength(3);
  });

  it("keeps unknown games inside the total with a truthful accessible label", () => {
    const { container } = render(
      <OutcomeTrack
        values={{ wins: 7, draws: 2, losses: 3, unknown: 2 }}
        accessibleLabel="7 wins, 2 draws, 3 losses, 2 unknown"
      />,
    );

    const track = screen.getByRole("img", { name: "7 wins, 2 draws, 3 losses, 2 unknown" });
    expect(track.children).toHaveLength(4);
    const unknownSegment = container.querySelector("[class*='unknown']") as HTMLElement;
    expect(unknownSegment).toBeInTheDocument();
    // 2 of 14 total games keeps the truthful share.
    expect(unknownSegment.style.inlineSize).toContain("14.28");
  });

  it("renders an empty total without negative widths", () => {
    render(<OutcomeTrack values={{ wins: 0, draws: 0, losses: 0 }} accessibleLabel="No games" />);

    const track = screen.getByRole("img", { name: "No games" });
    expect(track).toBeVisible();
    for (const segment of Array.from(track.children)) {
      expect((segment as HTMLElement).style.inlineSize).toBe("0%");
    }
  });
});
