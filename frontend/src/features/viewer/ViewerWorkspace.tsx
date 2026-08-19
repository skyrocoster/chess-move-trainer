import { useState } from "react";
import { Field } from "@base-ui/react/field";
import { Form } from "@base-ui/react/form";
import { Input } from "@base-ui/react/input";

import { BoardAdapter, STARTING_FEN, type BoardOrientation } from "../board-adapter/BoardAdapter";
import { Button } from "../design-system/Button";
import { Disclosure } from "../design-system/Disclosure";
import { PanelFeedback } from "../design-system/feedback/PanelFeedback";
import { fetchPosition } from "./positionApi";
import { type LookupResult, type PositionLookup, type SubjectColor } from "./positionLookup";
import styles from "./ViewerWorkspace.module.css";

const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const PLY_PATTERN = /^\d+$/;

function validateGameUuid(value: unknown): string | null {
  const text = typeof value === "string" ? value.trim() : "";
  return UUID_PATTERN.test(text) ? null : "Enter a valid game UUID.";
}

function validatePly(value: unknown): string | null {
  const text = typeof value === "string" ? value.trim() : "";
  return PLY_PATTERN.test(text) ? null : "Enter a whole ply of zero or greater.";
}

const CONTEXT_NOTES = [
  "Temporary context note: the standard starting position is loaded.",
  "White has the first move and the board is oriented with White at the bottom.",
  "The coordinate labels are visible on every square.",
  "This note is intentionally long enough to exercise the panel scroll behavior.",
  "Candidate focus: opening principles, development, and control of the center.",
  "Candidate focus: look for checks, captures, and threats before choosing a move.",
  "Candidate focus: compare the position description with the board graphic.",
  "Temporary context note: more analysis content could be placed here later.",
  "Temporary context note: this panel should scroll without moving the board.",
  "Temporary context note: the surrounding workspace remains read-only.",
];

type LoadState =
  | "idle"
  | "loading"
  | "success"
  | "position_not_found"
  | "corpus_unavailable"
  | "stored_position_invalid"
  | "unexpected_failure";

type BoardModel = {
  fen: string;
  orientation: BoardOrientation;
  label: string;
};

type Selection = {
  gameUuid: string;
  ply: number;
  fen: string;
  subjectColor: SubjectColor;
};

type FailureKind = Exclude<LoadState, "idle" | "loading" | "success">;

const START_BOARD: BoardModel = {
  fen: STARTING_FEN,
  orientation: "white",
  label: BOARD_LABEL,
};

function boardFor(selection: Selection): BoardModel {
  return {
    fen: selection.fen,
    orientation: selection.subjectColor,
    label: `Chess board: game ${selection.gameUuid}, ply ${selection.ply}, ${
      selection.subjectColor === "white" ? "White" : "Black"
    } at the bottom`,
  };
}

const FAILURE_CONTENT: Record<FailureKind, { heading: string; message: string }> = {
  position_not_found: {
    heading: "Position not found",
    message: "No stored position matches this game UUID and ply.",
  },
  corpus_unavailable: {
    heading: "Corpus unavailable",
    message: "The stored position data service is unavailable or incompatible.",
  },
  stored_position_invalid: {
    heading: "Stored position unavailable",
    message: "The stored position could not be displayed because its data is invalid.",
  },
  unexpected_failure: {
    heading: "Unable to load position",
    message: "The position could not be loaded due to an unexpected error.",
  },
};

function ContextContent() {
  return (
    <ul className={styles.contextContent} tabIndex={0} aria-label="Viewer context">
      {CONTEXT_NOTES.map((note) => (
        <li key={note}>{note}</li>
      ))}
    </ul>
  );
}

export default function ViewerWorkspace({ lookup = fetchPosition }: { lookup?: PositionLookup }) {
  const [gameUuidInput, setGameUuidInput] = useState("");
  const [plyInput, setPlyInput] = useState("");
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [selection, setSelection] = useState<Selection | null>(null);
  const [board, setBoard] = useState<BoardModel | null>(START_BOARD);

  const loading = loadState === "loading";
  const isFailure = loadState !== "idle" && loadState !== "loading" && loadState !== "success";

  function resetViewer() {
    setGameUuidInput("");
    setPlyInput("");
    setLoadState("idle");
    setSelection(null);
    setBoard(START_BOARD);
  }

  async function handleSubmit(formValues: Record<string, string>) {
    const gameUuid = (formValues.gameUuid ?? "").trim();
    const plyText = (formValues.ply ?? "").trim();
    const ply = Number(plyText);
    setLoadState("loading");

    let result: LookupResult;
    try {
      result = await lookup(gameUuid, ply);
    } catch {
      result = { status: "unexpected_failure" };
    }

    if (result.status === "success") {
      const next: Selection = {
        gameUuid,
        ply,
        fen: result.fen,
        subjectColor: result.subject_color,
      };
      setSelection(next);
      setBoard(boardFor(next));
      setLoadState("success");
    } else {
      setSelection(null);
      setBoard(null);
      setLoadState(result.status);
    }
  }

  const failureContent = isFailure ? FAILURE_CONTENT[loadState as FailureKind] : null;

  return (
    <div className={`${styles.workspace} ${isFailure ? styles.failureWorkspace : ""}`}>
      <h1 className={styles.heading}>Position viewer</h1>

      <Disclosure summary="Position picker" defaultOpen>
        <Form className={styles.lookupForm} onFormSubmit={handleSubmit}>
          <Field.Root
            className={`${styles.formField} ${styles.formFieldUuid}`}
            name="gameUuid"
            validate={validateGameUuid}
          >
            <Field.Label className={styles.fieldLabel}>Game UUID</Field.Label>
            <Input
              className={styles.fieldInput}
              id="gameUuid"
              name="gameUuid"
              type="text"
              value={gameUuidInput}
              onChange={(event) => setGameUuidInput(event.target.value)}
              spellCheck={false}
            />
            <Field.Error className={styles.formError} role="alert" />
          </Field.Root>

          <Field.Root
            className={`${styles.formField} ${styles.formFieldPly}`}
            name="ply"
            validate={validatePly}
          >
            <Field.Label className={styles.fieldLabel}>Ply</Field.Label>
            <Input
              className={styles.fieldInput}
              id="ply"
              name="ply"
              type="text"
              inputMode="numeric"
              value={plyInput}
              onChange={(event) => setPlyInput(event.target.value)}
              spellCheck={false}
            />
            <Field.Error className={styles.formError} role="alert" />
          </Field.Root>

          <div className={styles.formActions}>
            <Button
              className={styles.formButton}
              type="submit"
              variant="primary"
              disabled={loading}
            >
              Load position
            </Button>
            <Button
              className={styles.formButton}
              type="button"
              variant="secondary"
              onClick={resetViewer}
            >
              Reset viewer
            </Button>
          </div>
        </Form>
      </Disclosure>

      <div className={styles.resultArea} role="status">
        {loading ? <p className={styles.loadingNote}>Loading the requested position...</p> : null}

        {failureContent ? (
          <PanelFeedback
            severity="error"
            heading={failureContent.heading}
            message={failureContent.message}
          />
        ) : null}
      </div>

      <div className={styles.boardColumn}>
        {board ? (
          <BoardAdapter
            key={`${board.fen}|${board.orientation}`}
            fen={board.fen}
            orientation={board.orientation}
            label={board.label}
          />
        ) : null}
      </div>

      <Disclosure summary="Context" defaultOpen className={styles.contextDisclosure}>
        <ContextContent />
      </Disclosure>

      {loadState === "success" && selection ? (
        <Disclosure summary="Loaded position" defaultOpen className={styles.loadedDisclosure}>
          <dl className={styles.successDetails}>
            <div className={styles.successRow}>
              <dt>Game UUID</dt>
              <dd>{selection.gameUuid}</dd>
            </div>
            <div className={styles.successRow}>
              <dt>Ply</dt>
              <dd>{selection.ply}</dd>
            </div>
            <div className={styles.successRow}>
              <dt>FEN</dt>
              <dd className={styles.fenValue}>{selection.fen}</dd>
            </div>
            <div className={styles.successRow}>
              <dt>Corpus subject color</dt>
              <dd>{selection.subjectColor === "white" ? "White" : "Black"}</dd>
            </div>
          </dl>
        </Disclosure>
      ) : null}
    </div>
  );
}
