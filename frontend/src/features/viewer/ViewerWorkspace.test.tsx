import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it, vi } from "vitest";

import ViewerWorkspace from "./ViewerWorkspace";
import {
  mockCorpusUnavailable,
  mockPositionNotFound,
  mockStoredPositionInvalid,
  mockSuccessBlack,
  mockSuccessWhite,
  mockUnexpectedFailure,
  type LookupResult,
  type PositionLookup,
} from "./positionLookup";

expect.extend(matchers);

const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";
const GAME_UUID = "0101b08a-ce8b-11ee-b2fd-e90263e5548c";
const SAMPLE_FEN = "rn1qk2r/1bp1bpp1/pp1ppn1p/8/4PB2/2NP1NP1/PPPQ1PBP/R3K2R b KQkq e3 0 8";

const here = dirname(fileURLToPath(import.meta.url));
const rawStyles = readFileSync(join(here, "ViewerWorkspace.module.css"), "utf8");

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

async function fillAndSubmit(
  user: ReturnType<typeof userEvent.setup>,
  uuid = GAME_UUID,
  ply = "8",
) {
  await user.type(screen.getByLabelText("Game UUID"), uuid);
  await user.type(screen.getByLabelText("Ply"), ply);
  await user.click(screen.getByRole("button", { name: "Load position" }));
}

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

describe("ViewerWorkspace", () => {
  it("renders exactly one H1 'Position viewer' with no subtitle", () => {
    render(<ViewerWorkspace />);
    const headings = screen.getAllByRole("heading", { level: 1 });

    expect(headings).toHaveLength(1);
    expect(headings[0]).toHaveTextContent("Position viewer");
    expect(screen.queryByText("One static position - read-only")).not.toBeInTheDocument();
  });

  it("renders the starting-position board with the settled label and adapter defaults", () => {
    render(<ViewerWorkspace />);
    const graphic = screen.getByRole("img", { name: BOARD_LABEL });
    const description = document.getElementById(graphic.getAttribute("aria-describedby") ?? "");

    expect(description).toHaveTextContent("Orientation: White at the bottom.");
    expect(graphic.querySelectorAll("[data-square] span").length).toBeGreaterThan(0);
    // The board adapter stays read-only: no interactive button inside the graphic.
    expect(graphic.querySelector('[role="button"]')).toBeNull();
  });

  it("keeps the Context disclosure a plain container with no complementary landmark", () => {
    const { container } = render(<ViewerWorkspace />);
    const contextTrigger = screen.getByRole("button", { name: "Context" });
    const panel = contextTrigger.closest('[class*="contextDisclosure"]');
    const workspace = container.querySelector('[class*="workspace"]');

    expect(contextTrigger).toBeVisible();
    expect(screen.queryByRole("complementary")).toBeNull();
    expect(container.querySelector("aside")).toBeNull();

    expect(panel).not.toBeNull();
    expect(workspace).not.toBeNull();
    const elements = [panel as HTMLElement, workspace as HTMLElement];
    for (const element of elements) {
      expect(element).not.toHaveAttribute("role");
      expect(element).not.toHaveAttribute("aria-label");
      expect(element).not.toHaveAttribute("aria-labelledby");
    }
  });

  it("ships the container-query omission contract with no viewport breakpoint", () => {
    expect(rawStyles).toMatch(/@container\s*\(\s*max-width:\s*40rem\s*\)/);
    expect(rawStyles.slice(rawStyles.indexOf("@container"))).toMatch(
      /\.contextDisclosure\s*\{[^}]*grid-column:\s*1\s*\/\s*-1/,
    );
    expect(rawStyles).toMatch(/@media\s*\(\s*forced-colors:\s*active\s*\)/);
    expect(rawStyles).not.toMatch(/@media\s*\(\s*(?:max-width|min-width)\s*:/);
  });

  it("has no focused axe violations at the workspace boundary", async () => {
    const { container } = render(<ViewerWorkspace />);
    const results = await axe.run({ include: [container] });

    expect(results).toHaveNoViolations();
  });

  it("rejects a malformed UUID without calling the lookup", async () => {
    const lookup = vi.fn<PositionLookup>(async () => ({ status: "unexpected_failure" }));
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={lookup} />);

    await fillAndSubmit(user, "not-a-uuid", "8");

    expect(screen.getByRole("alert")).toHaveTextContent(/valid game UUID/);
    expect(lookup).not.toHaveBeenCalled();
  });

  it("rejects a negative or non-whole ply without calling the lookup", async () => {
    const lookup = vi.fn<PositionLookup>(async () => ({ status: "unexpected_failure" }));
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={lookup} />);

    await fillAndSubmit(user, GAME_UUID, "-3");

    expect(screen.getByRole("alert")).toHaveTextContent(/whole ply/);
    expect(lookup).not.toHaveBeenCalled();
  });

  it("disables submission while loading and keeps the current board visible", async () => {
    let resolveResult!: (result: LookupResult) => void;
    const pending: PositionLookup = () =>
      new Promise<LookupResult>((resolve) => {
        resolveResult = resolve;
      });
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={pending} />);

    expect(screen.getByRole("img", { name: BOARD_LABEL })).toBeInTheDocument();
    await fillAndSubmit(user);

    expect(screen.getByRole("button", { name: "Load position" })).toBeDisabled();
    expect(screen.getByText("Loading the requested position...")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: BOARD_LABEL })).toBeInTheDocument();

    resolveResult({
      status: "success",
      game_uuid: GAME_UUID,
      ply: 8,
      fen: SAMPLE_FEN,
      subject_color: "white",
    });
    await screen.findByRole("img", { name: /ply 8, White at the bottom/ });
    expect(screen.getByRole("button", { name: "Load position" })).toBeEnabled();
  });

  it("renders a successful White lookup with identity, FEN, color, and orientation", async () => {
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={mockSuccessWhite} />);

    await fillAndSubmit(user);

    expect(
      await screen.findByRole("img", { name: new RegExp(`ply 8, White at the bottom`) }),
    ).toBeInTheDocument();
    expect(screen.getByText(GAME_UUID)).toBeInTheDocument();
    expect(screen.getByText(SAMPLE_FEN)).toBeInTheDocument();
    expect(screen.getByText("White", { selector: "dd" })).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("renders a successful Black lookup oriented with Black at the bottom", async () => {
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={mockSuccessBlack} />);

    await fillAndSubmit(user);

    expect(
      await screen.findByRole("img", { name: new RegExp(`ply 8, Black at the bottom`) }),
    ).toBeInTheDocument();
    expect(screen.getByText("Black", { selector: "dd" })).toBeInTheDocument();
  });

  it("loads the success payload through the feature API client", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        game_uuid: GAME_UUID,
        ply: 8,
        fen: SAMPLE_FEN,
        subject_color: "white",
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<ViewerWorkspace />);

    await fillAndSubmit(user);

    expect(
      await screen.findByRole("img", { name: /ply 8, White at the bottom/ }),
    ).toBeInTheDocument();
    expect(screen.getByText(SAMPLE_FEN)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:5666/api/games/${GAME_UUID}/positions/8`,
      { signal: undefined },
    );
  });

  it.each([
    [404, "position_not_found", "Position not found"],
    [503, "corpus_unavailable", "Corpus unavailable"],
    [500, "stored_position_invalid", "Stored position unavailable"],
  ] as const)("maps API error %s to the %s state", async (status, code, heading) => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ code, message: "safe" }, status)),
    );
    const user = userEvent.setup();
    render(<ViewerWorkspace />);

    await fillAndSubmit(user);

    expect(await screen.findByText(heading)).toBeInTheDocument();
    expect(screen.queryByRole("img")).toBeNull();
  });

  it("maps an unexpected API failure and a network failure to the fallback state", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ code: "other" }, 502));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<ViewerWorkspace />);

    await fillAndSubmit(user);
    expect(await screen.findByText("Unable to load position")).toBeInTheDocument();

    cleanup();
    fetchMock.mockRejectedValueOnce(new Error("offline"));
    render(<ViewerWorkspace />);
    await fillAndSubmit(user);
    expect(await screen.findByText("Unable to load position")).toBeInTheDocument();
  });

  it.each([
    [mockPositionNotFound, "Position not found"],
    [mockCorpusUnavailable, "Corpus unavailable"],
    [mockStoredPositionInvalid, "Stored position unavailable"],
    [mockUnexpectedFailure, "Unable to load position"],
  ] as const)("removes the prior board and shows the %s state", async (lookup, heading) => {
    const user = userEvent.setup();
    const { container } = render(<ViewerWorkspace lookup={lookup} />);

    await fillAndSubmit(user);

    expect(await screen.findByText(heading)).toBeInTheDocument();
    // The prior (starting) board is removed so it is not mistaken for the request.
    expect(screen.queryByRole("img")).toBeNull();
    expect(container.querySelector('[class*="failureWorkspace"]')).toBeInTheDocument();
  });

  it("resets the viewer to the empty form and the standard starting board", async () => {
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={mockSuccessWhite} />);

    await fillAndSubmit(user);
    await screen.findByRole("img", { name: /ply 8, White at the bottom/ });

    await user.click(screen.getByRole("button", { name: "Reset viewer" }));

    expect(screen.getByRole("img", { name: BOARD_LABEL })).toBeInTheDocument();
    expect((screen.getByLabelText("Game UUID") as HTMLInputElement).value).toBe("");
    expect((screen.getByLabelText("Ply") as HTMLInputElement).value).toBe("");
  });

  it("has no focused axe violations after a successful lookup", async () => {
    const { container } = render(<ViewerWorkspace lookup={mockSuccessWhite} />);
    const user = userEvent.setup();

    await fillAndSubmit(user);
    await screen.findByRole("img", { name: /ply 8, White at the bottom/ });

    const results = await axe.run({ include: [container] });
    expect(results).toHaveNoViolations();
  });
});
