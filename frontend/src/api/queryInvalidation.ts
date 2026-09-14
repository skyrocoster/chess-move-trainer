import { QueryClient } from "@tanstack/react-query";

import {
  queryKeyPrefixes,
  queryKeys,
  type AnalysisObservationKeyInput,
  type PositionInsightKeyInput,
  type PreferredMoveKeyInput,
} from "./queryKeys";

/** Invalidate one preferred-move position/window read. */
export function invalidatePreferredMove(
  queryClient: QueryClient,
  input: PreferredMoveKeyInput,
): Promise<void> {
  return queryClient.invalidateQueries({
    queryKey: queryKeys.preferredMove(input),
    exact: true,
  });
}

/** Invalidate the complete assembled training-requirements family. */
export function invalidateTrainingRequirements(queryClient: QueryClient): Promise<void> {
  return queryClient.invalidateQueries({
    queryKey: queryKeyPrefixes.trainingRequirements(),
  });
}

/** Invalidate every shared position-insight variant for one canonical position. */
export function invalidatePositionInsight(
  queryClient: QueryClient,
  positionKey: PositionInsightKeyInput["positionKey"],
): Promise<void> {
  return queryClient.invalidateQueries({
    queryKey: queryKeyPrefixes.positionInsight(positionKey),
  });
}

/** Invalidate one canonical analysis observation. */
export function invalidateAnalysisObservation(
  queryClient: QueryClient,
  positionKey: AnalysisObservationKeyInput["positionKey"],
): Promise<void> {
  return queryClient.invalidateQueries({
    queryKey: queryKeys.analysisObservation({ positionKey }),
    exact: true,
  });
}
