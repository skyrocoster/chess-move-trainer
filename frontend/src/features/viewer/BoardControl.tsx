import { Toolbar } from "@base-ui/react/toolbar";
import { ChevronLeft, ChevronRight } from "lucide-react";

import styles from "./BoardControl.module.css";

export type BoardControlProps = {
  currentPly?: number;
  finalPly?: number;
  loading?: boolean;
  branchActive?: boolean;
  onPrevious?: () => void;
  onNext?: () => void;
};

export function BoardControl({
  currentPly,
  finalPly,
  loading = false,
  branchActive = false,
  onPrevious,
  onNext,
}: BoardControlProps) {
  const hasGame = currentPly !== undefined && finalPly !== undefined;
  const previousDisabled = loading || branchActive || !hasGame || currentPly === 0;
  const nextDisabled = loading || branchActive || !hasGame || currentPly === finalPly;

  return (
    <div className={styles.container}>
      {!hasGame ? <p className={styles.empty}>No game loaded</p> : null}
      <Toolbar.Root className={styles.toolbar} aria-label="Board controls">
        {/* Future skip controls: First/Last. */}
        <Toolbar.Button
          className={styles.button}
          type="button"
          disabled={previousDisabled}
          focusableWhenDisabled={false}
          onClick={onPrevious}
          aria-label="Previous"
        >
          <ChevronLeft aria-hidden="true" />
          <span className={styles.label}>Previous</span>
        </Toolbar.Button>
        {/* Future playback controls: Play/Pause. */}
        <Toolbar.Button
          className={styles.button}
          type="button"
          disabled={nextDisabled}
          focusableWhenDisabled={false}
          onClick={onNext}
          aria-label="Next"
        >
          <ChevronRight aria-hidden="true" />
          <span className={styles.label}>Next</span>
        </Toolbar.Button>
        {/* Future board control: Flip. */}
      </Toolbar.Root>
    </div>
  );
}
