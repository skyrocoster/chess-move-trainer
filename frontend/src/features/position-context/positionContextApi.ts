import { validateFen } from "chess.js";

import { getPositionInsight } from "../../api/client";
import type { ChessSide, Fen } from "../chess/chessPrimitives";

type JsonRecord = Record<string, unknown>;

export type PositionContextResponse = {
  fen: Fen;
  trainerColor: ChessSide;
  observedInGames: boolean;
  distinctGameCount: number;
  totalGameCount: number;
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
  trainerColor: ChessSide,
  signal?: AbortSignal,
) => Promise<PositionContextResult>;

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

function requestAsOf(): string {
  return new Date().toISOString().slice(0, 10);
}

export function validatePositionContextFen(value: unknown): PositionContextFailureCode | null {
  return isCanonicalFen(value) ? null : "invalid_fen";
}

function narrowInsightResponse(
  response: unknown,
  requestedFen: Fen,
  trainerColor: ChessSide,
): PositionContextResult {
  if (!isRecord(response) || !samePositionFen(response.fen, requestedFen)) {
    return { status: "unexpected_failure" };
  }
  if (response.trainer_color !== trainerColor) {
    return { status: "unexpected_failure" };
  }
  const experience = response.experience;
  if (
    !isRecord(experience) ||
    !isNonnegativeInteger(experience.distinct_game_count) ||
    !isNonnegativeInteger(experience.total_game_count) ||
    typeof response.observed_in_games !== "boolean"
  ) {
    return { status: "unexpected_failure" };
  }
  return {
    status: "success",
    data: {
      fen: response.fen,
      trainerColor,
      observedInGames: response.observed_in_games,
      distinctGameCount: experience.distinct_game_count,
      totalGameCount: experience.total_game_count,
    },
  };
}

function failureFromInsight(error: unknown, status: number | null): PositionContextFailure {
  const code = isRecord(error) && typeof error.code === "string" ? error.code : null;
  if (status === 422 && code === "invalid_fen") {
    return { status: "invalid_fen" };
  }
  if (status === 503 && code === "position_insight_unavailable") {
    return { status: "position_context_unavailable" };
  }
  if (status === 500 && code === "unexpected_failure") {
    return { status: "unexpected_failure" };
  }
  return { status: "unexpected_failure" };
}

export const fetchPositionContext: PositionContextClient = async (fen, trainerColor, signal) => {
  const validationFailure = validatePositionContextFen(fen);
  if (validationFailure !== null) {
    return { status: validationFailure };
  }

  const result = await getPositionInsight({
    query: {
      as_of: requestAsOf(),
      fen,
      trainer_color: trainerColor,
    },
    signal,
  });

  if (result.data === undefined || result.error !== undefined) {
    return failureFromInsight(result.error, result.response?.status ?? null);
  }
  return narrowInsightResponse(result.data, fen, trainerColor);
};
