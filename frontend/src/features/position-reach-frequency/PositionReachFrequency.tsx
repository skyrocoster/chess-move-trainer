import { Meter } from "@base-ui/react/meter";
import { useId } from "react";

import type { ChessSide } from "../viewer/chessPrimitives";
import type { PositionContextResponse } from "../viewer/positionContextApi";
import { derivePositionReachFrequencyModel } from "./positionReachFrequencyModel";
import styles from "./PositionReachFrequency.module.css";

export type PositionReachFrequencyProps = {
  context: PositionContextResponse | null;
  selectedColor: ChessSide;
};

export function PositionReachFrequency({ context, selectedColor }: PositionReachFrequencyProps) {
  const model = derivePositionReachFrequencyModel(context, selectedColor);
  const headingId = useId();

  return (
    <section className={styles.panel} data-state={model.state} aria-labelledby={headingId}>
      <div className={styles.header}>
        <h2 className={styles.heading} id={headingId}>
          Position reach frequency
        </h2>
        <span className={styles.color}>{model.colorLabel} repertoire colour</span>
      </div>

      {model.state === "available" ? (
        <div className={styles.content}>
          <div className={styles.summary}>
            <span className={styles.fraction}>{model.fractionLabel}</span>
            <span className={styles.percentage}>{model.percentageLabel}</span>
          </div>
          <Meter.Root
            className={styles.meter}
            min={0}
            max={100}
            value={model.meterValue}
            aria-valuetext={model.accessibleValue}
          >
            <Meter.Label className={styles.visuallyHidden}>
              Position reach frequency as {model.colorLabel}
            </Meter.Label>
            <Meter.Track className={styles.track}>
              <Meter.Indicator
                className={styles.indicator}
                data-testid="position-reach-indicator"
                style={{ inlineSize: `${model.meterValue}%` }}
              />
            </Meter.Track>
          </Meter.Root>
          <p className={styles.detail}>{model.message}</p>
        </div>
      ) : (
        <p className={styles.message} role="status">
          {model.message}
        </p>
      )}
    </section>
  );
}
