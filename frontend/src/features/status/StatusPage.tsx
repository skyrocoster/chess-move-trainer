import { useQuery } from "@tanstack/react-query";

import { getHealthOptions } from "../../api/client";
import { StatusView, type StatusDetail } from "./StatusView";

export function StatusPage() {
  const healthQuery = useQuery({ ...getHealthOptions(), gcTime: 0 });

  if (healthQuery.isPending) {
    return <StatusView state={{ kind: "loading" }} />;
  }
  if (healthQuery.isError || healthQuery.data?.status !== "ok") {
    return <StatusView state={{ kind: "error" }} />;
  }

  const data = healthQuery.data;
  const detail: StatusDetail = {
    workers: data.workers,
    analysis: data.analysis
      ? {
          positions: data.analysis.positions,
          analyzed: data.analysis.analyzed,
          queued: data.analysis.queued,
          running: data.analysis.running,
          remaining: data.analysis.remaining,
        }
      : null,
    lastGameAt: data.last_game_at,
  };
  return <StatusView state={{ kind: "success", detail }} />;
}
