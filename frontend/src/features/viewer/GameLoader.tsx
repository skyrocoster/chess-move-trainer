import { useState, type FormEvent } from "react";

import { Button } from "../design-system/Button";
import { Disclosure } from "../design-system/Disclosure";
import { GAME_FAILURE_COPY, type GameFailureKind } from "./gameModel";
import styles from "./GameLoader.module.css";

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const PLY_PATTERN = /^\d+$/;

export type GameLoaderStatus = "idle" | "loading" | GameFailureKind;

export type GameLoaderValues = {
  gameUuid: string;
  ply: string;
};

export type GameLoaderProps = {
  status?: GameLoaderStatus;
  gameUuid?: string;
  ply?: string;
  defaultGameUuid?: string;
  defaultPly?: string;
  onGameUuidChange?: (value: string) => void;
  onPlyChange?: (value: string) => void;
  onSubmit?: (values: GameLoaderValues) => void;
  onReset?: () => void;
};

function validationMessage(gameUuid: string, ply: string): string | null {
  if (!UUID_PATTERN.test(gameUuid.trim())) {
    return "Enter a valid game UUID.";
  }
  if (ply.trim() !== "" && !PLY_PATTERN.test(ply.trim())) {
    return "Enter a whole Ply of zero or greater, or leave it blank for zero.";
  }
  return null;
}

export function GameLoader({
  status = "idle",
  gameUuid,
  ply,
  defaultGameUuid = "",
  defaultPly = "",
  onGameUuidChange,
  onPlyChange,
  onSubmit,
  onReset,
}: GameLoaderProps) {
  const [internalGameUuid, setInternalGameUuid] = useState(defaultGameUuid);
  const [internalPly, setInternalPly] = useState(defaultPly);
  const [validationError, setValidationError] = useState<string | null>(null);
  const currentGameUuid = gameUuid ?? internalGameUuid;
  const currentPly = ply ?? internalPly;
  const loading = status === "loading";
  const failure = status !== "idle" && status !== "loading" ? GAME_FAILURE_COPY[status] : null;

  function updateGameUuid(value: string) {
    setInternalGameUuid(value);
    onGameUuidChange?.(value);
    setValidationError(null);
  }

  function updatePly(value: string) {
    setInternalPly(value);
    onPlyChange?.(value);
    setValidationError(null);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const error = validationMessage(currentGameUuid, currentPly);
    if (error) {
      setValidationError(error);
      return;
    }
    onSubmit?.({ gameUuid: currentGameUuid.trim(), ply: currentPly.trim() });
  }

  function handleReset() {
    setInternalGameUuid("");
    setInternalPly("");
    setValidationError(null);
    onGameUuidChange?.("");
    onPlyChange?.("");
    onReset?.();
  }

  return (
    <Disclosure summary="Game Loader" defaultOpen>
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        <div className={styles.fields}>
          <label className={styles.field}>
            <span>Game UUID</span>
            <input
              value={currentGameUuid}
              onChange={(event) => updateGameUuid(event.target.value)}
              aria-invalid={validationError !== null && !UUID_PATTERN.test(currentGameUuid.trim())}
              autoComplete="off"
              spellCheck={false}
            />
          </label>
          <label className={styles.field}>
            <span>
              Ply <span className={styles.optional}>(optional)</span>
            </span>
            <input
              value={currentPly}
              onChange={(event) => updatePly(event.target.value)}
              inputMode="numeric"
              aria-invalid={validationError !== null && currentPly.trim() !== ""}
              autoComplete="off"
            />
          </label>
        </div>

        {validationError ? (
          <p className={styles.validationError} role="alert">
            {validationError}
          </p>
        ) : null}

        {failure ? (
          <div className={styles.failure} role="alert" aria-live="assertive">
            <h2>{failure.heading}</h2>
            <p>{failure.message}</p>
          </div>
        ) : null}

        {loading ? (
          <p className={styles.loading} role="status" aria-live="polite">
            Loading the complete game...
          </p>
        ) : null}

        <div className={styles.actions}>
          <Button type="submit" variant="primary" disabled={loading}>
            Load game
          </Button>
          <Button type="button" variant="secondary" onClick={handleReset}>
            Reset
          </Button>
        </div>
      </form>
    </Disclosure>
  );
}
