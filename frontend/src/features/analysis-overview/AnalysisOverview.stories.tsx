import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, userEvent, within } from "storybook/test";

import { QueryClientTestProvider } from "../../test-utils/QueryClientTestProvider";
import { storyViewport } from "../../storybook/viewports";
import { AnalysisDashboard } from "./AnalysisDashboard";
import {
  AnalysisFilters,
  type AnalysisFilterDraft,
  type AnalysisFiltersInvalid,
} from "./AnalysisFilters";
import { AnalysisPage } from "./AnalysisPage";
import { AnalysisOverviewQueryError, type AnalysisOverviewClient } from "./analysisOverviewApi";
import {
  ANALYSIS_OVERVIEW_FIXTURE,
  EMPTY_ANALYSIS_OVERVIEW_FIXTURE,
} from "./analysisOverviewFixtures";

const meta = {
  title: "Production/Application/Analysis/Overview",
  tags: ["status-production"],
  parameters: { layout: "fullscreen" },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

const initialDraft: AnalysisFilterDraft = {
  asOf: new Date(Date.UTC(2026, 8, 21)),
  startedOnOrAfter: null,
  startedOnOrBefore: null,
  trainerColor: null,
  timeClass: null,
};

function FiltersHarness({
  validationMessage = null,
  invalid,
  applying = false,
}: {
  validationMessage?: string | null;
  invalid?: AnalysisFiltersInvalid;
  applying?: boolean;
}) {
  const [draft, setDraft] = useState(initialDraft);
  return (
    <main style={{ padding: "var(--cmt-spacing-24)" }}>
      <AnalysisFilters
        draft={draft}
        activeCount={2}
        validationMessage={validationMessage}
        invalid={invalid}
        applying={applying}
        onChange={setDraft}
        onApply={() => undefined}
        onReset={() => setDraft(initialDraft)}
      />
    </main>
  );
}

function isolatedPage(client: AnalysisOverviewClient) {
  return (
    <QueryClientTestProvider>
      <AnalysisPage client={client} />
    </QueryClientTestProvider>
  );
}

export const LoadedReport: Story = {
  render: () => isolatedPage(async () => ANALYSIS_OVERVIEW_FIXTURE),
};

export const LoadingReport: Story = {
  render: () => isolatedPage(() => new Promise(() => undefined)),
};

export const NoMatchingGames: Story = {
  render: () => isolatedPage(async () => EMPTY_ANALYSIS_OVERVIEW_FIXTURE),
};

export const UnavailableReport: Story = {
  render: () =>
    isolatedPage(async () => {
      throw new AnalysisOverviewQueryError("statistics_unavailable");
    }),
};

export const Filters: Story = {
  render: () => <FiltersHarness />,
};

export const FiltersValidation: Story = {
  render: () => (
    <FiltersHarness
      validationMessage="Games from must be on or before Games through."
      invalid={{ asOf: false, startedOnOrAfter: true, startedOnOrBefore: true }}
    />
  ),
};

export const FiltersConstrained: Story = {
  parameters: storyViewport("constrained-412"),
  render: () => <FiltersHarness />,
};

export const DashboardPerformance: Story = {
  render: () => <AnalysisDashboard data={ANALYSIS_OVERVIEW_FIXTURE} />,
};

export const DashboardOpenings: Story = {
  render: () => <AnalysisDashboard data={ANALYSIS_OVERVIEW_FIXTURE} />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("tab", { name: "Openings" }));
    await expect(canvas.getByRole("heading", { name: "Opening results" })).toBeVisible();
  },
};

export const DashboardPreparation: Story = {
  render: () => <AnalysisDashboard data={ANALYSIS_OVERVIEW_FIXTURE} />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("tab", { name: "Preparation" }));
    await expect(canvas.getByRole("heading", { name: "Preparation coverage" })).toBeVisible();
  },
};
