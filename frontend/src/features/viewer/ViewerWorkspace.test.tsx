import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ComponentProps } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import ViewerWorkspace from "./ViewerWorkspace";
import type {
  AnalysisClient,
  EvaluationObservation,
  EvaluationResult,
  EvaluationStatus,
} from "./analysisApi";
import type { GameLookup, GameLookupResult } from "./positionApi";
import {
  STAGE1_GAME,
  STAGE1_GAME_UUID,
  STAGE1_UNSAFE_SOURCE_GAME,
  type Stage1Game,
} from "./stage1GameTypes";

expect.extend(matchers);

const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";
const GAME_UUID = STAGE1_GAME_UUID;
const BLACK_GAME: Stage1Game = { ...STAGE1_GAME, subject_color: "black" };

const here = dirname(fileURLToPath(import.meta.url));
const rawStyles = readFileSync(join(here, "ViewerWorkspace.module.css"), "utf8");

afterEach(() => cleanup());

async function fillAndSubmit(user: ReturnType<typeof userEvent.setup>, uuid = GAME_UUID, ply = "") {
  await user.type(screen.getByLabelText("Game UUID"), uuid);
  if (ply) {
    await user.type(screen.getByLabelText(/Ply/), ply);
  }
  await user.click(screen.getByRole("button", { name: "Load game" }));
}

function successfulLookup(game: Stage1Game = STAGE1_GAME): GameLookup {
  return vi.fn<GameLookup>(async (_uuid, initialPly) => ({
    status: "success",
    game: { ...game, initial_ply: initialPly ?? 0 },
  }));
}

function noAnalysisClient(): AnalysisClient {
  return {
    observe: vi.fn(async (fen) => ({
      status: "success" as const,
      data: { fen, eligibility: "missing" as const, result: null, status: null, terminal: false },
    })),
    enqueue: vi.fn(async (fen, action) => ({
      status: "success" as const,
      data: {
        fen,
        action,
        outcome: "queued",
        eligibility: "missing" as const,
        status: {
          state: "queued" as const,
          position: 0,
          attempts: 1,
          enqueued_at: "2026-08-21T00:00:00+00:00",
          started_at: null,
          completed_at: null,
          error_code: null,
        },
      },
    })),
    status: vi.fn(),
  };
}

function completedAnalysisClient(): AnalysisClient {
  const result: EvaluationResult = {
    fen: STAGE1_GAME.positions[0].fen,
    profile_id: "mp09-balanced-nodes-v2-200000",
    candidates: [
      {
        rank: 1,
        score_kind: "cp",
        score_value: 34,
        wdl_wins: 420,
        wdl_draws: 300,
        wdl_losses: 280,
        pv_uci: ["e2e4"],
        depth: 20,
        seldepth: 24,
        nodes: 200000,
        engine_time_ms: 100,
      },
    ],
    terminal_kind: null,
    completed_at: "2026-08-21T00:00:01+00:00",
    wall_time_ms: 100,
  };
  const completedStatus: EvaluationStatus = {
    state: "done",
    position: 0,
    attempts: 1,
    enqueued_at: "2026-08-21T00:00:00+00:00",
    started_at: "2026-08-21T00:00:00+00:00",
    completed_at: "2026-08-21T00:00:01+00:00",
    error_code: null,
  };
  const observe = vi.fn(async (fen: string) => {
    const data: EvaluationObservation = {
      fen,
      eligibility: "eligible",
      result: { ...result, fen },
      status: completedStatus,
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

function renderViewer(props: ComponentProps<typeof ViewerWorkspace> = {}) {
  return render(<ViewerWorkspace analysisClient={noAnalysisClient()} {...props} />);
}

describe("ViewerWorkspace", () => {
  it("composes the empty viewer with the static board and both empty panels", () => {
    renderViewer();

    expect(screen.getByRole("heading", { level: 1, name: "Position viewer" })).toBeVisible();
    expect(screen.getByRole("img", { name: BOARD_LABEL })).toBeVisible();
    expect(screen.getByRole("meter", { name: "Evaluation" })).toHaveAttribute(
      "aria-valuetext",
      "No analysis yet; evaluation neutral.",
    );
    expect(screen.getAllByText("No game loaded")).toHaveLength(2);
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
  });

  it("uses the whole-game lookup, loads blank Ply at zero, and shows the complete context", async () => {
    const lookup = successfulLookup(BLACK_GAME);
    const user = userEvent.setup();
    renderViewer({ lookup });

    await fillAndSubmit(user);

    expect(await screen.findByText("Ply 0 of 3")).toBeVisible();
    expect(screen.getByText("Initial position")).toBeVisible();
    expect(screen.getByRole("group", { name: /ply 0, Black at the bottom/ })).toBeVisible();
    expect(screen.getByRole("link", { name: "Chess.com game" })).toHaveAttribute(
      "target",
      "_blank",
    );
    expect(lookup).toHaveBeenCalledWith(GAME_UUID, undefined, expect.any(AbortSignal));
  });

  it("loads an explicit Ply and traverses in memory without changing the form or requesting again", async () => {
    const lookup = successfulLookup();
    const user = userEvent.setup();
    renderViewer({ lookup });

    await fillAndSubmit(user, GAME_UUID, "1");
    await screen.findByText("Ply 1 of 3");
    const next = screen.getByRole("button", { name: "Next" });
    expect(screen.getByLabelText(/Ply/)).toHaveValue("1");

    await user.click(next);
    expect(screen.getByText("Ply 2 of 3")).toBeVisible();
    expect(screen.getByText("e5")).toBeVisible();
    expect(screen.getByLabelText(/Ply/)).toHaveValue("1");
    expect(lookup).toHaveBeenCalledOnce();
    expect(document.activeElement).toBe(next);

    await user.click(next);
    expect(screen.getByText("Ply 3 of 3")).toBeVisible();
    expect(next).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Previous" }));
    expect(screen.getByText("Ply 2 of 3")).toBeVisible();
  });

  it.each([
    ["game_not_found", "Game not found"],
    ["position_not_found", "Position not found"],
    ["corpus_unavailable", "Corpus unavailable"],
    ["game_unavailable", "Game unavailable"],
    ["unexpected_failure", "Unable to load game"],
  ] as const)("maps the typed %s response to an accessible state", async (status, heading) => {
    const lookup: GameLookup = vi.fn(async (): Promise<GameLookupResult> => ({ status }));
    const user = userEvent.setup();
    renderViewer({ lookup });

    await fillAndSubmit(user);

    expect(await screen.findByRole("heading", { name: heading, level: 2 })).toBeVisible();
    expect(screen.getByRole("img", { name: BOARD_LABEL })).toBeVisible();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
  });

  it("keeps the active game and controls during replacement loading and restores them after failure", async () => {
    let calls = 0;
    let resolveReplacement!: (result: GameLookupResult) => void;
    const lookup: GameLookup = vi.fn<GameLookup>(async (_uuid, initialPly) => {
      calls += 1;
      if (calls === 1) {
        return { status: "success", game: { ...STAGE1_GAME, initial_ply: initialPly ?? 0 } };
      }
      return new Promise<GameLookupResult>((resolve) => {
        resolveReplacement = resolve;
      });
    });
    const user = userEvent.setup();
    renderViewer({ lookup });

    await fillAndSubmit(user, GAME_UUID, "1");
    await screen.findByText("Ply 1 of 3");
    await user.clear(screen.getByLabelText(/Ply/));
    await user.type(screen.getByLabelText(/Ply/), "2");
    await user.click(screen.getByRole("button", { name: "Load game" }));

    await screen.findByText("Loading the complete game...");
    expect(screen.getByText("Ply 1 of 3")).toBeVisible();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();

    resolveReplacement({ status: "game_unavailable" });
    expect(
      await screen.findByRole("heading", { name: "Game unavailable", level: 2 }),
    ).toBeVisible();
    expect(screen.getByText("Ply 1 of 3")).toBeVisible();
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
  });

  it("reset aborts a pending request and restores empty panels without stale replacement", async () => {
    let resolvePending!: (result: GameLookupResult) => void;
    const lookup: GameLookup = vi.fn(
      () =>
        new Promise<GameLookupResult>((resolve) => {
          resolvePending = resolve;
        }),
    );
    const user = userEvent.setup();
    renderViewer({ lookup });

    await fillAndSubmit(user);
    await user.click(screen.getByRole("button", { name: "Reset" }));
    expect(screen.getAllByText("No game loaded")).toHaveLength(2);
    expect(screen.getByRole("img", { name: BOARD_LABEL })).toBeVisible();

    resolvePending({ status: "success", game: STAGE1_GAME });
    await Promise.resolve();
    expect(screen.getAllByText("No game loaded")).toHaveLength(2);
    expect(screen.getByLabelText("Game UUID")).toHaveValue("");
  });

  it("renders unsafe source attribution as unavailable without rejecting the active game", async () => {
    const lookup = successfulLookup(STAGE1_UNSAFE_SOURCE_GAME);
    const user = userEvent.setup();
    renderViewer({ lookup });

    await fillAndSubmit(user);

    expect(await screen.findByText("Ply 0 of 3")).toBeVisible();
    expect(screen.getByText("Source unavailable")).toBeVisible();
    expect(screen.queryByRole("link", { name: "Chess.com game" })).not.toBeInTheDocument();
  });

  it("keeps the displayed board unchanged while analysis is requested", async () => {
    const lookup = successfulLookup();
    const analysisClient = noAnalysisClient();
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={lookup} analysisClient={analysisClient} />);

    await fillAndSubmit(user);
    const board = await screen.findByRole("group", { name: /ply 0, White at the bottom/ });
    const boardLabel = board.getAttribute("aria-label");
    const analyze = await screen.findByRole("button", { name: "Analyze position" });

    await user.click(analyze);

    expect(analysisClient.enqueue).toHaveBeenCalledWith(
      STAGE1_GAME.positions[0].fen,
      "analyze",
      expect.any(AbortSignal),
    );
    expect(screen.getByRole("group", { name: /ply 0, White at the bottom/ })).toHaveAttribute(
      "aria-label",
      boardLabel,
    );
    expect(screen.getByRole("group", { name: /ply 0, White at the bottom/ })).not.toHaveAttribute(
      "aria-roledescription",
      "draggable",
    );
  });

  it("shares one completed observation with the panel and the beside-board eval bar", async () => {
    const lookup = successfulLookup();
    const analysisClient = completedAnalysisClient();
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={lookup} analysisClient={analysisClient} />);

    await fillAndSubmit(user);

    expect(await screen.findByText("Analysis complete")).toBeVisible();
    expect(screen.getByText("best-line evaluation +0.34.")).toBeVisible();
    expect(screen.getByRole("meter", { name: "Evaluation" })).toHaveAttribute(
      "data-state",
      "best-line",
    );
    expect(analysisClient.observe).toHaveBeenCalledOnce();
    expect(analysisClient.status).not.toHaveBeenCalled();
  });

  it("keeps the accepted container-query and accessibility boundaries", async () => {
    expect(rawStyles).toMatch(/container-type:\s*inline-size/);
    expect(rawStyles).toMatch(/@container\s*\(max-width:\s*40rem\)/);
    expect(rawStyles).not.toMatch(/@media\s*\(\s*(?:max-width|min-width)\s*:/);

    const { container } = renderViewer({ lookup: successfulLookup() });
    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });
});
