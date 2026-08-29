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
import type { ChessSide } from "../viewer/chessPrimitives";
import { type PositionContextClient, fetchPositionContext } from "../viewer/positionContextApi";
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

export type PreferredMoveWorkflowState = {
  positionModel: ReturnType<typeof deriveRepertoirePositionModel>;
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
  const [date, setDate] = useState<CalendarDateValue>(null);
  const [mutation, setMutation] = useState<PreferredMoveMutationKind | null>(null);
  const [workflowError, setWorkflowError] = useState<PreferredMoveFailureCode | null>(null);
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
      }),
    [contextState.context, preferredState.preferredMove, session.bottomColor, sideToMove],
  );

  const reset = useCallback(() => {
    mutationId.current += 1;
    mutationController.current?.abort();
    mutationController.current = null;
    setMutation(null);
    setWorkflowError(null);
    setDraft(cancelPreferredMoveDraft());
    setDate(null);
  }, []);

  useEffect(() => {
    reset();
  }, [reset, session.currentPosition.fen, session.bottomColor]);

  const onStagedMove = useCallback(
    (move: PositionPickerSession["stagedMove"]) => {
      if (!move) {
        return;
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
    [positionModel.saveability, preferredState.preferredMove?.state, session.bottomColor],
  );

  const onEdit = useCallback(() => {
    if (!positionModel.savedMove) {
      return;
    }
    const next = beginPreferredMoveDraft("edit");
    setDraft(
      session.stagedMove
        ? (stagePreferredMoveDraft(next, session.stagedMove, session.bottomColor) ?? next)
        : next,
    );
    setWorkflowError(null);
  }, [positionModel.savedMove, session.bottomColor, session.stagedMove]);

  const onCancelEdit = useCallback(() => {
    setDraft(cancelPreferredMoveDraft());
    setSession((current) => ({ ...current, stagedMove: null }));
  }, [setSession]);

  const runMutation = useCallback(
    async (kind: PreferredMoveMutationKind) => {
      const ownTurn = sideToMove === session.bottomColor;
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
        !ownTurn ||
        (kind !== "remove" && !canSave) ||
        (kind === "remove" && !positionModel.savedMove) ||
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
      const effectiveAt = date?.toISOString() ?? "";
      const result = await (async () => {
        try {
          return kind === "remove"
            ? await preferredMoveClient.remove(
                { fen: session.currentPosition.fen, effective_at: effectiveAt },
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

      setDate(null);
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
      date,
      draft.mode,
      mutation,
      positionModel.saveability,
      positionModel.savedMove,
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
    setSession(next);
    setSessionStatus(`Saved move played locally: ${savedMove!.san}.`);
  }, [positionModel.savedMove, session, setSession, setSessionStatus]);

  return {
    positionModel,
    preferredLoading: preferredState.loading,
    preferredError: preferredState.error,
    contextLoading: contextState.loading,
    contextError: contextState.error,
    stagedMove: session.stagedMove,
    draftMode: draft.mode,
    date,
    mutation,
    workflowError,
    onDateChange: setDate,
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
