import { Progress } from "@base-ui/react/progress";
import { Chess } from "chess.js";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import type { TrainingRequirementResponse } from "../../api/client";
import { InteractiveBoardHarness } from "../board-adapter/InteractiveBoardHarness";
import type { BoardAnswerPresentation } from "../board-adapter/answerPresentation";
import type { BranchSnapshot } from "../board-adapter/branchModel";
import { lastMoveFromSquares, type LastMove } from "../board-adapter/lastMove";
import { parseUciMove } from "../chess/chessPrimitives";
import { Button } from "../design-system/Button";
import { PanelFeedback } from "../design-system/feedback/PanelFeedback";
import type { TrainingAnswerInput, TrainingAnswerResult } from "./trainerPracticeApi";
import styles from "./TrainerSession.module.css";

type MoveDetails = {
  uci: string;
  san: string;
  squares: LastMove;
};

type SessionPhase =
  | { status: "awaiting" }
  | { status: "submitting"; played: MoveDetails }
  | {
      status: "resolved";
      played: MoveDetails;
      saved: MoveDetails;
      correct: boolean;
      correctAnswersNeeded: number;
    }
  | { status: "revealed"; saved: MoveDetails }
  | {
      status: "unconfirmed";
      played: MoveDetails;
      reason: Exclude<TrainingAnswerResult["status"], "success">;
    };

type SessionTotals = {
  answered: number;
  correct: number;
  reviewed: number;
  unconfirmed: number;
};

export type TrainerSessionProps = {
  data: TrainingRequirementResponse;
  scopeLabel: string;
  onSubmitAnswer: (
    input: TrainingAnswerInput,
    signal?: AbortSignal,
  ) => Promise<TrainingAnswerResult>;
  onRefreshRequirements: () => void;
};

function moveDetails(fen: string, uci: string): MoveDetails | null {
  try {
    const move = new Chess(fen).move(parseUciMove(uci));
    return { uci, san: move.san, squares: lastMoveFromSquares(move.from, move.to) };
  } catch {
    return null;
  }
}

function moveFromSnapshot(snapshot: BranchSnapshot): MoveDetails | null {
  const move = snapshot.moves[0];
  if (move === undefined || snapshot.moves.length !== 1) {
    return null;
  }
  return {
    uci: `${move.from}${move.to}${move.promotion ?? ""}`,
    san: move.san,
    squares: lastMoveFromSquares(move.from, move.to),
  };
}

function learnerLabel(color: "white" | "black") {
  return color === "white" ? "White" : "Black";
}

function sideToMove(fen: string) {
  return fen.split(" ")[1] === "b" ? "Black to move" : "White to move";
}

function failureMessage(reason: Exclude<TrainingAnswerResult["status"], "success">) {
  if (reason === "stale_date") {
    return "The training score changed after this session was loaded. Refresh the training set before answering this position again.";
  }
  if (reason === "requirement_not_found") {
    return "This position is no longer available for the selected training date. Refresh the training set to continue with current positions.";
  }
  return "The answer could not be confirmed. It will not be sent again automatically, so it cannot be counted twice.";
}

function answerPresentation(phase: SessionPhase): BoardAnswerPresentation {
  if (phase.status === "awaiting") {
    return { status: "awaiting-input", message: "Make one legal move on the board." };
  }
  if (phase.status === "submitting") {
    return {
      status: "disabled",
      attemptedMove: phase.played.squares,
      message: "Checking your move...",
    };
  }
  if (phase.status === "resolved") {
    return {
      status: phase.correct ? "correct" : "incorrect",
      attemptedMove: phase.played.squares,
      expectedMove: phase.correct ? null : phase.saved.squares,
      message: phase.correct
        ? "Correct. You found your saved move."
        : "That legal move does not match your saved move.",
    };
  }
  if (phase.status === "revealed") {
    return {
      status: "revealed",
      expectedMove: phase.saved.squares,
      message: "Your saved move is highlighted on the board.",
    };
  }
  return {
    status: "disabled",
    attemptedMove: phase.played.squares,
    message: "This answer could not be confirmed.",
  };
}

function SessionFeedback({
  phase,
  onReveal,
  onContinue,
}: {
  phase: SessionPhase;
  onReveal: () => void;
  onContinue: () => void;
}) {
  if (phase.status === "awaiting") {
    return (
      <div className={styles.feedbackCard}>
        <p className={styles.eyebrow}>Your turn</p>
        <h3>Find the move you saved</h3>
        <p>Play one legal move. The answer stays hidden until you commit or choose to reveal it.</p>
        <Button variant="ghost" onClick={onReveal}>
          Show saved move
        </Button>
      </div>
    );
  }
  if (phase.status === "submitting") {
    return (
      <PanelFeedback
        severity="information"
        heading="Checking your move"
        message="The board is locked while the backend records and judges this answer."
        role="status"
        aria-live="polite"
        aria-busy="true"
      />
    );
  }
  if (phase.status === "unconfirmed") {
    return (
      <div className={styles.feedbackStack}>
        <PanelFeedback
          severity="error"
          heading="Answer not confirmed"
          message={failureMessage(phase.reason)}
          role="alert"
        />
        <Button onClick={onContinue}>Continue</Button>
      </div>
    );
  }
  if (phase.status === "revealed") {
    return (
      <div className={styles.feedbackStack}>
        <PanelFeedback
          severity="information"
          heading="Saved move revealed"
          message={`Your saved move is ${phase.saved.san} (${phase.saved.uci}). This review does not change your training score.`}
          role="status"
          aria-live="polite"
        />
        <Button onClick={onContinue}>Continue</Button>
      </div>
    );
  }

  const remaining = phase.correctAnswersNeeded;
  return (
    <div className={styles.feedbackStack}>
      <PanelFeedback
        severity={phase.correct ? "success" : "warning"}
        heading={phase.correct ? "Saved move found" : "Different from your saved move"}
        message={
          phase.correct
            ? `You played ${phase.played.san}. The backend confirmed it matches your saved move.`
            : `You played ${phase.played.san}. Your saved move is ${phase.saved.san}.`
        }
        role="status"
        aria-live="polite"
      />
      <dl className={styles.answerComparison}>
        <div>
          <dt>You played</dt>
          <dd>
            {phase.played.san} <span>{phase.played.uci}</span>
          </dd>
        </div>
        <div>
          <dt>Saved move</dt>
          <dd>
            {phase.saved.san} <span>{phase.saved.uci}</span>
          </dd>
        </div>
      </dl>
      <p className={styles.scoreNote}>
        {remaining === 0
          ? "This position no longer needs training on the selected date."
          : `${remaining} more net correct ${remaining === 1 ? "answer" : "answers"} needed under the current score.`}
      </p>
      <Button onClick={onContinue}>Continue</Button>
    </div>
  );
}

export function TrainerSession({
  data,
  scopeLabel,
  onSubmitAnswer,
  onRefreshRequirements,
}: TrainerSessionProps) {
  const [positionIndex, setPositionIndex] = useState(0);
  const [phase, setPhase] = useState<SessionPhase>({ status: "awaiting" });
  const [complete, setComplete] = useState(false);
  const [totals, setTotals] = useState<SessionTotals>({
    answered: 0,
    correct: 0,
    reviewed: 0,
    unconfirmed: 0,
  });
  const requestControllerRef = useRef<AbortController | null>(null);
  const requestIdRef = useRef(0);
  const positions = useMemo(() => [...data.items], [data.items]);
  const activeItem = positions[positionIndex];
  const completedCount = totals.answered + totals.reviewed + totals.unconfirmed;

  useEffect(
    () => () => {
      requestIdRef.current += 1;
      requestControllerRef.current?.abort();
    },
    [],
  );

  const handleBranchChange = useCallback(
    (snapshot: BranchSnapshot) => {
      if (phase.status !== "awaiting" || activeItem === undefined) {
        return;
      }
      const played = moveFromSnapshot(snapshot);
      if (played === null) {
        return;
      }

      const id = requestIdRef.current + 1;
      requestIdRef.current = id;
      const controller = new AbortController();
      requestControllerRef.current = controller;
      setPhase({ status: "submitting", played });

      void onSubmitAnswer(
        {
          fen: activeItem.fen,
          trainerColor: activeItem.trainer_color,
          asOf: data.as_of,
          playedMoveUci: played.uci,
        },
        controller.signal,
      )
        .then((result) => {
          if (requestIdRef.current !== id || controller.signal.aborted) {
            return;
          }
          requestControllerRef.current = null;
          if (result.status !== "success") {
            setTotals((current) => ({ ...current, unconfirmed: current.unconfirmed + 1 }));
            setPhase({ status: "unconfirmed", played, reason: result.status });
            return;
          }

          const saved = moveDetails(activeItem.fen, result.data.item.preferred_move_uci);
          if (saved === null) {
            setTotals((current) => ({ ...current, unconfirmed: current.unconfirmed + 1 }));
            setPhase({ status: "unconfirmed", played, reason: "submission_error" });
            return;
          }
          setTotals((current) => ({
            ...current,
            answered: current.answered + 1,
            correct: current.correct + (result.data.correct ? 1 : 0),
          }));
          setPhase({
            status: "resolved",
            played,
            saved,
            correct: result.data.correct,
            correctAnswersNeeded: result.data.item.correct_answers_needed,
          });
        })
        .catch(() => {
          if (controller.signal.aborted || requestIdRef.current !== id) {
            return;
          }
          requestControllerRef.current = null;
          setTotals((current) => ({ ...current, unconfirmed: current.unconfirmed + 1 }));
          setPhase({ status: "unconfirmed", played, reason: "submission_error" });
        });
    },
    [activeItem, data.as_of, onSubmitAnswer, phase.status],
  );

  const handleReveal = useCallback(() => {
    if (activeItem === undefined || phase.status !== "awaiting") {
      return;
    }
    const saved = moveDetails(activeItem.fen, activeItem.preferred_move_uci);
    if (saved === null) {
      return;
    }
    setTotals((current) => ({ ...current, reviewed: current.reviewed + 1 }));
    setPhase({ status: "revealed", saved });
  }, [activeItem, phase.status]);

  const handleContinue = useCallback(() => {
    if (positionIndex + 1 >= positions.length) {
      setComplete(true);
      return;
    }
    setPositionIndex((current) => current + 1);
    setPhase({ status: "awaiting" });
  }, [positionIndex, positions.length]);

  if (complete || activeItem === undefined) {
    return (
      <section className={styles.complete} aria-labelledby="training-session-complete-heading">
        <p className={styles.eyebrow}>Session complete</p>
        <h2 id="training-session-complete-heading">Practice recorded</h2>
        <p>
          This summary describes this session only. It does not claim that a position is mastered.
        </p>
        <dl className={styles.summaryGrid}>
          <div>
            <dt>Completed</dt>
            <dd>
              {completedCount} / {positions.length}
            </dd>
          </div>
          <div>
            <dt>Correct first answers</dt>
            <dd>{totals.correct}</dd>
          </div>
          <div>
            <dt>Saved moves reviewed</dt>
            <dd>{totals.reviewed}</dd>
          </div>
          <div>
            <dt>Unconfirmed</dt>
            <dd>{totals.unconfirmed}</dd>
          </div>
        </dl>
        <Button onClick={onRefreshRequirements}>Practice updated set</Button>
      </section>
    );
  }

  const boardAnswer = answerPresentation(phase);
  const boardKey = `${activeItem.fen}:${activeItem.trainer_color}:${positionIndex}`;

  return (
    <section className={styles.session} aria-labelledby="training-session-heading">
      <header className={styles.sessionHeader}>
        <div>
          <p className={styles.eyebrow}>Practice session</p>
          <h2 id="training-session-heading">
            Position {positionIndex + 1} of {positions.length}
          </h2>
        </div>
        <p className={styles.scope}>
          {scopeLabel} · {data.as_of}
        </p>
      </header>

      <div className={styles.sessionLayout}>
        <div className={styles.boardColumn}>
          <div className={styles.positionPrompt}>
            <div>
              <span>{learnerLabel(activeItem.trainer_color)} repertoire</span>
              <strong>{sideToMove(activeItem.fen)}</strong>
            </div>
            <p>Read the position, then play the move you saved.</p>
          </div>
          <InteractiveBoardHarness
            key={boardKey}
            viewKey={boardKey}
            originFen={activeItem.fen}
            originPly={0}
            label={`Training position ${positionIndex + 1} of ${positions.length}`}
            orientation={activeItem.trainer_color}
            answer={boardAnswer}
            showBranchPanel={false}
            showRejectedMoveNotice
            onBranchChange={handleBranchChange}
          />
        </div>

        <aside className={styles.sessionRail} aria-label="Practice progress and feedback">
          <Progress.Root
            className={styles.progressCard}
            min={0}
            max={positions.length}
            value={completedCount}
          >
            <div className={styles.progressHeading}>
              <Progress.Label>Session progress</Progress.Label>
              <Progress.Value className={styles.progressValue}>
                {() => `${completedCount} / ${positions.length}`}
              </Progress.Value>
            </div>
            <Progress.Track className={styles.progressTrack}>
              <Progress.Indicator
                className={styles.progressIndicator}
                style={{ inlineSize: `${(completedCount / positions.length) * 100}%` }}
              />
            </Progress.Track>
            <dl className={styles.positionFacts}>
              <div>
                <dt>Game encounters</dt>
                <dd>{activeItem.encounters}</dd>
              </div>
              <div>
                <dt>Correct answers currently needed</dt>
                <dd>{activeItem.correct_answers_needed}</dd>
              </div>
            </dl>
          </Progress.Root>

          <SessionFeedback phase={phase} onReveal={handleReveal} onContinue={handleContinue} />

          {phase.status !== "submitting" ? (
            <Button variant="ghost" onClick={() => setComplete(true)}>
              End session
            </Button>
          ) : null}
        </aside>
      </div>
    </section>
  );
}
