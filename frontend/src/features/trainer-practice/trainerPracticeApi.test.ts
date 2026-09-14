import { afterEach, describe, expect, it, vi } from "vitest";

import { getOpenings, getPositionTrainingRequirements } from "../../api/client";
import type {
  OpeningCatalogueItemResponse,
  TrainingRequirementItemResponse,
  TrainingRequirementResponse,
} from "../../api/client";
import {
  buildTrainingRequirementsQuery,
  currentUtcDate,
  fetchOpeningChoices,
  fetchTrainingRequirements,
  isValidAsOf,
  type TrainerPracticeFilters,
} from "./trainerPracticeApi";

vi.mock("../../api/client", () => ({
  getOpenings: vi.fn(),
  getPositionTrainingRequirements: vi.fn(),
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

function page(pageNumber: number, total: number, items: TrainingRequirementItemResponse[]) {
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
    page: pageNumber,
    page_size: 100,
    total,
  } satisfies TrainingRequirementResponse;
}

const selectedFilters: TrainerPracticeFilters = {
  asOf: TODAY,
  openingKey: OPENING_KEY,
  trainerColor: "black",
};

afterEach(() => vi.clearAllMocks());

describe("fetchOpeningChoices", () => {
  it("loads catalogue choices with the existing sorted catalogue query", async () => {
    vi.mocked(getOpenings).mockResolvedValue({
      data: {
        has_next: false,
        items: [OPENING],
        page: 1,
        page_size: 100,
        total: 1,
        total_pages: 1,
      },
    } as never);
    const controller = new AbortController();

    await expect(fetchOpeningChoices(controller.signal)).resolves.toEqual({
      status: "success",
      data: [OPENING],
    });
    expect(getOpenings).toHaveBeenCalledWith({
      query: { page: 1, page_size: 100, sort: "name_asc" },
      signal: controller.signal,
    });
  });

  it("accumulates all catalogue pages in order", async () => {
    const secondOpening = { ...OPENING, key: "B11:Caro-Kann Defense: Main Line" };
    vi.mocked(getOpenings)
      .mockResolvedValueOnce({
        data: {
          has_next: true,
          items: [OPENING],
          page: 1,
          page_size: 100,
          total: 2,
          total_pages: 2,
        },
      } as never)
      .mockResolvedValueOnce({
        data: {
          has_next: false,
          items: [secondOpening],
          page: 2,
          page_size: 100,
          total: 2,
          total_pages: 2,
        },
      } as never);

    await expect(fetchOpeningChoices(undefined, "Caro-Kann")).resolves.toEqual({
      status: "success",
      data: [OPENING, secondOpening],
    });
    expect(vi.mocked(getOpenings).mock.calls.map(([request]) => request)).toEqual([
      {
        query: { page: 1, page_size: 100, sort: "name_asc", search: "Caro-Kann" },
        signal: undefined,
      },
      {
        query: { page: 2, page_size: 100, sort: "name_asc", search: "Caro-Kann" },
        signal: undefined,
      },
    ]);
  });

  it("maps catalogue network and typed failures to the safe catalogue error", async () => {
    vi.mocked(getOpenings).mockRejectedValueOnce(new Error("offline"));
    await expect(fetchOpeningChoices()).resolves.toEqual({ status: "catalogue_error" });

    vi.mocked(getOpenings).mockResolvedValueOnce({
      error: { code: "openings_unavailable", message: "safe detail" },
      response: { status: 503 },
    } as never);
    await expect(fetchOpeningChoices()).resolves.toEqual({ status: "catalogue_error" });
  });
});

describe("buildTrainingRequirementsQuery", () => {
  it("intersects the selected opening and colour with fixed training filters", () => {
    expect(buildTrainingRequirementsQuery(selectedFilters, 2)).toEqual({
      as_of: TODAY,
      training_requirement_lt: 0,
      trainer_color: "black",
      opening_key: OPENING_KEY,
      opening_match: "reached",
      page: 2,
      page_size: 100,
    });
  });

  it("omits optional filters for all openings and all colours", () => {
    expect(
      buildTrainingRequirementsQuery(
        { asOf: TODAY, openingKey: null, trainerColor: null },
        1,
      ),
    ).toEqual({
      as_of: TODAY,
      training_requirement_lt: 0,
      page: 1,
      page_size: 100,
    });
  });
});

describe("date helpers", () => {
  it("uses UTC for the default date and rejects impossible dates", () => {
    expect(currentUtcDate(new Date("2026-09-14T23:59:59.999Z"))).toBe(TODAY);
    expect(isValidAsOf("2024-02-29")).toBe(true);
    expect(isValidAsOf("2025-02-29")).toBe(false);
    expect(isValidAsOf("2026-9-14")).toBe(false);
  });
});

describe("fetchTrainingRequirements", () => {
  it("sends the generated operation with the exact selected key and filters", async () => {
    vi.mocked(getPositionTrainingRequirements).mockResolvedValue({
      data: page(1, 1, [item("selected")]),
    } as never);
    const controller = new AbortController();

    await expect(fetchTrainingRequirements(selectedFilters, controller.signal)).resolves.toEqual({
      status: "success",
      data: page(1, 1, [item("selected")]),
    });
    expect(getPositionTrainingRequirements).toHaveBeenCalledWith({
      query: {
        as_of: TODAY,
        training_requirement_lt: 0,
        trainer_color: "black",
        opening_key: OPENING_KEY,
        opening_match: "reached",
        page: 1,
        page_size: 100,
      },
      signal: controller.signal,
    });
  });

  it("accumulates sequential pages in response order without duplicating an item", async () => {
    const first = item("first");
    const second = item("second", { preferred_move_uci: "d2d4" });
    vi.mocked(getPositionTrainingRequirements)
      .mockResolvedValueOnce({ data: page(1, 2, [first]) } as never)
      .mockResolvedValueOnce({ data: page(2, 2, [first, second]) } as never);

    await expect(
      fetchTrainingRequirements({ asOf: TODAY, openingKey: null, trainerColor: null }),
    ).resolves.toEqual({ status: "success", data: page(1, 2, [first, second]) });
    expect(getPositionTrainingRequirements).toHaveBeenCalledTimes(2);
    expect(vi.mocked(getPositionTrainingRequirements).mock.calls.map(([request]) => request)).toEqual([
      {
        query: { as_of: TODAY, training_requirement_lt: 0, page: 1, page_size: 100 },
        signal: undefined,
      },
      {
        query: { as_of: TODAY, training_requirement_lt: 0, page: 2, page_size: 100 },
        signal: undefined,
      },
    ]);
  });

  it("does not make a request for an invalid date", async () => {
    vi.mocked(getPositionTrainingRequirements).mockResolvedValue({
      data: page(1, 0, []),
    } as never);

    await expect(
      fetchTrainingRequirements({ ...selectedFilters, asOf: "2026-02-31" }),
    ).resolves.toEqual({ status: "invalid_date" });
    expect(getPositionTrainingRequirements).not.toHaveBeenCalled();
  });

  it.each([
    [409, "training_requirements_stale", "stale_date"],
    [422, "invalid_as_of", "invalid_date"],
    [503, "position_training_requirements_unavailable", "retrieval_error"],
  ] as const)("maps typed HTTP failure %s/%s", async (status, code, expected) => {
    vi.mocked(getPositionTrainingRequirements).mockResolvedValue({
      error: { code, message: "safe detail" },
      response: { status },
    } as never);

    await expect(fetchTrainingRequirements({ ...selectedFilters })).resolves.toEqual({
      status: expected,
    });
  });

  it("maps a network rejection to retrieval_error", async () => {
    vi.mocked(getPositionTrainingRequirements).mockRejectedValue(new Error("offline"));

    await expect(fetchTrainingRequirements(selectedFilters)).resolves.toEqual({
      status: "retrieval_error",
    });
  });

  it("rejects an aborted response so a caller can ignore stale work", async () => {
    let resolveRequest!: (value: unknown) => void;
    const pending = new Promise((resolve) => {
      resolveRequest = resolve;
    });
    vi.mocked(getPositionTrainingRequirements).mockReturnValue(pending as never);
    const controller = new AbortController();
    const request = fetchTrainingRequirements(
      { asOf: TODAY, openingKey: null, trainerColor: null },
      controller.signal,
    );

    controller.abort();
    resolveRequest({ data: page(1, 1, [item("aborted")]) });
    await expect(request).rejects.toMatchObject({ name: "AbortError" });
  });
});
