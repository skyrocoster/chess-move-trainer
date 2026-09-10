import { Chess, validateFen } from "chess.js";

import { getPositionInsight } from "../../api/client";
import type { ChessSide, Fen } from "../chess/chessPrimitives";

type JsonRecord = Record<string, unknown>;

export type MoveResponseDistributionReply = {
  rank: number;
  child_uci: string;
  san: string;
  occurrence_count: number;
};

export type MoveResponseDistributionResponse = {
  fen: Fen;
  color: ChessSide;
  matching_game_count: number;
  outgoing_occurrence_count: number;
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

function isChessSide(value: unknown): value is ChessSide {
  return value === "white" || value === "black";
}

function isCanonicalUci(value: unknown): value is string {
  return typeof value === "string" && /^[a-h][1-8][a-h][1-8][qrbn]?$/.test(value);
}

function legalMoveFromUci(fen: Fen, uci: string) {
  if (!isCanonicalUci(uci)) return null;

  try {
    const move = new Chess(fen).move({
      from: uci.slice(0, 2),
      to: uci.slice(2, 4),
      ...(uci.length === 5 ? { promotion: uci[4] } : {}),
    });
    const canonicalUci = `${move.from}${move.to}${move.promotion ?? ""}`;
    return canonicalUci === uci ? move : null;
  } catch {
    return null;
  }
}

function narrowInsightResponse(
  value: unknown,
  requestedFen: Fen,
  requestedColor: ChessSide,
): MoveResponseDistributionResult {
  if (
    !isRecord(value) ||
    !samePositionFen(value.fen, requestedFen) ||
    value.trainer_color !== requestedColor ||
    !isRecord(value.experience) ||
    !isNonnegativeInteger(value.experience.distinct_game_count) ||
    !isRecord(value.observed_move_totals) ||
    !isNonnegativeInteger(value.observed_move_totals.occurrence_count) ||
    !Array.isArray(value.observed_moves)
  ) {
    return { status: "unexpected_failure" };
  }

  const replies: Array<Omit<MoveResponseDistributionReply, "rank">> = [];
  const seenUci = new Set<string>();
  let occurrenceTotal = 0;
  for (const item of value.observed_moves) {
    if (
      !isRecord(item) ||
      !isCanonicalUci(item.move_uci) ||
      !isNonnegativeInteger(item.occurrence_count) ||
      seenUci.has(item.move_uci)
    ) {
      return { status: "unexpected_failure" };
    }

    const move = legalMoveFromUci(requestedFen, item.move_uci);
    if (move === null) return { status: "unexpected_failure" };

    seenUci.add(item.move_uci);
    occurrenceTotal += item.occurrence_count;
    replies.push({
      child_uci: item.move_uci,
      san: move.san,
      occurrence_count: item.occurrence_count,
    });
  }

  if (occurrenceTotal !== value.observed_move_totals.occurrence_count) {
    return { status: "unexpected_failure" };
  }

  replies.sort(
    (left, right) =>
      right.occurrence_count - left.occurrence_count ||
      left.child_uci.localeCompare(right.child_uci),
  );

  return {
    status: "success",
    data: {
      fen: value.fen,
      color: requestedColor,
      matching_game_count: value.experience.distinct_game_count,
      outgoing_occurrence_count: value.observed_move_totals.occurrence_count,
      replies: replies.map((reply, index) => ({ ...reply, rank: index + 1 })),
    },
  };
}

function failureFromInsight(error: unknown, status: number | null): MoveResponseDistributionFailure {
  const code = isRecord(error) && typeof error.code === "string" ? error.code : null;
  if (status === 422 && code === "invalid_fen") return { status: "invalid_fen" };
  if (status === 422 && (code === "invalid_trainer_color" || code === "invalid_color")) {
    return { status: "invalid_color" };
  }
  if (status === 503 && code === "position_insight_unavailable") {
    return { status: "move_response_distribution_unavailable" };
  }
  if (status === 500 && code === "unexpected_failure") {
    return { status: "unexpected_failure" };
  }
  return { status: "unexpected_failure" };
}

function requestAsOf(): string {
  return new Date().toISOString().slice(0, 10);
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

  let result;
  try {
    result = await getPositionInsight({
      query: {
        as_of: requestAsOf(),
        fen,
        trainer_color: color,
      },
      signal,
    });
  } catch (error) {
    if (signal?.aborted) throw error;
    return { status: "unexpected_failure" };
  }

  if (result.data === undefined || result.error !== undefined) {
    if (signal?.aborted && result.error !== undefined) throw result.error;
    return failureFromInsight(result.error, result.response?.status ?? null);
  }
  return narrowInsightResponse(result.data, fen, color);
};
