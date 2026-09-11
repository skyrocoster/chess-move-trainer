import { Chess } from "chess.js";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  InteractiveBoardAdapter,
  type InteractiveBoardMoveIntent,
} from "./InteractiveBoardAdapter";
import {
  isPromotionTarget,
  type PromotionColor,
  type PromotionCommit,
  usePromotionController,
} from "./PromotionPicker";
import type { BranchSnapshot } from "./branchModel";
import { lastMoveFromSquares } from "./lastMove";

export type InteractiveBoardHarnessProps = {
  viewKey: string;
  originFen: string;
  originPly: number;
  label: string;
  onBranchChange?: (snapshot: BranchSnapshot) => void;
};

function terminalDescription(chess: Chess) {
  if (chess.isCheckmate()) {
    return "Checkmate";
  }
  if (chess.isStalemate()) {
    return "Stalemate";
  }
  if (chess.isInsufficientMaterial()) {
    return "Draw by insufficient material";
  }
  if (chess.isDrawByFiftyMoves()) {
    return "Draw by fifty-move rule";
  }
  return null;
}

export function InteractiveBoardHarness({
  viewKey,
  originFen,
  originPly,
  label,
  onBranchChange,
}: InteractiveBoardHarnessProps) {
  const chess = useMemo(() => new Chess(originFen), [originFen]);
  const [branchSnapshot, setBranchSnapshot] = useState<BranchSnapshot>(() => ({
    viewKey,
    resetToken: 0,
    originFen,
    currentFen: originFen,
    originPly,
    moves: [],
    active: false,
  }));
  const [notice, setNotice] = useState("Make a legal move to start a temporary branch.");
  const [promotionColor, setPromotionColor] = useState<PromotionColor>(chess.turn());

  const createSnapshot = useCallback(
    (active: boolean): BranchSnapshot => ({
      viewKey,
      resetToken: 0,
      originFen,
      currentFen: chess.fen(),
      originPly,
      moves: chess.history({ verbose: true }).map((move) => ({
        color: move.color,
        from: move.from,
        to: move.to,
        san: move.san,
        ...(move.promotion ? { promotion: move.promotion } : {}),
      })),
      active,
    }),
    [chess, originFen, originPly, viewKey],
  );

  useEffect(() => {
    onBranchChange?.(branchSnapshot);
  }, [branchSnapshot, onBranchChange]);

  const handleCommit = useCallback(
    (commit: PromotionCommit) => {
      setBranchSnapshot(createSnapshot(true));
      setPromotionColor(chess.turn());
      setNotice(`Branch move committed: ${commit.move.san}.`);
    },
    [chess, createSnapshot],
  );

  const handleReject = useCallback(
    (reason: "illegal" | "stale") => {
      setBranchSnapshot(createSnapshot(chess.history().length > 0));
      setPromotionColor(chess.turn());
      setNotice(
        reason === "stale"
          ? "Promotion rejected because the displayed branch position is stale."
          : "Promotion rejected because the move is illegal.",
      );
    },
    [chess, createSnapshot],
  );

  const controller = usePromotionController({
    chess,
    onCommit: handleCommit,
    onReject: handleReject,
  });
  const {
    pending,
    sourceElement,
    anchorElement,
    requestPromotion,
    selectPromotion,
    cancelPromotion,
  } = controller;

  const handleMoveIntent = useCallback(
    (intent: InteractiveBoardMoveIntent) => {
      const piece = chess.get(intent.sourceSquare);
      if (piece?.type === "p" && isPromotionTarget(piece.color, intent.targetSquare)) {
        const opened = requestPromotion(
          intent.sourceSquare,
          intent.targetSquare,
          intent.sourceElement,
          intent.anchorElement,
        );
        if (opened) {
          setBranchSnapshot(createSnapshot(true));
          setPromotionColor(piece.color);
          setNotice("Choose a promotion piece for the temporary branch.");
        }
        return false;
      }

      try {
        const move = chess.move({ from: intent.sourceSquare, to: intent.targetSquare });
        setBranchSnapshot(createSnapshot(true));
        setNotice(`Branch move committed: ${move.san}.`);
        return true;
      } catch {
        setNotice("Move rejected because it is illegal.");
        return false;
      }
    },
    [chess, createSnapshot, requestPromotion],
  );

  const handlePromotionCancel = useCallback(() => {
    cancelPromotion();
    setBranchSnapshot(createSnapshot(chess.history().length > 0));
    setPromotionColor(chess.turn());
    setNotice("Promotion cancelled; the captured position is unchanged.");
  }, [cancelPromotion, chess, createSnapshot]);

  const handleUndo = useCallback(() => {
    cancelPromotion();
    if (!chess.undo()) {
      return;
    }
    setBranchSnapshot(createSnapshot(chess.history().length > 0));
    setPromotionColor(chess.turn());
    setNotice("Undid the latest temporary branch move.");
  }, [cancelPromotion, chess, createSnapshot]);

  const handleReset = useCallback(() => {
    cancelPromotion();
    chess.load(originFen);
    setBranchSnapshot(createSnapshot(false));
    setPromotionColor(chess.turn());
    setNotice("Temporary branch reset to its captured-game ply.");
  }, [cancelPromotion, chess, createSnapshot, originFen]);

  return (
    <InteractiveBoardAdapter
      branchSnapshot={branchSnapshot}
      lastMove={
        branchSnapshot.moves.at(-1)
          ? lastMoveFromSquares(branchSnapshot.moves.at(-1)!.from, branchSnapshot.moves.at(-1)!.to)
          : null
      }
      label={label}
      notice={notice}
      terminal={terminalDescription(chess)}
      promotionPending={pending}
      promotionColor={promotionColor}
      promotionSourceElement={sourceElement}
      promotionAnchorElement={anchorElement}
      onMoveIntent={handleMoveIntent}
      onPromotionSelect={selectPromotion}
      onPromotionCancel={handlePromotionCancel}
      onUndo={handleUndo}
      onReset={handleReset}
    />
  );
}
