import { AlertDialog } from "@base-ui/react/alert-dialog";
import { useState } from "react";

import { Button } from "../design-system/Button";
import { CalendarDate, type CalendarDateValue } from "../design-system/CalendarDate";
import { formatUtcDate } from "../design-system/CalendarDateUtils";
import { InlineFeedback } from "../design-system/feedback/InlineFeedback";
import { PanelFeedback } from "../design-system/feedback/PanelFeedback";
import type { PositionContextFailureCode } from "../viewer/positionContextApi";
import type { PreferredMoveFailureCode } from "./preferredMoveApi";
import type { RepertoirePositionModel } from "./repertoireWorkflowModel";
import type { PositionPickerMoveRecord } from "./positionPickerSession";
import styles from "./PreferredMovePanel.module.css";

export type PreferredMoveMutationKind = "save" | "remove";

export type PreferredMovePanelProps = {
  model: RepertoirePositionModel;
  date: CalendarDateValue;
  mutation: PreferredMoveMutationKind | null;
  preferredLoading: boolean;
  preferredError: PreferredMoveFailureCode | null;
  contextLoading: boolean;
  contextError: PositionContextFailureCode | null;
  workflowError: PreferredMoveFailureCode | null;
  onDateChange: (value: CalendarDateValue) => void;
  onSave: () => void;
  onPlaySavedMove: () => void;
  onRemove: () => void;
};

function failureMessage(code: PreferredMoveFailureCode): string {
  switch (code) {
    case "invalid_fen":
      return "This position could not be saved.";
    case "invalid_move":
      return "That move is not legal for this position.";
    case "invalid_timestamp":
      return "The selected date could not be used.";
    case "future_effective_time":
      return "The selected date cannot be in the future.";
    case "position_not_found":
      return "This position is not available to save.";
    case "preferred_move_unavailable":
      return "Preferred move data is unavailable. Try again.";
    case "unexpected_failure":
      return "The preferred move could not be updated. Try again.";
  }
}

function contextFailureMessage(code: PositionContextFailureCode): string {
  switch (code) {
    case "invalid_fen":
      return "Position context is unavailable for this position.";
    case "position_context_unavailable":
      return "Position context is temporarily unavailable.";
    case "unexpected_failure":
      return "Position context could not be loaded.";
  }
}

function mutationLabel(mutation: PreferredMoveMutationKind): string {
  switch (mutation) {
    case "save":
      return "Saving preferred move...";
    case "remove":
      return "Removing preferred move...";
  }
}

function stagedLabel(move: PositionPickerMoveRecord): string {
  return `Staged move: ${move.san} (${move.sourceSquare}${move.targetSquare}${move.promotion ?? ""})`;
}

function effectiveDateLabel(value: CalendarDateValue): string | null {
  if (!value) {
    return null;
  }
  const formatted = formatUtcDate(value);
  return formatted === formatUtcDate(new Date()) ? "Today" : formatted;
}

function DateControl({
  value,
  onChange,
}: {
  value: CalendarDateValue;
  onChange: (value: CalendarDateValue) => void;
}) {
  const displayValue = effectiveDateLabel(value);

  return (
    <div className={styles.date}>
      <span className={styles.dateLabel}>Effective date</span>
      {displayValue ? (
        <span className={styles.effectiveDate} data-testid="effective-date">
          Effective from <strong>{displayValue}</strong>
        </span>
      ) : null}
      <CalendarDate value={value} onChange={onChange} label="Effective date" />
    </div>
  );
}

function RemoveConfirmation({
  onRemove,
  disabled = false,
}: {
  onRemove: () => void;
  disabled?: boolean;
}) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button variant="ghost" onClick={() => setOpen(true)} disabled={disabled}>
        Remove
      </Button>
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
              <div className={styles.actions}>
                <Button variant="secondary" onClick={() => setOpen(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={() => {
                    setOpen(false);
                    onRemove();
                  }}
                >
                  Remove
                </Button>
              </div>
            </AlertDialog.Popup>
          </AlertDialog.Viewport>
        </AlertDialog.Portal>
      </AlertDialog.Root>
    </>
  );
}

export function PreferredMovePanel({
  model,
  date,
  mutation,
  preferredLoading,
  preferredError,
  contextLoading,
  contextError,
  workflowError,
  onDateChange,
  onSave,
  onPlaySavedMove,
  onRemove,
}: PreferredMovePanelProps) {
  const ownTurn = model.ownTurn;
  const canSave =
    ownTurn &&
    model.saveability === "savable" &&
    model.savedPresence !== "unknown" &&
    (model.relationship === "first-choice" || model.relationship === "replacement") &&
    model.stagedMove !== null &&
    !preferredLoading &&
    preferredError === null &&
    !contextLoading &&
    contextError === null;
  const savedMove = model.savedMove;
  const stagedMove = model.stagedMove ?? model.staged?.move ?? null;
  const disabled = mutation !== null;

  return (
    <section
      className={styles.panel}
      data-state={model.relationship}
      aria-labelledby="preferred-move-heading"
    >
      <h2 className={styles.heading} id="preferred-move-heading">
        Preferred move
      </h2>
      <p className={styles.context} data-testid="preferred-context">
        {model.contextMessage ??
          (contextLoading
            ? "Loading position context..."
            : contextError
              ? contextFailureMessage(contextError)
              : "Position context is unavailable.")}
      </p>
      {model.saveability === "unsavable" ? (
        <p className={styles.instruction}>
          This position cannot be saved because it is not in the corpus.
        </p>
      ) : null}
      {preferredError ? (
        <PanelFeedback severity="error" role="alert" message={failureMessage(preferredError)} />
      ) : null}
      {contextError ? (
        <PanelFeedback
          severity="error"
          role="alert"
          message={contextFailureMessage(contextError)}
        />
      ) : null}
      {workflowError ? (
        <PanelFeedback severity="error" role="alert" message={failureMessage(workflowError)} />
      ) : null}
      {mutation ? (
        <InlineFeedback
          severity="information"
          role="status"
          aria-live="polite"
          message={mutationLabel(mutation)}
        />
      ) : null}

      {savedMove &&
      model.savedPresence === "present" &&
      !preferredLoading &&
      preferredError === null ? (
        <>
          {ownTurn ? <DateControl value={date} onChange={onDateChange} /> : null}
          {ownTurn ? (
            <Button
              data-testid="saved-move"
              onClick={onPlaySavedMove}
              disabled={disabled}
              aria-label={`Current saved choice: ${savedMove.san}; play and stage this move.`}
            >
              Current saved choice: {savedMove.san} ({savedMove.uci})
            </Button>
          ) : (
            <p className={styles.savedMove} data-testid="saved-move">
              Current saved choice: {savedMove.san} ({savedMove.uci})
            </p>
          )}
          {stagedMove ? (
            <p className={styles.stagedMove} data-testid="staged-move">
              {stagedLabel(stagedMove)}
            </p>
          ) : null}
          <div className={styles.actions}>
            {canSave ? (
              <Button onClick={onSave} disabled={disabled}>
                Save
              </Button>
            ) : null}
            {ownTurn ? <RemoveConfirmation onRemove={onRemove} disabled={disabled} /> : null}
          </div>
        </>
      ) : model.savedPresence === "absent" && ownTurn && stagedMove ? (
        <>
          <DateControl value={date} onChange={onDateChange} />
          <p className={styles.instruction} data-testid="staged-move">
            {stagedLabel(stagedMove)}
          </p>
          <div className={styles.actions}>
            {canSave ? (
              <Button onClick={onSave} disabled={disabled}>
                Save
              </Button>
            ) : null}
          </div>
        </>
      ) : model.savedPresence === "absent" && ownTurn && !stagedMove ? (
        <p className={styles.instruction}>Select a legal move to stage it.</p>
      ) : null}
    </section>
  );
}
