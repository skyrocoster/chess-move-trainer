import { Chess } from "chess.js";

export type BoardOrientation = "white" | "black";

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

export type PositionModel = {
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

export function orientationLabel(orientation: BoardOrientation) {
  return orientation === "white" ? "White at the bottom" : "Black at the bottom";
}

export function sideLabel(color: PieceColor) {
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

export function castlingNotation(rights: SideCastlingRights) {
  return (
    [rights.kingside ? "K" : null, rights.queenside ? "Q" : null]
      .filter((right): right is string => right !== null)
      .join(" + ") || "-"
  );
}

export function createPositionModel(fen: string, orientation: BoardOrientation): PositionModel {
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
