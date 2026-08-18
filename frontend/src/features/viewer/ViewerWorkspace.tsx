import { BoardAdapter, STARTING_FEN } from "../board-adapter/BoardAdapter";
import styles from "./ViewerWorkspace.module.css";

const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";
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

function ContextContent() {
  return (
    <ul className={styles.contextContent}>
      {CONTEXT_NOTES.map((note) => (
        <li key={note}>{note}</li>
      ))}
    </ul>
  );
}

export default function ViewerWorkspace() {
  return (
    <div className={styles.workspace}>
      <h1 className={styles.heading}>Position viewer</h1>
      <div className={styles.boardColumn}>
        <BoardAdapter fen={STARTING_FEN} label={BOARD_LABEL} />
      </div>
      <div className={styles.contextPanel} tabIndex={0}>
        <h2 className={styles.contextHeading}>Context</h2>
        <ContextContent />
      </div>
      <details className={styles.contextDisclosure}>
        <summary>Context</summary>
        <ContextContent />
      </details>
    </div>
  );
}
