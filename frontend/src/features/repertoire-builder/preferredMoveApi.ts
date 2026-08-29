import { Chess, validateFen, type Square } from "chess.js";

import type { Fen } from "../viewer/chessPrimitives";

const API_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5666";

type JsonRecord = Record<string, unknown>;

export type PreferredMoveState = "assigned" | "unassigned";

export type PreferredMoveValue = {
  uci: string;
  san: string;
};

export type PreferredMoveResponse = {
  fen: Fen;
  state: PreferredMoveState;
  move: PreferredMoveValue | null;
};

export type PreferredMoveMutationResponse = {
  fen: Fen;
  changed: boolean;
  effective_at: string;
};

export type PreferredMoveFailureCode =
  | "invalid_fen"
  | "invalid_move"
  | "invalid_timestamp"
  | "future_effective_time"
  | "position_not_found"
  | "preferred_move_unavailable"
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
  effective_at?: string | null;
};

export type PreferredMoveDeleteRequest = {
  fen: Fen;
  effective_at?: string | null;
};

export type PreferredMoveReadOptions = {
  asOf?: string;
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

function isCanonicalLegalUci(fen: Fen, value: unknown): value is string {
  if (typeof value !== "string" || !/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(value)) {
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

function isPreferredMoveValue(value: unknown, fen: Fen): value is PreferredMoveValue {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["uci", "san"]) &&
    isCanonicalLegalUci(fen, value.uci) &&
    typeof value.san === "string" &&
    value.san.length > 0
  );
}

function isPreferredMoveResponse(
  value: unknown,
  requestedFen: Fen,
): value is PreferredMoveResponse {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, ["fen", "state", "move"]) ||
    !samePositionFen(value.fen, requestedFen)
  ) {
    return false;
  }

  if (value.state === "unassigned") {
    return value.move === null;
  }
  return value.state === "assigned" && isPreferredMoveValue(value.move, requestedFen);
}

function isPreferredMoveMutationResponse(
  value: unknown,
  requestedFen: Fen,
): value is PreferredMoveMutationResponse {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["fen", "changed", "effective_at"]) &&
    samePositionFen(value.fen, requestedFen) &&
    typeof value.changed === "boolean" &&
    typeof value.effective_at === "string"
  );
}

function isFailureCode(value: unknown): value is PreferredMoveFailureCode {
  return (
    value === "invalid_fen" ||
    value === "invalid_move" ||
    value === "invalid_timestamp" ||
    value === "future_effective_time" ||
    value === "position_not_found" ||
    value === "preferred_move_unavailable" ||
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

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function failureFromResponse(status: number, body: unknown): PreferredMoveFailure {
  if (
    status === 422 &&
    isErrorBody(body) &&
    (body.code === "invalid_fen" ||
      body.code === "invalid_move" ||
      body.code === "invalid_timestamp" ||
      body.code === "future_effective_time")
  ) {
    return { status: body.code };
  }
  if (status === 404 && isErrorBody(body) && body.code === "position_not_found") {
    return { status: body.code };
  }
  if (status === 503 && isErrorBody(body) && body.code === "preferred_move_unavailable") {
    return { status: body.code };
  }
  if (status === 500 && isErrorBody(body) && body.code === "unexpected_failure") {
    return { status: body.code };
  }
  return { status: "unexpected_failure" };
}

function validateFenRequest(fen: Fen): PreferredMoveFailure | null {
  return isCanonicalFen(fen) ? null : { status: "invalid_fen" };
}

export const fetchPreferredMove: PreferredMoveReader = async (fen, options) => {
  const validationFailure = validateFenRequest(fen);
  if (validationFailure !== null) {
    return validationFailure;
  }

  const asOf = options?.asOf === undefined ? "" : `&as_of=${encodeURIComponent(options.asOf)}`;
  const response = await fetch(
    `${API_URL}/api/preferred-move?fen=${encodeURIComponent(fen)}${asOf}`,
    { signal: options?.signal },
  );
  const body = await readJson(response);

  if (!response.ok) {
    return failureFromResponse(response.status, body);
  }
  return isPreferredMoveResponse(body, fen)
    ? { status: "success", data: body }
    : { status: "unexpected_failure" };
};

export const putPreferredMove: PreferredMoveSetter = async (request, options) => {
  const fenFailure = validateFenRequest(request.fen);
  if (fenFailure !== null) {
    return fenFailure;
  }
  if (!isCanonicalLegalUci(request.fen, request.move_uci)) {
    return { status: "invalid_move" };
  }

  const response = await fetch(`${API_URL}/api/preferred-move`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal: options?.signal,
  });
  const body = await readJson(response);

  if (!response.ok) {
    return failureFromResponse(response.status, body);
  }
  return isPreferredMoveMutationResponse(body, request.fen)
    ? { status: "success", data: body }
    : { status: "unexpected_failure" };
};

export const deletePreferredMove: PreferredMoveRemover = async (request, options) => {
  const fenFailure = validateFenRequest(request.fen);
  if (fenFailure !== null) {
    return fenFailure;
  }

  const effectiveAt =
    request.effective_at === undefined || request.effective_at === null
      ? ""
      : `&effective_at=${encodeURIComponent(request.effective_at)}`;
  const response = await fetch(
    `${API_URL}/api/preferred-move?fen=${encodeURIComponent(request.fen)}${effectiveAt}`,
    { method: "DELETE", signal: options?.signal },
  );
  const body = await readJson(response);

  if (!response.ok) {
    return failureFromResponse(response.status, body);
  }
  return isPreferredMoveMutationResponse(body, request.fen)
    ? { status: "success", data: body }
    : { status: "unexpected_failure" };
};

export const defaultPreferredMoveClient: PreferredMoveClient = {
  get: fetchPreferredMove,
  put: putPreferredMove,
  remove: deletePreferredMove,
};
