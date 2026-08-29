import { PreferredMovePanel, type PreferredMovePanelProps } from "./PreferredMovePanel";
import styles from "./RepertoireSessionPanel.module.css";

export type RepertoireSessionPanelProps = PreferredMovePanelProps & {
  sanHistory: string;
  sessionStatus: string;
};

export function RepertoireSessionPanel({
  sanHistory,
  sessionStatus,
  ...preferredMoveProps
}: RepertoireSessionPanelProps) {
  return (
    <div className={styles.session} data-testid="repertoire-session">
      <p className={styles.historyLabel}>Local SAN history</p>
      <p
        className={styles.history}
        data-testid="session-san-history"
        aria-label="Local SAN history"
      >
        {sanHistory || "No local moves yet"}
      </p>
      <p
        className={styles.sessionStatus}
        data-testid="session-status"
        role="status"
        aria-live="polite"
      >
        {sessionStatus}
      </p>
      <PreferredMovePanel {...preferredMoveProps} />
    </div>
  );
}
