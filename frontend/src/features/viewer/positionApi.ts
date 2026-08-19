import type { LookupResult } from "./positionLookup";

const API_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5666";
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

type JsonRecord = Record<string, unknown>;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null;
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

export async function fetchPosition(
  gameUuid: string,
  ply: number,
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
