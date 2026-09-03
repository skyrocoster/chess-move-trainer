import { ArrowRight } from "lucide-react";
import { useId } from "react";

import { Button } from "../design-system/Button";
import { RemovePreferredMoveButton } from "./PreferredMoveActionButtons";
import styles from "./PreferredMovePanelExploration.module.css";

export type PreferredMoveExplorationState =
  | "staging_new"
  | "not_in_corpus"
  | "idle_saved"
  | "matches";

type ChoiceBoxData = {
  value?: string;
  sub?: string;
  empty?: string;
  tone?: "warning" | "success";
};

type PreferredMoveExplorationData = {
  meta: string;
  status: string;
  statusTone: "warning" | "success" | "neutral";
  saved: ChoiceBoxData;
  staged: ChoiceBoxData;
  helper?: string;
  primaryAction?: { label: string; disabled?: boolean };
  showRemove?: boolean;
};

const STATE_DATA: Record<PreferredMoveExplorationState, PreferredMoveExplorationData> = {
  staging_new: {
    meta: "Seen in 4 games as white",
    status: "Ready to save",
    statusTone: "warning",
    saved: { empty: "None yet" },
    staged: { value: "Nce2", sub: "c3e2", tone: "warning" },
    primaryAction: { label: "Save Nce2" },
  },
  not_in_corpus: {
    meta: "Never seen as white",
    status: "Not in Corpus",
    statusTone: "neutral",
    saved: { value: "Nce2", sub: "c3e2 · saved 2 Sep 2026", tone: "success" },
    staged: { empty: "No move staged" },
    helper: "This position isn't in your corpus, so it can't be saved yet.",
  },
  idle_saved: {
    meta: "Seen in 6,183 games as white",
    status: "Saved",
    statusTone: "success",
    saved: { value: "e4", sub: "e2e4 · saved 29 Aug 2026", tone: "success" },
    staged: { empty: "Stage a move to propose replacing e4" },
    showRemove: true,
  },
  matches: {
    meta: "Seen in 6,183 games as white",
    status: "Already saved",
    statusTone: "success",
    saved: { value: "e4", sub: "e2e4 · saved 29 Aug 2026", tone: "success" },
    staged: { value: "e4", sub: "e2e4", tone: "success" },
    primaryAction: { label: "Matches saved", disabled: true },
    showRemove: true,
  },
};

export type PreferredMovePanelExplorationProps = {
  state: PreferredMoveExplorationState;
  onSave?: () => void;
  onRemove?: () => void;
};

function toneClass(tone: ChoiceBoxData["tone"]): string | undefined {
  if (tone === "warning") return styles.choiceBoxWarning;
  if (tone === "success") return styles.choiceBoxSuccess;
  return undefined;
}

function statusToneClass(tone: PreferredMoveExplorationData["statusTone"]): string {
  switch (tone) {
    case "warning":
      return styles.statusWarning;
    case "success":
      return styles.statusSuccess;
    case "neutral":
      return styles.statusNeutral;
  }
}

function ChoiceBox({
  label,
  data,
  testId,
}: {
  label: "Saved" | "Staged";
  data: ChoiceBoxData;
  testId: string;
}) {
  return (
    <section className={`${styles.choiceBox} ${toneClass(data.tone) ?? ""}`} aria-label={label} data-testid={testId}>
      <p className={styles.boxLabel}>{label}</p>
      {data.value ? (
        <>
          <p className={styles.boxValue}>{data.value}</p>
          <p className={styles.boxSub}>{data.sub}</p>
        </>
      ) : (
        <p className={styles.boxEmpty}>{data.empty}</p>
      )}
    </section>
  );
}

export function PreferredMovePanelExploration({
  state,
  onSave = () => undefined,
  onRemove = () => undefined,
}: PreferredMovePanelExplorationProps) {
  const data = STATE_DATA[state];
  const headingId = useId();

  return (
    <div className={styles.frame}>
      <section
        className={styles.panel}
        data-state={state}
        data-testid="preferred-exploration-card"
        aria-labelledby={headingId}
      >
        <header className={styles.header}>
          <div>
            <h2 className={styles.heading} id={headingId}>
              Preferred move
            </h2>
            <p className={styles.meta}>{data.meta}</p>
          </div>
          <span className={`${styles.status} ${statusToneClass(data.statusTone)}`} role="status">
            {data.status}
          </span>
        </header>

        <div className={styles.relationship} data-testid="preferred-exploration-relationship">
          <ChoiceBox label="Saved" data={data.saved} testId="preferred-exploration-saved" />
          <div className={styles.connector} data-testid="preferred-exploration-connector" aria-hidden="true">
            <ArrowRight className={styles.connectorIcon} focusable="false" />
          </div>
          <ChoiceBox label="Staged" data={data.staged} testId="preferred-exploration-staged" />
        </div>

        {data.helper ? <p className={styles.helper}>{data.helper}</p> : null}

        {data.primaryAction || data.showRemove ? (
          <footer className={styles.actions} data-testid="preferred-exploration-actions">
            {data.primaryAction ? (
              <Button
                variant="primary"
                className={styles.primaryAction}
                disabled={data.primaryAction.disabled}
                onClick={onSave}
              >
                {data.primaryAction.label}
              </Button>
            ) : null}
            {data.showRemove ? (
              <RemovePreferredMoveButton
                className={`${styles.removeAction} ${data.primaryAction ? "" : styles.removeActionAlone}`}
                onClick={onRemove}
              />
            ) : null}
          </footer>
        ) : null}
      </section>
    </div>
  );
}
