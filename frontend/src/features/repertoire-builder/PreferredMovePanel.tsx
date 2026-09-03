import { AlertDialog } from "@base-ui/react/alert-dialog";
import { ArrowRight } from "lucide-react";
import { useState } from "react";

import { Button } from "../design-system/Button";
import { type CalendarDateValue } from "../design-system/CalendarDate";
import { InlineFeedback } from "../design-system/feedback/InlineFeedback";
import { PanelFeedback } from "../design-system/feedback/PanelFeedback";
import type { PositionContextFailureCode } from "../viewer/positionContextApi";
import type { PreferredMoveFailureCode } from "./preferredMoveApi";
import { PreferredMoveActionLayout } from "./PreferredMovePrimitives";
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
  if (model.saveability === "unsavable") return "Not in Corpus";

  switch (model.relationship) {
    case "empty":
      return "Ready to stage";
    case "first-choice":
      return "Ready to save";
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

type RuntimeChoiceBoxProps = {
  label: "Saved" | "Staged";
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

function choiceBoxToneClass(tone: RuntimeChoiceBoxProps["tone"]): string {
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

function RuntimeChoiceBox({
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

function RuntimeConnector() {
  return (
    <div className={styles.connector} aria-hidden="true">
      <ArrowRight className={styles.connectorIcon} focusable="false" />
    </div>
  );
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

function RemoveConfirmation({
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
  // Keep the effective-date inputs in the panel contract for the workflow even while its UI is date-free.
  void date;
  void dateEdit;

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
  const showMatches =
    model.ownTurn &&
    model.saveability === "savable" &&
    contextReady &&
    !hasContextError &&
    !hasPreferredError &&
    model.relationship === "matching";
  const savedRelation = model.savedPresence === "present";
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
    ? savedMove
      ? undefined
      : "None yet"
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
  const stagedEmptyTitle =
    model.relationship === "saved" && model.saved
      ? `Stage a move to propose replacing ${model.saved.move.san}`
       : "No move staged";
  const savedSubLabel = savedMove?.uci ?? undefined;
  const canonicalNormal =
    model.ownTurn &&
    model.saveability === "savable" &&
    preferredReady &&
    contextReady &&
    !hasPreferredError &&
    !hasContextError &&
    !workflowError &&
    !mutation &&
    model.relationship !== "unknown";
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
    <div className={styles.container}>
      <section
        className={`${styles.panel} ${panelTone} ${canonicalNormal ? styles.canonicalNormal : ""}`}
        data-state={model.relationship}
        aria-labelledby="preferred-move-heading"
      >
      <header className={styles.header}>
        <div>
          <h2 className={styles.heading} id="preferred-move-heading">
            Preferred move
          </h2>
          {contextLabel ? (
            <p className={styles.meta} data-testid="preferred-context">
              {contextLabel}
            </p>
          ) : null}
        </div>
        <span className={styles.status} role="status" data-testid="preferred-status">
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

      {model.saveability === "unsavable" ? (
        <p className={styles.gate}>
          This position isn't in your corpus, so it can't be saved yet.
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
        <RuntimeChoiceBox
          label="Saved"
          semanticLabel="Current saved choice"
          tone={savedMove ? "success" : "neutral"}
          move={savedMove}
          subLabel={savedSubLabel}
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
        <RuntimeConnector />
        <RuntimeChoiceBox
          label="Staged"
          semanticLabel="Staged move"
          tone={
            stagedTone === "proposal"
              ? "warning"
              : stagedTone === "matching"
                ? "success"
                : stagedTone === "blocked"
                  ? "blocked"
                  : "neutral"
          }
          move={stagedMove ? { san: stagedMove.san, uci: model.staged?.uci } : null}
          subLabel={stagedMove ? model.staged?.uci ?? undefined : undefined}
          emptyTitle={stagedEmptyTitle}
          emptyDescription={stagedEmptyTitle === "No move staged" ? emptyDescription : undefined}
          data-testid="staged-move"
        />
      </div>

      {showMatches || showSave || showRemove ? (
        <footer className={styles.footer} data-testid="preferred-actions">
          <PreferredMoveActionLayout className={styles.actionLayout}>
            {showMatches ? (
              <Button variant="primary" className={styles.primaryAction} disabled>
                Matches saved
              </Button>
            ) : null}
            {showSave ? (
              <SavePreferredMoveButton
                className={styles.primaryAction}
                label={stagedMove ? `Save ${stagedMove.san}` : undefined}
                pending={mutation === "save"}
                disabled={!canSave || persistenceDisabled}
                onClick={onSave}
              />
            ) : null}
            {showRemove ? (
              <RemoveConfirmation
                className={styles.removeAction}
                onRemove={onRemove}
                disabled={persistenceDisabled}
              />
            ) : null}
          </PreferredMoveActionLayout>
        </footer>
      ) : null}
      </section>
    </div>
  );
}
