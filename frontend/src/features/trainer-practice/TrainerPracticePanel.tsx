import type { FormEvent } from "react";

import type {
  OpeningCatalogueItemResponse,
  TrainingRequirementResponse,
} from "../../api/client";
import { Button } from "../design-system/Button";
import { CalendarDate, type CalendarDateValue } from "../design-system/CalendarDate";
import { Field } from "../design-system/form-controls/Field";
import { RadioGroup } from "../design-system/form-controls/RadioGroup";
import {
  OpeningSearchCombobox,
  type OpeningSelection,
} from "./OpeningSearchCombobox";
import type { TrainerColor } from "./trainerPracticeApi";
import styles from "./TrainerPracticePanel.module.css";

export type TrainerPracticeFormValues = {
  openingSelection: OpeningSelection;
  trainerColor: "" | TrainerColor;
  asOf: CalendarDateValue;
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
  onOpeningSelectionChange: (selection: OpeningSelection) => void;
  onCatalogueSearchChange: (value: string) => void;
  onMissingOpeningSelection: () => void;
  onTrainerColorChange: (value: "" | TrainerColor) => void;
  onAsOfChange: (value: CalendarDateValue) => void;
  onSubmit: (values: TrainerPracticeFormValues) => void;
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
    <section className={styles.results} aria-labelledby="training-requirements-heading">
      <h2 id="training-requirements-heading">training-required positions</h2>
      <div className={styles.metadata}>
        <Metadata data={data} />
      </div>
      {data.items.length === 0 ? (
        <p role="status" aria-live="polite">
          No positions currently require training for these filters.
        </p>
      ) : (
          <ol className={styles.positionList} aria-label="training-required positions">
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
  onCatalogueSearchChange,
  onTrainerColorChange,
  onAsOfChange,
  onSubmit,
  onRetryCatalogue,
  onOpeningSelectionChange,
  onMissingOpeningSelection,
}: TrainerPracticePanelProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(values);
  }

  return (
    <section className={styles.page} aria-labelledby="trainer-practice-heading">
      <h1 className={styles.heading} id="trainer-practice-heading">
        Trainer Practice
      </h1>

      {catalogueStatus === "loading" ? (
        <p role="status" aria-live="polite">
          {openings.length > 0
            ? "Checking opening catalogue..."
            : "Loading opening catalogue..."}
        </p>
      ) : null}
      {catalogueStatus === "error" ? (
        <div role="alert" aria-live="assertive">
          <p>
            {openings.length > 0
              ? "Opening catalogue could not be refreshed."
              : "Opening catalogue could not be loaded."}
          </p>
          <Button type="button" variant="secondary" onClick={onRetryCatalogue}>
            Retry opening catalogue
          </Button>
        </div>
      ) : null}

      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        <div className={styles.openingField}>
          <Field label="Opening" description="Search by opening name, ECO, or stable key.">
            <OpeningSearchCombobox
              onMissingSelection={onMissingOpeningSelection}
              onQueryChange={onCatalogueSearchChange}
              onSelectionChange={onOpeningSelectionChange}
              openings={openings}
              query={catalogueSearch}
              selection={values.openingSelection}
            />
          </Field>
        </div>

        <div className={styles.filterFields}>
          <Field label="Learner colour">
            <RadioGroup
              ariaLabel="Learner colour"
              options={[
                { value: "", label: "All colours" },
                { value: "white", label: "White" },
                { value: "black", label: "Black" },
              ]}
              value={values.trainerColor}
              onValueChange={(value) => onTrainerColorChange(value as "" | TrainerColor)}
            />
          </Field>

          <Field label="as_of" required>
            <CalendarDate
              value={values.asOf}
              onChange={onAsOfChange}
              label="as_of"
            />
          </Field>
        </div>

        <Button
          type="submit"
          disabled={catalogueStatus !== "ready" || values.openingSelection === null}
        >
          Find training positions
        </Button>
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
