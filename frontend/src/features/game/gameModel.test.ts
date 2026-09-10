import { describe, expect, it } from "vitest";

import type { GameDetailResponse } from "../../api/client";
import { mapGameDetailResponse } from "./gameModel";

const INITIAL_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 7 42";
const AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 42";
const AFTER_E5_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 43";
const AFTER_NF3_FEN = "rnbqkbnr/pppp1ppp/8/4p3/5N2/8/PPPP1PPP/RNBQKB1R b KQkq - 1 43";

const DETAIL: GameDetailResponse = {
  ended_at_utc: "2026-09-09T12:00:00Z",
  game_uuid: "0007925c-5a8d-11f0-9740-f690a301000f",
  occurrences: [
    { ply: 2, fen: AFTER_E5_FEN, move_uci: "g1f3" },
    { ply: 0, fen: INITIAL_FEN, move_uci: "e2e4" },
    { ply: 3, fen: AFTER_NF3_FEN, move_uci: null },
    { ply: 1, fen: AFTER_E4_FEN, move_uci: "e7e5" },
  ],
  opponent_chesscom_uuid: "opponent-id",
  opponent_rating: 1800,
  original_pgn: "1. e4 e5 2. Nf3",
  source_url: "https://www.chess.com/game/live/123",
  started_at_utc: "2026-09-09T11:00:00Z",
  termination_reason: "normal",
  time_class: "blitz",
  time_control: "300+0",
  trainer_chesscom_uuid: "trainer-id",
  trainer_color: "black",
  trainer_outcome: "win",
  trainer_rating: 1700,
};

describe("mapGameDetailResponse", () => {
  it("maps the complete ordered line, including the Ply 0 occurrence", () => {
    const model = mapGameDetailResponse(DETAIL);

    expect(model).toEqual({
      gameUuid: DETAIL.game_uuid,
      initialFen: INITIAL_FEN,
      trainerOrientation: "black",
      occurrences: [
        { ply: 0, fen: INITIAL_FEN, outgoingUci: "e2e4", san: "e4" },
        { ply: 1, fen: AFTER_E4_FEN, outgoingUci: "e7e5", san: "e5" },
        { ply: 2, fen: AFTER_E5_FEN, outgoingUci: "g1f3", san: "Nf3" },
        { ply: 3, fen: AFTER_NF3_FEN, outgoingUci: null, san: null },
      ],
    });
  });

  it("derives SAN deterministically from each occurrence FEN and outgoing UCI", () => {
    const first = mapGameDetailResponse(DETAIL);
    const second = mapGameDetailResponse(DETAIL);

    expect(first.occurrences.map((occurrence) => occurrence.san)).toEqual(["e4", "e5", "Nf3", null]);
    expect(second).toEqual(first);
  });

  it("does not carry clean response metadata into the neutral model", () => {
    const model = mapGameDetailResponse(DETAIL);

    expect(Object.keys(model).sort()).toEqual([
      "gameUuid",
      "initialFen",
      "occurrences",
      "trainerOrientation",
    ]);
    expect(model).not.toHaveProperty("originalPgn");
    expect(model).not.toHaveProperty("sourceUrl");
    expect(model).not.toHaveProperty("opponentRating");
    expect(model).not.toHaveProperty("trainerRating");
    expect(model).not.toHaveProperty("initial_ply");
    expect(model).not.toHaveProperty("subject_color");
    expect(model).not.toHaveProperty("positions");
    expect(Object.keys(model.occurrences[0]).sort()).toEqual(["fen", "outgoingUci", "ply", "san"]);
  });
});
