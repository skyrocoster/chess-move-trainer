import { cloneElement, type ReactElement, type SVGProps } from "react";
import {
  Chessboard,
  defaultPieces,
  type ChessboardOptions,
  type PieceDropHandlerArgs,
  type PieceRenderObject,
} from "react-chessboard";

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

export type ChessboardSurfaceProps = {
  options: ChessboardOptions;
  accessiblePieceNames?: boolean;
};

export type ChessboardPieceDropHandlerArgs = PieceDropHandlerArgs;

/**
 * Shared boundary around react-chessboard for static and trainer boards.
 * Product-specific semantics and controls belong in the adapter that composes it.
 */
export function ChessboardSurface({
  options,
  accessiblePieceNames = false,
}: ChessboardSurfaceProps) {
  return (
    <Chessboard
      options={{
        allowDrawingArrows: false,
        ...options,
        ...(accessiblePieceNames ? { pieces: accessiblePieces } : {}),
      }}
    />
  );
}
