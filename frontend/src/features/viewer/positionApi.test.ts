import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchGame, fetchPosition } from "./positionApi";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "./viewerFixtures";

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

afterEach(() => vi.unstubAllGlobals());

describe("fetchGame", () => {
  it("loads the exact whole-game envelope and omits the default query", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(VIEWER_GAME));
    vi.stubGlobal("fetch", fetchMock);

    const result = await fetchGame(VIEWER_GAME_UUID);

    expect(result).toEqual({ status: "success", game: VIEWER_GAME });
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:5666/api/games/${VIEWER_GAME_UUID}/positions`,
      { signal: undefined },
    );
  });

  it("passes an explicit initial Ply and signal without ever constructing a per-ply URL", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ ...VIEWER_GAME, initial_ply: 2 }));
    vi.stubGlobal("fetch", fetchMock);
    const controller = new AbortController();

    const result = await fetchGame(VIEWER_GAME_UUID, 2, controller.signal);

    expect(result.status).toBe("success");
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:5666/api/games/${VIEWER_GAME_UUID}/positions?ply=2`,
      { signal: controller.signal },
    );
    expect(fetchMock.mock.calls[0][0]).not.toContain("positions/2");
  });

  it.each([
    [{ ...VIEWER_GAME, extra: true }],
    [{ ...VIEWER_GAME, positions: [{ ...VIEWER_GAME.positions[0], extra: true }] }],
    [{ ...VIEWER_GAME, positions: VIEWER_GAME.positions.slice(1) }],
    [{ ...VIEWER_GAME, initial_ply: 99 }],
    [{ ...VIEWER_GAME, source_url: "https://example.com/unsafe" }],
  ])("rejects a non-exact success response", async (body) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(body)));

    await expect(fetchGame(VIEWER_GAME_UUID)).resolves.toEqual({
      status: "unexpected_failure",
    });
  });

  it.each([
    [404, "game_not_found", "technical detail"],
    [404, "position_not_found", "technical detail"],
    [503, "corpus_unavailable", "technical detail"],
    [500, "game_unavailable", "technical detail"],
    [500, "unexpected_failure", "technical detail"],
    [502, "other", "technical detail"],
  ] as const)("maps only the typed HTTP error %s/%s", async (status, code, message) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ code, message }, status)));

    await expect(fetchGame(VIEWER_GAME_UUID)).resolves.toEqual({
      status: code === "other" ? "unexpected_failure" : code,
    });
  });
});

describe("fetchPosition", () => {
  it("preserves the exact legacy single-position success contract", async () => {
    const body = {
      game_uuid: VIEWER_GAME_UUID,
      ply: 1,
      fen: VIEWER_GAME.positions[1].fen,
      subject_color: "white",
    };
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(body));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchPosition(VIEWER_GAME_UUID, 1)).resolves.toEqual({
      status: "success",
      ...body,
    });
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:5666/api/games/${VIEWER_GAME_UUID}/positions/1`,
      { signal: undefined },
    );
  });

  it.each([
    [404, "position_not_found"],
    [503, "corpus_unavailable"],
    [500, "stored_position_invalid"],
    [500, "unexpected_failure"],
  ] as const)("preserves typed legacy failure %s/%s", async (status, code) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ code }, status)));

    await expect(fetchPosition(VIEWER_GAME_UUID, 1)).resolves.toEqual({ status: code });
  });
});
