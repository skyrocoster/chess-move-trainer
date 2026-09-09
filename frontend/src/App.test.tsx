import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { MemoryRouter } from "react-router-dom";

import App from "./App";
import { QueryClientTestProvider } from "./test-utils/QueryClientTestProvider";

afterEach(cleanup);

function renderApp(initialEntries: string[]) {
  return render(
    <QueryClientTestProvider>
      <MemoryRouter initialEntries={initialEntries}>
        <App />
      </MemoryRouter>
    </QueryClientTestProvider>,
  );
}

describe("App routes", () => {
  it("preserves the status page at the root route", () => {
    renderApp(["/"]);

    expect(screen.getByRole("heading", { name: "System status" })).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("Checking backend health");
  });

  it("renders the ordinary in-shell not-found state for /viewer with no compatibility surface", () => {
    renderApp(["/viewer"]);

    expect(screen.getByRole("heading", { name: "Page not found", level: 1 })).toBeInTheDocument();
    expect(screen.getByText("The page you requested could not be found.")).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "System status" })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Position viewer" })).not.toBeInTheDocument();
    expect(screen.queryByText("Loading position viewer...")).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Viewer" })).not.toBeInTheDocument();
  });

  it("renders the Repertoire Builder scaffold at /repertoire", async () => {
    renderApp(["/repertoire"]);

    expect(
      await screen.findByRole(
        "heading",
        { name: "Repertoire Builder", level: 1 },
        { timeout: 15000 },
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("group", {
        name: "Chess board: standard starting position, White at the bottom",
      }),
    ).toBeInTheDocument();
  }, 20_000);

  it("renders the in-shell not-found state for an unmatched route", () => {
    renderApp(["/does-not-exist"]);

    expect(screen.getByRole("heading", { name: "Page not found", level: 1 })).toBeInTheDocument();
    expect(screen.getByText("The page you requested could not be found.")).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "System status" })).not.toBeInTheDocument();
  });
});
