import { useEffect, useState } from "react";

import {
  type PositionContextClient,
  type PositionContextFailureCode,
  type PositionContextResponse,
  fetchPositionContext,
} from "./positionContextApi";
import type { ChessSide, Fen } from "../chess/chessPrimitives";

export type PositionContextState = {
  context: PositionContextResponse | null;
  loading: boolean;
  error: PositionContextFailureCode | null;
};

export function usePositionContextState(
  fen: Fen | null,
  trainerColor: ChessSide,
  client: PositionContextClient = fetchPositionContext,
  refreshKey = 0,
): PositionContextState {
  const [context, setContext] = useState<PositionContextResponse | null>(null);
  const [loading, setLoading] = useState(fen !== null);
  const [error, setError] = useState<PositionContextFailureCode | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    setContext(null);
    setError(null);

    if (fen === null) {
      setLoading(false);
      return () => {
        active = false;
        controller.abort();
      };
    }

    const requestedFen = fen;
    const requestedTrainerColor = trainerColor;
    setLoading(true);

    async function loadContext() {
      let result;
      try {
        result = await client(requestedFen, requestedTrainerColor, controller.signal);
      } catch {
        if (active && !controller.signal.aborted) {
          setLoading(false);
          setError("unexpected_failure");
        }
        return;
      }

      if (!active || controller.signal.aborted) {
        return;
      }
      if (result.status !== "success") {
        setLoading(false);
        setError(result.status);
        return;
      }

      setContext(result.data);
      setLoading(false);
      setError(null);
    }

    void loadContext();

    return () => {
      active = false;
      controller.abort();
    };
  }, [client, fen, trainerColor, refreshKey]);

  return { context, loading, error };
}
