import type { Square } from "chess.js";
import { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "../design-system/Button";
import { ChessboardSurface, type ChessboardPieceDropHandlerArgs } from "./ChessboardSurface";
import { findBoardSourceElement, findBoardSquareElement } from "./boardElementQueries";
import {
  PromotionPicker,
  type PendingPromotion,
  type PromotionColor,
  type PromotionPiece,
} from "./PromotionPicker";
import styles from "./InteractiveBoardAdapter.module.css";
import type { BoardOrientation } from "./BoardAdapter";
import {
  boardSquareStyles,
  answerInteractionAllowed,
  answerMessage,
  type BoardAnswerPresentation,
} from "./answerPresentation";
import type { BranchMove, BranchSnapshot } from "./branchModel";
import type { LastMove } from "./lastMove";

export type { BranchMove, BranchSnapshot } from "./branchModel";
export type { BoardAnswerPresentation, BoardAnswerStatus } from "./answerPresentation";

export type InteractiveBoardAdapterProps = {
  branchSnapshot: BranchSnapshot;
  orientation?: BoardOrientation;
  label: string;
  notice: string;
  terminal: string | null;
  lastMove: LastMove | null;
  /**
   * The most recent directly rejected (illegal) drag/drop. Rendered with the
   * illegal red highlight while keeping the board interactive, so the user
   * can immediately try another move.
   */
  rejectedMove?: LastMove | null;
  /**
   * Optional caller-owned answer presentation (trainer verdict, revealed move,
   * loading lock). While present, the board renders its highlights, announces
   * its status, and allows interaction only in the "awaiting-input" state.
   */
  answer?: BoardAnswerPresentation | null;
  promotionPending: PendingPromotion | null;
  promotionColor: PromotionColor;
  promotionSourceElement: HTMLElement | null;
  promotionAnchorElement: HTMLElement | null;
  showBranchPanel?: boolean;
  showRejectedMoveNotice?: boolean;
  onMoveIntent: (intent: InteractiveBoardMoveIntent) => boolean;
  onPromotionSelect: (promotion: PromotionPiece) => void;
  onPromotionCancel: () => void;
  onUndo: () => void;
  onReset: () => void;
};

export type InteractiveBoardMoveIntent = {
  sourceSquare: Square;
  targetSquare: Square;
  sourceElement: HTMLElement | null;
  anchorElement: HTMLElement | null;
};

function branchSan(originFen: string, moves: readonly BranchMove[]) {
  const fields = originFen.split(" ");
  let moveNumber = Number(fields[5]) || 1;
  let color = fields[1] === "b" ? "b" : "w";

  return moves
    .map((move) => {
      const prefix = color === "w" ? `${moveNumber}. ` : `${moveNumber}... `;
      const result = `${prefix}${move.san}`;
      if (color === "b") {
        moveNumber += 1;
      }
      color = color === "w" ? "b" : "w";
      return result;
    })
    .join(" ");
}

const COPY_FEEDBACK_DURATION_MS = 2000;

export function InteractiveBoardAdapter({
  branchSnapshot,
  orientation = "white",
  label,
  notice,
  terminal,
  lastMove,
  rejectedMove = null,
  answer = null,
  promotionPending,
  promotionColor,
  promotionSourceElement,
  promotionAnchorElement,
  showBranchPanel = true,
  showRejectedMoveNotice = false,
  onMoveIntent,
  onPromotionSelect,
  onPromotionCancel,
  onUndo,
  onReset,
}: InteractiveBoardAdapterProps) {
  const boardRootRef = useRef<HTMLDivElement | null>(null);
  const copyFeedbackTimerRef = useRef<number | null>(null);
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);
  const interactionAllowed = answerInteractionAllowed(answer);

  useEffect(
    () => () => {
      if (copyFeedbackTimerRef.current !== null) {
        window.clearTimeout(copyFeedbackTimerRef.current);
      }
    },
    [],
  );

  const handlePieceDrop = useCallback(
    ({ sourceSquare, targetSquare }: ChessboardPieceDropHandlerArgs) => {
      if (!targetSquare) {
        return false;
      }
      if (!interactionAllowed) {
        return false;
      }

      const source = sourceSquare as Square;
      const target = targetSquare as Square;
      return onMoveIntent({
        sourceSquare: source,
        targetSquare: target,
        sourceElement: findBoardSourceElement(boardRootRef.current, source),
        anchorElement: findBoardSquareElement(boardRootRef.current, target),
      });
    },
    [interactionAllowed, onMoveIntent],
  );
  const san = branchSan(branchSnapshot.originFen, branchSnapshot.moves);
  const squareStyles = boardSquareStyles(answer, lastMove, rejectedMove);
  const showCopyFeedback = useCallback((message: string) => {
    if (copyFeedbackTimerRef.current !== null) {
      window.clearTimeout(copyFeedbackTimerRef.current);
    }
    setCopyFeedback(message);
    copyFeedbackTimerRef.current = window.setTimeout(() => {
      copyFeedbackTimerRef.current = null;
      setCopyFeedback(null);
    }, COPY_FEEDBACK_DURATION_MS);
  }, []);
  const handleCopyFen = useCallback(
    async (fen: string, field: "branch origin" | "current branch") => {
      try {
        await navigator.clipboard.writeText(fen);
        showCopyFeedback(`Copied ${field} FEN.`);
      } catch {
        showCopyFeedback(`Unable to copy ${field} FEN.`);
      }
    },
    [showCopyFeedback],
  );
  const options = {
    allowDragging: interactionAllowed || undefined,
    allowDrawingArrows: true,
    animationDurationInMs: 0,
    boardOrientation: orientation,
    id: "interactive-analysis-board",
    onPieceDrag: () => undefined,
    onPieceDragCancel: () => undefined,
    onPieceDrop: handlePieceDrop,
    position: branchSnapshot.currentFen,
    squareStyles,
    showAnimations: false,
    showNotation: true,
  } as const;

  return (
    <section className={styles.adapter} data-testid="interactive-board-adapter">
      <div
        ref={boardRootRef}
        className={styles.board}
        data-board-visual
        data-testid="interactive-board"
        data-locked={!interactionAllowed}
        aria-disabled={!interactionAllowed || undefined}
        role="group"
        aria-label={label}
      >
        <ChessboardSurface options={options} accessiblePieceNames />
      </div>
      {answer ? (
        <p
          className={styles.answerStatus}
          data-testid="board-answer-status"
          role="status"
          aria-live="polite"
          data-answer-status={answer.status}
        >
          {answerMessage(answer)}
        </p>
      ) : null}
      {!showBranchPanel && showRejectedMoveNotice && rejectedMove ? (
        <p className={styles.notice} role="status" aria-live="polite">
          {notice}
        </p>
      ) : null}
      {showBranchPanel ? (
        <div className={styles.branchPanel} aria-label="Temporary branch">
          <div className={styles.branchHeading}>
            <strong>Temporary branch</strong>
            <span>From captured ply {branchSnapshot.originPly}</span>
            <span data-testid="branch-current-ply">
              Current ply {branchSnapshot.originPly + branchSnapshot.moves.length}
            </span>
          </div>
          <div className={styles.fenFields} aria-label="Temporary branch FEN">
            <div className={styles.fenField}>
              <span>Branch origin FEN</span>
              <code data-testid="branch-origin-fen">{branchSnapshot.originFen}</code>
              <Button
                size="sm"
                variant="secondary"
                aria-label="Copy branch origin FEN"
                data-testid="copy-branch-origin-fen"
                onClick={() => void handleCopyFen(branchSnapshot.originFen, "branch origin")}
              >
                Copy
              </Button>
            </div>
            <div className={styles.fenField}>
              <span>Current branch FEN</span>
              <code data-testid="branch-current-fen">{branchSnapshot.currentFen}</code>
              <Button
                size="sm"
                variant="secondary"
                aria-label="Copy current branch FEN"
                data-testid="copy-current-branch-fen"
                onClick={() => void handleCopyFen(branchSnapshot.currentFen, "current branch")}
              >
                Copy
              </Button>
            </div>
          </div>
          <p className={styles.san} data-testid="branch-san" aria-label="Temporary branch SAN">
            {san || "No branch moves yet"}
          </p>
          {terminal ? (
            <p className={styles.terminal} data-testid="branch-terminal" role="status">
              Terminal result: {terminal}
            </p>
          ) : null}
          <div className={styles.actions} aria-label="Temporary branch actions">
            <Button
              size="sm"
              variant="secondary"
              onClick={onUndo}
              disabled={branchSnapshot.moves.length === 0}
            >
              Undo
            </Button>
            <Button
              size="sm"
              variant="secondary"
              onClick={onReset}
              disabled={!branchSnapshot.active}
            >
              Reset
            </Button>
          </div>
          <p className={styles.notice} data-testid="branch-status" role="status" aria-live="polite">
            {copyFeedback ?? notice}
          </p>
        </div>
      ) : null}
      <PromotionPicker
        pending={promotionPending}
        color={promotionColor}
        sourceElement={promotionSourceElement}
        anchorElement={promotionAnchorElement}
        onSelect={onPromotionSelect}
        onCancel={onPromotionCancel}
      />
    </section>
  );
}
