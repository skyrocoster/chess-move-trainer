import type { FormEvent } from "react";

import type {
  OpeningCatalogueItemResponse,
  TrainingRequirementResponse,
} from "../../api/client";
import type { TrainerColor } from "./trainerPracticeApi";

export type TrainerPracticeFormValues = {
  openingKey: string;
  trainerColor: "" | TrainerColor;
  asOf: string;
};

export type TrainerPracticePanelProps = {
  values: TrainerPracticeFormValues;
  catalogueSearch: string;
  openings: OpeningCatalogueItemResponse[];
  catalogueStatus: "loading" | "ready" | "error";
  retrieval:
    | { status: "idle" | "loading" }
    | { status: "catalogue-error" | "retrieval-error" | "invalid-date" | "stale-date" }
    | { status: "empty" | "success"; data: TrainingRequirementResponse };
  onOpeningKeyChange: (value: string) => void;
  onCatalogueSearchChange: (value: string) => void;
  onTrainerColorChange: (value: "" | TrainerColor) => void;
  onAsOfChange: (value: string) => void;
  onSubmit: (values: TrainerPracticeFormValues) => void;
  onSearchCatalogue: () => void;
  onRetryCatalogue: () => void;
};

function displayValue(value: string | number | boolean | null): string {
  return value === null ? "null" : String(value);
}

function Metadata({ data }: { data: TrainingRequirementResponse }) {
  return (
    <>
      <h3>response metadata</h3>
      <dl>
        <div>
          <dt>as_of</dt>
          <dd>{data.as_of}</dd>
        </div>
        <div>
          <dt>page</dt>
          <dd>{data.page}</dd>
        </div>
        <div>
          <dt>page_size</dt>
          <dd>{data.page_size}</dd>
        </div>
        <div>
          <dt>total</dt>
          <dd>{data.total}</dd>
        </div>
      </dl>

      <h3>scoring_policy</h3>
      <dl>
        <div>
          <dt>target_success_rate</dt>
          <dd>{data.scoring_policy.target_success_rate}</dd>
        </div>
        <div>
          <dt>game_hit_weight</dt>
          <dd>{data.scoring_policy.game_hit_weight}</dd>
        </div>
        <div>
          <dt>game_miss_weight</dt>
          <dd>{data.scoring_policy.game_miss_weight}</dd>
        </div>
        <div>
          <dt>training_curve</dt>
          <dd>{data.scoring_policy.training_curve}</dd>
        </div>
        <div>
          <dt>training_credit_half_life_days</dt>
          <dd>{data.scoring_policy.training_credit_half_life_days}</dd>
        </div>
      </dl>
    </>
  );
}

function PositionItem({
  item,
  index,
}: {
  item: TrainingRequirementResponse["items"][number];
  index: number;
}) {
  return (
    <li>
      <h3>position {index + 1}</h3>
      <dl>
        <div>
          <dt>fen</dt>
          <dd>{item.fen}</dd>
        </div>
        <div>
          <dt>trainer_color</dt>
          <dd>{item.trainer_color}</dd>
        </div>
        <div>
          <dt>preferred_move_uci</dt>
          <dd>{item.preferred_move_uci}</dd>
        </div>
        <div>
          <dt>encounters</dt>
          <dd>{item.encounters}</dd>
        </div>
        <div>
          <dt>hits</dt>
          <dd>{item.hits}</dd>
        </div>
        <div>
          <dt>misses</dt>
          <dd>{item.misses}</dd>
        </div>
        <div>
          <dt>observed_success_rate</dt>
          <dd>{item.observed_success_rate}</dd>
        </div>
        <div>
          <dt>game_balance</dt>
          <dd>{item.game_balance}</dd>
        </div>
        <div>
          <dt>effective_training_balance</dt>
          <dd>{item.effective_training_balance}</dd>
        </div>
        <div>
          <dt>training_adjustment</dt>
          <dd>{item.training_adjustment}</dd>
        </div>
        <div>
          <dt>training_updated_on</dt>
          <dd>{displayValue(item.training_updated_on)}</dd>
        </div>
        <div>
          <dt>training_requirement</dt>
          <dd>{item.training_requirement}</dd>
        </div>
        <div>
          <dt>training_required</dt>
          <dd>{displayValue(item.training_required)}</dd>
        </div>
        <div>
          <dt>correct_answers_needed</dt>
          <dd>{item.correct_answers_needed}</dd>
        </div>
      </dl>
    </li>
  );
}

function Results({ data }: { data: TrainingRequirementResponse }) {
  return (
    <section aria-labelledby="training-requirements-heading">
      <h2 id="training-requirements-heading">training-required positions</h2>
      <Metadata data={data} />
      {data.items.length === 0 ? (
        <p role="status" aria-live="polite">
          No positions currently require training for these filters.
        </p>
      ) : (
        <ol aria-label="training-required positions">
          {data.items.map((item, index) => (
            <PositionItem
              key={`${item.fen}-${item.trainer_color}-${item.preferred_move_uci}`}
              item={item}
              index={index}
            />
          ))}
        </ol>
      )}
    </section>
  );
}

export function TrainerPracticePanel({
  values,
  catalogueSearch,
  openings,
  catalogueStatus,
  retrieval,
  onOpeningKeyChange,
  onCatalogueSearchChange,
  onTrainerColorChange,
  onAsOfChange,
  onSubmit,
  onSearchCatalogue,
  onRetryCatalogue,
}: TrainerPracticePanelProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(values);
  }

  return (
    <section aria-labelledby="trainer-practice-heading">
      <h1 id="trainer-practice-heading">Trainer Practice</h1>

      {catalogueStatus === "loading" ? (
        <p role="status" aria-live="polite">
          Loading opening catalogue...
        </p>
      ) : null}
      {catalogueStatus === "error" ? (
        <div role="alert" aria-live="assertive">
          <p>Opening catalogue could not be loaded.</p>
          <button type="button" onClick={onRetryCatalogue}>
            Retry opening catalogue
          </button>
        </div>
      ) : null}

      <form onSubmit={handleSubmit} noValidate>
        <label htmlFor="trainer-practice-catalogue-search">Search openings</label>
        <input
          id="trainer-practice-catalogue-search"
          type="search"
          value={catalogueSearch}
          onChange={(event) => onCatalogueSearchChange(event.target.value)}
        />
        <button type="button" onClick={onSearchCatalogue}>
          Search opening catalogue
        </button>

        <label htmlFor="trainer-practice-opening">Opening</label>
        <select
          id="trainer-practice-opening"
          value={values.openingKey}
          onChange={(event) => onOpeningKeyChange(event.target.value)}
        >
          <option value="">All openings</option>
          {openings.map((opening) => (
            <option key={opening.key} value={opening.key}>
              {opening.name} ({opening.eco})
            </option>
          ))}
        </select>

        <label htmlFor="trainer-practice-color">Learner colour</label>
        <select
          id="trainer-practice-color"
          value={values.trainerColor}
          onChange={(event) =>
            onTrainerColorChange(event.target.value as "" | TrainerColor)
          }
        >
          <option value="">All colours</option>
          <option value="white">White</option>
          <option value="black">Black</option>
        </select>

        <label htmlFor="trainer-practice-as-of">as_of</label>
        <input
          id="trainer-practice-as-of"
          type="date"
          value={values.asOf}
          onChange={(event) => onAsOfChange(event.target.value)}
          required
        />

        <button type="submit" disabled={catalogueStatus !== "ready"}>
          Retrieve training positions
        </button>
      </form>

      {retrieval.status === "loading" ? (
        <p role="status" aria-live="polite">
          Loading training-required positions...
        </p>
      ) : null}
      {retrieval.status === "catalogue-error" ? (
        <p role="alert">Opening catalogue could not be loaded.</p>
      ) : null}
      {retrieval.status === "retrieval-error" ? (
        <p role="alert">Training-required positions could not be loaded.</p>
      ) : null}
      {retrieval.status === "invalid-date" ? (
        <p role="alert">The selected as_of date is not valid.</p>
      ) : null}
      {retrieval.status === "stale-date" ? (
        <p role="alert">
          Training requirements changed after this date. Choose a newer date and try again.
        </p>
      ) : null}
      {retrieval.status === "empty" || retrieval.status === "success" ? (
        <Results data={retrieval.data} />
      ) : null}
    </section>
  );
}
