import { useId, useLayoutEffect, useRef } from "react";
import { validateFen } from "chess.js";
import { Chessboard } from "react-chessboard";
import { ErrorBoundary } from "react-error-boundary";

import { PanelFeedback } from "../design-system/feedback/PanelFeedback";
import styles from "./BoardAdapter.module.css";
import { PositionDescription } from "./PositionDescription";
import {
  createPositionModel,
  type BoardOrientation,
  type PositionModel,
} from "./positionDescriptionModel";

export type { BoardOrientation } from "./PositionDescription";

export type BoardAdapterProps = {
  fen: string;
  orientation?: BoardOrientation;
  showCoordinates?: boolean;
  label: string;
};

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function UnavailablePosition() {
  return (
    <div className={styles.unavailable} role="status">
      <PanelFeedback
        severity="error"
        heading="Position unavailable"
        message="This position could not be displayed. Provide a changed safe FEN to try again."
      />
    </div>
  );
}

const PACKAGE_SEMANTIC_ATTRIBUTES = [
  "role",
  "aria-roledescription",
  "tabindex",
  "aria-describedby",
  "aria-disabled",
  "aria-pressed",
  "aria-live",
  "aria-atomic",
];

const PACKAGE_SEMANTIC_SELECTOR = PACKAGE_SEMANTIC_ATTRIBUTES.map(
  (attribute) => `[${attribute}]`,
).join(", ");

function stripPackageSemantics(node: Element) {
  PACKAGE_SEMANTIC_ATTRIBUTES.forEach((attribute) => node.removeAttribute(attribute));
}

function BoardRender({
  model,
  label,
  showCoordinates,
}: { model: PositionModel } & Pick<BoardAdapterProps, "label" | "showCoordinates">) {
  const descriptionId = `board-position-description-${useId().replace(/:/g, "")}`;
  const packageBoardRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const packageBoard = packageBoardRef.current;
    if (!packageBoard) {
      return;
    }

    packageBoard
      .querySelectorAll<HTMLElement>(PACKAGE_SEMANTIC_SELECTOR)
      .forEach(stripPackageSemantics);

    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === "attributes" && mutation.target instanceof Element) {
          stripPackageSemantics(mutation.target);
        }
        mutation.addedNodes.forEach((node) => {
          if (node instanceof Element) {
            stripPackageSemantics(node);
            node
              .querySelectorAll<HTMLElement>(PACKAGE_SEMANTIC_SELECTOR)
              .forEach(stripPackageSemantics);
          }
        });
      });
    });

    observer.observe(packageBoard, {
      subtree: true,
      childList: true,
      attributes: true,
      attributeFilter: PACKAGE_SEMANTIC_ATTRIBUTES,
    });

    return () => observer.disconnect();
  }, [model.fen, model.orientation]);

  return (
    <div className={styles.adapter}>
      <div
        className={styles.boardGraphic}
        data-board-visual
        role="img"
        aria-label={label}
        aria-describedby={descriptionId}
      >
        <div ref={packageBoardRef} className={styles.packageBoard} aria-hidden="true" inert>
          <Chessboard
            options={{
              allowDragging: false,
              allowDrawingArrows: false,
              boardOrientation: model.orientation,
              position: model.fen,
              showNotation: showCoordinates,
            }}
          />
        </div>
      </div>
      <p
        className={styles.assistiveDescription}
        id={descriptionId}
        role="status"
        aria-live="polite"
        aria-atomic="true"
      >
        {model.description}
      </p>
      <PositionDescription model={model} />
    </div>
  );
}

function BoardFailureFallback() {
  return <UnavailablePosition />;
}

export function BoardAdapter({
  fen,
  orientation = "white",
  showCoordinates = true,
  label,
}: BoardAdapterProps) {
  if (!label.trim()) {
    return <UnavailablePosition />;
  }

  const validation = validateFen(fen);
  if (!validation.ok) {
    return <UnavailablePosition />;
  }

  let model: PositionModel;
  try {
    model = createPositionModel(fen, orientation);
  } catch {
    return <UnavailablePosition />;
  }

  return (
    <ErrorBoundary FallbackComponent={BoardFailureFallback}>
      <BoardRender model={model} label={label} showCoordinates={showCoordinates} />
    </ErrorBoundary>
  );
}

// Exported for Storybook fixtures only; moving it to a separate file would
// create an unauthorized new source path.
// eslint-disable-next-line react-refresh/only-export-components
export { STARTING_FEN };
