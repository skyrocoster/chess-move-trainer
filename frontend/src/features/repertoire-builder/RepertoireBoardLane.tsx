import type { BoardOrientation } from "../board-adapter/BoardAdapter";
import {
  InteractiveBoardAdapter,
  type InteractiveBoardAdapterProps,
} from "../board-adapter/InteractiveBoardAdapter";
import { MoveHistory } from "../move-history/MoveHistory";
import type {
  MoveHistoryControlledState,
  MoveHistoryInput,
} from "../move-history/moveHistoryTypes";
import { BoardControl, type BoardControlProps } from "../viewer/BoardControl";
import { BoardEvalStage, type BoardEvalStageProps } from "../viewer/BoardEvalStage";
import styles from "./RepertoireBoardLane.module.css";

type BoardContentProps = Omit<InteractiveBoardAdapterProps, "orientation">;
type HistoryProps = MoveHistoryInput & MoveHistoryControlledState;

export type RepertoireBoardLaneProps = {
  orientation: BoardOrientation;
  evaluation: BoardEvalStageProps["display"];
  viewKey: string;
  board: BoardContentProps;
  controls: BoardControlProps;
  history: HistoryProps;
};

export function RepertoireBoardLane({
  orientation,
  evaluation,
  viewKey,
  board,
  controls,
  history,
}: RepertoireBoardLaneProps) {
  return (
    <section className={styles.lane} data-lane="board" data-testid="repertoire-board-lane">
      <BoardEvalStage orientation={orientation} display={evaluation}>
        <InteractiveBoardAdapter key={viewKey} {...board} orientation={orientation} />
      </BoardEvalStage>
      <div className={styles.controls}>
        <BoardControl {...controls} />
      </div>
      <MoveHistory
        {...history}
        data-testid="board-move-history"
        ariaLabel="Repertoire move history"
      />
    </section>
  );
}
