import { AlertDialog } from "@base-ui/react/alert-dialog";
import { useState } from "react";

import { Button } from "../design-system/Button";
import { CalendarDate, type CalendarDateValue } from "../design-system/CalendarDate";
import { formatUtcDate } from "../design-system/CalendarDateUtils";
import type { ChessSide } from "../viewer/chessPrimitives";
import type { PositionContextFailureCode } from "../viewer/positionContextApi";
import type { PreferredMoveFailureCode } from "./preferredMoveApi";
import type { PreferredMoveDraftMode, RepertoirePositionModel } from "./repertoireWorkflowModel";
import type { PositionPickerMoveRecord } from "./positionPickerSession";
import styles from "./PreferredMovePanel.module.css";

export type PreferredMoveMutationKind = "add" | "save" | "remove";

export type PreferredMovePanelProps = {
  model: RepertoirePositionModel;
  sideToMove: ChessSide;
  stagedMove: PositionPickerMoveRecord | null;
  draftMode: "idle" | PreferredMoveDraftMode;
  date: CalendarDateValue;
  mutation: PreferredMoveMutationKind | null;
  preferredLoading: boolean;
  preferredError: PreferredMoveFailureCode | null;
  contextLoading: boolean;
  contextError: PositionContextFailureCode | null;
  workflowError: PreferredMoveFailureCode | null;
  onDateChange: (value: CalendarDateValue) => void;
  onAdd: () => void;
  onEdit: () => void;
  onSave: () => void;
  onCancelEdit: () => void;
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
    case "add":
      return "Adding preferred move...";
    case "save":
      return "Saving preferred move...";
    case "remove":
      return "Removing preferred move...";
  }
}

function stagedLabel(move: PositionPickerMoveRecord): string {
  return `Staged move: ${move.san} (${move.sourceSquare}${move.targetSquare}${move.promotion ?? ""})`;
}

function playedLabel(move: PositionPickerMoveRecord): string {
  return `Played move: ${move.san} (${move.sourceSquare}${move.targetSquare}${move.promotion ?? ""})`;
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
  sideToMove,
  stagedMove,
  draftMode,
  date,
  mutation,
  preferredLoading,
  preferredError,
  contextLoading,
  contextError,
  workflowError,
  onDateChange,
  onAdd,
  onEdit,
  onSave,
  onCancelEdit,
  onPlaySavedMove,
  onRemove,
}: PreferredMovePanelProps) {
  const ownTurn = sideToMove === model.bottomColor;
  const canSave =
    ownTurn &&
    model.saveability === "savable" &&
    !preferredLoading &&
    preferredError === null &&
    !contextLoading &&
    contextError === null;
  const savedMove = model.savedMove;
  const playedMove = model.lastPlayedMove;
  const hasPersistedPreferredMove = model.lastPlayedPreferredMove?.state === "assigned";
  const disabled = mutation !== null;

  return (
    <section
      className={styles.panel}
      data-state={model.state}
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
        <p className={styles.error} role="alert">
          {failureMessage(preferredError)}
        </p>
      ) : null}
      {contextError ? (
        <p className={styles.error} role="alert">
          {contextFailureMessage(contextError)}
        </p>
      ) : null}
      {workflowError ? (
        <p className={styles.error} role="alert">
          {failureMessage(workflowError)}
        </p>
      ) : null}
      {mutation ? (
        <p className={styles.status} role="status" aria-live="polite">
          {mutationLabel(mutation)}
        </p>
      ) : null}

      {model.state === "saved" &&
      ownTurn &&
      !preferredLoading &&
      preferredError === null &&
      savedMove ? (
        <>
          <DateControl value={date} onChange={onDateChange} />
          <p className={styles.savedMove} data-testid="saved-move">
            Saved move: {savedMove.san} ({savedMove.uci})
          </p>
          {draftMode === "edit" ? (
            <>
              <p className={styles.instruction}>
                Select one legal replacement, then save it explicitly.
              </p>
              {stagedMove ? (
                <p className={styles.stagedMove} data-testid="replacement-move">
                  {stagedLabel(stagedMove)}
                </p>
              ) : null}
              <div className={styles.actions}>
                <Button onClick={onSave} disabled={!canSave || !stagedMove || disabled}>
                  Save replacement
                </Button>
                <Button variant="ghost" onClick={onCancelEdit} disabled={disabled}>
                  Cancel edit
                </Button>
                <RemoveConfirmation onRemove={onRemove} disabled={disabled} />
              </div>
            </>
          ) : (
            <div className={styles.actions}>
              <Button variant="secondary" onClick={onEdit} disabled={!canSave || disabled}>
                Edit
              </Button>
              <Button onClick={onPlaySavedMove} disabled={disabled}>
                Play saved move
              </Button>
              <RemoveConfirmation onRemove={onRemove} disabled={disabled} />
            </div>
          )}
        </>
      ) : model.state === "matching-played" && playedMove ? (
        <>
          <p className={styles.savedMove} data-testid="played-move">
            {playedLabel(playedMove)}
          </p>
          <p className={styles.instruction}>This move matches your preferred move.</p>
          {date ? (
            <p className={styles.effectiveDate} data-testid="effective-date">
              Effective from <strong>{effectiveDateLabel(date)}</strong>
            </p>
          ) : null}
          <div className={styles.actions}>
            <Button variant="secondary" onClick={onEdit} disabled={disabled}>
              Edit
            </Button>
            <RemoveConfirmation onRemove={onRemove} disabled={disabled} />
          </div>
        </>
      ) : model.state === "unsaved-played" && playedMove ? (
        <>
          <p className={styles.savedMove} data-testid="played-move">
            {playedLabel(playedMove)}
          </p>
          <p className={styles.instruction}>This move is not saved as your preferred move.</p>
          {draftMode === "edit" ? (
            <>
              <DateControl value={date} onChange={onDateChange} />
              {stagedMove ? (
                <p className={styles.stagedMove} data-testid="replacement-move">
                  {stagedLabel(stagedMove)}
                </p>
              ) : null}
              <div className={styles.actions}>
                <Button onClick={onSave} disabled={!canSave || !stagedMove || disabled}>
                  Save replacement
                </Button>
                <Button variant="ghost" onClick={onCancelEdit} disabled={disabled}>
                  Cancel edit
                </Button>
                <RemoveConfirmation onRemove={onRemove} disabled={disabled} />
              </div>
            </>
          ) : (
            <>
              {ownTurn ? <DateControl value={date} onChange={onDateChange} /> : null}
              {ownTurn ? (
                <div className={styles.actions}>
                  {hasPersistedPreferredMove ? (
                    <Button variant="secondary" onClick={onEdit} disabled={disabled}>
                      Edit
                    </Button>
                  ) : (
                    <Button onClick={onAdd} disabled={!canSave || !stagedMove || disabled}>
                      Add
                    </Button>
                  )}
                  {hasPersistedPreferredMove ? (
                    <RemoveConfirmation onRemove={onRemove} disabled={disabled} />
                  ) : null}
                </div>
              ) : null}
            </>
          )}
        </>
      ) : ownTurn && model.state === "no-saved" && canSave ? (
        <>
          <p className={styles.instruction}>No preferred move is saved for this position.</p>
          <DateControl value={date} onChange={onDateChange} />
          <p className={styles.instruction}>
            {stagedMove ? stagedLabel(stagedMove) : "Select a legal move to stage it."}
          </p>
          <div className={styles.actions}>
            <Button onClick={onAdd} disabled={!stagedMove || disabled}>
              Add
            </Button>
          </div>
        </>
      ) : null}
    </section>
  );
}
