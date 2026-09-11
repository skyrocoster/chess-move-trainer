import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const here = dirname(fileURLToPath(import.meta.url));
const tokenCss = readFileSync(join(here, "../../styles/cmt-tokens.css"), "utf8");

const FEEDBACK_TOKENS = [
  "--cmt-info-accent",
  "--cmt-info-on-accent",
  "--cmt-info-container",
  "--cmt-info-on-container",
  "--cmt-success-accent",
  "--cmt-success-on-accent",
  "--cmt-success-container",
  "--cmt-success-on-container",
  "--cmt-warning-accent",
  "--cmt-warning-on-accent",
  "--cmt-warning-container",
  "--cmt-warning-on-container",
  "--cmt-error-accent",
  "--cmt-error-on-accent",
  "--cmt-error-container",
  "--cmt-error-on-container",
] as const;

describe("design token contract", () => {
  it("defines the shared focus ring treatment", () => {
    expect(tokenCss).toContain("--cmt-focus-ring-color: var(--md-sys-color-primary);");
    expect(tokenCss).toContain("--cmt-focus-ring-width: 2px;");
    expect(tokenCss).toContain("--cmt-focus-ring-separation: 2px;");
  });

  it("defines all 16 dedicated feedback tokens", () => {
    for (const token of FEEDBACK_TOKENS) {
      expect(tokenCss).toContain(`${token}:`);
    }
  });
});
