import { useId, useLayoutEffect, useRef } from "react";
import { Chess, validateFen } from "chess.js";
import { Chessboard } from "react-chessboard";
import { ErrorBoundary } from "react-error-boundary";

import { PanelFeedback } from "../design-system/feedback/PanelFeedback";
import styles from "./BoardAdapter.module.css";

export type BoardOrientation = "white" | "black";

export type BoardAdapterProps = {
  fen: string;
  orientation?: BoardOrientation;
  showCoordinates?: boolean;
  label: string;
};

type PositionModel = {
  description: string;
  orientation: BoardOrientation;
  fen: string;
};

type PieceColor = "w" | "b";
type PieceType = "b" | "k" | "n" | "p" | "q" | "r";

const FILES = "abcdefgh";
const PIECE_NAMES: Record<PieceType, string> = {
  b: "bishop",
  k: "king",
  n: "knight",
  p: "pawn",
  q: "queen",
  r: "rook",
};

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function orientationLabel(orientation: BoardOrientation) {
  return orientation === "white" ? "White at the bottom" : "Black at the bottom";
}

function sideLabel(color: PieceColor) {
  return color === "w" ? "White" : "Black";
}

function castlingDescription(rights: string) {
  if (rights === "-") {
    return "No castling rights.";
  }

  const rightsByColor = [
    {
      color: "White",
      kingside: rights.includes("K"),
      queenside: rights.includes("Q"),
    },
    {
      color: "Black",
      kingside: rights.includes("k"),
      queenside: rights.includes("q"),
    },
  ];

  return (
    rightsByColor
      .map(({ color, kingside, queenside }) => {
        const sides = [kingside ? "kingside" : null, queenside ? "queenside" : null].filter(
          (side): side is string => side !== null,
        );

        return sides.length === 0
          ? `${color} has no castling rights`
          : `${color} may castle ${sides.join(" and ")}`;
      })
      .join("; ") + "."
  );
}

function createPositionModel(fen: string, orientation: BoardOrientation): PositionModel {
  const chess = new Chess(fen);
  const fields = fen.split(" ");
  const [castlingRights, enPassantTarget, halfmoveClock, fullmoveNumber] = fields.slice(2);
  const occupiedSquares: string[] = [];

  chess.board().forEach((rank, rankIndex) => {
    rank.forEach((piece, fileIndex) => {
      if (piece === null) {
        return;
      }

      const square = `${FILES[fileIndex]}${8 - rankIndex}`;
      const color = sideLabel(piece.color as PieceColor).toLowerCase();
      const pieceName = PIECE_NAMES[piece.type as PieceType];
      occupiedSquares.push(`${color} ${pieceName} at ${square}`);
    });
  });

  const enPassantDescription =
    enPassantTarget === "-"
      ? "En-passant target: no target square."
      : `En-passant target: ${enPassantTarget}.`;

  const description = [
    `Orientation: ${orientationLabel(orientation)}.`,
    `Side to move: ${sideLabel(chess.turn() as PieceColor)}.`,
    `Occupied squares in stable FEN order: ${occupiedSquares.join(", ")}.`,
    `Castling rights: ${castlingDescription(castlingRights)} `,
    enPassantDescription,
    `Halfmove clock: ${halfmoveClock}.`,
    `Fullmove number: ${fullmoveNumber}.`,
  ].join(" ");

  return { description, fen, orientation };
}

function UnavailablePosition() {
  return (
    <div className={styles.unavailable} role="status">
      <PanelFeedback
        severity="error"
        heading="Position unavailable"
        message="This position could not be displayed. Provide a changed safe FEN to try again."
      />
    </div>
  );
}

const PACKAGE_SEMANTIC_ATTRIBUTES = [
  "role",
  "aria-roledescription",
  "tabindex",
  "aria-describedby",
  "aria-disabled",
  "aria-pressed",
  "aria-live",
  "aria-atomic",
];

const PACKAGE_SEMANTIC_SELECTOR = PACKAGE_SEMANTIC_ATTRIBUTES.map(
  (attribute) => `[${attribute}]`,
).join(", ");

function stripPackageSemantics(node: Element) {
  PACKAGE_SEMANTIC_ATTRIBUTES.forEach((attribute) => node.removeAttribute(attribute));
}

function BoardRender({
  model,
  label,
  showCoordinates,
}: { model: PositionModel } & Pick<BoardAdapterProps, "label" | "showCoordinates">) {
  const descriptionId = `board-position-description-${useId().replace(/:/g, "")}`;
  const packageBoardRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const packageBoard = packageBoardRef.current;
    if (!packageBoard) {
      return;
    }

    packageBoard
      .querySelectorAll<HTMLElement>(PACKAGE_SEMANTIC_SELECTOR)
      .forEach(stripPackageSemantics);

    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === "attributes" && mutation.target instanceof Element) {
          stripPackageSemantics(mutation.target);
        }
        mutation.addedNodes.forEach((node) => {
          if (node instanceof Element) {
            stripPackageSemantics(node);
            node
              .querySelectorAll<HTMLElement>(PACKAGE_SEMANTIC_SELECTOR)
              .forEach(stripPackageSemantics);
          }
        });
      });
    });

    observer.observe(packageBoard, {
      subtree: true,
      childList: true,
      attributes: true,
      attributeFilter: PACKAGE_SEMANTIC_ATTRIBUTES,
    });

    return () => observer.disconnect();
  }, [model.fen, model.orientation]);

  return (
    <div className={styles.adapter}>
      <div
        className={styles.boardGraphic}
        role="img"
        aria-label={label}
        aria-describedby={descriptionId}
      >
        <div ref={packageBoardRef} className={styles.packageBoard} aria-hidden="true" inert>
          <Chessboard
            options={{
              allowDragging: false,
              allowDrawingArrows: false,
              boardOrientation: model.orientation,
              position: model.fen,
              showNotation: showCoordinates,
            }}
          />
        </div>
      </div>
      <p className={styles.assistiveDescription} id={descriptionId}>
        {model.description}
      </p>
      <details className={styles.descriptionDisclosure}>
        <summary>Position description</summary>
        <p>{model.description}</p>
      </details>
    </div>
  );
}

function BoardFailureFallback() {
  return <UnavailablePosition />;
}

export function BoardAdapter({
  fen,
  orientation = "white",
  showCoordinates = true,
  label,
}: BoardAdapterProps) {
  if (!label.trim()) {
    return <UnavailablePosition />;
  }

  const validation = validateFen(fen);
  if (!validation.ok) {
    return <UnavailablePosition />;
  }

  let model: PositionModel;
  try {
    model = createPositionModel(fen, orientation);
  } catch {
    return <UnavailablePosition />;
  }

  return (
    <ErrorBoundary FallbackComponent={BoardFailureFallback}>
      <BoardRender model={model} label={label} showCoordinates={showCoordinates} />
    </ErrorBoundary>
  );
}

// Exported for Storybook fixtures only; moving it to a separate file would
// create an unauthorized new source path.
// eslint-disable-next-line react-refresh/only-export-components
export { STARTING_FEN };
