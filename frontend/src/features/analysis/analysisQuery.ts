import { useQuery } from "@tanstack/react-query";
import { useRef } from "react";

import { queryKeys } from "../../api/queryKeys";
import { positionKeyFromFen, type Fen } from "../chess/chessPrimitives";
import {
  type AnalysisClient,
  type AnalysisFailureCode,
  type AnalysisObservation,
  defaultAnalysisClient,
} from "./analysisApi";

export const DEFAULT_ANALYSIS_POLL_INTERVAL_MS = 1000;
export const MAX_ANALYSIS_POLL_ATTEMPTS = 60;
export const ANALYSIS_OBSERVATION_GC_TIME = 5 * 60 * 1000;

export class AnalysisQueryError extends Error {
  constructor(readonly status: AnalysisFailureCode) {
    super(status);
    this.name = "AnalysisQueryError";
  }
}

export async function queryAnalysisObservation(
  client: AnalysisClient,
  fen: Fen,
  signal: AbortSignal,
): Promise<AnalysisObservation> {
  const result = await client.observe(fen, signal);
  if (signal.aborted) {
    throw new DOMException("The request was aborted", "AbortError");
  }
  if (result.status !== "success") {
    throw new AnalysisQueryError(result.status);
  }
  return result.data;
}

type PollState = {
  positionKey: string | null;
  resetToken: number;
  initialized: boolean;
  attempts: number;
};

export function analysisObservationQueryKey(fen: Fen | null) {
  return queryKeys.analysisObservation({
    positionKey: fen === null ? "" : positionKeyFromFen(fen),
  });
}

export function useAnalysisQuery(
  fen: Fen | null,
  client: AnalysisClient = defaultAnalysisClient,
  pollIntervalMs = DEFAULT_ANALYSIS_POLL_INTERVAL_MS,
  resetToken = 0,
) {
  const positionKey = fen === null ? null : positionKeyFromFen(fen);
  const pollState = useRef<PollState>({
    positionKey,
    resetToken,
    initialized: false,
    attempts: 0,
  });

  if (
    pollState.current.positionKey !== positionKey ||
    pollState.current.resetToken !== resetToken
  ) {
    pollState.current = {
      positionKey,
      resetToken,
      initialized: false,
      attempts: 0,
    };
  }

  const query = useQuery({
    queryKey: analysisObservationQueryKey(fen),
    queryFn: ({ signal }) => {
      if (pollState.current.initialized) {
        pollState.current.attempts += 1;
      } else {
        pollState.current.initialized = true;
      }
      return queryAnalysisObservation(client, fen!, signal);
    },
    enabled: fen !== null,
    retry: false,
    staleTime: 0,
    gcTime: ANALYSIS_OBSERVATION_GC_TIME,
    refetchInterval: (currentQuery) => {
      const state = currentQuery.state.data;
      if (
        (state?.state !== "queued" && state?.state !== "running") ||
        pollState.current.attempts >= MAX_ANALYSIS_POLL_ATTEMPTS
      ) {
        return false;
      }
      return pollIntervalMs;
    },
  });

  const active = query.data?.state === "queued" || query.data?.state === "running";
  return {
    ...query,
    pollLimitReached: active && pollState.current.attempts >= MAX_ANALYSIS_POLL_ATTEMPTS,
  };
}
