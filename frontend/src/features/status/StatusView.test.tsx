import * as axe from "axe-core";
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, expect, describe, it } from "vitest";
import axeMatchers from "@chialab/vitest-axe";

import { StatusView, type StatusDetail } from "./StatusView";

expect.extend(axeMatchers);
afterEach(cleanup);

const detail: StatusDetail = {
  workers: [
    { service: "worker", index: 1, running: true },
    { service: "worker-six", index: 1, running: true },
    { service: "worker-six", index: 2, running: false },
  ],
  analysis: { positions: 1200, analyzed: 1000, queued: 20, running: 4, remaining: 176 },
  lastGameAt: "2026-09-20T12:00:00+00:00",
};

describe("StatusView", () => {
  it.each([
    [{ kind: "loading" as const }, "Checking backend health…", "status"],
    [{ kind: "success" as const }, "Backend connected and healthy.", "status"],
    [{ kind: "error" as const }, "Backend unavailable.", "alert"],
  ])("renders the %s state with exact copy and role", (state, message, role) => {
    render(<StatusView state={state} />);

    expect(screen.getByRole("heading", { name: "System status" })).toBeInTheDocument();
    expect(screen.getByRole(role)).toHaveAttribute("role", role);
    expect(screen.getByText(message)).toBeInTheDocument();
  });

  it("renders one status line per worker plus the analysis table and last game date", () => {
    render(<StatusView state={{ kind: "success", detail }} />);

    expect(screen.getByText("Analysis worker running.")).toBeInTheDocument();
    expect(screen.getByText("Accelerated worker 1 running.")).toBeInTheDocument();
    expect(screen.getByText("Accelerated worker 2 stopped.")).toBeInTheDocument();

    expect(screen.getByRole("heading", { name: "Analysis" })).toBeInTheDocument();
    const table = screen.getByRole("table", { name: "Analysis progress by position" });
    expect(within(table).getByRole("rowheader", { name: "Remaining" })).toBeInTheDocument();
    expect(within(table).getByText("176")).toBeInTheDocument();
    expect(within(table).getByText("1,200")).toBeInTheDocument();
    expect(screen.getByText("Last game recorded: 2026-09-20")).toBeInTheDocument();
  });

  it("reports unavailable worker status", () => {
    render(
      <StatusView
        state={{
          kind: "success",
          detail: { workers: null, analysis: null, lastGameAt: null },
        }}
      />,
    );

    expect(screen.getByText("Worker status unavailable.")).toBeInTheDocument();
    expect(screen.getByText("Analysis details unavailable.")).toBeInTheDocument();
    expect(screen.getByText("Last game recorded: unknown")).toBeInTheDocument();
  });

  it("reports stopped analysis workers when no worker containers exist", () => {
    render(
      <StatusView
        state={{
          kind: "success",
          detail: { workers: [], analysis: null, lastGameAt: null },
        }}
      />,
    );

    expect(screen.getByText("Analysis workers stopped.")).toBeInTheDocument();
  });

  it("renders the error state without technical detail", () => {
    render(<StatusView state={{ kind: "error" }} />);

    expect(screen.queryByText(/HTTP|malformed|refused/i)).not.toBeInTheDocument();
  });

  it("passes a focused accessibility check", async () => {
    const { container } = render(<StatusView state={{ kind: "error" }} />);

    expect(await axe.run(container)).toHaveNoViolations();
  });

  it("passes a focused accessibility check with analysis detail", async () => {
    const { container } = render(<StatusView state={{ kind: "success", detail }} />);

    expect(await axe.run(container)).toHaveNoViolations();
  });
});
