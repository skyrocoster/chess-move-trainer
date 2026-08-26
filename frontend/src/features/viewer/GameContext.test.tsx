import { cleanup, render, screen } from "@testing-library/react";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";

import { GameContext } from "./GameContext";
import { safeSourceUrl } from "./stage1SourceSafety";
import { MISSING_SOURCE_GAME, UNSAFE_SOURCE_GAME, VIEWER_GAME } from "./viewerFixtures";

expect.extend(matchers);

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

  it.each([0, 1, 2, 3])("preserves exact Ply and SAN copy at position %i", (index) => {
    const position = VIEWER_GAME.positions[index];
    if (!position) {
      throw new Error(`Missing viewer fixture position at index ${index}`);
    }

    render(<GameContext game={VIEWER_GAME} position={position} />);

    expect(screen.getByText(`Ply ${position.ply} of 3`, { exact: true })).toBeVisible();
    expect(screen.getByText(position.san ?? "Initial position", { exact: true })).toBeVisible();
    expect(screen.queryByText(VIEWER_GAME.game_uuid)).not.toBeInTheDocument();
  });

  it.each([
    ["safe", VIEWER_GAME, true],
    ["unsafe", UNSAFE_SOURCE_GAME, false],
    ["missing", MISSING_SOURCE_GAME, false],
  ] as const)("handles the %s source value without changing the context", (_name, game, linked) => {
    render(<GameContext game={game} position={game.positions[1]} />);

    if (linked) {
      const sourceLink = screen.getByRole("link", { name: "Chess.com game" });
      expect(sourceLink).toHaveAttribute("href", VIEWER_GAME.source_url);
      expect(sourceLink).toHaveAttribute("target", "_blank");
      expect(sourceLink).toHaveAttribute("rel", "noopener noreferrer");
      expect(screen.queryByText("Source unavailable")).not.toBeInTheDocument();
    } else {
      expect(screen.getByText("Source unavailable")).toBeVisible();
      expect(screen.queryByRole("link", { name: "Chess.com game" })).not.toBeInTheDocument();
    }
    expect(screen.getByText("Ply 1 of 3")).toBeVisible();
  });

  it("keeps a controlled analysis child after metadata in the same disclosure", () => {
    render(
      <GameContext game={VIEWER_GAME} position={VIEWER_GAME.positions[0]}>
        <div data-testid="analysis-child">Controlled analysis child</div>
      </GameContext>,
    );

    const disclosureButton = screen.getByRole("button", { name: "Game Context" });
    const analysisChild = screen.getByTestId("analysis-child");
    const sourceLink = screen.getByRole("link", { name: "Chess.com game" });
    const contentId = disclosureButton.getAttribute("aria-controls");

    expect(disclosureButton).toHaveAttribute("aria-expanded", "true");
    expect(sourceLink.compareDocumentPosition(analysisChild)).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING,
    );
    if (!contentId) {
      throw new Error("Game Context disclosure did not expose its controlled content");
    }
    const disclosureContent = document.getElementById(contentId);
    if (!disclosureContent) {
      throw new Error(`Game Context disclosure content ${contentId} was not found`);
    }
    expect(disclosureContent).toContainElement(analysisChild);
  });

  it("preserves default-open disclosure interaction", async () => {
    const user = userEvent.setup();
    render(<GameContext game={VIEWER_GAME} position={VIEWER_GAME.positions[0]} />);

    const disclosureButton = screen.getByRole("button", { name: "Game Context" });
    const contextText = screen.getByText("Ply 0 of 3");
    expect(disclosureButton).toHaveAttribute("aria-expanded", "true");
    expect(contextText).toBeVisible();

    await user.click(disclosureButton);
    expect(disclosureButton).toHaveAttribute("aria-expanded", "false");
    expect(contextText).not.toBeVisible();

    await user.click(disclosureButton);
    expect(disclosureButton).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByText("Ply 0 of 3")).toBeVisible();
  });

  it("has no accessibility violations in empty and composed states", async () => {
    const empty = render(<GameContext />);
    expect(await axe.run(empty.container)).toHaveNoViolations();
    empty.unmount();

    const composed = render(
      <GameContext game={VIEWER_GAME} position={VIEWER_GAME.positions[2]}>
        <div data-testid="analysis-child">Controlled analysis child</div>
      </GameContext>,
    );
    expect(await axe.run(composed.container)).toHaveNoViolations();
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
    expect(safeSourceUrl("https://www.chess.com/game/live/123?tab=analysis")).toBeNull();
    expect(safeSourceUrl("https://www.chess.com/game/live/123#moves")).toBeNull();
  });
});
