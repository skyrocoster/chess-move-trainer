import { InlineFeedback } from "../design-system/feedback/InlineFeedback";
import { MoveHistory } from "../move-history/MoveHistory";
import { PositionReachFrequency } from "../position-reach-frequency/PositionReachFrequency";
import type { PositionContextResponse } from "../viewer/positionContextApi";
import type {
  MoveHistoryActivePlyChange,
  MoveHistoryInitialPosition,
  MoveHistoryMove,
} from "../move-history/moveHistoryTypes";
import { PreferredMovePanel, type PreferredMovePanelProps } from "./PreferredMovePanel";
import styles from "./RepertoireSessionPanel.module.css";

export type RepertoireSessionPanelProps = PreferredMovePanelProps & {
  positionContext?: PositionContextResponse | null;
  initialPosition?: MoveHistoryInitialPosition;
  moves?: readonly MoveHistoryMove[];
  activePly?: number;
  onActivePlyChange?: MoveHistoryActivePlyChange;
  /** @deprecated The controlled Move History replaces this presentation-only value. */
  sanHistory?: string;
  sessionStatus: string;
};

export function RepertoireSessionPanel({
  initialPosition = { ply: 0 },
  moves = [],
  activePly = initialPosition.ply,
  onActivePlyChange = () => {},
  positionContext = null,
  sessionStatus,
  ...preferredMoveProps
}: RepertoireSessionPanelProps) {
  return (
    <div className={styles.session} data-testid="repertoire-session">
      <MoveHistory
        data-testid="session-move-history"
        initialPosition={initialPosition}
        moves={moves}
        activePly={activePly}
        onActivePlyChange={onActivePlyChange}
        ariaLabel="Repertoire move history"
      />
      <PositionReachFrequency
        context={positionContext}
        selectedColor={preferredMoveProps.model.bottomColor}
      />
      <div
        data-testid="session-status"
        role="status"
        aria-live="polite"
      >
        <InlineFeedback severity="information" message={sessionStatus} />
      </div>
      <PreferredMovePanel {...preferredMoveProps} />
    </div>
  );
}
