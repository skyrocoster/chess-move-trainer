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
import { ANALYSIS_OVERVIEW_FIXTURE } from "./analysisOverviewFixtures";

expect.extend(matchers);

afterEach(cleanup);

const OVERVIEW = ANALYSIS_OVERVIEW_FIXTURE;
const record = OVERVIEW.games.record;

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
