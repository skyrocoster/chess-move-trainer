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
    case "invalid_from":
    case "invalid_until":
    case "invalid_window":
    case "invalid_effective_from":
    case "invalid_effective_until":
      return "The current preferred-move window could not be used.";
    case "invalid_preference":
    case "invalid_uci":
    case "illegal_move":
      return "That move could not be saved for this position.";
    case "preferred_moves_unavailable":
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

import { PanelError, RemoveConfirmation, RuntimeChoiceBox, RuntimeConnector, selectedEmptyDescription } from "./PreferredMovePanelSections";
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
  const selectedMove = model.selected;
  const hasPreferredError = preferredError !== null;
  const hasContextError = contextError !== null;
  const preferredReady = preferredKnown || preferredLoading || hasPreferredError;
  const contextReady = !contextLoading && !hasContextError;
  const canSave =
    model.ownTurn &&
    contextReady &&
    preferredReady &&
    model.selected !== null &&
    (model.relationship === "first-choice" || model.relationship === "replacement") &&
    !hasPreferredError;
  const saveRelationship =
    model.ownTurn &&
    model.selected !== null &&
    (model.relationship === "first-choice" || model.relationship === "replacement");
  const showSave =
    (mutation === "save" || saveRelationship) &&
    contextReady &&
    !hasContextError &&
    !hasPreferredError;
  const showMatches =
    model.ownTurn &&
    contextReady &&
    !hasContextError &&
    !hasPreferredError &&
    model.relationship === "matching";
  const savedRelation = model.savedPresence === "present";
  const showRemove = model.ownTurn && savedRelation && !hasPreferredError;
  const persistenceDisabled = mutation !== null || preferredLoading || contextLoading;
  const selectedTone = !model.ownTurn
    ? "blocked"
    : model.relationship === "matching"
      ? "matching"
      : selectedMove
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
  const emptyDescription = selectedEmptyDescription(model, contextLoading, contextError);
  const selectedEmptyTitle =
    model.relationship === "saved" && model.saved
      ? `Select a move to propose replacing ${model.saved.move.san}`
      : "No move selected";
  const savedSubLabel = savedMove?.uci ?? undefined;
  const canonicalNormal =
    model.ownTurn &&
    preferredReady &&
    contextReady &&
    !hasPreferredError &&
    !hasContextError &&
    !workflowError &&
    !mutation &&
    model.relationship !== "unknown";
  const panelTone = !model.ownTurn
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

        {!model.ownTurn ? (
          <p className={styles.gate}>Wait for your turn to select or save a preferred move.</p>
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
              savedMove ? `Current saved choice: ${savedMove.san}; play this move.` : undefined
            }
            disabled={mutation !== null || preferredLoading}
            data-testid="saved-move"
          />
          <RuntimeConnector />
          <RuntimeChoiceBox
            label="Selected"
            semanticLabel="Selected move"
            tone={
              selectedTone === "proposal"
                ? "warning"
                : selectedTone === "matching"
                  ? "success"
                  : selectedTone === "blocked"
                    ? "blocked"
                    : "neutral"
            }
            move={selectedMove ? { san: selectedMove.san, uci: selectedMove.uci } : null}
            subLabel={selectedMove ? selectedMove.uci : undefined}
            emptyTitle={selectedEmptyTitle}
            emptyDescription={
              selectedEmptyTitle === "No move selected" ? emptyDescription : undefined
            }
            data-testid="selected-move"
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
                  label={selectedMove ? `Save ${selectedMove.san}` : undefined}
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