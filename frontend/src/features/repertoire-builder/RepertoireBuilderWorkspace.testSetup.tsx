import { vi } from "vitest";

vi.mock("react-chessboard", () => ({
  defaultPieces: Object.fromEntries(
    ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"].map((pieceType) => [
      pieceType,
      () => <svg data-default-piece={pieceType} />,
    ]),
  ),
  Chessboard: ({
    options,
  }: {
    options: {
      position: string;
      pieces: Record<string, (props?: { square?: string }) => React.JSX.Element>;
      onPieceDrop: (args: { sourceSquare: string; targetSquare: string | null }) => boolean;
      squareStyles?: Record<string, React.CSSProperties>;
    };
  }) => (
    <div data-testid="mock-chessboard" data-position={options.position}>
      {[
        ["e2", "e4", "wP"],
        ["e7", "e5", "bP"],
        ["g8", "f6", "bN"],
        ["e7", "e8", "wP"],
        ["e2", "e5", "wP"],
        ["d2", "d4", "wP"],
      ].map(([source, target, pieceType]) => (
        <button
          key={`${source}-${target}-${pieceType}`}
          type="button"
          data-testid={`move-${source}-${target}`}
          data-square={source}
          aria-roledescription="draggable"
          aria-label={`Move ${source} to ${target}`}
          onClick={() => options.onPieceDrop({ sourceSquare: source, targetSquare: target })}
        >
          {options.pieces[pieceType]?.({ square: source })}
        </button>
      ))}
      {["e2", "e4", "e7", "e5", "e8", "d2", "d4"].map((square) => (
        <span
          key={`square-${square}`}
          data-testid={`board-square-${square}`}
          data-highlighted={options.squareStyles?.[square] ? "true" : "false"}
        />
      ))}
    </div>
  ),
}));

vi.mock("../design-system/CalendarDate", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../design-system/CalendarDate")>();

  return {
    ...actual,
    CalendarDate: ({
      value,
      onChange,
      label = "Date",
    }: {
      value: Date | null;
      onChange: (value: Date | null) => void;
      label?: string;
    }) => {
      const displayValue = value ? value.toISOString().slice(0, 10) : "Choose date";
      return (
        <button
          type="button"
          aria-label={`${label}: ${displayValue}`}
          onClick={() => onChange(new Date("2026-01-10T00:00:00.000Z"))}
        >
          {displayValue}
        </button>
      );
    },
  };
});

vi.mock("../board-adapter/PromotionPicker", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../board-adapter/PromotionPicker")>();

  return {
    ...actual,
    PromotionPicker: ({
      pending,
      onSelect,
    }: {
      pending: { sourceSquare: string; targetSquare: string } | null;
      onSelect: (piece: "q" | "r" | "b" | "n") => void;
    }) =>
      pending ? (
        <div role="dialog" aria-label="Choose a promotion piece">
          <button type="button" onClick={() => onSelect("n")}>
            Promote to knight
          </button>
        </div>
      ) : null,
  };
});
