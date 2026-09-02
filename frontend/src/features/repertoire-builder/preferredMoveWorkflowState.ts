import {
  useCallback,
  useEffect,
  useLayoutEffect,
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
  commitStagedMove,
  playAndStagePositionPickerMove,
  positionPickerSelectedTransition,
  type PositionPickerMove,
  type PositionPickerSession,
} from "./positionPickerSession";
import type { PreferredMoveMutationKind } from "./PreferredMovePanel";

export const PREFERRED_MOVE_DATE_UNAVAILABLE = "Date changes are temporarily unavailable";

export type PreferredMoveDateCapability = {
  available: false;
  reason: typeof PREFERRED_MOVE_DATE_UNAVAILABLE;
  onActivate: () => void;
  onChange: (value: CalendarDateValue) => void;
};

const unavailableDateCapability: PreferredMoveDateCapability = {
  available: false,
  reason: PREFERRED_MOVE_DATE_UNAVAILABLE,
  onActivate: () => undefined,
  onChange: () => undefined,
};

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
  date: CalendarDateValue;
  dateEdit: PreferredMoveDateCapability;
  mutation: PreferredMoveMutationKind | null;
  workflowError: PreferredMoveFailureCode | null;
  onDateChange: (value: CalendarDateValue) => void;
  onSave: () => void;
  onPlaySavedMove: () => void;
  onRemove: () => void;
  onRetry: () => void;
  reset: () => void;
};

type PendingRefresh = {
  id: number;
  key: number;
  kind: PreferredMoveMutationKind;
  stagedUci: string | null;
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
  const [contextRefreshToken, setContextRefreshToken] = useState(0);
  const [mutation, setMutation] = useState<PreferredMoveMutationKind | null>(null);
  const [workflowError, setWorkflowError] = useState<PreferredMoveFailureCode | null>(null);
  const [failedMutation, setFailedMutation] = useState<PreferredMoveMutationKind | null>(null);
  const [pendingRefresh, setPendingRefresh] = useState<PendingRefresh | null>(null);
  const mutationId = useRef(0);
  const mutationController = useRef<AbortController | null>(null);
  const preferredReader = useCallback(
    (fen: string, options?: { asOf?: string; signal?: AbortSignal }) => {
      return preferredMoveClient.get(fen, options);
    },
    [preferredMoveClient],
  );
  const contextReader = useCallback(
    (fen: string, signal?: AbortSignal) => positionContextClient(fen, signal),
    [positionContextClient],
  );
  const selectedTransition = useMemo(() => positionPickerSelectedTransition(session), [session]);
  const focusedOwnerTransition =
    selectedTransition?.move.color === session.bottomColor ? selectedTransition : null;
  const preferredPositionFen =
    focusedOwnerTransition?.sourcePosition.fen ?? session.currentPosition.fen;
  const preferredState = usePreferredMoveState(preferredPositionFen, preferredReader, refreshToken);
  const contextState = usePositionContextState(
    session.currentPosition.fen,
    contextReader,
    contextRefreshToken,
  );
  const positionModel = useMemo(
    () =>
      deriveRepertoirePositionModel({
        context: contextState.context,
        preferredMove: preferredState.preferredMove,
        sideToMove,
        bottomColor: session.bottomColor,
        sourceFen: preferredPositionFen,
        stagedMove: session.stagedMove,
        preferredMoveKnown:
          preferredState.preferredMove !== null ||
          (!preferredState.loading && preferredState.error === null),
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
    setFailedMutation(null);
    setPendingRefresh(null);
  }, []);

  const reset = useCallback(() => {
    resetPositionState();
  }, [resetPositionState]);

  useEffect(() => {
    resetPositionState();
  }, [resetPositionState, session.currentPosition.fen, session.bottomColor]);

  const persistedDate = useMemo(() => {
    if (!positionModel.saved?.effectiveAt) {
      return null;
    }
    const parsed = new Date(positionModel.saved.effectiveAt);
    return Number.isNaN(parsed.getTime()) ? null : normalizeToUtcMidnight(parsed);
  }, [positionModel.saved]);
  const date = persistedDate;

  useLayoutEffect(() => {
    if (
      pendingRefresh === null ||
      preferredState.completedRefreshKey !== pendingRefresh.key ||
      preferredState.loading
    ) {
      return;
    }

    if (preferredState.error !== null) {
      setPendingRefresh(null);
      setMutation(null);
      setFailedMutation(null);
      return;
    }

    const refreshed = preferredState.preferredMove;
    const confirmed =
      pendingRefresh.kind === "save"
        ? refreshed?.state === "assigned" && refreshed.move?.uci === pendingRefresh.stagedUci
        : refreshed?.state === "unassigned";
    if (!confirmed) {
      setPendingRefresh(null);
      setMutation(null);
      setFailedMutation(pendingRefresh.kind);
      setWorkflowError("unexpected_failure");
      return;
    }

    if (pendingRefresh.kind === "save") {
      setSession((current) => {
        const staged = current.stagedMove;
        const stagedUci = staged
          ? `${staged.sourceSquare}${staged.targetSquare}${staged.promotion ?? ""}`
          : null;
        return stagedUci === pendingRefresh.stagedUci ? commitStagedMove(current) : current;
      });
    }
    setPendingRefresh(null);
    setMutation(null);
    setFailedMutation(null);
    setSessionStatus(
      pendingRefresh.kind === "save" ? "Preferred move saved." : "Preferred move removed.",
    );
  }, [
    pendingRefresh,
    preferredState.completedRefreshKey,
    preferredState.error,
    preferredState.loading,
    preferredState.preferredMove,
    setSession,
    setSessionStatus,
  ]);

  const runMutation = useCallback(
    async (kind: PreferredMoveMutationKind) => {
      const ownTurn = sideToMove === session.bottomColor;
      const mutationFen = positionModel.sourceFen;
      const mutationSavedMove = positionModel.saved?.move ?? null;
      const canSave =
        ownTurn &&
        positionModel.saveability === "savable" &&
        positionModel.savedPresence !== "unknown" &&
        positionModel.relationship !== "matching" &&
        positionModel.staged !== null &&
        !preferredState.loading &&
        preferredState.error === null &&
        !contextState.loading &&
        contextState.error === null;
      const move = positionModel.staged?.move ?? null;

      if (
        mutation !== null ||
        pendingRefresh !== null ||
        (!ownTurn && kind === "remove") ||
        (kind === "save" && !canSave) ||
        (kind === "remove" &&
          (!mutationSavedMove ||
            positionModel.savedPresence !== "present" ||
            preferredState.loading ||
            preferredState.error !== null)) ||
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
      setFailedMutation(null);
      const result = await (async () => {
        try {
          return kind === "remove"
            ? await preferredMoveClient.remove(
                { fen: mutationFen, effective_at: "" },
                { signal: controller.signal },
              )
            : await preferredMoveClient.put(
                {
                  fen: mutationFen,
                  move_uci: `${move!.sourceSquare}${move!.targetSquare}${move!.promotion ?? ""}`,
                  effective_at: "",
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
      if (result.status !== "success") {
        setMutation(null);
        setFailedMutation(kind);
        setWorkflowError(result.status);
        return;
      }

      const nextRefreshToken = refreshToken + 1;
      setPendingRefresh({
        id,
        key: nextRefreshToken,
        kind,
        stagedUci: kind === "save" ? (positionModel.staged?.uci ?? null) : null,
      });
      setRefreshToken(nextRefreshToken);
    },
    [
      contextState.error,
      contextState.loading,
      mutation,
      pendingRefresh,
      positionModel.relationship,
      positionModel.savedPresence,
      positionModel.saveability,
      positionModel.sourceFen,
      positionModel.saved,
      positionModel.staged,
      preferredMoveClient,
      preferredState.error,
      preferredState.loading,
      refreshToken,
      session,
      sideToMove,
    ],
  );

  const onPlaySavedMove = useCallback(() => {
    const savedMove = positionModel.saved?.move ?? null;
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
  }, [mutation, positionModel.ownTurn, positionModel.saved, session, setSession, setSessionStatus]);

  const onRetry = useCallback(() => {
    if (failedMutation !== null) {
      void runMutation(failedMutation);
      return;
    }
    setWorkflowError(null);
    setRefreshToken((value) => value + 1);
    setContextRefreshToken((value) => value + 1);
  }, [failedMutation, runMutation]);

  return {
    positionModel,
    positionContext: contextState.context,
    preferredLoading: preferredState.loading,
    preferredError: preferredState.error,
    contextLoading: contextState.loading,
    contextError: contextState.error,
    date,
    dateEdit: unavailableDateCapability,
    mutation,
    workflowError,
    onDateChange: unavailableDateCapability.onChange,
    onSave: () => void runMutation("save"),
    onPlaySavedMove,
    onRemove: () => void runMutation("remove"),
    onRetry,
    reset,
  };
}
