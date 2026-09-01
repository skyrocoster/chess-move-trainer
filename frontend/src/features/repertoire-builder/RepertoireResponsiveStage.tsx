import {
  useCallback,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
  type RefObject,
} from "react";
import {
  Group,
  Panel,
  Separator,
  type GroupImperativeHandle,
  type Layout,
} from "react-resizable-panels";

import styles from "./RepertoireResponsiveStage.module.css";

type Mode = "wide" | "medium" | "narrow";
type ResizableMode = Exclude<Mode, "narrow">;

const WIDE_BREAKPOINT = 1040;
const MEDIUM_BREAKPOINT = 700;
const SEPARATOR_SLOT = 12;

const BOARD_MIN = 320;
const SESSION_MIN = 280;
const ENGINE_MIN = 360;

const WIDE_BOARD_DEFAULT = 390;
const WIDE_SESSION_DEFAULT = 325;
const MEDIUM_SESSION_DEFAULT = 350;

export type RepertoireResponsiveStageProps = {
  board: ReactNode;
  session: ReactNode;
  engine: ReactNode;
};

function clamp(value: number, minimum: number, maximum: number) {
  return Math.min(maximum, Math.max(minimum, value));
}

function modeForWidth(width: number): Mode {
  if (width >= WIDE_BREAKPOINT) {
    return "wide";
  }
  if (width >= MEDIUM_BREAKPOINT) {
    return "medium";
  }
  return "narrow";
}

function useStageWidth(stageRef: RefObject<HTMLDivElement | null>) {
  const [width, setWidth] = useState(0);

  useLayoutEffect(() => {
    const stage = stageRef.current;
    if (!stage) {
      return;
    }

    const updateWidth = (nextWidth: number) => {
      const roundedWidth = Math.round(nextWidth);
      setWidth((currentWidth) => (currentWidth === roundedWidth ? currentWidth : roundedWidth));
    };

    updateWidth(stage.getBoundingClientRect().width);
    if (typeof ResizeObserver === "undefined") {
      return;
    }

    let updateTimer: ReturnType<typeof setTimeout> | null = null;
    const observer = new ResizeObserver(([entry]) => {
      const nextWidth = entry?.contentRect.width ?? stage.getBoundingClientRect().width;
      if (updateTimer !== null) {
        clearTimeout(updateTimer);
      }
      updateTimer = setTimeout(() => {
        updateTimer = null;
        updateWidth(nextWidth);
      });
    });
    observer.observe(stage);
    return () => {
      observer.disconnect();
      if (updateTimer !== null) {
        clearTimeout(updateTimer);
      }
    };
  }, [stageRef]);

  return width;
}

function panelSpaceForStage(width: number, separatorCount: number) {
  return Math.max(0, width - separatorCount * SEPARATOR_SLOT);
}

function panelSpaceForGroup(
  groupElement: HTMLDivElement | null,
  stageWidth: number,
  separatorCount: number,
) {
  if (groupElement) {
    const separators = Array.from(groupElement.querySelectorAll<HTMLElement>("[data-separator]"));
    const measuredSeparatorWidth = separators.reduce(
      (total, separator) => total + separator.getBoundingClientRect().width,
      0,
    );
    const separatorWidth = measuredSeparatorWidth || separators.length * SEPARATOR_SLOT;
    const groupWidth = groupElement.getBoundingClientRect().width;
    if (groupWidth > 0) {
      return Math.max(0, groupWidth - separatorWidth);
    }
  }

  return panelSpaceForStage(stageWidth, separatorCount);
}

function layoutFromPixels(sizes: Record<string, number>, panelSpace: number): Layout | undefined {
  if (panelSpace <= 0) {
    return undefined;
  }

  const total = Object.values(sizes).reduce((sum, size) => sum + size, 0);
  if (total <= 0) {
    return undefined;
  }

  return Object.fromEntries(Object.entries(sizes).map(([id, size]) => [id, (size / total) * 100]));
}

function defaultLayout(mode: ResizableMode, panelSpace: number): Layout | undefined {
  if (mode === "wide") {
    if (panelSpace < BOARD_MIN + SESSION_MIN + ENGINE_MIN) {
      return undefined;
    }

    const board = clamp(WIDE_BOARD_DEFAULT, BOARD_MIN, panelSpace - SESSION_MIN - ENGINE_MIN);
    const session = clamp(WIDE_SESSION_DEFAULT, SESSION_MIN, panelSpace - board - ENGINE_MIN);
    return layoutFromPixels({ board, session, engine: panelSpace - board - session }, panelSpace);
  }

  if (panelSpace < SESSION_MIN + ENGINE_MIN) {
    return undefined;
  }

  const session = clamp(MEDIUM_SESSION_DEFAULT, SESSION_MIN, panelSpace - ENGINE_MIN);
  return layoutFromPixels({ session, engine: panelSpace - session }, panelSpace);
}

function PillSeparator({ id, label }: { id: string; label: string }) {
  return (
    <Separator id={id} className={styles.separator} aria-label={label} disableDoubleClick>
      <span className={styles.pill} aria-hidden="true" />
    </Separator>
  );
}

function RepertoirePanel({
  id,
  minimum,
  defaultSize,
  children,
}: {
  id: string;
  minimum: number;
  defaultSize: number;
  children: ReactNode;
}) {
  return (
    <Panel
      id={id}
      className={styles.panel}
      minSize={minimum}
      defaultSize={defaultSize}
      data-panel-min-size={`${minimum}px`}
    >
      {children}
    </Panel>
  );
}

export function RepertoireResponsiveStage({
  board,
  session,
  engine,
}: RepertoireResponsiveStageProps) {
  const stageRef = useRef<HTMLDivElement>(null);
  const stageWidth = useStageWidth(stageRef);
  const mode = modeForWidth(stageWidth);
  const wideGroupRef = useRef<GroupImperativeHandle | null>(null);
  const wideGroupElementRef = useRef<HTMLDivElement | null>(null);
  const mediumGroupRef = useRef<GroupImperativeHandle | null>(null);
  const mediumGroupElementRef = useRef<HTMLDivElement | null>(null);

  const wideDefaultLayout = useMemo(
    () => defaultLayout("wide", panelSpaceForStage(stageWidth, 2)),
    [stageWidth],
  );
  const mediumDefaultLayout = useMemo(
    () => defaultLayout("medium", panelSpaceForStage(stageWidth, 1)),
    [stageWidth],
  );

  const resetLayout = useCallback(() => {
    if (mode === "narrow") {
      return;
    }

    const groupRef = mode === "wide" ? wideGroupRef : mediumGroupRef;
    const groupElementRef = mode === "wide" ? wideGroupElementRef : mediumGroupElementRef;
    const separatorCount = mode === "wide" ? 2 : 1;
    const layout = defaultLayout(
      mode,
      panelSpaceForGroup(groupElementRef.current, stageWidth, separatorCount),
    );
    if (layout) {
      groupRef.current?.setLayout(layout);
    }
  }, [mode, stageWidth]);

  return (
    <div
      ref={stageRef}
      className={styles.stage}
      data-testid="repertoire-workspace-stage"
      data-layout-mode={mode}
    >
      <div className={styles.stageActions}>
        <button
          type="button"
          className={styles.reset}
          onClick={resetLayout}
          aria-label="Reset panel layout"
          data-testid="repertoire-responsive-reset"
        >
          Reset layout
        </button>
      </div>

      {mode === "wide" ? (
        <Group
          id="repertoire-responsive-wide-group"
          className={styles.group}
          orientation="horizontal"
          defaultLayout={wideDefaultLayout}
          elementRef={wideGroupElementRef}
          groupRef={wideGroupRef}
          resizeTargetMinimumSize={{ coarse: 28, fine: 18 }}
          style={{ inlineSize: "100%", blockSize: "auto", minInlineSize: 0 }}
        >
          <RepertoirePanel id="board" minimum={BOARD_MIN} defaultSize={WIDE_BOARD_DEFAULT}>
            {board}
          </RepertoirePanel>
          <PillSeparator id="board-session-wide" label="Board and Session boundary" />
          <RepertoirePanel id="session" minimum={SESSION_MIN} defaultSize={WIDE_SESSION_DEFAULT}>
            {session}
          </RepertoirePanel>
          <PillSeparator id="session-engine-wide" label="Session and Engine boundary" />
          <RepertoirePanel id="engine" minimum={ENGINE_MIN} defaultSize={420}>
            {engine}
          </RepertoirePanel>
        </Group>
      ) : null}

      {mode === "medium" ? (
        <>
          <div className={styles.mediumBoardRow} data-testid="repertoire-responsive-board-row">
            {board}
          </div>
          <div className={styles.mediumLowerRow}>
            <Group
              id="repertoire-responsive-medium-group"
              className={styles.group}
              orientation="horizontal"
              defaultLayout={mediumDefaultLayout}
              elementRef={mediumGroupElementRef}
              groupRef={mediumGroupRef}
              resizeTargetMinimumSize={{ coarse: 28, fine: 18 }}
              style={{ inlineSize: "100%", blockSize: "auto", minInlineSize: 0 }}
            >
              <RepertoirePanel
                id="session"
                minimum={SESSION_MIN}
                defaultSize={MEDIUM_SESSION_DEFAULT}
              >
                {session}
              </RepertoirePanel>
              <PillSeparator id="session-engine-medium" label="Session and Engine boundary" />
              <RepertoirePanel id="engine" minimum={ENGINE_MIN} defaultSize={380}>
                {engine}
              </RepertoirePanel>
            </Group>
          </div>
        </>
      ) : null}

      {mode === "narrow" ? (
        <div className={styles.narrowStack}>
          {board}
          {session}
          {engine}
        </div>
      ) : null}
    </div>
  );
}
