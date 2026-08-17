import { useEffect, useState } from "react";

import { fetchHealth } from "./statusApi";
import { StatusView } from "./StatusView";

type ViewState = { kind: "loading" } | { kind: "success" } | { kind: "error"; message: string };

export function StatusPage() {
  const [state, setState] = useState<ViewState>({ kind: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    fetchHealth(controller.signal)
      .then(() => setState({ kind: "success" }))
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          const message = error instanceof Error ? error.message : "Unable to reach the backend";
          setState({ kind: "error", message });
        }
      });
    return () => controller.abort();
  }, []);

  return <StatusView state={state} />;
}
