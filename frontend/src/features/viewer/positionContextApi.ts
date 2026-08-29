import { validateFen } from "chess.js";

import type { Fen } from "./chessPrimitives";

const API_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5666";

type JsonRecord = Record<string, unknown>;

export type PositionContextResponse = {
  fen: Fen;
  overall_exists: boolean;
  white_count: number;
  black_count: number;
};

export type PositionContextFailureCode =
  | "invalid_fen"
  | "position_context_unavailable"
  | "unexpected_failure";

export type PositionContextFailure = { status: PositionContextFailureCode };
export type PositionContextResult =
  | { status: "success"; data: PositionContextResponse }
  | PositionContextFailure;

export type PositionContextClient = (
  fen: Fen,
  signal?: AbortSignal,
) => Promise<PositionContextResult>;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null;
}

function hasExactKeys(value: JsonRecord, keys: string[]): boolean {
  return Object.keys(value).sort().join(",") === [...keys].sort().join(",");
}

function isNonnegativeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
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

function isPositionContextResponse(
  value: unknown,
  requestedFen: Fen,
): value is PositionContextResponse {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["fen", "overall_exists", "white_count", "black_count"]) &&
    samePositionFen(value.fen, requestedFen) &&
    typeof value.overall_exists === "boolean" &&
    isNonnegativeInteger(value.white_count) &&
    isNonnegativeInteger(value.black_count)
  );
}

function isFailureCode(value: unknown): value is PositionContextFailureCode {
  return (
    value === "invalid_fen" ||
    value === "position_context_unavailable" ||
    value === "unexpected_failure"
  );
}

function isErrorBody(
  value: unknown,
): value is { code: PositionContextFailureCode; message: string } {
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

function failureFromResponse(status: number, body: unknown): PositionContextFailure {
  if (status === 422 && isErrorBody(body) && body.code === "invalid_fen") {
    return { status: body.code };
  }
  if (status === 503 && isErrorBody(body) && body.code === "position_context_unavailable") {
    return { status: body.code };
  }
  if (status === 500 && isErrorBody(body) && body.code === "unexpected_failure") {
    return { status: body.code };
  }
  return { status: "unexpected_failure" };
}

export function validatePositionContextFen(value: unknown): PositionContextFailureCode | null {
  return isCanonicalFen(value) ? null : "invalid_fen";
}

export const fetchPositionContext: PositionContextClient = async (fen, signal) => {
  const validationFailure = validatePositionContextFen(fen);
  if (validationFailure !== null) {
    return { status: validationFailure };
  }

  const response = await fetch(`${API_URL}/api/position-context?fen=${encodeURIComponent(fen)}`, {
    signal,
  });
  const body = await readJson(response);

  if (!response.ok) {
    return failureFromResponse(response.status, body);
  }
  return isPositionContextResponse(body, fen)
    ? { status: "success", data: body }
    : { status: "unexpected_failure" };
};
