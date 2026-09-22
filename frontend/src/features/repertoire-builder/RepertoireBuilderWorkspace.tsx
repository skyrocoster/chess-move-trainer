import { Chess, type Square } from "chess.js";
import { useCallback, useEffect, useMemo, useState } from "react";

import { getGame } from "../../api/client";
import type { InteractiveBoardMoveIntent } from "../board-adapter/InteractiveBoardAdapter";
import { deriveLastMove, lastMoveFromSquares, type LastMove } from "../board-adapter/lastMove";
import { PositionDescription } from "../board-adapter/PositionDescription";
import { createPositionModel } from "../board-adapter/positionDescriptionModel";
import {
  isPromotionTarget,
  type PromotionCommit,
  usePromotionController,
} from "../board-adapter/PromotionPicker";
import { defaultAnalysisClient } from "../analysis/analysisApi";
import { analysisPanelDisplay } from "../analysis/analysisFormatting";
import { useAnalysisState } from "../analysis/analysisState";
import { evaluationDisplay } from "../analysis/evalBarDisplay";
import { GameLoader, type GameLoaderStatus, type GameLoaderValues } from "../game/GameLoader";
import { mapGameDetailResponse } from "../game/gameModel";
import { usePreferredMoveWorkflow } from "./preferredMoveWorkflowState";
import { GameDetailQueryError, useGameDetailQuery } from "./gameDetailQuery";
import { RepertoireBoardLane } from "./RepertoireBoardLane";
import { RepertoireResponsiveStage } from "./RepertoireResponsiveStage";
import {
  boardLabel,
  branchMoves,
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

import type {
  PositionPickerMove,
  RepertoireBuilderWorkspaceProps,
} from "./RepertoireBuilderWorkspaceTypes";
import { loadFailure, moveToSessionMove } from "./RepertoireBuilderWorkspaceTypes";
export type { GameDetailClient } from "./RepertoireBuilderWorkspaceTypes";

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
  const [submittedGameUuid, setSubmittedGameUuid] = useState<string | null>(null);
  const [submissionVersion, setSubmissionVersion] = useState(0);
  const [session, setSession] = useState<PositionPickerSessionBoundary>(createFreshSession);
  const [orientation, setOrientation] = useState<ChessSide>("white");
  const [sessionStatus, setSessionStatus] = useState(
    "Select a legal move to start the local line.",
  );
  const [rejectedMove, setRejectedMove] = useState<LastMove | null>(null);
  const gameDetailQuery = useGameDetailQuery(submittedGameUuid, gameClient);

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
        setRejectedMove(
          lastMoveFromSquares(move.sourceSquare as Square, move.targetSquare as Square),
        );
        setSessionStatus("Move rejected because it is illegal.");
        return false;
      }

      setRejectedMove(null);
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

  function resetWorkspace() {
    cancelPromotion();
    resetWorkflow();
    setGameUuidInput("");
    setSubmittedGameUuid(null);
    setStatus("idle");
    setSession(resetSession());
    setOrientation("white");
    clearSelectedResponse();
    setRejectedMove(null);
    setSessionStatus("Select a legal move to start the local line.");
  }

  function handleSubmit(values: GameLoaderValues) {
    cancelPromotion();
    resetWorkflow();
    clearSelectedResponse();
    setStatus("loading");
    const nextGameUuid = values.gameUuid.trim();
    if (submittedGameUuid === nextGameUuid && gameDetailQuery.isError) {
      void gameDetailQuery.refetch();
    }
    setSubmissionVersion((value) => value + 1);
    setSubmittedGameUuid(nextGameUuid);
  }

  useEffect(() => {
    if (submittedGameUuid === null || gameDetailQuery.isFetching) {
      return;
    }
    if (gameDetailQuery.isError) {
      setStatus(
        gameDetailQuery.error instanceof GameDetailQueryError
          ? loadFailure(gameDetailQuery.error.result)
          : "unexpected_failure",
      );
      return;
    }
    if (!gameDetailQuery.isSuccess) {
      return;
    }

    try {
      const mainLine = mapGameDetailResponse(gameDetailQuery.data);
      setSession(loadImportedSession(mainLine));
      setOrientation(mainLine.trainerOrientation);
      setRejectedMove(null);
      setSessionStatus("Select a legal move to continue the imported game.");
      setStatus("idle");
    } catch {
      setStatus("game_unavailable");
    }
  }, [
    gameDetailQuery.data,
    gameDetailQuery.error,
    gameDetailQuery.isError,
    gameDetailQuery.isFetching,
    gameDetailQuery.isSuccess,
    submittedGameUuid,
    submissionVersion,
  ]);

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
          setRejectedMove(null);
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
        setRejectedMove(null);
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
    setRejectedMove(null);
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
      setRejectedMove(null);
      setSessionStatus(statusMessage);
    },
    [cancelPromotion, clearSelectedResponse, resetWorkflow],
  );

  const historyControls = historyNavigationHandlers(handleHistorySelection);

  const handleReturnToGame = useCallback(() => {
    cancelPromotion();
    resetWorkflow();
    clearSelectedResponse();
    setRejectedMove(null);
    setSession((current) => returnToGame(current));
    setSessionStatus("Returned to the imported game.");
  }, [cancelPromotion, clearSelectedResponse, resetWorkflow]);

  const handleFlip = useCallback(() => {
    cancelPromotion();
    resetWorkflow();
    clearSelectedResponse();
    setRejectedMove(null);
    setOrientation((current) => (current === "white" ? "black" : "white"));
    setSessionStatus(`Flipped to ${orientation === "white" ? "Black" : "White"} at the bottom.`);
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
                rejectedMove,
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
                <PositionDescription
                  model={createPositionModel(currentPosition.fen, orientation)}
                />
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
                   onUpgrade: analysisState.requestFullAnalysis,
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
