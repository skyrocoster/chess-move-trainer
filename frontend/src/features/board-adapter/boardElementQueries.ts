import type { Square } from "chess.js";

export function findBoardSourceElement(boardRoot: HTMLElement | null, sourceSquare: Square) {
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

export function findBoardSquareElement(boardRoot: HTMLElement | null, square: Square) {
  return boardRoot?.querySelector<HTMLElement>(`[data-square="${square}"]`) ?? null;
}
