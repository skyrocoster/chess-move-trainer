import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "../../api/queryKeys";
import type { GameDetailResponse } from "../../api/client";
import type { GameDetailClient } from "./RepertoireBuilderWorkspaceTypes";

export class GameDetailQueryError extends Error {
  constructor(readonly result: Awaited<ReturnType<GameDetailClient>>) {
    super("The game detail request failed");
    this.name = "GameDetailQueryError";
  }
}

export async function queryGameDetail(
  client: GameDetailClient,
  gameUuid: string,
  signal: AbortSignal,
): Promise<GameDetailResponse> {
  const result = await client({
    path: { game_uuid: gameUuid },
    signal,
  });
  if (result.data === undefined) {
    throw new GameDetailQueryError(result);
  }
  return result.data as GameDetailResponse;
}

export function useGameDetailQuery(
  gameUuid: string | null,
  client: GameDetailClient,
) {
  const normalizedUuid = gameUuid?.trim() || null;
  return useQuery({
    queryKey: queryKeys.gameDetail({ gameUuid: normalizedUuid ?? "" }),
    queryFn: ({ signal }) => queryGameDetail(client, normalizedUuid!, signal),
    enabled: normalizedUuid !== null,
    retry: false,
    staleTime: 5 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  });
}
