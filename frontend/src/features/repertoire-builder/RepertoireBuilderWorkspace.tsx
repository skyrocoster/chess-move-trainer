import { Chess, type Square } from "chess.js";
import { useCallback, useMemo, useRef, useState } from "react";

import { AnalysisPanel } from "../analysis/AnalysisPanel";
import {
  InteractiveBoardAdapter,
  type InteractiveBoardMoveIntent,
} from "../board-adapter/InteractiveBoardAdapter";
import {
  isPromotionTarget,
  type PromotionCommit,
  type PromotionPiece,
  usePromotionController,
} from "../board-adapter/PromotionPicker";
import { Disclosure } from "../design-system/Disclosure";
import { BoardControl } from "../viewer/BoardControl";
import { defaultAnalysisClient, type AnalysisClient } from "../viewer/analysisApi";
import { analysisPanelDisplay } from "../viewer/analysisFormatting";
import { useAnalysisState } from "../viewer/analysisState";
import { GameLoader, type GameLoaderStatus, type GameLoaderValues } from "../viewer/GameLoader";
import { fetchGame, type GameLookup } from "../viewer/positionApi";
import type { PositionContextClient } from "../viewer/positionContextApi";
import type { PreferredMoveClient } from "./preferredMoveApi";
import { PreferredMovePanel } from "./PreferredMovePanel";
import { usePreferredMoveWorkflow } from "./preferredMoveWorkflowState";
import {
  createStandardStartSession,
  createStoredGameSession,
  flipPositionPickerSession,
  navigatePositionPickerSession,
  selectPositionPickerMove,
  sessionSanHistory,
  type PositionPickerMove,
  type PositionPickerMoveRecord,
  type PositionPickerSession,
} from "./positionPickerSession";
import styles from "./RepertoireBuilderWorkspace.module.css";

function orientationDescription(orientation: PositionPickerSession["orientation"]): string {
  return orientation === "white" ? "White at the bottom" : "Black at the bottom";
}

function sideDescription(side: "w" | "b"): string {
  return side === "w" ? "White" : "Black";
}

function boardLabel(session: PositionPickerSession): string {
  const orientation = orientationDescription(session.orientation);
  if (session.origin.kind === "standard") {
    return `Chess board: standard starting position, ${orientation}`;
  }
  return `Chess board: game ${session.origin.gameUuid}, ply ${session.currentPly}, ${orientation}`;
}

function originDescription(session: PositionPickerSession): string {
  if (session.origin.kind === "standard") {
    return "Standard starting position; local session begins at Ply 0.";
  }
  return `Game ${session.origin.gameUuid}; complete prefix through Ply ${session.origin.selectedPly}.`;
}

function sessionViewKey(session: PositionPickerSession): string {
  return session.origin.kind === "standard"
    ? "repertoire:standard"
    : `repertoire:${session.origin.gameUuid}:${session.origin.selectedPly}`;
}

function branchMove(move: PositionPickerMoveRecord) {
  return {
    color: move.color === "white" ? ("w" as const) : ("b" as const),
    from: move.sourceSquare,
    to: move.targetSquare,
    san: move.san,
    ...(move.promotion ? { promotion: move.promotion } : {}),
  };
}

function promotionPiece(value: string | undefined): PromotionPiece | undefined {
  return value === "q" || value === "r" || value === "b" || value === "n" ? value : undefined;
}

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
  const viewKey = sessionViewKey(session);
  const chess = useMemo(() => {
    void chessVersion;
    return new Chess(currentPosition.fen);
  }, [chessVersion, currentPosition.fen]);
  const analysisState = useAnalysisState(
    currentPosition.fen,
    analysisClient,
    analysisPollIntervalMs,
  );
  const analysisDisplay = analysisPanelDisplay(analysisState, {
    displayedPly: session.currentPly,
  });
  const sideToMoveColor = chess.turn() === "w" ? "white" : "black";
  const workflow = usePreferredMoveWorkflow({
    session,
    sideToMove: sideToMoveColor,
    preferredMoveClient,
    positionContextClient,
    setSession,
    setSessionStatus,
  });
  const { onStagedMove, reset: resetWorkflow } = workflow;

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
      if (result.disposition === "staged") {
        onStagedMove(result.move);
      }
      setChessVersion((version) => version + 1);
      setSessionStatus(
        result.disposition === "staged"
          ? `My move staged: ${result.move.san}.`
          : `Opponent move played locally: ${result.move.san}.`,
      );
    },
    [onStagedMove, session],
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
  const hasLocalPrevious = session.localCursor > 0;
  const hasLocalNext = session.localCursor < session.localContinuation.length;
  const label = boardLabel(session);
  const orientation = orientationDescription(session.orientation);
  const sideToMove = sideDescription(chess.turn());
  const sanHistory = sessionSanHistory(session);
  const localMoves = session.localMoves.slice(0, session.localCursor).map(branchMove);

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
      if (result.disposition === "staged") {
        onStagedMove(result.move);
      }
      if (result.disposition === "staged") {
        setSessionStatus(`My move staged: ${result.move.san}.`);
        return false;
      }
      setSessionStatus(`Opponent move played locally: ${result.move.san}.`);
      return true;
    },
    [onStagedMove, session],
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

  const handlePrevious = useCallback(() => {
    cancelPromotion();
    resetWorkflow();
    setSession((current) => navigatePositionPickerSession(current, "previous"));
    setSessionStatus("Moved to the previous local position.");
  }, [cancelPromotion, resetWorkflow]);

  const handleNext = useCallback(() => {
    cancelPromotion();
    resetWorkflow();
    setSession((current) => navigatePositionPickerSession(current, "next"));
    setSessionStatus("Moved to the next local position.");
  }, [cancelPromotion, resetWorkflow]);

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
        <div className={styles.board}>
          <InteractiveBoardAdapter
            key={viewKey}
            branchSnapshot={{
              viewKey,
              resetToken: 0,
              originFen: session.prefix.at(-1)!.fen,
              currentFen: currentPosition.fen,
              originPly: session.origin.selectedPly,
              moves: localMoves,
              active: localMoves.length > 0,
            }}
            orientation={session.orientation}
            label={label}
            notice={sessionStatus}
            terminal={null}
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
          <Disclosure summary="Position description" defaultOpen>
            <p className={styles.positionSummary} data-testid="position-summary" role="status">
              Orientation: {orientation}. Side to move: {sideToMove}.
            </p>
            <p className={styles.fen} data-testid="current-fen">
              Current FEN: {currentPosition.fen}
            </p>
          </Disclosure>
        </div>
        <div className={styles.controls}>
          <BoardControl
            hasGame
            canGoPrevious={hasLocalPrevious}
            canGoNext={hasLocalNext}
            onPrevious={handlePrevious}
            onNext={handleNext}
            onFlip={handleFlip}
          />
        </div>
        <div className={styles.session}>
          <p className={styles.historyLabel}>Local SAN history</p>
          <p
            className={styles.history}
            data-testid="session-san-history"
            aria-label="Local SAN history"
          >
            {sanHistory || "No local moves yet"}
          </p>
          {session.stagedMove ? (
            <p className={styles.staged} data-testid="staged-move" aria-live="polite">
              My move staged: {session.stagedMove.san}.
            </p>
          ) : null}
          <p className={styles.sessionStatus} data-testid="session-status" aria-live="polite">
            {sessionStatus}
          </p>
          <PreferredMovePanel
            model={workflow.positionModel}
            sideToMove={sideToMoveColor}
            stagedMove={workflow.stagedMove}
            draftMode={workflow.draftMode}
            date={workflow.date}
            mutation={workflow.mutation}
            preferredLoading={workflow.preferredLoading}
            preferredError={workflow.preferredError}
            contextLoading={workflow.contextLoading}
            contextError={workflow.contextError}
            workflowError={workflow.workflowError}
            onDateChange={workflow.onDateChange}
            onAdd={workflow.onAdd}
            onEdit={workflow.onEdit}
            onSave={workflow.onSave}
            onCancelEdit={workflow.onCancelEdit}
            onPlaySavedMove={workflow.onPlaySavedMove}
            onRemove={workflow.onRemove}
          />
        </div>
        <div className={styles.analysis}>
          <AnalysisPanel
            display={analysisDisplay}
            onAnalyze={() => analysisState.handleAction("analyze")}
            onUpdate={() => analysisState.handleAction("update")}
            onRetry={() => analysisState.handleAction("retry")}
            onRetryObservation={analysisState.retryObservation}
            onCandidateMove={handleCandidateMove}
          />
        </div>
      </div>
    </div>
  );
}
