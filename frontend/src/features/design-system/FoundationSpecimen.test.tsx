import { cleanup, render, screen } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";

import { FoundationSpecimen } from "./FoundationSpecimen";

afterEach(() => {
  cleanup();
});

const here = dirname(fileURLToPath(import.meta.url));
const tokenCss = readFileSync(join(here, "../../styles/cmt-tokens.css"), "utf8");
const moduleCss = readFileSync(join(here, "FoundationSpecimen.module.css"), "utf8");

const SPACING_STEPS = ["4", "8", "12", "16", "24", "32", "48"] as const;
const ELEVATION_VALUES: Record<string, string> = {
  e0: "none",
  e1: "0 1px 2px rgba(0,0,0,0.3), 0 1px 3px 1px rgba(0,0,0,0.15)",
  e2: "0 1px 2px rgba(0,0,0,0.3), 0 2px 6px 2px rgba(0,0,0,0.15)",
  e3: "0 1px 3px rgba(0,0,0,0.3), 0 4px 8px 3px rgba(0,0,0,0.15)",
};

/** Remove all whitespace so formatting never changes the asserted value. */
function normalize(css: string): string {
  return css.replace(/\s+/g, "");
}

function ruleBlock(css: string, selector: string): string {
  const match = css.match(new RegExp(`${selector}\\s*\\{[^}]*\\}`));
  return match ? match[0] : "";
}

describe("FoundationSpecimen", () => {
  it("renders the foundation specimens and a real focusable specimen", () => {
    render(<FoundationSpecimen />);

    expect(screen.getByRole("heading", { name: "Foundations" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Spacing scale" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Radius" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Elevation (reserved)" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Focus ring" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Focus specimen" })).toBeVisible();
  });

  it("defines exactly the spacing scale 4/8/12/16/24/32/48 with no intermediate tokens", () => {
    render(<FoundationSpecimen />);

    for (const step of SPACING_STEPS) {
      expect(tokenCss).toContain(`--cmt-spacing-${step}: ${step}px;`);
      expect(screen.getByText(`--cmt-spacing-${step}`)).toBeVisible();
    }

    const spacingTokens = [...tokenCss.matchAll(/--cmt-spacing-(\d+):\s*(\d+)px;/g)].map(
      (match) => match[1],
    );
    expect(spacingTokens).toEqual([...SPACING_STEPS]);
  });

  it("defines the radius scale 4/8/12 with an 8px default", () => {
    expect(tokenCss).toContain("--cmt-radius-4: 4px;");
    expect(tokenCss).toContain("--cmt-radius-8: 8px;");
    expect(tokenCss).toContain("--cmt-radius-12: 12px;");
    expect(tokenCss).toContain("--cmt-radius-default: var(--cmt-radius-8);");
    render(<FoundationSpecimen />);

    expect(screen.getByText("--cmt-radius-4")).toBeVisible();
    expect(screen.getByText("--cmt-radius-8")).toBeVisible();
    expect(screen.getByText("--cmt-radius-12")).toBeVisible();
    expect(screen.getByText("--cmt-radius-default")).toBeVisible();
  });

  it("defines e0 as none and e1/e2/e3 with the approved shadow values", () => {
    for (const level of ["e0", "e1", "e2", "e3"]) {
      const match = tokenCss.match(new RegExp(`--cmt-elevation-${level}:\\s*([^;]+);`));
      expect(match).not.toBeNull();
      expect(normalize(match![1])).toBe(normalize(ELEVATION_VALUES[level]));
    }
  });

  it("keeps depth border-first: structure specimens carry no elevation", () => {
    for (const selector of ["\\.surfaceSample", "\\.specimen", "\\.section"]) {
      expect(ruleBlock(moduleCss, selector)).not.toContain("box-shadow");
    }
    for (const level of ["e0", "e1", "e2", "e3"]) {
      expect(ruleBlock(moduleCss, `\\.elevation${level.toUpperCase()}`)).toContain(
        `box-shadow: var(--cmt-elevation-${level});`,
      );
    }
  });

  it("applies the 2px primary focus ring with 2px surface separation", () => {
    expect(tokenCss).toContain("--cmt-focus-ring-color: var(--md-sys-color-primary);");
    expect(tokenCss).toContain("--cmt-focus-ring-width: 2px;");
    expect(tokenCss).toContain("--cmt-focus-ring-separation: 2px;");
    const focusBlock = ruleBlock(moduleCss, "\\.focusSpecimen:focus");
    expect(focusBlock).toContain(
      "outline: var(--cmt-focus-ring-width) solid var(--cmt-focus-ring-color);",
    );
    expect(focusBlock).toContain("outline-offset: var(--cmt-focus-ring-separation);");
  });
});
