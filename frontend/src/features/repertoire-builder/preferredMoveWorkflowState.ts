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
import { deriveRepertoirePositionModel } from "./repertoireWorkflowModel";
import {
  playAndStagePositionPickerMove,
  positionPickerSelectedTransition,
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
  positionContext: PositionContextResponse | null;
  preferredLoading: boolean;
  preferredError: ReturnType<typeof usePreferredMoveState>["error"];
  contextLoading: boolean;
  contextError: ReturnType<typeof usePositionContextState>["error"];
  stagedMove: PositionPickerSession["stagedMove"];
  date: CalendarDateValue;
  mutation: PreferredMoveMutationKind | null;
  workflowError: PreferredMoveFailureCode | null;
  onDateChange: (value: CalendarDateValue) => void;
  onSave: () => void;
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
  const [explicitDate, setExplicitDate] = useState<CalendarDateValue>(null);
  const [hasExplicitDate, setHasExplicitDate] = useState(false);
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
  const selectedTransition = useMemo(() => positionPickerSelectedTransition(session), [session]);
  const focusedOwnerTransition =
    selectedTransition?.move.color === session.bottomColor ? selectedTransition : null;
  const preferredPositionFen =
    focusedOwnerTransition?.sourcePosition.fen ?? session.currentPosition.fen;
  const preferredState = usePreferredMoveState(preferredPositionFen, preferredReader);
  const contextState = usePositionContextState(session.currentPosition.fen, contextReader);
  const positionModel = useMemo(
    () =>
      deriveRepertoirePositionModel({
        context: contextState.context,
        preferredMove: preferredState.preferredMove,
        sideToMove,
        bottomColor: session.bottomColor,
        sourceFen: preferredPositionFen,
        stagedMove: session.stagedMove,
        preferredMoveKnown: !preferredState.loading && preferredState.error === null,
      }),
    [
      contextState.context,
      preferredPositionFen,
      preferredState.error,
      preferredState.loading,
      preferredState.preferredMove,
      session.bottomColor,
      session.stagedMove,
      sideToMove,
    ],
  );

  const resetPositionState = useCallback(() => {
    mutationId.current += 1;
    mutationController.current?.abort();
    mutationController.current = null;
    setMutation(null);
    setWorkflowError(null);
    setExplicitDate(null);
    setHasExplicitDate(false);
  }, []);

  const reset = useCallback(() => {
    resetPositionState();
  }, [resetPositionState]);

  useEffect(() => {
    resetPositionState();
  }, [resetPositionState, session.currentPosition.fen, session.bottomColor]);

  const persistedDate = useMemo(() => {
    if (!positionModel.effectiveAt) {
      return null;
    }
    const parsed = new Date(positionModel.effectiveAt);
    return Number.isNaN(parsed.getTime()) ? null : normalizeToUtcMidnight(parsed);
  }, [positionModel.effectiveAt]);
  const date = hasExplicitDate ? explicitDate : persistedDate;

  const runMutation = useCallback(
    async (kind: PreferredMoveMutationKind) => {
      const ownTurn = sideToMove === session.bottomColor;
      const mutationFen = positionModel.sourceFen;
      const mutationSavedMove = positionModel.savedMove;
      const canSave =
        ownTurn &&
        positionModel.saveability === "savable" &&
        positionModel.savedPresence !== "unknown" &&
        positionModel.relationship !== "matching" &&
        positionModel.stagedMove !== null &&
        !preferredState.loading &&
        preferredState.error === null &&
        !contextState.loading &&
        contextState.error === null;
      const move = positionModel.stagedMove;

      if (
        mutation !== null ||
        (!ownTurn && kind === "remove") ||
        (kind === "save" && !canSave) ||
        (kind === "remove" && !mutationSavedMove) ||
        (kind === "save" && !move)
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
                  fen: mutationFen,
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
      if (kind === "save") {
        setSession((current) => ({ ...current, stagedMove: null }));
      }
      setSessionStatus(kind === "save" ? "Preferred move saved." : "Preferred move removed.");
      setRefreshToken((value) => value + 1);
    },
    [
      contextState.error,
      contextState.loading,
      explicitDate,
      mutation,
      positionModel.relationship,
      positionModel.savedPresence,
      positionModel.saveability,
      positionModel.sourceFen,
      positionModel.savedMove,
      positionModel.stagedMove,
      preferredMoveClient,
      preferredState.error,
      preferredState.loading,
      session,
      setSession,
      setSessionStatus,
      sideToMove,
    ],
  );

  const onPlaySavedMove = useCallback(() => {
    const savedMove = positionModel.savedMove;
    const move = savedMove ? moveFromUci(savedMove.uci) : null;
    const result =
      move && positionModel.ownTurn && mutation === null
        ? playAndStagePositionPickerMove(session, move)
        : null;
    if (!result) {
      setSessionStatus("Saved move rejected because it is illegal in the current position.");
      return;
    }
    setWorkflowError(null);
    setSession(result.session);
    setSessionStatus(`Saved move staged locally: ${savedMove!.san}.`);
  }, [
    mutation,
    positionModel.ownTurn,
    positionModel.savedMove,
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
    date,
    mutation,
    workflowError,
    onDateChange: (value) => {
      setExplicitDate(value);
      setHasExplicitDate(true);
    },
    onSave: () => void runMutation("save"),
    onPlaySavedMove,
    onRemove: () => void runMutation("remove"),
    reset,
  };
}
