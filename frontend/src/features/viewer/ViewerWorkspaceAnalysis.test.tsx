import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it, vi } from "vitest";

import ViewerWorkspace from "./ViewerWorkspace";
import type {
  AnalysisClient,
  EvaluationObservation,
  EvaluationResult,
  EvaluationStatus,
} from "./analysisApi";
import type { GameLookup } from "./positionApi";
import type { Game } from "./gameModel";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "./viewerFixtures";

expect.extend(matchers);

const here = dirname(fileURLToPath(import.meta.url));
const rawStyles = readFileSync(join(here, "ViewerWorkspace.module.css"), "utf8");

afterEach(() => cleanup());

function successfulLookup(game: Game = VIEWER_GAME): GameLookup {
  return vi.fn<GameLookup>(async (_uuid, initialPly) => ({
    status: "success",
    game: { ...game, initial_ply: initialPly ?? 0 },
  }));
}

function completedResult(fen: string, candidateMoves = ["e2e4"]): EvaluationResult {
  return {
    fen,
    profile_id: "mp09-balanced-nodes-v2-200000",
    candidates: candidateMoves.map((move, index) => ({
      rank: index + 1,
      score_kind: "cp",
      score_value: 34 - index * 10,
      wdl_wins: 420,
      wdl_draws: 300,
      wdl_losses: 280,
      pv_uci: [move],
      depth: 20,
      seldepth: 24,
      nodes: 200000,
      engine_time_ms: 100,
    })),
    terminal_kind: null,
    completed_at: "2026-08-21T00:00:01+00:00",
    wall_time_ms: 100,
  };
}

function completedStatus(): EvaluationStatus {
  return {
    state: "done",
    position: 0,
    attempts: 1,
    enqueued_at: "2026-08-21T00:00:00+00:00",
    started_at: "2026-08-21T00:00:00+00:00",
    completed_at: "2026-08-21T00:00:01+00:00",
    error_code: null,
  };
}

function completedAnalysisClient(candidateMoves = ["e2e4"]): AnalysisClient {
  const observe = vi.fn(async (fen: string) => {
    const data: EvaluationObservation = {
      fen,
      eligibility: "eligible",
      result: completedResult(fen, candidateMoves),
      status: completedStatus(),
      terminal: false,
    };
    return { status: "success" as const, data };
  });
  return {
    observe,
    enqueue: vi.fn(),
    status: vi.fn(),
  };
}

describe("ViewerWorkspace analysis", () => {
  it("shares one completed observation with the panel and the beside-board eval bar", async () => {
    const lookup = successfulLookup();
    const analysisClient = completedAnalysisClient();
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={lookup} analysisClient={analysisClient} />);

    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.click(screen.getByRole("button", { name: "Load game" }));

    const analysisStatus = await screen.findByText("Analysis complete");
    const contextButton = screen.getByRole("button", { name: "Game Context" });
    const sourceLink = screen.getByRole("link", { name: "Chess.com game" });
    const contentId = contextButton.getAttribute("aria-controls");
    const stage = screen.getByTestId("board-eval-stage");
    const board = screen.getByRole("group", { name: /ply 0, White at the bottom/ });

    expect(analysisStatus).toBeVisible();
    expect(stage).toContainElement(board);
    expect(board).toHaveAttribute("data-board-visual");
    const meter = screen.getByRole("meter", { name: "Evaluation" });
    expect(meter).toHaveTextContent("+0.34");
    expect(meter).toHaveAttribute("data-state", "best-line");
    expect(meter).toHaveAttribute("aria-valuetext", "best-line evaluation +0.34.");
    expect(contextButton).toHaveAttribute("aria-expanded", "true");
    expect(sourceLink.compareDocumentPosition(analysisStatus)).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING,
    );
    if (!contentId) {
      throw new Error("Game Context disclosure did not expose its controlled content");
    }
    const disclosureContent = document.getElementById(contentId);
    if (!disclosureContent) {
      throw new Error(`Game Context disclosure content ${contentId} was not found`);
    }
    expect(disclosureContent).toContainElement(sourceLink);
    expect(analysisClient.observe).toHaveBeenCalledOnce();
    expect(analysisClient.status).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Flip" }));
    expect(screen.getByRole("group", { name: /ply 0, Black at the bottom/ })).toBeVisible();
    expect(screen.getByRole("meter", { name: "Evaluation" })).toHaveAttribute(
      "data-orientation",
      "black",
    );
    expect(screen.getByText("Analysis complete")).toBeVisible();
    expect(analysisClient.observe).toHaveBeenCalledOnce();
  });

  it("keeps the accepted container-query and accessibility boundaries", async () => {
    expect(rawStyles).toMatch(/container-type:\s*inline-size/);
    expect(rawStyles).toMatch(/@container\s*\(max-width:\s*40rem\)/);
    expect(rawStyles).not.toMatch(/@media\s*\(\s*(?:max-width|min-width)\s*:/);
    expect(rawStyles).toMatch(/"board board context"/);
    expect(rawStyles).toMatch(/grid-template-columns:\s*minmax\(0, 1fr\) 30px minmax\(0, 1fr\)/);
    expect(rawStyles).toMatch(/"board board"/);
    expect(rawStyles).not.toMatch(/"board eval context"/);
    expect(rawStyles).not.toMatch(/2\.75rem/);

    const { container } = render(<ViewerWorkspace lookup={successfulLookup()} />);
    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });
});
