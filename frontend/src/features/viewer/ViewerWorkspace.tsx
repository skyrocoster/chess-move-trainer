import { useCallback, useRef, useState } from "react";

import { BoardAdapter, STARTING_FEN, type BoardOrientation } from "../board-adapter/BoardAdapter";
import { InteractiveBoardAdapter } from "../board-adapter/InteractiveBoardAdapter";
import { BoardControl } from "./BoardControl";
import { EvalBar } from "./EvalBar";
import { GameContext } from "./GameContext";
import { GameLoader, type GameLoaderStatus, type GameLoaderValues } from "./GameLoader";
import { defaultAnalysisClient, type AnalysisClient } from "./analysisApi";
import { useAnalysisState } from "./analysisState";
import type { Game } from "./gameModel";
import { fetchGame, type GameLookup } from "./positionApi";
import type { BranchSnapshot } from "./temporaryBranchModel";
import styles from "./ViewerWorkspace.module.css";

const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";

const START_BOARD = {
  fen: STARTING_FEN,
  orientation: "white" as BoardOrientation,
  label: BOARD_LABEL,
};

function announcementFor(game: Game, index: number): string {
  const position = game.positions[index];
  const finalPly = game.positions.at(-1)?.ply ?? 0;
  return `Ply ${position.ply} of ${finalPly}: ${position.san ?? "Initial position"}`;
}

export type ViewerWorkspaceProps = {
  lookup?: GameLookup;
  analysisClient?: AnalysisClient;
  analysisPollIntervalMs?: number;
};

export default function ViewerWorkspace({
  lookup = fetchGame,
  analysisClient = defaultAnalysisClient,
  analysisPollIntervalMs,
}: ViewerWorkspaceProps) {
  const [gameUuidInput, setGameUuidInput] = useState("");
  const [plyInput, setPlyInput] = useState("");
  const [status, setStatus] = useState<GameLoaderStatus>("idle");
  const [game, setGame] = useState<Game | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [announcement, setAnnouncement] = useState("");
  const [branchSnapshot, setBranchSnapshot] = useState<BranchSnapshot | null>(null);
  const [branchResetToken, setBranchResetToken] = useState(0);
  const requestId = useRef(0);
  const controller = useRef<AbortController | null>(null);

  const loading = status === "loading";
  const currentPosition = game?.positions[currentIndex];
  const finalPly = game?.positions.at(-1)?.ply;
  const viewKey = game && currentPosition ? `${game.game_uuid}:${currentPosition.ply}` : "empty";
  const branchForView =
    branchSnapshot?.viewKey === viewKey && branchSnapshot.resetToken === branchResetToken
      ? branchSnapshot
      : null;
  const analysisFen = branchForView?.currentFen ?? currentPosition?.fen ?? null;
  const analysisState = useAnalysisState(analysisFen, analysisClient, analysisPollIntervalMs);

  const handleBranchChange = useCallback((snapshot: BranchSnapshot) => {
    setBranchSnapshot(snapshot);
  }, []);

  function discardBranch() {
    setBranchSnapshot(null);
    setBranchResetToken((token) => token + 1);
  }

  function invalidateRequest() {
    requestId.current += 1;
    controller.current?.abort();
    controller.current = null;
  }

  function resetViewer() {
    discardBranch();
    invalidateRequest();
    setGameUuidInput("");
    setPlyInput("");
    setStatus("idle");
    setGame(null);
    setCurrentIndex(0);
    setAnnouncement("");
  }

  async function handleSubmit(values: GameLoaderValues) {
    discardBranch();
    invalidateRequest();
    const currentRequestId = requestId.current;
    const nextController = new AbortController();
    controller.current = nextController;
    setStatus("loading");

    const initialPly = values.ply === "" ? undefined : Number(values.ply);
    let result: Awaited<ReturnType<GameLookup>>;
    try {
      result = await lookup(values.gameUuid, initialPly, nextController.signal);
    } catch {
      if (nextController.signal.aborted || currentRequestId !== requestId.current) {
        return;
      }
      result = { status: "unexpected_failure" };
    }

    if (nextController.signal.aborted || currentRequestId !== requestId.current) {
      return;
    }
    if (controller.current === nextController) {
      controller.current = null;
    }

    if (result.status === "success") {
      const nextGame = result.game;
      const nextIndex = nextGame.positions.findIndex(
        (position) => position.ply === nextGame.initial_ply,
      );
      if (nextIndex < 0) {
        setStatus("unexpected_failure");
        return;
      }
      setGame(nextGame);
      setCurrentIndex(nextIndex);
      setStatus("idle");
      setAnnouncement(announcementFor(nextGame, nextIndex));
      return;
    }

    setStatus(result.status);
  }

  function handlePrevious() {
    if (branchForView?.active) {
      discardBranch();
      return;
    }
    if (!game || currentIndex === 0) {
      return;
    }
    const nextIndex = currentIndex - 1;
    setCurrentIndex(nextIndex);
    setAnnouncement(announcementFor(game, nextIndex));
  }

  function handleNext() {
    if (branchForView?.active) {
      discardBranch();
      return;
    }
    if (!game || currentIndex >= game.positions.length - 1) {
      return;
    }
    const nextIndex = currentIndex + 1;
    setCurrentIndex(nextIndex);
    setAnnouncement(announcementFor(game, nextIndex));
  }

  const boardFen = analysisFen ?? START_BOARD.fen;
  const boardOrientation = game?.subject_color ?? START_BOARD.orientation;
  const boardLabel =
    branchForView && currentPosition
      ? `Chess board: temporary branch from game ${game.game_uuid}, captured ply ${currentPosition.ply}, ${
          boardOrientation === "white" ? "White" : "Black"
        } at the bottom`
      : currentPosition
        ? `Chess board: game ${game.game_uuid}, ply ${currentPosition.ply}, ${
            boardOrientation === "white" ? "White" : "Black"
          } at the bottom`
        : START_BOARD.label;

  return (
    <div className={styles.viewer}>
      <div className={styles.workspace}>
        <h1 className={styles.heading}>Position viewer</h1>

        <div className={styles.loader}>
          <GameLoader
            status={status}
            gameUuid={gameUuidInput}
            ply={plyInput}
            onGameUuidChange={setGameUuidInput}
            onPlyChange={setPlyInput}
            onSubmit={handleSubmit}
            onReset={resetViewer}
          />
        </div>

        <div className={styles.board}>
          {game && currentPosition ? (
            <InteractiveBoardAdapter
              key={`${viewKey}:${branchResetToken}`}
              viewKey={viewKey}
              originFen={currentPosition.fen}
              originPly={currentPosition.ply}
              orientation={boardOrientation}
              label={boardLabel}
              resetToken={branchResetToken}
              onBranchChange={handleBranchChange}
            />
          ) : (
            <BoardAdapter
              key={`${boardFen}|${boardOrientation}`}
              fen={boardFen}
              orientation={boardOrientation}
              label={boardLabel}
            />
          )}
        </div>

        <div className={styles.evalBar}>
          <EvalBar orientation={boardOrientation} analysisState={analysisState} />
        </div>

        <div className={styles.controls}>
          <BoardControl
            currentPly={currentPosition?.ply}
            finalPly={finalPly}
            loading={loading}
            branchActive={branchForView?.active ?? false}
            onPrevious={handlePrevious}
            onNext={handleNext}
          />
        </div>

        <div className={styles.context}>
          <GameContext
            game={game}
            position={currentPosition}
            analysisClient={analysisClient}
            analysisPollIntervalMs={analysisPollIntervalMs}
            analysisState={analysisState}
            analysisFen={analysisFen ?? undefined}
          />
        </div>

        <p className={styles.announcement} role="status" aria-live="polite" aria-atomic="true">
          {announcement}
        </p>
      </div>
    </div>
  );
}
