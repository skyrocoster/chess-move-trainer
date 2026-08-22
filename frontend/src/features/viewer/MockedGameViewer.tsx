import { useState } from "react";

import { BoardAdapter, STARTING_FEN } from "../board-adapter/BoardAdapter";
import { BoardControl } from "./BoardControl";
import { GameContext } from "./GameContext";
import { GameLoader, type GameLoaderStatus, type GameLoaderValues } from "./GameLoader";
import {
  STAGE1_GAME,
  STAGE1_MISSING_SOURCE_GAME,
  STAGE1_UNSAFE_SOURCE_GAME,
  type Stage1FailureKind,
  type Stage1Game,
} from "./stage1GameTypes";
import styles from "./MockedGameViewer.module.css";

export type MockedViewerScenario =
  | "empty"
  | "loading"
  | "replacement_loading"
  | "initial"
  | "intermediate"
  | "final"
  | "black_subject"
  | "unsafe_source"
  | "missing_source"
  | "replacement_failure"
  | "game_not_found"
  | "position_not_found"
  | "corpus_unavailable"
  | "game_unavailable"
  | "unexpected_failure";

type MockedGameViewerProps = {
  scenario?: MockedViewerScenario;
};

const START_BOARD_LABEL = "Chess board: standard starting position, White at the bottom";
const FAILURE_SCENARIOS: Stage1FailureKind[] = [
  "game_not_found",
  "position_not_found",
  "corpus_unavailable",
  "game_unavailable",
  "unexpected_failure",
];

function scenarioGame(scenario: MockedViewerScenario): Stage1Game | null {
  if (
    scenario === "empty" ||
    scenario === "loading" ||
    FAILURE_SCENARIOS.includes(scenario as Stage1FailureKind)
  ) {
    return null;
  }
  if (scenario === "unsafe_source") {
    return STAGE1_UNSAFE_SOURCE_GAME;
  }
  if (scenario === "missing_source") {
    return STAGE1_MISSING_SOURCE_GAME;
  }
  if (scenario === "black_subject") {
    return { ...STAGE1_GAME, subject_color: "black" };
  }
  return STAGE1_GAME;
}

function scenarioStatus(scenario: MockedViewerScenario): GameLoaderStatus {
  if (scenario === "loading" || scenario === "replacement_loading") {
    return "loading";
  }
  if (scenario === "replacement_failure") {
    return "game_unavailable";
  }
  if (FAILURE_SCENARIOS.includes(scenario as Stage1FailureKind)) {
    return scenario as Stage1FailureKind;
  }
  return "idle";
}

function scenarioIndex(scenario: MockedViewerScenario): number {
  if (scenario === "initial") {
    return 0;
  }
  if (scenario === "final") {
    return STAGE1_GAME.positions.length - 1;
  }
  return 1;
}

function announcementFor(game: Stage1Game, index: number): string {
  const position = game.positions[index];
  return `Ply ${position.ply} of ${game.positions.at(-1)?.ply}: ${position.san ?? "Initial position"}`;
}

export function MockedGameViewer({ scenario = "empty" }: MockedGameViewerProps) {
  const [game, setGame] = useState<Stage1Game | null>(() => scenarioGame(scenario));
  const [currentIndex, setCurrentIndex] = useState(() => scenarioIndex(scenario));
  const [status, setStatus] = useState<GameLoaderStatus>(() => scenarioStatus(scenario));
  const [gameUuidInput, setGameUuidInput] = useState(
    scenario === "empty" ? "" : STAGE1_GAME.game_uuid,
  );
  const [plyInput, setPlyInput] = useState(
    game && scenario !== "initial" ? String(game.positions[currentIndex]?.ply ?? 0) : "",
  );
  const [announcement, setAnnouncement] = useState(() =>
    game ? announcementFor(game, currentIndex) : "",
  );

  const currentPosition = game?.positions[currentIndex];
  const loading = status === "loading";
  const finalPly = game?.positions.at(-1)?.ply;

  function handleSubmit(values: GameLoaderValues) {
    setStatus("loading");
    const requestedPly = values.ply === "" ? 0 : Number(values.ply);
    const nextGame = { ...STAGE1_GAME, initial_ply: requestedPly };
    const nextIndex = nextGame.positions.findIndex((position) => position.ply === requestedPly);

    if (
      scenario === "game_not_found" ||
      scenario === "position_not_found" ||
      scenario === "corpus_unavailable" ||
      scenario === "game_unavailable" ||
      scenario === "unexpected_failure" ||
      scenario === "replacement_failure"
    ) {
      const failure: Stage1FailureKind =
        scenario === "replacement_failure" ? "game_unavailable" : scenario;
      globalThis.setTimeout(() => setStatus(failure), 0);
      return;
    }

    if (nextIndex === -1) {
      globalThis.setTimeout(() => setStatus("position_not_found"), 0);
      return;
    }

    globalThis.setTimeout(() => {
      setGame(nextGame);
      setCurrentIndex(nextIndex);
      setStatus("idle");
      setAnnouncement(announcementFor(nextGame, nextIndex));
    }, 0);
  }

  function handleReset() {
    setGame(null);
    setCurrentIndex(0);
    setStatus("idle");
    setGameUuidInput("");
    setPlyInput("");
    setAnnouncement("");
  }

  function handlePrevious() {
    if (!game || currentIndex === 0) {
      return;
    }
    const nextIndex = currentIndex - 1;
    setCurrentIndex(nextIndex);
    setPlyInput(String(game.positions[nextIndex].ply));
    setAnnouncement(announcementFor(game, nextIndex));
  }

  function handleNext() {
    if (!game || currentIndex >= game.positions.length - 1) {
      return;
    }
    const nextIndex = currentIndex + 1;
    setCurrentIndex(nextIndex);
    setPlyInput(String(game.positions[nextIndex].ply));
    setAnnouncement(announcementFor(game, nextIndex));
  }

  const boardFen = currentPosition?.fen ?? STARTING_FEN;
  const boardOrientation = game?.subject_color ?? "white";
  const boardLabel = currentPosition
    ? `Chess board: game ${game.game_uuid}, ply ${currentPosition.ply}, ${
        boardOrientation === "white" ? "White" : "Black"
      } at the bottom`
    : START_BOARD_LABEL;

  return (
    <div className={styles.viewer}>
      <div className={styles.workspace}>
        <h1 className={styles.heading}>Complete-game traversal (mocked)</h1>
        <div className={styles.loader}>
          <GameLoader
            status={status}
            gameUuid={gameUuidInput}
            ply={plyInput}
            onGameUuidChange={setGameUuidInput}
            onPlyChange={setPlyInput}
            onSubmit={handleSubmit}
            onReset={handleReset}
          />
        </div>

        <div className={styles.board}>
          <BoardAdapter
            key={`${boardFen}|${boardOrientation}`}
            fen={boardFen}
            orientation={boardOrientation}
            label={boardLabel}
          />
        </div>

        <div className={styles.controls}>
          <BoardControl
            currentPly={currentPosition?.ply}
            finalPly={finalPly}
            loading={loading}
            onPrevious={handlePrevious}
            onNext={handleNext}
          />
        </div>

        <div className={styles.context}>
          <GameContext game={game} position={currentPosition} />
        </div>

        <p className={styles.announcement} role="status" aria-live="polite" aria-atomic="true">
          {announcement}
        </p>
      </div>
    </div>
  );
}
