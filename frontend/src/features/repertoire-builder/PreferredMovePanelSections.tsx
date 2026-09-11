import { AlertDialog } from "@base-ui/react/alert-dialog";
import { ArrowRight } from "lucide-react";
import { useState } from "react";

import { Button } from "../design-system/Button";
import { type CalendarDateValue } from "../design-system/CalendarDate";
import { InlineFeedback } from "../design-system/feedback/InlineFeedback";
import { PanelFeedback } from "../design-system/feedback/PanelFeedback";
import type { PositionContextFailureCode } from "../position-context/positionContextApi";
import type { PreferredMoveFailureCode } from "./preferredMoveApi";
import { PreferredMoveActionLayout } from "./PreferredMovePrimitives";
import { RemovePreferredMoveButton, SavePreferredMoveButton } from "./PreferredMoveActionButtons";
import {
  PREFERRED_MOVE_DATE_UNAVAILABLE,
  type PreferredMoveDateCapability,
} from "./preferredMoveWorkflowState";
import type { RepertoirePositionModel } from "./repertoireWorkflowModel";
import styles from "./PreferredMovePanel.module.css";

import { useState } from "react";

export function selectedEmptyDescription(
  model: RepertoirePositionModel,
  contextLoading: boolean,
  contextError: PositionContextFailureCode | null,
): string | undefined {
  if (!model.ownTurn || contextLoading || contextError) {
    return undefined;
  }
  if (model.relationship === "empty") return "Play a legal move to select the first saved choice.";
  if (model.relationship === "saved" && model.saved) {
    return `Play a legal move to propose replacing ${model.saved.move.san}.`;
  }
  return undefined;
}

export type RuntimeChoiceBoxProps = {
  label: "Saved" | "Selected";
  semanticLabel: string;
  tone: "warning" | "success" | "neutral" | "blocked";
  move?: { san: string; uci?: string | null } | null;
  subLabel?: string;
  emptyTitle: string;
  emptyDescription?: string;
  onActivate?: () => void;
  activationLabel?: string;
  disabled?: boolean;
  "data-testid"?: string;
};

export function choiceBoxToneClass(tone: RuntimeChoiceBoxProps["tone"]): string {
  switch (tone) {
    case "warning":
      return styles.choiceBoxWarning;
    case "success":
      return styles.choiceBoxSuccess;
    case "blocked":
      return styles.choiceBoxBlocked;
    case "neutral":
      return styles.choiceBoxNeutral;
  }
}

export function RuntimeChoiceBox({
  label,
  semanticLabel,
  tone,
  move,
  subLabel,
  emptyTitle,
  emptyDescription,
  onActivate,
  activationLabel,
  disabled = false,
  "data-testid": dataTestId,
}: RuntimeChoiceBoxProps) {
  const content = (
    <>
      <p className={styles.boxLabel}>{label}</p>
      {move ? (
        <>
          <p className={styles.boxValue}>{move.san}</p>
          {subLabel ? <p className={styles.boxSub}>{subLabel}</p> : null}
        </>
      ) : (
        <div className={styles.boxEmpty}>
          <strong>{emptyTitle}</strong>
          {emptyDescription ? <span>{emptyDescription}</span> : null}
        </div>
      )}
    </>
  );

  if (onActivate) {
    return (
      <button
        type="button"
        className={`${styles.choiceBox} ${choiceBoxToneClass(tone)}`}
        aria-label={activationLabel}
        onClick={onActivate}
        disabled={disabled}
        data-testid={dataTestId}
      >
        {content}
      </button>
    );
  }

  return (
    <section
      className={`${styles.choiceBox} ${choiceBoxToneClass(tone)}`}
      aria-label={semanticLabel}
      data-testid={dataTestId}
    >
      {content}
    </section>
  );
}

export function RuntimeConnector() {
  return (
    <div className={styles.connector} aria-hidden="true">
      <ArrowRight className={styles.connectorIcon} focusable="false" />
    </div>
  );
}

export function PanelError({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className={styles.feedbackRow}>
      <PanelFeedback severity="error" role="alert" message={message} />
      {onRetry ? (
        <Button size="sm" variant="secondary" onClick={onRetry}>
          Retry
        </Button>
      ) : null}
    </div>
  );
}

export function RemoveConfirmation({
  onRemove,
  disabled = false,
  className,
}: {
  onRemove: () => void;
  disabled?: boolean;
  className?: string;
}) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <RemovePreferredMoveButton
        className={className}
        disabled={disabled}
        onClick={() => setOpen(true)}
      />
      <AlertDialog.Root open={open} onOpenChange={setOpen}>
        <AlertDialog.Portal>
          <AlertDialog.Backdrop className={styles.dialogBackdrop} />
          <AlertDialog.Viewport className={styles.dialogViewport}>
            <AlertDialog.Popup
              className={styles.dialogPopup}
              initialFocus
              finalFocus
              aria-labelledby="remove-preferred-move-title"
            >
              <AlertDialog.Title className={styles.dialogTitle} id="remove-preferred-move-title">
                Remove preferred move?
              </AlertDialog.Title>
              <AlertDialog.Description className={styles.dialogDescription}>
                This removes the saved move for the current position.
              </AlertDialog.Description>
              <div className={styles.dialogActions}>
                <Button variant="secondary" onClick={() => setOpen(false)}>
                  Cancel
                </Button>
                <RemovePreferredMoveButton
                  onClick={() => {
                    setOpen(false);
                    onRemove();
                  }}
                />
              </div>
            </AlertDialog.Popup>
          </AlertDialog.Viewport>
        </AlertDialog.Portal>
      </AlertDialog.Root>
    </>
  );
}

