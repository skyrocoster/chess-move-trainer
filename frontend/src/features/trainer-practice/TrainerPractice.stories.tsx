import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";

import type {
  OpeningCatalogueItemResponse,
  TrainingRequirementItemResponse,
  TrainingRequirementResponse,
} from "../../api/client";
import { storyViewport } from "../../storybook/viewports";
import { QueryClientTestProvider } from "../../test-utils/QueryClientTestProvider";
import { OpeningSearchCombobox, type OpeningSelection } from "./OpeningSearchCombobox";
import { TrainerPracticePage, type TrainerPracticeApi } from "./TrainerPracticePage";
import { TrainerPracticePanel, type TrainerPracticeFormValues } from "./TrainerPracticePanel";
import { TrainerSession } from "./TrainerSession";

const meta = {
  title: "Production/Application/Trainer Practice",
  tags: ["status-production"],
  parameters: { layout: "fullscreen" },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

const OPENINGS: OpeningCatalogueItemResponse[] = [
  {
    key: "B10:Caro-Kann Defense",
    eco: "B10",
    name: "Caro-Kann Defense",
    route_count: 2,
    games_reached: 12,
    games_deepest: 9,
  },
  {
    key: "C50:Italian Game",
    eco: "C50",
    name: "Italian Game",
    route_count: 4,
    games_reached: 18,
    games_deepest: 11,
  },
];

const TRAINING_ITEM: TrainingRequirementItemResponse = {
  fen: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  trainer_color: "white",
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
};

const TRAINING_REQUIREMENTS: TrainingRequirementResponse = {
  as_of: "2026-09-21",
  scoring_policy: {
    target_success_rate: 0.8,
    game_hit_weight: 1,
    game_miss_weight: 1,
    training_curve: "linear",
    training_credit_half_life_days: 30,
  },
  items: [TRAINING_ITEM],
  page: 1,
  page_size: 100,
  total: 1,
};

const submitAnswer = async () => ({ status: "submission_error" as const });

function OpeningSearchHarness() {
  const [query, setQuery] = useState("");
  const [selection, setSelection] = useState<OpeningSelection>(null);
  return (
    <main style={{ maxWidth: "42rem", padding: "var(--cmt-spacing-24)" }}>
      <OpeningSearchCombobox
        openings={OPENINGS}
        query={query}
        selection={selection}
        onQueryChange={setQuery}
        onSelectionChange={setSelection}
        onMissingSelection={() => setSelection(null)}
      />
    </main>
  );
}

function PanelHarness({
  retrieval = { status: "idle" },
  catalogueStatus = "ready",
}: {
  retrieval?: Parameters<typeof TrainerPracticePanel>[0]["retrieval"];
  catalogueStatus?: Parameters<typeof TrainerPracticePanel>[0]["catalogueStatus"];
}) {
  const [values, setValues] = useState<TrainerPracticeFormValues>({
    openingSelection: { kind: "specific", key: OPENINGS[0]!.key },
    trainerColor: "",
    asOf: new Date(Date.UTC(2026, 8, 21)),
  });
  const [catalogueSearch, setCatalogueSearch] = useState("");

  return (
    <TrainerPracticePanel
      values={values}
      catalogueSearch={catalogueSearch}
      openings={OPENINGS}
      catalogueStatus={catalogueStatus}
      retrieval={retrieval}
      submittedFilters={{
        asOf: "2026-09-21",
        openingKey: OPENINGS[0]!.key,
        trainerColor: null,
      }}
      sessionRevision={0}
      onOpeningSelectionChange={(openingSelection) =>
        setValues((current) => ({ ...current, openingSelection }))
      }
      onCatalogueSearchChange={setCatalogueSearch}
      onMissingOpeningSelection={() =>
        setValues((current) => ({ ...current, openingSelection: null }))
      }
      onTrainerColorChange={(trainerColor) =>
        setValues((current) => ({ ...current, trainerColor }))
      }
      onAsOfChange={(asOf) => setValues((current) => ({ ...current, asOf }))}
      onSubmit={fn()}
      onRetryCatalogue={fn()}
      onSubmitAnswer={submitAnswer}
      onRefreshRequirements={fn()}
    />
  );
}

const practiceApi: TrainerPracticeApi = {
  loadCatalogue: async () => ({
    status: "success",
    data: OPENINGS,
    catalogueVersion: "storybook-v1",
  }),
  loadRequirements: async () => ({ status: "success", data: TRAINING_REQUIREMENTS }),
  submitAnswer,
};

export const PracticePage: Story = {
  render: () => (
    <QueryClientTestProvider>
      <TrainerPracticePage api={practiceApi} />
    </QueryClientTestProvider>
  ),
};

export const OpeningSearch: Story = {
  render: () => <OpeningSearchHarness />,
};

export const PracticeBuilder: Story = {
  render: () => <PanelHarness />,
};

export const PracticeBuilderConstrained: Story = {
  parameters: storyViewport("constrained-412"),
  render: () => <PanelHarness />,
};

export const EmptyPracticeSet: Story = {
  render: () => (
    <PanelHarness retrieval={{ status: "empty", data: { ...TRAINING_REQUIREMENTS, items: [] } }} />
  ),
};

export const CatalogueUnavailable: Story = {
  render: () => <PanelHarness catalogueStatus="error" />,
};

export const PracticeSession: Story = {
  render: () => (
    <TrainerSession
      data={TRAINING_REQUIREMENTS}
      scopeLabel="Caro-Kann Defense · White repertoire"
      onSubmitAnswer={submitAnswer}
      onRefreshRequirements={fn()}
    />
  ),
};
