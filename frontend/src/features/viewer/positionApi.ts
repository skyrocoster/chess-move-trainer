import { validateFen } from "chess.js";

import { safeSourceUrl } from "./stage1SourceSafety";
import type { ChessSide, Fen, Ply } from "./chessPrimitives";
import type { Game, GamePosition, GameFailureKind } from "./gameModel";

const API_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5666";
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

type JsonRecord = Record<string, unknown>;

export type GameLookupFailure = GameFailureKind;

export type GameLookupResult = { status: "success"; game: Game } | { status: GameLookupFailure };

export type SubjectColor = ChessSide;

export type PositionLookupSuccess = {
  status: "success";
  game_uuid: string;
  ply: Ply;
  fen: Fen;
  subject_color: SubjectColor;
};

export type PositionLookupFailure =
  | { status: "position_not_found" }
  | { status: "corpus_unavailable" }
  | { status: "stored_position_invalid" }
  | { status: "unexpected_failure" };

export type LookupResult = PositionLookupSuccess | PositionLookupFailure;

export type GameLookup = (
  gameUuid: string,
  initialPly?: Ply,
  signal?: AbortSignal,
) => Promise<GameLookupResult>;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null;
}

function hasExactKeys(value: JsonRecord, keys: string[]): boolean {
  return Object.keys(value).sort().join(",") === [...keys].sort().join(",");
}

function isUuid(value: unknown): value is string {
  return typeof value === "string" && UUID_PATTERN.test(value);
}

function isNonnegativeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
}

function isPosition(value: unknown, expectedPly: Ply): value is GamePosition {
  if (!isRecord(value) || !hasExactKeys(value, ["ply", "fen", "san"])) {
    return false;
  }
  if (!isNonnegativeInteger(value.ply) || value.ply !== expectedPly) {
    return false;
  }
  if (typeof value.fen !== "string" || value.fen.trim().split(/\s+/).length !== 6) {
    return false;
  }
  if (!validateFen(value.fen).ok) {
    return false;
  }
  if (expectedPly === 0) {
    return value.san === null;
  }
  return typeof value.san === "string" && value.san.length > 0;
}

function isGameBody(
  body: unknown,
  requestedUuid: string,
  requestedPly: Ply,
): body is {
  game_uuid: string;
  initial_ply: number;
  subject_color: ChessSide;
  source_url: string | null;
  positions: GamePosition[];
} {
  if (
    !isRecord(body) ||
    !hasExactKeys(body, ["game_uuid", "initial_ply", "subject_color", "source_url", "positions"])
  ) {
    return false;
  }
  if (
    !isUuid(body.game_uuid) ||
    body.game_uuid.toLowerCase() !== requestedUuid.toLowerCase() ||
    !isNonnegativeInteger(body.initial_ply) ||
    body.initial_ply !== requestedPly ||
    (body.subject_color !== "white" && body.subject_color !== "black") ||
    !Array.isArray(body.positions) ||
    body.positions.length === 0
  ) {
    return false;
  }
  const positions = body.positions;
  if (!positions.every((position, index) => isPosition(position, index))) {
    return false;
  }
  if (!positions.some((position) => position.ply === body.initial_ply)) {
    return false;
  }
  if (body.source_url !== null) {
    if (typeof body.source_url !== "string" || safeSourceUrl(body.source_url) !== body.source_url) {
      return false;
    }
  }
  return true;
}

function isSuccessBody(body: unknown): body is {
  game_uuid: string;
  ply: number;
  fen: string;
  subject_color: "white" | "black";
} {
  if (!isRecord(body)) {
    return false;
  }

  const keys = Object.keys(body).sort();
  return (
    keys.join(",") === "fen,game_uuid,ply,subject_color" &&
    typeof body.game_uuid === "string" &&
    UUID_PATTERN.test(body.game_uuid) &&
    typeof body.ply === "number" &&
    Number.isInteger(body.ply) &&
    body.ply >= 0 &&
    typeof body.fen === "string" &&
    (body.subject_color === "white" || body.subject_color === "black")
  );
}

function failureFromResponse(status: number, body: unknown): LookupResult {
  const code = isRecord(body) && typeof body.code === "string" ? body.code : null;
  if (status === 404 && code === "position_not_found") {
    return { status: "position_not_found" };
  }
  if (status === 503 && code === "corpus_unavailable") {
    return { status: "corpus_unavailable" };
  }
  if (status === 500 && code === "stored_position_invalid") {
    return { status: "stored_position_invalid" };
  }
  return { status: "unexpected_failure" };
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function gameFailureFromResponse(status: number, body: unknown): GameLookupFailure {
  const code = isRecord(body) && typeof body.code === "string" ? body.code : null;
  if (status === 404 && (code === "game_not_found" || code === "position_not_found")) {
    return code;
  }
  if (status === 503 && code === "corpus_unavailable") {
    return code;
  }
  if (status === 500 && (code === "game_unavailable" || code === "unexpected_failure")) {
    return code;
  }
  return "unexpected_failure";
}

export const fetchGame: GameLookup = async (gameUuid, initialPly, signal) => {
  const query = initialPly === undefined ? "" : `?ply=${initialPly}`;
  const response = await fetch(
    `${API_URL}/api/games/${encodeURIComponent(gameUuid)}/positions${query}`,
    { signal },
  );
  const body = await readJson(response);

  if (!response.ok) {
    return { status: gameFailureFromResponse(response.status, body) };
  }
  const requestedPly = initialPly ?? 0;
  if (!isGameBody(body, gameUuid, requestedPly)) {
    return { status: "unexpected_failure" };
  }
  return {
    status: "success",
    game: {
      game_uuid: body.game_uuid,
      initial_ply: body.initial_ply,
      subject_color: body.subject_color,
      source_url: body.source_url,
      positions: body.positions,
    },
  };
};

export async function fetchPosition(
  gameUuid: string,
  ply: Ply,
  signal?: AbortSignal,
): Promise<LookupResult> {
  const response = await fetch(
    `${API_URL}/api/games/${encodeURIComponent(gameUuid)}/positions/${ply}`,
    { signal },
  );
  const body = await readJson(response);

  if (!response.ok) {
    return failureFromResponse(response.status, body);
  }
  if (!isSuccessBody(body)) {
    return { status: "unexpected_failure" };
  }

  return {
    status: "success",
    game_uuid: body.game_uuid,
    ply: body.ply,
    fen: body.fen,
    subject_color: body.subject_color,
  };
}
