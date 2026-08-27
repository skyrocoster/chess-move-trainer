import { validateFen } from "chess.js";

import { safeSourceUrl } from "./stage1SourceSafety";
import type { ChessSide, Ply } from "./chessPrimitives";
import type { Game, GamePosition, GameFailureKind } from "./gameModel";

const API_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5666";
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

type JsonRecord = Record<string, unknown>;

export type GameLookupFailure = GameFailureKind;

export type GameLookupResult = { status: "success"; game: Game } | { status: GameLookupFailure };

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
