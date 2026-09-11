import { validateFen } from "chess.js";

import { getAnalysis, requestAnalysis as generatedRequestAnalysis } from "../../api/client";
import type { Fen } from "../chess/chessPrimitives";

export const MAX_FEN_LENGTH = 128;

type JsonRecord = Record<string, unknown>;

export type AnalysisStateValue = "not_requested" | "queued" | "running" | "ready";
export type AnalysisScoreKind = "cp" | "mate";
export type AnalysisTerminalKind = "checkmate" | "stalemate" | "insufficient_material";
export type PositionKey = string;

export type AnalysisFailureCode =
  | "invalid_fen"
  | "invalid_quality"
  | "analysis_unavailable"
  | "unexpected_failure";

export type AnalysisLine = {
  rank: number;
  score_kind: AnalysisScoreKind;
  score_value: number;
  wdl_wins: number;
  wdl_draws: number;
  wdl_losses: number;
  pv_uci: string[];
  depth: number;
};

export type AnalysisResult = {
  lines: AnalysisLine[];
  terminal_kind: AnalysisTerminalKind | null;
};

export type AnalysisObservation = {
  fen: Fen;
  state: AnalysisStateValue;
  result: AnalysisResult | null;
};

export type AnalysisRequest = {
  fen: Fen;
  quality: "tool";
};

export type AnalysisFailure = { status: AnalysisFailureCode };
export type AnalysisOperationResult<T> = { status: "success"; data: T } | AnalysisFailure;

export type AnalysisClient = {
  observe: (fen: Fen, signal?: AbortSignal) => Promise<AnalysisOperationResult<AnalysisObservation>>;
  request: (fen: Fen, signal?: AbortSignal) => Promise<AnalysisOperationResult<AnalysisObservation>>;
};

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null;
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function isInteger(value: unknown, minimum = 0): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= minimum;
}

function isCanonicalFen(value: unknown): value is Fen {
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

export function positionKeyFromFen(fen: Fen): PositionKey {
  return fen.split(" ").slice(0, 4).join(" ");
}

function samePositionFen(value: unknown, fen: Fen): value is Fen {
  return isCanonicalFen(value) && positionKeyFromFen(value) === positionKeyFromFen(fen);
}

export function validateAnalysisFen(value: unknown): AnalysisFailureCode | null {
  if (typeof value === "string" && value.length > MAX_FEN_LENGTH) {
    return "invalid_fen";
  }
  return isCanonicalFen(value) ? null : "invalid_fen";
}

function isState(value: unknown): value is AnalysisStateValue {
  return value === "not_requested" || value === "queued" || value === "running" || value === "ready";
}

function isScoreKind(value: unknown): value is AnalysisScoreKind {
  return value === "cp" || value === "mate";
}

function isTerminalKind(value: unknown): value is AnalysisTerminalKind {
  return value === "checkmate" || value === "stalemate" || value === "insufficient_material";
}

function isUciMove(value: unknown): value is string {
  return typeof value === "string" && /^[a-h][1-8][a-h][1-8][qrbn]?$/.test(value);
}

function isLine(value: unknown): value is AnalysisLine {
  if (!isRecord(value)) {
    return false;
  }

  return (
    isInteger(value.rank, 1) &&
    isScoreKind(value.score_kind) &&
    isFiniteNumber(value.score_value) &&
    isInteger(value.wdl_wins) &&
    isInteger(value.wdl_draws) &&
    isInteger(value.wdl_losses) &&
    value.wdl_wins + value.wdl_draws + value.wdl_losses === 1000 &&
    Array.isArray(value.pv_uci) &&
    value.pv_uci.length > 0 &&
    value.pv_uci.every(isUciMove) &&
    isInteger(value.depth)
  );
}

function mapLine(value: JsonRecord): AnalysisLine {
  return {
    rank: value.rank as number,
    score_kind: value.score_kind as AnalysisScoreKind,
    score_value: value.score_value as number,
    wdl_wins: value.wdl_wins as number,
    wdl_draws: value.wdl_draws as number,
    wdl_losses: value.wdl_losses as number,
    pv_uci: [...(value.pv_uci as string[])],
    depth: value.depth as number,
  };
}

function mapResult(value: unknown): AnalysisResult | null {
  if (!isRecord(value) || !Array.isArray(value.lines) || !value.lines.every(isLine)) {
    return null;
  }
  if (value.terminal_kind !== null && !isTerminalKind(value.terminal_kind)) {
    return null;
  }

  return {
    lines: value.lines.map((line) => mapLine(line as JsonRecord)),
    terminal_kind: value.terminal_kind,
  };
}

function mapObservation(value: unknown, requestedFen: Fen): AnalysisObservation | null {
  if (!isRecord(value) || !samePositionFen(value.fen, requestedFen) || !isState(value.state)) {
    return null;
  }
  if (value.result !== null && mapResult(value.result) === null) {
    return null;
  }

  return {
    fen: value.fen,
    state: value.state,
    result: value.result === null ? null : mapResult(value.result),
  };
}

function isFailureCode(value: unknown): value is AnalysisFailureCode {
  return (
    value === "invalid_fen" ||
    value === "invalid_quality" ||
    value === "analysis_unavailable" ||
    value === "unexpected_failure"
  );
}

function failureFromResponse(
  error: unknown,
  status: number | null,
  operation: "observe" | "request",
): AnalysisFailure {
  const code = isRecord(error) && isFailureCode(error.code) ? error.code : null;

  if (status === 422 && (code === "invalid_fen" || (operation === "request" && code === "invalid_quality"))) {
    return { status: code };
  }
  if (status === 503 && code === "analysis_unavailable") {
    return { status: code };
  }
  if (status === 500 && code === "unexpected_failure") {
    return { status: code };
  }
  return { status: "unexpected_failure" };
}

function invalidFenResult<T>(): AnalysisOperationResult<T> {
  return { status: "invalid_fen" };
}

export const fetchAnalysis = async (
  fen: Fen,
  signal?: AbortSignal,
): Promise<AnalysisOperationResult<AnalysisObservation>> => {
  const validationFailure = validateAnalysisFen(fen);
  if (validationFailure !== null) {
    return invalidFenResult();
  }

  const response = await getAnalysis({
    query: { fen },
    signal,
  });
  if (response.data === undefined || response.error !== undefined) {
    return failureFromResponse(response.error, response.response?.status ?? null, "observe");
  }

  const observation = mapObservation(response.data, fen);
  return observation === null ? { status: "unexpected_failure" } : { status: "success", data: observation };
};

export const requestAnalysis = async (
  fen: Fen,
  signal?: AbortSignal,
): Promise<AnalysisOperationResult<AnalysisObservation>> => {
  const validationFailure = validateAnalysisFen(fen);
  if (validationFailure !== null) {
    return invalidFenResult();
  }

  const response = await generatedRequestAnalysis({
    body: { fen, quality: "tool" },
    signal,
  });
  if (response.data === undefined || response.error !== undefined) {
    return failureFromResponse(response.error, response.response?.status ?? null, "request");
  }

  const observation = mapObservation(response.data, fen);
  return observation === null ? { status: "unexpected_failure" } : { status: "success", data: observation };
};

export const defaultAnalysisClient: AnalysisClient = {
  observe: fetchAnalysis,
  request: requestAnalysis,
};
