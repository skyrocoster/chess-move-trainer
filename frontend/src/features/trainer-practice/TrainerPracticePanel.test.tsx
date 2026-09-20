import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type {
  OpeningCatalogueItemResponse,
  TrainingRequirementItemResponse,
  TrainingRequirementResponse,
} from "../../api/client";
import {
  createTestQueryClient,
  QueryClientTestProvider,
} from "../../test-utils/QueryClientTestProvider";
import { TrainerPracticePage, type TrainerPracticeApi } from "./TrainerPracticePage";
import {
  currentUtcDate,
  type OpeningCatalogueSnapshotResult,
  type TrainingRequirementsResult,
} from "./trainerPracticeApi";

vi.mock("react-chessboard", () => ({
  defaultPieces: Object.fromEntries(
    ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"].map((pieceType) => [
      pieceType,
      () => <svg data-default-piece={pieceType} />,
    ]),
  ),
  Chessboard: ({
    options,
  }: {
    options: {
      position: string;
      onPieceDrop: (args: { sourceSquare: string; targetSquare: string }) => boolean;
    };
  }) => (
    <div data-testid="mock-chessboard" data-position={options.position}>
      <button
        type="button"
        data-testid="move-e2-e4"
        onClick={() => options.onPieceDrop({ sourceSquare: "e2", targetSquare: "e4" })}
      >
        Play e4
      </button>
      <button
        type="button"
        data-testid="move-d2-d4"
        onClick={() => options.onPieceDrop({ sourceSquare: "d2", targetSquare: "d4" })}
      >
        Play d4
      </button>
      <button
        type="button"
        data-testid="move-e2-e5"
        onClick={() => options.onPieceDrop({ sourceSquare: "e2", targetSquare: "e5" })}
      >
        Try illegal e5
      </button>
    </div>
  ),
}));

const TODAY = "2026-09-14";
const OPENING_KEY = "B10:Caro-Kann Defense";
const OPENING: OpeningCatalogueItemResponse = {
  key: OPENING_KEY,
  eco: "B10",
  name: "Caro-Kann Defense",
  route_count: 2,
  games_reached: 12,
  games_deepest: 9,
};
const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1";

function item(id: string, overrides: Partial<TrainingRequirementItemResponse> = {}) {
  return {
    fen: id === "newer" ? AFTER_E4_FEN : STARTING_FEN,
    trainer_color: "white" as const,
    preferred_move_uci: "e2e4",
    encounters: 4,
    hits: 1,
    misses: 3,
    observed_success_rate: 0.25,
    game_balance: -0.5,
    effective_training_balance: -0.75,
    training_adjustment: -0.25,
    training_updated_on: null,
    training_requirement: -0.75,
    training_required: true,
    correct_answers_needed: 2,
    ...overrides,
  } satisfies TrainingRequirementItemResponse;
}

function page(items: TrainingRequirementItemResponse[], total = items.length) {
  return {
    as_of: TODAY,
    scoring_policy: {
      target_success_rate: 0.8,
      game_hit_weight: 1,
      game_miss_weight: 1,
      training_curve: "linear",
      training_credit_half_life_days: 30,
    },
    items,
    page: 1,
    page_size: 100,
    total,
  } satisfies TrainingRequirementResponse;
}

function successfulCatalogue(): OpeningCatalogueSnapshotResult {
  return { status: "success", data: [OPENING], catalogueVersion: "opaque-v1" };
}

function successfulRequirements(
  items: TrainingRequirementItemResponse[] = [item("one")],
): TrainingRequirementsResult {
  return { status: "success", data: page(items) };
}

function createApi(
  requirements: TrainingRequirementsResult = successfulRequirements(),
): TrainerPracticeApi {
  return {
    loadCatalogue: vi.fn().mockResolvedValue(successfulCatalogue()),
    loadRequirements: vi.fn().mockResolvedValue(requirements),
    submitAnswer: vi.fn<TrainerPracticeApi["submitAnswer"]>(async (input) => ({
      status: "success",
      data: {
        as_of: input.asOf,
        correct: input.playedMoveUci === "e2e4",
        item: item("answered", {
          fen: input.fen,
          trainer_color: input.trainerColor,
          training_requirement: 0,
          training_required: false,
          correct_answers_needed: 0,
        }),
      },
    })),
  };
}

function renderPage(
  api: TrainerPracticeApi,
  client: ReturnType<typeof createTestQueryClient> = createTestQueryClient(),
) {
  return render(
    <QueryClientTestProvider client={client}>
      <TrainerPracticePage api={api} />
    </QueryClientTestProvider>,
  );
}

async function renderReady(api = createApi(), client?: ReturnType<typeof createTestQueryClient>) {
  const user = userEvent.setup();
  renderPage(api, client);
  await screen.findByRole("combobox", { name: "Opening" });
  await waitFor(() => expect(api.loadCatalogue).toHaveBeenCalledTimes(1));
  return user;
}

async function chooseOpening(user: ReturnType<typeof userEvent.setup>, name: RegExp | string) {
  await user.click(screen.getByRole("combobox", { name: "Opening" }));
  await user.click(await screen.findByRole("option", { name }));
}

beforeEach(() => {
  vi.stubGlobal("PointerEvent", MouseEvent);
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("TrainerPracticePage", () => {
  it("shows catalogue loading and then exposes native labelled controls", async () => {
    let resolveCatalogue!: (value: OpeningCatalogueSnapshotResult) => void;
    const catalogue = new Promise<OpeningCatalogueSnapshotResult>((resolve) => {
      resolveCatalogue = resolve;
    });
    const api: TrainerPracticeApi = {
      loadCatalogue: vi.fn(() => catalogue),
      loadRequirements: vi.fn().mockResolvedValue(successfulRequirements()),
      submitAnswer: vi.fn(),
    };

    renderPage(api);
    expect(screen.getByRole("status")).toHaveTextContent("Loading opening catalogue");
    expect(screen.getByRole("button", { name: "Find training positions" })).toBeDisabled();

    resolveCatalogue(successfulCatalogue());
    await screen.findByRole("combobox", { name: "Opening" });
    expect(screen.getByRole("combobox", { name: "Opening" })).toBeVisible();
    expect(screen.getByRole("radio", { name: "All colours" })).toBeVisible();
    expect(
      screen.getByRole("button", { name: new RegExp(`as_of: ${currentUtcDate()}`) }),
    ).toBeVisible();
  });

  it("waits for explicit submit and sends the selected catalogue key", async () => {
    const api = createApi();
    const user = await renderReady(api);

    await chooseOpening(user, /B10 Caro-Kann Defense/);
    await user.click(screen.getByRole("radio", { name: "Black" }));
    expect(api.loadRequirements).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await waitFor(() => expect(api.loadRequirements).toHaveBeenCalledTimes(1));
    expect(api.loadRequirements).toHaveBeenCalledWith(
      { asOf: currentUtcDate(), openingKey: OPENING_KEY, trainerColor: "black" },
      expect.any(AbortSignal),
    );
  });

  it("sends the calendar-selected date as YYYY-MM-DD", async () => {
    const api = createApi();
    const user = await renderReady(api);
    await chooseOpening(user, /B10 Caro-Kann Defense/);

    const now = new Date();
    const year = now.getUTCFullYear();
    const month = now.getUTCMonth();
    const monthName = new Intl.DateTimeFormat("en-US", {
      month: "long",
      timeZone: "UTC",
    }).format(new Date(Date.UTC(year, month, 1)));
    const expectedAsOf = `${String(year).padStart(4, "0")}-${String(month + 1).padStart(2, "0")}-01`;

    await user.click(screen.getByRole("button", { name: /as_of:/ }));
    const dialog = await screen.findByRole("dialog", { name: "as_of" });
    await user.click(
      within(dialog).getByRole("button", { name: new RegExp(`${monthName} 1st, ${year}`) }),
    );

    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await waitFor(() => expect(api.loadRequirements).toHaveBeenCalledTimes(1));
    expect(api.loadRequirements).toHaveBeenCalledWith(
      { asOf: expectedAsOf, openingKey: OPENING_KEY, trainerColor: null },
      expect.any(AbortSignal),
    );
  });

  it("filters the complete catalogue locally without a request per keystroke", async () => {
    const loadCatalogue = vi.fn().mockResolvedValue(successfulCatalogue());
    const api: TrainerPracticeApi = {
      loadCatalogue,
      loadRequirements: vi.fn(),
      submitAnswer: vi.fn(),
    };
    const user = await renderReady(api);

    const opening = screen.getByRole("combobox", { name: "Opening" });
    await user.click(opening);
    await user.type(opening, "Caro-Kann");

    expect(await screen.findByRole("option", { name: /B10 Caro-Kann Defense/ })).toBeVisible();
    await user.clear(opening);
    await user.type(opening, OPENING_KEY);
    expect(await screen.findByRole("option", { name: /B10 Caro-Kann Defense/ })).toBeVisible();
    expect(loadCatalogue).toHaveBeenCalledTimes(1);
    expect(api.loadRequirements).not.toHaveBeenCalled();
  });

  it("preserves committed focus and Escape semantics while clear and typing uncommit", async () => {
    const user = await renderReady();
    await chooseOpening(user, /B10 Caro-Kann Defense/);
    const opening = screen.getByRole("combobox", { name: "Opening" });
    const findButton = screen.getByRole("button", { name: "Find training positions" });

    opening.blur();
    await user.click(opening);
    expect(opening).toHaveValue("Caro-Kann Defense");
    expect((opening as HTMLInputElement).selectionStart).toBe(0);
    expect((opening as HTMLInputElement).selectionEnd).toBe("Caro-Kann Defense".length);
    await user.keyboard("{Escape}");
    expect(opening).toHaveValue("Caro-Kann Defense");
    expect(findButton).toBeEnabled();

    await user.click(screen.getByRole("button", { name: "Clear selection" }));
    expect(opening).toHaveValue("");
    expect(findButton).toBeDisabled();

    await chooseOpening(user, /B10 Caro-Kann Defense/);
    await user.click(opening);
    await user.type(opening, "Italian");
    expect(opening).toHaveValue("Italian");
    expect(findButton).toBeDisabled();
  });

  it("deduplicates concurrent complete catalogue and training reads", async () => {
    const loadCatalogue = vi.fn().mockResolvedValue(successfulCatalogue());
    const api: TrainerPracticeApi = {
      loadCatalogue,
      loadRequirements: vi.fn().mockResolvedValue(successfulRequirements()),
      submitAnswer: vi.fn(),
    };
    const client = createTestQueryClient();
    const user = userEvent.setup();
    render(
      <QueryClientTestProvider client={client}>
        <TrainerPracticePage api={api} />
        <TrainerPracticePage api={api} />
      </QueryClientTestProvider>,
    );

    await screen.findAllByRole("combobox", { name: "Opening" });
    expect(loadCatalogue).toHaveBeenCalledTimes(1);

    const openingComboboxes = screen.getAllByRole("combobox", { name: "Opening" });
    await user.click(openingComboboxes[0]!);
    await user.click(screen.getByRole("option", { name: "All openings" }));
    await user.click(openingComboboxes[1]!);
    await user.click(screen.getByRole("option", { name: "All openings" }));

    const retrieveButtons = screen.getAllByRole("button", {
      name: "Find training positions",
    });
    await user.click(retrieveButtons[0]!);
    await user.click(retrieveButtons[1]!);
    await screen.findAllByRole("heading", { name: "Position 1 of 1" });
    expect(loadCatalogue).toHaveBeenCalledTimes(1);
    expect(api.loadRequirements).toHaveBeenCalledTimes(1);
  });

  it("keeps All openings explicit and omits opening filters from the request", async () => {
    const api = createApi();
    const client = createTestQueryClient();
    const user = userEvent.setup();
    renderPage(api, client);
    await screen.findByRole("combobox", { name: "Opening" });
    await chooseOpening(user, "All openings");
    expect(screen.getByRole("combobox", { name: "Opening" })).toHaveValue("All openings");
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByRole("heading", { name: "Position 1 of 1" });
    expect(api.loadRequirements).toHaveBeenCalledWith(
      { asOf: currentUtcDate(), openingKey: null, trainerColor: null },
      expect.any(AbortSignal),
    );
  });

  it("keeps complete training results distinct when a filter changes", async () => {
    const api = createApi();
    const client = createTestQueryClient();
    const user = userEvent.setup();
    render(
      <QueryClientTestProvider client={client}>
        <TrainerPracticePage api={api} />
        <TrainerPracticePage api={api} />
      </QueryClientTestProvider>,
    );

    await screen.findAllByRole("combobox", { name: "Opening" });
    const whiteColours = screen.getAllByRole("radio", { name: "White" });
    const blackColours = screen.getAllByRole("radio", { name: "Black" });
    await user.click(whiteColours[0]!);
    await user.click(blackColours[1]!);
    const openingComboboxes = screen.getAllByRole("combobox", { name: "Opening" });
    await user.click(openingComboboxes[0]!);
    await user.click(screen.getByRole("option", { name: "All openings" }));
    await user.click(openingComboboxes[1]!);
    await user.click(screen.getByRole("option", { name: "All openings" }));
    const retrieveButtons = screen.getAllByRole("button", { name: "Find training positions" });
    await user.click(retrieveButtons[0]!);
    await user.click(retrieveButtons[1]!);

    await waitFor(() => expect(api.loadRequirements).toHaveBeenCalledTimes(2));
  });

  it("reuses fresh assembled catalogue and training results after remounting", async () => {
    const api = createApi();
    const client = createTestQueryClient();
    const firstUser = userEvent.setup();
    const firstRender = renderPage(api, client);

    await screen.findByRole("combobox", { name: "Opening" });
    await chooseOpening(firstUser, /B10 Caro-Kann Defense/);
    await firstUser.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByRole("heading", { name: "Position 1 of 1" });
    firstRender.unmount();

    const secondUser = userEvent.setup();
    renderPage(api, client);
    await screen.findByRole("combobox", { name: "Opening" });
    await chooseOpening(secondUser, /B10 Caro-Kann Defense/);
    await secondUser.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByRole("heading", { name: "Position 1 of 1" });

    expect(api.loadCatalogue).toHaveBeenCalledTimes(1);
    expect(api.loadRequirements).toHaveBeenCalledTimes(1);
  });

  it("starts a board session and keeps the saved move hidden until the answer is judged", async () => {
    let resolveRequirements!: (value: TrainingRequirementsResult) => void;
    const requirements = new Promise<TrainingRequirementsResult>((resolve) => {
      resolveRequirements = resolve;
    });
    const api: TrainerPracticeApi = {
      loadCatalogue: vi.fn().mockResolvedValue(successfulCatalogue()),
      loadRequirements: vi.fn(() => requirements),
      submitAnswer: vi.fn().mockResolvedValue({
        status: "success",
        data: {
          as_of: TODAY,
          correct: true,
          item: item("complete", {
            preferred_move_uci: "d2d4",
            training_requirement: 0,
            training_required: false,
            correct_answers_needed: 0,
          }),
        },
      }),
    };
    const user = await renderReady(api);

    await chooseOpening(user, /B10 Caro-Kann Defense/);
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    expect(screen.getByRole("status")).toHaveTextContent("Loading training-required positions");

    resolveRequirements(
      successfulRequirements([
        item("complete", {
          preferred_move_uci: "d2d4",
          training_updated_on: "2026-09-01",
          training_required: false,
        }),
      ]),
    );
    await screen.findByRole("heading", { name: "Position 1 of 1" });
    expect(screen.getByRole("group", { name: "Training position 1 of 1" })).toBeVisible();
    expect(screen.getByRole("progressbar", { name: "Session progress" })).toHaveAttribute(
      "aria-valuenow",
      "0",
    );
    expect(screen.queryByText("d2d4", { exact: false })).not.toBeInTheDocument();

    await user.click(screen.getByTestId("move-d2-d4"));

    expect(await screen.findByText("Saved move found")).toBeVisible();
    expect(api.submitAnswer).toHaveBeenCalledWith(
      {
        fen: STARTING_FEN,
        trainerColor: "white",
        asOf: TODAY,
        playedMoveUci: "d2d4",
      },
      expect.any(AbortSignal),
    );
    expect(screen.getAllByText("d2d4", { exact: false })).toHaveLength(2);

    await user.click(screen.getByRole("button", { name: "Continue" }));
    expect(screen.getByRole("heading", { name: "Practice recorded" })).toBeVisible();

    await user.click(screen.getByRole("button", { name: "Practice updated set" }));
    expect(await screen.findByRole("heading", { name: "Position 1 of 1" })).toBeVisible();
    expect(api.loadRequirements).toHaveBeenCalledTimes(2);
  });

  it("keeps illegal input in the open position without submitting an answer", async () => {
    const api = createApi();
    const user = await renderReady(api);
    await chooseOpening(user, "All openings");
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByRole("heading", { name: "Position 1 of 1" });

    await user.click(screen.getByTestId("move-e2-e5"));

    expect(screen.getByText("Move rejected because it is illegal.")).toBeVisible();
    expect(screen.getByTestId("interactive-board")).toHaveAttribute("data-locked", "false");
    expect(api.submitAnswer).not.toHaveBeenCalled();
  });

  it("reveals a saved move for review without changing the training score", async () => {
    const api = createApi();
    const user = await renderReady(api);
    await chooseOpening(user, "All openings");
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByRole("heading", { name: "Position 1 of 1" });

    await user.click(screen.getByRole("button", { name: "Show saved move" }));

    expect(screen.getByText("Saved move revealed")).toBeVisible();
    expect(screen.getByText("e2e4", { exact: false })).toBeVisible();
    expect(api.submitAnswer).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Continue" }));
    expect(screen.getByText("Saved moves reviewed").nextElementSibling).toHaveTextContent("1");
  });

  it("starts a fresh session when returning to a cached filter", async () => {
    const api = createApi();
    const user = await renderReady(api);
    await chooseOpening(user, "All openings");
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByRole("heading", { name: "Position 1 of 1" });

    await user.click(screen.getByRole("radio", { name: "White" }));
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await waitFor(() => expect(api.loadRequirements).toHaveBeenCalledTimes(2));
    expect(screen.getByText("All openings · White repertoire", { exact: false })).toBeVisible();

    await user.click(screen.getByTestId("move-e2-e4"));
    expect(await screen.findByText("Saved move found")).toBeVisible();

    await user.click(screen.getByRole("radio", { name: "All colours" }));
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await waitFor(() => expect(api.loadRequirements).toHaveBeenCalledTimes(3));

    expect(screen.getByText("Find the move you saved")).toBeVisible();
    expect(screen.queryByText("Saved move found")).not.toBeInTheDocument();
    expect(screen.getByTestId("interactive-board")).toHaveAttribute("data-locked", "false");
  });

  it("records an incorrect legal move once and shows the saved repertoire move", async () => {
    const api = createApi();
    const user = await renderReady(api);
    await chooseOpening(user, "All openings");
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByRole("heading", { name: "Position 1 of 1" });

    await user.click(screen.getByTestId("move-d2-d4"));

    expect(await screen.findByText("Different from your saved move")).toBeVisible();
    expect(screen.getByText(/Your saved move is e4\./)).toBeVisible();
    expect(api.submitAnswer).toHaveBeenCalledTimes(1);
  });

  it("does not automatically retry an answer whose response is uncertain", async () => {
    const api = createApi();
    api.submitAnswer = vi.fn().mockResolvedValue({ status: "submission_error" });
    const user = await renderReady(api);
    await chooseOpening(user, "All openings");
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByRole("heading", { name: "Position 1 of 1" });

    await user.click(screen.getByTestId("move-e2-e4"));

    expect(await screen.findByText("Answer not confirmed")).toBeVisible();
    expect(screen.getByText(/will not be sent again automatically/)).toBeVisible();
    await waitFor(() => expect(api.submitAnswer).toHaveBeenCalledTimes(1));
  });

  it("shows a valid empty response as a directed empty state", async () => {
    const api = createApi(successfulRequirements([]));
    const user = await renderReady(api);

    await chooseOpening(user, /B10 Caro-Kann Defense/);
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    expect(
      await screen.findByText("No positions currently require training for these filters."),
    ).toBeVisible();
    expect(screen.getByRole("heading", { name: "Nothing to practise right now" })).toBeVisible();
    expect(screen.queryByRole("group", { name: /Training position/ })).not.toBeInTheDocument();
  });

  it("shows a catalogue error and can retry the catalogue request", async () => {
    const loadCatalogue = vi
      .fn()
      .mockResolvedValueOnce({ status: "catalogue_error" } as OpeningCatalogueSnapshotResult)
      .mockResolvedValueOnce(successfulCatalogue());
    const api: TrainerPracticeApi = {
      loadCatalogue,
      loadRequirements: vi.fn().mockResolvedValue(successfulRequirements()),
      submitAnswer: vi.fn(),
    };
    const user = userEvent.setup();
    renderPage(api);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Opening catalogue could not be loaded",
    );
    await user.click(screen.getByRole("button", { name: "Retry opening catalogue" }));
    await screen.findByRole("combobox", { name: "Opening" });
    expect(loadCatalogue).toHaveBeenCalledTimes(2);
  });

  it.each([
    ["invalid_date", "The selected as_of date is not valid."],
    ["stale_date", "Training requirements changed after this date."],
    ["retrieval_error", "Training-required positions could not be loaded."],
  ] as const)("shows the safe %s response state", async (status, message) => {
    const api = createApi({ status });
    const user = await renderReady(api);
    await chooseOpening(user, /B10 Caro-Kann Defense/);

    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(message);
  });

  it("can retry a failed training query without caching the error as data", async () => {
    const loadRequirements = vi
      .fn()
      .mockResolvedValueOnce({ status: "retrieval_error" } as TrainingRequirementsResult)
      .mockResolvedValueOnce(successfulRequirements());
    const api: TrainerPracticeApi = {
      loadCatalogue: vi.fn().mockResolvedValue(successfulCatalogue()),
      loadRequirements,
      submitAnswer: vi.fn(),
    };
    const user = await renderReady(api);

    await chooseOpening(user, /B10 Caro-Kann Defense/);
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByText("Training-required positions could not be loaded.");
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByRole("heading", { name: "Position 1 of 1" });

    expect(loadRequirements).toHaveBeenCalledTimes(2);
  });

  it("aborts the old request and ignores its late result after a newer submit", async () => {
    let resolveFirst!: (value: TrainingRequirementsResult) => void;
    let resolveSecond!: (value: TrainingRequirementsResult) => void;
    const first = new Promise<TrainingRequirementsResult>((resolve) => {
      resolveFirst = resolve;
    });
    const second = new Promise<TrainingRequirementsResult>((resolve) => {
      resolveSecond = resolve;
    });
    const loadRequirements = vi
      .fn()
      .mockImplementationOnce(() => first)
      .mockImplementationOnce(() => second);
    const api: TrainerPracticeApi = {
      loadCatalogue: vi.fn().mockResolvedValue(successfulCatalogue()),
      loadRequirements,
      submitAnswer: vi.fn(),
    };
    const user = await renderReady(api);

    await chooseOpening(user, /B10 Caro-Kann Defense/);
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await user.click(screen.getByRole("radio", { name: "Black" }));
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    const firstSignal = loadRequirements.mock.calls[0]?.[1] as AbortSignal;
    expect(firstSignal.aborted).toBe(true);

    resolveSecond(successfulRequirements([item("newer", { preferred_move_uci: "e7e5" })]));
    await waitFor(() =>
      expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN),
    );
    resolveFirst(successfulRequirements([item("older")]));
    await waitFor(() =>
      expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN),
    );
  });

  it("aborts an active retrieval when the page unmounts", async () => {
    let resolveRequirements!: (value: TrainingRequirementsResult) => void;
    const pending = new Promise<TrainingRequirementsResult>((resolve) => {
      resolveRequirements = resolve;
    });
    const loadRequirements = vi.fn<TrainerPracticeApi["loadRequirements"]>(() => pending);
    const api: TrainerPracticeApi = {
      loadCatalogue: vi.fn().mockResolvedValue(successfulCatalogue()),
      loadRequirements,
      submitAnswer: vi.fn(),
    };
    const user = userEvent.setup();
    const rendered = renderPage(api);
    await screen.findByRole("combobox", { name: "Opening" });
    await chooseOpening(user, /B10 Caro-Kann Defense/);
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    const signal = loadRequirements.mock.calls[0]?.[1];

    rendered.unmount();
    expect(signal?.aborted).toBe(true);
    resolveRequirements(successfulRequirements());
  });
});
