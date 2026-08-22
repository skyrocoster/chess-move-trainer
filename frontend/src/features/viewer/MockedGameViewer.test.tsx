import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";

import { MockedGameViewer } from "./MockedGameViewer";
import styles from "./MockedGameViewer.module.css";

afterEach(() => cleanup());

describe("MockedGameViewer", () => {
  it("owns an ancestor container so the workspace grid reflows instead of querying itself", () => {
    const { container } = render(<MockedGameViewer scenario="intermediate" />);

    const workspace = container.querySelector(`.${styles.workspace}`);
    const viewer = container.querySelector(`.${styles.viewer}`);

    expect(viewer).not.toBeNull();
    expect(workspace).not.toBeNull();
    expect(viewer).not.toBe(workspace);
    expect(viewer!.contains(workspace)).toBe(true);
  });

  it("keeps the production viewer untouched while composing the Stage 1 surface", () => {
    render(<MockedGameViewer scenario="empty" />);

    expect(screen.getByRole("button", { name: "Game Loader" })).toBeVisible();
    const toolbar = screen.getByRole("toolbar", { name: "Board controls" });
    expect(within(toolbar).getAllByRole("button")).toHaveLength(2);
    expect(screen.getByRole("button", { name: "Game Context" })).toBeVisible();
    expect(screen.getByRole("img", { name: /standard starting position/ })).toBeVisible();
  });

  it("traverses the deterministic mocked game one ply and announces the new context", async () => {
    const user = userEvent.setup();
    render(<MockedGameViewer scenario="intermediate" />);

    await user.click(screen.getByRole("button", { name: "Next" }));

    expect(screen.getByText("Ply 2 of 3")).toBeVisible();
    expect(screen.getByRole("status")).toHaveTextContent("Ply 2 of 3: e5");
  });

  it("keeps the board and prior context visible for replacement failure", () => {
    render(<MockedGameViewer scenario="replacement_failure" />);

    expect(screen.getByText("Game unavailable")).toBeVisible();
    expect(screen.getByText("Ply 1 of 3")).toBeVisible();
    expect(screen.getByRole("img", { name: /ply 1/ })).toBeVisible();
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
  });

  it("resets the mocked composition to the static board and empty panels", async () => {
    const user = userEvent.setup();
    render(<MockedGameViewer scenario="intermediate" />);

    await user.click(screen.getByRole("button", { name: "Reset" }));

    expect(screen.getAllByText("No game loaded")).toHaveLength(2);
    expect(screen.getByRole("img", { name: /standard starting position/ })).toBeVisible();
  });
});
