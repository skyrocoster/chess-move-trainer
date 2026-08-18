import { cleanup, render, screen } from "@testing-library/react";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";

import ViewerWorkspace from "./ViewerWorkspace";

expect.extend(matchers);

const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";

const here = dirname(fileURLToPath(import.meta.url));
const rawStyles = readFileSync(join(here, "ViewerWorkspace.module.css"), "utf8");

afterEach(() => {
  cleanup();
});

describe("ViewerWorkspace", () => {
  it("renders exactly one H1 'Position viewer' with no subtitle", () => {
    render(<ViewerWorkspace />);
    const headings = screen.getAllByRole("heading", { level: 1 });

    expect(headings).toHaveLength(1);
    expect(headings[0]).toHaveTextContent("Position viewer");
    expect(screen.queryByText("One static position - read-only")).not.toBeInTheDocument();
  });

  it("renders the starting-position board with the settled label and adapter defaults", () => {
    const { container } = render(<ViewerWorkspace />);
    const graphic = screen.getByRole("img", { name: BOARD_LABEL });
    const description = document.getElementById(graphic.getAttribute("aria-describedby") ?? "");

    expect(description).toHaveTextContent("Orientation: White at the bottom.");
    expect(graphic.querySelectorAll("[data-square] span").length).toBeGreaterThan(0);
    expect(container.querySelector('[role="button"]')).not.toBeInTheDocument();
  });

  it("keeps the Context panel a plain container with no complementary landmark", () => {
    const { container } = render(<ViewerWorkspace />);
    const contextHeading = screen.getByRole("heading", { level: 2, name: "Context" });
    const panel = contextHeading.closest('[class*="contextPanel"]');
    const workspace = container.querySelector('[class*="workspace"]');

    expect(contextHeading).toBeVisible();
    expect(screen.queryByRole("complementary")).toBeNull();
    expect(container.querySelector("aside")).toBeNull();

    expect(panel).not.toBeNull();
    expect(workspace).not.toBeNull();
    const elements = [panel as HTMLElement, workspace as HTMLElement];
    for (const element of elements) {
      expect(element).not.toHaveAttribute("role");
      expect(element).not.toHaveAttribute("aria-label");
      expect(element).not.toHaveAttribute("aria-labelledby");
    }
  });

  it("ships the container-query omission contract with no viewport breakpoint", () => {
    expect(rawStyles).toMatch(/@container\s*\(\s*max-width:\s*40rem\s*\)/);
    expect(rawStyles.slice(rawStyles.indexOf("@container"))).toMatch(
      /\.contextPanel\s*\{[^}]*display:\s*none/,
    );
    expect(rawStyles).toMatch(/@media\s*\(\s*forced-colors:\s*active\s*\)/);
    expect(rawStyles).not.toMatch(/@media\s*\(\s*(?:max-width|min-width)\s*:/);
  });

  it("has no focused axe violations at the workspace boundary", async () => {
    const { container } = render(<ViewerWorkspace />);
    const results = await axe.run({ include: [container] });

    expect(results).toHaveNoViolations();
  });
});
