import { useEffect, useMemo, useRef, useState, type CSSProperties, type RefObject } from "react";

type LaneKey = "board" | "session" | "engine";
type ModelId = "fluid" | "envelope" | "priority";
type Allocation = Record<LaneKey, number>;
type Bounds = { min: number; max: number; step: number };

type ModelDefinition = {
  id: ModelId;
  index: string;
  title: string;
  kicker: string;
  summary: string;
  unit: "weight" | "pixels";
  defaults: Allocation;
  bounds: Record<LaneKey, Bounds>;
  physicalMins: Allocation;
  physicalMaxes: Allocation;
  sizingRule: string;
  safeguard: string;
  fallback: string;
  layoutClass: string;
};

const LANE_LABELS: Record<LaneKey, string> = {
  board: "Board + history",
  session: "Reach + moves",
  engine: "Engine output",
};

const LANE_SHORT_LABELS: Record<LaneKey, string> = {
  board: "Board",
  session: "Session",
  engine: "Engine",
};

const MODELS: ModelDefinition[] = [
  {
    id: "fluid",
    index: "01",
    title: "Fluid proportion",
    kicker: "Weighted three-way rail",
    summary: "Every lane grows from a relative share; moving one weight lets the other two absorb the difference.",
    unit: "weight",
    defaults: { board: 1.25, session: 0.9, engine: 1.35 },
    bounds: {
      board: { min: 0.8, max: 2.4, step: 0.05 },
      session: { min: 0.7, max: 2.1, step: 0.05 },
      engine: { min: 0.9, max: 2.5, step: 0.05 },
    },
    physicalMins: { board: 280, session: 245, engine: 330 },
    physicalMaxes: { board: 560, session: 510, engine: 720 },
    sizingRule: "A single flex-weight vocabulary keeps the three columns fluid as the desktop shell changes.",
    safeguard: "Each lane has a hard pixel floor and ceiling; the controls also clamp its relative weight.",
    fallback: "Below the three-lane floor, stack Board → Session → Engine so no panel becomes an unusable sliver.",
    layoutClass: "model-fluid",
  },
  {
    id: "envelope",
    index: "02",
    title: "Preferred envelopes",
    kicker: "Soft target widths",
    summary: "Each lane asks for a useful width in pixels; spare room is shared, with engine output taking the final stretch.",
    unit: "pixels",
    defaults: { board: 390, session: 330, engine: 520 },
    bounds: {
      board: { min: 300, max: 560, step: 10 },
      session: { min: 270, max: 500, step: 10 },
      engine: { min: 360, max: 720, step: 10 },
    },
    physicalMins: { board: 300, session: 270, engine: 360 },
    physicalMaxes: { board: 560, session: 500, engine: 720 },
    sizingRule: "A preferred pixel envelope protects dense content while the solver shrinks targets before it wraps.",
    safeguard: "Targets are bounded independently; the board and session never borrow below their readable floors.",
    fallback: "At narrow widths, keep Board and Session side by side when possible, then put the full Engine tray below.",
    layoutClass: "model-envelope",
  },
  {
    id: "priority",
    index: "03",
    title: "Priority dock",
    kicker: "Flexible focus order",
    summary: "Three priority weights set who claims open space; a narrow viewport keeps Board + Engine visible and docks Session below.",
    unit: "weight",
    defaults: { board: 1.1, session: 0.72, engine: 1.5 },
    bounds: {
      board: { min: 0.75, max: 2.2, step: 0.05 },
      session: { min: 0.55, max: 1.8, step: 0.05 },
      engine: { min: 1.0, max: 2.8, step: 0.05 },
    },
    physicalMins: { board: 300, session: 275, engine: 360 },
    physicalMaxes: { board: 580, session: 520, engine: 760 },
    sizingRule: "The board and engine are the primary scan path; the session lane stays flexible but has a lower default claim.",
    safeguard: "Priority weights are bounded and each lane remains clamped to an explicit readable pixel range.",
    fallback: "When three lanes cannot fit, Board and Engine remain together first; Session becomes a full-width dock.",
    layoutClass: "model-priority",
  },
];

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

const INITIAL_ALLOCATIONS: Record<ModelId, Allocation> = Object.fromEntries(
  MODELS.map((model) => [model.id, { ...model.defaults }]),
) as Record<ModelId, Allocation>;

function formatNumber(value: number) {
  return value.toLocaleString("en-US");
}

function formatControlValue(model: ModelDefinition, value: number) {
  return model.unit === "pixels" ? `${Math.round(value)} px` : `${value.toFixed(2)}×`;
}

function formatBound(model: ModelDefinition, value: number) {
  return model.unit === "pixels" ? `${value} px` : `${value.toFixed(2)}×`;
}

function allocationShare(allocation: Allocation, lane: LaneKey) {
  const total = Object.values(allocation).reduce((sum, value) => sum + value, 0);
  return Math.round((allocation[lane] / total) * 100);
}

function clamp(value: number, bounds: Bounds) {
  return Math.min(bounds.max, Math.max(bounds.min, value));
}

function weightedWidths(total: number, weights: Allocation, mins: Allocation, maxes: Allocation) {
  const lanes: LaneKey[] = ["board", "session", "engine"];
  const widths: Allocation = { board: 0, session: 0, engine: 0 };
  let remaining = total;
  let active = [...lanes];

  while (active.length > 0) {
    const weightTotal = active.reduce((sum, lane) => sum + weights[lane], 0);
    const constrained = active.filter((lane) => {
      const proposal = (remaining * weights[lane]) / weightTotal;
      return proposal < mins[lane] || proposal > maxes[lane];
    });

    if (constrained.length === 0) {
      active.forEach((lane) => {
        widths[lane] = (remaining * weights[lane]) / weightTotal;
      });
      break;
    }

    const constrainedSet = new Set(constrained);
    constrained.forEach((lane) => {
      const proposal = (remaining * weights[lane]) / weightTotal;
      widths[lane] = proposal < mins[lane] ? mins[lane] : maxes[lane];
      remaining -= widths[lane];
    });
    active = active.filter((lane) => !constrainedSet.has(lane));
  }

  return lanes.map((lane) => Math.max(0, Math.round(widths[lane])));
}

function resolveWidths(total: number, model: ModelDefinition, allocation: Allocation) {
  const available = Math.max(0, total - 24);
  if (model.unit === "pixels") {
    const targets: Allocation = {
      board: clamp(allocation.board, model.bounds.board),
      session: clamp(allocation.session, model.bounds.session),
      engine: clamp(allocation.engine, model.bounds.engine),
    };
    const targetTotal = Object.values(targets).reduce((sum, value) => sum + value, 0);
    if (targetTotal > available) {
      return weightedWidths(available, targets, model.physicalMins, targets);
    }
    return weightedWidths(
      available,
      { board: 1, session: 1, engine: 1.35 },
      targets,
      model.physicalMaxes,
    );
  }

  return weightedWidths(available, allocation, model.physicalMins, model.physicalMaxes);
}

function useElementWidth(elementRef: RefObject<HTMLDivElement | null>) {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const updateWidth = () => setWidth(Math.round(element.getBoundingClientRect().width));
    updateWidth();
    const observer = new ResizeObserver(updateWidth);
    observer.observe(element);
    return () => observer.disconnect();
  }, [elementRef]);

  return width;
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

function LaneHeader({ eyebrow, title, meta, titleId }: { eyebrow: string; title: string; meta?: string; titleId?: string }) {
  return (
    <div className="lane-header">
      <div>
        <span className="lane-eyebrow">{eyebrow}</span>
        <h3 id={titleId}>{title}</h3>
      </div>
      {meta && <span className="lane-meta">{meta}</span>}
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
        <div className="board-status-row">
          <span className="live-dot" /> Position loaded
          <span className="mono">ply 5</span>
        </div>
      </div>
      <div className="lane-panel history-panel">
        <LaneHeader eyebrow="Current game" title="Move history" titleId="history-lane-title" meta="Scandi main line" />
        <table className="move-table">
          <thead>
            <tr><th>#</th><th>White</th><th>Black</th></tr>
          </thead>
          <tbody>
            {MOVE_ROWS.map(([move, white, black], index) => (
              <tr className={index === 2 ? "current-row" : ""} key={move}>
                <td>{move}</td><td>{white}</td><td>{black}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="history-note">The current ply stays anchored while the other lanes flex.</p>
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
        <LaneHeader eyebrow="Repertoire choice" title="Preferred move" titleId="move-lane-title" meta="Saved" />
        <p className="supporting-copy">The choice currently attached to this position.</p>
        <div className="saved-move">
          <div className="move-title"><strong>exd5</strong><span className="saved-badge"><i /> Saved</span></div>
          <span className="mono muted">e4d5 · 2. exd5</span>
          <div className="move-details"><span>Effective</span><strong>2026-08-29</strong><span>Seen in</span><strong>4,812 games</strong></div>
        </div>
        <div className="staged-move">
          <div><span className="staged-label">Staged proposal</span><strong>Nc3</strong></div>
          <span className="mono muted">d1c3 · compare before saving</span>
        </div>
        <div className="move-actions">
          <button type="button" className="quiet-button">Compare</button>
          <button type="button" className="accent-button">Stage move</button>
        </div>
      </div>

      <details className="lane-panel description-panel">
        <summary><span>Position description</span><span>⌄</span></summary>
        <p>Open centre, early queen recapture; the next choice decides whether this branch stays classical or enters an active development line.</p>
      </details>
    </section>
  );
}

function EngineLane() {
  return (
    <section className="layout-column engine-lane" aria-labelledby="engine-lane-title">
      <div className="lane-panel engine-panel">
        <div className="lane-header engine-header">
          <div>
            <span className="lane-eyebrow">Lane 03</span>
            <h3 id="engine-lane-title">Engine output</h3>
            <span className="lane-meta block-meta">Displayed position · depth 15 · 4 lines</span>
          </div>
          <div className="engine-status"><span className="live-dot" /> Complete<br /><button type="button" className="text-button">Update analysis</button></div>
        </div>
        <div className="engine-lines">
          {ENGINE_LINES.map((line, index) => (
            <article className={`engine-line ${index === 0 ? "best-line" : ""}`} key={line.rank}>
              <div className="line-top"><span className="line-rank">{line.rank}</span><span className="line-moves">{line.line}</span><strong>{line.score}</strong></div>
              <div className="wdl-bar"><span style={{ width: `${line.win}%` }} /><i style={{ width: `${line.draw}%` }} /><b style={{ width: `${line.loss}%` }} /></div>
              <div className="wdl-labels"><span>Win {line.win}%</span><span>Draw {line.draw}%</span><span>Loss {line.loss}%</span></div>
            </article>
          ))}
        </div>
        <div className="engine-footer"><span>Stockfish simulation · illustrative</span><span className="mono">18.4k n/s</span></div>
      </div>
    </section>
  );
}

function OptionTab({ model, allocation, active, onSelect }: { model: ModelDefinition; allocation: Allocation; active: boolean; onSelect: () => void }) {
  return (
    <button className={`option-tab ${active ? "active" : ""}`} type="button" role="tab" aria-selected={active} onClick={onSelect}>
      <div className="option-tab-top"><span className="option-index">{model.index}</span><span className="option-kicker">{model.kicker}</span><span className="option-state">{active ? "Open" : "View"}</span></div>
      <strong>{model.title}</strong>
      <p>{model.summary}</p>
      <div className="mini-rail" aria-hidden="true">
        <span className="mini-board" style={{ flex: allocation.board }} />
        <span className="mini-session" style={{ flex: allocation.session }} />
        <span className="mini-engine" style={{ flex: allocation.engine }} />
      </div>
      <div className="mini-legend"><span>Board {allocationShare(allocation, "board")}%</span><span>Session {allocationShare(allocation, "session")}%</span><span>Engine {allocationShare(allocation, "engine")}%</span></div>
    </button>
  );
}

function AllocationControl({ model, lane, value, onChange, actualWidth }: { model: ModelDefinition; lane: LaneKey; value: number; onChange: (value: number) => void; actualWidth?: number }) {
  const bounds = model.bounds[lane];
  const controlValue = model.unit === "pixels" ? value : Number(value.toFixed(2));
  const actualText = actualWidth ? `${actualWidth}px lane` : "Resize stage to measure";
  return (
    <div className="allocation-control">
      <div className="allocation-label"><label htmlFor={`${model.id}-${lane}`}>{LANE_LABELS[lane]}</label><output htmlFor={`${model.id}-${lane}`}>{formatControlValue(model, value)}</output></div>
      <input id={`${model.id}-${lane}`} type="range" min={bounds.min} max={bounds.max} step={bounds.step} value={controlValue} onChange={(event) => onChange(Number(event.target.value))} aria-valuetext={`${LANE_LABELS[lane]} ${formatControlValue(model, value)}`} />
      <div className="allocation-limits"><span>min {formatBound(model, bounds.min)}</span><span>{actualText}</span><span>max {formatBound(model, bounds.max)}</span></div>
    </div>
  );
}

function AllocationConsole({ model, allocation, widths, onChange, onReset, onResetAll }: { model: ModelDefinition; allocation: Allocation; widths: number[] | null; onChange: (lane: LaneKey, value: number) => void; onReset: () => void; onResetAll: () => void }) {
  const actualByLane: Record<LaneKey, number | undefined> = { board: widths?.[0], session: widths?.[1], engine: widths?.[2] };
  return (
    <section className="allocation-console" aria-labelledby="allocation-heading">
      <div className="console-heading">
        <div><span className="section-eyebrow">Live allocation controls</span><h2 id="allocation-heading">Work the three lanes</h2></div>
        <div className="console-actions"><button type="button" className="quiet-button" onClick={onReset}>Reset this model</button><button type="button" className="text-button" onClick={onResetAll}>Reset all</button></div>
      </div>
      <p className="console-copy">Drag any slider or use arrow keys. The stage solves the three values together, so you can judge the trade-off without resizing only the board.</p>
      <div className="allocation-grid">
        {(["board", "session", "engine"] as LaneKey[]).map((lane) => <AllocationControl key={lane} model={model} lane={lane} value={allocation[lane]} actualWidth={actualByLane[lane]} onChange={(value) => onChange(lane, value)} />)}
      </div>
      <div className="console-foot"><span><b>Observed lane widths</b> {widths ? `${widths[0]} + ${widths[1]} + ${widths[2]} px, plus 24 px gaps` : "measuring the stage…"}</span><span className="guardrail"><i /> Minimums and maximums are active</span></div>
    </section>
  );
}

function ModelAnnotation({ model, narrow, stageWidth }: { model: ModelDefinition; narrow: boolean; stageWidth: number }) {
  return (
    <aside className="model-annotation" aria-label={`${model.title} sizing notes`}>
      <div className="annotation-title"><span className="annotation-index">{model.index}</span><div><span className="section-eyebrow">Sizing rule</span><h2>{model.title}</h2></div><span className={`fallback-pill ${narrow ? "is-narrow" : ""}`}>{narrow ? "Fallback active" : "Three lanes active"}</span></div>
      <div className="annotation-grid">
        <div><span>How it flexes</span><p>{model.sizingRule}</p></div>
        <div><span>Safeguards</span><p>{model.safeguard}</p></div>
        <div><span>Narrow fallback</span><p>{model.fallback}</p></div>
      </div>
      <div className="annotation-status"><span>{stageWidth ? `Stage ${stageWidth}px wide` : "Stage width pending"}</span><span>•</span><span>{narrow ? "Intentional reflow, not horizontal scroll" : "All three principal columns are visible"}</span></div>
    </aside>
  );
}

function App() {
  const [activeModelId, setActiveModelId] = useState<ModelId>("fluid");
  const [allocations, setAllocations] = useState<Record<ModelId, Allocation>>(INITIAL_ALLOCATIONS);
  const stageRef = useRef<HTMLDivElement>(null);
  const stageWidth = useElementWidth(stageRef);
  const activeModel = MODELS.find((model) => model.id === activeModelId) ?? MODELS[0];
  const activeAllocation = allocations[activeModel.id];
  const minimumStageWidth = Object.values(activeModel.physicalMins).reduce((sum, value) => sum + value, 0) + 24;
  const isNarrow = stageWidth > 0 && stageWidth < minimumStageWidth;
  const resolvedWidths = useMemo(() => {
    if (!stageWidth || isNarrow) return null;
    return resolveWidths(stageWidth, activeModel, activeAllocation);
  }, [activeAllocation, activeModel, isNarrow, stageWidth]);
  const stageStyle: CSSProperties | undefined = resolvedWidths && !isNarrow ? { gridTemplateColumns: resolvedWidths.map((width) => `${width}px`).join(" ") } : undefined;

  function updateAllocation(lane: LaneKey, value: number) {
    setAllocations((current) => ({ ...current, [activeModel.id]: { ...current[activeModel.id], [lane]: clamp(value, activeModel.bounds[lane]) } }));
  }

  function resetActiveModel() {
    setAllocations((current) => ({ ...current, [activeModel.id]: { ...activeModel.defaults } }));
  }

  function resetAllModels() {
    setAllocations(Object.fromEntries(MODELS.map((model) => [model.id, { ...model.defaults }])) as Record<ModelId, Allocation>);
  }

  return (
    <main className="catalogue-shell">
      <header className="site-header">
        <div className="topline"><div className="wordmark"><span className="wordmark-mark">♞</span><span>Chess Move Trainer <b>/</b> repertoire lab</span></div><span className="noncanonical-stamp">First branch · noncanonical</span></div>
        <div className="hero-grid">
          <div><span className="section-eyebrow amber">Rearranged repertoire · round 01</span><h1>Three columns,<br /><em>one working surface.</em></h1><p className="hero-copy">A live comparison of flexible desktop allocations for the inherited Board / Position / Engine grouping. Every lane keeps a useful job before it gives up space.</p></div>
          <aside className="lineage-card"><span className="lineage-label">Lineage</span><strong>Parent concept</strong><p><code>initial.html</code> → this branch</p><strong>Question</strong><p>Can all three principal columns flex without creating a throwaway state?</p></aside>
        </div>
      </header>

      <section className="catalogue-section" aria-labelledby="catalogue-heading">
        <div className="section-heading"><div><span className="section-eyebrow">Comparison catalogue</span><h2 id="catalogue-heading">Choose a resizing model to inspect.</h2></div><span className="section-count">3 structural options</span></div>
        <div className="option-tabs" role="tablist" aria-label="Three flexible column models">
          {MODELS.map((model) => <OptionTab key={model.id} model={model} allocation={allocations[model.id]} active={model.id === activeModel.id} onSelect={() => setActiveModelId(model.id)} />)}
        </div>
      </section>

      <section className="workbench-section" aria-labelledby="workbench-heading">
        <div className="workbench-heading"><div><span className="section-eyebrow">Open model · {activeModel.index}</span><h2 id="workbench-heading">{activeModel.title}</h2></div><span className="model-mode">{activeModel.kicker}</span></div>
        <AllocationConsole model={activeModel} allocation={activeAllocation} widths={resolvedWidths} onChange={updateAllocation} onReset={resetActiveModel} onResetAll={resetAllModels} />
        <div ref={stageRef} className={`layout-surface ${activeModel.layoutClass} ${isNarrow ? "is-narrow" : ""}`} style={stageStyle}>
          <BoardLane />
          <SessionLane />
          <EngineLane />
        </div>
        <ModelAnnotation model={activeModel} narrow={isNarrow} stageWidth={stageWidth} />
      </section>

      <section className="decision-strip" aria-label="Decisions this catalogue is designed to settle"><span className="section-eyebrow">Designed to settle</span><div><strong>Which rule feels predictable while dragging?</strong><span>Does the narrow fallback preserve the next useful action?</span><span>Which lane deserves the extra desktop width?</span></div></section>
      <footer className="document-footer"><span><strong>Exploration only.</strong> All repertoire, engine, and game values are local illustrative data. No trainer records change.</span><span>rearranged-rep / round-01-flexible-columns</span></footer>
    </main>
  );
}

export default App;
