import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import userEvent from "@testing-library/user-event";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it, vi } from "vitest";

import type {
  MoveResponseDistributionClient,
  MoveResponseDistributionResponse,
} from "./moveResponseDistributionApi";
import { MoveResponseDistribution } from "./MoveResponseDistribution";

expect.extend(matchers);

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const here = dirname(fileURLToPath(import.meta.url));
const rawStyles = readFileSync(join(here, "MoveResponseDistribution.module.css"), "utf8");

function availableData(
  overrides: Partial<MoveResponseDistributionResponse> = {},
): MoveResponseDistributionResponse {
  return {
    fen: FEN,
    color: "white",
    matching_game_count: 4,
    outgoing_occurrence_count: 13,
    replies: [
      { rank: 1, child_uci: "e2e4", san: "e4", occurrence_count: 4 },
      { rank: 2, child_uci: "d2d4", san: "d4", occurrence_count: 3 },
      { rank: 3, child_uci: "c2c4", san: "c4", occurrence_count: 2 },
      { rank: 4, child_uci: "g1f3", san: "Nf3", occurrence_count: 1 },
      { rank: 5, child_uci: "c2c3", san: "c3", occurrence_count: 1 },
      { rank: 6, child_uci: "b2b3", san: "b3", occurrence_count: 1 },
      { rank: 7, child_uci: "f2f4", san: "f4", occurrence_count: 1 },
    ],
    ...overrides,
  };
}

function clientFor(data: MoveResponseDistributionResponse): MoveResponseDistributionClient {
  return vi.fn().mockResolvedValue({ status: "success", data });
}

// Shared chart-label geometry for the label-layout tests below. Widths are
// estimates, only good enough to prove labels stay inside the fixed 240x240
// chart frame and do not collide.
const CHART_FRAME_SIZE = 240;
const ESTIMATED_CHAR_WIDTH = 6.2;
const LABEL_HALF_HEIGHT = 5.5;

type ChartLabel = {
  text: string;
  x: number;
  y: number;
  anchor: string;
  left: number;
  right: number;
  top: number;
  bottom: number;
};

function chartLabels(svg: SVGSVGElement): ChartLabel[] {
  return Array.from(svg.querySelectorAll("text")).map((text) => {
    const x = Number(text.getAttribute("x"));
    const y = Number(text.getAttribute("y"));
    const anchor = text.getAttribute("text-anchor") ?? "start";
    const width = (text.textContent ?? "").length * ESTIMATED_CHAR_WIDTH;
    return {
      text: text.textContent ?? "",
      x,
      y,
      anchor,
      left: anchor === "start" ? x : x - width,
      right: anchor === "start" ? x + width : x,
      top: y - LABEL_HALF_HEIGHT,
      bottom: y + LABEL_HALF_HEIGHT,
    };
  });
}

function labelsOverlap(a: ChartLabel, b: ChartLabel): boolean {
  return a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
}

function segmentHitsBox(
  leader: { x1: number; y1: number; x2: number; y2: number },
  box: { left: number; right: number; top: number; bottom: number },
): boolean {
  let t0 = 0;
  let t1 = 1;
  const dx = leader.x2 - leader.x1;
  const dy = leader.y2 - leader.y1;
  const p = [-dx, dx, -dy, dy];
  const q = [
    leader.x1 - box.left,
    box.right - leader.x1,
    leader.y1 - box.top,
    box.bottom - leader.y1,
  ];
  for (let index = 0; index < 4; index += 1) {
    if (p[index] === 0) {
      if (q[index]! < 0) return false;
    } else {
      const r = q[index]! / p[index]!;
      if (p[index]! < 0) {
        if (r > t1) return false;
        if (r > t0) t0 = r;
      } else {
        if (r < t0) return false;
        if (r < t1) t1 = r;
      }
    }
  }
  return true;
}

afterEach(() => cleanup());

describe("MoveResponseDistribution", () => {
  it("keeps the standalone card surface by default and marks embedded mode as opt-in", () => {
    const standalone = render(
      <MoveResponseDistribution
        fen={FEN}
        color="white"
        client={clientFor(availableData())}
        onMoveSelect={vi.fn()}
      />,
    );
    const standalonePanel = screen.getByTestId("move-response-distribution");
    expect(standalonePanel).not.toHaveAttribute("data-embedded");
    standalone.unmount();

    render(
      <MoveResponseDistribution
        embedded
        fen={FEN}
        color="white"
        client={clientFor(availableData())}
        onMoveSelect={vi.fn()}
      />,
    );
    expect(screen.getByTestId("move-response-distribution")).toHaveAttribute(
      "data-embedded",
      "true",
    );

    const standaloneRule = rawStyles.match(/\.panel\s*\{[^}]*\}/)?.[0];
    expect(standaloneRule).toContain("border: 1px solid var(--md-sys-color-outline-variant);");
    expect(standaloneRule).toContain("border-radius: var(--cmt-radius-default);");
    const embeddedRule = rawStyles.match(/\.panel\.embedded\s*\{[^}]*\}/)?.[0];
    expect(embeddedRule).toContain("border: 0;");
    expect(embeddedRule).toContain("border-radius: 0;");
    expect(embeddedRule).toContain("background: transparent;");
    expect(embeddedRule).toContain("box-shadow: none;");
  });

  it("renders the available chart/list with occurrence semantics and no opening or overlap copy", async () => {
    render(
      <MoveResponseDistribution
        fen={FEN}
        color="white"
        client={clientFor(availableData())}
        onMoveSelect={vi.fn()}
      />,
    );

    await waitFor(() =>
      expect(screen.getByTestId("move-response-distribution")).toHaveAttribute(
        "data-state",
        "available",
      ),
    );
    expect(screen.getByRole("heading", { name: "Move response distribution" })).toBeVisible();
    expect(screen.getByText("White repertoire colour", { exact: true })).toBeVisible();
    expect(screen.getByRole("img")).toBeVisible();
    expect(screen.getByRole("button", { name: /e4, 4 occurrences, 30.8%/ })).toBeVisible();
    expect(screen.getByRole("button", { name: /d4, 3 occurrences, 23.1%/ })).toBeVisible();
    expect(screen.queryByText("Queen's Pawn Game")).not.toBeInTheDocument();
    expect(
      screen.queryByText(/one game may appear in more than one reply/),
    ).not.toBeInTheDocument();
    expect(
      screen.getByText(/outgoing move occurrences observed in 4 matching White/),
    ).toBeVisible();
    expect(
      screen.getByText(/Pie chart of outgoing moves by recorded occurrences/),
    ).toBeInTheDocument();
  });

  it("uses the same UCI selection callback for chart sectors and text controls", async () => {
    const onMoveSelect = vi.fn();
    const { container } = render(
      <MoveResponseDistribution
        fen={FEN}
        color="white"
        client={clientFor(availableData())}
        onMoveSelect={onMoveSelect}
      />,
    );
    await waitFor(() => expect(container.querySelectorAll(".recharts-sector").length).toBe(6));

    await userEvent.click(screen.getByRole("button", { name: /e4, 4 occurrences/ }));
    expect(onMoveSelect).toHaveBeenLastCalledWith("e2e4");
    onMoveSelect.mockClear();

    const sectors = container.querySelectorAll(".recharts-sector");
    fireEvent.click(sectors[0]!);
    expect(onMoveSelect).toHaveBeenCalledWith("e2e4");
  });

  it("shows hover-only move and Other tooltips, emphasizes one sector, and restores on leave", async () => {
    const onMoveSelect = vi.fn();
    render(
      <MoveResponseDistribution
        fen={FEN}
        color="white"
        client={clientFor(availableData())}
        onMoveSelect={onMoveSelect}
      />,
    );
    const chart = await screen.findByTestId("move-response-distribution-chart");
    const getSectors = () => chart.querySelectorAll(".recharts-sector");
    await waitFor(() => expect(getSectors()).toHaveLength(6));
    const other = screen.getByRole("button", { name: /Show other replies/ });

    fireEvent.mouseEnter(getSectors()[0]!);
    await waitFor(() => expect(screen.getByRole("tooltip")).toBeVisible());
    expect(screen.getByRole("tooltip")).toHaveTextContent("e4");
    expect(screen.getByRole("tooltip")).toHaveTextContent("4 occurrences");
    expect(screen.getByRole("tooltip")).toHaveTextContent("30.8%");
    expect(getSectors()[0]).toHaveAttribute("data-hovered", "true");
    expect(getSectors()[1]).toHaveAttribute("data-hovered", "false");
    expect(onMoveSelect).not.toHaveBeenCalled();
    expect(other).toHaveAttribute("aria-expanded", "false");

    fireEvent.mouseLeave(getSectors()[0]!);
    await waitFor(() => expect(screen.queryByRole("tooltip")).not.toBeInTheDocument());
    expect(getSectors()[0]).not.toHaveAttribute("data-hovered");
    expect(getSectors()[1]).not.toHaveAttribute("data-hovered");

    fireEvent.mouseEnter(getSectors()[5]!);
    await waitFor(() => expect(screen.getByRole("tooltip")).toBeVisible());
    expect(screen.getByRole("tooltip")).toHaveTextContent("Other");
    expect(screen.getByRole("tooltip")).toHaveTextContent("2 occurrences");
    expect(screen.getByRole("tooltip")).toHaveTextContent("15.4%");
    expect(onMoveSelect).not.toHaveBeenCalled();
    expect(other).toHaveAttribute("aria-expanded", "false");
  });

  it("keeps Other disclosure-only and exposes all tail controls with disclosure ARIA", async () => {
    const onMoveSelect = vi.fn();
    render(
      <MoveResponseDistribution
        fen={FEN}
        color="white"
        client={clientFor(availableData())}
        onMoveSelect={onMoveSelect}
      />,
    );
    const other = await screen.findByRole("button", { name: /Show other replies/ });
    expect(other).toHaveAttribute("aria-expanded", "false");
    const tailId = other.getAttribute("aria-controls");
    expect(tailId).toBeTruthy();
    expect(document.getElementById(tailId!)).toHaveAttribute("hidden");

    await userEvent.click(other);
    expect(other).toHaveAttribute("aria-expanded", "true");
    expect(document.getElementById(tailId!)).not.toHaveAttribute("hidden");
    expect(screen.getByRole("button", { name: /b3, 1 occurrences/ })).toBeVisible();

    expect(onMoveSelect).not.toHaveBeenCalled();
    await userEvent.click(screen.getByRole("button", { name: /b3, 1 occurrences/ }));
    expect(onMoveSelect).toHaveBeenCalledWith("b2b3");

    const sectors = document.querySelectorAll(".recharts-sector");
    fireEvent.click(sectors[5]!);
    expect(other).toHaveAttribute("aria-expanded", "false");
    expect(onMoveSelect).toHaveBeenCalledTimes(1);
  });

  it("marks the selected UCI and omits Other when there is no tail", async () => {
    render(
      <MoveResponseDistribution
        fen={FEN}
        color="black"
        selectedUci="d2d4"
        client={clientFor(
          availableData({ color: "black", replies: availableData().replies.slice(0, 5) }),
        )}
        onMoveSelect={vi.fn()}
      />,
    );

    await waitFor(() =>
      expect(screen.getByTestId("move-response-distribution")).toHaveAttribute(
        "data-state",
        "available",
      ),
    );
    expect(screen.queryByRole("button", { name: /Show other replies/ })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /d4, 3 occurrences/ })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
  });

  it("renders no-games without a chart or misleading Other control", async () => {
    render(
      <MoveResponseDistribution
        fen={FEN}
        color="white"
        client={clientFor(
          availableData({ matching_game_count: 0, outgoing_occurrence_count: 0, replies: [] }),
        )}
        onMoveSelect={vi.fn()}
      />,
    );

    await waitFor(() =>
      expect(screen.getByTestId("move-response-distribution")).toHaveAttribute(
        "data-state",
        "no-games",
      ),
    );
    expect(screen.getByRole("status")).toHaveTextContent(
      "No matching White repertoire games were found for this position.",
    );
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Other/ })).not.toBeInTheDocument();
  });

  it("renders matching games with no recorded next moves distinctly", async () => {
    render(
      <MoveResponseDistribution
        fen={FEN}
        color="white"
        client={clientFor(
          availableData({ matching_game_count: 4, outgoing_occurrence_count: 0, replies: [] }),
        )}
        onMoveSelect={vi.fn()}
      />,
    );

    await waitFor(() =>
      expect(screen.getByTestId("move-response-distribution")).toHaveAttribute(
        "data-state",
        "no-games",
      ),
    );
    expect(screen.getByRole("status")).toHaveTextContent("No recorded next moves");
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("renders unavailable with retry and recovers the current request", async () => {
    const client = vi
      .fn<MoveResponseDistributionClient>()
      .mockResolvedValueOnce({ status: "move_response_distribution_unavailable" })
      .mockResolvedValueOnce({ status: "success", data: availableData() });
    render(
      <MoveResponseDistribution fen={FEN} color="white" client={client} onMoveSelect={vi.fn()} />,
    );

    await waitFor(() =>
      expect(screen.getByTestId("move-response-distribution")).toHaveAttribute(
        "data-state",
        "unavailable",
      ),
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Move response data is unavailable.");
    await userEvent.click(screen.getByRole("button", { name: "Retry" }));
    await waitFor(() =>
      expect(screen.getByTestId("move-response-distribution")).toHaveAttribute(
        "data-state",
        "available",
      ),
    );
  });

  it("keeps keyboard focus and has no focused axe violations", async () => {
    const { container } = render(
      <MoveResponseDistribution
        fen={FEN}
        color="white"
        client={clientFor(availableData())}
        onMoveSelect={vi.fn()}
      />,
    );
    await waitFor(() =>
      expect(screen.getByRole("button", { name: /e4, 4 occurrences/ })).toBeVisible(),
    );
    const e4 = screen.getByRole("button", { name: /e4, 4 occurrences/ });
    e4.focus();
    expect(e4).toHaveFocus();
    await userEvent.keyboard("{Enter}");
    expect(e4).toHaveFocus();
    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });

  it("keeps every pie label inside the chart frame and vertically separated", async () => {
    const { container } = render(
      <MoveResponseDistribution
        fen={FEN}
        color="white"
        client={clientFor(availableData())}
        onMoveSelect={vi.fn()}
      />,
    );
    await waitFor(() => expect(container.querySelectorAll(".recharts-sector").length).toBe(6));

    const svg = container.querySelector("svg");
    expect(svg).not.toBeNull();
    const labels = chartLabels(svg!);
    expect(labels.map((label) => label.text)).toEqual([
      "e4 30.8%",
      "d4 23.1%",
      "c4 15.4%",
      "b3 7.7%",
      "c3 7.7%",
      "Other 15.4%",
    ]);

    for (const label of labels) {
      expect(label.x).toBeGreaterThan(0);
      expect(label.x).toBeLessThan(CHART_FRAME_SIZE);
      expect(label.y).toBeGreaterThan(0);
      expect(label.y).toBeLessThan(CHART_FRAME_SIZE);
      expect(label.left).toBeGreaterThanOrEqual(0);
      expect(label.right).toBeLessThanOrEqual(CHART_FRAME_SIZE);
    }

    for (const anchor of ["start", "end"]) {
      const side = labels.filter((label) => label.anchor === anchor).sort((a, b) => a.y - b.y);
      for (let index = 1; index < side.length; index += 1) {
        expect(side[index]!.y - side[index - 1]!.y).toBeGreaterThanOrEqual(13);
      }
    }
  });

  it("keeps the dense tiny-sector label cluster readable, spread, and collision-free", async () => {
    // User-reported regression shape: one dominant reply plus four tiny
    // replies and an Other tail, whose sectors are adjacent so their leader
    // lines all leave the pie edge from nearly the same point.
    const denseData: MoveResponseDistributionResponse = {
      fen: FEN,
      color: "white",
      matching_game_count: 10000,
      replies: [
        { rank: 1, child_uci: "e2e4", san: "e4", occurrence_count: 9804 },
        { rank: 2, child_uci: "d2d4", san: "d4", occurrence_count: 180 },
        { rank: 3, child_uci: "e2e3", san: "e3", occurrence_count: 10 },
        { rank: 4, child_uci: "b1c3", san: "Nc3", occurrence_count: 4 },
        { rank: 5, child_uci: "g1f3", san: "f3", occurrence_count: 2 },
        { rank: 6, child_uci: "g1g3", san: "g3", occurrence_count: 1 },
      ],
      outgoing_occurrence_count: 10001,
    };
    const { container } = render(
      <MoveResponseDistribution
        fen={FEN}
        color="white"
        client={clientFor(denseData)}
        onMoveSelect={vi.fn()}
      />,
    );
    await waitFor(() => expect(container.querySelectorAll(".recharts-sector").length).toBe(6));

    const svg = container.querySelector("svg");
    expect(svg).not.toBeNull();
    const labels = chartLabels(svg!);

    // The dominant reply sits alone on the left; the four tiny replies and
    // the grey Other label form the dense cluster on the right edge.
    const left = labels.filter((label) => label.anchor === "end");
    const right = labels.filter((label) => label.anchor === "start");
    expect(left.map((label) => label.text)).toEqual(["e4 98.0%"]);
    expect([...right.map((label) => label.text)].sort()).toEqual(
      ["d4 1.8%", "e3 0.1%", "f3 0.0%", "Nc3 0.0%", "Other 0.0%"].sort(),
    );

    // Every label stays inside the fixed chart frame.
    for (const label of labels) {
      expect(label.left).toBeGreaterThanOrEqual(0);
      expect(label.right).toBeLessThanOrEqual(CHART_FRAME_SIZE);
      expect(label.top).toBeGreaterThanOrEqual(0);
      expect(label.bottom).toBeLessThanOrEqual(CHART_FRAME_SIZE);
    }

    // The dense right-edge cluster spreads with a readable vertical gap
    // instead of compressing into a tight stack.
    const sortedRight = [...right].sort((a, b) => a.y - b.y);
    for (let index = 1; index < sortedRight.length; index += 1) {
      expect(sortedRight[index]!.y - sortedRight[index - 1]!.y).toBeGreaterThanOrEqual(17);
    }
    const spreadTop = sortedRight[0]!.y;
    const spreadBottom = sortedRight[sortedRight.length - 1]!.y;
    expect(spreadBottom - spreadTop).toBeGreaterThanOrEqual(4 * 17);
    expect(spreadTop).toBeGreaterThan(60);
    expect(spreadBottom).toBeLessThan(180);

    // No two labels overlap.
    for (let first = 0; first < labels.length; first += 1) {
      for (let second = first + 1; second < labels.length; second += 1) {
        const a = labels[first]!;
        const b = labels[second]!;
        expect(labelsOverlap(a, b), `labels "${a.text}" and "${b.text}" overlap`).toBe(false);
      }
    }

    // No leader line runs through another label's text box: the leaders fan
    // out to the spread stack instead of tangling across the labels.
    const leaders = Array.from(svg!.querySelectorAll("g")).flatMap((group) => {
      const line = group.querySelector(":scope > line");
      const text = group.querySelector(":scope > text");
      if (!line || !text) return [];
      return [
        {
          text: text.textContent ?? "",
          x1: Number(line.getAttribute("x1")),
          y1: Number(line.getAttribute("y1")),
          x2: Number(line.getAttribute("x2")),
          y2: Number(line.getAttribute("y2")),
        },
      ];
    });
    expect(leaders).toHaveLength(labels.length);
    for (const leader of leaders) {
      for (const label of labels) {
        if (label.text === leader.text) continue;
        expect(
          segmentHitsBox(leader, label),
          `leader for "${leader.text}" crosses label "${label.text}"`,
        ).toBe(false);
      }
    }
  });

  it("keeps the panel's constrained and motion/forced-colour CSS boundaries", async () => {
    expect(rawStyles).toContain("@container move-response-distribution");
    expect(rawStyles).toContain("max-width: 25.75rem");
    expect(rawStyles).toContain("@media (prefers-reduced-motion: reduce)");
    expect(rawStyles).toContain("@media (forced-colors: active)");
    expect(rawStyles).toContain("background: Canvas;");
    expect(rawStyles).toContain("background: Highlight;");
  });

  it("keeps SAN tokens unbreakable and lets the tooltip escape the chart frame", () => {
    const sanRule = rawStyles.match(/\.replySan\s*\{[^}]*\}/);
    expect(sanRule).not.toBeNull();
    expect(sanRule![0]).toContain("white-space: nowrap");
    expect(sanRule![0]).toContain("overflow-wrap: normal");
    // The chart frame must not clip: the cursor-anchored hover tooltip is
    // allowed to extend past the frame edge. Pie labels stay inside the
    // frame by geometry (see the label-layout test above), not by clipping.
    const chartFrameRule = rawStyles.match(/\.chartFrame\s*\{[^}]*\}/);
    expect(chartFrameRule).not.toBeNull();
    expect(chartFrameRule![0]).toContain("overflow: visible");
    expect(rawStyles).toContain("minmax(auto, 1fr)");
    // The shared reply/other button rule must not re-enable per-character
    // wrapping (SAN tokens stay whole); descriptive text wraps via its own
    // rules instead.
    const buttonRule = rawStyles.match(/\.replyButton,\s*\.otherButton\s*\{[^}]*\}/);
    expect(buttonRule).not.toBeNull();
    expect(buttonRule![0]).not.toContain("overflow-wrap");
  });
});
