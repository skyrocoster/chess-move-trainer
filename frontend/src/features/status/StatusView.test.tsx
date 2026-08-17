import * as axe from "axe-core";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, describe, it } from "vitest";
import axeMatchers from "@chialab/vitest-axe";

import { StatusView } from "./StatusView";

expect.extend(axeMatchers);
afterEach(cleanup);

describe("StatusView", () => {
  it.each([
    [{ kind: "loading" as const }, "Checking backend health…", "status"],
    [{ kind: "success" as const }, "Backend connected and healthy.", "status"],
    [
      { kind: "error" as const, message: "Health request failed with HTTP 503" },
      "Backend unavailable: Health request failed with HTTP 503",
      "alert",
    ],
  ])("renders the %s state with exact copy and role", (state, message, role) => {
    render(<StatusView state={state} />);

    expect(screen.getByRole("heading", { name: "System status" })).toBeInTheDocument();
    expect(screen.getByRole(role)).toHaveAttribute("role", role);
    expect(screen.getByText(message)).toBeInTheDocument();
  });

  it("passes a focused accessibility check", async () => {
    const { container } = render(<StatusView state={{ kind: "error", message: "Offline" }} />);

    expect(await axe.run(container)).toHaveNoViolations();
  });
});
