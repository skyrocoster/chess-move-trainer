import { Collapsible } from "@base-ui/react/collapsible";
import { Chess, validateFen } from "chess.js";
import { Check } from "lucide-react";
import { Chessboard } from "react-chessboard";
import { ErrorBoundary } from "react-error-boundary";
import { createMemoryRouter, RouterProvider, useLocation } from "react-router-dom";
import styles from "./FoundationCheck.module.css";

const VALID_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const INVALID_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 99";

function ChessJsProof() {
  const validResult = validateFen(VALID_FEN);
  const invalidResult = validateFen(INVALID_FEN);

  let sideToMove = null;
  let pieceCount = null;
  if (validResult.ok) {
    const chess = new Chess(VALID_FEN);
    sideToMove = chess.turn();
    pieceCount = chess
      .board()
      .flat()
      .filter((square) => square !== null).length;
  }

  return (
    <section className={styles.chessJsProof}>
      <p className={styles.developmentLabel}>Development-only chess.js proof</p>
      <div className={styles.validResult}>
        <strong>Valid FEN validated</strong>
        <span>Side to move: {sideToMove}</span>
        <span>Board piece count: {pieceCount}</span>
      </div>
      <div className={styles.invalidResult}>
        <strong>Invalid FEN unavailable</strong>
        <code>{invalidResult.error}</code>
      </div>
    </section>
  );
}

function StaticBoardProof() {
  const validResult = validateFen(VALID_FEN);

  if (!validResult.ok) {
    return null;
  }

  return (
    <section className={styles.boardProof}>
      <p className={styles.developmentLabel}>Development-only static board proof</p>
      <div className={styles.boardProofBoard}>
        <Chessboard
          options={{
            position: VALID_FEN,
            allowDragging: false,
            allowDrawingArrows: false,
          }}
        />
      </div>
    </section>
  );
}

function DeliberateFailure(): never {
  throw new Error("Deliberate development-only render failure");
}

function ContainedFailureProof() {
  return (
    <section className={styles.boundaryProof}>
      <p className={styles.developmentLabel}>Development-only boundary proof</p>
      <ErrorBoundary
        fallback={
          <p className={styles.containedFailure}>
            Boundary contained the deliberate development-only render failure.
          </p>
        }
      >
        <DeliberateFailure />
      </ErrorBoundary>
    </section>
  );
}

function FoundationContent() {
  const location = useLocation();

  return (
    <main>
      <section className={styles.statusCard}>
        <p className={styles.developmentLabel}>Development-only Foundation Check</p>
        <h1>Shared CSS surface</h1>
        <p className={styles.globalProbe}>
          This card demonstrates the existing global <code>status-card</code> style.
        </p>
        <div className={styles.moduleProbe}>
          <strong>CSS Module probe</strong>
          <span>Scoped local presentation</span>
        </div>
        <p className={styles.globalProbe}>
          Router context probe: <code>{location.pathname}</code>
        </p>
      </section>
      <section className={styles.collapsibleProof}>
        <p className={styles.developmentLabel}>Development-only structural proof</p>
        <Collapsible.Root className={styles.collapsibleRoot}>
          <Collapsible.Trigger className={styles.collapsibleTrigger}>
            Toggle structural proof
          </Collapsible.Trigger>
          <Collapsible.Panel className={styles.collapsiblePanel} keepMounted>
            <p>Base UI Collapsible panel is visible when expanded.</p>
          </Collapsible.Panel>
        </Collapsible.Root>
      </section>
      <section>
        <p className={styles.developmentLabel}>Development-only icon proof</p>
        <button type="button" aria-label="Foundation icon proof">
          <Check aria-hidden="true" />
        </button>
      </section>
      <ChessJsProof />
      <StaticBoardProof />
      <ContainedFailureProof />
    </main>
  );
}

const router = createMemoryRouter([{ path: "/", element: <FoundationContent /> }], {
  initialEntries: ["/"],
});

export function FoundationCheck() {
  return <RouterProvider router={router} />;
}
