import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { StatisticsOverviewResponse } from "../../api/client";
import { QueryClientTestProvider } from "../../test-utils/QueryClientTestProvider";
import { AnalysisPage } from "./AnalysisPage";
import { AnalysisOverviewQueryError, type AnalysisOverviewClient } from "./analysisOverviewApi";

expect.extend(matchers);

afterEach(cleanup);

const record = {
  total_count: 12,
  known_outcome_count: 12,
  win_count: 7,
  loss_count: 3,
  draw_count: 2,
  unknown_count: 0,
  score_rate: 2 / 3,
};

const numericSummary = {
  count: 12,
  minimum: 1400,
  maximum: 1580,
  average: 1512,
  median: 1518,
};

const OVERVIEW: StatisticsOverviewResponse = {
  as_of: "2026-09-21",
  filters: {
    started_on_or_after: null,
    started_on_or_before: null,
    trainer_color: null,
    time_class: null,
  },
  games: {
    record,
    by_trainer_color: [
      { category: "white", record: { ...record, total_count: 7 } },
      { category: "black", record: { ...record, total_count: 5 } },
    ],
    by_time_class: [{ category: "rapid", record }],
    by_time_control: [{ category: "600+5", record }],
    by_termination_reason: [{ category: "checkmate", record }],
    by_rating_difference: [{ category: "within_49", record }],
    by_length_plies: [{ category: "20-39", record }],
    trainer_rating: numericSummary,
    opponent_rating: { ...numericSummary, average: 1502 },
    rating_difference: { ...numericSummary, minimum: -80, maximum: 90, average: 10 },
    length_plies: { ...numericSummary, minimum: 22, maximum: 58, average: 36 },
    duration_seconds: { ...numericSummary, minimum: 300, maximum: 1400, average: 780 },
    trainer_rating_progression: {
      dated_rating_count: 12,
      first_rating: 1480,
      last_rating: 1542,
      change: 62,
      peak_rating: 1558,
      lowest_rating: 1472,
    },
  },
  activity: {
    first_game_at_utc: "2026-07-02T10:00:00Z",
    last_game_at_utc: "2026-09-18T18:00:00Z",
    dated_game_count: 12,
    by_month: [
      { period: "2026-08", record: { ...record, total_count: 5 }, average_trainer_rating: 1504 },
      { period: "2026-09", record: { ...record, total_count: 7 }, average_trainer_rating: 1530 },
    ],
    by_weekday_utc: [],
    by_hour_utc: [],
    recent_form: [10, 25, 50].map((requested_game_count) => ({
      requested_game_count,
      dated_game_count: Math.min(requested_game_count, 12),
      record,
    })),
    streaks: {
      current_kind: "win",
      current_count: 3,
      longest_win_count: 4,
      longest_loss_count: 2,
      longest_draw_count: 1,
      longest_unbeaten_count: 6,
      longest_winless_count: 3,
    },
  },
  openings: {
    classified_game_count: 11,
    unclassified_game_count: 1,
    distinct_opening_count: 4,
    returned_opening_count: 1,
    openings: [
      {
        key: "B90:Sicilian Najdorf",
        eco: "B90",
        name: "Sicilian Najdorf",
        deepest_ply: 14,
        record,
        average_trainer_rating: 1520,
        average_length_plies: 42,
      },
    ],
  },
  opponents: {
    known_opponent_game_count: 12,
    unknown_opponent_game_count: 0,
    distinct_known_opponent_count: 10,
    repeat_opponent_count: 2,
    returned_opponent_count: 0,
    opponents: [],
  },
  positions: {
    database_position_count: 300,
    observed_position_count: 180,
    distinct_game_count: 12,
    occurrence_count: 420,
    outgoing_occurrence_count: 408,
    terminal_occurrence_count: 12,
    trainer_turn_occurrence_count: 210,
    opponent_turn_occurrence_count: 210,
    distinct_outgoing_move_count: 250,
    repeated_position_count: 44,
    average_occurrences_per_observed_position: 2.3,
    ply_buckets: [],
    recurring_positions: [
      {
        fen: "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
        distinct_game_count: 8,
        occurrence_count: 8,
        outgoing_occurrence_count: 8,
        terminal_occurrence_count: 0,
      },
    ],
  },
  analysis: {
    scoped_position_count: 180,
    ready_position_count: 135,
    browser_quality_count: 20,
    tool_quality_count: 115,
    terminal_result_count: 4,
    queued_position_count: 8,
    running_position_count: 1,
    not_requested_position_count: 36,
    line_count: 390,
    centipawn_line_count: 370,
    mate_line_count: 20,
    multi_pv_result_count: 120,
    average_depth: 19.4,
    ready_coverage_rate: 0.75,
  },
  repertoire: {
    trainer_turn_position_count: 90,
    move_preference_position_count: 63,
    no_preference_position_count: 5,
    unconfigured_position_count: 22,
    preference_coverage_rate: 0.7,
    preference_observed_position_count: 60,
    preferred_move_opportunity_count: 80,
    preferred_move_played_count: 58,
    preferred_move_adherence_rate: 0.725,
    training_balances: {
      count: 63,
      negative_count: 14,
      zero_count: 8,
      positive_count: 41,
      updated_count: 55,
      missing_count: 0,
      summary: { count: 63, minimum: -4, maximum: 9, average: 2.4, median: 2 },
    },
  },
  data_quality: {
    missing_outcome_count: 0,
    missing_trainer_rating_count: 0,
    missing_opponent_rating_count: 0,
    missing_started_at_count: 0,
    invalid_started_at_count: 0,
    missing_ended_at_count: 0,
    invalid_ended_at_count: 0,
    negative_duration_count: 0,
    missing_time_class_count: 0,
    missing_time_control_count: 0,
    missing_termination_reason_count: 0,
    missing_opponent_count: 0,
  },
};

function renderPage(client: AnalysisOverviewClient) {
  return render(
    <QueryClientTestProvider>
      <AnalysisPage client={client} />
    </QueryClientTestProvider>,
  );
}

describe("AnalysisPage", () => {
  it("loads an all-games scorecard and exposes the prepared report sections", async () => {
    const user = userEvent.setup();
    const client = vi.fn<AnalysisOverviewClient>().mockResolvedValue(OVERVIEW);
    const { container } = renderPage(client);

    expect(await screen.findByRole("heading", { name: "Your results" })).toBeInTheDocument();
    expect(screen.getByText("12 games")).toBeInTheDocument();
    expect(client).toHaveBeenCalledWith(
      expect.objectContaining({
        startedOnOrAfter: null,
        startedOnOrBefore: null,
        trainerColor: null,
        timeClass: null,
      }),
      expect.any(AbortSignal),
    );
    expect(await axe.run({ include: [container] })).toHaveNoViolations();

    await user.click(screen.getByRole("tab", { name: "Openings" }));
    expect(screen.getByRole("heading", { name: "Opening results" })).toBeVisible();
    expect(screen.getByText("Sicilian Najdorf")).toBeVisible();

    await user.click(screen.getByRole("tab", { name: "Preparation" }));
    expect(screen.getByRole("heading", { name: "Preparation coverage" })).toBeVisible();
    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });

  it("keeps filter changes local until Apply filters is pressed", async () => {
    const user = userEvent.setup();
    const client = vi.fn<AnalysisOverviewClient>().mockImplementation(async (filters) => ({
      ...OVERVIEW,
      filters: {
        started_on_or_after: filters.startedOnOrAfter,
        started_on_or_before: filters.startedOnOrBefore,
        trainer_color: filters.trainerColor,
        time_class: filters.timeClass,
      },
    }));
    renderPage(client);
    await screen.findByRole("heading", { name: "Your results" });

    await user.click(screen.getByRole("combobox", { name: "Learner colour" }));
    await user.click(screen.getByRole("option", { name: "White" }));
    expect(client).toHaveBeenCalledTimes(1);

    await user.click(screen.getByRole("button", { name: "Apply filters" }));
    await waitFor(() => expect(client).toHaveBeenCalledTimes(2));
    expect(client).toHaveBeenLastCalledWith(
      expect.objectContaining({ trainerColor: "white" }),
      expect.any(AbortSignal),
    );
    expect(await screen.findByText("All game dates · White · All speeds")).toBeInTheDocument();
  });

  it("offers recovery for an unavailable report", async () => {
    const client = vi
      .fn<AnalysisOverviewClient>()
      .mockRejectedValue(new AnalysisOverviewQueryError("statistics_unavailable"));
    renderPage(client);

    expect(
      await screen.findByRole("heading", { name: "Analysis unavailable" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Retry report" })).toBeInTheDocument();
    expect(screen.getByText(/rebuilt database is ready/i)).toBeInTheDocument();
  });

  it("explains when no games match and provides a one-step reset", async () => {
    const emptyOverview: StatisticsOverviewResponse = {
      ...OVERVIEW,
      games: { ...OVERVIEW.games, record: { ...record, total_count: 0 } },
    };
    const client = vi.fn<AnalysisOverviewClient>().mockResolvedValue(emptyOverview);
    renderPage(client);

    expect(
      await screen.findByRole("heading", { name: "No games match these filters" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Clear game filters" })).toBeInTheDocument();
  });

  it("links a missing snapshot date to its trigger and clears the alert on edit", async () => {
    const user = userEvent.setup();
    const client = vi.fn<AnalysisOverviewClient>().mockResolvedValue(OVERVIEW);
    renderPage(client);
    await screen.findByRole("heading", { name: "Your results" });

    const asOfTrigger = screen.getByRole("button", { name: /Training scores as of:/ });
    await user.click(asOfTrigger);
    const dialog = await screen.findByRole("dialog", { name: "Training scores as of" });
    const { within } = await import("@testing-library/react");
    await user.click(within(dialog).getByRole("button", { name: "Clear date" }));

    await user.click(screen.getByRole("button", { name: "Apply filters" }));
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Choose a training snapshot date");
    const alertId = alert.getAttribute("id");
    expect(alertId).toMatch(/^analysis-filters-error-/);

    const blankTrigger = screen.getByRole("button", {
      name: "Training scores as of: Choose date",
    });
    expect(blankTrigger).toHaveAttribute("aria-invalid", "true");
    expect(blankTrigger).toHaveAttribute("aria-describedby", alertId);
    expect(screen.getAllByRole("alert")).toHaveLength(1);

    // Editing clears the single alert and the invalid state.
    await user.click(blankTrigger);
    const reopened = await screen.findByRole("dialog", { name: "Training scores as of" });
    const dayButton = within(reopened)
      .getAllByRole("button")
      .find(
        (button) =>
          !button.hasAttribute("disabled") &&
          /\d{4}/.test(button.getAttribute("aria-label") ?? button.textContent ?? ""),
      );
    expect(dayButton).toBeDefined();
    await user.click(dayButton!);
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Training scores as of: \d{4}-\d{2}-\d{2}/ }),
    ).not.toHaveAttribute("aria-invalid");
    expect(client).toHaveBeenCalledTimes(1);
  });

  it("keeps unknown games in the outcome total", async () => {
    const unknownRecord = {
      ...record,
      total_count: 14,
      known_outcome_count: 12,
      unknown_count: 2,
    };
    const unknownOverview: StatisticsOverviewResponse = {
      ...OVERVIEW,
      games: { ...OVERVIEW.games, record: unknownRecord },
    };
    const client = vi.fn<AnalysisOverviewClient>().mockResolvedValue(unknownOverview);
    renderPage(client);

    await screen.findByRole("heading", { name: "Your results" });
    expect(
      screen.getByRole("img", { name: "7 wins, 2 draws, 3 losses, 2 unknown" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Unknown")).toBeInTheDocument();
  });

  it("announces the filter count with meaningful text", async () => {
    const client = vi.fn<AnalysisOverviewClient>().mockResolvedValue(OVERVIEW);
    renderPage(client);
    await screen.findByRole("heading", { name: "Your results" });

    expect(screen.getByText("All games")).toBeVisible();
  });
});
