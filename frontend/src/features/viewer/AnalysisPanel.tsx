import { Chess } from "chess.js";

import { Button } from "../design-system/Button";
import type { AnalysisClient, EvaluationCandidate, EvaluationResult } from "./analysisApi";
import type { Fen } from "./chessPrimitives";
import { formatScore } from "./analysisFormatting";
import { type AnalysisState, useAnalysisState } from "./analysisState";
import styles from "./AnalysisPanel.module.css";

export type AnalysisPanelProps = {
  fen: Fen;
  client?: AnalysisClient;
  pollIntervalMs?: number;
  analysisState?: AnalysisState;
};

function formatPercentage(value: number): string {
  return `${(value / 10).toFixed(1)}%`;
}

function formatWdl(candidate: EvaluationCandidate): string {
  return `W ${formatPercentage(candidate.wdl_wins)} / D ${formatPercentage(
    candidate.wdl_draws,
  )} / L ${formatPercentage(candidate.wdl_losses)}`;
}

function moveFromUci(uci: string) {
  const promotion = uci.length === 5 ? (uci[4] as "q" | "r" | "b" | "n") : undefined;
  return {
    from: uci.slice(0, 2),
    to: uci.slice(2, 4),
    ...(promotion ? { promotion } : {}),
  };
}

function formatPv(fen: Fen, pv: string[]): string {
  const chess = new Chess(fen);
  const sanMoves: string[] = [];

  pv.forEach((uci, index) => {
    const fields = chess.fen().split(" ");
    const moveNumber = fields[5];
    const whiteToMove = chess.turn() === "w";
    const move = chess.move(moveFromUci(uci));
    const prefix = whiteToMove ? `${moveNumber}. ` : index === 0 ? `${moveNumber}... ` : "";
    sanMoves.push(`${prefix}${move.san}`);
  });

  return sanMoves.join(" ");
}

function displayPv(result: EvaluationResult, candidate: EvaluationCandidate): string {
  try {
    return formatPv(result.fen, candidate.pv_uci);
  } catch {
    return "Line unavailable";
  }
}

function ResultLines({ result, stale }: { result: EvaluationResult; stale: boolean }) {
  return (
    <div className={styles.result}>
      {stale ? (
        <p className={styles.stale}>Stale analysis; update deliberately to refresh it.</p>
      ) : null}
      {result.candidates.length === 0 ? (
        <p className={styles.emptyResult}>
          No candidate lines are available for this terminal position.
        </p>
      ) : (
        <ol className={styles.lines} aria-label="Ranked analysis lines">
          {result.candidates.slice(0, 5).map((candidate) => (
            <li className={styles.line} key={candidate.rank}>
              <div className={styles.lineHeading}>
                <span>Line {candidate.rank}</span>
                <strong>{formatScore(candidate)}</strong>
              </div>
              <p className={styles.pv}>{displayPv(result, candidate)}</p>
              <p className={styles.wdl}>{formatWdl(candidate)}</p>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

export function AnalysisPanel({ fen, client, pollIntervalMs, analysisState }: AnalysisPanelProps) {
  const ownedState = useAnalysisState(analysisState ? null : fen, client, pollIntervalMs);
  const state = analysisState ?? ownedState;
  const {
    observation,
    loading,
    error,
    actionError,
    actionPending,
    handleAction,
    retryObservation,
  } = state;

  const status = observation?.status?.state;
  const result = observation?.result;
  const stale = observation?.eligibility === "stale" || status === "queued" || status === "running";
  const showAnalyze = !loading && observation?.eligibility === "missing" && !status;
  const showUpdate =
    !loading &&
    Boolean(result) &&
    status !== "queued" &&
    status !== "running" &&
    status !== "failed";
  const showRetry = !loading && status === "failed";
  const showObservationRetry = !loading && Boolean(error);

  let stateLabel = "Loading evaluation…";
  if (!loading && error) {
    stateLabel = "Evaluation unavailable";
  } else if (status === "queued") {
    stateLabel = "Analysis queued";
  } else if (status === "running") {
    stateLabel = "Analysis running";
  } else if (status === "failed") {
    stateLabel = "Analysis failed";
  } else if (result) {
    stateLabel = stale ? "Stale analysis" : "Analysis complete";
  } else if (showAnalyze) {
    stateLabel = "Analysis available on request";
  }

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
      {status === "queued" ? (
        <p className={styles.message}>This position is waiting for analysis.</p>
      ) : null}
      {status === "running" ? <p className={styles.message}>Analysis is in progress.</p> : null}
      {status === "failed" ? (
        <p className={styles.message} role="alert">
          No complete result was published. Retry deliberately when ready.
        </p>
      ) : null}
      {showAnalyze ? (
        <p className={styles.message}>
          Analyze this displayed position deliberately to request a result.
        </p>
      ) : null}
      {result ? <ResultLines result={result} stale={stale} /> : null}

      <div className={styles.actions}>
        {showAnalyze ? (
          <Button onClick={() => void handleAction("analyze")} disabled={actionPending}>
            Analyze position
          </Button>
        ) : null}
        {showUpdate ? (
          <Button
            variant="secondary"
            onClick={() => void handleAction("update")}
            disabled={actionPending}
          >
            Update analysis
          </Button>
        ) : null}
        {showRetry ? (
          <Button onClick={() => void handleAction("retry")} disabled={actionPending}>
            Retry analysis
          </Button>
        ) : null}
        {showObservationRetry ? (
          <Button variant="secondary" onClick={retryObservation}>
            Retry observation
          </Button>
        ) : null}
      </div>
    </section>
  );
}
