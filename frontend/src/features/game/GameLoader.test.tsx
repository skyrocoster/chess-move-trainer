import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { useState, type ComponentProps } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { GameLoader } from "./GameLoader";
import { GAME_UUID } from "./gameFixtures";

afterEach(() => cleanup());

expect.extend(matchers);

const here = dirname(fileURLToPath(import.meta.url));
const rawStyles = readFileSync(join(here, "GameLoader.module.css"), "utf8");

type LoaderHarnessProps = Omit<
  ComponentProps<typeof GameLoader>,
  "gameUuid" | "onGameUuidChange"
> & {
  gameUuid?: string;
  onGameUuidChange?: (value: string) => void;
};

function ControlledGameLoader({
  gameUuid: initialGameUuid = "",
  onGameUuidChange,
  ...props
}: LoaderHarnessProps) {
  const [gameUuid, setGameUuid] = useState(initialGameUuid);

  return (
    <GameLoader
      {...props}
      gameUuid={gameUuid}
      onGameUuidChange={(value) => {
        setGameUuid(value);
        onGameUuidChange?.(value);
      }}
    />
  );
}

function renderLoader(props: LoaderHarnessProps = {}) {
  return render(<ControlledGameLoader {...props} />);
}

describe("GameLoader", () => {
  it("follows parent-controlled UUID values and emits field changes", async () => {
    const onGameUuidChange = vi.fn();
    const { rerender } = render(
      <GameLoader
        gameUuid=""
        onGameUuidChange={onGameUuidChange}
      />,
    );
    const user = userEvent.setup();

    await user.type(screen.getByLabelText("Game UUID"), "x");
    expect(onGameUuidChange).toHaveBeenLastCalledWith("x");

    rerender(<GameLoader gameUuid={GAME_UUID} onGameUuidChange={onGameUuidChange} />);
    expect(screen.getByLabelText("Game UUID")).toHaveValue(GAME_UUID);
  });

  it("starts expanded with only the UUID field", () => {
    renderLoader();

    expect(screen.getByRole("button", { name: "Game Loader" })).toHaveAttribute(
      "aria-expanded",
      "true",
    );
    expect(screen.getByLabelText("Game UUID")).toBeVisible();
    expect(screen.queryByLabelText(/Ply/)).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Load game" })).toHaveAttribute("type", "submit");
  });

  it("trims a valid UUID only for submission", async () => {
    const onGameUuidChange = vi.fn();
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    renderLoader({ onGameUuidChange, onSubmit });

    await user.type(screen.getByLabelText("Game UUID"), ` ${GAME_UUID} `);
    await user.click(screen.getByRole("button", { name: "Load game" }));

    expect(onGameUuidChange).toHaveBeenLastCalledWith(` ${GAME_UUID} `);
    expect(onSubmit).toHaveBeenCalledWith({ gameUuid: GAME_UUID });
  });

  it("rejects a malformed UUID before submission", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    renderLoader({ onSubmit });

    await user.type(screen.getByLabelText("Game UUID"), "not-a-uuid");
    await user.click(screen.getByRole("button", { name: "Load game" }));

    expect(screen.getByRole("alert")).toHaveTextContent("valid game UUID");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("clears validation feedback after the UUID changes", async () => {
    const user = userEvent.setup();
    renderLoader();

    await user.type(screen.getByLabelText("Game UUID"), "not-a-uuid");
    await user.click(screen.getByRole("button", { name: "Load game" }));
    expect(screen.getByRole("alert")).toBeVisible();

    await user.clear(screen.getByLabelText("Game UUID"));
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("keeps Reset available while loading and clears the controlled UUID", async () => {
    const onGameUuidChange = vi.fn();
    const onReset = vi.fn();
    const user = userEvent.setup();
    renderLoader({
      status: "loading",
      gameUuid: GAME_UUID,
      onGameUuidChange,
      onReset,
    });

    expect(screen.getByRole("button", { name: "Load game" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Reset" })).toBeEnabled();
    expect(screen.getByRole("status")).toHaveTextContent("Loading the complete game");
    await user.click(screen.getByRole("button", { name: "Reset" }));

    expect(onGameUuidChange).toHaveBeenLastCalledWith("");
    expect(onReset).toHaveBeenCalledOnce();
  });

  it.each([
    ["game_not_found", "Game not found"],
    ["corpus_unavailable", "Corpus unavailable"],
    ["game_unavailable", "Game unavailable"],
    ["unexpected_failure", "Unable to load game"],
  ] as const)("renders the typed %s failure", (status, heading) => {
    renderLoader({ status });

    expect(screen.getByRole("alert")).toHaveTextContent(heading);
    expect(screen.getByRole("alert")).toHaveAttribute("aria-live", "assertive");
  });

  it("clears local values and calls reset", async () => {
    const onReset = vi.fn();
    const user = userEvent.setup();
    renderLoader({ onReset });

    await user.type(screen.getByLabelText("Game UUID"), GAME_UUID);
    await user.click(screen.getByRole("button", { name: "Reset" }));

    expect(screen.getByLabelText("Game UUID")).toHaveValue("");
    expect(onReset).toHaveBeenCalledOnce();
  });

  it("preserves native keyboard focus order", async () => {
    const user = userEvent.setup();
    renderLoader();
    const disclosure = screen.getByRole("button", { name: "Game Loader" });

    await user.click(disclosure);
    expect(disclosure).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByLabelText("Game UUID")).not.toBeInTheDocument();
    await user.click(disclosure);
    expect(disclosure).toHaveFocus();
    await user.tab();
    expect(screen.getByLabelText("Game UUID")).toHaveFocus();
    await user.tab();
    expect(screen.getByRole("button", { name: "Load game" })).toHaveFocus();
    await user.tab();
    expect(screen.getByRole("button", { name: "Reset" })).toHaveFocus();
  });

  it("retains the constrained and forced-colors CSS boundaries", () => {
    expect(rawStyles).toMatch(/@container\s*\(max-width:\s*40rem\)/);
    expect(rawStyles).not.toMatch(/@media\s*\(\s*(?:max-width|min-width)\s*:/);
    expect(rawStyles).toMatch(/@media\s*\(forced-colors:\s*active\)/);
    expect(rawStyles).toMatch(/--cmt-focus-ring-width/);
    expect(rawStyles).toMatch(/--md-sys-color-error-container/);
  });

  it("has no focused axe violations at the controlled boundary", async () => {
    const { container } = renderLoader();
    const results = await axe.run({ include: [container] });

    expect(results).toHaveNoViolations();
  });
});
