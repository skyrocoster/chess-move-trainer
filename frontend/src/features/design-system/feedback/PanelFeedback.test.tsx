import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { PanelFeedback } from "./PanelFeedback";
import styles from "./PanelFeedback.module.css";
import type { FeedbackSeverity } from "./feedbackTypes";

const here = dirname(fileURLToPath(import.meta.url));
const tokenCss = readFileSync(join(here, "../../../styles/cmt-tokens.css"), "utf8");
const moduleCss = readFileSync(join(here, "PanelFeedback.module.css"), "utf8");

const SEVERITIES: FeedbackSeverity[] = ["information", "success", "warning", "error"];

const TOKEN_SET: Record<FeedbackSeverity, [string, string, string, string]> = {
  information: [
    "--cmt-info-accent",
    "--cmt-info-on-accent",
    "--cmt-info-container",
    "--cmt-info-on-container",
  ],
  success: [
    "--cmt-success-accent",
    "--cmt-success-on-accent",
    "--cmt-success-container",
    "--cmt-success-on-container",
  ],
  warning: [
    "--cmt-warning-accent",
    "--cmt-warning-on-accent",
    "--cmt-warning-container",
    "--cmt-warning-on-container",
  ],
  error: [
    "--cmt-error-accent",
    "--cmt-error-on-accent",
    "--cmt-error-container",
    "--cmt-error-on-container",
  ],
};

afterEach(() => {
  cleanup();
});

describe("PanelFeedback", () => {
  it("delegates presentation content to the shared FeedbackCore", () => {
    render(
      <PanelFeedback severity="information" heading="Information" message="A shared message" />,
    );

    expect(screen.getByTestId("core-information")).toBeVisible();
    expect(screen.getByRole("heading", { name: "Information" })).toBeVisible();
    expect(screen.getByText("A shared message")).toBeVisible();
  });

  it.each(SEVERITIES)("uses the filled %s severity container", (severity) => {
    const { container } = render(
      <PanelFeedback severity={severity} message={`${severity} message`} />,
    );

    const panel = container.querySelector(`[data-severity="${severity}"]`);
    expect(panel).toBeInTheDocument();
    expect(panel).toHaveClass(styles.panel);
    expect(screen.getByTestId(`core-${severity}`)).toBeVisible();

    for (const token of TOKEN_SET[severity]) {
      expect(tokenCss).toContain(`${token}:`);
    }
    expect(moduleCss).toContain(`var(${TOKEN_SET[severity][0]})`);
    expect(moduleCss).toContain(`var(${TOKEN_SET[severity][2]})`);
    expect(moduleCss).toContain(`var(${TOKEN_SET[severity][3]})`);
  });

  it("requires a message while allowing an optional heading", () => {
    const { rerender } = render(
      <PanelFeedback severity="success" message="Message without heading" />,
    );

    expect(screen.getByText("Message without heading")).toBeVisible();
    expect(screen.queryByRole("heading")).not.toBeInTheDocument();

    rerender(
      <PanelFeedback
        severity="success"
        heading="Optional heading"
        message="Message with heading"
      />,
    );

    expect(screen.getByRole("heading", { name: "Optional heading" })).toBeVisible();
    expect(screen.getByText("Message with heading")).toBeVisible();
  });

  it("does not add an automatic announcement role", () => {
    render(<PanelFeedback severity="warning" message="No announcement default" />);

    const core = screen.getByTestId("core-warning");
    expect(core).not.toHaveAttribute("role");
    expect(core).not.toHaveAttribute("aria-live");
  });
});
