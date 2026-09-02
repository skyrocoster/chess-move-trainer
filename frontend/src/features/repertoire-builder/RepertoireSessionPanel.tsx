import { InlineFeedback } from "../design-system/feedback/InlineFeedback";
import { PositionReachFrequency } from "../position-reach-frequency/PositionReachFrequency";
import type { PositionContextResponse } from "../viewer/positionContextApi";
import { PreferredMovePanel, type PreferredMovePanelProps } from "./PreferredMovePanel";
import styles from "./RepertoireSessionPanel.module.css";

export type RepertoireSessionPanelProps = PreferredMovePanelProps & {
  positionContext?: PositionContextResponse | null;
  sessionStatus: string;
};

export function RepertoireSessionPanel({
  positionContext = null,
  sessionStatus,
  ...preferredMoveProps
}: RepertoireSessionPanelProps) {
  return (
    <div className={styles.session} data-testid="repertoire-session">
      <PositionReachFrequency
        context={positionContext}
        selectedColor={preferredMoveProps.model.bottomColor}
      />
      <div data-testid="session-status" role="status" aria-live="polite">
        <InlineFeedback severity="information" message={sessionStatus} />
      </div>
      <PreferredMovePanel {...preferredMoveProps} />
    </div>
  );
}
