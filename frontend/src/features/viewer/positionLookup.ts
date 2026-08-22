/*
 * Legacy single-position lookup contract and deterministic mocks retained for
 * direct MP-07 client regression coverage. The production viewer uses the
 * whole-game GameLookup contract in positionApi.ts.
 */

export type SubjectColor = "white" | "black";

export type PositionLookupSuccess = {
  status: "success";
  game_uuid: string;
  ply: number;
  fen: string;
  subject_color: SubjectColor;
};

export type PositionLookupFailure =
  | { status: "position_not_found" }
  | { status: "corpus_unavailable" }
  | { status: "stored_position_invalid" }
  | { status: "unexpected_failure" };

export type LookupResult = PositionLookupSuccess | PositionLookupFailure;

export type PositionLookup = (gameUuid: string, ply: number) => Promise<LookupResult>;

const SAMPLE_GAME_UUID = "0101b08a-ce8b-11ee-b2fd-e90263e5548c";
const SAMPLE_PLY = 8;
const SAMPLE_FEN = "rn1qk2r/1bp1bpp1/pp1ppn1p/8/4PB2/2NP1NP1/PPPQ1PBP/R3K2R b KQkq e3 0 8";

function successWith(subjectColor: SubjectColor): PositionLookupSuccess {
  return {
    status: "success",
    game_uuid: SAMPLE_GAME_UUID,
    ply: SAMPLE_PLY,
    fen: SAMPLE_FEN,
    subject_color: subjectColor,
  };
}

export const mockSuccessWhite: PositionLookup = async () => successWith("white");
export const mockSuccessBlack: PositionLookup = async () => successWith("black");
export const mockPositionNotFound: PositionLookup = async () => ({
  status: "position_not_found",
});
export const mockCorpusUnavailable: PositionLookup = async () => ({
  status: "corpus_unavailable",
});
export const mockStoredPositionInvalid: PositionLookup = async () => ({
  status: "stored_position_invalid",
});
export const mockUnexpectedFailure: PositionLookup = async () => ({
  status: "unexpected_failure",
});

/** Deterministic canned mocks retained for the MP-07 client contract. */
export const mockLookup = {
  successWhite: mockSuccessWhite,
  successBlack: mockSuccessBlack,
  positionNotFound: mockPositionNotFound,
  corpusUnavailable: mockCorpusUnavailable,
  storedPositionInvalid: mockStoredPositionInvalid,
  unexpectedFailure: mockUnexpectedFailure,
} satisfies Record<string, PositionLookup>;

/**
 * Legacy default stub for callers that still exercise the single-position
 * lookup contract.
 */
export const defaultLookup: PositionLookup = async () => ({
  status: "unexpected_failure",
});
