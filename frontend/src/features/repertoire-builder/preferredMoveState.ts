import { useEffect, useState } from "react";

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
};

export function usePreferredMoveState(
  fen: Fen | null,
  client: PreferredMoveReader = fetchPreferredMove,
): PreferredMoveReadState {
  const [preferredMove, setPreferredMove] = useState<PreferredMoveResponse | null>(null);
  const [loading, setLoading] = useState(fen !== null);
  const [error, setError] = useState<PreferredMoveFailureCode | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    setPreferredMove(null);
    setError(null);

    if (fen === null) {
      setLoading(false);
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

      setPreferredMove(result.data);
      setLoading(false);
      setError(null);
    }

    void loadPreferredMove();

    return () => {
      active = false;
      controller.abort();
    };
  }, [client, fen]);

  return { preferredMove, loading, error };
}
