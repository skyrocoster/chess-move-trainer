import { useEffect, useRef, useState } from "react";

import {
  type AnalysisClient,
  type AnalysisFailure,
  type AnalysisObservation,
  defaultAnalysisClient,
  positionKeyFromFen,
} from "./analysisApi";
import type { Fen } from "../chess/chessPrimitives";

const DEFAULT_POLL_INTERVAL_MS = 1000;
const MAX_POLL_ATTEMPTS = 60;

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

export function useAnalysisState(
  fen: Fen | null,
  client: AnalysisClient = defaultAnalysisClient,
  pollIntervalMs = DEFAULT_POLL_INTERVAL_MS,
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
      if (pollAttempts > MAX_POLL_ATTEMPTS) {
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
