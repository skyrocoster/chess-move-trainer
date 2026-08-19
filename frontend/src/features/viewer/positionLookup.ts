/*
 * Feature-local lookup contract and deterministic mocks for the MP-07 viewer
 * (Stage 1). No real API exists yet: the viewer consumes an injected
 * PositionLookup and the default stub reports an unexpected failure until
 * Stage 3 wires the real backend client. Storybook stories and component
 * tests pass the canned deterministic mocks below.
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

/** Deterministic canned mocks keyed by the MP-07 visual state. */
export const mockLookup = {
  successWhite: mockSuccessWhite,
  successBlack: mockSuccessBlack,
  positionNotFound: mockPositionNotFound,
  corpusUnavailable: mockCorpusUnavailable,
  storedPositionInvalid: mockStoredPositionInvalid,
  unexpectedFailure: mockUnexpectedFailure,
} satisfies Record<string, PositionLookup>;

/**
 * Default stub used by the viewer until Stage 3 wires the real backend
 * client. It deterministically reports an unexpected failure.
 */
export const defaultLookup: PositionLookup = async () => ({
  status: "unexpected_failure",
});
