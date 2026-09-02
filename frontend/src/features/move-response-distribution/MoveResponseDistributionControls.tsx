import type {
  MoveResponseDistributionOtherView,
  MoveResponseDistributionReplyView,
} from "./moveResponseDistributionModel";
import styles from "./MoveResponseDistribution.module.css";

export type MoveResponseDistributionControlsProps = {
  replies: readonly MoveResponseDistributionReplyView[];
  tail: readonly MoveResponseDistributionReplyView[];
  other: MoveResponseDistributionOtherView | null;
  otherExpanded: boolean;
  tailId: string;
  selectedUci: string | null;
  onMoveSelect: (childUci: string) => void;
  onOtherToggle: () => void;
};

function ReplyButton({
  reply,
  selectedUci,
  onMoveSelect,
}: {
  reply: MoveResponseDistributionReplyView;
  selectedUci: string | null;
  onMoveSelect: (childUci: string) => void;
}) {
  return (
    <li className={styles.replyItem}>
      <button
        className={styles.replyButton}
        type="button"
        data-uci={reply.child_uci}
        aria-label={reply.accessibleLabel}
        aria-pressed={selectedUci === reply.child_uci}
        onClick={() => onMoveSelect(reply.child_uci)}
      >
        <span className={styles.replyRank} aria-hidden="true">
          {reply.rank}
        </span>
        <span className={styles.replyDetails}>
          <span className={styles.replySan}>{reply.san}</span>
          {reply.opening_name ? (
            <span className={styles.openingName}>{reply.opening_name}</span>
          ) : null}
        </span>
        <span className={styles.replyMetrics}>
          <span>{reply.distinct_game_count} games</span>
          <span>{reply.percentageLabel}</span>
        </span>
      </button>
    </li>
  );
}

export function MoveResponseDistributionControls({
  replies,
  tail,
  other,
  otherExpanded,
  tailId,
  selectedUci,
  onMoveSelect,
  onOtherToggle,
}: MoveResponseDistributionControlsProps) {
  return (
    <div className={styles.controls}>
      <h3 className={styles.controlsHeading}>Common replies</h3>
      <ul className={styles.replyList} aria-label="Common replies">
        {replies.map((reply) => (
          <ReplyButton
            key={reply.child_uci}
            reply={reply}
            selectedUci={selectedUci}
            onMoveSelect={onMoveSelect}
          />
        ))}
      </ul>

      {other ? (
        <>
          <button
            className={styles.otherButton}
            type="button"
            aria-expanded={otherExpanded}
            aria-controls={tailId}
            aria-label={`${otherExpanded ? "Hide" : "Show"} other replies: ${other.accessibleLabel}`}
            onClick={onOtherToggle}
          >
            <span>Other</span>
            <span className={styles.replyMetrics} aria-hidden="true">
              <span>{other.distinct_game_count} games</span>
              <span>{other.percentageLabel}</span>
            </span>
          </button>
          <ul
            className={styles.replyList}
            id={tailId}
            aria-label="Other replies"
            hidden={!otherExpanded}
          >
            {tail.map((reply) => (
              <ReplyButton
                key={reply.child_uci}
                reply={reply}
                selectedUci={selectedUci}
                onMoveSelect={onMoveSelect}
              />
            ))}
          </ul>
        </>
      ) : null}
    </div>
  );
}
