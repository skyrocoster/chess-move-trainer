import { Button } from "../design-system/Button";
import type { AnalysisPanelDisplay } from "./analysisFormatting";
import styles from "./AnalysisPanel.module.css";

export type AnalysisPanelIntent = () => void | Promise<void>;

export type AnalysisPanelProps = {
  display: AnalysisPanelDisplay;
  onAnalyze: AnalysisPanelIntent;
  onUpdate: AnalysisPanelIntent;
  onRetry: AnalysisPanelIntent;
  onRetryObservation: () => void;
};

function ResultLines({ result }: { result: NonNullable<AnalysisPanelDisplay["result"]> }) {
  return (
    <div className={styles.result}>
      {result.stale ? (
        <p className={styles.stale}>Stale analysis; update deliberately to refresh it.</p>
      ) : null}
      {result.lines.length === 0 ? (
        <p className={styles.emptyResult}>
          No candidate lines are available for this terminal position.
        </p>
      ) : (
        <ol className={styles.lines} aria-label="Ranked analysis lines">
          {result.lines.map((line) => (
            <li className={styles.line} key={line.rank}>
              <div className={styles.lineHeading}>
                <span>Line {line.rank}</span>
                <strong>{line.score}</strong>
              </div>
              <p className={styles.pv}>{line.pv}</p>
              <p className={styles.wdl}>{line.wdl}</p>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

export function AnalysisPanel({
  display,
  onAnalyze,
  onUpdate,
  onRetry,
  onRetryObservation,
}: AnalysisPanelProps) {
  const { stateLabel, error, actionError, message, result, actions } = display;

  return (
    <section className={styles.panel} aria-labelledby="analysis-panel-heading">
      <div className={styles.header}>
        <h2 id="analysis-panel-heading">Analysis</h2>
        <p className={styles.state} role="status" aria-live="polite">
          {stateLabel}
        </p>
      </div>

      {error ? (
        <p className={styles.error} role="alert">
          {error}
        </p>
      ) : null}
      {actionError ? (
        <p className={styles.error} role="alert">
          {actionError}
        </p>
      ) : null}
      {message ? (
        <p className={styles.message} role={message.alert ? "alert" : undefined}>
          {message.text}
        </p>
      ) : null}
      {result ? <ResultLines result={result} /> : null}

      <div className={styles.actions}>
        {actions.analyze ? (
          <Button onClick={() => void onAnalyze()} disabled={actions.pending}>
            Analyze position
          </Button>
        ) : null}
        {actions.update ? (
          <Button variant="secondary" onClick={() => void onUpdate()} disabled={actions.pending}>
            Update analysis
          </Button>
        ) : null}
        {actions.retry ? (
          <Button onClick={() => void onRetry()} disabled={actions.pending}>
            Retry analysis
          </Button>
        ) : null}
        {actions.observationRetry ? (
          <Button variant="secondary" onClick={onRetryObservation}>
            Retry observation
          </Button>
        ) : null}
      </div>
    </section>
  );
}
