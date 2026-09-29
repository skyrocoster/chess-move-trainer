import { InlineFeedback } from "../design-system/feedback/InlineFeedback";
import styles from "./StatusView.module.css";

export type WorkerService = "worker" | "worker-six";

export interface WorkerStatus {
  service: WorkerService;
  index: number;
  running: boolean;
}

export interface AnalysisSummary {
  positions: number;
  analyzed: number;
  queued: number;
  running: number;
  remaining: number;
}

export interface StatusDetail {
  workers: WorkerStatus[] | null;
  analysis: AnalysisSummary | null;
  lastGameAt: string | null;
}

export type StatusViewState =
  | { kind: "loading" }
  | { kind: "success"; detail?: StatusDetail }
  | { kind: "error" };

interface StatusViewProps {
  state: StatusViewState;
}

const integerFormat = new Intl.NumberFormat("en-US");

const ANALYSIS_ROWS: { key: keyof AnalysisSummary; label: string }[] = [
  { key: "positions", label: "Positions" },
  { key: "analyzed", label: "Analysed" },
  { key: "queued", label: "Queued" },
  { key: "running", label: "Running" },
  { key: "remaining", label: "Remaining" },
];

function workerFeedback(worker: WorkerStatus): {
  severity: "success" | "information";
  message: string;
} {
  const label = worker.service === "worker" ? "Analysis worker" : `Accelerated worker ${worker.index}`;
  return worker.running
    ? { severity: "success", message: `${label} running.` }
    : { severity: "information", message: `${label} stopped.` };
}

function WorkersStatus({ workers }: { workers: WorkerStatus[] | null }) {
  if (workers === null) {
    return <InlineFeedback severity="information" message="Worker status unavailable." />;
  }
  if (workers.length === 0) {
    return <InlineFeedback severity="information" message="Analysis workers stopped." />;
  }
  return (
    <>
      {workers.map((worker) => (
        <InlineFeedback key={`${worker.service}-${worker.index}`} {...workerFeedback(worker)} />
      ))}
    </>
  );
}

function StatusDetailView({ detail }: { detail: StatusDetail }) {
  const analysis = detail.analysis;

  return (
    <>
      <WorkersStatus workers={detail.workers} />
      <section className={styles.detail} aria-labelledby="analysis-heading">
        <h2 className={styles.subheading} id="analysis-heading">
          Analysis
        </h2>
        {analysis ? (
          <div className={styles.tableScroller} tabIndex={0}>
            <table className={styles.dataTable}>
              <caption className={styles.visuallyHidden}>Analysis progress by position</caption>
              <thead>
                <tr>
                  <th scope="col">Measure</th>
                  <th scope="col" className={styles.number}>
                    Count
                  </th>
                </tr>
              </thead>
              <tbody>
                {ANALYSIS_ROWS.map((row) => (
                  <tr key={row.key}>
                    <th scope="row">{row.label}</th>
                    <td className={styles.number}>{integerFormat.format(analysis[row.key])}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className={styles.muted}>Analysis details unavailable.</p>
        )}
        <p className={styles.lastGame}>
          {detail.lastGameAt
            ? `Last game recorded: ${detail.lastGameAt.slice(0, 10)}`
            : "Last game recorded: unknown"}
        </p>
      </section>
    </>
  );
}

export function StatusView({ state }: StatusViewProps) {
  const feedback =
    state.kind === "loading"
      ? {
          severity: "information" as const,
          message: "Checking backend health…",
          role: "status" as const,
        }
      : state.kind === "success"
        ? {
            severity: "success" as const,
            message: "Backend connected and healthy.",
            role: "status" as const,
          }
        : {
            severity: "error" as const,
            message: "Backend unavailable.",
            role: "alert" as const,
          };

  return (
    <section className={styles.status} data-state={state.kind} aria-labelledby="status-heading">
      <h1 className={styles.heading} id="status-heading">
        System status
      </h1>
      <InlineFeedback {...feedback} />
      {state.kind === "success" && state.detail ? (
        <StatusDetailView detail={state.detail} />
      ) : null}
    </section>
  );
}
