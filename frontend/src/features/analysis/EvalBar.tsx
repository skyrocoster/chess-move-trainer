import { Meter } from "@base-ui/react/meter";

import type { BoardOrientation } from "../board-adapter/BoardAdapter";
import styles from "./EvalBar.module.css";

export type EvalBarDisplayState = "neutral" | "pending" | "best-line";

export type EvalBarProps = {
  orientation: BoardOrientation;
  state: EvalBarDisplayState;
  value: number;
  shortValue: string;
  accessibleValue: string;
};

export function EvalBar({ orientation, state, value, shortValue, accessibleValue }: EvalBarProps) {
  const clampedValue = Math.max(0, Math.min(100, value));

  return (
    <Meter.Root
      className={styles.bar}
      data-orientation={orientation}
      data-state={state}
      min={0}
      max={100}
      value={clampedValue}
      aria-valuetext={accessibleValue}
    >
      <Meter.Label className={styles.label}>Evaluation</Meter.Label>
      <Meter.Track className={styles.track}>
        <Meter.Indicator
          className={styles.indicator}
          style={{ width: "100%", height: `${clampedValue}%` }}
        />
        <span className={styles.midline} aria-hidden="true" />
      </Meter.Track>
      <Meter.Value className={styles.value}>{() => shortValue}</Meter.Value>
    </Meter.Root>
  );
}
