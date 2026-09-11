import { Chess, type Square } from "chess.js";

import { getGame } from "../../api/client";
import type { GameLoaderStatus } from "../game/GameLoader";
import type { PromotionPiece } from "../board-adapter/PromotionPicker";
import type {
  PositionPickerSessionBoundary,
  SessionMove,
} from "./positionPickerSessionBoundary";

export type GameDetailClient = (options: {
  path: { game_uuid: string };
  signal?: AbortSignal;
}) => ReturnType<typeof getGame>;

export type RepertoireBuilderWorkspaceProps = {
  gameClient?: GameDetailClient;
  analysisClient?: AnalysisClient;
  analysisPollIntervalMs?: number;
  preferredMoveClient?: PreferredMoveClient;
  positionContextClient?: PositionContextClient;
  moveResponseDistributionClient?: MoveResponseDistributionClient;
};

export type PositionPickerMove = {
  sourceSquare: Square;
  targetSquare: Square;
  promotion?: PromotionPiece;
};

export function moveToSessionMove(
  session: PositionPickerSessionBoundary,
  move: PositionPickerMove,
): SessionMove | null {
  const chess = new Chess(session.currentPosition.fen);
  try {
    const played = chess.move({
      from: move.sourceSquare,
      to: move.targetSquare,
      ...(move.promotion ? { promotion: move.promotion } : {}),
    });
    return {
      outgoingUCI: `${move.sourceSquare}${move.targetSquare}${move.promotion ?? ""}`,
      resultingFEN: chess.fen({ forceEnpassantSquare: true }),
      san: played.san,
    };
  } catch {
    return null;
  }
}

export function failureCode(value: unknown): string | null {
  return typeof value === "object" &&
    value !== null &&
    "code" in value &&
    typeof value.code === "string"
    ? value.code
    : null;
}

export function loadFailure(
  result: Awaited<ReturnType<GameDetailClient>>,
): Exclude<GameLoaderStatus, "idle" | "loading"> {
  const code = failureCode(result.error);
  const status = result.response?.status;
  if (code === "game_not_found" || status === 404) {
    return "game_not_found";
  }
  if (code === "games_unavailable" || status === 503) {
    return "corpus_unavailable";
  }
  if (status === 422) {
    return "game_unavailable";
  }
  return code === "unexpected_failure" || status === 500
    ? "unexpected_failure"
    : "unexpected_failure";
}
