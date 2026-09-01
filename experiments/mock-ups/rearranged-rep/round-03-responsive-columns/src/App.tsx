import { useCallback, useEffect, useRef, useState, type ReactNode, type RefObject } from "react";
import { Group, Panel, Separator, type GroupImperativeHandle, type Layout } from "react-resizable-panels";

type PanelId = "board" | "session" | "engine";
type Mode = "wide" | "medium" | "narrow";

const SEPARATOR_WIDTH = 12;
const BOARD_MIN = 320;
const SESSION_MIN = 280;
const ENGINE_MIN = 360;
const WIDE_BREAKPOINT = 1040;
const MEDIUM_BREAKPOINT = 700;
const WIDE_DEFAULTS: Record<PanelId, number> = { board: 390, session: 325, engine: 420 };

const BOARD_POSITION = [
  ["♜", "♞", "♝", "♛", "♚", "♝", "♞", "♜"],
  ["♟", "♟", "♟", "", "", "♟", "♟", "♟"],
  ["", "", "", "", "", "", "", ""],
  ["", "", "", "♟", "", "", "", ""],
  ["", "", "", "", "♙", "", "", ""],
  ["", "", "", "", "", "", "", ""],
  ["♙", "♙", "♙", "♙", "", "♙", "♙", "♙"],
  ["♖", "♘", "♗", "♕", "♔", "♗", "♘", "♖"],
];

const MOVE_ROWS = [
  ["1", "e4", "d5"],
  ["2", "exd5", "Qxd5"],
  ["3", "Nc3", "Qd8"],
];

const ENGINE_LINES = [
  { rank: "01", line: "2. exd5 Qxd5 3. Nc3 Qd8 4. d4", score: "+0.31", win: 9, draw: 89, loss: 2 },
  { rank: "02", line: "2. Nc3 Nf6 3. d4 Bf5 4. Nf3", score: "+0.18", win: 7, draw: 91, loss: 2 },
  { rank: "03", line: "2. d4 Nf6 3. Nf3 Bg4 4. c4", score: "+0.12", win: 6, draw: 92, loss: 2 },
  { rank: "04", line: "2. c4 e5 3. Nf3 e4 4. Nd4", score: "+0.04", win: 5, draw: 92, loss: 3 },
];

function formatNumber(value: number) {
  return value.toLocaleString("en-US");
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function useStageWidth(stageRef: RefObject<HTMLDivElement | null>) {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const element = stageRef.current;
    if (!element) return;

    const observer = new ResizeObserver(([entry]) => {
      if (entry) setWidth(Math.round(entry.contentRect.width));
    });
    setWidth(Math.round(element.getBoundingClientRect().width));
    observer.observe(element);
    return () => observer.disconnect();
  }, [stageRef]);

  return width;
}

function getMode(width: number): Mode {
  if (width >= WIDE_BREAKPOINT) return "wide";
  if (width >= MEDIUM_BREAKPOINT) return "medium";
  return "narrow";
}

function getGroupPanelSpace(groupElement: HTMLDivElement | null) {
  if (!groupElement) return 0;
  const separatorWidth = Array.from(groupElement.querySelectorAll<HTMLElement>("[data-separator]"))
    .reduce((total, separator) => total + separator.getBoundingClientRect().width, 0);
  return Math.max(0, groupElement.getBoundingClientRect().width - separatorWidth);
}

function getInitialLayout(mode: Exclude<Mode, "narrow">, groupElement: HTMLDivElement | null): Layout | undefined {
  const panelSpace = getGroupPanelSpace(groupElement);
  if (mode === "wide") {
    if (panelSpace < BOARD_MIN + SESSION_MIN + ENGINE_MIN) return undefined;
    const board = clamp(WIDE_DEFAULTS.board, BOARD_MIN, panelSpace - SESSION_MIN - ENGINE_MIN);
    const session = clamp(WIDE_DEFAULTS.session, SESSION_MIN, panelSpace - board - ENGINE_MIN);
    const engine = panelSpace - board - session;
    return { board: (board / panelSpace) * 100, session: (session / panelSpace) * 100, engine: (engine / panelSpace) * 100 };
  }

  if (panelSpace < SESSION_MIN + ENGINE_MIN) return undefined;
  const session = clamp(350, SESSION_MIN, panelSpace - ENGINE_MIN);
  const engine = panelSpace - session;
  return { session: (session / panelSpace) * 100, engine: (engine / panelSpace) * 100 };
}

function BoardView() {
  return (
    <div className="board-wrap" aria-label="Simulated Scandinavian position after 1. e4 d5">
      <div className="board-grid">
        {BOARD_POSITION.flatMap((row, rowIndex) =>
          row.map((piece, columnIndex) => {
            const isLight = (rowIndex + columnIndex) % 2 === 0;
            const isWhite = piece !== "" && "♙♖♘♗♕♔".includes(piece);
            return (
              <div className={`square ${isLight ? "light" : "dark"}`} key={`${rowIndex}-${columnIndex}`}>
                {piece && <span className={isWhite ? "white-piece" : "black-piece"}>{piece}</span>}
              </div>
            );
          }),
        )}
      </div>
      <div className="eval-bar" aria-label="Evaluation plus zero point thirty one">
        <span className="eval-marker">+0.31</span>
      </div>
    </div>
  );
}

function LaneHeader({ eyebrow, title, meta, titleId }: { eyebrow: string; title: string; meta: string; titleId: string }) {
  return (
    <div className="lane-header">
      <div>
        <span className="lane-eyebrow">{eyebrow}</span>
        <h3 id={titleId}>{title}</h3>
      </div>
      <span className="lane-meta">{meta}</span>
    </div>
  );
}

function BoardLane() {
  return (
    <section className="layout-column board-lane" aria-labelledby="board-lane-title">
      <div className="lane-panel board-panel">
        <LaneHeader eyebrow="Lane 01" title="Board & history" titleId="board-lane-title" meta="White to move" />
        <BoardView />
        <div className="board-tools">
          <button type="button" className="quiet-button">‹ Prev</button>
          <button type="button" className="quiet-button">Next ›</button>
          <button type="button" className="quiet-button">Flip</button>
        </div>
        <div className="board-status-row"><span className="live-dot" /> Position loaded <span className="mono">ply 5</span></div>
      </div>
      <div className="lane-panel history-panel">
        <LaneHeader eyebrow="Current game" title="Move history" titleId="history-title" meta="Scandi main line" />
        <table className="move-table">
          <thead><tr><th>#</th><th>White</th><th>Black</th></tr></thead>
          <tbody>{MOVE_ROWS.map(([move, white, black], index) => <tr className={index === 2 ? "current-row" : ""} key={move}><td>{move}</td><td>{white}</td><td>{black}</td></tr>)}</tbody>
        </table>
        <p className="history-note">The board lane stays intact while either adjacent edge moves.</p>
      </div>
    </section>
  );
}

function SessionLane() {
  return (
    <section className="layout-column session-lane" aria-labelledby="session-lane-title">
      <div className="lane-panel reach-panel">
        <LaneHeader eyebrow="Position reach" title="A useful position" titleId="session-lane-title" meta="White repertoire" />
        <div className="reach-stat"><strong>4,812</strong><span>/ 5,040 games</span><b>95.5%</b></div>
        <div className="reach-bar"><span /></div>
        <p className="supporting-copy">Reached after the Scandinavian move order in the simulated corpus.</p>
        <div className="stat-foot"><span>Master + club sample</span><span>2022–25</span></div>
      </div>
      <div className="lane-panel move-panel">
        <LaneHeader eyebrow="Repertoire choice" title="Preferred move" titleId="move-title" meta="Saved" />
        <p className="supporting-copy">The choice currently attached to this position.</p>
        <div className="saved-move">
          <div className="move-title"><strong>exd5</strong><span className="saved-badge"><i /> Saved</span></div>
          <span className="mono muted">e4d5 · 2. exd5</span>
          <div className="move-details"><span>Effective</span><strong>2026-08-29</strong><span>Seen in</span><strong>4,812 games</strong></div>
        </div>
        <div className="staged-move"><div><span className="staged-label">Staged proposal</span><strong>Nc3</strong></div><span className="mono muted">d1c3 · compare before saving</span></div>
        <div className="move-actions"><button type="button" className="quiet-button">Compare</button><button type="button" className="accent-button">Stage move</button></div>
      </div>
      <details className="lane-panel description-panel"><summary><span>Position description</span><span>⌄</span></summary><p>Open centre, early queen recapture; the next choice decides whether this branch stays classical or enters an active development line.</p></details>
    </section>
  );
}

function EngineLane() {
  return (
    <section className="layout-column engine-lane" aria-labelledby="engine-lane-title">
      <div className="lane-panel engine-panel">
        <div className="lane-header engine-header">
          <div><span className="lane-eyebrow">Lane 03</span><h3 id="engine-lane-title">Engine output</h3><span className="lane-meta block-meta">Displayed position · depth 15 · 4 lines</span></div>
          <div className="engine-status"><span className="live-dot" /> Complete<br /><button type="button" className="text-button">Update analysis</button></div>
        </div>
        <div className="engine-lines">
          {ENGINE_LINES.map((line, index) => <article className={`engine-line ${index === 0 ? "best-line" : ""}`} key={line.rank}>
            <div className="line-top"><span className="line-rank">{line.rank}</span><span className="line-moves">{line.line}</span><strong>{line.score}</strong></div>
            <div className="wdl-bar"><span style={{ width: `${line.win}%` }} /><i style={{ width: `${line.draw}%` }} /><b style={{ width: `${line.loss}%` }} /></div>
            <div className="wdl-labels"><span>Win {line.win}%</span><span>Draw {line.draw}%</span><span>Loss {line.loss}%</span></div>
          </article>)}
        </div>
        <div className="engine-footer"><span>Stockfish simulation · illustrative</span><span className="mono">18.4k n/s</span></div>
      </div>
    </section>
  );
}

function PillSeparator({ id, label }: { id: string; label: string }) {
  return (
    <Separator id={id} className="divider-bar treatment-pill" aria-label={label} disableDoubleClick>
      <span className="divider-grip" aria-hidden="true"><i /><i /><i /></span>
      <span className="divider-label">Idea 03 · drag</span>
    </Separator>
  );
}

function ResizableColumns({
  mode,
  groupId,
  resetKey,
  onLayoutChange,
  children,
}: {
  mode: Exclude<Mode, "narrow">;
  groupId: string;
  resetKey: number;
  onLayoutChange: (layout: Layout, panelSpace: number) => void;
  children: ReactNode;
}) {
  const groupRef = useRef<GroupImperativeHandle | null>(null);
  const groupElementRef = useRef<HTMLDivElement | null>(null);

  const reportLayout = useCallback((nextLayout: Layout) => {
    onLayoutChange(nextLayout, getGroupPanelSpace(groupElementRef.current));
  }, [onLayoutChange]);

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      const nextLayout = getInitialLayout(mode, groupElementRef.current);
      if (nextLayout) {
        groupRef.current?.setLayout(nextLayout);
        reportLayout(nextLayout);
      }
    });
    return () => window.cancelAnimationFrame(frame);
  }, [mode, resetKey, reportLayout]);

  return (
    <Group
      id={groupId}
      className="split-group"
      orientation="horizontal"
      elementRef={groupElementRef}
      groupRef={groupRef}
      onLayoutChanged={reportLayout}
      resizeTargetMinimumSize={{ coarse: 28, fine: 18 }}
      style={{ height: "auto" }}
    >
      {children}
    </Group>
  );
}

function modeLabel(mode: Mode) {
  if (mode === "wide") return "Wide · 3 columns";
  if (mode === "medium") return "Medium · board + 2 columns";
  return "Narrow · 1 column";
}

function App() {
  const stageRef = useRef<HTMLDivElement | null>(null);
  const stageWidth = useStageWidth(stageRef);
  const mode = getMode(stageWidth);
  const [layout, setLayout] = useState<Layout>({});
  const [panelSpace, setPanelSpace] = useState(0);
  const [resetKey, setResetKey] = useState(0);

  const handleLayoutChange = useCallback((nextLayout: Layout, nextPanelSpace: number) => {
    setLayout(nextLayout);
    setPanelSpace(nextPanelSpace);
  }, []);

  function resetSplit() {
    setResetKey((current) => current + 1);
  }

  return (
    <main className="mockup-shell">
      <header className="site-header">
        <div className="topline"><div className="wordmark"><span className="wordmark-mark">♞</span><span>Chess Move Trainer <b>/</b> repertoire lab</span></div><span className="noncanonical-stamp">Responsive branch · noncanonical</span></div>
        <div className="hero-grid">
          <div><span className="section-eyebrow amber">Rearranged repertoire · responsive branch</span><h1>Let the workspace<br /><em>find its shape.</em></h1><p className="hero-copy">One selected centered pill, three container-aware arrangements. The board gets the full row it needs before Session and Engine share the lower edge.</p></div>
          <aside className="lineage-card"><span className="lineage-label">Lineage</span><strong>Idea 03 carried forward</strong><p>Only the available-width composition changes in this branch. Live resizing remains internal to each bounded Group.</p><div className="lineage-rule"><span>parent</span><b>round-02-divider-design-catalogue</b><span>selected</span><b>03 / centered pill</b></div></aside>
        </div>
      </header>

      <section className="workbench-section" aria-labelledby="workbench-heading">
        <div className="workbench-heading"><div><span className="section-eyebrow">Focused responsive question</span><h2 id="workbench-heading">Same lanes. Better fit.</h2></div><button type="button" className="reset-button" onClick={resetSplit}>↺ Reset split</button></div>
        <div className="preview-callout"><span className="preview-mark">03</span><div><strong>Centered pill carried forward</strong><span>Muted at rest, amber on hover/focus/drag; the visual cue remains unchanged wherever a vertical splitter exists.</span></div><span className="guardrail"><i /> Fake local content · no calls</span></div>
        <div className="split-readout" aria-live="polite">
          <span className="mode-annotation" data-testid="layout-mode"><i /> {modeLabel(mode)}</span>
          <span className="measured-width">Stage <strong>{stageWidth || "—"} px</strong></span>
          {mode === "wide" && <><span><i className="board-key" /> Board <strong>{layout.board && panelSpace ? `${formatNumber(Math.round((layout.board / 100) * panelSpace))} px` : "—"}</strong></span><span><i className="session-key" /> Session <strong>{layout.session && panelSpace ? `${formatNumber(Math.round((layout.session / 100) * panelSpace))} px` : "—"}</strong></span><span><i className="engine-key" /> Engine <strong>{layout.engine && panelSpace ? `${formatNumber(Math.round((layout.engine / 100) * panelSpace))} px` : "—"}</strong></span></>}
          {mode === "medium" && <><span><i className="session-key" /> Lower Session <strong>{layout.session && panelSpace ? `${formatNumber(Math.round((layout.session / 100) * panelSpace))} px` : "—"}</strong></span><span><i className="engine-key" /> Lower Engine <strong>{layout.engine && panelSpace ? `${formatNumber(Math.round((layout.engine / 100) * panelSpace))} px` : "—"}</strong></span></>}
          <span className="edge-note">Outer stage edges fixed</span>
        </div>

        <div ref={stageRef} className={`split-stage mode-${mode}`} data-layout-mode={mode}>
          {mode === "wide" && (
            <ResizableColumns mode="wide" groupId="responsive-wide-group" resetKey={resetKey} onLayoutChange={handleLayoutChange}>
              <Panel id="board" minSize={BOARD_MIN} defaultSize={WIDE_DEFAULTS.board} groupResizeBehavior="preserve-pixel-size"><BoardLane /></Panel>
              <PillSeparator id="board-session-wide" label="Board and Session boundary" />
              <Panel id="session" minSize={SESSION_MIN} defaultSize={WIDE_DEFAULTS.session} groupResizeBehavior="preserve-pixel-size"><SessionLane /></Panel>
              <PillSeparator id="session-engine-wide" label="Session and Engine boundary" />
              <Panel id="engine" minSize={ENGINE_MIN} defaultSize={WIDE_DEFAULTS.engine} groupResizeBehavior="preserve-relative-size"><EngineLane /></Panel>
            </ResizableColumns>
          )}
          {mode === "medium" && (
            <>
              <div className="medium-board-row"><BoardLane /></div>
              <div className="medium-lower-row">
                <ResizableColumns mode="medium" groupId="responsive-medium-group" resetKey={resetKey} onLayoutChange={handleLayoutChange}>
                  <Panel id="session" minSize={SESSION_MIN} defaultSize={350} groupResizeBehavior="preserve-pixel-size"><SessionLane /></Panel>
                  <PillSeparator id="session-engine-medium" label="Session and Engine boundary" />
                  <Panel id="engine" minSize={ENGINE_MIN} defaultSize={380} groupResizeBehavior="preserve-relative-size"><EngineLane /></Panel>
                </ResizableColumns>
              </div>
            </>
          )}
          {mode === "narrow" && <div className="narrow-stack"><BoardLane /><SessionLane /><EngineLane /></div>}
        </div>
      </section>

      <section className="responsive-notes" aria-labelledby="responsive-notes-heading">
        <div><span className="section-eyebrow">What to judge next</span><h2 id="responsive-notes-heading">Does the hierarchy survive the squeeze?</h2></div>
        <dl className="decision-grid">
          <div><dt>Wide</dt><dd>Three live panels keep their credible minimums; both centered pills mark internal redistribution.</dd></div>
          <div><dt>Medium</dt><dd>Board owns a full-width row. Session and Engine use a separate two-panel Group underneath.</dd></div>
          <div><dt>Narrow</dt><dd>The vertical stack removes draggable fiction and keeps the reading order explicit.</dd></div>
        </dl>
      </section>

      <footer className="document-footer"><span><strong>Exploration only.</strong> Fake local repertoire, board, and engine values; no backend calls or trainer records.</span><span>rearranged-rep / round-03-responsive-columns</span></footer>
    </main>
  );
}

export default App;
