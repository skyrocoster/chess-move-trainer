import { ArrowRight, ArrowUpRight, Check, Equal, Minus, TriangleAlert } from "lucide-react";
import type { ReactNode } from "react";

import { CalendarDate, type CalendarDateValue } from "../design-system/CalendarDate";
import { formatUtcDate } from "../design-system/CalendarDateUtils";
import styles from "./PreferredMovePrimitives.module.css";

export type PreferredMoveValueProps = {
  san: string;
  uci?: string | null;
};

export type PreferredMoveChoiceBoxTone = "saved" | "proposal" | "matching" | "empty" | "blocked";

export type PreferredMoveChoiceBoxProps = {
  label: "Current saved choice" | "Staged move";
  tone?: PreferredMoveChoiceBoxTone;
  move?: PreferredMoveValueProps | null;
  effectiveDate?: Date | null;
  emptyTitle?: string;
  emptyDescription?: string;
  onActivate?: () => void;
  activationLabel?: string;
  disabled?: boolean;
};

const TONE_ICON = {
  saved: Check,
  proposal: ArrowUpRight,
  matching: Equal,
  empty: Minus,
  blocked: TriangleAlert,
} as const;

function joinClasses(...classes: Array<string | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

function choiceBoxEmptyTitle(label: PreferredMoveChoiceBoxProps["label"]): string {
  return label === "Current saved choice" ? "No saved choice yet." : "No move staged.";
}

export function PreferredMoveValue({ san, uci }: PreferredMoveValueProps) {
  return (
    <div className={styles.moveValue}>
      <span className={styles.san}>{san}</span>
      {uci ? <span className={styles.uci}>{uci}</span> : null}
    </div>
  );
}

export function PreferredMoveDateValue({ value }: { value: Date }) {
  return (
    <div className={styles.dateValue}>
      <span>Effective date</span>
      <strong>{formatUtcDate(value)}</strong>
    </div>
  );
}

export function PreferredMoveChoiceBox({
  label,
  tone = "empty",
  move = null,
  effectiveDate = null,
  emptyTitle,
  emptyDescription,
  onActivate,
  activationLabel,
  disabled = false,
}: PreferredMoveChoiceBoxProps) {
  const Icon = TONE_ICON[tone];
  const content = (
    <>
      <div className={styles.boxTop}>
        <div className={styles.boxLabel}>
          <span className={joinClasses(styles.boxIcon, styles[`boxIcon${tone}`])}>
            <Icon aria-hidden="true" focusable="false" />
          </span>
          <span>{label}</span>
        </div>
      </div>
      {move ? (
        <PreferredMoveValue san={move.san} uci={move.uci} />
      ) : (
        <div className={styles.emptyContent}>
          <strong>{emptyTitle ?? choiceBoxEmptyTitle(label)}</strong>
          {emptyDescription ? <span>{emptyDescription}</span> : null}
        </div>
      )}
      {effectiveDate ? <PreferredMoveDateValue value={effectiveDate} /> : null}
    </>
  );

  if (onActivate) {
    return (
      <button
        type="button"
        className={joinClasses(
          styles.choiceBox,
          styles[`choiceBox${tone[0].toUpperCase()}${tone.slice(1)}`],
          styles.choiceBoxInteractive,
        )}
        aria-label={
          activationLabel ?? `${label}${move ? `: ${move.san}; play and stage this move.` : ""}`
        }
        onClick={onActivate}
        disabled={disabled}
      >
        {content}
      </button>
    );
  }

  return (
    <section
      className={joinClasses(
        styles.choiceBox,
        styles[`choiceBox${tone[0].toUpperCase()}${tone.slice(1)}`],
      )}
      aria-label={label}
    >
      {content}
    </section>
  );
}

export function PreferredMoveConnector({ label }: { label: string }) {
  return (
    <div className={styles.connector} aria-hidden="true">
      <ArrowRight className={styles.connectorIcon} focusable="false" />
      <span>{label}</span>
    </div>
  );
}

export type PreferredMoveConsequenceProps =
  | { kind: "first-choice"; stagedSan: string }
  | { kind: "replacement"; stagedSan: string; savedSan: string }
  | { kind: "matching"; savedSan: string };

function consequenceText(props: PreferredMoveConsequenceProps): string {
  switch (props.kind) {
    case "first-choice":
      return `Save ${props.stagedSan} as the current saved choice.`;
    case "replacement":
      return `Save ${props.stagedSan} to replace ${props.savedSan}.`;
    case "matching":
      return `${props.savedSan} is already the current saved choice.`;
  }
}

export function PreferredMoveConsequence(props: PreferredMoveConsequenceProps) {
  const toneClass =
    props.kind === "matching" ? styles.consequenceMatching : styles.consequenceReady;

  return (
    <p className={joinClasses(styles.consequence, toneClass)} data-kind={props.kind}>
      <ArrowRight className={styles.consequenceIcon} aria-hidden="true" focusable="false" />
      <span>{consequenceText(props)}</span>
    </p>
  );
}

export type PreferredMoveDateProps = {
  value: CalendarDateValue;
  onChange: (value: CalendarDateValue) => void;
  label?: string;
};

export function PreferredMoveDate({
  value,
  onChange,
  label = "Change effective date",
}: PreferredMoveDateProps) {
  return (
    <div className={styles.dateControl}>
      <CalendarDate value={value} onChange={onChange} label={label} />
    </div>
  );
}

export function PreferredMoveActionLayout({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={joinClasses(styles.actionLayout, className)}>{children}</div>;
}
