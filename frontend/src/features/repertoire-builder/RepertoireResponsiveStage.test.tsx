import userEvent from "@testing-library/user-event";
import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { RepertoireResponsiveStage } from "./RepertoireResponsiveStage";

type ResizeObserverInstance = {
  observe: ReturnType<typeof vi.fn>;
  disconnect: ReturnType<typeof vi.fn>;
  trigger: (width: number) => void;
};

const resizeObservers: ResizeObserverInstance[] = [];
let stageWidth = 0;

class ResizeObserverMock {
  private readonly callback: ResizeObserverCallback;
  private element: Element | null = null;
  readonly observe = vi.fn((element: Element) => {
    this.element = element;
  });
  readonly disconnect = vi.fn();

  constructor(callback: ResizeObserverCallback) {
    this.callback = callback;
    resizeObservers.push(this as unknown as ResizeObserverInstance);
  }

  trigger(width: number) {
    stageWidth = width;
    this.callback(
      [
        {
          target: this.element,
          contentRect: { width },
        } as ResizeObserverEntry,
      ],
      this as unknown as ResizeObserver,
    );
  }
}

function fixture() {
  return (
    <RepertoireResponsiveStage
      board={
        <div data-lane="board" data-testid="fixture-board">
          Board
        </div>
      }
      session={
        <div data-lane="session" data-testid="fixture-session">
          Session
        </div>
      }
      engine={
        <div data-lane="engine" data-testid="fixture-engine">
          Engine
        </div>
      }
    />
  );
}

function stage() {
  return screen.getByTestId("repertoire-workspace-stage");
}

function panelSizes() {
  return ["board", "session", "engine"].map((id) => screen.getByTestId(id).style.flexGrow);
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  resizeObservers.length = 0;
});

beforeEach(() => {
  vi.stubGlobal("ResizeObserver", ResizeObserverMock);
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockImplementation(function (
    this: HTMLElement,
  ) {
    if (
      this.matches("[data-testid='repertoire-workspace-stage']") ||
      this.matches("[data-group]")
    ) {
      return {
        width: stageWidth,
        height: 500,
        top: 0,
        right: stageWidth,
        bottom: 500,
        left: 0,
      } as DOMRect;
    }
    if (this.matches("[data-separator]")) {
      return { width: 12, height: 500, top: 0, right: 12, bottom: 500, left: 0 } as DOMRect;
    }
    return { width: 0, height: 0, top: 0, right: 0, bottom: 0, left: 0 } as DOMRect;
  });
  const widthFor = (element: HTMLElement) => {
    if (element.matches("[data-separator]")) {
      return 12;
    }
    if (!element.matches("[data-panel]")) {
      return 0;
    }

    const panels = element.parentElement?.querySelectorAll("[data-panel]").length ?? 1;
    const space = stageWidth - Math.max(0, panels - 1) * 12;
    const flexGrow = Number(element.style.flexGrow);
    if (flexGrow > 0) {
      return (space * flexGrow) / 100;
    }
    const basis = Number.parseFloat(element.style.flexBasis);
    return Number.isFinite(basis) && basis > 0 ? basis : space / panels;
  };
  vi.spyOn(HTMLElement.prototype, "offsetWidth", "get").mockImplementation(function (
    this: HTMLElement,
  ) {
    return widthFor(this);
  });
  vi.spyOn(HTMLElement.prototype, "offsetLeft", "get").mockImplementation(function (
    this: HTMLElement,
  ) {
    if (
      !this.parentElement ||
      (!this.matches("[data-panel]") && !this.matches("[data-separator]"))
    ) {
      return 0;
    }
    let left = 0;
    for (const sibling of Array.from(this.parentElement.children)) {
      if (sibling === this) {
        break;
      }
      left += widthFor(sibling as HTMLElement);
    }
    return left;
  });
});

describe("RepertoireResponsiveStage", () => {
  it.each([
    [699, "narrow", 0],
    [700, "medium", 1],
    [1039, "medium", 1],
    [1040, "wide", 2],
  ] as const)("uses the measured %dpx boundary for %s mode", async (width, mode, separators) => {
    stageWidth = width;
    render(fixture());

    await waitFor(() => expect(stage()).toHaveAttribute("data-layout-mode", mode));
    expect(
      Array.from(stage().querySelectorAll("[data-lane]")).map((lane) =>
        lane.getAttribute("data-testid"),
      ),
    ).toEqual(["fixture-board", "fixture-session", "fixture-engine"]);
    expect(within(stage()).queryAllByRole("separator")).toHaveLength(separators);
    if (separators > 0) {
      expect(
        within(stage())
          .getAllByRole("separator")
          .map((separator) => separator.getAttribute("aria-label")),
      ).toEqual(
        mode === "wide"
          ? ["Board and Session boundary", "Session and Engine boundary"]
          : ["Session and Engine boundary"],
      );
    }
  });

  it("changes mode when the stage observer crosses a boundary without using viewport width", async () => {
    stageWidth = 699;
    render(fixture());
    await waitFor(() => expect(stage()).toHaveAttribute("data-layout-mode", "narrow"));

    resizeObservers[0]!.trigger(700);
    await waitFor(() => expect(stage()).toHaveAttribute("data-layout-mode", "medium"));
    expect(within(stage()).getAllByRole("separator")).toHaveLength(1);

    resizeObservers[0]!.trigger(1040);
    await waitFor(() => expect(stage()).toHaveAttribute("data-layout-mode", "wide"));
    expect(within(stage()).getAllByRole("separator")).toHaveLength(2);
  });

  it("declares valid panel minimums and restores the mode defaults through the group API", async () => {
    stageWidth = 1200;
    render(fixture());
    await waitFor(() => expect(stage()).toHaveAttribute("data-layout-mode", "wide"));

    expect(screen.getByTestId("board")).toHaveAttribute("data-panel-min-size", "320px");
    expect(screen.getByTestId("session")).toHaveAttribute("data-panel-min-size", "280px");
    expect(screen.getByTestId("engine")).toHaveAttribute("data-panel-min-size", "360px");
    const defaults = panelSizes();
    expect(defaults.every(Boolean)).toBe(true);

    const user = userEvent.setup();
    const separator = within(stage()).getByRole("separator", {
      name: "Board and Session boundary",
    });
    separator.focus();
    await user.keyboard("{ArrowRight}");
    await waitFor(() => expect(panelSizes()).not.toEqual(defaults));

    await user.click(screen.getByRole("button", { name: "Reset panel layout" }));
    await waitFor(() => expect(panelSizes()).toEqual(defaults));
  });

  it("renders no resize controls in the narrow stack", async () => {
    stageWidth = 699;
    render(fixture());
    await waitFor(() => expect(stage()).toHaveAttribute("data-layout-mode", "narrow"));

    expect(within(stage()).queryByRole("separator")).not.toBeInTheDocument();
    expect(within(stage()).getByTestId("fixture-board")).toBeVisible();
    expect(within(stage()).getByTestId("fixture-session")).toBeVisible();
    expect(within(stage()).getByTestId("fixture-engine")).toBeVisible();
  });
});
