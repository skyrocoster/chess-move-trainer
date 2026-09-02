import { Chess, validateFen } from "chess.js";

import type { ChessSide, Fen } from "../viewer/chessPrimitives";

const API_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5666";

type JsonRecord = Record<string, unknown>;

export type MoveResponseDistributionReply = {
  rank: number;
  child_uci: string;
  san: string;
  distinct_game_count: number;
  opening_name: string | null;
};

export type MoveResponseDistributionResponse = {
  fen: Fen;
  color: ChessSide;
  matching_game_count: number;
  replies: MoveResponseDistributionReply[];
};

export type MoveResponseDistributionFailureCode =
  | "invalid_fen"
  | "invalid_color"
  | "move_response_distribution_unavailable"
  | "unexpected_failure";

export type MoveResponseDistributionFailure = {
  status: MoveResponseDistributionFailureCode;
};

export type MoveResponseDistributionResult =
  | { status: "success"; data: MoveResponseDistributionResponse }
  | MoveResponseDistributionFailure;

export type MoveResponseDistributionClient = (
  fen: Fen,
  color: ChessSide,
  signal?: AbortSignal,
) => Promise<MoveResponseDistributionResult>;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null;
}

function hasExactKeys(value: JsonRecord, keys: readonly string[]): boolean {
  return Object.keys(value).sort().join(",") === [...keys].sort().join(",");
}

function isNonnegativeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
}

function isPositiveInteger(value: unknown): value is number {
  return isNonnegativeInteger(value) && value > 0;
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

function isChessSide(value: unknown): value is ChessSide {
  return value === "white" || value === "black";
}

function isCanonicalUci(value: unknown): value is string {
  return typeof value === "string" && /^[a-h][1-8][a-h][1-8][qrbn]?$/.test(value);
}

function isMoveResponseDistributionReply(
  value: unknown,
  board: Chess,
): value is MoveResponseDistributionReply {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, ["rank", "child_uci", "san", "distinct_game_count", "opening_name"]) ||
    !isPositiveInteger(value.rank) ||
    !isCanonicalUci(value.child_uci) ||
    typeof value.san !== "string" ||
    value.san.length === 0 ||
    !isNonnegativeInteger(value.distinct_game_count) ||
    (value.opening_name !== null &&
      (typeof value.opening_name !== "string" || value.opening_name.length === 0))
  ) {
    return false;
  }

  try {
    const move = new Chess(board.fen()).move({
      from: value.child_uci.slice(0, 2),
      to: value.child_uci.slice(2, 4),
      ...(value.child_uci.length === 5 ? { promotion: value.child_uci[4] } : {}),
    });
    const canonicalUci = `${move.from}${move.to}${move.promotion ?? ""}`;
    return canonicalUci === value.child_uci && move.san === value.san;
  } catch {
    return false;
  }
}

function isMoveResponseDistributionResponse(
  value: unknown,
  requestedFen: Fen,
  requestedColor: ChessSide,
): value is MoveResponseDistributionResponse {
  if (
    !isRecord(value) ||
    !hasExactKeys(value, ["fen", "color", "matching_game_count", "replies"]) ||
    !samePositionFen(value.fen, requestedFen) ||
    value.color !== requestedColor ||
    !isNonnegativeInteger(value.matching_game_count) ||
    !Array.isArray(value.replies)
  ) {
    return false;
  }

  let board: Chess;
  try {
    board = new Chess(requestedFen);
  } catch {
    return false;
  }

  const replies: MoveResponseDistributionReply[] = [];
  for (const item of value.replies) {
    if (!isMoveResponseDistributionReply(item, board)) {
      return false;
    }
    replies.push(item);
  }

  return (
    replies.every((reply, index) => reply.rank === index + 1) &&
    new Set(replies.map((reply) => reply.child_uci)).size === replies.length
  );
}

function isFailureCode(value: unknown): value is MoveResponseDistributionFailureCode {
  return (
    value === "invalid_fen" ||
    value === "invalid_color" ||
    value === "move_response_distribution_unavailable" ||
    value === "unexpected_failure"
  );
}

function isErrorBody(
  value: unknown,
): value is { code: MoveResponseDistributionFailureCode; message: string } {
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

function failureFromResponse(status: number, body: unknown): MoveResponseDistributionFailure {
  if (
    status === 422 &&
    isErrorBody(body) &&
    (body.code === "invalid_fen" || body.code === "invalid_color")
  ) {
    return { status: body.code };
  }
  if (
    status === 503 &&
    isErrorBody(body) &&
    body.code === "move_response_distribution_unavailable"
  ) {
    return { status: body.code };
  }
  if (status === 500 && isErrorBody(body) && body.code === "unexpected_failure") {
    return { status: body.code };
  }
  return { status: "unexpected_failure" };
}

export function validateMoveResponseDistributionFen(
  value: unknown,
): MoveResponseDistributionFailureCode | null {
  return isCanonicalFen(value) ? null : "invalid_fen";
}

export function validateMoveResponseDistributionColor(
  value: unknown,
): MoveResponseDistributionFailureCode | null {
  return isChessSide(value) ? null : "invalid_color";
}

export const fetchMoveResponseDistribution: MoveResponseDistributionClient = async (
  fen,
  color,
  signal,
) => {
  const fenFailure = validateMoveResponseDistributionFen(fen);
  if (fenFailure !== null) {
    return { status: fenFailure };
  }
  const colorFailure = validateMoveResponseDistributionColor(color);
  if (colorFailure !== null) {
    return { status: colorFailure };
  }

  let response: Response;
  try {
    response = await fetch(
      `${API_URL}/api/move-response-distribution?fen=${encodeURIComponent(fen)}&color=${encodeURIComponent(color)}`,
      { signal },
    );
  } catch (error) {
    if (signal?.aborted) {
      throw error;
    }
    return { status: "unexpected_failure" };
  }

  const body = await readJson(response);
  if (!response.ok) {
    return failureFromResponse(response.status, body);
  }
  return isMoveResponseDistributionResponse(body, fen, color)
    ? { status: "success", data: body }
    : { status: "unexpected_failure" };
};
