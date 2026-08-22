import { useCallback, useState } from "react";
import { Chess } from "chess.js";
import { Chessboard, type PieceDropHandlerArgs, type ChessboardOptions } from "react-chessboard";

export const NATIVE_PROBE_STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
export const NATIVE_PROBE_PROMOTION_FEN = "k7/4P3/8/8/8/8/8/4K3 w - - 0 1";

type NativeProbeProps = {
  fen?: string;
};

function isPromotionAttempt(fen: string, sourceSquare: string, targetSquare: string | null) {
  if (!targetSquare) {
    return false;
  }

  const piece = new Chess(fen).get(sourceSquare as Parameters<Chess["get"]>[0]);
  return piece?.type === "p" && (targetSquare.endsWith("1") || targetSquare.endsWith("8"));
}

function getLegalDrop(fen: string, sourceSquare: string, targetSquare: string | null) {
  if (!targetSquare) {
    return false;
  }

  try {
    new Chess(fen).move({ from: sourceSquare, to: targetSquare });
    return true;
  } catch {
    return false;
  }
}

export function BoardAdapterNativeProbe({ fen = NATIVE_PROBE_STARTING_FEN }: NativeProbeProps) {
  const [events, setEvents] = useState<string[]>([]);

  const record = useCallback((event: string) => {
    setEvents((current) => [...current, event]);
  }, []);

  const handlePieceDrop = useCallback(
    ({ piece, sourceSquare, targetSquare }: PieceDropHandlerArgs) => {
      const promotion = isPromotionAttempt(fen, sourceSquare, targetSquare);
      const legal = getLegalDrop(fen, sourceSquare, targetSquare);
      // The probe deliberately keeps position controlled and does not provide a promotion fallback.
      const accepted = promotion ? Boolean(targetSquare) : legal;
      record(
        `pieceDrop|${sourceSquare}->${targetSquare ?? "null"}|piece=${piece.pieceType}|legal=${legal}|promotion=${promotion}|accepted=${accepted}`,
      );
      return accepted;
    },
    [fen, record],
  );

  const options: ChessboardOptions = {
    id: "native-interaction-probe",
    allowDragging: true,
    allowDragOffBoard: true,
    allowDrawingArrows: false,
    animationDurationInMs: 0,
    boardOrientation: "white",
    position: fen,
    showAnimations: false,
    showNotation: true,
    onPieceDrag: ({ piece, square }) => {
      record(`pieceDrag|${square ?? "null"}|piece=${piece.pieceType}`);
    },
    onPieceDragCancel: () => record("pieceDragCancel"),
    onPieceClick: ({ piece, square }) => {
      record(`pieceClick|${square ?? "null"}|piece=${piece.pieceType}`);
    },
    onPieceDrop: handlePieceDrop,
    onSquareClick: ({ square }) => record(`squareClick|${square}`),
    onSquareMouseDown: ({ square }, event) => record(`squareMouseDown|${square}|${event.type}`),
    onSquareMouseUp: ({ square }, event) => record(`squareMouseUp|${square}|${event.type}`),
  };

  return (
    <section data-testid="native-interaction-probe" style={{ maxWidth: "32rem", width: "100%" }}>
      <h1>Native board interaction probe</h1>
      <div data-testid="native-probe-board">
        <Chessboard options={options} />
      </div>
      <p data-testid="native-probe-controlled-position">Controlled position: {fen}</p>
      <output aria-label="Native probe event log" data-testid="native-probe-events">
        {events.length === 0 ? "No events recorded" : events.join("\n")}
      </output>
    </section>
  );
}
