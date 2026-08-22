import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { GameContext } from "./GameContext";
import { STAGE1_GAME, STAGE1_UNSAFE_SOURCE_GAME } from "./stage1GameTypes";
import { safeSourceUrl } from "./stage1SourceSafety";

afterEach(() => cleanup());

describe("GameContext", () => {
  it("starts expanded with the empty state", () => {
    render(<GameContext />);

    expect(screen.getByRole("button", { name: "Game Context" })).toHaveAttribute(
      "aria-expanded",
      "true",
    );
    expect(screen.getByText("No game loaded")).toBeVisible();
  });

  it("shows only the current ply, SAN/initial text, and source attribution", () => {
    render(<GameContext game={STAGE1_GAME} position={STAGE1_GAME.positions[0]} />);

    expect(screen.getByText("Ply 0 of 3")).toBeVisible();
    expect(screen.getByText("Initial position")).toBeVisible();
    expect(screen.getByRole("link", { name: "Chess.com game" })).toHaveAttribute(
      "target",
      "_blank",
    );
    expect(screen.queryByText(STAGE1_GAME.game_uuid)).not.toBeInTheDocument();
  });

  it("renders unsafe source data as unavailable without a link", () => {
    render(
      <GameContext
        game={STAGE1_UNSAFE_SOURCE_GAME}
        position={STAGE1_UNSAFE_SOURCE_GAME.positions[1]}
      />,
    );

    expect(screen.getByText("Source unavailable")).toBeVisible();
    expect(screen.queryByRole("link", { name: "Chess.com game" })).not.toBeInTheDocument();
    expect(screen.getByText("Ply 1 of 3")).toBeVisible();
  });

  it("accepts only HTTPS Chess.com live and daily URLs", () => {
    expect(safeSourceUrl("https://www.chess.com/game/live/140399891142")).toBe(
      "https://www.chess.com/game/live/140399891142",
    );
    expect(safeSourceUrl("https://www.chess.com/game/daily/123")).toBe(
      "https://www.chess.com/game/daily/123",
    );
    expect(safeSourceUrl("http://www.chess.com/game/live/123")).toBeNull();
    expect(safeSourceUrl("https://example.com/game/live/123")).toBeNull();
  });
});
