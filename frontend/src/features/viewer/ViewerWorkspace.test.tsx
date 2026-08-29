import { cleanup, render, screen, waitFor } from "@testing-library/react";
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
import type { PositionContextClient, PositionContextResult } from "./positionContextApi";
import type { Game } from "./gameModel";
import { UNSAFE_SOURCE_GAME, VIEWER_GAME, VIEWER_GAME_UUID } from "./viewerFixtures";
import { PROMOTION_GAME } from "./viewerStoryFixtures";

expect.extend(matchers);

const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";
const GAME_UUID = VIEWER_GAME_UUID;
const BLACK_GAME: Game = { ...VIEWER_GAME, subject_color: "black" };

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

function successfulLookup(game: Game = VIEWER_GAME): GameLookup {
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

function positionContextClient(
  resultFor: (fen: string) => PositionContextResult = (fen) => ({
    status: "success",
    data: {
      fen,
      overall_exists: true,
      white_count: 2,
      black_count: 1,
    },
  }),
): PositionContextClient {
  return vi.fn(async (fen) => resultFor(fen));
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

function retryingAnalysisClient(): AnalysisClient {
  const observe = vi.fn<AnalysisClient["observe"]>(async (fen) => ({
    status: "success",
    data: { fen, eligibility: "missing", result: null, status: null, terminal: false },
  }));
  observe.mockResolvedValueOnce({ status: "evaluation_unavailable" });
  return { observe, enqueue: vi.fn(), status: vi.fn() };
}

function pollingAnalysisClient(): AnalysisClient {
  const observe = vi.fn<AnalysisClient["observe"]>();
  observe.mockImplementationOnce(async (fen) => ({
    status: "success",
    data: {
      fen,
      eligibility: "missing",
      result: null,
      status: {
        state: "queued",
        position: 0,
        attempts: 1,
        enqueued_at: "2026-08-21T00:00:00+00:00",
        started_at: null,
        completed_at: null,
        error_code: null,
      },
      terminal: false,
    },
  }));
  observe.mockImplementation(async (fen) => ({
    status: "success",
    data: {
      fen,
      eligibility: "eligible",
      result: completedResult(fen),
      status: completedStatus(),
      terminal: false,
    },
  }));

  const status = vi.fn<AnalysisClient["status"]>();
  status.mockImplementationOnce(async (fen) => ({
    status: "success",
    data: { fen, state: "running", completed_at: null, error_code: null },
  }));
  status.mockImplementationOnce(async (fen) => ({
    status: "success",
    data: {
      fen,
      state: "done",
      completed_at: "2026-08-21T00:00:01+00:00",
      error_code: null,
    },
  }));
  return { observe, enqueue: vi.fn(), status };
}

function renderViewer(props: ComponentProps<typeof ViewerWorkspace> = {}) {
  return render(
    <ViewerWorkspace
      analysisClient={noAnalysisClient()}
      positionContextClient={positionContextClient()}
      {...props}
    />,
  );
}

describe("ViewerWorkspace", () => {
  it("composes the empty viewer with the static board and both empty panels", async () => {
    const user = userEvent.setup();
    renderViewer();

    expect(screen.getByRole("heading", { level: 1, name: "Position viewer" })).toBeVisible();
    const stage = screen.getByTestId("board-eval-stage");
    const board = screen.getByRole("img", { name: BOARD_LABEL });
    const meter = screen.getByRole("meter", { name: "Evaluation" });
    expect(stage).toHaveAttribute("data-board-staged", "true");
    expect(stage).toContainElement(board);
    expect(stage).toContainElement(meter);
    expect(board).toBeVisible();
    expect(meter).toHaveAttribute("aria-valuetext", "No analysis yet; evaluation neutral.");
    expect(screen.getAllByText("No game loaded")).toHaveLength(2);
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
    const flip = screen.getByRole("button", { name: "Flip" });
    expect(flip).toBeEnabled();

    await user.click(flip);
    expect(
      screen.getByRole("img", { name: /standard starting position, Black at the bottom/ }),
    ).toBeVisible();
    expect(meter).toHaveAttribute("data-orientation", "black");

    await user.click(flip);
    expect(screen.getByRole("img", { name: BOARD_LABEL })).toBeVisible();
    expect(meter).toHaveAttribute("data-orientation", "white");
  });

  it("shows recurrence for the displayed position, refreshes navigation, and preserves it through Flip", async () => {
    const contextClient = positionContextClient();
    const user = userEvent.setup();
    renderViewer({ lookup: successfulLookup(), positionContextClient: contextClient });

    await fillAndSubmit(user);
    await screen.findByText("Seen in 2 games as White", { exact: true });
    expect(contextClient).toHaveBeenCalledWith(
      VIEWER_GAME.positions[0].fen,
      expect.any(AbortSignal),
    );
    const callsBeforeFlip = vi.mocked(contextClient).mock.calls.length;

    await user.click(screen.getByRole("button", { name: "Flip" }));
    expect(screen.getByText("Seen in 2 games as White", { exact: true })).toBeVisible();
    expect(contextClient).toHaveBeenCalledTimes(callsBeforeFlip);

    await user.click(screen.getByRole("button", { name: "Next" }));
    await screen.findByText("Ply 1 of 3");
    await waitFor(() =>
      expect(contextClient).toHaveBeenCalledWith(
        VIEWER_GAME.positions[1].fen,
        expect.any(AbortSignal),
      ),
    );
  });

  it("renders Never seen for zero and absent positions without exposing context failures", async () => {
    const contextClient = positionContextClient((fen) => ({
      status: "success",
      data: {
        fen,
        overall_exists: fen === VIEWER_GAME.positions[0].fen,
        white_count: 0,
        black_count: 0,
      },
    }));
    const user = userEvent.setup();
    renderViewer({ lookup: successfulLookup(), positionContextClient: contextClient });

    await fillAndSubmit(user);
    expect(await screen.findByText("Never seen as White", { exact: true })).toBeVisible();
    expect(screen.getByText("Never seen as Black", { exact: true })).toBeVisible();
    expect(screen.queryByText(/Seen in/)).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Next" }));
    await screen.findByText("Ply 1 of 3");
    await waitFor(() =>
      expect(contextClient).toHaveBeenCalledWith(
        VIEWER_GAME.positions[1].fen,
        expect.any(AbortSignal),
      ),
    );
    expect(screen.getByText("Never seen as White", { exact: true })).toBeVisible();
    expect(screen.getByText("Never seen as Black", { exact: true })).toBeVisible();
  });

  it("keeps the existing Game Context visible while recurrence is loading or unavailable", async () => {
    const contextClient = vi.fn<PositionContextClient>(() => new Promise(() => {}));
    const user = userEvent.setup();
    renderViewer({ lookup: successfulLookup(), positionContextClient: contextClient });

    await fillAndSubmit(user);
    expect(await screen.findByText("Ply 0 of 3")).toBeVisible();
    expect(screen.queryByText(/Seen in|Never seen/)).not.toBeInTheDocument();
    expect(screen.queryByText(/position context/i)).not.toBeInTheDocument();
  });

  it("silently omits recurrence when the position-context request fails", async () => {
    const contextClient = vi.fn<PositionContextClient>(async () => ({
      status: "position_context_unavailable",
    }));
    const user = userEvent.setup();
    renderViewer({ lookup: successfulLookup(), positionContextClient: contextClient });

    await fillAndSubmit(user);
    expect(await screen.findByText("Ply 0 of 3")).toBeVisible();
    expect(screen.queryByText(/Seen in|Never seen/)).not.toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("uses the whole-game lookup, loads blank Ply at zero, and shows the complete context", async () => {
    const lookup = successfulLookup(BLACK_GAME);
    const user = userEvent.setup();
    renderViewer({ lookup });

    await fillAndSubmit(user);

    expect(await screen.findByText("Ply 0 of 3")).toBeVisible();
    const announcement = screen.getByText("Ply 0 of 3: Initial position", { exact: true });
    expect(announcement).toHaveAttribute("role", "status");
    expect(announcement).toHaveAttribute("aria-live", "polite");
    expect(announcement).toHaveAttribute("aria-atomic", "true");
    expect(screen.getByText("Initial position")).toBeVisible();
    expect(screen.getByRole("group", { name: /ply 0, Black at the bottom/ })).toBeVisible();
    const flip = screen.getByRole("button", { name: "Flip" });
    await user.click(flip);
    expect(screen.getByRole("group", { name: /ply 0, White at the bottom/ })).toBeVisible();
    expect(screen.getByText("Ply 0 of 3: Initial position", { exact: true })).toBeVisible();
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
    await user.click(flip);
    expect(screen.getByRole("group", { name: /ply 0, Black at the bottom/ })).toBeVisible();
    expect(screen.getByRole("link", { name: "Chess.com game" })).toHaveAttribute(
      "target",
      "_blank",
    );
    expect(lookup).toHaveBeenCalledWith(GAME_UUID, undefined, expect.any(AbortSignal));
  });

  it("resets the flipped orientation for reset and a newly loaded game", async () => {
    const lookup = vi
      .fn<GameLookup>()
      .mockResolvedValueOnce({
        status: "success",
        game: { ...VIEWER_GAME, initial_ply: 0 },
      })
      .mockResolvedValueOnce({
        status: "success",
        game: { ...VIEWER_GAME, initial_ply: 0 },
      });
    const user = userEvent.setup();
    renderViewer({ lookup });

    await fillAndSubmit(user);
    await screen.findByText("Ply 0 of 3");
    const flip = screen.getByRole("button", { name: "Flip" });
    await user.click(flip);
    expect(screen.getByRole("group", { name: /ply 0, Black at the bottom/ })).toBeVisible();

    await user.click(screen.getByRole("button", { name: "Load game" }));
    expect(await screen.findByRole("group", { name: /ply 0, White at the bottom/ })).toBeVisible();
    expect(lookup).toHaveBeenCalledTimes(2);

    await user.click(screen.getAllByRole("button", { name: "Reset" })[0]);
    expect(screen.getByRole("img", { name: BOARD_LABEL })).toBeVisible();
  });

  it("loads an explicit Ply and traverses in memory without changing the form or requesting again", async () => {
    const lookup = successfulLookup();
    const user = userEvent.setup();
    renderViewer({ lookup });

    await fillAndSubmit(user, GAME_UUID, "1");
    await screen.findByText("Ply 1 of 3");
    const next = screen.getByRole("button", { name: "Next" });
    const flip = screen.getByRole("button", { name: "Flip" });
    expect(screen.getByLabelText(/Ply/)).toHaveValue("1");

    await user.click(flip);
    expect(screen.getByRole("group", { name: /ply 1, Black at the bottom/ })).toBeVisible();
    expect(screen.getByText("Ply 1 of 3: e4", { exact: true })).toBeInTheDocument();

    await user.click(next);
    expect(screen.getByRole("group", { name: /ply 2, Black at the bottom/ })).toBeVisible();
    expect(screen.getByText("Ply 2 of 3")).toBeVisible();
    expect(screen.getByText("e5")).toBeVisible();
    expect(screen.getByText("Ply 2 of 3: e5", { exact: true })).toBeInTheDocument();
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
        return { status: "success", game: { ...VIEWER_GAME, initial_ply: initialPly ?? 0 } };
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
    await user.click(screen.getByRole("button", { name: "Flip" }));
    expect(screen.getByRole("group", { name: /ply 1, Black at the bottom/ })).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Load game" }));

    await screen.findByText("Loading the complete game...");
    expect(screen.getByText("Ply 1 of 3")).toBeVisible();
    expect(screen.getByRole("group", { name: /ply 1, Black at the bottom/ })).toBeVisible();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();

    resolveReplacement({ status: "game_unavailable" });
    expect(
      await screen.findByRole("heading", { name: "Game unavailable", level: 2 }),
    ).toBeVisible();
    expect(screen.getByText("Ply 1 of 3")).toBeVisible();
    expect(screen.getByRole("group", { name: /ply 1, Black at the bottom/ })).toBeVisible();
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

    resolvePending({ status: "success", game: VIEWER_GAME });
    await Promise.resolve();
    expect(screen.getAllByText("No game loaded")).toHaveLength(2);
    expect(screen.getByLabelText("Game UUID")).toHaveValue("");
  });

  it("renders unsafe source attribution as unavailable without rejecting the active game", async () => {
    const lookup = successfulLookup(UNSAFE_SOURCE_GAME);
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
      VIEWER_GAME.positions[0].fen,
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

  it("retries an observation only from the deliberate observation-retry action", async () => {
    const lookup = successfulLookup();
    const analysisClient = retryingAnalysisClient();
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={lookup} analysisClient={analysisClient} />);

    await fillAndSubmit(user);

    expect(await screen.findByText("Evaluation unavailable")).toBeVisible();
    expect(screen.getByRole("button", { name: "Retry observation" })).toBeVisible();
    expect(analysisClient.observe).toHaveBeenCalledOnce();
    expect(analysisClient.enqueue).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Retry observation" }));

    expect(await screen.findByText("Analysis available on request")).toBeVisible();
    expect(analysisClient.observe).toHaveBeenCalledTimes(2);
    expect(analysisClient.enqueue).not.toHaveBeenCalled();
  });

  it("keeps queue polling in the page-owned analysis workflow until completion", async () => {
    const lookup = successfulLookup();
    const analysisClient = pollingAnalysisClient();
    const user = userEvent.setup();
    render(
      <ViewerWorkspace
        lookup={lookup}
        analysisClient={analysisClient}
        analysisPollIntervalMs={1}
      />,
    );

    await fillAndSubmit(user);

    expect(await screen.findByText("Analysis complete")).toBeVisible();
    expect(analysisClient.observe).toHaveBeenCalledTimes(2);
    expect(analysisClient.status).toHaveBeenCalledTimes(2);
    expect(analysisClient.enqueue).not.toHaveBeenCalled();
  });

  it("routes a promotion candidate through the existing picker without changing FEN until selection", async () => {
    const user = userEvent.setup();
    renderViewer({
      lookup: successfulLookup(PROMOTION_GAME),
      analysisClient: completedAnalysisClient(["e7e8q"]),
    });

    await fillAndSubmit(user);
    const candidate = await screen.findByRole("button", { name: /1\. e8=Q/ });
    const originFen = PROMOTION_GAME.positions[0].fen;
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(originFen);

    await user.click(candidate);
    const queen = await screen.findByRole("button", { name: "Promote to queen" });
    await waitFor(() => expect(queen).toHaveFocus());
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(originFen);

    await user.keyboard("{Escape}");
    await waitFor(() => expect(candidate).toHaveFocus());
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(originFen);

    await user.click(candidate);
    await user.click(await screen.findByRole("button", { name: "Promote to queen" }));
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "k3Q3/8/8/8/8/8/8/4K3 b - - 0 1",
    );
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1. e8=Q+");
  });

  it("shares one completed observation with the panel and the beside-board eval bar", async () => {
    const lookup = successfulLookup();
    const analysisClient = completedAnalysisClient();
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={lookup} analysisClient={analysisClient} />);

    await fillAndSubmit(user);

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
    expect(disclosureContent).toContainElement(analysisStatus);
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

    const { container } = renderViewer({ lookup: successfulLookup() });
    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });
});
