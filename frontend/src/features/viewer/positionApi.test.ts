import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchGame } from "./positionApi";
import { STAGE1_GAME, STAGE1_GAME_UUID } from "./stage1GameTypes";

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
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(STAGE1_GAME));
    vi.stubGlobal("fetch", fetchMock);

    const result = await fetchGame(STAGE1_GAME_UUID);

    expect(result).toEqual({ status: "success", game: STAGE1_GAME });
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:5666/api/games/${STAGE1_GAME_UUID}/positions`,
      { signal: undefined },
    );
  });

  it("passes an explicit initial Ply and signal without ever constructing a per-ply URL", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ ...STAGE1_GAME, initial_ply: 2 }));
    vi.stubGlobal("fetch", fetchMock);
    const controller = new AbortController();

    const result = await fetchGame(STAGE1_GAME_UUID, 2, controller.signal);

    expect(result.status).toBe("success");
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:5666/api/games/${STAGE1_GAME_UUID}/positions?ply=2`,
      { signal: controller.signal },
    );
    expect(fetchMock.mock.calls[0][0]).not.toContain("positions/2");
  });

  it.each([
    [{ ...STAGE1_GAME, extra: true }],
    [{ ...STAGE1_GAME, positions: [{ ...STAGE1_GAME.positions[0], extra: true }] }],
    [{ ...STAGE1_GAME, positions: STAGE1_GAME.positions.slice(1) }],
    [{ ...STAGE1_GAME, initial_ply: 99 }],
    [{ ...STAGE1_GAME, source_url: "https://example.com/unsafe" }],
  ])("rejects a non-exact success response", async (body) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(body)));

    await expect(fetchGame(STAGE1_GAME_UUID)).resolves.toEqual({
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

    await expect(fetchGame(STAGE1_GAME_UUID)).resolves.toEqual({
      status: code === "other" ? "unexpected_failure" : code,
    });
  });
});
