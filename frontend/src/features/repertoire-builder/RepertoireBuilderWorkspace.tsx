import { Chess, type Square } from "chess.js";
import { useCallback, useMemo, useRef, useState } from "react";

import { AnalysisPanel } from "../analysis/AnalysisPanel";
import {
  InteractiveBoardAdapter,
  type InteractiveBoardMoveIntent,
} from "../board-adapter/InteractiveBoardAdapter";
import { deriveLastMove, lastMoveFromSquares } from "../board-adapter/lastMove";
import { PositionDescription } from "../board-adapter/PositionDescription";
import { createPositionModel } from "../board-adapter/positionDescriptionModel";
import {
  isPromotionTarget,
  type PromotionCommit,
  usePromotionController,
} from "../board-adapter/PromotionPicker";
import { BoardControl } from "../viewer/BoardControl";
import { BoardEvalStage } from "../viewer/BoardEvalStage";
import { defaultAnalysisClient, type AnalysisClient } from "../viewer/analysisApi";
import { analysisPanelDisplay } from "../viewer/analysisFormatting";
import { useAnalysisState } from "../viewer/analysisState";
import { GameLoader, type GameLoaderStatus, type GameLoaderValues } from "../viewer/GameLoader";
import { fetchGame, type GameLookup } from "../viewer/positionApi";
import type { PositionContextClient } from "../viewer/positionContextApi";
import { evaluationDisplay } from "../viewer/evalBarDisplay";
import type { PreferredMoveClient } from "./preferredMoveApi";
import { usePreferredMoveWorkflow } from "./preferredMoveWorkflowState";
import {
  boardLabel,
  branchMove,
  originDescription,
  promotionPiece,
  sessionViewKey,
} from "./repertoireBuilderWorkspaceModel";
import {
  createStandardStartSession,
  createStoredGameSession,
  flipPositionPickerSession,
  navigatePositionPickerSession,
  positionPickerHistory,
  selectPositionPickerPly,
  selectPositionPickerMove,
  type PositionPickerMove,
  type PositionPickerNavigation,
  type PositionPickerSession,
} from "./positionPickerSession";
import type { Ply } from "../viewer/chessPrimitives";
import styles from "./RepertoireBuilderWorkspace.module.css";
import { RepertoireSessionPanel } from "./RepertoireSessionPanel";

export type RepertoireBuilderWorkspaceProps = {
  lookup?: GameLookup;
  analysisClient?: AnalysisClient;
  analysisPollIntervalMs?: number;
  preferredMoveClient?: PreferredMoveClient;
  positionContextClient?: PositionContextClient;
};

export default function RepertoireBuilderWorkspace({
  lookup = fetchGame,
  analysisClient = defaultAnalysisClient,
  analysisPollIntervalMs,
  preferredMoveClient,
  positionContextClient,
}: RepertoireBuilderWorkspaceProps) {
  const [gameUuidInput, setGameUuidInput] = useState("");
  const [plyInput, setPlyInput] = useState("");
  const [status, setStatus] = useState<GameLoaderStatus>("idle");
  const [session, setSession] = useState<PositionPickerSession>(createStandardStartSession);
  const [sessionStatus, setSessionStatus] = useState(
    "Select a legal move to start the local line.",
  );
  const [chessVersion, setChessVersion] = useState(0);
  const requestId = useRef(0);
  const controller = useRef<AbortController | null>(null);

  const currentPosition = session.currentPosition;
  const displayedPosition = session.stagedMove?.position ?? currentPosition;
  const viewKey = sessionViewKey(session);
  const chess = useMemo(() => {
    void chessVersion;
    return new Chess(currentPosition.fen);
  }, [chessVersion, currentPosition.fen]);
  const positionModel = useMemo(
    () => createPositionModel(displayedPosition.fen, session.orientation),
    [displayedPosition.fen, session.orientation],
  );
  const parentAnalysisState = useAnalysisState(
    currentPosition.fen,
    analysisClient,
    analysisPollIntervalMs,
  );
  const displayedAnalysisState = useAnalysisState(
    displayedPosition.fen,
    analysisClient,
    analysisPollIntervalMs,
  );
  const analysisDisplay = analysisPanelDisplay(parentAnalysisState, {
    displayedPly: session.currentPly,
  });
  const displayedEvaluationDisplay = evaluationDisplay(displayedAnalysisState);
  const sideToMoveColor = chess.turn() === "w" ? "white" : "black";
  const workflow = usePreferredMoveWorkflow({
    session,
    sideToMove: sideToMoveColor,
    preferredMoveClient,
    positionContextClient,
    setSession,
    setSessionStatus,
  });
  const { reset: resetWorkflow } = workflow;

  const handlePromotionCommit = useCallback(
    (commit: PromotionCommit) => {
      const selectedPromotion = promotionPiece(commit.move.promotion);
      const result = selectPositionPickerMove(session, {
        sourceSquare: commit.move.from,
        targetSquare: commit.move.to,
        ...(selectedPromotion ? { promotion: selectedPromotion } : {}),
      });
      if (!result) {
        setSessionStatus("Move rejected because it is illegal.");
        return;
      }
      setSession(result.session);
      if (result.disposition === "advanced") {
        resetWorkflow();
      }
      setChessVersion((version) => version + 1);
      setSessionStatus(
        result.disposition === "staged"
          ? `My move staged: ${result.move.san}.`
          : `Opponent move played locally: ${result.move.san}.`,
      );
    },
    [resetWorkflow, session],
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
  const representedHistory = useMemo(() => positionPickerHistory(session), [session]);
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
  const hasPrevious = session.currentPly > representedHistory[0]!.ply;
  const hasNext = session.currentPly < representedHistory.at(-1)!.ply;
  const label = boardLabel(session);
  const localMoves = session.localMoves.slice(0, session.localCursor).map(branchMove);
  const localLastMove =
    session.localCursor > 0 ? session.localMoves[session.localCursor - 1] : null;
  const currentHistoryIndex = representedHistory.findIndex(
    (position) => position.ply === session.currentPly,
  );
  const previousHistoryPosition =
    currentHistoryIndex > 0 ? representedHistory[currentHistoryIndex - 1] : undefined;
  const lastMove = session.stagedMove
    ? lastMoveFromSquares(session.stagedMove.sourceSquare, session.stagedMove.targetSquare)
    : localLastMove
      ? lastMoveFromSquares(localLastMove.sourceSquare, localLastMove.targetSquare)
      : deriveLastMove(previousHistoryPosition?.fen, session.currentPosition.san);

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
    setPlyInput("");
    setStatus("idle");
    setSession(createStandardStartSession());
    setSessionStatus("Select a legal move to start the local line.");
  }

  async function handleSubmit(values: GameLoaderValues) {
    cancelPromotion();
    invalidateRequest();
    resetWorkflow();
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
      try {
        setSession(createStoredGameSession(result.game));
        setSessionStatus("Select a legal move to continue the local line.");
        setStatus("idle");
      } catch {
        setStatus("game_unavailable");
      }
      return;
    }

    setStatus(result.status);
  }

  const applyMove = useCallback(
    (move: PositionPickerMove): boolean => {
      const result = selectPositionPickerMove(session, move);
      if (!result) {
        setSessionStatus("Move rejected because it is illegal.");
        return false;
      }

      setSession(result.session);
      if (result.disposition === "advanced") {
        resetWorkflow();
      }
      if (result.disposition === "staged") {
        setSessionStatus(`My move staged: ${result.move.san}.`);
        return false;
      }
      setSessionStatus(`Opponent move played locally: ${result.move.san}.`);
      return true;
    },
    [resetWorkflow, session],
  );

  const handleMoveIntent = useCallback(
    (intent: InteractiveBoardMoveIntent): boolean => {
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
    [applyMove, chess, requestPromotion],
  );

  const handleCandidateMove = useCallback(
    (move: string) => {
      const sourceElement =
        document.activeElement instanceof HTMLElement ? document.activeElement : null;
      if (move.length < 4) {
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

  const handlePromotionCancel = useCallback(() => {
    cancelPromotion();
    setSessionStatus("Promotion cancelled; the current position is unchanged.");
  }, [cancelPromotion]);

  const handleHistorySelection = useCallback(
    (
      selection: Ply | PositionPickerNavigation,
      status = "Moved to the selected history position.",
    ) => {
      cancelPromotion();
      resetWorkflow();
      setSession((current) => {
        const next =
          typeof selection === "number"
            ? selectPositionPickerPly(current, selection)
            : navigatePositionPickerSession(current, selection);
        return next ?? current;
      });
      setSessionStatus(status);
    },
    [cancelPromotion, resetWorkflow],
  );

  const handlePrevious = useCallback(() => {
    handleHistorySelection("previous", "Moved to the previous local position.");
  }, [handleHistorySelection]);

  const handleNext = useCallback(() => {
    handleHistorySelection("next", "Moved to the next local position.");
  }, [handleHistorySelection]);

  const handleFlip = useCallback(() => {
    cancelPromotion();
    resetWorkflow();
    setSession((current) => flipPositionPickerSession(current));
    setSessionStatus(
      `Flipped to ${session.orientation === "white" ? "Black" : "White"} at the bottom.`,
    );
  }, [cancelPromotion, resetWorkflow, session.orientation]);

  return (
    <div className={styles.repertoire}>
      <div className={styles.workspace}>
        <h1 className={styles.heading}>Repertoire Builder</h1>
        <div className={styles.loader}>
          <GameLoader
            status={status}
            gameUuid={gameUuidInput}
            ply={plyInput}
            onGameUuidChange={setGameUuidInput}
            onPlyChange={setPlyInput}
            onSubmit={handleSubmit}
            onReset={resetWorkspace}
          />
        </div>
        <p className={styles.origin} data-testid="session-origin">
          {originDescription(session)} Current Ply {session.currentPly}.
        </p>
        <BoardEvalStage orientation={session.orientation} display={displayedEvaluationDisplay}>
          <InteractiveBoardAdapter
            key={viewKey}
            branchSnapshot={{
              viewKey,
              resetToken: 0,
              originFen: session.prefix.at(-1)!.fen,
              currentFen: displayedPosition.fen,
              originPly: session.origin.selectedPly,
              moves: localMoves,
              active: localMoves.length > 0,
            }}
            orientation={session.orientation}
            label={label}
            notice={sessionStatus}
            terminal={null}
            lastMove={lastMove}
            promotionPending={promotionPending}
            promotionColor={chess.turn()}
            promotionSourceElement={promotionSourceElement}
            promotionAnchorElement={promotionAnchorElement}
            showBranchPanel={false}
            onMoveIntent={handleMoveIntent}
            onPromotionSelect={selectPromotion}
            onPromotionCancel={handlePromotionCancel}
            onUndo={() => undefined}
            onReset={() => undefined}
          />
        </BoardEvalStage>
        <div className={styles.controls}>
          <BoardControl
            hasGame
            canGoPrevious={hasPrevious}
            canGoNext={hasNext}
            onPrevious={handlePrevious}
            onNext={handleNext}
            onFlip={handleFlip}
          />
        </div>
        <div className={styles.positionDescription} data-testid="position-description-row">
          <PositionDescription model={positionModel} />
        </div>
        <RepertoireSessionPanel
          initialPosition={historyInput.initialPosition}
          moves={historyInput.moves}
          activePly={session.currentPly}
          onActivePlyChange={handleHistorySelection}
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
          onPlaySavedMove={workflow.onPlaySavedMove}
          onRemove={workflow.onRemove}
          onRetry={workflow.onRetry}
        />
        <div className={styles.analysis}>
          <AnalysisPanel
            display={analysisDisplay}
            onAnalyze={() => parentAnalysisState.handleAction("analyze")}
            onUpdate={() => parentAnalysisState.handleAction("update")}
            onRetry={() => parentAnalysisState.handleAction("retry")}
            onRetryObservation={parentAnalysisState.retryObservation}
            onCandidateMove={handleCandidateMove}
          />
        </div>
      </div>
    </div>
  );
}
