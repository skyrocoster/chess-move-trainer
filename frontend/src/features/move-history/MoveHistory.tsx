import type { ComponentPropsWithoutRef, KeyboardEvent } from "react";
import { useEffect, useMemo, useRef } from "react";

import { createMoveHistoryModel, navigateMoveHistory } from "./moveHistoryModel";
import styles from "./MoveHistory.module.css";
import type {
  MoveHistoryControlledState,
  MoveHistoryInput,
  MoveHistoryEntry,
  MoveHistoryNavigation,
} from "./moveHistoryTypes";

export interface MoveHistoryProps
  extends Omit<ComponentPropsWithoutRef<"nav">, "aria-label" | "children">,
    MoveHistoryInput,
    MoveHistoryControlledState {
  ariaLabel?: string;
}

const KEY_NAVIGATION: Readonly<Record<string, MoveHistoryNavigation>> = {
  ArrowDown: "next",
  ArrowLeft: "previous",
  ArrowRight: "next",
  ArrowUp: "previous",
  End: "end",
  Home: "home",
};

interface MoveHistoryRow {
  readonly moveNumber: number;
  white?: Extract<MoveHistoryEntry, { kind: "move" }>;
  black?: Extract<MoveHistoryEntry, { kind: "move" }>;
}

function createMoveHistoryRows(entries: readonly MoveHistoryEntry[]): MoveHistoryRow[] {
  const rows: MoveHistoryRow[] = [];

  for (const entry of entries) {
    if (entry.kind === "initial") continue;

    const moveNumber = Math.ceil(entry.ply / 2);
    let row = rows.at(-1);
    if (!row || row.moveNumber !== moveNumber) {
      row = { moveNumber };
      rows.push(row);
    }

    if (entry.ply % 2 === 1) {
      row.white = entry;
    } else {
      row.black = entry;
    }
  }

  return rows;
}

export function MoveHistory({
  initialPosition,
  moves,
  activePly,
  onActivePlyChange,
  ariaLabel = "Move history",
  className,
  ...rest
}: MoveHistoryProps) {
  const model = useMemo(
    () => createMoveHistoryModel({ initialPosition, moves }),
    [initialPosition, moves],
  );
  const moveRows = createMoveHistoryRows(model.entries);
  const activeButtonRef = useRef<HTMLButtonElement | null>(null);
  const previousActivePlyRef = useRef<number | null>(null);

  useEffect(() => {
    const activeButton = activeButtonRef.current;
    if (!activeButton) return;

    if (previousActivePlyRef.current !== null && previousActivePlyRef.current !== activePly) {
      activeButton.focus({ preventScroll: true });
    }
    if (typeof activeButton.scrollIntoView === "function") {
      activeButton.scrollIntoView({ behavior: "auto", block: "nearest" });
    }
    previousActivePlyRef.current = activePly;
  }, [activePly, model]);

  function handleKeyDown(event: KeyboardEvent<HTMLButtonElement>, entryPly: number) {
    const navigation = KEY_NAVIGATION[event.key];
    if (!navigation) return;

    event.preventDefault();
    onActivePlyChange(navigateMoveHistory(model, entryPly, navigation));
  }

  function renderEntry(entry: MoveHistoryEntry) {
    const isActive = entry.ply === activePly;
    const accessibleName =
      entry.kind === "initial"
        ? "Initial position"
        : `${entry.ply % 2 === 1 ? "White" : "Black"}, move ${Math.ceil(entry.ply / 2)}, ${entry.san}`;

    return (
      <button
        ref={isActive ? activeButtonRef : undefined}
        className={styles.entry}
        type="button"
        aria-current={isActive ? "step" : undefined}
        aria-label={accessibleName}
        data-active={isActive ? "true" : undefined}
        data-ply={entry.ply}
        onClick={() => onActivePlyChange(entry.ply)}
        onKeyDown={(event) => handleKeyDown(event, entry.ply)}
      >
        {entry.kind === "initial" ? "Initial position" : entry.san}
      </button>
    );
  }

  const historyClassName = [styles.history, className].filter(Boolean).join(" ");

  return (
    <nav {...rest} className={historyClassName} aria-label={ariaLabel}>
      <div className={styles.list}>
        <table className={styles.table}>
          <caption className={styles.visuallyHidden}>Move history by move number</caption>
          <colgroup>
            <col className={styles.numberColumn} />
            <col />
            <col />
          </colgroup>
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">White</th>
              <th scope="col">Black</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row" className={styles.moveNumber}>
                <span aria-hidden="true">-</span>
                <span className={styles.visuallyHidden}>Start</span>
              </th>
              <td colSpan={2}>{renderEntry(model.entries[0]!)}</td>
            </tr>
            {moveRows.map((row) => (
              <tr key={row.moveNumber}>
                <th scope="row" className={styles.moveNumber}>
                  {row.moveNumber}.
                </th>
                <td>
                  {row.white ? renderEntry(row.white) : <span className={styles.emptyMove}>-</span>}
                </td>
                <td>
                  {row.black ? renderEntry(row.black) : <span className={styles.emptyMove}>-</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </nav>
  );
}
