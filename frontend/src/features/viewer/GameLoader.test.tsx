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
import { VIEWER_GAME_UUID } from "./viewerFixtures";

afterEach(() => cleanup());

expect.extend(matchers);

const here = dirname(fileURLToPath(import.meta.url));
const rawStyles = readFileSync(join(here, "GameLoader.module.css"), "utf8");

type LoaderHarnessProps = Omit<
  ComponentProps<typeof GameLoader>,
  "gameUuid" | "ply" | "onGameUuidChange" | "onPlyChange"
> & {
  gameUuid?: string;
  ply?: string;
  onGameUuidChange?: (value: string) => void;
  onPlyChange?: (value: string) => void;
};

function ControlledGameLoader({
  gameUuid: initialGameUuid = "",
  ply: initialPly = "",
  onGameUuidChange,
  onPlyChange,
  ...props
}: LoaderHarnessProps) {
  const [gameUuid, setGameUuid] = useState(initialGameUuid);
  const [ply, setPly] = useState(initialPly);

  return (
    <GameLoader
      {...props}
      gameUuid={gameUuid}
      ply={ply}
      onGameUuidChange={(value) => {
        setGameUuid(value);
        onGameUuidChange?.(value);
      }}
      onPlyChange={(value) => {
        setPly(value);
        onPlyChange?.(value);
      }}
    />
  );
}

function renderLoader(props: LoaderHarnessProps = {}) {
  return render(<ControlledGameLoader {...props} />);
}

describe("GameLoader", () => {
  it("follows parent-controlled values and emits raw field changes", async () => {
    const onGameUuidChange = vi.fn();
    const onPlyChange = vi.fn();
    const { rerender } = render(
      <GameLoader
        gameUuid=""
        ply=""
        onGameUuidChange={onGameUuidChange}
        onPlyChange={onPlyChange}
      />,
    );
    const user = userEvent.setup();

    await user.type(screen.getByLabelText("Game UUID"), "x");
    await user.type(screen.getByLabelText(/Ply/), "7");

    expect(onGameUuidChange).toHaveBeenLastCalledWith("x");
    expect(onPlyChange).toHaveBeenLastCalledWith("7");

    rerender(
      <GameLoader
        gameUuid={VIEWER_GAME_UUID}
        ply="2"
        onGameUuidChange={onGameUuidChange}
        onPlyChange={onPlyChange}
      />,
    );

    expect(screen.getByLabelText("Game UUID")).toHaveValue(VIEWER_GAME_UUID);
    expect(screen.getByLabelText(/Ply/)).toHaveValue("2");
  });

  it("starts expanded with optional Ply and native form controls", () => {
    renderLoader();

    expect(screen.getByRole("button", { name: "Game Loader" })).toHaveAttribute(
      "aria-expanded",
      "true",
    );
    expect(screen.getByLabelText("Game UUID")).toBeVisible();
    expect(screen.getByLabelText(/Ply/)).toBeVisible();
    expect(screen.getByRole("button", { name: "Load game" })).toHaveAttribute("type", "submit");
  });

  it("accepts blank Ply as zero without adding a request concern to the component", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    renderLoader({ onSubmit });

    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.click(screen.getByRole("button", { name: "Load game" }));

    expect(onSubmit).toHaveBeenCalledWith({ gameUuid: VIEWER_GAME_UUID, ply: "" });
  });

  it("rejects malformed UUID and non-whole Ply before submission", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    renderLoader({ onSubmit });

    await user.type(screen.getByLabelText("Game UUID"), "not-a-uuid");
    await user.type(screen.getByLabelText(/Ply/), "-1");
    await user.click(screen.getByRole("button", { name: "Load game" }));

    expect(screen.getByRole("alert")).toHaveTextContent("valid game UUID");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("rejects a non-whole Ply after accepting a valid UUID", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    renderLoader({ onSubmit });

    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.type(screen.getByLabelText(/Ply/), "-1");
    await user.click(screen.getByRole("button", { name: "Load game" }));

    expect(screen.getByRole("alert")).toHaveTextContent("Enter a whole Ply of zero or greater");
    expect(screen.getByLabelText("Game UUID")).toHaveAttribute("aria-invalid", "false");
    expect(screen.getByLabelText(/Ply/)).toHaveAttribute("aria-invalid", "true");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("trims valid UUID and Ply values only for submission", async () => {
    const onGameUuidChange = vi.fn();
    const onPlyChange = vi.fn();
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    renderLoader({ onGameUuidChange, onPlyChange, onSubmit });

    await user.type(screen.getByLabelText("Game UUID"), ` ${VIEWER_GAME_UUID} `);
    await user.type(screen.getByLabelText(/Ply/), " 2 ");
    await user.click(screen.getByRole("button", { name: "Load game" }));

    expect(onGameUuidChange).toHaveBeenLastCalledWith(` ${VIEWER_GAME_UUID} `);
    expect(onPlyChange).toHaveBeenLastCalledWith(" 2 ");
    expect(onSubmit).toHaveBeenCalledWith({ gameUuid: VIEWER_GAME_UUID, ply: "2" });
  });

  it("clears validation feedback after either field changes", async () => {
    const user = userEvent.setup();
    renderLoader();

    await user.type(screen.getByLabelText("Game UUID"), "not-a-uuid");
    await user.click(screen.getByRole("button", { name: "Load game" }));
    expect(screen.getByRole("alert")).toBeVisible();

    await user.clear(screen.getByLabelText("Game UUID"));
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("keeps Reset available while loading and exposes a polite loading state", () => {
    renderLoader({ status: "loading", gameUuid: VIEWER_GAME_UUID });

    expect(screen.getByRole("button", { name: "Load game" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Reset" })).toBeEnabled();
    expect(screen.getByRole("status")).toHaveTextContent("Loading the complete game");
  });

  it.each([
    ["game_not_found", "Game not found"],
    ["position_not_found", "Position not found"],
    ["corpus_unavailable", "Corpus unavailable"],
    ["game_unavailable", "Game unavailable"],
    ["unexpected_failure", "Unable to load game"],
  ] as const)("renders the typed %s failure", (status, heading) => {
    renderLoader({ status });

    expect(screen.getByRole("alert")).toHaveTextContent(heading);
    expect(screen.getByRole("alert")).toHaveAttribute("aria-live", "assertive");
  });

  it("keeps Reset available while loading and emits empty controlled values", async () => {
    const onGameUuidChange = vi.fn();
    const onPlyChange = vi.fn();
    const onReset = vi.fn();
    const user = userEvent.setup();
    renderLoader({
      status: "loading",
      gameUuid: VIEWER_GAME_UUID,
      ply: "2",
      onGameUuidChange,
      onPlyChange,
      onReset,
    });

    expect(screen.getByRole("status")).toHaveAttribute("aria-live", "polite");
    await user.click(screen.getByRole("button", { name: "Reset" }));

    expect(onGameUuidChange).toHaveBeenLastCalledWith("");
    expect(onPlyChange).toHaveBeenLastCalledWith("");
    expect(onReset).toHaveBeenCalledOnce();
  });

  it("clears local values and calls reset", async () => {
    const onReset = vi.fn();
    const user = userEvent.setup();
    renderLoader({ onReset });

    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.type(screen.getByLabelText(/Ply/), "2");
    await user.click(screen.getByRole("button", { name: "Reset" }));

    expect(screen.getByLabelText("Game UUID")).toHaveValue("");
    expect(screen.getByLabelText(/Ply/)).toHaveValue("");
    expect(onReset).toHaveBeenCalledOnce();
  });

  it("toggles the default-open disclosure and preserves native keyboard focus order", async () => {
    const user = userEvent.setup();
    renderLoader();
    const disclosure = screen.getByRole("button", { name: "Game Loader" });

    await user.click(disclosure);
    expect(disclosure).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByLabelText("Game UUID")).not.toBeInTheDocument();

    await user.click(disclosure);
    expect(disclosure).toHaveAttribute("aria-expanded", "true");

    expect(disclosure).toHaveFocus();
    await user.tab();
    expect(screen.getByLabelText("Game UUID")).toHaveFocus();
    await user.tab();
    expect(screen.getByLabelText(/Ply/)).toHaveFocus();
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
