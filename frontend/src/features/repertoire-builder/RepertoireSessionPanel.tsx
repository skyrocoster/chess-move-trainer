import { PositionReachFrequency } from "../position-reach-frequency/PositionReachFrequency";
import type { PositionContextResponse } from "../position-context/positionContextApi";
import { PreferredMovePanel, type PreferredMovePanelProps } from "./PreferredMovePanel";
import styles from "./RepertoireSessionPanel.module.css";

export type RepertoireSessionPanelProps = PreferredMovePanelProps & {
  positionContext?: PositionContextResponse | null;
};

export function RepertoireSessionPanel({
  positionContext = null,
  ...preferredMoveProps
}: RepertoireSessionPanelProps) {
  return (
    <div className={styles.session} data-testid="repertoire-session">
      <PositionReachFrequency
        context={positionContext}
        selectedColor={preferredMoveProps.model.bottomColor}
      />
      <PreferredMovePanel {...preferredMoveProps} />
    </div>
  );
}
