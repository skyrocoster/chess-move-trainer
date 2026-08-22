import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AnalysisPanel } from "./AnalysisPanel";
import type {
  AnalysisClient,
  EvaluationObservation,
  EvaluationPoll,
  EvaluationResult,
  EvaluationStatus,
} from "./analysisApi";

expect.extend(matchers);

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function queueStatus(state: EvaluationStatus["state"]): EvaluationStatus {
  return {
    state,
    position: 0,
    attempts: 1,
    enqueued_at: "2026-08-21T00:00:00+00:00",
    started_at: state === "queued" ? null : "2026-08-21T00:00:00+00:00",
    completed_at: state === "done" || state === "failed" ? "2026-08-21T00:00:01+00:00" : null,
    error_code: state === "failed" ? "engine_failure" : null,
  };
}

function result(): EvaluationResult {
  return {
    fen: FEN,
    profile_id: "mp09-balanced-nodes-v2-200000",
    candidates: [
      {
        rank: 1,
        score_kind: "cp",
        score_value: 34,
        wdl_wins: 420,
        wdl_draws: 300,
        wdl_losses: 280,
        pv_uci: ["e2e4", "e7e5", "g1f3"],
        depth: 20,
        seldepth: 24,
        nodes: 200000,
        engine_time_ms: 100,
      },
      {
        rank: 2,
        score_kind: "mate",
        score_value: -3,
        wdl_wins: 200,
        wdl_draws: 300,
        wdl_losses: 500,
        pv_uci: ["d2d4", "d7d5"],
        depth: 20,
        seldepth: 24,
        nodes: 200000,
        engine_time_ms: 100,
      },
      ...[3, 4, 5].map((rank) => ({
        rank,
        score_kind: "cp" as const,
        score_value: 10 - rank,
        wdl_wins: 400,
        wdl_draws: 300,
        wdl_losses: 300,
        pv_uci: ["c2c4"],
        depth: 20,
        seldepth: 24,
        nodes: 200000,
        engine_time_ms: 100,
      })),
    ],
    terminal_kind: null,
    completed_at: "2026-08-21T00:00:01+00:00",
    wall_time_ms: 100,
  };
}

function observation(
  eligibility: EvaluationObservation["eligibility"],
  currentResult: EvaluationResult | null = null,
  status: EvaluationStatus | null = null,
): EvaluationObservation {
  return { fen: FEN, eligibility, result: currentResult, status, terminal: false };
}

function poll(state: EvaluationPoll["state"]): EvaluationPoll {
  return {
    fen: FEN,
    state,
    completed_at: state === "done" ? "2026-08-21T00:00:01+00:00" : null,
    error_code: state === "failed" ? "engine_failure" : null,
  };
}

function clientFor(initial: EvaluationObservation): AnalysisClient {
  return {
    observe: vi.fn().mockResolvedValue({ status: "success", data: initial }),
    enqueue: vi.fn().mockResolvedValue({
      status: "success",
      data: {
        fen: FEN,
        action: "analyze",
        outcome: "queued",
        eligibility: initial.eligibility,
        status: queueStatus("queued"),
      },
    }),
    status: vi.fn().mockResolvedValue({ status: "success", data: poll(null) }),
  };
}

afterEach(() => cleanup());

describe("AnalysisPanel", () => {
  it("loads eligible results automatically and renders five text-only lines", async () => {
    const client = clientFor(observation("eligible", result()));
    render(<AnalysisPanel fen={FEN} client={client} />);

    expect(await screen.findByText("Analysis complete")).toBeVisible();
    expect(screen.getByRole("list", { name: "Ranked analysis lines" })).toBeVisible();
    expect(screen.getAllByRole("listitem")).toHaveLength(5);
    expect(screen.getByText("+0.34")).toBeVisible();
    expect(screen.getByText("-M3")).toBeVisible();
    expect(screen.getByText("1. e4 e5 2. Nf3")).toBeVisible();
    expect(screen.getByText("W 42.0% / D 30.0% / L 28.0%")).toBeVisible();
    expect(screen.getByRole("button", { name: "Update analysis" })).toBeVisible();
    expect(client.enqueue).not.toHaveBeenCalled();
  });

  it("shows missing results only behind a deliberate Analyze action", async () => {
    const client = clientFor(observation("missing"));
    render(<AnalysisPanel fen={FEN} client={client} />);

    expect(await screen.findByText("Analysis available on request")).toBeVisible();
    expect(screen.getByRole("button", { name: "Analyze position" })).toBeVisible();
    expect(client.enqueue).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole("button", { name: "Analyze position" }));
    expect(client.enqueue).toHaveBeenCalledWith(FEN, "analyze", expect.any(AbortSignal));
  });

  it("labels stale results and requires a deliberate Update", async () => {
    const client = clientFor(observation("stale", result()));
    render(<AnalysisPanel fen={FEN} client={client} />);

    expect(await screen.findByText("Stale analysis")).toBeVisible();
    await userEvent.click(screen.getByRole("button", { name: "Update analysis" }));
    expect(client.enqueue).toHaveBeenCalledWith(FEN, "update", expect.any(AbortSignal));
  });

  it.each([
    ["queued", "Analysis queued"],
    ["running", "Analysis running"],
  ] as const)("observes an already %s position without an action", async (state, label) => {
    const client = clientFor(observation("missing", null, queueStatus(state)));
    render(<AnalysisPanel fen={FEN} client={client} pollIntervalMs={60000} />);

    expect(await screen.findByText(label)).toBeVisible();
    expect(
      screen.queryByRole("button", { name: /Analyze|Update|Retry analysis/ }),
    ).not.toBeInTheDocument();
    expect(client.enqueue).not.toHaveBeenCalled();
  });

  it("polls queued work and reloads the completed result", async () => {
    const completed = observation("eligible", result());
    const client = clientFor(observation("missing", null, queueStatus("queued")));
    client.status = vi
      .fn()
      .mockResolvedValueOnce({ status: "success", data: poll("running") })
      .mockResolvedValueOnce({ status: "success", data: poll("done") });
    client.observe = vi
      .fn()
      .mockResolvedValueOnce({
        status: "success",
        data: observation("missing", null, queueStatus("queued")),
      })
      .mockResolvedValueOnce({ status: "success", data: completed });
    render(<AnalysisPanel fen={FEN} client={client} pollIntervalMs={1} />);

    expect(await screen.findByText("Analysis complete")).toBeVisible();
    expect(client.status).toHaveBeenCalledTimes(2);
  });

  it("shows failure without automatic retry and offers deliberate Retry", async () => {
    const client = clientFor(observation("missing", null, queueStatus("failed")));
    render(<AnalysisPanel fen={FEN} client={client} />);

    expect(await screen.findByText("Analysis failed")).toBeVisible();
    expect(screen.getByRole("alert")).toHaveTextContent("No complete result was published");
    expect(screen.getByRole("button", { name: "Retry analysis" })).toBeVisible();
    expect(client.enqueue).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole("button", { name: "Retry analysis" }));
    expect(client.enqueue).toHaveBeenCalledWith(FEN, "retry", expect.any(AbortSignal));
  });

  it("has no focused accessibility violations", async () => {
    const client = clientFor(observation("eligible", result()));
    const { container } = render(<AnalysisPanel fen={FEN} client={client} />);
    await screen.findByText("Analysis complete");

    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });

  it("does not invent candidate lines for a terminal result", async () => {
    const terminal = { ...result(), candidates: [], terminal_kind: "checkmate" };
    const client = clientFor(observation("eligible", terminal));
    render(<AnalysisPanel fen={FEN} client={client} />);

    expect(
      await screen.findByText("No candidate lines are available for this terminal position."),
    ).toBeVisible();
    expect(screen.queryByRole("list", { name: "Ranked analysis lines" })).not.toBeInTheDocument();
  });

  it("does not automatically retry an observation failure", async () => {
    const client: AnalysisClient = {
      observe: vi.fn().mockResolvedValue({ status: "evaluation_unavailable" }),
      enqueue: vi.fn(),
      status: vi.fn(),
    };
    render(<AnalysisPanel fen={FEN} client={client} />);

    expect(await screen.findByText("Evaluation unavailable")).toBeVisible();
    await waitFor(() => expect(client.observe).toHaveBeenCalledOnce());
    expect(client.enqueue).not.toHaveBeenCalled();
  });
});
