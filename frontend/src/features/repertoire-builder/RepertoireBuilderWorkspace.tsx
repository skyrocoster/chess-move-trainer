import { Chess, type Square } from "chess.js";
import { useCallback, useMemo, useRef, useState } from "react";

import { getGame } from "../../api/client";
import type { GameDetailResponse } from "../../api/client";
import type { InteractiveBoardMoveIntent } from "../board-adapter/InteractiveBoardAdapter";
import { deriveLastMove, lastMoveFromSquares } from "../board-adapter/lastMove";
import { PositionDescription } from "../board-adapter/PositionDescription";
import { createPositionModel } from "../board-adapter/positionDescriptionModel";
import {
  isPromotionTarget,
  type PromotionCommit,
  type PromotionPiece,
  usePromotionController,
} from "../board-adapter/PromotionPicker";
import { defaultAnalysisClient, type AnalysisClient } from "../analysis/analysisApi";
import { analysisPanelDisplay } from "../analysis/analysisFormatting";
import { useAnalysisState } from "../analysis/analysisState";
import { evaluationDisplay } from "../analysis/evalBarDisplay";
import { GameLoader, type GameLoaderStatus, type GameLoaderValues } from "../game/GameLoader";
import { mapGameDetailResponse } from "../game/gameModel";
import type { PositionContextClient } from "../position-context/positionContextApi";
import type { MoveResponseDistributionClient } from "../move-response-distribution/moveResponseDistributionApi";
import type { PreferredMoveClient } from "./preferredMoveApi";
import { usePreferredMoveWorkflow } from "./preferredMoveWorkflowState";
import { RepertoireBoardLane } from "./RepertoireBoardLane";
import { RepertoireResponsiveStage } from "./RepertoireResponsiveStage";
import {
  boardLabel,
  branchMoves,
  originDescription,
  promotionPiece,
  sessionViewKey,
} from "./repertoireBuilderWorkspaceModel";
import { RepertoireAnalysisTabs } from "./RepertoireAnalysisTabs";
import {
  applySessionMove,
  createFreshSession,
  loadImportedSession,
  navigateSession,
  returnToGame,
  resetSession,
  selectSessionPly,
  sessionHistory,
  type PositionPickerSessionBoundary,
  type SessionMove,
  type SessionNavigation,
} from "./positionPickerSessionBoundary";
import type { ChessSide, Ply } from "../chess/chessPrimitives";
import styles from "./RepertoireBuilderWorkspace.module.css";
import { RepertoireSessionPanel } from "./RepertoireSessionPanel";
import {
  cancelPromotionWithStatus,
  historyNavigationHandlers,
} from "./repertoireBuilderWorkspaceHandlers";
import { useMoveResponseSelection } from "./moveResponseSelection";

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

type PositionPickerMove = {
  sourceSquare: Square;
  targetSquare: Square;
  promotion?: PromotionPiece;
};

function moveToSessionMove(
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

function failureCode(value: unknown): string | null {
  return typeof value === "object" && value !== null && "code" in value && typeof value.code === "string"
    ? value.code
    : null;
}

function loadFailure(
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
  return code === "unexpected_failure" || status === 500 ? "unexpected_failure" : "unexpected_failure";
}

export default function RepertoireBuilderWorkspace({
  gameClient = getGame,
  analysisClient = defaultAnalysisClient,
  analysisPollIntervalMs,
  preferredMoveClient,
  positionContextClient,
  moveResponseDistributionClient,
}: RepertoireBuilderWorkspaceProps) {
  const [gameUuidInput, setGameUuidInput] = useState("");
  const [status, setStatus] = useState<GameLoaderStatus>("idle");
  const [session, setSession] = useState<PositionPickerSessionBoundary>(createFreshSession);
  const [orientation, setOrientation] = useState<ChessSide>("white");
  const [sessionStatus, setSessionStatus] = useState(
    "Select a legal move to start the local line.",
  );
  const requestId = useRef(0);
  const controller = useRef<AbortController | null>(null);

  const currentPosition = session.currentPosition;
  const viewKey = sessionViewKey(session);
  const chess = useMemo(() => new Chess(currentPosition.fen), [currentPosition.fen]);
  const analysisState = useAnalysisState(
    currentPosition.fen,
    analysisClient,
    analysisPollIntervalMs,
  );
  const analysisDisplay = analysisPanelDisplay(analysisState, {
    displayedPly: currentPosition.ply,
  });
  const displayedEvaluationDisplay = evaluationDisplay(analysisState);
  const sideToMoveColor = chess.turn() === "w" ? "white" : "black";
  const workflow = usePreferredMoveWorkflow({
    session,
    sideToMove: sideToMoveColor,
    bottomColor: orientation,
    preferredMoveClient,
    positionContextClient,
    setSession,
    setSessionStatus,
  });
  const { onPlaySavedMove, reset: resetWorkflow } = workflow;

  const applyMove = useCallback(
    (move: PositionPickerMove): boolean => {
      const sessionMove = moveToSessionMove(session, move);
      if (sessionMove === null) {
        setSessionStatus("Move rejected because it is illegal.");
        return false;
      }

      setSession(applySessionMove(session, sessionMove));
      resetWorkflow();
      setSessionStatus(`Move played locally: ${sessionMove.san}.`);
      return true;
    },
    [resetWorkflow, session],
  );

  const handlePromotionCommit = useCallback(
    (commit: PromotionCommit) => {
      const selectedPromotion = promotionPiece(commit.move.promotion);
      applyMove({
        sourceSquare: commit.move.from,
        targetSquare: commit.move.to,
        ...(selectedPromotion ? { promotion: selectedPromotion } : {}),
      });
    },
    [applyMove],
  );

  const handlePromotionReject = useCallback((reason: "illegal" | "stale") => {
    setSessionStatus(
      reason === "stale"
        ? "Promotion rejected because the current position is stale."
        : "Move rejected because it is illegal.",
    );
  }, []);

  const promotionController = usePromotionController({
    chess,
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

  const representedHistory = useMemo(() => sessionHistory(session), [session]);
  const historyInput = useMemo(
    () => ({
      initialPosition: { ply: representedHistory[0]!.ply },
      moves: representedHistory.slice(1).map((position) => ({
        ply: position.ply,
        san: position.san!,
      })),
    }),
    [representedHistory],
  );
  const hasPrevious = session.currentIndex > 0;
  const hasNext = session.currentIndex < representedHistory.length - 1;
  const label = boardLabel(session, orientation);
  const localMoves = branchMoves(session);
  const lastMove = session.selectedTransition
      ? lastMoveFromSquares(
        session.selectedTransition.outgoingUCI.slice(0, 2) as Square,
        session.selectedTransition.outgoingUCI.slice(2, 4) as Square,
      )
    : deriveLastMove(undefined, null);

  function invalidateRequest() {
    requestId.current += 1;
    controller.current?.abort();
    controller.current = null;
  }

  function resetWorkspace() {
    cancelPromotion();
    invalidateRequest();
    resetWorkflow();
    setGameUuidInput("");
    setStatus("idle");
    setSession(resetSession());
    setOrientation("white");
    clearSelectedResponse();
    setSessionStatus("Select a legal move to start the local line.");
  }

  async function handleSubmit(values: GameLoaderValues) {
    cancelPromotion();
    invalidateRequest();
    resetWorkflow();
    clearSelectedResponse();
    const currentRequestId = requestId.current;
    const nextController = new AbortController();
    controller.current = nextController;
    setStatus("loading");

    let result: Awaited<ReturnType<GameDetailClient>>;
    try {
      result = await gameClient({
        path: { game_uuid: values.gameUuid },
        signal: nextController.signal,
      });
    } catch {
      if (nextController.signal.aborted || currentRequestId !== requestId.current) {
        return;
      }
      setStatus("unexpected_failure");
      return;
    }

    if (nextController.signal.aborted || currentRequestId !== requestId.current) {
      return;
    }
    if (controller.current === nextController) {
      controller.current = null;
    }

    if (result.data !== undefined) {
      try {
        const mainLine = mapGameDetailResponse(result.data as GameDetailResponse);
        setSession(loadImportedSession(mainLine));
        setOrientation(mainLine.trainerOrientation);
        setSessionStatus("Select a legal move to continue the imported game.");
        setStatus("idle");
      } catch {
        setStatus("game_unavailable");
      }
      return;
    }

    setStatus(loadFailure(result));
  }

  const {
    clear: clearSelectedResponse,
    select: selectResponse,
    selectedUci: selectedResponseUci,
  } = useMoveResponseSelection(currentPosition.fen, orientation);

  const handleMoveIntent = useCallback(
    (intent: InteractiveBoardMoveIntent): boolean => {
      clearSelectedResponse();
      const piece = chess.get(intent.sourceSquare);
      if (piece?.type === "p" && isPromotionTarget(piece.color, intent.targetSquare)) {
        const opened = requestPromotion(
          intent.sourceSquare,
          intent.targetSquare,
          intent.sourceElement,
          intent.anchorElement,
        );
        if (opened) {
          setSessionStatus("Choose a promotion piece.");
        }
        return false;
      }

      return applyMove({
        sourceSquare: intent.sourceSquare,
        targetSquare: intent.targetSquare,
      });
    },
    [applyMove, chess, clearSelectedResponse, requestPromotion],
  );

  const handleCandidateMove = useCallback(
    (move: string) => {
      const sourceElement =
        document.activeElement instanceof HTMLElement ? document.activeElement : null;
      if (move.length < 4 || move.length > 5) {
        setSessionStatus("Move rejected because it is illegal.");
        return;
      }
      handleMoveIntent({
        sourceSquare: move.slice(0, 2) as Square,
        targetSquare: move.slice(2, 4) as Square,
        sourceElement,
        anchorElement: sourceElement,
      });
    },
    [handleMoveIntent],
  );
  const handleResponseMove = useCallback(
    (uci: string) => {
      handleCandidateMove(uci);
      selectResponse(uci);
    },
    [handleCandidateMove, selectResponse],
  );

  const handlePromotionCancel = () => cancelPromotionWithStatus(cancelPromotion, setSessionStatus);
  const handlePlaySavedMove = useCallback(() => {
    clearSelectedResponse();
    onPlaySavedMove();
  }, [clearSelectedResponse, onPlaySavedMove]);

  const handleHistorySelection = useCallback(
    (
      selection: Ply | SessionNavigation,
      statusMessage = "Moved to the selected history position.",
    ) => {
      cancelPromotion();
      resetWorkflow();
      setSession((current) => {
        const next =
          typeof selection === "number"
            ? selectSessionPly(current, selection)
            : navigateSession(current, selection);
        return next ?? current;
      });
      clearSelectedResponse();
      setSessionStatus(statusMessage);
    },
    [cancelPromotion, clearSelectedResponse, resetWorkflow],
  );

  const historyControls = historyNavigationHandlers(handleHistorySelection);

  const handleReturnToGame = useCallback(() => {
    cancelPromotion();
    resetWorkflow();
    clearSelectedResponse();
    setSession((current) => returnToGame(current));
    setSessionStatus("Returned to the imported game.");
  }, [cancelPromotion, clearSelectedResponse, resetWorkflow]);

  const handleFlip = useCallback(() => {
    cancelPromotion();
    resetWorkflow();
    clearSelectedResponse();
    setOrientation((current) => (current === "white" ? "black" : "white"));
    setSessionStatus(
      `Flipped to ${orientation === "white" ? "Black" : "White"} at the bottom.`,
    );
  }, [cancelPromotion, clearSelectedResponse, orientation, resetWorkflow]);

  const branchOrigin = session.branch
    ? sessionHistory({ ...session, branch: null }).at(session.branch.branchPointIndex)!
    : representedHistory[0]!;

  return (
    <div className={styles.repertoire}>
      <div className={styles.workspace}>
        <h1 className={styles.heading}>Repertoire Builder</h1>
        <div className={styles.loader}>
          <GameLoader
            status={status}
            gameUuid={gameUuidInput}
            onGameUuidChange={setGameUuidInput}
            onSubmit={handleSubmit}
            onReset={resetWorkspace}
          />
        </div>
        <p className={styles.origin} data-testid="session-origin">
          {originDescription(session)} Current Ply {currentPosition.ply}.
        </p>
        <RepertoireResponsiveStage
          board={
            <RepertoireBoardLane
              orientation={orientation}
              evaluation={displayedEvaluationDisplay}
              viewKey={viewKey}
              board={{
                branchSnapshot: {
                  viewKey,
                  resetToken: 0,
                  originFen: branchOrigin.fen,
                  currentFen: currentPosition.fen,
                  originPly: branchOrigin.ply,
                  moves: localMoves,
                  active: session.branch !== null && localMoves.length > 0,
                },
                label,
                notice: sessionStatus,
                terminal: null,
                lastMove,
                promotionPending,
                promotionColor: chess.turn(),
                promotionSourceElement,
                promotionAnchorElement,
                showBranchPanel: session.branch !== null,
                onMoveIntent: handleMoveIntent,
                onPromotionSelect: selectPromotion,
                onPromotionCancel: handlePromotionCancel,
                onUndo: () => undefined,
                onReset: handleReturnToGame,
              }}
              controls={{
                hasGame: true,
                canGoPrevious: hasPrevious,
                canGoNext: hasNext,
                onPrevious: historyControls.previous,
                onNext: historyControls.next,
                onFlip: handleFlip,
              }}
              history={{
                initialPosition: historyInput.initialPosition,
                moves: historyInput.moves,
                activePly: currentPosition.ply,
                onActivePlyChange: handleHistorySelection,
              }}
            />
          }
          session={
            <section
              className={styles.sessionLane}
              data-lane="session"
              data-testid="repertoire-session-lane"
              aria-label="Session lane"
            >
              <RepertoireSessionPanel
                sessionStatus={sessionStatus}
                model={workflow.positionModel}
                positionContext={workflow.positionContext}
                date={workflow.date}
                mutation={workflow.mutation}
                preferredLoading={workflow.preferredLoading}
                preferredError={workflow.preferredError}
                contextLoading={workflow.contextLoading}
                contextError={workflow.contextError}
                workflowError={workflow.workflowError}
                dateEdit={workflow.dateEdit}
                onDateChange={workflow.onDateChange}
                onSave={workflow.onSave}
                onPlaySavedMove={handlePlaySavedMove}
                onRemove={workflow.onRemove}
                onRetry={workflow.onRetry}
              />
              <div className={styles.positionDescription} data-testid="position-description-row">
                <PositionDescription model={createPositionModel(currentPosition.fen, orientation)} />
              </div>
            </section>
          }
          engine={
            <section
              className={styles.engineLane}
              data-lane="engine"
              data-testid="repertoire-engine-lane"
              aria-label="Engine lane"
            >
              <RepertoireAnalysisTabs
                analysis={{
                  display: analysisDisplay,
                  onAnalyze: analysisState.requestAnalysis,
                  onRetryObservation: analysisState.retryObservation,
                  onCandidateMove: handleCandidateMove,
                }}
                moveResponseDistribution={{
                  fen: currentPosition.fen,
                  color: orientation,
                  selectedUci: selectedResponseUci,
                  client: moveResponseDistributionClient,
                  onMoveSelect: handleResponseMove,
                }}
              />
            </section>
          }
        />
      </div>
    </div>
  );
}
