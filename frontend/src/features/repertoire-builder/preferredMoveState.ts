import { useEffect, useRef, useState } from "react";

import {
  fetchPreferredMove,
  type PreferredMoveFailureCode,
  type PreferredMoveReader,
  type PreferredMoveResponse,
} from "./preferredMoveApi";
import type { Fen } from "../viewer/chessPrimitives";

export type PreferredMoveReadState = {
  preferredMove: PreferredMoveResponse | null;
  loading: boolean;
  error: PreferredMoveFailureCode | null;
  completedRefreshKey: number;
};

export function usePreferredMoveState(
  fen: Fen | null,
  client: PreferredMoveReader = fetchPreferredMove,
  refreshKey = 0,
): PreferredMoveReadState {
  const [preferredMove, setPreferredMove] = useState<PreferredMoveResponse | null>(null);
  const [loading, setLoading] = useState(fen !== null);
  const [error, setError] = useState<PreferredMoveFailureCode | null>(null);
  const [completedRefreshKey, setCompletedRefreshKey] = useState(refreshKey);
  const lastFen = useRef<Fen | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    const isRefreshForSameFen = fen !== null && lastFen.current === fen;
    lastFen.current = fen;
    if (!isRefreshForSameFen) {
      setPreferredMove(null);
    }
    setError(null);

    if (fen === null) {
      setLoading(false);
      setCompletedRefreshKey(refreshKey);
      return () => {
        active = false;
        controller.abort();
      };
    }

    const requestedFen = fen;
    setLoading(true);

    async function loadPreferredMove() {
      let result;
      try {
        result = await client(requestedFen, { signal: controller.signal });
      } catch {
        if (active && !controller.signal.aborted) {
          setLoading(false);
          setError("unexpected_failure");
          setCompletedRefreshKey(refreshKey);
        }
        return;
      }

      if (!active || controller.signal.aborted) {
        return;
      }
      if (result.status !== "success") {
        setLoading(false);
        setError(result.status);
        setCompletedRefreshKey(refreshKey);
        return;
      }

      setPreferredMove(result.data);
      setLoading(false);
      setError(null);
      setCompletedRefreshKey(refreshKey);
    }

    void loadPreferredMove();

    return () => {
      active = false;
      controller.abort();
    };
  }, [client, fen, refreshKey]);

  return { preferredMove, loading, error, completedRefreshKey };
}
