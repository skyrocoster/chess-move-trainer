import { Chess } from "chess.js";
import { useMemo, useState } from "react";

import type {
  AnalysisClient,
  EvaluationAction,
  EvaluationEligibility,
  EvaluationEnqueue,
  EvaluationObservation,
  EvaluationPoll,
  EvaluationQueueState,
  EvaluationResult,
  EvaluationStatus,
} from "./analysisApi";
import ViewerWorkspace from "./ViewerWorkspace";
import type { GameLookup } from "./positionApi";
import styles from "./Stage1Story.module.css";
import { STAGE1_GAME } from "./stage1GameTypes";

const STAGE5_STORED_FEN = STAGE1_GAME.positions[0].fen;

export type Stage5Scenario = "branch" | "stale" | "failed" | "running";

type Stage5Entry = {
  eligibility: EvaluationEligibility;
  result: EvaluationResult | null;
  state: EvaluationQueueState | null;
  attempts: number;
  errorCode: string | null;
  settlesOnPoll: boolean;
};

type Stage5Event =
  | { kind: "observe"; fen: string }
  | { kind: "enqueue"; action: EvaluationAction; fen: string }
  | { kind: "status"; fen: string; state: EvaluationQueueState | null }
  | { kind: "abort"; fen: string };

const EVENT_TIME = "2026-08-22T00:00:00+00:00";

function resultFor(fen: string): EvaluationResult {
  const chess = new Chess(fen);
  const move = chess.moves({ verbose: true })[0];
  const pv = move ? [`${move.from}${move.to}${move.promotion ?? ""}`] : [];

  return {
    fen,
    profile_id: "mp09-balanced-nodes-v2-200000",
    candidates: move
      ? [
          {
            rank: 1,
            score_kind: "cp",
            score_value: 34,
            wdl_wins: 420,
            wdl_draws: 300,
            wdl_losses: 280,
            pv_uci: pv,
            depth: 20,
            seldepth: 24,
            nodes: 200000,
            engine_time_ms: 100,
          },
        ]
      : [],
    terminal_kind: move ? null : "checkmate",
    completed_at: EVENT_TIME,
    wall_time_ms: 100,
  };
}

function statusFor(entry: Stage5Entry): EvaluationStatus | null {
  if (!entry.state) {
    return null;
  }
  const finished = entry.state === "done" || entry.state === "failed";
  return {
    state: entry.state,
    position: 0,
    attempts: entry.attempts,
    enqueued_at: EVENT_TIME,
    started_at: entry.state === "queued" ? null : EVENT_TIME,
    completed_at: finished ? EVENT_TIME : null,
    error_code: entry.errorCode,
  };
}

function entryFor(scenario: Stage5Scenario): Stage5Entry {
  const result = resultFor(STAGE5_STORED_FEN);
  if (scenario === "stale") {
    return {
      eligibility: "stale",
      result,
      state: null,
      attempts: 1,
      errorCode: null,
      settlesOnPoll: false,
    };
  }
  if (scenario === "failed") {
    return {
      eligibility: "missing",
      result: null,
      state: "failed",
      attempts: 1,
      errorCode: "engine_failure",
      settlesOnPoll: false,
    };
  }
  if (scenario === "running") {
    return {
      eligibility: "missing",
      result: null,
      state: "running",
      attempts: 1,
      errorCode: null,
      settlesOnPoll: false,
    };
  }
  return {
    eligibility: "eligible",
    result,
    state: null,
    attempts: 1,
    errorCode: null,
    settlesOnPoll: false,
  };
}

function createStage5Client(scenario: Stage5Scenario, emit: (event: Stage5Event) => void) {
  const entries = new Map<string, Stage5Entry>();
  entries.set(STAGE5_STORED_FEN, entryFor(scenario));

  function watchAbort(fen: string, signal?: AbortSignal) {
    if (!signal) {
      return;
    }
    const recordAbort = () => emit({ kind: "abort", fen });
    if (signal.aborted) {
      recordAbort();
      return;
    }
    signal.addEventListener("abort", recordAbort, { once: true });
  }

  function observation(fen: string): EvaluationObservation {
    const entry = entries.get(fen) ?? {
      eligibility: "missing",
      result: null,
      state: null,
      attempts: 0,
      errorCode: null,
      settlesOnPoll: false,
    };
    return {
      fen,
      eligibility: entry.eligibility,
      result: entry.result,
      status: statusFor(entry),
      terminal: false,
    };
  }

  const observe: AnalysisClient["observe"] = async (fen, signal) => {
    watchAbort(fen, signal);
    emit({ kind: "observe", fen });
    return { status: "success", data: observation(fen) };
  };

  const enqueue: AnalysisClient["enqueue"] = async (fen, action, signal) => {
    watchAbort(fen, signal);
    emit({ kind: "enqueue", action, fen });
    const existing = entries.get(fen);
    const entry =
      existing ??
      ({
        eligibility: "missing",
        result: null,
        state: null,
        attempts: 0,
        errorCode: null,
        settlesOnPoll: false,
      } satisfies Stage5Entry);
    const allowed =
      (action === "analyze" && (!entry.state || entry.state === "failed") && !entry.result) ||
      (action === "update" &&
        Boolean(entry.result) &&
        entry.state !== "queued" &&
        entry.state !== "running") ||
      (action === "retry" && entry.state === "failed");
    if (!allowed) {
      return { status: "invalid_transition" };
    }

    entry.state = "queued";
    entry.attempts += 1;
    entry.errorCode = null;
    entry.eligibility = entry.result ? "stale" : "missing";
    entry.settlesOnPoll = true;
    entries.set(fen, entry);
    const data: EvaluationEnqueue = {
      fen,
      action,
      outcome: action === "analyze" ? "queued" : action === "update" ? "requeued" : "retried",
      eligibility: entry.eligibility,
      status: statusFor(entry)!,
    };
    return { status: "success", data };
  };

  const status: AnalysisClient["status"] = async (fen, signal) => {
    watchAbort(fen, signal);
    const entry = entries.get(fen);
    if (entry?.state === "queued" && entry.settlesOnPoll) {
      entry.state = "done";
      entry.eligibility = "eligible";
      entry.result = entry.result ?? resultFor(fen);
      entry.settlesOnPoll = false;
    }
    const state = entry?.state ?? null;
    emit({ kind: "status", fen, state });
    const data: EvaluationPoll = {
      fen,
      state,
      completed_at: state === "done" || state === "failed" ? EVENT_TIME : null,
      error_code: entry?.errorCode ?? null,
    };
    return { status: "success", data };
  };

  return { observe, enqueue, status } satisfies AnalysisClient;
}

const completeGameLookup: GameLookup = async (_uuid, initialPly) => ({
  status: "success",
  game: { ...STAGE1_GAME, initial_ply: initialPly ?? 0 },
});

export function Stage5AnalysisStory({ scenario }: { scenario: Stage5Scenario }) {
  const [events, setEvents] = useState<Stage5Event[]>([]);
  const client = useMemo(
    () => createStage5Client(scenario, (event) => setEvents((current) => [...current, event])),
    [scenario],
  );
  const enqueues = events.filter((event) => event.kind === "enqueue");
  const aborts = events.filter((event) => event.kind === "abort");

  return (
    <main className={styles.frame}>
      <ViewerWorkspace
        lookup={completeGameLookup}
        analysisClient={client}
        analysisPollIntervalMs={50}
      />
      <section
        aria-label="Stage 5 proof diagnostics"
        style={{ margin: "1rem auto", maxWidth: "66rem" }}
      >
        <h2>Stage 5 proof diagnostics</h2>
        <p data-testid="stage5-enqueue-log">
          {enqueues.length === 0
            ? "No deliberate analysis actions"
            : enqueues.map((event) => `${event.action}: ${event.fen}`).join(" | ")}
        </p>
        <p data-testid="stage5-abort-log">
          {aborts.length === 0
            ? "No aborted observations"
            : `${aborts.length} aborted observation(s)`}
        </p>
      </section>
    </main>
  );
}

export type { Stage5Event };
