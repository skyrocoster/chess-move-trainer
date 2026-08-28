import { useId, useLayoutEffect, useRef } from "react";
import { Chess, validateFen } from "chess.js";
import { Chessboard } from "react-chessboard";
import { ErrorBoundary } from "react-error-boundary";

import { PanelFeedback } from "../design-system/feedback/PanelFeedback";
import { Disclosure } from "../design-system/Disclosure";
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
  sideToMove: PieceColor;
  occupiedSquares: string[];
  inventories: SideInventory[];
  castlingRights: CastlingRights;
  enPassantTarget: string;
  halfmoveClock: string;
  fullmoveNumber: string;
};

type PieceColor = "w" | "b";
type PieceType = "b" | "k" | "n" | "p" | "q" | "r";
type SideCastlingRights = { kingside: boolean; queenside: boolean };
type CastlingRights = {
  raw: string;
  white: SideCastlingRights;
  black: SideCastlingRights;
};
type PieceGroup = { pieceType: PieceType; label: string; squares: string[] };
type SideInventory = { color: PieceColor; groups: PieceGroup[] };

const FILES = "abcdefgh";
const PIECE_NAMES: Record<PieceType, string> = {
  b: "bishop",
  k: "king",
  n: "knight",
  p: "pawn",
  q: "queen",
  r: "rook",
};
const PIECE_GROUP_LABELS: Record<PieceType, string> = {
  b: "Bishops",
  k: "King",
  n: "Knights",
  p: "Pawns",
  q: "Queen",
  r: "Rooks",
};
const PIECE_ORDER: PieceType[] = ["k", "q", "r", "b", "n", "p"];

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function orientationLabel(orientation: BoardOrientation) {
  return orientation === "white" ? "White at the bottom" : "Black at the bottom";
}

function sideLabel(color: PieceColor) {
  return color === "w" ? "White" : "Black";
}

function createCastlingRights(rights: string): CastlingRights {
  return {
    raw: rights,
    white: { kingside: rights.includes("K"), queenside: rights.includes("Q") },
    black: { kingside: rights.includes("k"), queenside: rights.includes("q") },
  };
}

function castlingDescription(rights: CastlingRights) {
  if (rights.raw === "-") {
    return "No castling rights.";
  }

  const rightsByColor = [
    {
      color: "White",
      ...rights.white,
    },
    {
      color: "Black",
      ...rights.black,
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

function emptyPieceSquares(): Record<PieceType, string[]> {
  return { b: [], k: [], n: [], p: [], q: [], r: [] };
}

function castlingNotation(rights: SideCastlingRights) {
  return (
    [rights.kingside ? "K" : null, rights.queenside ? "Q" : null]
      .filter((right): right is string => right !== null)
      .join(" + ") || "-"
  );
}

function createPositionModel(fen: string, orientation: BoardOrientation): PositionModel {
  const chess = new Chess(fen);
  const fields = fen.split(" ");
  const [castlingField, enPassantTarget, halfmoveClock, fullmoveNumber] = fields.slice(2);
  const castlingRights = createCastlingRights(castlingField);
  const sideToMove = chess.turn() as PieceColor;
  const occupiedSquares: string[] = [];
  const squaresBySide: Record<PieceColor, Record<PieceType, string[]>> = {
    w: emptyPieceSquares(),
    b: emptyPieceSquares(),
  };

  chess.board().forEach((rank, rankIndex) => {
    rank.forEach((piece, fileIndex) => {
      if (piece === null) {
        return;
      }

      const square = `${FILES[fileIndex]}${8 - rankIndex}`;
      const pieceColor = piece.color as PieceColor;
      const pieceType = piece.type as PieceType;
      const color = sideLabel(pieceColor).toLowerCase();
      const pieceName = PIECE_NAMES[pieceType];
      occupiedSquares.push(`${color} ${pieceName} at ${square}`);
      squaresBySide[pieceColor][pieceType].push(square);
    });
  });

  const inventories = (Object.keys(squaresBySide) as PieceColor[]).map((color) => ({
    color,
    groups: PIECE_ORDER.map((pieceType) => ({
      pieceType,
      label: PIECE_GROUP_LABELS[pieceType],
      squares: squaresBySide[color][pieceType],
    })).filter((group) => group.squares.length > 0),
  }));

  const enPassantDescription =
    enPassantTarget === "-"
      ? "En-passant target: no target square."
      : `En-passant target: ${enPassantTarget}.`;

  const description = [
    `Orientation: ${orientationLabel(orientation)}.`,
    `Side to move: ${sideLabel(sideToMove)}.`,
    `Occupied squares in stable FEN order: ${occupiedSquares.join(", ")}.`,
    `Castling rights: ${castlingDescription(castlingRights)}`,
    enPassantDescription,
    `Halfmove clock: ${halfmoveClock}.`,
    `Fullmove number: ${fullmoveNumber}.`,
  ].join(" ");

  return {
    description,
    orientation,
    fen,
    sideToMove,
    occupiedSquares,
    inventories,
    castlingRights,
    enPassantTarget,
    halfmoveClock,
    fullmoveNumber,
  };
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

function VisiblePositionSummary({ model }: { model: PositionModel }) {
  return (
    <div className={styles.descriptionDisclosure} aria-hidden="true" inert>
      <div className={styles.positionSummary} data-position-summary>
        <div className={styles.positionMetadata} data-position-metadata>
          <div className={styles.metadataItem} data-position-metadata-item="orientation">
            <span className={styles.metadataLabel}>Orientation</span>
            <span className={styles.metadataValue}>{orientationLabel(model.orientation)}</span>
          </div>
          <div className={styles.metadataItem} data-position-metadata-item="side-to-move">
            <span className={styles.metadataLabel}>Side to move</span>
            <span className={styles.metadataValue}>{sideLabel(model.sideToMove)}</span>
          </div>
        </div>
        <div className={styles.positionInventories} data-position-inventories>
          {model.inventories.map((inventory) => (
            <section
              className={styles.sideInventory}
              key={inventory.color}
              data-position-side={inventory.color}
              data-position-side-to-move={model.sideToMove === inventory.color}
            >
              <div className={styles.sideHeader}>
                <h3>{sideLabel(inventory.color)}</h3>
              </div>
              <div className={styles.pieceRows}>
                {inventory.groups.map((group) => (
                  <div
                    className={styles.pieceRow}
                    key={group.pieceType}
                    data-position-piece={group.pieceType}
                  >
                    <span className={styles.pieceLabel}>{group.label}</span>
                    <span className={styles.positionSquares} data-position-squares>
                      {group.squares.map((square) => (
                        <span
                          className={styles.squareToken}
                          key={square}
                          data-position-square={square}
                        >
                          {square}
                        </span>
                      ))}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>
        <div className={styles.positionFacts} data-position-facts>
          <span className={styles.factChip} data-position-fact="castling-white">
            Castling · White <strong>{castlingNotation(model.castlingRights.white)}</strong>
          </span>
          <span className={styles.factChip} data-position-fact="castling-black">
            Castling · Black <strong>{castlingNotation(model.castlingRights.black)}</strong>
          </span>
          <span className={styles.factChip} data-position-fact="en-passant">
            En-passant target <strong>{model.enPassantTarget}</strong>
          </span>
          <span className={styles.factChip} data-position-fact="halfmove">
            Halfmove clock <strong>{model.halfmoveClock}</strong>
          </span>
          <span className={styles.factChip} data-position-fact="fullmove">
            Fullmove <strong>{model.fullmoveNumber}</strong>
          </span>
        </div>
      </div>
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
        data-board-visual
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
      <p
        className={styles.assistiveDescription}
        id={descriptionId}
        role="status"
        aria-live="polite"
        aria-atomic="true"
      >
        {model.description}
      </p>
      <Disclosure summary="Position description">
        <VisiblePositionSummary model={model} />
      </Disclosure>
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
