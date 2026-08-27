import { useEffect, useRef, useState } from "react";

import {
  type AnalysisClient,
  type AnalysisFailure,
  type EvaluationAction,
  type EvaluationObservation,
  defaultAnalysisClient,
  positionKeyFromFen,
} from "./analysisApi";
import type { Fen } from "./chessPrimitives";

const DEFAULT_POLL_INTERVAL_MS = 1000;
const MAX_POLL_ATTEMPTS = 60;

export type AnalysisState = {
  observation: EvaluationObservation | null;
  loading: boolean;
  error: string | null;
  actionError: string | null;
  actionPending: boolean;
  handleAction: (action: EvaluationAction) => Promise<void>;
  retryObservation: () => void;
};

function failureMessage(failure: AnalysisFailure): string {
  switch (failure.status) {
    case "evaluation_unavailable":
      return "Evaluation data is unavailable.";
    case "invalid_fen":
      return "This position cannot be evaluated.";
    case "request_too_large":
      return "This position request is too large.";
    case "evaluation_busy":
      return "The evaluation service is busy. Try again deliberately.";
    case "invalid_action":
    case "invalid_transition":
      return "That analysis action is no longer available.";
    default:
      return "The evaluation could not be loaded.";
  }
}

export function useAnalysisState(
  fen: Fen | null,
  client: AnalysisClient = defaultAnalysisClient,
  pollIntervalMs = DEFAULT_POLL_INTERVAL_MS,
): AnalysisState {
  const [observation, setObservation] = useState<EvaluationObservation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionPending, setActionPending] = useState(false);
  const [refreshToken, setRefreshToken] = useState(0);
  const previousFen = useRef<Fen | null>(null);
  const actionController = useRef<AbortController | null>(null);

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
    setActionError(null);
    setActionPending(false);

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

    async function observe() {
      let result;
      try {
        result = await client.observe(positionFen, controller.signal);
      } catch {
        if (!controller.signal.aborted) {
          fail("The evaluation could not be loaded.");
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

      setObservation(result.data);
      setLoading(false);
      setError(null);
      if (result.data.status?.state === "queued" || result.data.status?.state === "running") {
        schedulePoll();
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

      let result;
      try {
        result = await client.status(positionFen, controller.signal);
      } catch {
        if (!controller.signal.aborted) {
          fail("The evaluation status could not be loaded.");
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
      if (result.data.state === "queued" || result.data.state === "running") {
        schedulePoll();
        return;
      }
      await observe();
    }

    function schedulePoll() {
      stopTimer();
      timer = setTimeout(() => void poll(), pollIntervalMs);
    }

    void observe();

    return () => {
      active = false;
      controller.abort();
      stopTimer();
    };
  }, [client, fen, pollIntervalMs, refreshToken]);

  useEffect(() => {
    return () => actionController.current?.abort();
  }, [client, fen]);

  async function handleAction(action: EvaluationAction) {
    if (fen === null || actionPending) {
      return;
    }
    const positionFen = fen;
    actionController.current?.abort();
    const controller = new AbortController();
    actionController.current = controller;
    setActionPending(true);
    setActionError(null);

    let result;
    try {
      result = await client.enqueue(positionFen, action, controller.signal);
    } catch {
      if (!controller.signal.aborted) {
        setActionPending(false);
        setActionError("The analysis action could not be submitted.");
      }
      return;
    }
    if (controller.signal.aborted) {
      return;
    }
    if (result.status !== "success") {
      setActionPending(false);
      setActionError(failureMessage(result));
      return;
    }

    setObservation((current) => ({
      fen: positionFen,
      eligibility: current?.result ? "stale" : (current?.eligibility ?? "missing"),
      result: current?.result ?? null,
      status: result.data.status,
      terminal: current?.terminal ?? false,
    }));
    setActionPending(false);
    setRefreshToken((token) => token + 1);
  }

  return {
    observation,
    loading,
    error,
    actionError,
    actionPending,
    handleAction,
    retryObservation: () => setRefreshToken((token) => token + 1),
  };
}
