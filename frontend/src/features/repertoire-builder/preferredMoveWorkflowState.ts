import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type Dispatch,
  type SetStateAction,
} from "react";

import { type CalendarDateValue } from "../design-system/CalendarDate";
import { normalizeToUtcMidnight } from "../design-system/CalendarDateUtils";
import type { ChessSide } from "../viewer/chessPrimitives";
import {
  type PositionContextClient,
  type PositionContextResponse,
  fetchPositionContext,
} from "../viewer/positionContextApi";
import { usePositionContextState } from "../viewer/positionContextState";
import {
  defaultPreferredMoveClient,
  type PreferredMoveClient,
  type PreferredMoveFailureCode,
} from "./preferredMoveApi";
import { usePreferredMoveState } from "./preferredMoveState";
import {
  beginPreferredMoveDraft,
  cancelPreferredMoveDraft,
  deriveRepertoirePositionModel,
  emptyPreferredMoveDraft,
  stagePreferredMoveDraft,
  type PreferredMoveDraftState,
} from "./repertoireWorkflowModel";
import {
  appendPositionPickerMove,
  selectPositionPickerPly,
  type PositionPickerMove,
  type PositionPickerSession,
} from "./positionPickerSession";
import type { PreferredMoveMutationKind } from "./PreferredMovePanel";

type WorkflowArgs = {
  session: PositionPickerSession;
  sideToMove: ChessSide;
  preferredMoveClient?: PreferredMoveClient;
  positionContextClient?: PositionContextClient;
  setSession: Dispatch<SetStateAction<PositionPickerSession>>;
  setSessionStatus: Dispatch<SetStateAction<string>>;
};

type PlayedMoveFocus = {
  move: PositionPickerSession["stagedMove"];
  preferredMove: ReturnType<typeof usePreferredMoveState>["preferredMove"];
};

export type PreferredMoveWorkflowState = {
  positionModel: ReturnType<typeof deriveRepertoirePositionModel>;
  positionContext: PositionContextResponse | null;
  preferredLoading: boolean;
  preferredError: ReturnType<typeof usePreferredMoveState>["error"];
  contextLoading: boolean;
  contextError: ReturnType<typeof usePositionContextState>["error"];
  stagedMove: PositionPickerSession["stagedMove"];
  draftMode: PreferredMoveDraftState["mode"];
  date: CalendarDateValue;
  mutation: PreferredMoveMutationKind | null;
  workflowError: PreferredMoveFailureCode | null;
  onDateChange: (value: CalendarDateValue) => void;
  onStagedMove: (move: PositionPickerSession["stagedMove"]) => void;
  onAdd: () => void;
  onEdit: () => void;
  onSave: () => void;
  onCancelEdit: () => void;
  onPlaySavedMove: () => void;
  onRemove: () => void;
  reset: () => void;
};

function moveFromUci(uci: string): PositionPickerMove | null {
  if (!/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(uci)) {
    return null;
  }

  const promotion = uci.slice(4);
  return {
    sourceSquare: uci.slice(0, 2) as PositionPickerMove["sourceSquare"],
    targetSquare: uci.slice(2, 4) as PositionPickerMove["targetSquare"],
    ...(promotion ? { promotion: promotion as NonNullable<PositionPickerMove["promotion"]> } : {}),
  };
}

export function usePreferredMoveWorkflow({
  session,
  sideToMove,
  preferredMoveClient = defaultPreferredMoveClient,
  positionContextClient = fetchPositionContext,
  setSession,
  setSessionStatus,
}: WorkflowArgs): PreferredMoveWorkflowState {
  const [refreshToken, setRefreshToken] = useState(0);
  const [draft, setDraft] = useState<PreferredMoveDraftState>(emptyPreferredMoveDraft);
  const [explicitDate, setExplicitDate] = useState<CalendarDateValue>(null);
  const [hasExplicitDate, setHasExplicitDate] = useState(false);
  const [mutation, setMutation] = useState<PreferredMoveMutationKind | null>(null);
  const [workflowError, setWorkflowError] = useState<PreferredMoveFailureCode | null>(null);
  const [playedMoveFocus, setPlayedMoveFocus] = useState<PlayedMoveFocus | null>(null);
  const [pendingEditPositionFen, setPendingEditPositionFen] = useState<string | null>(null);
  const mutationId = useRef(0);
  const mutationController = useRef<AbortController | null>(null);
  const preferredReader = useCallback(
    (fen: string, options?: { asOf?: string; signal?: AbortSignal }) => {
      void refreshToken;
      return preferredMoveClient.get(fen, options);
    },
    [preferredMoveClient, refreshToken],
  );
  const contextReader = useCallback(
    (fen: string, signal?: AbortSignal) => {
      void refreshToken;
      return positionContextClient(fen, signal);
    },
    [positionContextClient, refreshToken],
  );
  const preferredState = usePreferredMoveState(session.currentPosition.fen, preferredReader);
  const contextState = usePositionContextState(session.currentPosition.fen, contextReader);
  const positionModel = useMemo(
    () =>
      deriveRepertoirePositionModel({
        context: contextState.context,
        preferredMove: preferredState.preferredMove,
        sideToMove,
        bottomColor: session.bottomColor,
        lastPlayedMove: playedMoveFocus?.move,
        lastPlayedPreferredMove: playedMoveFocus?.preferredMove,
      }),
    [
      contextState.context,
      playedMoveFocus,
      preferredState.preferredMove,
      session.bottomColor,
      sideToMove,
    ],
  );

  const resetPositionState = useCallback(() => {
    mutationId.current += 1;
    mutationController.current?.abort();
    mutationController.current = null;
    setMutation(null);
    setWorkflowError(null);
    setDraft(cancelPreferredMoveDraft());
    setExplicitDate(null);
    setHasExplicitDate(false);
  }, []);

  const reset = useCallback(() => {
    setPendingEditPositionFen(null);
    resetPositionState();
    setPlayedMoveFocus(null);
  }, [resetPositionState]);

  useEffect(() => {
    resetPositionState();
  }, [resetPositionState, session.currentPosition.fen, session.bottomColor]);

  useEffect(() => {
    if (
      pendingEditPositionFen === null ||
      session.currentPosition.fen !== pendingEditPositionFen ||
      preferredState.loading ||
      preferredState.error !== null ||
      preferredState.preferredMove?.state !== "assigned"
    ) {
      return;
    }

    setDraft(beginPreferredMoveDraft("edit"));
    setPendingEditPositionFen(null);
  }, [
    pendingEditPositionFen,
    preferredState.error,
    preferredState.loading,
    preferredState.preferredMove,
    session.currentPosition.fen,
  ]);

  const persistedDate = useMemo(() => {
    if (!positionModel.effectiveAt) {
      return null;
    }
    const parsed = new Date(positionModel.effectiveAt);
    return Number.isNaN(parsed.getTime()) ? null : normalizeToUtcMidnight(parsed);
  }, [positionModel.effectiveAt]);
  const date = hasExplicitDate ? explicitDate : persistedDate;

  const onStagedMove = useCallback(
    (move: PositionPickerSession["stagedMove"]) => {
      if (!move) {
        return;
      }
      if (move.color === session.bottomColor) {
        setPlayedMoveFocus({ move, preferredMove: preferredState.preferredMove });
      }
      setDraft((current) => {
        if (current.mode !== "idle") {
          return stagePreferredMoveDraft(current, move, session.bottomColor) ?? current;
        }
        if (
          positionModel.saveability === "savable" &&
          preferredState.preferredMove?.state === "unassigned"
        ) {
          return (
            stagePreferredMoveDraft(beginPreferredMoveDraft("add"), move, session.bottomColor) ??
            current
          );
        }
        return current;
      });
    },
    [positionModel.saveability, preferredState.preferredMove, session.bottomColor],
  );

  const onEdit = useCallback(() => {
    if (positionModel.savedMove) {
      const next = beginPreferredMoveDraft("edit");
      setDraft(
        session.stagedMove
          ? (stagePreferredMoveDraft(next, session.stagedMove, session.bottomColor) ?? next)
          : next,
      );
      setWorkflowError(null);
      return;
    }

    const focusedMove = playedMoveFocus?.move;
    const focusedPreferredMove = playedMoveFocus?.preferredMove;
    if (
      positionModel.state !== "matching-played" ||
      !focusedMove ||
      focusedPreferredMove?.state !== "assigned"
    ) {
      return;
    }

    setPendingEditPositionFen(focusedPreferredMove.fen);
    setPlayedMoveFocus(null);
    setSession(
      (current) => selectPositionPickerPly(current, focusedMove.position.ply - 1) ?? current,
    );
    setWorkflowError(null);
  }, [playedMoveFocus, positionModel.savedMove, positionModel.state, session, setSession]);

  const onCancelEdit = useCallback(() => {
    setPendingEditPositionFen(null);
    setDraft(cancelPreferredMoveDraft());
    setPlayedMoveFocus(null);
    setSession((current) => ({ ...current, stagedMove: null }));
  }, [setSession]);

  const runMutation = useCallback(
    async (kind: PreferredMoveMutationKind) => {
      const ownTurn = sideToMove === session.bottomColor;
      const focusedPreferredMove =
        positionModel.state === "matching-played" &&
        playedMoveFocus?.preferredMove?.state === "assigned"
          ? playedMoveFocus.preferredMove
          : null;
      const mutationFen = focusedPreferredMove?.fen ?? session.currentPosition.fen;
      const mutationSavedMove = positionModel.savedMove ?? focusedPreferredMove?.move ?? null;
      const focusedOwnMove =
        focusedPreferredMove !== null && playedMoveFocus?.move?.color === session.bottomColor;
      const canSave =
        ownTurn &&
        positionModel.saveability === "savable" &&
        !preferredState.loading &&
        preferredState.error === null &&
        !contextState.loading &&
        contextState.error === null;
      const move = session.stagedMove;

      if (
        mutation !== null ||
        (!ownTurn && !focusedOwnMove) ||
        (kind !== "remove" && !canSave) ||
        (kind === "remove" && !mutationSavedMove) ||
        (kind === "add" && preferredState.preferredMove?.state !== "unassigned") ||
        (kind === "save" && (draft.mode !== "edit" || !move)) ||
        (kind !== "remove" && !move)
      ) {
        return;
      }

      const id = mutationId.current + 1;
      mutationId.current = id;
      const controller = new AbortController();
      mutationController.current = controller;
      setMutation(kind);
      setWorkflowError(null);
      const effectiveAt = explicitDate?.toISOString() ?? "";
      const result = await (async () => {
        try {
          return kind === "remove"
            ? await preferredMoveClient.remove(
                { fen: mutationFen, effective_at: effectiveAt },
                { signal: controller.signal },
              )
            : await preferredMoveClient.put(
                {
                  fen: session.currentPosition.fen,
                  move_uci: `${move!.sourceSquare}${move!.targetSquare}${move!.promotion ?? ""}`,
                  effective_at: effectiveAt,
                },
                { signal: controller.signal },
              );
        } catch {
          return { status: "unexpected_failure" as const };
        }
      })();

      if (id !== mutationId.current || controller.signal.aborted) {
        return;
      }
      mutationController.current = null;
      setMutation(null);
      if (result.status !== "success") {
        setWorkflowError(result.status);
        return;
      }

      setExplicitDate(null);
      setHasExplicitDate(false);
      setPendingEditPositionFen(null);
      setPlayedMoveFocus(null);
      setDraft(cancelPreferredMoveDraft());
      setSession((current) => ({ ...current, stagedMove: null }));
      setSessionStatus(
        kind === "add"
          ? "Preferred move added."
          : kind === "save"
            ? "Preferred move replaced."
            : "Preferred move removed.",
      );
      setRefreshToken((value) => value + 1);
    },
    [
      contextState.error,
      contextState.loading,
      explicitDate,
      draft.mode,
      mutation,
      playedMoveFocus,
      positionModel.saveability,
      positionModel.savedMove,
      positionModel.state,
      preferredMoveClient,
      preferredState.error,
      preferredState.loading,
      preferredState.preferredMove,
      session,
      setSession,
      setSessionStatus,
      sideToMove,
    ],
  );

  const onPlaySavedMove = useCallback(() => {
    const savedMove = positionModel.savedMove;
    const move = savedMove ? moveFromUci(savedMove.uci) : null;
    const next = move ? appendPositionPickerMove(session, move) : null;
    if (!next) {
      setSessionStatus("Saved move rejected because it is illegal in the current position.");
      return;
    }
    const playedMove = next.localMoves.at(-1) ?? null;
    if (playedMove) {
      setPlayedMoveFocus({ move: playedMove, preferredMove: preferredState.preferredMove });
    }
    setSession(next);
    setSessionStatus(`Saved move played locally: ${savedMove!.san}.`);
  }, [
    positionModel.savedMove,
    preferredState.preferredMove,
    session,
    setSession,
    setSessionStatus,
  ]);

  return {
    positionModel,
    positionContext: contextState.context,
    preferredLoading: preferredState.loading,
    preferredError: preferredState.error,
    contextLoading: contextState.loading,
    contextError: contextState.error,
    stagedMove: session.stagedMove,
    draftMode: draft.mode,
    date,
    mutation,
    workflowError,
    onDateChange: (value) => {
      setExplicitDate(value);
      setHasExplicitDate(true);
    },
    onStagedMove,
    onAdd: () => void runMutation("add"),
    onEdit,
    onSave: () => void runMutation("save"),
    onCancelEdit,
    onPlaySavedMove,
    onRemove: () => void runMutation("remove"),
    reset,
  };
}
