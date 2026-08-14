import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { StatusPage } from "./StatusPage";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("StatusPage", () => {
  it("shows loading then healthy", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ status: "ok" }), { status: 200 }),
    );
    render(<StatusPage />);

    expect(screen.getByRole("status")).toHaveTextContent("Checking backend health");
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("healthy"));
  });

  it("shows a network error accessibly", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("Connection refused"));
    render(<StatusPage />);

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("unavailable"));
  });

  it("shows a non-ok response error", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("", { status: 503 }));
    render(<StatusPage />);

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("HTTP 503"));
  });
});
