import { useEffect, useState } from "react";

import { fetchHealth } from "./statusApi";

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

  const content =
    state.kind === "loading" ? (
      <p role="status">Checking backend health…</p>
    ) : state.kind === "success" ? (
      <p role="status">Backend connected and healthy.</p>
    ) : (
      <p role="alert">Backend unavailable: {state.message}</p>
    );

  return (
    <main>
      <section className="status-card" data-state={state.kind} aria-labelledby="page-title">
        <h1 id="page-title">Chess Move Trainer</h1>
        {content}
      </section>
    </main>
  );
}
