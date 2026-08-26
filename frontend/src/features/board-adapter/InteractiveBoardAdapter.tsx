import type { Square } from "chess.js";
import { cloneElement, useCallback, useRef, type ReactElement, type SVGProps } from "react";
import {
  Chessboard,
  defaultPieces,
  type PieceDropHandlerArgs,
  type PieceRenderObject,
} from "react-chessboard";

import { Button } from "../design-system/Button";
import {
  PromotionPicker,
  type PendingPromotion,
  type PromotionColor,
  type PromotionPiece,
} from "./PromotionPicker";
import styles from "./InteractiveBoardAdapter.module.css";
import type { BoardOrientation } from "./BoardAdapter";
import type { BranchMove, BranchSnapshot } from "../viewer/temporaryBranchModel";

export type { BranchMove, BranchSnapshot } from "../viewer/temporaryBranchModel";

export type InteractiveBoardAdapterProps = {
  branchSnapshot: BranchSnapshot;
  orientation?: BoardOrientation;
  label: string;
  notice: string;
  terminal: string | null;
  promotionPending: PendingPromotion | null;
  promotionColor: PromotionColor;
  promotionSourceElement: HTMLElement | null;
  promotionAnchorElement: HTMLElement | null;
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

const PIECE_NAMES: Record<string, string> = {
  wP: "White pawn",
  wR: "White rook",
  wN: "White knight",
  wB: "White bishop",
  wQ: "White queen",
  wK: "White king",
  bP: "Black pawn",
  bR: "Black rook",
  bN: "Black knight",
  bB: "Black bishop",
  bQ: "Black queen",
  bK: "Black king",
};

const accessiblePieces = Object.fromEntries(
  Object.entries(defaultPieces).map(([pieceType, renderPiece]) => [
    pieceType,
    (props?: { fill?: string; square?: string; svgStyle?: React.CSSProperties }) => {
      const piece = renderPiece(props) as ReactElement<SVGProps<SVGSVGElement>>;
      const name = `${PIECE_NAMES[pieceType]}${props?.square ? ` on ${props.square}` : ""}`;
      return cloneElement(piece, { "aria-label": name, role: "img" });
    },
  ]),
) as PieceRenderObject;

function findSourceElement(boardRoot: HTMLElement | null, sourceSquare: Square) {
  const activeElement = document.activeElement;
  const activeSource =
    activeElement instanceof HTMLElement
      ? activeElement.closest<HTMLElement>(`[data-square="${sourceSquare}"]`)
      : null;
  return (
    activeSource?.querySelector<HTMLElement>('[aria-roledescription="draggable"]') ??
    boardRoot?.querySelector<HTMLElement>(
      `[data-square="${sourceSquare}"] [aria-roledescription="draggable"]`,
    ) ??
    boardRoot?.querySelector<HTMLElement>(`[data-square="${sourceSquare}"]`) ??
    null
  );
}

function findSquareElement(boardRoot: HTMLElement | null, square: Square) {
  return boardRoot?.querySelector<HTMLElement>(`[data-square="${square}"]`) ?? null;
}

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

export function InteractiveBoardAdapter({
  branchSnapshot,
  orientation = "white",
  label,
  notice,
  terminal,
  promotionPending,
  promotionColor,
  promotionSourceElement,
  promotionAnchorElement,
  onMoveIntent,
  onPromotionSelect,
  onPromotionCancel,
  onUndo,
  onReset,
}: InteractiveBoardAdapterProps) {
  const boardRootRef = useRef<HTMLDivElement | null>(null);

  const handlePieceDrop = useCallback(
    ({ sourceSquare, targetSquare }: PieceDropHandlerArgs) => {
      if (!targetSquare) {
        return false;
      }

      const source = sourceSquare as Square;
      const target = targetSquare as Square;
      return onMoveIntent({
        sourceSquare: source,
        targetSquare: target,
        sourceElement: findSourceElement(boardRootRef.current, source),
        anchorElement: findSquareElement(boardRootRef.current, target),
      });
    },
    [onMoveIntent],
  );
  const san = branchSan(branchSnapshot.originFen, branchSnapshot.moves);
  const options = {
    allowDragging: true,
    allowDrawingArrows: false,
    animationDurationInMs: 0,
    boardOrientation: orientation,
    id: "interactive-analysis-board",
    onPieceDrag: () => undefined,
    onPieceDragCancel: () => undefined,
    onPieceDrop: handlePieceDrop,
    pieces: accessiblePieces,
    position: branchSnapshot.currentFen,
    showAnimations: false,
    showNotation: true,
  } as const;

  return (
    <section className={styles.adapter} data-testid="interactive-board-adapter">
      <div
        ref={boardRootRef}
        className={styles.board}
        data-testid="interactive-board"
        role="group"
        aria-label={label}
      >
        <Chessboard options={options} />
      </div>
      <div className={styles.branchPanel} aria-label="Temporary branch">
        <div className={styles.branchHeading}>
          <strong>Temporary branch</strong>
          <span>From captured ply {branchSnapshot.originPly}</span>
        </div>
        <div className={styles.fenFields} aria-label="Temporary branch FEN">
          <p className={styles.fenField}>
            <span>Branch origin FEN</span>
            <code data-testid="branch-origin-fen">{branchSnapshot.originFen}</code>
          </p>
          <p className={styles.fenField}>
            <span>Current branch FEN</span>
            <code data-testid="branch-current-fen">{branchSnapshot.currentFen}</code>
          </p>
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
          <Button size="sm" variant="secondary" onClick={onReset} disabled={!branchSnapshot.active}>
            Reset
          </Button>
        </div>
        <p className={styles.notice} data-testid="branch-status" role="status" aria-live="polite">
          {notice}
        </p>
      </div>
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
