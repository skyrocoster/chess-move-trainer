import { Chess, type Move, type Square } from "chess.js";
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

import { Button } from "../design-system/Button";
import {
  PromotionPicker,
  type PromotionColor,
  type PromotionCommit,
  usePromotionController,
} from "./PromotionPicker";
import styles from "./InteractiveBoardAdapter.module.css";
import type { BoardOrientation } from "./BoardAdapter";

export type BranchMove = Pick<Move, "color" | "from" | "to" | "san"> & {
  promotion?: string;
};

export type BranchSnapshot = {
  viewKey: string;
  resetToken: number;
  originFen: string;
  currentFen: string;
  originPly: number;
  moves: readonly BranchMove[];
  active: boolean;
};

export type InteractiveBoardAdapterProps = {
  viewKey: string;
  originFen: string;
  originPly: number;
  orientation?: BoardOrientation;
  label: string;
  resetToken?: number;
  onBranchChange?: (snapshot: BranchSnapshot) => void;
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

function isPromotionTarget(color: PromotionColor, square: Square) {
  return color === "w" ? square.endsWith("8") : square.endsWith("1");
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

function historyMoves(chess: Chess): BranchMove[] {
  return chess.history({ verbose: true }).map((move) => ({
    color: move.color,
    from: move.from,
    to: move.to,
    san: move.san,
    ...(move.promotion ? { promotion: move.promotion } : {}),
  }));
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

export function InteractiveBoardAdapter({
  viewKey,
  originFen,
  originPly,
  orientation = "white",
  label,
  resetToken = 0,
  onBranchChange,
}: InteractiveBoardAdapterProps) {
  const boardRootRef = useRef<HTMLDivElement | null>(null);
  const chessRef = useRef<Chess | null>(null);
  if (!chessRef.current) {
    chessRef.current = new Chess(originFen);
  }
  const chess = chessRef.current;
  const [currentFen, setCurrentFen] = useState(originFen);
  const [moves, setMoves] = useState<BranchMove[]>([]);
  const [promotionColor, setPromotionColor] = useState<PromotionColor | null>(null);
  const [notice, setNotice] = useState("Make a legal move to start a temporary branch.");
  const lastResetToken = useRef(resetToken);
  const lastOriginFen = useRef(originFen);

  const syncFromChess = useCallback(() => {
    setCurrentFen(chess.fen());
    setMoves(historyMoves(chess));
  }, [chess]);

  const handleCommit = useCallback(
    (commit: PromotionCommit) => {
      setCurrentFen(commit.fen);
      setMoves(historyMoves(chess));
      setPromotionColor(null);
      setNotice(`Branch move committed: ${commit.move.san}.`);
    },
    [chess],
  );

  const handleReject = useCallback((reason: "illegal" | "stale") => {
    setPromotionColor(null);
    setNotice(
      reason === "stale"
        ? "Promotion rejected because the displayed branch position is stale."
        : "Promotion rejected because the move is illegal.",
    );
  }, []);

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

  const resetBranch = useCallback(
    (message: string) => {
      cancelPromotion();
      chess.load(originFen);
      setCurrentFen(originFen);
      setMoves([]);
      setPromotionColor(null);
      setNotice(message);
    },
    [cancelPromotion, chess, originFen],
  );

  useEffect(() => {
    if (lastOriginFen.current === originFen) {
      return;
    }
    lastOriginFen.current = originFen;
    resetBranch("Branch discarded because the displayed captured ply changed.");
  }, [originFen, resetBranch]);

  useEffect(() => {
    if (lastResetToken.current === resetToken) {
      return;
    }
    lastResetToken.current = resetToken;
    resetBranch("Branch discarded before the game or viewer was reset.");
  }, [resetBranch, resetToken]);

  useEffect(() => {
    onBranchChange?.({
      viewKey,
      resetToken,
      originFen,
      currentFen,
      originPly,
      moves,
      active: moves.length > 0 || pending !== null,
    });
  }, [pending, currentFen, moves, onBranchChange, originFen, originPly, resetToken, viewKey]);

  const handlePieceDrop = useCallback(
    ({ sourceSquare, targetSquare }: PieceDropHandlerArgs) => {
      if (!targetSquare) {
        return false;
      }

      const source = sourceSquare as Square;
      const target = targetSquare as Square;
      const piece = chess.get(source);
      if (piece?.type === "p" && isPromotionTarget(piece.color, target)) {
        const opened = requestPromotion(
          source,
          target,
          findSourceElement(boardRootRef.current, source),
          findSquareElement(boardRootRef.current, target),
        );
        if (opened) {
          setPromotionColor(piece.color);
          setNotice("Choose a promotion piece for the temporary branch.");
        }
        return false;
      }

      try {
        const move = chess.move({ from: source, to: target });
        syncFromChess();
        setNotice(`Branch move committed: ${move.san}.`);
        return true;
      } catch {
        setNotice("Move rejected because it is illegal.");
        return false;
      }
    },
    [chess, requestPromotion, syncFromChess],
  );

  const handleUndo = useCallback(() => {
    cancelPromotion();
    if (!chess.undo()) {
      return;
    }
    syncFromChess();
    setPromotionColor(null);
    setNotice("Undid the latest temporary branch move.");
  }, [cancelPromotion, chess, syncFromChess]);

  const active = moves.length > 0 || pending !== null;
  const san = branchSan(originFen, moves);
  const terminal = terminalDescription(chess);
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
    position: currentFen,
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
          <span>From captured ply {originPly}</span>
        </div>
        <div className={styles.fenFields} aria-label="Temporary branch FEN">
          <p className={styles.fenField}>
            <span>Branch origin FEN</span>
            <code data-testid="branch-origin-fen">{originFen}</code>
          </p>
          <p className={styles.fenField}>
            <span>Current branch FEN</span>
            <code data-testid="branch-current-fen">{currentFen}</code>
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
          <Button size="sm" variant="secondary" onClick={handleUndo} disabled={moves.length === 0}>
            Undo
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => resetBranch("Temporary branch reset to its captured-game ply.")}
            disabled={!active}
          >
            Reset
          </Button>
        </div>
        <p className={styles.notice} data-testid="branch-status" role="status" aria-live="polite">
          {notice}
        </p>
      </div>
      <PromotionPicker
        pending={pending}
        color={promotionColor ?? chess.turn()}
        sourceElement={sourceElement}
        anchorElement={anchorElement}
        onSelect={selectPromotion}
        onCancel={() => {
          cancelPromotion();
          setPromotionColor(null);
          setNotice("Promotion cancelled; the captured position is unchanged.");
        }}
      />
    </section>
  );
}
