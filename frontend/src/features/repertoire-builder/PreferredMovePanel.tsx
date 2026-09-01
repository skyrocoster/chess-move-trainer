import { AlertDialog } from "@base-ui/react/alert-dialog";
import { CalendarDays } from "lucide-react";
import { useState } from "react";

import { Button } from "../design-system/Button";
import { type CalendarDateValue } from "../design-system/CalendarDate";
import { InlineFeedback } from "../design-system/feedback/InlineFeedback";
import { PanelFeedback } from "../design-system/feedback/PanelFeedback";
import type { PositionContextFailureCode } from "../viewer/positionContextApi";
import type { PreferredMoveFailureCode } from "./preferredMoveApi";
import {
  PreferredMoveActionLayout,
  PreferredMoveChoiceBox,
  PreferredMoveConsequence,
  PreferredMoveConnector,
} from "./PreferredMovePrimitives";
import { RemovePreferredMoveButton, SavePreferredMoveButton } from "./PreferredMoveActionButtons";
import {
  PREFERRED_MOVE_DATE_UNAVAILABLE,
  type PreferredMoveDateCapability,
} from "./preferredMoveWorkflowState";
import type { RepertoirePositionModel } from "./repertoireWorkflowModel";
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
  /** @deprecated Date selection is unavailable until the storage decision is reauthorized. */
  onDateChange?: (value: CalendarDateValue) => void;
  dateEdit?: PreferredMoveDateCapability;
  onSave: () => void;
  onPlaySavedMove: () => void;
  onRemove: () => void;
  onRetry?: () => void;
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

function statusLabel({
  model,
  mutation,
  preferredLoading,
  preferredError,
  contextLoading,
  contextError,
}: Pick<
  PreferredMovePanelProps,
  "model" | "mutation" | "preferredLoading" | "preferredError" | "contextLoading" | "contextError"
>): string {
  if (mutation) return mutation === "save" ? "Saving" : "Removing";
  if (preferredLoading && model.savedPresence === "unknown") return "Loading saved choice...";
  if (contextLoading && model.saveability === "unknown") return "Loading position context...";
  if (preferredError && model.savedPresence === "unknown") return "Saved choice unavailable";
  if (contextError && model.saveability === "unknown") return "Position context unavailable";
  if (!model.ownTurn) return "Opponent turn";
  if (model.saveability === "unsavable") return "Saving unavailable";

  switch (model.relationship) {
    case "empty":
      return "Ready to stage";
    case "first-choice":
      return "First choice ready";
    case "saved":
      return "Saved";
    case "replacement":
      return "Ready to save";
    case "matching":
      return "Already saved";
    case "unknown":
      return "Checking position";
  }
}

function connectorLabel(model: RepertoirePositionModel): string {
  switch (model.relationship) {
    case "first-choice":
      return "first choice";
    case "replacement":
      return "replace";
    case "matching":
      return "matches";
    case "unknown":
      return "checking";
    default:
      return model.ownTurn ? "stage a move" : "your turn next";
  }
}

function stagedEmptyDescription(
  model: RepertoirePositionModel,
  contextLoading: boolean,
  contextError: PositionContextFailureCode | null,
): string | undefined {
  if (!model.ownTurn || contextLoading || contextError || model.saveability !== "savable") {
    return undefined;
  }
  if (model.relationship === "empty")
    return "Stage a legal move to propose the first saved choice.";
  if (model.relationship === "saved" && model.saved) {
    return `Stage a legal move to propose replacing ${model.saved.move.san}.`;
  }
  return undefined;
}

function PanelError({ message, onRetry }: { message: string; onRetry?: () => void }) {
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

function DateAction({
  capability,
  disabled,
}: {
  capability: PreferredMoveDateCapability;
  disabled: boolean;
}) {
  const reason = capability.available ? null : capability.reason;

  return (
    <div className={styles.dateAction}>
      <Button
        variant="secondary"
        disabled={disabled || !capability.available}
        onClick={capability.onActivate}
        aria-describedby={reason ? "preferred-date-unavailable" : undefined}
      >
        <CalendarDays aria-hidden="true" focusable="false" className={styles.actionIcon} />
        <span>Change effective date</span>
      </Button>
      {reason ? (
        <span id="preferred-date-unavailable" className={styles.dateUnavailable}>
          {reason}
        </span>
      ) : null}
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
      <RemovePreferredMoveButton disabled={disabled} onClick={() => setOpen(true)} />
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

export function PreferredMovePanel({
  model,
  date,
  mutation,
  preferredLoading,
  preferredError,
  contextLoading,
  contextError,
  workflowError,
  dateEdit = {
    available: false,
    reason: PREFERRED_MOVE_DATE_UNAVAILABLE,
    onActivate: () => undefined,
    onChange: () => undefined,
  },
  onSave,
  onPlaySavedMove,
  onRemove,
  onRetry,
}: PreferredMovePanelProps) {
  const preferredKnown = model.savedPresence !== "unknown";
  const savedMove = preferredKnown ? (model.saved?.move ?? null) : null;
  const stagedMove = model.staged?.move ?? null;
  const hasPreferredError = preferredError !== null;
  const hasContextError = contextError !== null;
  const preferredReady = preferredKnown || preferredLoading || hasPreferredError;
  const contextReady = !contextLoading && !hasContextError;
  const canSave =
    model.ownTurn &&
    model.saveability === "savable" &&
    contextReady &&
    preferredReady &&
    model.staged !== null &&
    (model.relationship === "first-choice" || model.relationship === "replacement") &&
    !hasPreferredError;
  const saveRelationship =
    model.ownTurn &&
    model.staged !== null &&
    (model.relationship === "first-choice" || model.relationship === "replacement");
  const showSave =
    (mutation === "save" || (saveRelationship && model.saveability === "savable")) &&
    contextReady &&
    !hasContextError &&
    !hasPreferredError;
  const savedRelation = model.savedPresence === "present";
  const firstChoiceDate =
    model.relationship === "first-choice" &&
    model.saveability === "savable" &&
    contextReady &&
    !hasPreferredError;
  const showDate =
    model.ownTurn &&
    !hasPreferredError &&
    (savedRelation ||
      firstChoiceDate ||
      (mutation === "save" && model.staged !== null && model.ownTurn));
  const showRemove = model.ownTurn && savedRelation && !hasPreferredError;
  const persistenceDisabled = mutation !== null || preferredLoading || contextLoading;
  const stagedTone =
    !model.ownTurn || model.saveability === "unsavable"
      ? "blocked"
      : model.relationship === "matching"
        ? "matching"
        : stagedMove
          ? "proposal"
          : "empty";
  const savedEmptyTitle = preferredKnown
    ? undefined
    : preferredError
      ? "Saved choice unavailable."
      : preferredLoading
        ? "Loading saved choice..."
        : "Saved choice is unavailable.";
  const contextLabel =
    model.contextMessage ??
    (contextLoading
      ? "Loading position context..."
      : contextError
        ? contextFailureMessage(contextError)
        : null);
  const emptyDescription = stagedEmptyDescription(model, contextLoading, contextError);
  const showConsequence =
    model.ownTurn &&
    !hasPreferredError &&
    !hasContextError &&
    contextReady &&
    ((model.relationship === "first-choice" && model.saveability === "savable") ||
      (model.relationship === "replacement" && model.saveability === "savable") ||
      model.relationship === "matching");
  const panelTone =
    !model.ownTurn || model.saveability === "unsavable"
      ? styles.toneBlocked
      : model.relationship === "matching"
        ? styles.toneMatching
        : model.relationship === "saved"
          ? styles.toneSaved
          : model.relationship === "unknown"
            ? styles.toneChecking
            : styles.toneReady;

  return (
    <section
      className={`${styles.panel} ${panelTone}`}
      data-state={model.relationship}
      aria-labelledby="preferred-move-heading"
    >
      <header className={styles.header}>
        <div>
          <span className={styles.kicker}>Preferred move</span>
          <h2 className={styles.heading} id="preferred-move-heading">
            What is saved, and what is staged?
          </h2>
        </div>
        <span className={styles.status} data-testid="preferred-status">
          {statusLabel({
            model,
            mutation,
            preferredLoading,
            preferredError,
            contextLoading,
            contextError,
          })}
        </span>
      </header>

      {contextLabel ? (
        <p className={styles.context} data-testid="preferred-context">
          {contextLabel}
        </p>
      ) : null}
      {model.saveability === "unsavable" ? (
        <p className={styles.gate}>
          This position cannot be saved because it is not in the corpus.
        </p>
      ) : null}
      {!model.ownTurn ? (
        <p className={styles.gate}>Wait for your turn to stage or save a preferred move.</p>
      ) : null}

      {preferredError ? (
        <PanelError message={failureMessage(preferredError)} onRetry={onRetry} />
      ) : null}
      {contextError ? (
        <PanelError message={contextFailureMessage(contextError)} onRetry={onRetry} />
      ) : null}
      {workflowError ? (
        <PanelError message={failureMessage(workflowError)} onRetry={onRetry} />
      ) : null}
      {mutation ? (
        <InlineFeedback
          severity="information"
          role="status"
          aria-live="polite"
          message={mutationLabel(mutation)}
        />
      ) : null}

      <div className={styles.relationship}>
        <PreferredMoveChoiceBox
          label="Current saved choice"
          tone={savedMove ? "saved" : "empty"}
          move={savedMove}
          effectiveDate={savedMove && model.saved && date ? date : null}
          emptyTitle={savedEmptyTitle}
          onActivate={savedMove && model.ownTurn ? onPlaySavedMove : undefined}
          activationLabel={
            savedMove
              ? `Current saved choice: ${savedMove.san}; play and stage this move.`
              : undefined
          }
          disabled={mutation !== null || preferredLoading}
          data-testid="saved-move"
        />
        <PreferredMoveConnector label={connectorLabel(model)} />
        <PreferredMoveChoiceBox
          label="Staged move"
          tone={stagedTone}
          move={stagedMove ? { san: stagedMove.san, uci: model.staged?.uci } : null}
          emptyDescription={emptyDescription}
          data-testid="staged-move"
        />
      </div>

      {showConsequence ? (
        <div className={styles.consequence} data-testid="preferred-consequence">
          {model.relationship === "first-choice" ? (
            <PreferredMoveConsequence kind="first-choice" stagedSan={model.staged!.move.san} />
          ) : model.relationship === "replacement" ? (
            <PreferredMoveConsequence
              kind="replacement"
              stagedSan={model.staged!.move.san}
              savedSan={model.saved!.move.san}
            />
          ) : (
            <PreferredMoveConsequence kind="matching" savedSan={model.saved!.move.san} />
          )}
        </div>
      ) : null}

      {showSave || showDate || showRemove ? (
        <footer className={styles.footer} data-testid="preferred-actions">
          <PreferredMoveActionLayout className={styles.actionLayout}>
            {showSave ? (
              <SavePreferredMoveButton
                pending={mutation === "save"}
                disabled={!canSave || persistenceDisabled}
                onClick={onSave}
              />
            ) : null}
            {showDate ? <DateAction capability={dateEdit} disabled={persistenceDisabled} /> : null}
            {showRemove ? (
              <RemoveConfirmation onRemove={onRemove} disabled={persistenceDisabled} />
            ) : null}
          </PreferredMoveActionLayout>
        </footer>
      ) : null}
    </section>
  );
}
