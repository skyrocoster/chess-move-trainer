import { Chess } from "chess.js";
import { useCallback, useMemo, useRef, useState } from "react";

import { BoardAdapter, STARTING_FEN, type BoardOrientation } from "../board-adapter/BoardAdapter";
import {
  InteractiveBoardAdapter,
  type InteractiveBoardMoveIntent,
} from "../board-adapter/InteractiveBoardAdapter";
import { BoardControl } from "./BoardControl";
import { AnalysisPanel } from "../analysis/AnalysisPanel";
import { BoardEvalStage } from "./BoardEvalStage";
import { GameContext } from "./GameContext";
import { GameLoader, type GameLoaderStatus, type GameLoaderValues } from "./GameLoader";
import { defaultAnalysisClient, type AnalysisClient } from "./analysisApi";
import { useAnalysisState } from "./analysisState";
import { analysisPanelDisplay } from "./analysisFormatting";
import { evaluationDisplay } from "./evalBarDisplay";
import {
  isPromotionTarget,
  type PromotionColor,
  usePromotionController,
} from "../board-adapter/PromotionPicker";
import type { BranchMove, BranchSnapshot } from "../board-adapter/branchModel";
import type { Game } from "./gameModel";
import { fetchGame, type GameLookup } from "./positionApi";
import styles from "./ViewerWorkspace.module.css";

const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";

const START_BOARD = {
  fen: STARTING_FEN,
  orientation: "white" as BoardOrientation,
  label: BOARD_LABEL,
};

const DEFAULT_BRANCH_NOTICE = "Make a legal move to start a temporary branch.";

function historyMoves(chess: Chess): BranchMove[] {
  return chess.history({ verbose: true }).map((move) => ({
    color: move.color,
    from: move.from,
    to: move.to,
    san: move.san,
    ...(move.promotion ? { promotion: move.promotion } : {}),
  }));
}

function terminalDescription(chess: Chess) {
  if (chess.isCheckmate()) {
    return "Checkmate";
  }
  if (chess.isStalemate()) {
    return "Stalemate";
  }
  if (chess.isInsufficientMaterial()) {
    return "Draw by insufficient material";
  }
  if (chess.isDrawByFiftyMoves()) {
    return "Draw by fifty-move rule";
  }
  return null;
}

function announcementFor(game: Game, index: number): string {
  const position = game.positions[index];
  const finalPly = game.positions.at(-1)?.ply ?? 0;
  return `Ply ${position.ply} of ${finalPly}: ${position.san ?? "Initial position"}`;
}

export type ViewerWorkspaceProps = {
  lookup?: GameLookup;
  analysisClient?: AnalysisClient;
  analysisPollIntervalMs?: number;
};

export default function ViewerWorkspace({
  lookup = fetchGame,
  analysisClient = defaultAnalysisClient,
  analysisPollIntervalMs,
}: ViewerWorkspaceProps) {
  const [gameUuidInput, setGameUuidInput] = useState("");
  const [plyInput, setPlyInput] = useState("");
  const [status, setStatus] = useState<GameLoaderStatus>("idle");
  const [game, setGame] = useState<Game | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [announcement, setAnnouncement] = useState("");
  const [branchSnapshot, setBranchSnapshot] = useState<BranchSnapshot | null>(null);
  const [branchResetToken, setBranchResetToken] = useState(0);
  const [branchNotice, setBranchNotice] = useState(DEFAULT_BRANCH_NOTICE);
  const [promotionColor, setPromotionColor] = useState<PromotionColor>("w");
  const requestId = useRef(0);
  const controller = useRef<AbortController | null>(null);

  const loading = status === "loading";
  const currentPosition = game?.positions[currentIndex];
  const finalPly = game?.positions.at(-1)?.ply;
  const hasGame = currentPosition !== undefined && finalPly !== undefined;
  const viewKey = game && currentPosition ? `${game.game_uuid}:${currentPosition.ply}` : "empty";
  const branchOriginFen = currentPosition?.fen ?? START_BOARD.fen;
  const branchChess = useMemo(
    () => new Chess(branchOriginFen),
    [branchOriginFen, branchResetToken, viewKey],
  );
  const emptyBranchSnapshot =
    game && currentPosition
      ? {
          viewKey,
          resetToken: branchResetToken,
          originFen: currentPosition.fen,
          currentFen: currentPosition.fen,
          originPly: currentPosition.ply,
          moves: [],
          active: false,
        }
      : null;
  const branchForView =
    branchSnapshot?.viewKey === viewKey && branchSnapshot.resetToken === branchResetToken
      ? branchSnapshot
      : emptyBranchSnapshot;
  const analysisFen = branchForView?.currentFen ?? currentPosition?.fen ?? null;
  const analysisState = useAnalysisState(analysisFen, analysisClient, analysisPollIntervalMs);
  const analysisDisplay = analysisPanelDisplay(analysisState, {
    displayedPly: currentPosition?.ply,
  });
  const evalBarDisplay = evaluationDisplay(analysisState);
  const canGoPrevious = hasGame && !loading && !branchForView?.active && currentPosition?.ply !== 0;
  const canGoNext =
    hasGame && !loading && !branchForView?.active && currentPosition?.ply !== finalPly;

  const createBranchSnapshot = useCallback(
    (active: boolean): BranchSnapshot | null => {
      if (!currentPosition) {
        return null;
      }

      return {
        viewKey,
        resetToken: branchResetToken,
        originFen: currentPosition.fen,
        currentFen: branchChess.fen(),
        originPly: currentPosition.ply,
        moves: historyMoves(branchChess),
        active,
      };
    },
    [branchChess, branchResetToken, currentPosition, viewKey],
  );

  const handlePromotionCommit = useCallback(
    (commit: { move: { san: string } }) => {
      setBranchSnapshot(createBranchSnapshot(true));
      setPromotionColor(branchChess.turn());
      setBranchNotice(`Branch move committed: ${commit.move.san}.`);
    },
    [branchChess, createBranchSnapshot],
  );

  const handlePromotionReject = useCallback(
    (reason: "illegal" | "stale") => {
      const moves = historyMoves(branchChess);
      setBranchSnapshot(createBranchSnapshot(moves.length > 0));
      setPromotionColor(branchChess.turn());
      setBranchNotice(
        reason === "stale"
          ? "Promotion rejected because the displayed branch position is stale."
          : "Promotion rejected because the move is illegal.",
      );
    },
    [branchChess, createBranchSnapshot],
  );

  const promotionController = usePromotionController({
    chess: branchChess,
    onCommit: handlePromotionCommit,
    onReject: handlePromotionReject,
  });
  const {
    pending: promotionPending,
    sourceElement: promotionSourceElement,
    anchorElement: promotionAnchorElement,
    requestPromotion,
    selectPromotion,
    cancelPromotion,
  } = promotionController;

  const handleMoveIntent = useCallback(
    (intent: InteractiveBoardMoveIntent) => {
      const piece = branchChess.get(intent.sourceSquare);
      if (piece?.type === "p" && isPromotionTarget(piece.color, intent.targetSquare)) {
        const opened = requestPromotion(
          intent.sourceSquare,
          intent.targetSquare,
          intent.sourceElement,
          intent.anchorElement,
        );
        if (opened) {
          setBranchSnapshot(createBranchSnapshot(true));
          setPromotionColor(piece.color);
          setBranchNotice("Choose a promotion piece for the temporary branch.");
        }
        return false;
      }

      try {
        const move = branchChess.move({
          from: intent.sourceSquare,
          to: intent.targetSquare,
        });
        setBranchSnapshot(createBranchSnapshot(true));
        setBranchNotice(`Branch move committed: ${move.san}.`);
        return true;
      } catch {
        setBranchNotice("Move rejected because it is illegal.");
        return false;
      }
    },
    [branchChess, createBranchSnapshot, requestPromotion],
  );

  const handlePromotionCancel = useCallback(() => {
    cancelPromotion();
    const moves = historyMoves(branchChess);
    setBranchSnapshot(createBranchSnapshot(moves.length > 0));
    setPromotionColor(branchChess.turn());
    setBranchNotice("Promotion cancelled; the captured position is unchanged.");
  }, [branchChess, cancelPromotion, createBranchSnapshot]);

  const handleBranchUndo = useCallback(() => {
    cancelPromotion();
    if (!branchChess.undo()) {
      return;
    }
    const moves = historyMoves(branchChess);
    setBranchSnapshot(createBranchSnapshot(moves.length > 0));
    setPromotionColor(branchChess.turn());
    setBranchNotice("Undid the latest temporary branch move.");
  }, [branchChess, cancelPromotion, createBranchSnapshot]);

  const handleBranchReset = useCallback(() => {
    cancelPromotion();
    branchChess.load(branchOriginFen);
    setBranchSnapshot(createBranchSnapshot(false));
    setPromotionColor(branchChess.turn());
    setBranchNotice("Temporary branch reset to its captured-game ply.");
  }, [branchChess, branchOriginFen, cancelPromotion, createBranchSnapshot]);

  function discardBranch() {
    cancelPromotion();
    setBranchSnapshot(null);
    setBranchResetToken((token) => token + 1);
    setPromotionColor(branchChess.turn());
    setBranchNotice(DEFAULT_BRANCH_NOTICE);
  }

  function invalidateRequest() {
    requestId.current += 1;
    controller.current?.abort();
    controller.current = null;
  }

  function resetViewer() {
    discardBranch();
    invalidateRequest();
    setGameUuidInput("");
    setPlyInput("");
    setStatus("idle");
    setGame(null);
    setCurrentIndex(0);
    setAnnouncement("");
  }

  async function handleSubmit(values: GameLoaderValues) {
    discardBranch();
    invalidateRequest();
    const currentRequestId = requestId.current;
    const nextController = new AbortController();
    controller.current = nextController;
    setStatus("loading");

    const initialPly = values.ply === "" ? undefined : Number(values.ply);
    let result: Awaited<ReturnType<GameLookup>>;
    try {
      result = await lookup(values.gameUuid, initialPly, nextController.signal);
    } catch {
      if (nextController.signal.aborted || currentRequestId !== requestId.current) {
        return;
      }
      result = { status: "unexpected_failure" };
    }

    if (nextController.signal.aborted || currentRequestId !== requestId.current) {
      return;
    }
    if (controller.current === nextController) {
      controller.current = null;
    }

    if (result.status === "success") {
      const nextGame = result.game;
      const nextIndex = nextGame.positions.findIndex(
        (position) => position.ply === nextGame.initial_ply,
      );
      if (nextIndex < 0) {
        setStatus("unexpected_failure");
        return;
      }
      setGame(nextGame);
      setCurrentIndex(nextIndex);
      setStatus("idle");
      setAnnouncement(announcementFor(nextGame, nextIndex));
      return;
    }

    setStatus(result.status);
  }

  function handlePrevious() {
    if (branchForView?.active) {
      discardBranch();
      return;
    }
    if (!game || currentIndex === 0) {
      return;
    }
    const nextIndex = currentIndex - 1;
    setBranchNotice(DEFAULT_BRANCH_NOTICE);
    setCurrentIndex(nextIndex);
    setAnnouncement(announcementFor(game, nextIndex));
  }

  function handleNext() {
    if (branchForView?.active) {
      discardBranch();
      return;
    }
    if (!game || currentIndex >= game.positions.length - 1) {
      return;
    }
    const nextIndex = currentIndex + 1;
    setBranchNotice(DEFAULT_BRANCH_NOTICE);
    setCurrentIndex(nextIndex);
    setAnnouncement(announcementFor(game, nextIndex));
  }

  const boardFen = analysisFen ?? START_BOARD.fen;
  const boardOrientation = game?.subject_color ?? START_BOARD.orientation;
  const branchTerminal = terminalDescription(branchChess);
  const boardLabel =
    branchForView && currentPosition
      ? `Chess board: temporary branch from game ${game.game_uuid}, captured ply ${currentPosition.ply}, ${
          boardOrientation === "white" ? "White" : "Black"
        } at the bottom`
      : currentPosition
        ? `Chess board: game ${game.game_uuid}, ply ${currentPosition.ply}, ${
            boardOrientation === "white" ? "White" : "Black"
          } at the bottom`
        : START_BOARD.label;

  return (
    <div className={styles.viewer}>
      <div className={styles.workspace}>
        <h1 className={styles.heading}>Position viewer</h1>

        <div className={styles.loader}>
          <GameLoader
            status={status}
            gameUuid={gameUuidInput}
            ply={plyInput}
            onGameUuidChange={setGameUuidInput}
            onPlyChange={setPlyInput}
            onSubmit={handleSubmit}
            onReset={resetViewer}
          />
        </div>

        <BoardEvalStage orientation={boardOrientation} display={evalBarDisplay}>
          {game && currentPosition ? (
            <InteractiveBoardAdapter
              key={`${viewKey}:${branchResetToken}`}
              branchSnapshot={branchForView!}
              orientation={boardOrientation}
              label={boardLabel}
              notice={branchNotice}
              terminal={branchTerminal}
              promotionPending={promotionPending}
              promotionColor={promotionColor}
              promotionSourceElement={promotionSourceElement}
              promotionAnchorElement={promotionAnchorElement}
              onMoveIntent={handleMoveIntent}
              onPromotionSelect={selectPromotion}
              onPromotionCancel={handlePromotionCancel}
              onUndo={handleBranchUndo}
              onReset={handleBranchReset}
            />
          ) : (
            <BoardAdapter
              key={`${boardFen}|${boardOrientation}`}
              fen={boardFen}
              orientation={boardOrientation}
              label={boardLabel}
            />
          )}
        </BoardEvalStage>

        <div className={styles.controls}>
          <BoardControl
            hasGame={hasGame}
            canGoPrevious={canGoPrevious}
            canGoNext={canGoNext}
            onPrevious={handlePrevious}
            onNext={handleNext}
          />
        </div>

        <div className={styles.context}>
          <GameContext game={game} position={currentPosition}>
            <AnalysisPanel
              display={analysisDisplay}
              onAnalyze={() => analysisState.handleAction("analyze")}
              onUpdate={() => analysisState.handleAction("update")}
              onRetry={() => analysisState.handleAction("retry")}
              onRetryObservation={analysisState.retryObservation}
            />
          </GameContext>
        </div>

        <p className={styles.announcement} role="status" aria-live="polite" aria-atomic="true">
          {announcement}
        </p>
      </div>
    </div>
  );
}
