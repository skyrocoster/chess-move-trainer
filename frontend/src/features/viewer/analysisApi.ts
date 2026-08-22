import { validateFen } from "chess.js";

const API_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5666";
export const MAX_FEN_LENGTH = 128;

type JsonRecord = Record<string, unknown>;

export type EvaluationEligibility = "missing" | "eligible" | "stale";
export type EvaluationQueueState = "queued" | "running" | "done" | "failed";
export type EvaluationAction = "analyze" | "update" | "retry";
export type EvaluationScoreKind = "cp" | "mate" | "mate_given";
export type EvaluationErrorCode =
  | "evaluation_unavailable"
  | "invalid_fen"
  | "request_too_large"
  | "invalid_action"
  | "invalid_transition"
  | "evaluation_busy"
  | "unexpected_failure";

export type EvaluationCandidate = {
  rank: number;
  score_kind: EvaluationScoreKind;
  score_value: number;
  wdl_wins: number;
  wdl_draws: number;
  wdl_losses: number;
  pv_uci: string[];
  depth: number;
  seldepth: number;
  nodes: number;
  engine_time_ms: number;
};

export type EvaluationResult = {
  fen: string;
  profile_id: string;
  candidates: EvaluationCandidate[];
  terminal_kind: string | null;
  completed_at: string;
  wall_time_ms: number;
};

export type EvaluationStatus = {
  state: EvaluationQueueState;
  position: number;
  attempts: number;
  enqueued_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_code: string | null;
};

export type EvaluationObservation = {
  fen: string;
  eligibility: EvaluationEligibility;
  result: EvaluationResult | null;
  status: EvaluationStatus | null;
  terminal: boolean;
};

export type EvaluationEnqueue = {
  fen: string;
  action: EvaluationAction;
  outcome: string;
  eligibility: EvaluationEligibility;
  status: EvaluationStatus;
};

export type EvaluationPoll = {
  fen: string;
  state: EvaluationQueueState | null;
  completed_at: string | null;
  error_code: string | null;
};

export type AnalysisFailure = { status: EvaluationErrorCode };
export type AnalysisResult<T> = { status: "success"; data: T } | AnalysisFailure;

export type AnalysisClient = {
  observe: (fen: string, signal?: AbortSignal) => Promise<AnalysisResult<EvaluationObservation>>;
  enqueue: (
    fen: string,
    action: EvaluationAction,
    signal?: AbortSignal,
  ) => Promise<AnalysisResult<EvaluationEnqueue>>;
  status: (fen: string, signal?: AbortSignal) => Promise<AnalysisResult<EvaluationPoll>>;
};

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null;
}

function hasExactKeys(value: JsonRecord, keys: string[]): boolean {
  return Object.keys(value).sort().join(",") === [...keys].sort().join(",");
}

function isInteger(value: unknown, minimum = 0): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= minimum;
}

function isCanonicalFen(value: unknown): value is string {
  if (
    typeof value !== "string" ||
    value.length > MAX_FEN_LENGTH ||
    value !== value.trim() ||
    value.split(" ").length !== 6
  ) {
    return false;
  }
  return validateFen(value).ok;
}

export function validateAnalysisFen(value: unknown): EvaluationErrorCode | null {
  if (typeof value === "string" && value.length > MAX_FEN_LENGTH) {
    return "request_too_large";
  }
  return isCanonicalFen(value) ? null : "invalid_fen";
}

function isEligibility(value: unknown): value is EvaluationEligibility {
  return value === "missing" || value === "eligible" || value === "stale";
}

function isQueueState(value: unknown): value is EvaluationQueueState {
  return value === "queued" || value === "running" || value === "done" || value === "failed";
}

function isAction(value: unknown): value is EvaluationAction {
  return value === "analyze" || value === "update" || value === "retry";
}

function isScoreKind(value: unknown): value is EvaluationScoreKind {
  return value === "cp" || value === "mate" || value === "mate_given";
}

function isStringOrNull(value: unknown): value is string | null {
  return value === null || typeof value === "string";
}

function isCandidate(value: unknown): value is EvaluationCandidate {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, [
      "rank",
      "score_kind",
      "score_value",
      "wdl_wins",
      "wdl_draws",
      "wdl_losses",
      "pv_uci",
      "depth",
      "seldepth",
      "nodes",
      "engine_time_ms",
    ])
  ) {
    return false;
  }
  if (
    !isInteger(value.rank, 1) ||
    value.rank > 5 ||
    !isScoreKind(value.score_kind) ||
    !isInteger(value.score_value, Number.MIN_SAFE_INTEGER) ||
    !isInteger(value.wdl_wins) ||
    !isInteger(value.wdl_draws) ||
    !isInteger(value.wdl_losses) ||
    value.wdl_wins + value.wdl_draws + value.wdl_losses !== 1000 ||
    !Array.isArray(value.pv_uci) ||
    value.pv_uci.length === 0 ||
    !value.pv_uci.every(
      (move) => typeof move === "string" && /^[a-h][1-8][a-h][1-8][qrbn]?$/.test(move),
    ) ||
    !isInteger(value.depth) ||
    !isInteger(value.seldepth) ||
    !isInteger(value.nodes, 1) ||
    !isInteger(value.engine_time_ms)
  ) {
    return false;
  }
  return value.score_kind !== "mate_given" || value.score_value === 0;
}

function isResult(value: unknown, fen: string): value is EvaluationResult {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, [
      "fen",
      "profile_id",
      "candidates",
      "terminal_kind",
      "completed_at",
      "wall_time_ms",
    ]) ||
    value.fen !== fen ||
    typeof value.profile_id !== "string" ||
    value.profile_id.length === 0 ||
    !Array.isArray(value.candidates) ||
    value.candidates.length > 5 ||
    !value.candidates.every(isCandidate) ||
    !isStringOrNull(value.terminal_kind) ||
    typeof value.completed_at !== "string" ||
    !isInteger(value.wall_time_ms)
  ) {
    return false;
  }
  return value.candidates.every((candidate, index) => candidate.rank === index + 1);
}

function isEvaluationStatus(value: unknown): value is EvaluationStatus {
  return (
    isRecord(value) &&
    hasExactKeys(value, [
      "state",
      "position",
      "attempts",
      "enqueued_at",
      "started_at",
      "completed_at",
      "error_code",
    ]) &&
    isQueueState(value.state) &&
    isInteger(value.position) &&
    isInteger(value.attempts) &&
    typeof value.enqueued_at === "string" &&
    isStringOrNull(value.started_at) &&
    isStringOrNull(value.completed_at) &&
    isStringOrNull(value.error_code)
  );
}

function isObservation(value: unknown, fen: string): value is EvaluationObservation {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["fen", "eligibility", "result", "status", "terminal"]) &&
    value.fen === fen &&
    isEligibility(value.eligibility) &&
    (value.result === null || isResult(value.result, fen)) &&
    (value.status === null || isEvaluationStatus(value.status)) &&
    typeof value.terminal === "boolean"
  );
}

function isEnqueue(value: unknown, fen: string): value is EvaluationEnqueue {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["fen", "action", "outcome", "eligibility", "status"]) &&
    value.fen === fen &&
    isAction(value.action) &&
    typeof value.outcome === "string" &&
    value.outcome.length > 0 &&
    isEligibility(value.eligibility) &&
    isEvaluationStatus(value.status)
  );
}

function isPoll(value: unknown, fen: string): value is EvaluationPoll {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["fen", "state", "completed_at", "error_code"]) &&
    value.fen === fen &&
    (value.state === null || isQueueState(value.state)) &&
    isStringOrNull(value.completed_at) &&
    isStringOrNull(value.error_code)
  );
}

function isErrorCode(value: unknown): value is EvaluationErrorCode {
  return (
    value === "evaluation_unavailable" ||
    value === "invalid_fen" ||
    value === "request_too_large" ||
    value === "invalid_action" ||
    value === "invalid_transition" ||
    value === "evaluation_busy" ||
    value === "unexpected_failure"
  );
}

function isErrorBody(value: unknown): value is { code: EvaluationErrorCode; message: string } {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["code", "message"]) &&
    isErrorCode(value.code) &&
    typeof value.message === "string"
  );
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

async function requestJson(
  input: RequestInfo | URL,
  init: RequestInit | undefined,
  signal: AbortSignal | undefined,
): Promise<{ response: Response; body: unknown }> {
  const response = await fetch(input, { ...init, signal });
  return { response, body: await readJson(response) };
}

function failureFromResponse(status: number, body: unknown): AnalysisFailure {
  if (status >= 400 && isErrorBody(body)) {
    return { status: body.code };
  }
  return { status: "unexpected_failure" };
}

function validFenOrFailure(fen: string): AnalysisFailure | null {
  const status = validateAnalysisFen(fen);
  return status === null ? null : { status };
}

export const fetchEvaluation = async (
  fen: string,
  signal?: AbortSignal,
): Promise<AnalysisResult<EvaluationObservation>> => {
  const failure = validFenOrFailure(fen);
  if (failure) {
    return failure;
  }
  const { response, body } = await requestJson(
    `${API_URL}/api/evaluation?fen=${encodeURIComponent(fen)}`,
    undefined,
    signal,
  );
  if (!response.ok) {
    return failureFromResponse(response.status, body);
  }
  return isObservation(body, fen)
    ? { status: "success", data: body }
    : { status: "unexpected_failure" };
};

export const enqueueEvaluation = async (
  fen: string,
  action: EvaluationAction,
  signal?: AbortSignal,
): Promise<AnalysisResult<EvaluationEnqueue>> => {
  const fenFailure = validFenOrFailure(fen);
  if (fenFailure) {
    return fenFailure;
  }
  if (!isAction(action)) {
    return { status: "invalid_action" };
  }
  const { response, body } = await requestJson(
    `${API_URL}/api/evaluation`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fen, action }),
    },
    signal,
  );
  if (!response.ok) {
    return failureFromResponse(response.status, body);
  }
  return isEnqueue(body, fen)
    ? { status: "success", data: body }
    : { status: "unexpected_failure" };
};

export const fetchEvaluationStatus = async (
  fen: string,
  signal?: AbortSignal,
): Promise<AnalysisResult<EvaluationPoll>> => {
  const failure = validFenOrFailure(fen);
  if (failure) {
    return failure;
  }
  const { response, body } = await requestJson(
    `${API_URL}/api/evaluation/status?fen=${encodeURIComponent(fen)}`,
    undefined,
    signal,
  );
  if (!response.ok) {
    return failureFromResponse(response.status, body);
  }
  return isPoll(body, fen) ? { status: "success", data: body } : { status: "unexpected_failure" };
};

export const defaultAnalysisClient: AnalysisClient = {
  observe: fetchEvaluation,
  enqueue: enqueueEvaluation,
  status: fetchEvaluationStatus,
};
