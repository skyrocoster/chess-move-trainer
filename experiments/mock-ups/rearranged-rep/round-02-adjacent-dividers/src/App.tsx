import { useEffect, useRef, useState } from "react";
import { Group, Panel, Separator, type GroupImperativeHandle, type Layout } from "react-resizable-panels";

type PanelId = "board" | "session" | "engine";

const SEPARATOR_WIDTH = 12;
const BOARD_MIN = 320;
const SESSION_MIN = 280;
const ENGINE_MIN = 360;
const MIN_THREE_COLUMN_WIDTH = BOARD_MIN + SESSION_MIN + ENGINE_MIN + SEPARATOR_WIDTH * 2;
const WIDE_LAYOUT_QUERY = `(min-width: ${MIN_THREE_COLUMN_WIDTH + 42}px)`;

const BOARD_POSITION = [
  ["♜", "♞", "♝", "♛", "♚", "♝", "♞", "♜"],
  ["♟", "♟", "♟", "", "", "♟", "♟", "♟"],
  ["", "", "", "", "", "", ""],
  ["", "", "", "♟", "", "", ""],
  ["", "", "", "", "♙", "", "", ""],
  ["", "", "", "", "", "", ""],
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

const INITIAL_PANEL_SIZES: Record<PanelId, number> = { board: 390, session: 325, engine: 420 };

function formatNumber(value: number) {
  return value.toLocaleString("en-US");
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(() => typeof window !== "undefined" && window.matchMedia(query).matches);

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    const updateMatches = () => setMatches(mediaQuery.matches);
    updateMatches();
    mediaQuery.addEventListener("change", updateMatches);
    return () => mediaQuery.removeEventListener("change", updateMatches);
  }, [query]);

  return matches;
}

function getGroupPanelSpace(groupElement: HTMLDivElement | null) {
  if (!groupElement) return 0;
  const separatorWidth = Array.from(groupElement.querySelectorAll<HTMLElement>("[data-separator]"))
    .reduce((total, separator) => total + separator.getBoundingClientRect().width, 0);
  return groupElement.getBoundingClientRect().width - separatorWidth;
}

function initialPanelSizes(panelSpace: number): Record<PanelId, number> {
  const board = clamp(INITIAL_PANEL_SIZES.board, BOARD_MIN, panelSpace - SESSION_MIN - ENGINE_MIN);
  const session = clamp(INITIAL_PANEL_SIZES.session, SESSION_MIN, panelSpace - board - ENGINE_MIN);
  return { board, session, engine: panelSpace - board - session };
}

function initialLayout(groupElement: HTMLDivElement | null): Layout | undefined {
  const panelSpace = getGroupPanelSpace(groupElement);
  if (panelSpace < BOARD_MIN + SESSION_MIN + ENGINE_MIN) return undefined;

  const sizes = initialPanelSizes(panelSpace);
  return Object.fromEntries(Object.entries(sizes).map(([id, size]) => [id, (size / panelSpace) * 100]));
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

function SplitReadout({ layout, groupElement, isNarrow }: { layout: Layout; groupElement: HTMLDivElement | null; isNarrow: boolean }) {
  const panelSpace = getGroupPanelSpace(groupElement);
  const widthFor = (panelId: PanelId) => {
    if (isNarrow) return "full width";
    const percentage = layout[panelId];
    return percentage === undefined || panelSpace === 0 ? "—" : `${formatNumber(Math.round((percentage / 100) * panelSpace))} px`;
  };

  return (
    <div className="split-readout" aria-live="polite">
      <span><i className="board-key" /> Board <strong>{widthFor("board")}</strong></span>
      <span><i className="session-key" /> Session <strong>{widthFor("session")}</strong></span>
      <span><i className="engine-key" /> Engine <strong>{widthFor("engine")}</strong></span>
      <span className={`layout-state ${isNarrow ? "is-stacked" : ""}`}>{isNarrow ? "Stacked fallback" : "Two live dividers"}</span>
    </div>
  );
}

function App() {
  const [layout, setLayout] = useState<Layout>({});
  const groupRef = useRef<GroupImperativeHandle | null>(null);
  const groupElementRef = useRef<HTMLDivElement | null>(null);
  const isNarrow = !useMediaQuery(WIDE_LAYOUT_QUERY);

  useEffect(() => {
    if (isNarrow) return;
    const nextLayout = initialLayout(groupElementRef.current);
    if (nextLayout) groupRef.current?.setLayout(nextLayout);
  }, [isNarrow]);

  function resetSplit() {
    if (isNarrow) return;
    const nextLayout = initialLayout(groupElementRef.current);
    if (nextLayout) groupRef.current?.setLayout(nextLayout);
  }

  return (
    <main className="mockup-shell">
      <header className="site-header">
        <div className="topline"><div className="wordmark"><span className="wordmark-mark">♞</span><span>Chess Move Trainer <b>/</b> repertoire lab</span></div><span className="noncanonical-stamp">Focused branch · noncanonical</span></div>
        <div className="hero-grid">
           <div><span className="section-eyebrow amber">Rearranged repertoire · round 02</span><h1>Move the edge,<br /><em>not the abstraction.</em></h1><p className="hero-copy">A direct-manipulation split view for the inherited Board / Position / Engine grouping. Each visible bar owns one shared boundary and redistributes space through the library inside the fixed stage bounds.</p></div>
          <aside className="lineage-card"><span className="lineage-label">Focused question</span><strong>Can the edge feel real?</strong><p>Drag the bar between Board and Session. Then drag the bar between Session and Engine.</p><div className="lineage-rule"><span>left divider</span><b>Board ↔ Session</b><span>right divider</span><b>Session ↔ Engine</b></div></aside>
        </div>
      </header>

      <section className="workbench-section" aria-labelledby="workbench-heading">
        <div className="workbench-heading"><div><span className="section-eyebrow">Direct split view · three principal columns</span><h2 id="workbench-heading">Two boundaries. Three working lanes.</h2></div><button type="button" className="reset-button" onClick={resetSplit}>↺ Reset split</button></div>
         <div className="instruction-bar"><span className="instruction-mark">↔</span><div><strong>Drag either vertical bar to move its shared component edge.</strong><span>Board ↔ Session starts with those adjacent panels. Session ↔ Engine starts with those adjacent panels; at a minimum, the library redistributes available room. Focus a bar and use ← →, Home, or End.</span></div><span className="guardrail"><i /> Min widths active</span></div>
         <SplitReadout layout={layout} groupElement={groupElementRef.current} isNarrow={isNarrow} />
         {isNarrow && <div className="fallback-banner"><span className="fallback-icon">↳</span><div><strong>Stacked fallback active</strong><p>The splitters are intentionally disabled here: the lanes now flow vertically in Board → Session → Engine order, with each lane full-width.</p></div></div>}
         <div className={`split-stage ${isNarrow ? "is-narrow" : ""}`}>
           {isNarrow ? <>
             <BoardLane />
             <SessionLane />
             <EngineLane />
           </> : <Group
             id="rearranged-rep-split"
             className="split-group"
             orientation="horizontal"
             elementRef={groupElementRef}
             groupRef={groupRef}
             onLayoutChanged={(nextLayout) => setLayout(nextLayout)}
             style={{ height: "auto" }}
           >
             <Panel id="board" minSize={BOARD_MIN} defaultSize={INITIAL_PANEL_SIZES.board} groupResizeBehavior="preserve-pixel-size">
               <BoardLane />
             </Panel>
             <Separator id="board-session" className="divider-bar" aria-label="Board and Session boundary" disableDoubleClick>
               <span className="divider-grip" aria-hidden="true"><i /><i /><i /></span>
               <span className="divider-label">Board / Session</span>
             </Separator>
             <Panel id="session" minSize={SESSION_MIN} defaultSize={INITIAL_PANEL_SIZES.session} groupResizeBehavior="preserve-pixel-size">
               <SessionLane />
             </Panel>
             <Separator id="session-engine" className="divider-bar" aria-label="Session and Engine boundary" disableDoubleClick>
               <span className="divider-grip" aria-hidden="true"><i /><i /><i /></span>
               <span className="divider-label">Session / Engine</span>
             </Separator>
             <Panel id="engine" minSize={ENGINE_MIN} defaultSize={INITIAL_PANEL_SIZES.engine} groupResizeBehavior="preserve-relative-size">
               <EngineLane />
             </Panel>
           </Group>}
         </div>
      </section>

       <aside className="interaction-notes" aria-labelledby="notes-heading"><div><span className="section-eyebrow">What to judge</span><h2 id="notes-heading">Does the shared edge behave like the component edge?</h2></div><div className="note-grid"><div><span>Left bar</span><p>Board grows as Session contracts, or the reverse. At a minimum, the library uses available room without breaking bounds.</p></div><div><span>Right bar</span><p>Session grows as Engine contracts, or the reverse. Board remains unchanged unless a constraint requires redistribution.</p></div><div><span>At narrow width</span><p>No fake vertical affordance: splitters disappear and the full-width reading order is explicit.</p></div></div></aside>
      <footer className="document-footer"><span><strong>Exploration only.</strong> Fake local repertoire, board, and engine values; no backend calls or trainer records.</span><span>rearranged-rep / round-02-adjacent-dividers</span></footer>
    </main>
  );
}

export default App;
