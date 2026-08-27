import { Button } from "../design-system/Button";
import styles from "./AnalysisPanel.module.css";

export type AnalysisPanelWdlValue = {
  percentage: number;
  label: string;
};

export type AnalysisPanelWdl = {
  wins: AnalysisPanelWdlValue;
  draws: AnalysisPanelWdlValue;
  losses: AnalysisPanelWdlValue;
  accessibleLabel: string;
};

export type AnalysisPanelLine = {
  rank: number;
  score: string;
  pv: string;
  wdl: AnalysisPanelWdl;
};

export type AnalysisPanelResultMetadata = {
  displayedPly: number | null;
  depth: number | null;
  candidateCount: number;
};

export type AnalysisPanelResult = {
  stale: boolean;
  lines: AnalysisPanelLine[];
  metadata: AnalysisPanelResultMetadata;
};

export type AnalysisPanelDisplay = {
  stateLabel: string;
  error: string | null;
  actionError: string | null;
  message: { text: string; alert: boolean } | null;
  result: AnalysisPanelResult | null;
  actions: {
    analyze: boolean;
    update: boolean;
    retry: boolean;
    observationRetry: boolean;
    pending: boolean;
  };
};

export type AnalysisPanelIntent = () => void | Promise<void>;

export type AnalysisPanelProps = {
  display: AnalysisPanelDisplay;
  onAnalyze: AnalysisPanelIntent;
  onUpdate: AnalysisPanelIntent;
  onRetry: AnalysisPanelIntent;
  onRetryObservation: () => void;
};

type WdlItem = {
  label: string;
  value: AnalysisPanelWdlValue;
  className: string;
};

function wdlItems(wdl: AnalysisPanelWdl): WdlItem[] {
  return [
    { label: "Win", value: wdl.wins, className: styles.wdlWin },
    { label: "Draw", value: wdl.draws, className: styles.wdlDraw },
    { label: "Loss", value: wdl.losses, className: styles.wdlLoss },
  ];
}

function WdlTrack({
  wdl,
  compact = false,
  label,
}: {
  wdl: AnalysisPanelWdl;
  compact?: boolean;
  label?: string;
}) {
  return (
    <div
      className={compact ? styles.miniTrack : styles.wdlTrack}
      role="img"
      aria-label={label ?? wdl.accessibleLabel}
    >
      <span
        className={styles.wdlWin}
        style={{ inlineSize: `${wdl.wins.percentage}%` }}
        aria-hidden="true"
      />
      <span
        className={styles.wdlDraw}
        style={{ inlineSize: `${wdl.draws.percentage}%` }}
        aria-hidden="true"
      />
      <span
        className={styles.wdlLoss}
        style={{ inlineSize: `${wdl.losses.percentage}%` }}
        aria-hidden="true"
      />
    </div>
  );
}

function WdlLegend({ wdl }: { wdl: AnalysisPanelWdl }) {
  return (
    <dl className={styles.wdlLegend}>
      {wdlItems(wdl).map((item) => (
        <div key={item.label}>
          <dt>
            <span className={`${styles.legendDot} ${item.className}`} aria-hidden="true" />
            {item.label}
          </dt>
          <dd>{item.value.label}</dd>
        </div>
      ))}
    </dl>
  );
}

function InlineWdl({ wdl }: { wdl: AnalysisPanelWdl }) {
  return (
    <p className={styles.lineWdl}>
      {wdlItems(wdl).map((item) => (
        <span key={item.label}>
          <span className={`${styles.legendDot} ${item.className}`} aria-hidden="true" />
          {item.label} <strong>{item.value.label}</strong>
        </span>
      ))}
    </p>
  );
}

function resultMetadataLabel(metadata: AnalysisPanelResultMetadata): string {
  const details = [
    metadata.displayedPly === null ? null : `ply ${metadata.displayedPly}`,
    metadata.depth === null ? null : `depth ${metadata.depth}`,
    `${metadata.candidateCount} ${metadata.candidateCount === 1 ? "line" : "lines"}`,
  ].filter((detail): detail is string => detail !== null);

  return `Displayed position${details.length > 0 ? ` · ${details.join(" · ")}` : ""}`;
}

function ResultPresentation({ result }: { result: NonNullable<AnalysisPanelDisplay["result"]> }) {
  const [bestLine, ...alternativeLines] = result.lines;

  return (
    <div className={styles.result}>
      {result.stale ? (
        <p className={styles.staleMessage} role="note">
          <span className={styles.messageIcon} aria-hidden="true">
            !
          </span>
          <span>This result is from an earlier position. Update deliberately to refresh it.</span>
        </p>
      ) : null}
      {bestLine ? (
        <>
          <section className={styles.bestLine} aria-labelledby="best-line-heading">
            <div className={styles.bestLineHeader}>
              <h3 className={styles.bestLineLabel} id="best-line-heading">
                Best line
              </h3>
              <strong className={styles.bestLineScore} aria-label={`Evaluation ${bestLine.score}`}>
                {bestLine.score}
              </strong>
            </div>
            <p className={styles.bestLineMoves}>{bestLine.pv}</p>

            <figure className={styles.wdlFigure} aria-labelledby="analysis-wdl-caption">
              <figcaption className={styles.wdlCaption} id="analysis-wdl-caption">
                <span>Win / draw / loss</span>
                <span>engine distribution</span>
              </figcaption>
              <WdlTrack wdl={bestLine.wdl} />
              <WdlLegend wdl={bestLine.wdl} />
            </figure>
          </section>

          {alternativeLines.length > 0 ? (
            <section className={styles.ledger} aria-labelledby="ranked-lines-heading">
              <div className={styles.sectionHeading}>
                <h3 id="ranked-lines-heading">Ranked candidate lines</h3>
                <p className={styles.sectionNote}>Best score first</p>
              </div>
              <ol className={styles.lineList} aria-label="Ranked analysis lines">
                {alternativeLines.map((line) => (
                  <li className={styles.line} key={line.rank}>
                    <span className={styles.lineRank}>{String(line.rank).padStart(2, "0")}</span>
                    <div className={styles.lineBody}>
                      <p className={styles.linePv}>{line.pv}</p>
                      <WdlTrack
                        wdl={line.wdl}
                        compact
                        label={`Line ${line.rank}: ${line.wdl.accessibleLabel}`}
                      />
                      <InlineWdl wdl={line.wdl} />
                    </div>
                    <p className={styles.lineEval}>
                      {line.score}
                      <span className={styles.scoreLabel}>evaluation</span>
                    </p>
                  </li>
                ))}
              </ol>
            </section>
          ) : null}
        </>
      ) : (
        <p className={styles.emptyResult} role="note">
          No candidate lines are available for this terminal position.
        </p>
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
      <header className={styles.header}>
        <div className={styles.panelTitle}>
          <p className={styles.eyebrow}>Engine output</p>
          <h2 id="analysis-panel-heading">Analysis</h2>
          {result ? <p className={styles.meta}>{resultMetadataLabel(result.metadata)}</p> : null}
        </div>
        <p className={styles.state} role="status" aria-live="polite">
          {stateLabel}
        </p>
      </header>

      {error ? (
        <p className={styles.observationError} role="alert">
          {error}
        </p>
      ) : null}
      {actionError ? (
        <p className={styles.actionError} role="alert">
          {actionError}
        </p>
      ) : null}
      {message ? (
        <p
          className={message.alert ? styles.alertMessage : styles.message}
          role={message.alert ? "alert" : "note"}
        >
          {message.text}
        </p>
      ) : null}
      {result ? <ResultPresentation result={result} /> : null}

      <div className={styles.actionRow}>
        {actions.update ? (
          <p className={styles.updateHelp} id="analysis-update-help">
            Refreshes analysis for this displayed position only.
          </p>
        ) : null}
        <div className={styles.actions}>
          {actions.analyze ? (
            <Button onClick={() => void onAnalyze()} disabled={actions.pending}>
              Analyze position
            </Button>
          ) : null}
          {actions.update ? (
            <Button
              variant="secondary"
              onClick={() => void onUpdate()}
              disabled={actions.pending}
              aria-describedby="analysis-update-help"
            >
              <span className={styles.buttonIcon} aria-hidden="true">
                ↻
              </span>
              <span>Update analysis</span>
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
      </div>
    </section>
  );
}
