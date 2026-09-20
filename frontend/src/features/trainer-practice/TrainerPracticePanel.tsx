import type { FormEvent } from "react";

import type { OpeningCatalogueItemResponse, TrainingRequirementResponse } from "../../api/client";
import { Button } from "../design-system/Button";
import { CalendarDate, type CalendarDateValue } from "../design-system/CalendarDate";
import { Field } from "../design-system/form-controls/Field";
import { RadioGroup } from "../design-system/form-controls/RadioGroup";
import { OpeningSearchCombobox, type OpeningSelection } from "./OpeningSearchCombobox";
import { TrainerSession } from "./TrainerSession";
import type {
  TrainerColor,
  TrainerPracticeFilters,
  TrainingAnswerInput,
  TrainingAnswerResult,
} from "./trainerPracticeApi";
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
  submittedFilters: TrainerPracticeFilters | null;
  sessionRevision: number;
  onOpeningSelectionChange: (selection: OpeningSelection) => void;
  onCatalogueSearchChange: (value: string) => void;
  onMissingOpeningSelection: () => void;
  onTrainerColorChange: (value: "" | TrainerColor) => void;
  onAsOfChange: (value: CalendarDateValue) => void;
  onSubmit: (values: TrainerPracticeFormValues) => void;
  onRetryCatalogue: () => void;
  onSubmitAnswer: (
    input: TrainingAnswerInput,
    signal?: AbortSignal,
  ) => Promise<TrainingAnswerResult>;
  onRefreshRequirements: () => void;
};

function sessionKey(
  data: TrainingRequirementResponse,
  submittedFilters: TrainerPracticeFilters | null,
) {
  return JSON.stringify([
    submittedFilters,
    data.items.map((item) => [
      item.fen,
      item.trainer_color,
      item.preferred_move_uci,
      item.training_requirement,
    ]),
  ]);
}

function EmptyResults() {
  return (
    <section className={styles.emptyResults} aria-labelledby="training-session-empty-heading">
      <h2 id="training-session-empty-heading">Nothing to practise right now</h2>
      <p role="status" aria-live="polite">
        No positions currently require training for these filters.
      </p>
    </section>
  );
}

export function TrainerPracticePanel({
  values,
  catalogueSearch,
  openings,
  catalogueStatus,
  retrieval,
  submittedFilters,
  sessionRevision,
  onCatalogueSearchChange,
  onTrainerColorChange,
  onAsOfChange,
  onSubmit,
  onRetryCatalogue,
  onSubmitAnswer,
  onRefreshRequirements,
  onOpeningSelectionChange,
  onMissingOpeningSelection,
}: TrainerPracticePanelProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(values);
  }

  const specificOpeningKey = submittedFilters?.openingKey ?? null;
  const selectedOpening =
    specificOpeningKey === null
      ? null
      : openings.find((opening) => opening.key === specificOpeningKey);
  const openingScopeLabel =
    submittedFilters?.openingKey === null
      ? "All openings"
      : (selectedOpening?.name ?? "Selected opening");
  const scopeLabel = submittedFilters?.trainerColor
    ? `${openingScopeLabel} · ${
        submittedFilters.trainerColor === "white" ? "White" : "Black"
      } repertoire`
    : openingScopeLabel;

  return (
    <section className={styles.page} aria-labelledby="trainer-practice-heading">
      <h1 className={styles.heading} id="trainer-practice-heading">
        Trainer Practice
      </h1>

      {catalogueStatus === "loading" ? (
        <p role="status" aria-live="polite">
          {openings.length > 0 ? "Checking opening catalogue..." : "Loading opening catalogue..."}
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
        <div className={styles.formIntro}>
          <h2>Build a practice set</h2>
          <p>Choose where to focus. Positions appear only when their current score needs work.</p>
        </div>
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
            <CalendarDate value={values.asOf} onChange={onAsOfChange} label="as_of" />
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
      {retrieval.status === "empty" ? <EmptyResults /> : null}
      {retrieval.status === "success" ? (
        <TrainerSession
          key={`${sessionRevision}:${sessionKey(retrieval.data, submittedFilters)}`}
          data={retrieval.data}
          scopeLabel={scopeLabel}
          onSubmitAnswer={onSubmitAnswer}
          onRefreshRequirements={onRefreshRequirements}
        />
      ) : null}
    </section>
  );
}
