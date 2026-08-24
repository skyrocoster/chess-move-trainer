import { Disclosure } from "../design-system/Disclosure";
import { AnalysisPanel } from "./AnalysisPanel";
import type { AnalysisClient } from "./analysisApi";
import type { AnalysisState } from "./analysisState";
import type { Fen } from "./chessPrimitives";
import type { Game, GamePosition } from "./gameModel";
import { safeSourceUrl } from "./stage1SourceSafety";
import styles from "./GameContext.module.css";

export type GameContextProps = {
  game?: Game | null;
  position?: GamePosition;
  analysisClient?: AnalysisClient;
  analysisPollIntervalMs?: number;
  analysisState?: AnalysisState;
  analysisFen?: Fen;
};

function SourceAttribution({ sourceUrl }: { sourceUrl: string | null }) {
  const safeUrl = safeSourceUrl(sourceUrl);
  return safeUrl ? (
    <a href={safeUrl} target="_blank" rel="noopener noreferrer">
      Chess.com game
    </a>
  ) : (
    <span>Source unavailable</span>
  );
}

export function GameContext({
  game,
  position,
  analysisClient,
  analysisPollIntervalMs,
  analysisState,
  analysisFen,
}: GameContextProps) {
  const currentPosition = game && position ? position : null;
  const finalPly = game?.positions.at(-1)?.ply;

  return (
    <Disclosure summary="Game Context" defaultOpen>
      <div className={styles.panel}>
        {!game || !currentPosition || finalPly === undefined ? (
          <p className={styles.empty}>No game loaded</p>
        ) : (
          <>
            <dl className={styles.details}>
              <div>
                <dt>Ply</dt>
                <dd>
                  Ply {currentPosition.ply} of {finalPly}
                </dd>
              </div>
              <div>
                <dt>Last move</dt>
                <dd>{currentPosition.san ?? "Initial position"}</dd>
              </div>
              <div>
                <dt>Source</dt>
                <dd>
                  <SourceAttribution sourceUrl={game.source_url} />
                </dd>
              </div>
            </dl>
            {analysisClient ? (
              <AnalysisPanel
                fen={analysisFen ?? currentPosition.fen}
                client={analysisClient}
                pollIntervalMs={analysisPollIntervalMs}
                analysisState={analysisState}
              />
            ) : null}
          </>
        )}
      </div>
    </Disclosure>
  );
}
