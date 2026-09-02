import { useId, useMemo, useState } from "react";

import { Button } from "../design-system/Button";
import type { ChessSide, Fen } from "../viewer/chessPrimitives";
import {
  type MoveResponseDistributionClient,
  fetchMoveResponseDistribution,
} from "./moveResponseDistributionApi";
import { MoveResponseDistributionChart } from "./MoveResponseDistributionChart";
import { MoveResponseDistributionControls } from "./MoveResponseDistributionControls";
import { deriveMoveResponseDistributionModel } from "./moveResponseDistributionModel";
import { useMoveResponseDistributionState } from "./moveResponseDistributionState";
import styles from "./MoveResponseDistribution.module.css";

export type MoveResponseDistributionProps = {
  fen: Fen | null;
  color: ChessSide;
  /** Remove the standalone card surface when a parent composition owns it. */
  embedded?: boolean;
  selectedUci?: string | null;
  client?: MoveResponseDistributionClient;
  onMoveSelect: (childUci: string) => void;
};

function colorLabel(color: ChessSide): "White" | "Black" {
  return color === "white" ? "White" : "Black";
}

export function MoveResponseDistribution({
  fen,
  color,
  embedded = false,
  selectedUci = null,
  client = fetchMoveResponseDistribution,
  onMoveSelect,
}: MoveResponseDistributionProps) {
  const state = useMoveResponseDistributionState(fen, color, client);
  const [otherExpanded, setOtherExpanded] = useState(false);
  const headingId = useId();
  const tailId = `${headingId}-other-replies`;
  const model = useMemo(
    () => (state.data === null ? null : deriveMoveResponseDistributionModel(state.data)),
    [state.data],
  );
  const label = colorLabel(color);

  const statusMessage =
    state.status === "loading"
      ? `Loading move responses for the ${label} repertoire colour.`
      : state.status === "unavailable"
        ? "Move response data is unavailable."
        : state.status === "idle"
          ? "Choose a position to view move responses."
          : (model?.message ?? "Move response data is ready.");

  return (
    <section
      className={[styles.panel, embedded ? styles.embedded : null].filter(Boolean).join(" ")}
      data-embedded={embedded ? "true" : undefined}
      data-testid="move-response-distribution"
      data-state={state.status}
      aria-labelledby={headingId}
    >
      <header className={styles.header}>
        <h2 className={styles.heading} id={headingId}>
          Move response distribution
        </h2>
        <span className={styles.color}>{label} repertoire colour</span>
      </header>

      <p
        className={styles.status}
        role={state.status === "unavailable" ? "alert" : "status"}
        aria-live={state.status === "unavailable" ? "assertive" : "polite"}
        aria-atomic="true"
      >
        {statusMessage}
      </p>

      {state.status === "loading" ? (
        <p className={styles.message}>Loading the complete set of recorded replies...</p>
      ) : state.status === "idle" ? (
        <p className={styles.message}>A canonical position is required to load replies.</p>
      ) : state.status === "unavailable" ? (
        <div className={styles.actionRow}>
          <Button type="button" variant="secondary" onClick={state.retry}>
            Retry
          </Button>
        </div>
      ) : model?.state === "no-games" ? (
        <p className={styles.message}>{model.message}</p>
      ) : model ? (
        <>
          <div className={styles.content}>
            <MoveResponseDistributionChart
              replies={model.common}
              other={model.other}
              otherExpanded={otherExpanded}
              onMoveSelect={onMoveSelect}
              onOtherToggle={() => setOtherExpanded((expanded) => !expanded)}
            />
            <MoveResponseDistributionControls
              replies={model.common}
              tail={model.tail}
              other={model.other}
              otherExpanded={otherExpanded}
              tailId={tailId}
              selectedUci={selectedUci}
              onMoveSelect={onMoveSelect}
              onOtherToggle={() => setOtherExpanded((expanded) => !expanded)}
            />
          </div>
          <p className={styles.overlapNote}>{model.overlapNote}</p>
        </>
      ) : null}
    </section>
  );
}

export const MoveResponseDistributionPanel = MoveResponseDistribution;
