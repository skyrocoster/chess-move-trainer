import { cleanup, render, screen } from "@testing-library/react";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import { afterEach, describe, expect, it, vi } from "vitest";

import { FoundationCheck } from "./FoundationCheck";

expect.extend(matchers);

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("FoundationCheck", () => {
  it("renders the development-only proof states with no axe violations", async () => {
    const { container } = render(<FoundationCheck />);

    expect(screen.getByText("Development-only Foundation Check")).toBeVisible();
    expect(screen.getByRole("button", { name: "Foundation icon proof" })).toBeVisible();

    // react-chessboard 5.12.0 renders one unnamed `role="button"` draggable
    // wrapper per piece (`[aria-roledescription="draggable"]`), even in
    // read-only static mode. Those are third-party internals whose accessible
    // board contract is owned by the future MP-04 board adapter, not by MP-01's
    // temporary Foundation Check, so they are excluded here. The run stays
    // scoped to the rendered container, so all application-owned proof content
    // remains fully axe-checked.
    const results = await axe.run({
      include: [container],
      exclude: ['[aria-roledescription="draggable"]'],
    });
    expect(results).toHaveNoViolations();
  });
});
