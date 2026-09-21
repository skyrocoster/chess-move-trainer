import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { NavigationMenu } from "../NavigationMenu";
import { ContextMenu } from "./ContextMenu";
import { Menu } from "./Menu";
import { Menubar } from "./Menubar";

afterEach(cleanup);

describe("menu and navigation primitives", () => {
  it("runs actions from a button-triggered menu", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(
      <Menu trigger="Position actions" items={[{ id: "copy", label: "Copy FEN", onSelect }]} />,
    );

    fireEvent.mouseDown(screen.getByRole("button", { name: "Position actions" }));
    await user.click(await screen.findByText("Copy FEN"));
    expect(onSelect).toHaveBeenCalledOnce();
  });

  it("opens a context menu for a consumer-owned region", () => {
    render(
      <ContextMenu items={[{ id: "annotate", label: "Add comment" }]}>
        <span>Move e4</span>
      </ContextMenu>,
    );

    fireEvent.contextMenu(screen.getByText("Move e4"));
    expect(screen.getByText("Add comment")).toBeInTheDocument();
  });

  it("composes related menus into a menubar", () => {
    render(
      <Menubar
        aria-label="Editor commands"
        menus={[
          { id: "file", label: "File", items: [{ id: "save", label: "Save" }] },
          { id: "edit", label: "Edit", items: [{ id: "undo", label: "Undo" }] },
        ]}
      />,
    );

    expect(screen.getByRole("menubar", { name: "Editor commands" })).toBeVisible();
    expect(screen.getByRole("menuitem", { name: "File" })).toHaveAttribute("aria-haspopup", "menu");
    expect(screen.getByRole("menuitem", { name: "Edit" })).toBeVisible();
  });

  it("renders direct and grouped navigation links", () => {
    render(
      <NavigationMenu
        aria-label="Primary"
        defaultValue="train"
        items={[
          {
            id: "train",
            label: "Train",
            links: [
              { id: "due", label: "Due moves", href: "/trainer", description: "Practice now" },
            ],
          },
          { id: "analysis", label: "Analysis", href: "/analysis" },
        ]}
      />,
    );

    expect(screen.getByRole("navigation", { name: "Primary" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Analysis" })).toHaveAttribute("href", "/analysis");
    expect(screen.getByRole("link", { name: /Due moves/ })).toHaveAttribute("href", "/trainer");
  });
});
