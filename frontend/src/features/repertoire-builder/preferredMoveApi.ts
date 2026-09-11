import { Chess, validateFen, type Square } from "chess.js";

import { deletePreferredMoves, getPreferredMoves, putPreferredMoves } from "../../api/client";
import type {
  PreferredMovesMutationResponse,
  PreferredMovesRemovalResponse,
  PreferredMovesResponse,
  PreferredMovesSegmentResponse,
} from "../../api/client";
import type { Fen } from "../chess/chessPrimitives";

type JsonRecord = Record<string, unknown>;

export type PreferredMoveState = "assigned" | "unassigned";

export type PreferredMoveValue = {
  uci: string;
  san: string;
};

/** The view model retained by the existing Repertoire preferred-move UI. */
export type PreferredMoveResponse = {
  fen: Fen;
  state: PreferredMoveState;
  move: PreferredMoveValue | null;
  effective_at: string | null;
};

/** Clean mutation responses are returned for transport purposes only. */
export type PreferredMoveMutationResponse =
  | PreferredMovesMutationResponse
  | PreferredMovesRemovalResponse;

export type PreferredMoveFailureCode =
  | "invalid_fen"
  | "invalid_from"
  | "invalid_until"
  | "invalid_window"
  | "invalid_effective_from"
  | "invalid_effective_until"
  | "invalid_preference"
  | "invalid_uci"
  | "illegal_move"
  | "preferred_moves_unavailable"
  | "unexpected_failure";

export type PreferredMoveFailure = { status: PreferredMoveFailureCode };
export type PreferredMoveResult =
  | { status: "success"; data: PreferredMoveResponse }
  | PreferredMoveFailure;
export type PreferredMoveMutationResult =
  | { status: "success"; data: PreferredMoveMutationResponse }
  | PreferredMoveFailure;

export type PreferredMoveRequest = {
  fen: Fen;
  move_uci: string;
};

export type PreferredMoveDeleteRequest = {
  fen: Fen;
};

export type PreferredMoveReadOptions = {
  signal?: AbortSignal;
};

export type PreferredMoveMutationOptions = {
  signal?: AbortSignal;
};

export type PreferredMoveReader = (
  fen: Fen,
  options?: PreferredMoveReadOptions,
) => Promise<PreferredMoveResult>;

export type PreferredMoveSetter = (
  request: PreferredMoveRequest,
  options?: PreferredMoveMutationOptions,
) => Promise<PreferredMoveMutationResult>;

export type PreferredMoveRemover = (
  request: PreferredMoveDeleteRequest,
  options?: PreferredMoveMutationOptions,
) => Promise<PreferredMoveMutationResult>;

export type PreferredMoveClient = {
  get: PreferredMoveReader;
  put: PreferredMoveSetter;
  remove: PreferredMoveRemover;
};

export type PreferredMoveDateWindow = {
  today: string;
  tomorrow: string;
};

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null;
}

function hasExactKeys(value: JsonRecord, keys: string[]): boolean {
  return Object.keys(value).sort().join(",") === [...keys].sort().join(",");
}

function isCanonicalFen(value: unknown): value is Fen {
  if (typeof value !== "string" || value !== value.trim() || value.split(" ").length !== 6) {
    return false;
  }
  return validateFen(value).ok;
}

function positionKeyFromFen(fen: Fen): string {
  return fen.split(" ").slice(0, 4).join(" ");
}

function samePositionFen(value: unknown, requestedFen: Fen): value is Fen {
  return isCanonicalFen(value) && positionKeyFromFen(value) === positionKeyFromFen(requestedFen);
}

function isCanonicalUci(value: unknown): value is string {
  return typeof value === "string" && /^[a-h][1-8][a-h][1-8][qrbn]?$/.test(value);
}

function isLegalUci(fen: Fen, value: unknown): value is string {
  if (!isCanonicalUci(value)) {
    return false;
  }

  try {
    const chess = new Chess(fen);
    const move = chess.move({
      from: value.slice(0, 2) as Square,
      to: value.slice(2, 4) as Square,
      ...(value.length === 5 ? { promotion: value.slice(4) as "q" | "r" | "b" | "n" } : {}),
    });
    return `${move.from}${move.to}${move.promotion ?? ""}` === value;
  } catch {
    return false;
  }
}

function sanFromUci(fen: Fen, uci: string): string | null {
  try {
    const chess = new Chess(fen);
    const move = chess.move({
      from: uci.slice(0, 2) as Square,
      to: uci.slice(2, 4) as Square,
      ...(uci.length === 5 ? { promotion: uci.slice(4) as "q" | "r" | "b" | "n" } : {}),
    });
    return move.san;
  } catch {
    return null;
  }
}

function isCleanSegmentPreference(
  value: unknown,
  fen: Fen,
): value is PreferredMovesSegmentResponse["preference"] {
  if (!isRecord(value) || typeof value.kind !== "string") {
    return false;
  }
  if (value.kind === "unconfigured") {
    return hasExactKeys(value, ["kind"]);
  }
  if (value.kind === "no_preference") {
    return hasExactKeys(value, ["kind"]);
  }
  return hasExactKeys(value, ["kind", "uci"]) && isLegalUci(fen, value.uci);
}

function isCompleteSegment(value: unknown, fen: Fen): value is PreferredMovesSegmentResponse {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["from", "until", "preference"]) &&
    typeof value.from === "string" &&
    typeof value.until === "string" &&
    isCleanSegmentPreference(value.preference, fen)
  );
}

function isPreferredMovesResponse(
  value: unknown,
  requestedFen: Fen,
  window: PreferredMoveDateWindow,
): value is PreferredMovesResponse {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, ["fen", "from", "until", "segments"]) ||
    !samePositionFen(value.fen, requestedFen) ||
    value.from !== window.today ||
    value.until !== window.tomorrow ||
    !Array.isArray(value.segments)
  ) {
    return false;
  }

  return value.segments.some(
    (segment) =>
      isCompleteSegment(segment, requestedFen) &&
      segment.from === window.today &&
      segment.until === window.tomorrow,
  );
}

function isMutationPreference(value: unknown, fen: Fen): boolean {
  if (!isRecord(value) || typeof value.kind !== "string") {
    return false;
  }
  if (value.kind === "no_preference") {
    return hasExactKeys(value, ["kind"]);
  }
  return hasExactKeys(value, ["kind", "uci"]) && isLegalUci(fen, value.uci);
}

function isMutationPeriod(value: unknown, fen: Fen): boolean {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["effective_from", "effective_until", "preference"]) &&
    typeof value.effective_from === "string" &&
    (typeof value.effective_until === "string" || value.effective_until === null) &&
    isMutationPreference(value.preference, fen)
  );
}

function isPreferredMovesMutationResponse(
  value: unknown,
  requestedFen: Fen,
): value is PreferredMovesMutationResponse {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["effective_from", "effective_until", "fen", "periods", "preference"]) &&
    typeof value.effective_from === "string" &&
    (typeof value.effective_until === "string" || value.effective_until === null) &&
    samePositionFen(value.fen, requestedFen) &&
    isMutationPreference(value.preference, requestedFen) &&
    Array.isArray(value.periods) &&
    value.periods.every((period) => isMutationPeriod(period, requestedFen))
  );
}

function isPreferredMovesRemovalResponse(
  value: unknown,
  requestedFen: Fen,
): value is PreferredMovesRemovalResponse {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["effective_from", "effective_until", "fen", "periods"]) &&
    typeof value.effective_from === "string" &&
    (typeof value.effective_until === "string" || value.effective_until === null) &&
    samePositionFen(value.fen, requestedFen) &&
    Array.isArray(value.periods) &&
    value.periods.every((period) => isMutationPeriod(period, requestedFen))
  );
}

function isFailureCode(value: unknown): value is PreferredMoveFailureCode {
  return (
    value === "invalid_fen" ||
    value === "invalid_from" ||
    value === "invalid_until" ||
    value === "invalid_window" ||
    value === "invalid_effective_from" ||
    value === "invalid_effective_until" ||
    value === "invalid_preference" ||
    value === "invalid_uci" ||
    value === "illegal_move" ||
    value === "preferred_moves_unavailable" ||
    value === "unexpected_failure"
  );
}

function isErrorBody(value: unknown): value is { code: PreferredMoveFailureCode; message: string } {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["code", "message"]) &&
    isFailureCode(value.code) &&
    typeof value.message === "string"
  );
}

function failureFromOperation(result: unknown): PreferredMoveFailure {
  if (!isRecord(result)) {
    return { status: "unexpected_failure" };
  }

  const response = isRecord(result.response) ? result.response : null;
  const httpStatus = typeof response?.status === "number" ? response.status : null;
  const error = result.error;

  if (httpStatus === 422 && isErrorBody(error) && error.code !== "unexpected_failure") {
    return { status: error.code };
  }
  if (httpStatus === 503 && isErrorBody(error) && error.code === "preferred_moves_unavailable") {
    return { status: error.code };
  }
  if (httpStatus === 500 && isErrorBody(error) && error.code === "unexpected_failure") {
    return { status: error.code };
  }
  return { status: "unexpected_failure" };
}

function validationFailure(fen: Fen): PreferredMoveFailure | null {
  return isCanonicalFen(fen) ? null : { status: "invalid_fen" };
}

function moveValidationFailure(fen: Fen, uci: string): PreferredMoveFailure | null {
  if (!isCanonicalUci(uci)) {
    return { status: "invalid_uci" };
  }
  return isLegalUci(fen, uci) ? null : { status: "illegal_move" };
}

function formatUtcDate(date: Date): string {
  return [date.getUTCFullYear(), date.getUTCMonth() + 1, date.getUTCDate()]
    .map((part, index) =>
      index === 0 ? String(part).padStart(4, "0") : String(part).padStart(2, "0"),
    )
    .join("-");
}

export function getPreferredMoveDateWindow(now = new Date()): PreferredMoveDateWindow {
  const today = formatUtcDate(now);
  const tomorrow = formatUtcDate(
    new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() + 1)),
  );
  return { today, tomorrow };
}

function mappedPreferredMove(
  body: PreferredMovesResponse,
  requestedFen: Fen,
  window: PreferredMoveDateWindow,
): PreferredMoveResponse {
  const segment = body.segments.find(
    (candidate) =>
      isCompleteSegment(candidate, requestedFen) &&
      candidate.from === window.today &&
      candidate.until === window.tomorrow,
  );

  if (!segment) {
    throw new Error("The clean response did not contain the requested one-day segment");
  }

  if (segment.preference.kind === "move") {
    const san = sanFromUci(requestedFen, segment.preference.uci);
    if (san === null) {
      throw new Error("The clean response contained an illegal preferred move");
    }
    return {
      fen: body.fen,
      state: "assigned",
      move: { uci: segment.preference.uci, san },
      effective_at: segment.from,
    };
  }

  return {
    fen: body.fen,
    state: "unassigned",
    move: null,
    effective_at: null,
  };
}

export const fetchPreferredMove: PreferredMoveReader = async (fen, options) => {
  const fenFailure = validationFailure(fen);
  if (fenFailure !== null) {
    return fenFailure;
  }

  const window = getPreferredMoveDateWindow();
  const result = await getPreferredMoves({
    query: { fen, from: window.today, until: window.tomorrow },
    signal: options?.signal,
  });

  if (!isRecord(result) || !("data" in result) || result.data === undefined) {
    return failureFromOperation(result);
  }
  if (!isPreferredMovesResponse(result.data, fen, window)) {
    return { status: "unexpected_failure" };
  }

  try {
    return { status: "success", data: mappedPreferredMove(result.data, fen, window) };
  } catch {
    return { status: "unexpected_failure" };
  }
};

export const putPreferredMove: PreferredMoveSetter = async (request, options) => {
  const fenFailure = validationFailure(request.fen);
  if (fenFailure !== null) {
    return fenFailure;
  }
  const moveFailure = moveValidationFailure(request.fen, request.move_uci);
  if (moveFailure !== null) {
    return moveFailure;
  }

  const window = getPreferredMoveDateWindow();
  const result = await putPreferredMoves({
    body: {
      fen: request.fen,
      effective_from: window.today,
      preference: { kind: "move", uci: request.move_uci },
    },
    signal: options?.signal,
  });

  if (!isRecord(result) || !("data" in result) || result.data === undefined) {
    return failureFromOperation(result);
  }
  return isPreferredMovesMutationResponse(result.data, request.fen)
    ? { status: "success", data: result.data }
    : { status: "unexpected_failure" };
};

export const deletePreferredMove: PreferredMoveRemover = async (request, options) => {
  const fenFailure = validationFailure(request.fen);
  if (fenFailure !== null) {
    return fenFailure;
  }

  const window = getPreferredMoveDateWindow();
  const result = await deletePreferredMoves({
    body: { fen: request.fen, effective_from: window.today },
    signal: options?.signal,
  });

  if (!isRecord(result) || !("data" in result) || result.data === undefined) {
    return failureFromOperation(result);
  }
  return isPreferredMovesRemovalResponse(result.data, request.fen)
    ? { status: "success", data: result.data }
    : { status: "unexpected_failure" };
};

export const defaultPreferredMoveClient: PreferredMoveClient = {
  get: fetchPreferredMove,
  put: putPreferredMove,
  remove: deletePreferredMove,
};
