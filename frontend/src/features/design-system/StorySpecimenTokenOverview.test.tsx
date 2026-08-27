import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { StorySpecimenTokenOverview } from "./StorySpecimenTokenOverview";

afterEach(() => {
  cleanup();
});

describe("StorySpecimenTokenOverview", () => {
  it("reviews the fixed dark scheme and its settings", () => {
    render(<StorySpecimenTokenOverview />);

    expect(screen.getByRole("heading", { name: "TokenOverview" })).toBeVisible();
    expect(screen.getByText("Fixed dark Material scheme")).toBeVisible();
    expect(screen.getByText("#3F51B5")).toBeVisible();
    expect(screen.getByText("tonal-spot")).toBeVisible();
    expect(screen.getByText("standard")).toBeVisible();
    expect(screen.getByText("dark")).toBeVisible();
    expect(screen.getByText("system-ui")).toBeVisible();
  });

  it("reviews honest artifact provenance", () => {
    render(<StorySpecimenTokenOverview />);

    expect(screen.getByText("@material/material-color-utilities 0.4.0")).toBeVisible();
    expect(screen.getByText("material-theme-builder-css-export.zip")).toBeVisible();
    expect(screen.getByText("css/dark.css")).toBeVisible();
    expect(
      screen.getByText("3c52785020f13710d531247cf71707aee7a308bdf8a84af98e1dfeab328c6608"),
    ).toBeVisible();
    expect(
      screen.getByText("e52f0cbbeb21b2d56cb22db7dddbd99ba7611b6bf55fae04003c12350382e0fb"),
    ).toBeVisible();
    expect(screen.getByText("false")).toBeVisible();
    expect(screen.getByText(/generated-unmodified inputs/)).toBeVisible();
  });

  it("reviews the Material system roles", () => {
    render(<StorySpecimenTokenOverview />);

    expect(screen.getByText("--md-sys-color-primary")).toBeVisible();
    expect(screen.getByText("--md-sys-color-on-primary-container")).toBeVisible();
    expect(screen.getByText("--md-sys-color-surface-container-highest")).toBeVisible();
    expect(screen.getByText("--md-sys-color-surface-tint")).toBeVisible();
  });

  it("reviews all 16 dedicated feedback tokens by severity", () => {
    render(<StorySpecimenTokenOverview />);

    expect(screen.getByText("Information")).toBeVisible();
    expect(screen.getByText("Success")).toBeVisible();
    expect(screen.getByText("Warning")).toBeVisible();
    expect(screen.getByText("Error")).toBeVisible();

    for (const token of [
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
    ]) {
      expect(screen.getByText(token)).toBeVisible();
    }
    expect(screen.getByText(/not aliases of the Material system roles/)).toBeVisible();
  });

  it("renders no theme switch or runtime theme controls", () => {
    render(<StorySpecimenTokenOverview />);

    expect(screen.queryByRole("button")).toBeNull();
    expect(screen.queryByLabelText(/theme|scheme/i)).toBeNull();
  });
});
