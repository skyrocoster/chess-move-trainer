import { Chess, type Square } from "chess.js";
import {
  cloneElement,
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactElement,
  type SVGProps,
} from "react";
import {
  Chessboard,
  defaultPieces,
  type PieceDropHandlerArgs,
  type PieceRenderObject,
} from "react-chessboard";

import {
  PromotionPicker,
  type PromotionColor,
  type PromotionCommit,
  type PromotionPresentation,
  usePromotionController,
} from "./PromotionPicker";
import styles from "./PromotionPicker.module.css";

const PROMOTION_FEN_WHITE = "k7/4P3/8/8/8/8/8/4K3 w - - 0 1";
const PROMOTION_FEN_BLACK = "4k3/8/8/8/8/8/4p3/K7 b - - 0 1";

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

function isPromotionTarget(pieceColor: PromotionColor, square: Square) {
  return pieceColor === "w" ? square.endsWith("8") : square.endsWith("1");
}

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

export type PromotionPickerDemoProps = {
  color?: PromotionColor;
  presentation?: PromotionPresentation;
  initiallyPending?: boolean;
  onCommit?: (commit: PromotionCommit) => void;
  onReject?: (reason: "illegal" | "stale") => void;
  onCancel?: () => void;
};

export function PromotionPickerDemo({
  color = "w",
  presentation = "auto",
  initiallyPending = false,
  onCommit,
  onReject,
  onCancel,
}: PromotionPickerDemoProps) {
  const initialFen = color === "w" ? PROMOTION_FEN_WHITE : PROMOTION_FEN_BLACK;
  const chessRef = useRef<Chess | null>(null);
  if (!chessRef.current) {
    chessRef.current = new Chess(initialFen);
  }
  const chess = chessRef.current;
  const [fen, setFen] = useState(initialFen);
  const [lastSan, setLastSan] = useState("No move committed");
  const [notice, setNotice] = useState("Ready for a promotion move.");
  const boardRootRef = useRef<HTMLDivElement | null>(null);
  const initiallyPendingOpenedRef = useRef(false);

  const handleCommit = useCallback(
    (commit: PromotionCommit) => {
      setFen(commit.fen);
      setLastSan(commit.move.san);
      setNotice(`Committed ${commit.move.san}.`);
      onCommit?.(commit);
    },
    [onCommit],
  );

  const handleReject = useCallback(
    (reason: "illegal" | "stale") => {
      setNotice(
        reason === "stale"
          ? "Promotion rejected because the source position is stale."
          : "Promotion rejected because the move is illegal.",
      );
      onReject?.(reason);
    },
    [onReject],
  );

  const controller = usePromotionController({
    chess,
    onCommit: handleCommit,
    onReject: handleReject,
  });
  const {
    pending,
    sourceElement,
    anchorElement,
    requestPromotion,
    selectPromotion,
    cancelPromotion,
  } = controller;

  const handlePieceDrop = useCallback(
    ({ sourceSquare, targetSquare }: PieceDropHandlerArgs) => {
      if (!targetSquare) {
        return false;
      }

      const source = sourceSquare as Square;
      const target = targetSquare as Square;
      const piece = chess.get(source);
      if (piece?.type === "p" && isPromotionTarget(piece.color, target)) {
        const sourceElement = findSourceElement(boardRootRef.current, source);
        const anchorElement = findSquareElement(boardRootRef.current, target);
        const opened = requestPromotion(source, target, sourceElement, anchorElement);
        setNotice(opened ? "Choose a promotion piece." : "Promotion move rejected.");
        return false;
      }

      try {
        const move = chess.move({ from: source, to: target });
        setFen(chess.fen());
        setLastSan(move.san);
        setNotice(`Committed ${move.san}.`);
        return true;
      } catch {
        setNotice("Move rejected because it is illegal.");
        return false;
      }
    },
    [chess, requestPromotion],
  );

  useEffect(() => {
    if (!initiallyPending || initiallyPendingOpenedRef.current) {
      return;
    }

    const sourceSquare: Square = color === "w" ? "e7" : "e2";
    const targetSquare: Square = color === "w" ? "e8" : "e1";
    const sourceElement = findSourceElement(boardRootRef.current, sourceSquare);
    const anchorElement = findSquareElement(boardRootRef.current, targetSquare);
    if (
      sourceElement &&
      requestPromotion(sourceSquare, targetSquare, sourceElement, anchorElement)
    ) {
      initiallyPendingOpenedRef.current = true;
      setNotice("Choose a promotion piece.");
    }
  }, [color, initiallyPending, requestPromotion]);

  const options = {
    allowDragging: true,
    allowDrawingArrows: false,
    animationDurationInMs: 0,
    boardOrientation: color === "w" ? "white" : "black",
    id: "promotion-picker-board",
    onPieceDrag: () => undefined,
    onPieceDragCancel: () => undefined,
    pieces: accessiblePieces,
    position: fen,
    showAnimations: false,
    showNotation: true,
    onPieceDrop: handlePieceDrop,
  } as const;

  return (
    <section
      className={styles.demo}
      data-testid="promotion-picker-demo"
      data-presentation={presentation}
    >
      <h1>Application-owned promotion picker</h1>
      <div ref={boardRootRef} className={styles.demoBoard} data-testid="promotion-board">
        <Chessboard options={options} />
      </div>
      <div className={styles.demoState} aria-label="Promotion state">
        <p data-testid="promotion-current-fen">FEN: {fen}</p>
        <p data-testid="promotion-last-san">SAN: {lastSan}</p>
        <p data-testid="promotion-status" role="status" aria-live="polite">
          {notice}
        </p>
      </div>
      <PromotionPicker
        pending={pending}
        color={color}
        sourceElement={sourceElement}
        anchorElement={anchorElement}
        presentation={presentation}
        onSelect={selectPromotion}
        onCancel={() => {
          cancelPromotion();
          onCancel?.();
        }}
      />
    </section>
  );
}
