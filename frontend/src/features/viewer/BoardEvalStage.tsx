import { useCallback, useLayoutEffect, useRef, useState, type ReactNode } from "react";

import { EvalBar, type EvalBarProps } from "../analysis/EvalBar";
import type { BoardOrientation } from "../board-adapter/BoardAdapter";
import styles from "./BoardEvalStage.module.css";

const BOARD_VISUAL_SELECTOR = "[data-board-visual]";

export type BoardEvalStageProps = {
  children: ReactNode;
  orientation: BoardOrientation;
  display: Omit<EvalBarProps, "orientation">;
};

function boardVisualIn(stage: HTMLDivElement | null): HTMLElement | null {
  return stage?.querySelector<HTMLElement>(BOARD_VISUAL_SELECTOR) ?? null;
}

export function BoardEvalStage({ children, orientation, display }: BoardEvalStageProps) {
  const stageRef = useRef<HTMLDivElement>(null);
  const [boardVisual, setBoardVisual] = useState<HTMLElement | null>(null);
  const [boardHeight, setBoardHeight] = useState<number | null>(null);

  const resolveBoardVisual = useCallback(() => {
    const nextBoardVisual = boardVisualIn(stageRef.current);
    setBoardVisual((currentBoardVisual) =>
      currentBoardVisual === nextBoardVisual ? currentBoardVisual : nextBoardVisual,
    );
  }, []);

  useLayoutEffect(() => {
    const stage = stageRef.current;
    if (!stage) {
      return;
    }

    resolveBoardVisual();
    const mutationObserver = new MutationObserver(resolveBoardVisual);
    mutationObserver.observe(stage, {
      attributes: true,
      attributeFilter: ["data-board-visual"],
      childList: true,
      subtree: true,
    });

    return () => mutationObserver.disconnect();
  }, [resolveBoardVisual]);

  useLayoutEffect(() => {
    if (!boardVisual) {
      setBoardHeight(null);
      return;
    }

    const measure = () => setBoardHeight(boardVisual.getBoundingClientRect().height);
    measure();

    if (typeof ResizeObserver === "undefined") {
      return;
    }

    const resizeObserver = new ResizeObserver(measure);
    resizeObserver.observe(boardVisual);
    return () => resizeObserver.disconnect();
  }, [boardVisual]);

  return (
    <div ref={stageRef} className={styles.stage} data-board-staged data-testid="board-eval-stage">
      <div className={styles.board}>{children}</div>
      <div
        className={styles.evalBar}
        data-testid="board-eval-rail-shell"
        style={boardHeight === null ? undefined : { blockSize: `${boardHeight}px` }}
      >
        <EvalBar orientation={orientation} {...display} />
      </div>
    </div>
  );
}
