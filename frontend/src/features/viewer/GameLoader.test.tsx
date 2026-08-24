import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { GameLoader } from "./GameLoader";
import { VIEWER_GAME_UUID } from "./viewerFixtures";

afterEach(() => cleanup());

describe("GameLoader", () => {
  it("starts expanded with optional Ply and native form controls", () => {
    render(<GameLoader />);

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
    render(<GameLoader onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.click(screen.getByRole("button", { name: "Load game" }));

    expect(onSubmit).toHaveBeenCalledWith({ gameUuid: VIEWER_GAME_UUID, ply: "" });
  });

  it("rejects malformed UUID and non-whole Ply before submission", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<GameLoader onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText("Game UUID"), "not-a-uuid");
    await user.type(screen.getByLabelText(/Ply/), "-1");
    await user.click(screen.getByRole("button", { name: "Load game" }));

    expect(screen.getByRole("alert")).toHaveTextContent("valid game UUID");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("keeps Reset available while loading and exposes a polite loading state", () => {
    render(<GameLoader status="loading" gameUuid={VIEWER_GAME_UUID} />);

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
    render(<GameLoader status={status} />);

    expect(screen.getByRole("alert")).toHaveTextContent(heading);
  });

  it("clears local values and calls reset", async () => {
    const onReset = vi.fn();
    const user = userEvent.setup();
    render(<GameLoader onReset={onReset} />);

    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.type(screen.getByLabelText(/Ply/), "2");
    await user.click(screen.getByRole("button", { name: "Reset" }));

    expect(screen.getByLabelText("Game UUID")).toHaveValue("");
    expect(screen.getByLabelText(/Ply/)).toHaveValue("");
    expect(onReset).toHaveBeenCalledOnce();
  });
});
