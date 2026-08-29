import { Drawer } from "@base-ui/react/drawer";
import { Popover } from "@base-ui/react/popover";
import { Chess, type Move, type Square } from "chess.js";
import { useCallback, useEffect, useRef, useState, type RefObject } from "react";

import { strictFen } from "../viewer/chessPrimitives";
import styles from "./PromotionPicker.module.css";

export type PromotionPiece = "q" | "r" | "b" | "n";
export type PromotionColor = "w" | "b";
export type PromotionPresentation = "auto" | "popover" | "drawer";

export type PendingPromotion = {
  sourceSquare: Square;
  targetSquare: Square;
};

export type PromotionCommit = {
  move: Move;
  fen: string;
  history: string[];
};

type PromotionRejection = "illegal" | "stale";

type PromotionControllerOptions = {
  chess: Chess;
  onCommit?: (commit: PromotionCommit) => void;
  onReject?: (reason: PromotionRejection) => void;
};

type PromotionController = {
  pending: PendingPromotion | null;
  sourceElement: HTMLElement | null;
  anchorElement: HTMLElement | null;
  requestPromotion: (
    sourceSquare: Square,
    targetSquare: Square,
    sourceElement: HTMLElement | null,
    anchorElement?: HTMLElement | null,
  ) => boolean;
  selectPromotion: (promotion: PromotionPiece) => boolean;
  cancelPromotion: () => void;
};

const PROMOTION_OPTIONS: Array<{
  piece: PromotionPiece;
  name: string;
  glyph: Record<PromotionColor, string>;
}> = [
  { piece: "q", name: "queen", glyph: { w: "♕", b: "♛" } },
  { piece: "r", name: "rook", glyph: { w: "♖", b: "♜" } },
  { piece: "b", name: "bishop", glyph: { w: "♗", b: "♝" } },
  { piece: "n", name: "knight", glyph: { w: "♘", b: "♞" } },
];

// eslint-disable-next-line react-refresh/only-export-components
export function isPromotionTarget(pieceColor: PromotionColor, square: Square) {
  return pieceColor === "w" ? square.endsWith("8") : square.endsWith("1");
}

function isPromotionCandidate(chess: Chess, sourceSquare: Square, targetSquare: Square) {
  const piece = chess.get(sourceSquare);
  if (!piece || piece.type !== "p" || !isPromotionTarget(piece.color, targetSquare)) {
    return false;
  }

  return chess
    .moves({ square: sourceSquare, verbose: true })
    .some((move) => move.to === targetSquare && move.isPromotion());
}

function clearPending(
  setPending: (pending: PendingPromotion | null) => void,
  positionTokenRef: { current: string | null },
) {
  setPending(null);
  positionTokenRef.current = null;
}

// eslint-disable-next-line react-refresh/only-export-components
export function usePromotionController({
  chess,
  onCommit,
  onReject,
}: PromotionControllerOptions): PromotionController {
  const [pending, setPending] = useState<PendingPromotion | null>(null);
  const positionTokenRef = useRef<string | null>(null);
  const sourceElementRef = useRef<HTMLElement | null>(null);
  const anchorElementRef = useRef<HTMLElement | null>(null);

  const requestPromotion = useCallback(
    (
      sourceSquare: Square,
      targetSquare: Square,
      sourceElement: HTMLElement | null,
      anchorElement = sourceElement,
    ) => {
      if (!isPromotionCandidate(chess, sourceSquare, targetSquare)) {
        return false;
      }

      positionTokenRef.current = chess.fen();
      sourceElementRef.current = sourceElement;
      anchorElementRef.current = anchorElement;
      setPending({ sourceSquare, targetSquare });
      return true;
    },
    [chess],
  );

  const cancelPromotion = useCallback(() => {
    if (!pending) {
      return;
    }

    clearPending(setPending, positionTokenRef);
  }, [pending]);

  const selectPromotion = useCallback(
    (promotion: PromotionPiece) => {
      if (!pending || positionTokenRef.current !== chess.fen()) {
        if (pending) {
          onReject?.("stale");
          clearPending(setPending, positionTokenRef);
        }
        return false;
      }

      const { sourceSquare, targetSquare } = pending;
      const trial = new Chess(chess.fen());
      let trialMove: Move;
      try {
        trialMove = trial.move({ from: sourceSquare, to: targetSquare, promotion });
      } catch {
        onReject?.("illegal");
        clearPending(setPending, positionTokenRef);
        return false;
      }

      if (!trialMove.isPromotion()) {
        onReject?.("illegal");
        clearPending(setPending, positionTokenRef);
        return false;
      }

      let move: Move;
      try {
        move = chess.move({ from: sourceSquare, to: targetSquare, promotion });
      } catch {
        onReject?.("stale");
        clearPending(setPending, positionTokenRef);
        return false;
      }

      const commit = {
        move,
        fen: strictFen(chess),
        history: chess.history(),
      };
      clearPending(setPending, positionTokenRef);
      onCommit?.(commit);
      return true;
    },
    [chess, onCommit, onReject, pending],
  );

  return {
    pending,
    sourceElement: sourceElementRef.current,
    anchorElement: anchorElementRef.current,
    requestPromotion,
    selectPromotion,
    cancelPromotion,
  };
}

type PromotionPickerProps = {
  pending: PendingPromotion | null;
  color: PromotionColor;
  sourceElement: HTMLElement | null;
  anchorElement?: HTMLElement | null;
  presentation?: PromotionPresentation;
  onSelect: (promotion: PromotionPiece) => void;
  onCancel: () => void;
};

function useConstrainedPresentation(presentation: PromotionPresentation) {
  const [constrained, setConstrained] = useState(false);

  useEffect(() => {
    if (
      presentation !== "auto" ||
      typeof window === "undefined" ||
      typeof window.matchMedia !== "function"
    ) {
      return;
    }

    const media = window.matchMedia("(max-width: 679px)");
    const update = () => setConstrained(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, [presentation]);

  return presentation === "drawer" || (presentation === "auto" && constrained);
}

function promotionDescription(pending: PendingPromotion, color: PromotionColor) {
  const side = color === "w" ? "White" : "Black";
  return `${side} pawn from ${pending.sourceSquare} to ${pending.targetSquare}. Choose a promotion piece.`;
}

function PromotionChoices({
  color,
  firstButtonRef,
  onSelect,
}: {
  color: PromotionColor;
  firstButtonRef: RefObject<HTMLButtonElement | null>;
  onSelect: (promotion: PromotionPiece) => void;
}) {
  return (
    <div className={styles.choices} role="group" aria-label="Promotion pieces">
      {PROMOTION_OPTIONS.map(({ piece, name, glyph }, index) => (
        <button
          key={piece}
          ref={index === 0 ? firstButtonRef : undefined}
          className={styles.choice}
          type="button"
          aria-label={`Promote to ${name}`}
          onClick={() => onSelect(piece)}
        >
          <span className={styles.glyph} aria-hidden="true">
            {glyph[color]}
          </span>
          <span className={styles.choiceName}>{name}</span>
        </button>
      ))}
    </div>
  );
}

function PickerLiveRegion({ pending, color }: Pick<PromotionPickerProps, "pending" | "color">) {
  if (!pending) {
    return null;
  }

  return (
    <p className={styles.liveRegion} role="status" aria-live="polite" aria-atomic="true">
      {promotionDescription(pending, color)}
    </p>
  );
}

export function PromotionPicker({
  pending,
  color,
  sourceElement,
  anchorElement,
  presentation = "auto",
  onSelect,
  onCancel,
}: PromotionPickerProps) {
  const isDrawer = useConstrainedPresentation(presentation);
  const firstButtonRef = useRef<HTMLButtonElement | null>(null);
  const finalFocusRef = useRef<HTMLElement | null>(null);
  finalFocusRef.current = sourceElement;

  useEffect(() => {
    if (!pending) {
      return;
    }

    const focusTimer = window.setTimeout(() => firstButtonRef.current?.focus(), 0);
    return () => window.clearTimeout(focusTimer);
  }, [pending]);

  if (!pending || !sourceElement) {
    return null;
  }

  const description = promotionDescription(pending, color);
  const cancelAndRestoreFocus = () => {
    const focusTarget = sourceElement;
    onCancel();
    queueMicrotask(() => focusTarget.focus());
  };

  if (isDrawer) {
    return (
      <Drawer.Root
        open
        modal
        swipeDirection="down"
        onOpenChange={(open) => {
          if (!open) {
            cancelAndRestoreFocus();
          }
        }}
      >
        <Drawer.Portal>
          <Drawer.Backdrop
            className={styles.drawerBackdrop}
            data-testid="promotion-drawer-backdrop"
          />
          <Drawer.Viewport className={styles.drawerViewport}>
            <Drawer.Popup
              className={styles.drawerPopup}
              initialFocus={firstButtonRef}
              finalFocus={finalFocusRef}
              data-testid="promotion-drawer"
            >
              <Drawer.Content className={styles.content}>
                <Drawer.Title className={styles.title}>Choose a promotion piece</Drawer.Title>
                <p className={styles.description}>{description}</p>
                <Drawer.Close className={styles.visuallyHidden} aria-label="Cancel promotion" />
                <PromotionChoices
                  color={color}
                  firstButtonRef={firstButtonRef}
                  onSelect={onSelect}
                />
                <PickerLiveRegion pending={pending} color={color} />
              </Drawer.Content>
            </Drawer.Popup>
          </Drawer.Viewport>
        </Drawer.Portal>
      </Drawer.Root>
    );
  }

  return (
    <Popover.Root
      open
      modal
      onOpenChange={(open) => {
        if (!open) {
          cancelAndRestoreFocus();
        }
      }}
    >
      <Popover.Portal>
        <Popover.Backdrop
          className={styles.popoverBackdrop}
          data-testid="promotion-popover-backdrop"
        />
        <Popover.Positioner
          className={styles.popoverPositioner}
          anchor={anchorElement ?? sourceElement}
          side="top"
          align="center"
          sideOffset={8}
        >
          <Popover.Popup
            className={styles.popoverPopup}
            initialFocus={firstButtonRef}
            finalFocus={finalFocusRef}
            data-testid="promotion-popover"
          >
            <Popover.Title className={styles.title}>Choose a promotion piece</Popover.Title>
            <Popover.Description className={styles.description}>{description}</Popover.Description>
            <Popover.Close className={styles.visuallyHidden} aria-label="Cancel promotion" />
            <PromotionChoices color={color} firstButtonRef={firstButtonRef} onSelect={onSelect} />
            <PickerLiveRegion pending={pending} color={color} />
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  );
}
