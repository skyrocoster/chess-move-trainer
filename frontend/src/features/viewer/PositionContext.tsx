import type { PositionContextResponse } from "./positionContextApi";
import styles from "./GameContext.module.css";

export type PositionContextProps = {
  context: PositionContextResponse | null;
};

function recurrenceMessage(
  overallExists: boolean,
  count: number,
  color: "White" | "Black",
): string {
  return overallExists && count > 0
    ? `Seen in ${count} games as ${color}`
    : `Never seen as ${color}`;
}

export function PositionContext({ context }: PositionContextProps) {
  if (!context) {
    return null;
  }

  return (
    <div className={styles.details} role="group" aria-label="Position recurrence">
      <p className={styles.empty}>
        {recurrenceMessage(context.overall_exists, context.white_count, "White")}
      </p>
      <p className={styles.empty}>
        {recurrenceMessage(context.overall_exists, context.black_count, "Black")}
      </p>
    </div>
  );
}
