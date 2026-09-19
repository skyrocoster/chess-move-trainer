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

function item(id: string, overrides: Partial<TrainingRequirementItemResponse> = {}) {
  return {
    fen: `fen-${id}`,
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

async function renderReady(
  api = createApi(),
  client?: ReturnType<typeof createTestQueryClient>,
) {
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
  it("shows catalogue loading and then exposes native labelled controls", async () => {    let resolveCatalogue!: (value: OpeningCatalogueSnapshotResult) => void;
    const catalogue = new Promise<OpeningCatalogueSnapshotResult>((resolve) => {
      resolveCatalogue = resolve;
    });
    const api: TrainerPracticeApi = {
      loadCatalogue: vi.fn(() => catalogue),
      loadRequirements: vi.fn().mockResolvedValue(successfulRequirements()),
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
    const api: TrainerPracticeApi = { loadCatalogue, loadRequirements: vi.fn() };
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
    await screen.findAllByText("fen-one");
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
    await screen.findByText("fen-one");
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
    await screen.findByText("fen-one");
    firstRender.unmount();

    const secondUser = userEvent.setup();
    renderPage(api, client);
    await screen.findByRole("combobox", { name: "Opening" });
    await chooseOpening(secondUser, /B10 Caro-Kann Defense/);
    await secondUser.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByText("fen-one");

    expect(api.loadCatalogue).toHaveBeenCalledTimes(1);
    expect(api.loadRequirements).toHaveBeenCalledTimes(1);
  });

  it("shows retrieval loading and the complete minimal response fields", async () => {
    let resolveRequirements!: (value: TrainingRequirementsResult) => void;
    const requirements = new Promise<TrainingRequirementsResult>((resolve) => {
      resolveRequirements = resolve;
    });
    const api: TrainerPracticeApi = {
      loadCatalogue: vi.fn().mockResolvedValue(successfulCatalogue()),
      loadRequirements: vi.fn(() => requirements),
    };
    const user = await renderReady(api);

    await chooseOpening(user, /B10 Caro-Kann Defense/);
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    expect(screen.getByRole("status")).toHaveTextContent("Loading training-required positions");

    resolveRequirements(
      successfulRequirements([
        item("complete", {
          trainer_color: "black",
          preferred_move_uci: "d2d4",
          training_updated_on: "2026-09-01",
          training_required: false,
        }),
      ]),
    );
    await screen.findByRole("heading", { name: "training-required positions" });

    for (const field of [
      "as_of",
      "page",
      "page_size",
      "total",
      "target_success_rate",
      "game_hit_weight",
      "game_miss_weight",
      "training_curve",
      "training_credit_half_life_days",
      "fen",
      "trainer_color",
      "preferred_move_uci",
      "encounters",
      "hits",
      "misses",
      "observed_success_rate",
      "game_balance",
      "effective_training_balance",
      "training_adjustment",
      "training_updated_on",
      "training_requirement",
      "training_required",
      "correct_answers_needed",
    ]) {
      expect(screen.getAllByText(field).length).toBeGreaterThan(0);
    }
    expect(screen.getByText("fen-complete")).toBeVisible();
    expect(screen.getByText("d2d4")).toBeVisible();
    expect(screen.getByText("2026-09-01")).toBeVisible();
    expect(screen.getByText("false")).toBeVisible();
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /board|session/i })).not.toBeInTheDocument();
  });

  it("shows a valid empty response with its metadata", async () => {
    const api = createApi(successfulRequirements([]));
    const user = await renderReady(api);

    await chooseOpening(user, /B10 Caro-Kann Defense/);
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    expect(
      await screen.findByText("No positions currently require training for these filters."),
    ).toBeVisible();
    expect(screen.getByText("0")).toBeVisible();
    expect(screen.queryByRole("list", { name: "training-required positions" })).not.toBeInTheDocument();
  });

  it("shows a catalogue error and can retry the catalogue request", async () => {
    const loadCatalogue = vi
      .fn()
      .mockResolvedValueOnce({ status: "catalogue_error" } as OpeningCatalogueSnapshotResult)
      .mockResolvedValueOnce(successfulCatalogue());
    const api: TrainerPracticeApi = {
      loadCatalogue,
      loadRequirements: vi.fn().mockResolvedValue(successfulRequirements()),
    };
    const user = userEvent.setup();
    renderPage(api);

    expect(await screen.findByRole("alert")).toHaveTextContent("Opening catalogue could not be loaded");
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
    };
    const user = await renderReady(api);

    await chooseOpening(user, /B10 Caro-Kann Defense/);
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByText("Training-required positions could not be loaded.");
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await screen.findByText("fen-one");

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
    };
    const user = await renderReady(api);

    await chooseOpening(user, /B10 Caro-Kann Defense/);
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    await user.click(screen.getByRole("radio", { name: "Black" }));
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    const firstSignal = loadRequirements.mock.calls[0]?.[1] as AbortSignal;
    expect(firstSignal.aborted).toBe(true);

    resolveSecond(successfulRequirements([item("newer")]));
    await screen.findByText("fen-newer");
    resolveFirst(successfulRequirements([item("older")]));
    await waitFor(() => expect(screen.queryByText("fen-older")).not.toBeInTheDocument());
    expect(screen.getByText("fen-newer")).toBeVisible();
  });

  it("aborts an active retrieval when the page unmounts", async () => {
    let resolveRequirements!: (value: TrainingRequirementsResult) => void;
    const pending = new Promise<TrainingRequirementsResult>((resolve) => {
      resolveRequirements = resolve;
    });
    const loadRequirements = vi.fn(() => pending);
    const api: TrainerPracticeApi = {
      loadCatalogue: vi.fn().mockResolvedValue(successfulCatalogue()),
      loadRequirements,
    };
    const user = userEvent.setup();
    const rendered = renderPage(api);
    await screen.findByRole("combobox", { name: "Opening" });
    await chooseOpening(user, /B10 Caro-Kann Defense/);
    await user.click(screen.getByRole("button", { name: "Find training positions" }));
    const signal = loadRequirements.mock.calls[0]?.[1] as AbortSignal;

    rendered.unmount();
    expect(signal.aborted).toBe(true);
    resolveRequirements(successfulRequirements());
  });
});
