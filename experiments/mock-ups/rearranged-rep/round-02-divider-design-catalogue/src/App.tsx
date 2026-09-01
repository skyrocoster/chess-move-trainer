import { useEffect, useRef, useState } from "react";
import { Group, Panel, Separator, type GroupImperativeHandle, type Layout } from "react-resizable-panels";

type PanelId = "board" | "session" | "engine";
type TreatmentId = "hairline" | "rail" | "pill" | "dots" | "tabs" | "beacon";

type DividerTreatment = {
  id: TreatmentId;
  number: string;
  name: string;
  label: string;
  summary: string;
  resting: string;
  feedback: string;
  hitTarget: string;
  relationship: string;
  tradeoff: string;
};

const TREATMENTS: DividerTreatment[] = [
  {
    id: "hairline",
    number: "01",
    name: "Whisper hairline",
    label: "Minimal seam",
    summary: "A nearly quiet rule keeps the three cards visually continuous.",
    resting: "One faint 1px rule sits inside the 12px separator slot.",
    feedback: "Hover, focus, and active states raise the rule and add a restrained amber glow.",
    hitTarget: "The library keeps an 18px fine and 28px coarse hit region beyond the visible rule.",
    relationship: "The divider reads as a gap between adjacent cards rather than another component.",
    tradeoff: "The cleanest option, but the resting affordance is easiest to overlook.",
  },
  {
    id: "rail",
    number: "02",
    name: "Recessed rail",
    label: "Gutter track",
    summary: "A dark inset channel makes the movable boundary feel structural.",
    resting: "A full-width 12px rail is visible as a recessed dark groove with an inner edge.",
    feedback: "Hover and focus lift the rail border; active dragging fills its groove with warm contrast.",
    hitTarget: "The visible rail nearly matches the library hit region, so pointer discovery is immediate.",
    relationship: "The channel preserves breathing room between the panel surfaces and their borders.",
    tradeoff: "Clear and stable, though the extra track can make the workspace feel more engineered.",
  },
  {
    id: "pill",
    number: "03",
    name: "Centered pill",
    label: "Handle first",
    summary: "A small vertical handle says exactly where the boundary can be moved.",
    resting: "A muted rounded pill floats in the center of an otherwise quiet separator slot.",
    feedback: "The pill lengthens and turns amber on hover, focus, and active drag.",
    hitTarget: "The handle is visual, while the library supplies the larger invisible target around it.",
    relationship: "It separates the cards without creating a heavy line across their full height.",
    tradeoff: "A familiar direct-manipulation cue; the small resting handle needs enough contrast to be found.",
  },
  {
    id: "dots",
    number: "04",
    name: "Dot grip",
    label: "Tactile cue",
    summary: "A three-dot grip borrows a compact drag vocabulary from panels and drawers.",
    resting: "Three muted dots sit in the center of a low-contrast seam.",
    feedback: "The dots brighten and spread slightly on hover, focus, and active drag.",
    hitTarget: "Only the dots are visible; the library-owned target remains wider than the grip.",
    relationship: "The dot cluster feels attached to neither card, keeping the shared edge neutral.",
    tradeoff: "Friendly and compact, but dots can be mistaken for a menu or grip that drags another object.",
  },
  {
    id: "tabs",
    number: "05",
    name: "Edge tabs",
    label: "Notched boundary",
    summary: "Small edge tabs make each panel’s movable edge explicit without a full rail.",
    resting: "Short notches touch the neighboring card edges with a quiet center seam between them.",
    feedback: "Both tabs brighten and extend inward on hover, focus, and active drag.",
    hitTarget: "The tabs are only the visible marker; the library preserves the larger transparent target.",
    relationship: "Each card appears to own one side of the shared boundary, clarifying adjacency.",
    tradeoff: "Strong edge ownership, though the paired tabs can look busier where three cards meet.",
  },
  {
    id: "beacon",
    number: "06",
    name: "State beacon",
    label: "Accent on action",
    summary: "The seam stays quiet until interaction makes the active boundary unmistakable.",
    resting: "A tiny muted cap and near-invisible line mark the resting boundary.",
    feedback: "Hover and focus wake the full rail in blue; active dragging switches it to an amber signal.",
    hitTarget: "A broad library-owned target makes the dramatic feedback feel larger than the resting mark.",
    relationship: "The boundary disappears into the cards at rest and becomes a deliberate working tool on demand.",
    tradeoff: "Excellent feedback for active work, but the quiet resting state relies on hover or focus discovery.",
  },
];

const SEPARATOR_WIDTH = 12;
const BOARD_MIN = 320;
const SESSION_MIN = 280;
const ENGINE_MIN = 360;
const MIN_THREE_COLUMN_WIDTH = BOARD_MIN + SESSION_MIN + ENGINE_MIN + SEPARATOR_WIDTH * 2;
const WIDE_LAYOUT_QUERY = `(min-width: ${MIN_THREE_COLUMN_WIDTH + 42}px)`;
const INITIAL_PANEL_SIZES: Record<PanelId, number> = { board: 390, session: 325, engine: 420 };

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

function TreatmentSwatch({ treatment }: { treatment: DividerTreatment }) {
  return (
    <div className="treatment-swatch" aria-hidden="true">
      <span className="swatch-pane" />
      <span className={`swatch-divider treatment-${treatment.id}`}><span className="swatch-grip"><i /><i /><i /></span></span>
      <span className="swatch-pane" />
    </div>
  );
}

function CatalogueOption({ treatment, selected, onSelect }: { treatment: DividerTreatment; selected: boolean; onSelect: () => void }) {
  return (
    <button type="button" className={`catalogue-option ${selected ? "is-selected" : ""}`} aria-pressed={selected} onClick={onSelect}>
      <span className="option-topline"><span className="option-number">{treatment.number}</span><span className="option-label">{treatment.label}</span></span>
      <TreatmentSwatch treatment={treatment} />
      <strong>{treatment.name}</strong>
      <span className="option-summary">{treatment.summary}</span>
      <span className="option-tradeoff"><b>Trade-off</b> {treatment.tradeoff}</span>
    </button>
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
  const [selectedId, setSelectedId] = useState<TreatmentId>("pill");
  const [layout, setLayout] = useState<Layout>({});
  const groupRef = useRef<GroupImperativeHandle | null>(null);
  const groupElementRef = useRef<HTMLDivElement | null>(null);
  const isNarrow = !useMediaQuery(WIDE_LAYOUT_QUERY);
  const selectedTreatment = TREATMENTS.find((treatment) => treatment.id === selectedId) ?? TREATMENTS[2];

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

  const treatmentClass = `treatment-${selectedTreatment.id}`;

  return (
    <main className="mockup-shell">
      <header className="site-header">
        <div className="topline"><div className="wordmark"><span className="wordmark-mark">♞</span><span>Chess Move Trainer <b>/</b> repertoire lab</span></div><span className="noncanonical-stamp">Catalogue branch · noncanonical</span></div>
        <div className="hero-grid">
          <div><span className="section-eyebrow amber">Rearranged repertoire · divider catalogue</span><h1>Make the shared edge<br /><em>easy to find.</em></h1><p className="hero-copy">Six visual treatments for the same bounded Board / Session / Engine split. Choose the cue that makes the live edge feel discoverable without changing how the panels resize.</p></div>
          <aside className="lineage-card"><span className="lineage-label">Lineage</span><strong>Round 02 mechanics inherited</strong><p>Only the separator affordance changes in this branch. The library still owns both live boundaries.</p><div className="lineage-rule"><span>parent</span><b>round-02-adjacent-dividers</b><span>question</span><b>divider cue</b></div></aside>
        </div>
      </header>

      <section className="catalogue-section" aria-labelledby="catalogue-heading">
        <div className="catalogue-heading"><div><span className="section-eyebrow">One question · six treatments</span><h2 id="catalogue-heading">Which edge should invite a hand?</h2></div><span className="catalogue-count">Select a card to apply it below</span></div>
        <div className="catalogue-grid">{TREATMENTS.map((treatment) => <CatalogueOption key={treatment.id} treatment={treatment} selected={selectedId === treatment.id} onSelect={() => setSelectedId(treatment.id)} />)}</div>
      </section>

      <section className="workbench-section" aria-labelledby="workbench-heading">
        <div className="workbench-heading"><div><span className="section-eyebrow">Live preview · {selectedTreatment.label}</span><h2 id="workbench-heading">Same split. New signal.</h2></div><button type="button" className="reset-button" onClick={resetSplit}>↺ Reset split</button></div>
        <div className="preview-callout"><span className="preview-mark">{selectedTreatment.number}</span><div><strong>{selectedTreatment.name}</strong><span>{selectedTreatment.resting} {selectedTreatment.feedback}</span></div><span className="guardrail"><i /> Library mechanics fixed</span></div>
        <SplitReadout layout={layout} groupElement={groupElementRef.current} isNarrow={isNarrow} />
        {isNarrow && <div className="fallback-banner"><span className="fallback-icon">↳</span><div><strong>Stacked fallback active</strong><p>The splitters are intentionally disabled here: the lanes now flow vertically in Board → Session → Engine order, with each lane full-width.</p></div></div>}
        <div className={`split-stage ${isNarrow ? "is-narrow" : ""}`}>
          {isNarrow ? <>
            <BoardLane />
            <SessionLane />
            <EngineLane />
          </> : <Group
            id="divider-catalogue-split"
            className="split-group"
            orientation="horizontal"
            elementRef={groupElementRef}
            groupRef={groupRef}
            onLayoutChanged={(nextLayout) => setLayout(nextLayout)}
            resizeTargetMinimumSize={{ coarse: 28, fine: 18 }}
            style={{ height: "auto" }}
          >
            <Panel id="board" minSize={BOARD_MIN} defaultSize={INITIAL_PANEL_SIZES.board} groupResizeBehavior="preserve-pixel-size">
              <BoardLane />
            </Panel>
            <Separator id="board-session" className={`divider-bar ${treatmentClass}`} aria-label="Board and Session boundary" disableDoubleClick>
              <span className="divider-grip" aria-hidden="true"><i /><i /><i /></span>
              <span className="divider-label">Board / Session</span>
            </Separator>
            <Panel id="session" minSize={SESSION_MIN} defaultSize={INITIAL_PANEL_SIZES.session} groupResizeBehavior="preserve-pixel-size">
              <SessionLane />
            </Panel>
            <Separator id="session-engine" className={`divider-bar ${treatmentClass}`} aria-label="Session and Engine boundary" disableDoubleClick>
              <span className="divider-grip" aria-hidden="true"><i /><i /><i /></span>
              <span className="divider-label">Session / Engine</span>
            </Separator>
            <Panel id="engine" minSize={ENGINE_MIN} defaultSize={INITIAL_PANEL_SIZES.engine} groupResizeBehavior="preserve-relative-size">
              <EngineLane />
            </Panel>
          </Group>}
        </div>
      </section>

      <section className="selected-notes" aria-labelledby="selected-notes-heading">
        <div><span className="section-eyebrow">Selected treatment · {selectedTreatment.number}</span><h2 id="selected-notes-heading">{selectedTreatment.name}</h2></div>
        <dl className="decision-grid">
          <div><dt>Resting</dt><dd>{selectedTreatment.resting}</dd></div>
          <div><dt>Feedback</dt><dd>{selectedTreatment.feedback}</dd></div>
          <div><dt>Target</dt><dd>{selectedTreatment.hitTarget}</dd></div>
          <div><dt>Panel relationship</dt><dd>{selectedTreatment.relationship}</dd></div>
          <div><dt>Why choose it</dt><dd>{selectedTreatment.summary}</dd></div>
          <div><dt>Downside</dt><dd>{selectedTreatment.tradeoff}</dd></div>
        </dl>
      </section>

      <footer className="document-footer"><span><strong>Exploration only.</strong> Fake local repertoire, board, and engine values; no backend calls or trainer records.</span><span>rearranged-rep / round-02-divider-design-catalogue</span></footer>
    </main>
  );
}

export default App;
