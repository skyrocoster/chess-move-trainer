import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  PreferredMoveActionLayout,
  PreferredMoveChoiceBox,
  PreferredMoveConsequence,
  PreferredMoveConnector,
  PreferredMoveDate,
  PreferredMoveValue,
} from "./PreferredMovePrimitives";
import primitiveStyles from "./PreferredMovePrimitives.module.css";
import { RemovePreferredMoveButton, SavePreferredMoveButton } from "./PreferredMoveActionButtons";

afterEach(() => {
  cleanup();
});

const here = dirname(fileURLToPath(import.meta.url));
const actionCss = readFileSync(join(here, "PreferredMoveActionButtons.module.css"), "utf8");
const primitiveCss = readFileSync(join(here, "PreferredMovePrimitives.module.css"), "utf8");

describe("preferred move primitives", () => {
  it("renders both labelled choice boxes, move values, date, connector, and consequence", () => {
    render(
      <div>
        <PreferredMoveChoiceBox
          label="Current saved choice"
          tone="saved"
          move={{ san: "e4", uci: "e2e4" }}
          effectiveDate={new Date("2026-08-29T00:00:00Z")}
        />
        <PreferredMoveChoiceBox
          label="Staged move"
          tone="proposal"
          move={{ san: "d4", uci: "d2d4" }}
        />
        <PreferredMoveConnector label="replace" />
        <PreferredMoveConsequence kind="replacement" stagedSan="d4" savedSan="e4" />
        <PreferredMoveDate value={null} onChange={vi.fn()} />
      </div>,
    );

    expect(screen.getByRole("region", { name: "Current saved choice" })).toBeVisible();
    expect(screen.getByRole("region", { name: "Staged move" })).toBeVisible();
    expect(screen.getByText("e4")).toBeVisible();
    expect(screen.getByText("e2e4")).toBeVisible();
    expect(screen.getByText("Effective date")).toBeVisible();
    expect(screen.getByText("2026-08-29")).toBeVisible();
    expect(screen.getByText("Save d4 to replace e4.")).toBeVisible();
    expect(screen.queryByTestId("calendar-date-popup")).not.toBeInTheDocument();

    const connector = screen.getByText("replace").closest('[aria-hidden="true"]');
    expect(connector).toHaveTextContent("replace");
  });

  it("keeps consequence copy component-owned for each supported relationship", () => {
    render(
      <div>
        <PreferredMoveConsequence kind="first-choice" stagedSan="d4" />
        <PreferredMoveConsequence kind="replacement" stagedSan="c4" savedSan="e4" />
        <PreferredMoveConsequence kind="matching" savedSan="e4" />
      </div>,
    );

    expect(screen.getByText("Save d4 as the current saved choice.")).toBeVisible();
    expect(screen.getByText("Save c4 to replace e4.")).toBeVisible();
    expect(screen.getByText("e4 is already the current saved choice.")).toBeVisible();
  });

  it("makes an assigned saved choice a reusable keyboard-activated button", async () => {
    const user = userEvent.setup();
    const onActivate = vi.fn();

    render(
      <PreferredMoveChoiceBox
        label="Current saved choice"
        tone="saved"
        move={{ san: "e4", uci: "e2e4" }}
        onActivate={onActivate}
        activationLabel="Current saved choice: e4; play and stage this move."
      />,
    );

    const savedChoice = screen.getByRole("button", {
      name: "Current saved choice: e4; play and stage this move.",
    });
    await user.tab();
    expect(savedChoice).toHaveFocus();
    await user.keyboard("{Enter}");
    await user.keyboard(" ");

    expect(onActivate).toHaveBeenCalledTimes(2);
    expect(savedChoice.tagName).toBe("BUTTON");
  });
});

describe("preferred move action buttons", () => {
  it("keeps Save and Remove independently reusable with fixed labels and hierarchy", () => {
    render(
      <PreferredMoveActionLayout>
        <SavePreferredMoveButton />
        <RemovePreferredMoveButton />
      </PreferredMoveActionLayout>,
    );

    const save = screen.getByRole("button", { name: "Save" });
    const remove = screen.getByRole("button", { name: "Remove" });
    expect(save.className).toContain("primary");
    expect(remove.className).toContain("ghost");
    expect(remove.className).toContain("removeButton");
    expect(save.querySelector("svg")).toHaveAttribute("aria-hidden", "true");
    expect(remove.querySelector("svg")).toHaveAttribute("aria-hidden", "true");
    expect(save.querySelector("svg")).toHaveAttribute("focusable", "false");
    expect(remove.querySelector("svg")).toHaveAttribute("focusable", "false");
    expect(screen.getByRole("button", { name: "Save" }).parentElement).toHaveClass(
      primitiveStyles.actionLayout,
    );
  });

  it("supports move-specific Save copy without changing the reusable action semantics", () => {
    render(<SavePreferredMoveButton label="Save e4" />);

    const save = screen.getByRole("button", { name: "Save e4" });
    expect(save).toBeEnabled();
    expect(save.className).toContain("primary");
    expect(save.querySelector("svg")).toHaveAttribute("aria-hidden", "true");
  });

  it("disables pending operations while retaining their accessible labels", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    const onRemove = vi.fn();

    render(
      <>
        <SavePreferredMoveButton pending onClick={onSave} />
        <RemovePreferredMoveButton disabled onClick={onRemove} />
      </>,
    );

    const save = screen.getByRole("button", { name: "Save" });
    const remove = screen.getByRole("button", { name: "Remove" });
    expect(save).toBeDisabled();
    expect(save).toHaveAttribute("aria-busy", "true");
    expect(remove).toBeDisabled();
    await user.click(save);
    await user.click(remove);
    expect(onSave).not.toHaveBeenCalled();
    expect(onRemove).not.toHaveBeenCalled();
  });

  it("uses the shared icon box, label gap, and focus foundation", () => {
    expect(actionCss).toContain("gap: var(--cmt-spacing-8);");
    expect(actionCss).toContain("inline-size: var(--cmt-spacing-16);");
    expect(actionCss).toContain("block-size: var(--cmt-spacing-16);");
    expect(primitiveCss).toContain("gap: var(--cmt-spacing-8);");
    expect(primitiveCss).toContain(
      "outline: var(--cmt-focus-ring-width) solid var(--cmt-focus-ring-color);",
    );
    expect(primitiveCss).toContain("outline-offset: var(--cmt-focus-ring-separation);");
  });

  it("activates the reusable Save action with normal keyboard behavior", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();

    render(<SavePreferredMoveButton onClick={onSave} />);
    const save = screen.getByRole("button", { name: "Save" });
    await user.tab();
    await user.keyboard("{Enter}");

    expect(save).toHaveFocus();
    expect(onSave).toHaveBeenCalledOnce();
  });

  it("renders a real date trigger through the existing CalendarDate primitive", () => {
    render(<PreferredMoveDate value={null} onChange={vi.fn()} />);

    expect(
      screen.getByRole("button", { name: "Change effective date: Choose date" }),
    ).toBeVisible();
  });

  it("renders a move value independently from a choice box", () => {
    render(<PreferredMoveValue san="Nf3" uci="g1f3" />);

    expect(screen.getByText("Nf3")).toBeVisible();
    expect(screen.getByText("g1f3")).toBeVisible();
  });
});
