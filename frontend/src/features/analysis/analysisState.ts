import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";

import {
  type AnalysisClient,
  type AnalysisFailure,
  type AnalysisObservation,
  defaultAnalysisClient,
  positionKeyFromFen,
} from "./analysisApi";
import type { Fen } from "../chess/chessPrimitives";
import {
  AnalysisQueryError,
  DEFAULT_ANALYSIS_POLL_INTERVAL_MS,
  MAX_ANALYSIS_POLL_ATTEMPTS,
  useAnalysisQuery,
} from "./analysisQuery";
import {
  invalidateAnalysisObservation,
  invalidatePositionInsight,
} from "../../api/queryInvalidation";

const POLL_TIMEOUT_MESSAGE = "Analysis is taking longer than expected. Try again later.";

export type AnalysisState = {
  observation: AnalysisObservation | null;
  loading: boolean;
  error: string | null;
  requestError: string | null;
  requestPending: boolean;
  requestAnalysis: () => Promise<void>;
  retryObservation: () => void;
};

function failureMessage(failure: AnalysisFailure): string {
  switch (failure.status) {
    case "invalid_fen":
      return "This position cannot be analyzed.";
    case "invalid_quality":
      return "This analysis request is not supported.";
    case "analysis_unavailable":
      return "The analysis service is unavailable.";
    default:
      return "The analysis could not be loaded.";
  }
}

function mergeObservation(
  current: AnalysisObservation | null,
  next: AnalysisObservation,
): AnalysisObservation {
  const active = next.state === "queued" || next.state === "running";
  if (
    active &&
    next.result === null &&
    current !== null &&
    positionKeyFromFen(current.fen) === positionKeyFromFen(next.fen)
  ) {
    return { ...next, result: current.result };
  }
  return next;
}

function observationFingerprint(observation: AnalysisObservation): string {
  return JSON.stringify({ state: observation.state, result: observation.result });
}

function changedObservation(
  previous: AnalysisObservation | null,
  next: AnalysisObservation,
): boolean {
  return (
    previous !== null &&
    (previous.state !== next.state ||
      JSON.stringify(previous.result) !== JSON.stringify(next.result))
  );
}

function useDefaultAnalysisState(fen: Fen | null, pollIntervalMs: number): AnalysisState {
  const queryClient = useQueryClient();
  const positionKey = fen === null ? null : positionKeyFromFen(fen);
  const [pollResetToken, setPollResetToken] = useState(0);
  const [retryToken, setRetryToken] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const [retained, setRetained] = useState<{
    positionKey: string | null;
    observation: AnalysisObservation | null;
  }>({ positionKey: null, observation: null });
  const [requestError, setRequestError] = useState<string | null>(null);
  const [requestPending, setRequestPending] = useState(false);
  const requestController = useRef<AbortController | null>(null);
  const requestPendingRef = useRef(false);
  const currentFen = useRef<Fen | null>(fen);
  const lastObserved = useRef<AnalysisObservation | null>(null);
  const lastObservedPositionKey = useRef<string | null>(null);
  const lastInsightInvalidated = useRef<string | null>(null);
  const previousRetryToken = useRef(retryToken);
  const query = useAnalysisQuery(fen, undefined, pollIntervalMs, pollResetToken);
  const { refetch } = query;

  useEffect(() => {
    currentFen.current = fen;
  }, [fen]);

  useEffect(() => {
    if (previousRetryToken.current === retryToken) return;
    previousRetryToken.current = retryToken;
    setRefreshing(true);
    void refetch().finally(() => setRefreshing(false));
  }, [refetch, retryToken]);

  useEffect(() => {
    setRetained((current) => {
      if (positionKey === null) {
        return current.positionKey === null && current.observation === null
          ? current
          : { positionKey: null, observation: null };
      }
      const existing = current.positionKey === positionKey ? current.observation : null;
      const observation =
        query.data === undefined ? existing : mergeObservation(existing, query.data);
      if (current.positionKey === positionKey && current.observation === observation) {
        return current;
      }
      return { positionKey, observation };
    });
  }, [positionKey, query.data]);

  useEffect(() => {
    if (query.data === undefined || positionKey === null) return;
    if (lastObservedPositionKey.current !== positionKey) {
      lastObservedPositionKey.current = positionKey;
      lastObserved.current = query.data;
      lastInsightInvalidated.current = null;
      return;
    }
    const previous = lastObserved.current;
    lastObserved.current = query.data;
    if (!changedObservation(previous, query.data)) return;

    const fingerprint = observationFingerprint(query.data);
    if (lastInsightInvalidated.current === fingerprint) {
      lastInsightInvalidated.current = null;
      return;
    }
    lastInsightInvalidated.current = fingerprint;
    void invalidatePositionInsight(queryClient, positionKey);
  }, [positionKey, query.data, queryClient]);

  useEffect(() => {
    requestController.current?.abort();
    requestController.current = null;
    requestPendingRef.current = false;
    setRequestPending(false);
    setRequestError(null);
    return () => requestController.current?.abort();
  }, [positionKey]);

  const baseObservation = retained.positionKey === positionKey ? retained.observation : null;
  const observation =
    query.data === undefined ? baseObservation : mergeObservation(baseObservation, query.data);
  const queryError = query.isError
    ? query.error instanceof AnalysisQueryError
      ? failureMessage({ status: query.error.status })
      : "The analysis could not be loaded."
    : null;
  const pollLimitError =
    query.pollLimitReached && observation !== null ? POLL_TIMEOUT_MESSAGE : null;
  const loading = fen !== null && (query.isPending || refreshing);

  async function requestAnalysis(): Promise<void> {
    if (fen === null || requestPendingRef.current) return;

    const positionFen = fen;
    requestController.current?.abort();
    const controller = new AbortController();
    requestController.current = controller;
    requestPendingRef.current = true;
    setRequestPending(true);
    setRequestError(null);

    let result;
    try {
      result = await defaultAnalysisClient.request(positionFen, controller.signal);
    } catch {
      if (!controller.signal.aborted) {
        requestPendingRef.current = false;
        setRequestPending(false);
        setRequestError("The analysis request could not be submitted.");
      }
      return;
    }
    if (controller.signal.aborted) return;

    const latestFen = currentFen.current;
    if (latestFen === null || positionKeyFromFen(latestFen) !== positionKeyFromFen(positionFen)) {
      return;
    }

    if (result.status !== "success") {
      requestPendingRef.current = false;
      setRequestPending(false);
      setRequestError(failureMessage(result));
      return;
    }

    requestPendingRef.current = false;
    setRequestPending(false);
    setRetained((current) => ({
      positionKey: positionKeyFromFen(positionFen),
      observation: mergeObservation(
        current.positionKey === positionKeyFromFen(positionFen) ? current.observation : null,
        result.data,
      ),
    }));
    lastInsightInvalidated.current = observationFingerprint(result.data);
    setPollResetToken((token) => token + 1);
    void Promise.all([
      invalidateAnalysisObservation(queryClient, positionKeyFromFen(positionFen)),
      invalidatePositionInsight(queryClient, positionKeyFromFen(positionFen)),
    ]);
  }

  return {
    observation,
    loading,
    error: queryError ?? pollLimitError,
    requestError,
    requestPending,
    requestAnalysis,
    retryObservation: () => setRetryToken((token) => token + 1),
  };
}

function useInjectedAnalysisState(
  fen: Fen | null,
  client: AnalysisClient = defaultAnalysisClient,
  pollIntervalMs = DEFAULT_ANALYSIS_POLL_INTERVAL_MS,
): AnalysisState {
  const [observation, setObservation] = useState<AnalysisObservation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [requestError, setRequestError] = useState<string | null>(null);
  const [requestPending, setRequestPending] = useState(false);
  const [refreshToken, setRefreshToken] = useState(0);
  const previousFen = useRef<Fen | null>(null);
  const currentFen = useRef<Fen | null>(fen);
  const requestController = useRef<AbortController | null>(null);
  const requestPendingRef = useRef(false);
  const positionKey = fen === null ? null : positionKeyFromFen(fen);

  useEffect(() => {
    currentFen.current = fen;
  }, [fen]);

  useEffect(() => {
    return () => {
      requestController.current?.abort();
      requestController.current = null;
    };
  }, [client, positionKey]);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    let timer: ReturnType<typeof setTimeout> | null = null;
    let pollAttempts = 0;
    const samePosition =
      fen !== null &&
      previousFen.current !== null &&
      positionKeyFromFen(previousFen.current) === positionKeyFromFen(fen);
    previousFen.current = fen;

    if (!samePosition) {
      setObservation(null);
    }
    setError(null);
    setRequestError(null);
    if (!samePosition) {
      requestPendingRef.current = false;
      setRequestPending(false);
    }

    if (fen === null) {
      setLoading(false);
      return () => {
        active = false;
        controller.abort();
      };
    }

    const positionFen = fen;
    setLoading(true);

    function stopTimer() {
      if (timer !== null) {
        clearTimeout(timer);
        timer = null;
      }
    }

    function fail(message: string) {
      if (!active) {
        return;
      }
      stopTimer();
      setLoading(false);
      setError(message);
    }

    function schedulePoll() {
      stopTimer();
      timer = setTimeout(() => void poll(), pollIntervalMs);
    }

    async function observe() {
      let result;
      try {
        result = await client.observe(positionFen, controller.signal);
      } catch {
        if (!controller.signal.aborted) {
          fail("The analysis could not be loaded.");
        }
        return;
      }
      if (!active || controller.signal.aborted) {
        return;
      }
      if (result.status !== "success") {
        fail(failureMessage(result));
        return;
      }

      setObservation((current) => mergeObservation(current, result.data));
      setLoading(false);
      setError(null);
      if (result.data.state === "queued" || result.data.state === "running") {
        schedulePoll();
      } else {
        stopTimer();
      }
    }

    async function poll() {
      if (!active || controller.signal.aborted) {
        return;
      }
      pollAttempts += 1;
      if (pollAttempts > MAX_ANALYSIS_POLL_ATTEMPTS) {
        fail("Analysis is taking longer than expected. Try again later.");
        return;
      }
      await observe();
    }

    void observe();

    return () => {
      active = false;
      controller.abort();
      stopTimer();
    };
  }, [client, fen, pollIntervalMs, refreshToken]);

  async function requestAnalysis() {
    if (fen === null || requestPendingRef.current) {
      return;
    }

    const positionFen = fen;
    requestController.current?.abort();
    const controller = new AbortController();
    requestController.current = controller;
    requestPendingRef.current = true;
    setRequestPending(true);
    setRequestError(null);

    let result;
    try {
      result = await client.request(positionFen, controller.signal);
    } catch {
      if (!controller.signal.aborted) {
        requestPendingRef.current = false;
        setRequestPending(false);
        setRequestError("The analysis request could not be submitted.");
      }
      return;
    }
    if (controller.signal.aborted) {
      return;
    }

    const latestFen = currentFen.current;
    if (latestFen === null || positionKeyFromFen(latestFen) !== positionKeyFromFen(positionFen)) {
      return;
    }

    if (result.status !== "success") {
      requestPendingRef.current = false;
      setRequestPending(false);
      setRequestError(failureMessage(result));
      return;
    }

    requestPendingRef.current = false;
    setRequestPending(false);
    setObservation((current) => mergeObservation(current, result.data));
    setRefreshToken((token) => token + 1);
  }

  return {
    observation,
    loading,
    error,
    requestError,
    requestPending,
    requestAnalysis,
    retryObservation: () => setRefreshToken((token) => token + 1),
  };
}

export function useAnalysisState(
  fen: Fen | null,
  client: AnalysisClient = defaultAnalysisClient,
  pollIntervalMs = DEFAULT_ANALYSIS_POLL_INTERVAL_MS,
): AnalysisState {
  // The client is a construction-time dependency: switching it remounts this
  // feature. Keeping the implementations separate avoids unused queries for test clients.
  if (client === defaultAnalysisClient) {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    return useDefaultAnalysisState(fen, pollIntervalMs);
  }
  // eslint-disable-next-line react-hooks/rules-of-hooks
  return useInjectedAnalysisState(fen, client, pollIntervalMs);
}
