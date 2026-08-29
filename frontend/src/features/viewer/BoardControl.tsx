import { Toolbar } from "@base-ui/react/toolbar";
import { ChevronLeft, ChevronRight, FlipHorizontal2 } from "lucide-react";

import styles from "./BoardControl.module.css";

export type BoardControlProps = {
  hasGame?: boolean;
  canGoPrevious?: boolean;
  canGoNext?: boolean;
  onPrevious?: () => void;
  onNext?: () => void;
  onFlip?: () => void;
};

export function BoardControl({
  hasGame = false,
  canGoPrevious = false,
  canGoNext = false,
  onPrevious,
  onNext,
  onFlip,
}: BoardControlProps) {
  const previousDisabled = !hasGame || !canGoPrevious;
  const nextDisabled = !hasGame || !canGoNext;

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
        <Toolbar.Button className={styles.button} type="button" onClick={onFlip} aria-label="Flip">
          <FlipHorizontal2 aria-hidden="true" />
          <span className={styles.label}>Flip</span>
        </Toolbar.Button>
      </Toolbar.Root>
    </div>
  );
}
