import { useState, type FormEvent } from "react";

import { Button } from "../design-system/Button";
import { Disclosure } from "../design-system/Disclosure";
import { Field } from "../design-system/form-controls/Field";
import { TextInput } from "../design-system/form-controls/TextInput";
import { GAME_FAILURE_COPY, type GameFailureKind } from "./gameModel";
import styles from "./GameLoader.module.css";

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export type GameLoaderFailureKind = Exclude<GameFailureKind, "position_not_found">;
export type GameLoaderStatus = "idle" | "loading" | GameLoaderFailureKind;

export type GameLoaderValues = {
  gameUuid: string;
};

export type GameLoaderProps = {
  status?: GameLoaderStatus;
  gameUuid: string;
  onGameUuidChange: (value: string) => void;
  onSubmit?: (values: GameLoaderValues) => void;
  onReset?: () => void;
};

function validationMessage(gameUuid: string): string | null {
  if (!UUID_PATTERN.test(gameUuid.trim())) {
    return "Enter a valid game UUID.";
  }
  return null;
}

export function GameLoader({
  status = "idle",
  gameUuid,
  onGameUuidChange,
  onSubmit,
  onReset,
}: GameLoaderProps) {
  const [validationError, setValidationError] = useState<string | null>(null);
  const loading = status === "loading";
  const failure = status !== "idle" && status !== "loading" ? GAME_FAILURE_COPY[status] : null;

  function updateGameUuid(value: string) {
    onGameUuidChange(value);
    setValidationError(null);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const error = validationMessage(gameUuid);
    if (error) {
      setValidationError(error);
      return;
    }
    onSubmit?.({ gameUuid: gameUuid.trim() });
  }

  function handleReset() {
    setValidationError(null);
    onGameUuidChange("");
    onReset?.();
  }

  return (
    <Disclosure summary="Game Loader" defaultOpen>
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        <div className={styles.fields}>
          <Field
            label="Game UUID"
            invalid={validationError !== null && !UUID_PATTERN.test(gameUuid.trim())}
            error={
              validationError ? <span role="alert">{validationError}</span> : undefined
            }
          >
            <TextInput
              value={gameUuid}
              onChange={(event) => updateGameUuid(event.target.value)}
              invalid={validationError !== null && !UUID_PATTERN.test(gameUuid.trim())}
              autoComplete="off"
              spellCheck={false}
            />
          </Field>
        </div>

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
