import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "../../api/queryKeys";
import type { PositionInsightResponse } from "../../api/client";
import { positionKeyFromFen, type ChessSide, type Fen } from "../chess/chessPrimitives";
import {
  narrowInsightResponse as narrowPositionContextInsight,
  requestPositionInsight,
  validatePositionContextFen,
} from "../position-context/positionContextApi";
import {
  narrowInsightResponse as narrowMoveResponseInsight,
  validateMoveResponseDistributionColor,
} from "../move-response-distribution/moveResponseDistributionApi";

export const POSITION_INSIGHT_STALE_TIME = 5 * 1000;
export const POSITION_INSIGHT_GC_TIME = 10 * 60 * 1000;

type PositionInsightQueryErrorKind = "transport" | "malformed_response";

export class PositionInsightQueryError extends Error {
  constructor(
    readonly insightError: unknown,
    readonly httpStatus: number | null,
    readonly kind: PositionInsightQueryErrorKind = "transport",
  ) {
    super(kind === "malformed_response" ? "The position insight response was invalid" : "The position insight request failed");
    this.name = "PositionInsightQueryError";
  }
}

function currentUtcDate(): string {
  return new Date().toISOString().slice(0, 10);
}

function queryInput(fen: Fen | null, trainerColor: ChessSide | null) {
  return {
    positionKey: fen === null ? "" : positionKeyFromFen(fen),
    trainerColor,
    asOf: currentUtcDate(),
  };
}

export function positionInsightQueryKey(
  fen: Fen | null,
  trainerColor: ChessSide | null,
  asOf = currentUtcDate(),
) {
  return queryKeys.positionInsight({
    positionKey: fen === null ? "" : positionKeyFromFen(fen),
    trainerColor,
    asOf,
  });
}

function isValidRawInsight(
  response: unknown,
  requestedFen: Fen,
  trainerColor: ChessSide,
): response is PositionInsightResponse {
  const contextResult = narrowPositionContextInsight(response, requestedFen, trainerColor);
  const distributionResult = narrowMoveResponseInsight(response, requestedFen, trainerColor);
  return contextResult.status === "success" && distributionResult.status === "success";
}

export async function queryPositionInsight(
  fen: Fen,
  trainerColor: ChessSide,
  asOf: string,
  signal: AbortSignal,
): Promise<PositionInsightResponse> {
  const fenFailure = validatePositionContextFen(fen);
  if (fenFailure !== null) {
    throw new PositionInsightQueryError({ code: fenFailure }, 422);
  }
  const colorFailure = validateMoveResponseDistributionColor(trainerColor);
  if (colorFailure !== null) {
    throw new PositionInsightQueryError({ code: "invalid_trainer_color" }, 422);
  }

  const result = await requestPositionInsight(fen, trainerColor, asOf, signal);
  if (result.data === undefined || result.error !== undefined) {
    throw new PositionInsightQueryError(result.error, result.response?.status ?? null);
  }
  if (!isValidRawInsight(result.data, fen, trainerColor)) {
    throw new PositionInsightQueryError(null, null, "malformed_response");
  }
  return result.data;
}

export function usePositionInsightQuery(
  fen: Fen | null,
  trainerColor: ChessSide | null,
) {
  const input = queryInput(fen, trainerColor);
  return useQuery({
    queryKey: positionInsightQueryKey(fen, trainerColor, input.asOf),
    queryFn: ({ signal }) => queryPositionInsight(fen!, trainerColor!, input.asOf, signal),
    enabled: fen !== null && trainerColor !== null,
    retry: false,
    staleTime: POSITION_INSIGHT_STALE_TIME,
    gcTime: POSITION_INSIGHT_GC_TIME,
  });
}
