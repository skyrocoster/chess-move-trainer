import { useId, type FormEvent } from "react";

import { Button } from "../design-system/Button";
import { CalendarDate, type CalendarDateValue } from "../design-system/CalendarDate";
import { Field } from "../design-system/form-controls/Field";
import { Select } from "../design-system/form-controls/Select";
import type { AnalysisTimeClass, AnalysisTrainerColor } from "./analysisOverviewApi";
import styles from "./AnalysisFilters.module.css";

export type AnalysisFilterDraft = {
  asOf: CalendarDateValue;
  startedOnOrAfter: CalendarDateValue;
  startedOnOrBefore: CalendarDateValue;
  trainerColor: AnalysisTrainerColor | null;
  timeClass: AnalysisTimeClass | null;
};

export type AnalysisFiltersInvalid = {
  asOf: boolean;
  startedOnOrAfter: boolean;
  startedOnOrBefore: boolean;
};

type AnalysisFiltersProps = {
  draft: AnalysisFilterDraft;
  activeCount: number;
  validationMessage: string | null;
  validationId?: string;
  invalid?: AnalysisFiltersInvalid;
  applying: boolean;
  onChange: (draft: AnalysisFilterDraft) => void;
  onApply: () => void;
  onReset: () => void;
};

const COLOR_OPTIONS = [
  { value: "all", label: "Both colours" },
  { value: "white", label: "White" },
  { value: "black", label: "Black" },
];

const TIME_CLASS_OPTIONS = [
  { value: "all", label: "All speeds" },
  { value: "bullet", label: "Bullet" },
  { value: "blitz", label: "Blitz" },
  { value: "rapid", label: "Rapid" },
  { value: "daily", label: "Daily" },
];

function activeCountLabel(activeCount: number): string {
  if (activeCount === 0) return "All games";
  return `${activeCount} active ${activeCount === 1 ? "filter" : "filters"}`;
}

export function AnalysisFilters({
  draft,
  activeCount,
  validationMessage,
  validationId,
  invalid = { asOf: false, startedOnOrAfter: false, startedOnOrBefore: false },
  applying,
  onChange,
  onApply,
  onReset,
}: AnalysisFiltersProps) {
  const generatedValidationId = useId();
  const resolvedValidationId = validationId ?? `analysis-filters-error-${generatedValidationId}`;

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onApply();
  }

  const describedBy = (isInvalid: boolean) =>
    validationMessage && isInvalid ? resolvedValidationId : undefined;

  return (
    <form className={styles.filters} onSubmit={handleSubmit} noValidate>
      <div className={styles.filterHeader}>
        <div>
          <p className={styles.eyebrow}>Report scope</p>
          <h2>Filter your games</h2>
          <p>All charts and tables update together when you apply these filters.</p>
        </div>
        <span className={styles.filterCount}>{activeCountLabel(activeCount)}</span>
      </div>

      <div className={styles.filterGrid}>
        <Field
          label="Games from"
          description="Optional start date, in UTC."
          invalid={invalid.startedOnOrAfter}
        >
          <CalendarDate
            label="Games from"
            value={draft.startedOnOrAfter}
            onChange={(value) => onChange({ ...draft, startedOnOrAfter: value })}
            invalid={invalid.startedOnOrAfter}
            describedBy={describedBy(invalid.startedOnOrAfter)}
          />
        </Field>
        <Field
          label="Games through"
          description="Optional end date, in UTC."
          invalid={invalid.startedOnOrBefore}
        >
          <CalendarDate
            label="Games through"
            value={draft.startedOnOrBefore}
            onChange={(value) => onChange({ ...draft, startedOnOrBefore: value })}
            invalid={invalid.startedOnOrBefore}
            describedBy={describedBy(invalid.startedOnOrBefore)}
          />
        </Field>
        <Field label="Learner colour">
          <Select
            ariaLabel="Learner colour"
            options={COLOR_OPTIONS}
            value={draft.trainerColor ?? "all"}
            onValueChange={(value) =>
              onChange({
                ...draft,
                trainerColor: value === "white" || value === "black" ? value : null,
              })
            }
          />
        </Field>
        <Field label="Time class">
          <Select
            ariaLabel="Time class"
            options={TIME_CLASS_OPTIONS}
            value={draft.timeClass ?? "all"}
            onValueChange={(value) =>
              onChange({
                ...draft,
                timeClass:
                  value === "bullet" || value === "blitz" || value === "rapid" || value === "daily"
                    ? value
                    : null,
              })
            }
          />
        </Field>
        <Field
          label="Training scores as of"
          description="Sets the date used for repertoire training balances."
          required
          invalid={invalid.asOf}
        >
          <CalendarDate
            label="Training scores as of"
            value={draft.asOf}
            onChange={(value) => onChange({ ...draft, asOf: value })}
            invalid={invalid.asOf}
            describedBy={describedBy(invalid.asOf)}
          />
        </Field>
      </div>

      {validationMessage ? (
        <p className={styles.filterError} role="alert" id={resolvedValidationId}>
          {validationMessage}
        </p>
      ) : null}

      <div className={styles.filterActions}>
        <Button type="submit" disabled={applying}>
          {applying ? "Applying…" : "Apply filters"}
        </Button>
        <Button type="button" variant="ghost" onClick={onReset}>
          Reset filters
        </Button>
      </div>
    </form>
  );
}
