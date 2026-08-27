import { Meter } from "@base-ui/react/meter";

import type { BoardOrientation } from "../board-adapter/BoardAdapter";
import styles from "./EvalBar.module.css";

export type EvalBarDisplayState = "neutral" | "pending" | "best-line";

export type EvalBarProps = {
  orientation: BoardOrientation;
  state: EvalBarDisplayState;
  value: number;
  accessibleValue: string;
};

export function EvalBar({ orientation, state, value, accessibleValue }: EvalBarProps) {
  return (
    <Meter.Root
      className={styles.bar}
      data-orientation={orientation}
      data-state={state}
      min={0}
      max={100}
      value={value}
      aria-valuetext={accessibleValue}
    >
      <Meter.Label className={styles.label}>Evaluation</Meter.Label>
      <Meter.Track className={styles.track}>
        <Meter.Indicator
          className={styles.indicator}
          style={{ width: "100%", height: `${value}%` }}
        />
      </Meter.Track>
      <Meter.Value className={styles.value}>{() => accessibleValue}</Meter.Value>
    </Meter.Root>
  );
}
