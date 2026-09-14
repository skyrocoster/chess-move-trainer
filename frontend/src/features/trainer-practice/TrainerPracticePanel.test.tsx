import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

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
  type OpeningChoicesResult,
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

function successfulOpenings(): OpeningChoicesResult {
  return { status: "success", data: [OPENING] };
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
    loadOpenings: vi.fn().mockResolvedValue(successfulOpenings()),
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
  await screen.findByRole("option", { name: "Caro-Kann Defense (B10)" });
  return user;
}

afterEach(() => cleanup());

describe("TrainerPracticePage", () => {
  it("shows catalogue loading and then exposes native labelled controls", async () => {
    let resolveOpenings!: (value: OpeningChoicesResult) => void;
    const openings = new Promise<OpeningChoicesResult>((resolve) => {
      resolveOpenings = resolve;
    });
    const api: TrainerPracticeApi = {
      loadOpenings: vi.fn(() => openings),
      loadRequirements: vi.fn().mockResolvedValue(successfulRequirements()),
    };

    renderPage(api);
    expect(screen.getByRole("status")).toHaveTextContent("Loading opening catalogue");
    expect(screen.getByRole("button", { name: "Retrieve training positions" })).toBeDisabled();

    resolveOpenings(successfulOpenings());
    await screen.findByRole("option", { name: "Caro-Kann Defense (B10)" });
    expect(screen.getByLabelText("Opening")).toBeVisible();
    expect(screen.getByLabelText("Learner colour")).toBeVisible();
    expect(screen.getByLabelText("as_of")).toHaveValue(currentUtcDate());
  });

  it("waits for explicit submit and sends the selected catalogue key", async () => {
    const api = createApi();
    const user = await renderReady(api);
    const opening = screen.getByLabelText("Opening");
    const color = screen.getByLabelText("Learner colour");
    const asOf = screen.getByLabelText("as_of");

    await user.selectOptions(opening, OPENING_KEY);
    await user.selectOptions(color, "black");
    fireEvent.change(asOf, { target: { value: TODAY } });
    expect(api.loadRequirements).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Retrieve training positions" }));
    await waitFor(() => expect(api.loadRequirements).toHaveBeenCalledTimes(1));
    expect(api.loadRequirements).toHaveBeenCalledWith(
      { asOf: TODAY, openingKey: OPENING_KEY, trainerColor: "black" },
      expect.any(AbortSignal),
    );
  });

  it("reloads the catalogue only when its search is submitted", async () => {
    const loadOpenings = vi.fn().mockResolvedValue(successfulOpenings());
    const api: TrainerPracticeApi = {
      loadOpenings,
      loadRequirements: vi.fn().mockResolvedValue(successfulRequirements()),
    };
    const user = await renderReady(api);

    await user.type(screen.getByLabelText("Search openings"), "Caro-Kann Defense");
    expect(loadOpenings).toHaveBeenCalledTimes(1);

    await user.click(screen.getByRole("button", { name: "Search opening catalogue" }));
    await waitFor(() => expect(loadOpenings).toHaveBeenCalledTimes(2));
    expect(loadOpenings.mock.calls[1]).toEqual([expect.any(AbortSignal), "Caro-Kann Defense"]);
  });

  it("normalizes submitted search values so concurrent identical reads share one result", async () => {
    const loadOpenings = vi.fn().mockResolvedValue(successfulOpenings());
    const api: TrainerPracticeApi = {
      loadOpenings,
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

    await screen.findAllByRole("option", { name: "Caro-Kann Defense (B10)" });
    expect(loadOpenings).toHaveBeenCalledTimes(1);

    const searches = screen.getAllByRole("searchbox");
    await user.type(searches[0]!, " Caro-Kann Defense ");
    await user.type(searches[1]!, "Caro-Kann Defense");
    const searchButtons = screen.getAllByRole("button", { name: "Search opening catalogue" });
    await user.click(searchButtons[0]!);
    await user.click(searchButtons[1]!);

    await waitFor(() => expect(loadOpenings).toHaveBeenCalledTimes(2));
    expect(loadOpenings.mock.calls[1]).toEqual([
      expect.any(AbortSignal),
      "Caro-Kann Defense",
    ]);
  });

  it("deduplicates concurrent catalogue and complete training reads", async () => {
    const api = createApi();
    const client = createTestQueryClient();
    const user = userEvent.setup();
    render(
      <QueryClientTestProvider client={client}>
        <TrainerPracticePage api={api} />
        <TrainerPracticePage api={api} />
      </QueryClientTestProvider>,
    );

    await screen.findAllByRole("option", { name: "Caro-Kann Defense (B10)" });
    const retrieveButtons = screen.getAllByRole("button", {
      name: "Retrieve training positions",
    });
    await user.click(retrieveButtons[0]!);
    await user.click(retrieveButtons[1]!);

    await screen.findAllByText("fen-one");
    expect(api.loadOpenings).toHaveBeenCalledTimes(1);
    expect(api.loadRequirements).toHaveBeenCalledTimes(1);
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

    await screen.findAllByRole("option", { name: "Caro-Kann Defense (B10)" });
    const colours = screen
      .getAllByRole("combobox")
      .filter((element) => element.id === "trainer-practice-color");
    await user.selectOptions(colours[0]!, "white");
    await user.selectOptions(colours[1]!, "black");
    const retrieveButtons = screen.getAllByRole("button", {
      name: "Retrieve training positions",
    });
    await user.click(retrieveButtons[0]!);
    await user.click(retrieveButtons[1]!);

    await waitFor(() => expect(api.loadRequirements).toHaveBeenCalledTimes(2));
  });

  it("reuses fresh assembled catalogue and training results after remounting", async () => {
    const api = createApi();
    const client = createTestQueryClient();
    const firstUser = userEvent.setup();
    const firstRender = renderPage(api, client);

    await screen.findByRole("option", { name: "Caro-Kann Defense (B10)" });
    await firstUser.click(screen.getByRole("button", { name: "Retrieve training positions" }));
    await screen.findByText("fen-one");
    firstRender.unmount();

    const secondUser = userEvent.setup();
    renderPage(api, client);
    await screen.findByRole("option", { name: "Caro-Kann Defense (B10)" });
    await secondUser.click(screen.getByRole("button", { name: "Retrieve training positions" }));
    await screen.findByText("fen-one");

    expect(api.loadOpenings).toHaveBeenCalledTimes(1);
    expect(api.loadRequirements).toHaveBeenCalledTimes(1);
  });

  it("shows retrieval loading and the complete minimal response fields", async () => {
    let resolveRequirements!: (value: TrainingRequirementsResult) => void;
    const requirements = new Promise<TrainingRequirementsResult>((resolve) => {
      resolveRequirements = resolve;
    });
    const api: TrainerPracticeApi = {
      loadOpenings: vi.fn().mockResolvedValue(successfulOpenings()),
      loadRequirements: vi.fn(() => requirements),
    };
    const user = await renderReady(api);

    await user.click(screen.getByRole("button", { name: "Retrieve training positions" }));
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
    const user = await renderReady(createApi(successfulRequirements([])));

    await user.click(screen.getByRole("button", { name: "Retrieve training positions" }));
    expect(
      await screen.findByText("No positions currently require training for these filters."),
    ).toBeVisible();
    expect(screen.getByText("0")).toBeVisible();
    expect(screen.queryByRole("list", { name: "training-required positions" })).not.toBeInTheDocument();
  });

  it("shows a catalogue error and can retry the catalogue request", async () => {
    const loadOpenings = vi
      .fn()
      .mockResolvedValueOnce({ status: "catalogue_error" } as OpeningChoicesResult)
      .mockResolvedValueOnce(successfulOpenings());
    const api: TrainerPracticeApi = {
      loadOpenings,
      loadRequirements: vi.fn().mockResolvedValue(successfulRequirements()),
    };
    const user = userEvent.setup();
    renderPage(api);

    expect(await screen.findByRole("alert")).toHaveTextContent("Opening catalogue could not be loaded");
    await user.click(screen.getByRole("button", { name: "Retry opening catalogue" }));
    await screen.findByRole("option", { name: "Caro-Kann Defense (B10)" });
    expect(loadOpenings).toHaveBeenCalledTimes(2);
  });

  it.each([
    ["invalid_date", "The selected as_of date is not valid."],
    ["stale_date", "Training requirements changed after this date."],
    ["retrieval_error", "Training-required positions could not be loaded."],
  ] as const)("shows the safe %s response state", async (status, message) => {
    const user = await renderReady(createApi({ status }));

    await user.click(screen.getByRole("button", { name: "Retrieve training positions" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(message);
  });

  it("can retry a failed training query without caching the error as data", async () => {
    const loadRequirements = vi
      .fn()
      .mockResolvedValueOnce({ status: "retrieval_error" } as TrainingRequirementsResult)
      .mockResolvedValueOnce(successfulRequirements());
    const api: TrainerPracticeApi = {
      loadOpenings: vi.fn().mockResolvedValue(successfulOpenings()),
      loadRequirements,
    };
    const user = await renderReady(api);

    await user.click(screen.getByRole("button", { name: "Retrieve training positions" }));
    await screen.findByText("Training-required positions could not be loaded.");
    await user.click(screen.getByRole("button", { name: "Retrieve training positions" }));
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
      loadOpenings: vi.fn().mockResolvedValue(successfulOpenings()),
      loadRequirements,
    };
    const user = await renderReady(api);

    await user.click(screen.getByRole("button", { name: "Retrieve training positions" }));
    const asOf = screen.getByLabelText("as_of");
    fireEvent.change(asOf, { target: { value: "2026-09-13" } });
    await user.click(screen.getByRole("button", { name: "Retrieve training positions" }));
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
      loadOpenings: vi.fn().mockResolvedValue(successfulOpenings()),
      loadRequirements,
    };
    const user = userEvent.setup();
    const rendered = renderPage(api);
    await screen.findByRole("option", { name: "Caro-Kann Defense (B10)" });
    await user.click(screen.getByRole("button", { name: "Retrieve training positions" }));
    const signal = loadRequirements.mock.calls[0]?.[1] as AbortSignal;

    rendered.unmount();
    expect(signal.aborted).toBe(true);
    resolveRequirements(successfulRequirements());
  });
});
