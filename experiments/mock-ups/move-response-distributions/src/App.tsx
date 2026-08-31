import { useMemo, useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type OutcomeKey = "balanced" | "sharp" | "resilient" | "active";

type ResponseMove = {
  id: string;
  san: string;
  uci: string;
  count: number;
  family: string;
  outcome: string;
  outcomeKey: OutcomeKey;
  whiteScore: number;
  note: string;
  color: string;
};

type ChartEntry = {
  payload?: ResponseMove;
  id?: string;
};

const TOTAL_GAMES = 12_480;

const OUTCOME_COLORS: Record<OutcomeKey, string> = {
  balanced: "#9bb3bd",
  sharp: "#e7a45e",
  resilient: "#87c99a",
  active: "#c18ce9",
};

const RESPONSE_SEEDS: ResponseMove[] = [
  {
    id: "e5",
    san: "e5",
    uci: "e7e5",
    count: 4_118,
    family: "Open game",
    outcome: "Balanced centre",
    outcomeKey: "balanced",
    whiteScore: 51,
    note: "Classical development; the centre opens immediately.",
    color: "#e4b76c",
  },
  {
    id: "c5",
    san: "c5",
    uci: "c7c5",
    count: 3_331,
    family: "Sicilian",
    outcome: "Sharp branches",
    outcomeKey: "sharp",
    whiteScore: 52,
    note: "The most ambitious reply, trading symmetry for counterplay.",
    color: "#55bda9",
  },
  {
    id: "c6",
    san: "c6",
    uci: "c7c6",
    count: 1_548,
    family: "Caro-Kann",
    outcome: "Resilient shell",
    outcomeKey: "resilient",
    whiteScore: 50,
    note: "A sturdy centre with a clear light-squared bishop plan.",
    color: "#86a9ef",
  },
  {
    id: "e6",
    san: "e6",
    uci: "e7e6",
    count: 1_228,
    family: "French",
    outcome: "Sharp tension",
    outcomeKey: "sharp",
    whiteScore: 51,
    note: "Black accepts a cramped start to challenge the centre later.",
    color: "#bc8de2",
  },
  {
    id: "d6",
    san: "d6",
    uci: "d7d6",
    count: 742,
    family: "Pirc",
    outcome: "Active fianchetto",
    outcomeKey: "active",
    whiteScore: 53,
    note: "Flexible and provocative, but White gets the first space claim.",
    color: "#ee8e6c",
  },
  {
    id: "d5",
    san: "d5",
    uci: "d7d5",
    count: 618,
    family: "Scandinavian",
    outcome: "Active challenge",
    outcomeKey: "active",
    whiteScore: 52,
    note: "Immediate contact in the centre; the queen decision follows.",
    color: "#db83a9",
  },
  {
    id: "Nf6",
    san: "Nf6",
    uci: "g8f6",
    count: 493,
    family: "Alekhine",
    outcome: "Sharp chase",
    outcomeKey: "sharp",
    whiteScore: 53,
    note: "Invites White to build a pawn centre and then attacks it.",
    color: "#5eafca",
  },
  {
    id: "g6",
    san: "g6",
    uci: "g7g6",
    count: 402,
    family: "Modern",
    outcome: "Flexible pressure",
    outcomeKey: "resilient",
    whiteScore: 52,
    note: "The king-side fianchetto keeps the central commitment hidden.",
    color: "#a5c96b",
  },
  {
    id: "a6",
    san: "a6",
    uci: "a7a6",
    count: 80,
    family: "Rare sidestep",
    outcome: "Small sample",
    outcomeKey: "balanced",
    whiteScore: 49,
    note: "A rare waiting move; keep it visible without giving it equal weight.",
    color: "#89969a",
  },
];

const BASE_BOARD = new Chess();
const FIRST_MOVE = BASE_BOARD.move({ from: "e2", to: "e4" });
const AFTER_E4_FEN = BASE_BOARD.fen();
const LEGAL_UCIS = new Set(
  BASE_BOARD.moves({ verbose: true }).map((move) => `${move.from}${move.to}${move.promotion ?? ""}`),
);
const RESPONSES = RESPONSE_SEEDS.map((response) => ({
  ...response,
  pct: (response.count / TOTAL_GAMES) * 100,
  legal: LEGAL_UCIS.has(response.uci),
}));

const PIE_TOOLTIP_STYLE = {
  backgroundColor: "#1d292d",
  border: "1px solid #405057",
  borderRadius: "10px",
  color: "#f6f1e8",
  fontSize: "12px",
};

function formatCount(count: number) {
  return count.toLocaleString("en-US");
}

function formatPct(count: number) {
  return `${((count / TOTAL_GAMES) * 100).toFixed(1)}%`;
}

function getResponseFromEntry(entry: unknown) {
  if (!entry || typeof entry !== "object") return undefined;
  const candidate = entry as ChartEntry;
  if (candidate.payload?.id) return candidate.payload;
  return candidate.id ? RESPONSES.find((response) => response.id === candidate.id) : undefined;
}

function ConceptCard({
  number,
  title,
  question,
  tradeoff,
  children,
}: {
  number: string;
  title: string;
  question: string;
  tradeoff: string;
  children: React.ReactNode;
}) {
  return (
    <article className="concept-card" data-testid={`mockup-card-${number}`}>
      <header className="concept-header">
        <div className="concept-heading">
          <span className="concept-number">{number}</span>
          <div>
            <p className="eyebrow">Presentation approach</p>
            <h2>{title}</h2>
          </div>
        </div>
        <div className="concept-question">
          <span className="label">Product question</span>
          <strong>{question}</strong>
        </div>
      </header>
      <div className="concept-content">{children}</div>
      <footer className="concept-footer">
        <span className="tradeoff-mark" aria-hidden="true">
          ↔
        </span>
        <p>
          <span>Trade-off</span> {tradeoff}
        </p>
      </footer>
    </article>
  );
}

function ResponseList({
  responses,
  selectedId,
  onSelect,
  compact = false,
}: {
  responses: typeof RESPONSES;
  selectedId: string | null;
  onSelect: (id: string) => void;
  compact?: boolean;
}) {
  return (
    <div className={`response-list${compact ? " response-list-compact" : ""}`} aria-label="Move response controls">
      {responses.map((response, index) => (
        <button
          className={`response-row${selectedId === response.id ? " is-selected" : ""}`}
          type="button"
          key={response.id}
          onClick={() => onSelect(response.id)}
          aria-pressed={selectedId === response.id}
          data-testid={`move-${response.id}`}
          title={`Play ${response.san} (${response.uci})`}
        >
          <span className="row-index" style={{ backgroundColor: response.color }} aria-hidden="true">
            {String(index + 1).padStart(2, "0")}
          </span>
          <span className="row-main">
            <strong>{response.san}</strong>
            <small>
              {response.uci} · {response.family}
            </small>
          </span>
          <span className="row-stat">
            <strong>{formatPct(response.count)}</strong>
            <small>{formatCount(response.count)} games</small>
          </span>
          <span className="row-chevron" aria-hidden="true">
            ↗
          </span>
        </button>
      ))}
    </div>
  );
}

function ChartHint({ children }: { children: React.ReactNode }) {
  return <p className="chart-hint"><span aria-hidden="true">⌁</span>{children}</p>;
}

function BoardView({ position, mini = false }: { position: string; mini?: boolean }) {
  return (
    <div className={mini ? "mini-board" : "board-frame"} aria-label={mini ? "Live board preview" : "Live position board"}>
      <Chessboard
        options={{
          position,
          boardOrientation: "white",
          showNotation: true,
          allowDragging: false,
          allowDrawingArrows: false,
          showAnimations: false,
          animationDurationInMs: 0,
          boardStyle: {
            borderRadius: mini ? "8px" : "12px",
            overflow: "hidden",
            boxShadow: "0 16px 32px rgba(0, 0, 0, 0.26)",
          },
          darkSquareStyle: { backgroundColor: "#5b756f" },
          lightSquareStyle: { backgroundColor: "#e6ddca" },
          alphaNotationStyle: { color: "#213438", fontWeight: 700 },
          numericNotationStyle: { color: "#213438", fontWeight: 700 },
        }}
      />
    </div>
  );
}

function App() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [position, setPosition] = useState(AFTER_E4_FEN);
  const [announcement, setAnnouncement] = useState("No reply selected yet. Choose a legal move below to preview it.");
  const [expanded, setExpanded] = useState(false);

  const selected = RESPONSES.find((response) => response.id === selectedId) ?? null;
  const topResponse = selected ?? RESPONSES[0];
  const representedLegal = useMemo(() => RESPONSES.filter((response) => response.legal).length, []);

  function selectResponse(id: string) {
    const response = RESPONSES.find((candidate) => candidate.id === id);
    if (!response) return;

    const board = new Chess(AFTER_E4_FEN);
    const legalMove = board.moves({ verbose: true }).find(
      (move) => `${move.from}${move.to}${move.promotion ?? ""}` === response.uci,
    );

    if (!legalMove) {
      setAnnouncement(`${response.san} is not legal from the 1.e4 position.`);
      return;
    }

    const played = board.move({ from: legalMove.from, to: legalMove.to, promotion: legalMove.promotion });
    setSelectedId(response.id);
    setPosition(board.fen());
    setAnnouncement(
      `Previewing 1. e4 ${played.san}: ${response.family}. ${formatPct(response.count)} of ${formatCount(TOTAL_GAMES)} sampled games chose this reply.`,
    );
  }

  function handleChartClick(entry: unknown, index?: number) {
    const chartResponse = getResponseFromEntry(entry) ?? (typeof index === "number" ? RESPONSES[index] : undefined);
    if (chartResponse) selectResponse(chartResponse.id);
  }

  function resetPosition() {
    setSelectedId(null);
    setPosition(AFTER_E4_FEN);
    setAnnouncement("Position reset to after 1. e4. Choose a legal reply to preview it.");
  }

  const visibleRanked = expanded ? RESPONSES : RESPONSES.slice(0, 6);
  const ringData = RESPONSES.map((response) => ({
    ...response,
    pressure: Math.round(response.count * (response.whiteScore / 50)),
  }));

  return (
    <main className="document-shell">
      <header className="site-header">
        <div className="topline">
          <div className="wordmark">
            <span className="wordmark-mark" aria-hidden="true">♞</span>
            <span>Chess Move Trainer <b>/</b> opening lab</span>
          </div>
          <span className="noncanonical-stamp">Exploration · noncanonical</span>
        </div>

        <div className="hero-grid">
          <div>
            <p className="eyebrow hero-eyebrow">Response distribution study · 01</p>
            <h1>Five ways to read<br /><em>the next move.</em></h1>
            <p className="hero-copy">
              After <strong>1. e4</strong>, what should a move trainer show first: the crowd, the coach, the board, or the risk?
              This document puts five real interaction patterns side by side using one legal, simulated opening sample.
            </p>
          </div>
          <aside className="hero-aside">
            <span className="aside-index">The brief</span>
            <p>Move response distributions are not only statistics. They are invitations to choose a line.</p>
            <span className="aside-formula">distribution → decision → preview</span>
          </aside>
        </div>
      </header>

      <section className="live-workbench" aria-labelledby="live-heading">
        <div className="workbench-heading">
          <div>
            <p className="eyebrow">Shared interaction surface</p>
            <h2 id="live-heading">Every view drives the same position</h2>
          </div>
          <button className="reset-button" type="button" onClick={resetPosition}>
            <span aria-hidden="true">↺</span> Reset position
          </button>
        </div>

        <div className="workbench-grid">
          <div className="board-column">
            <BoardView position={position} />
            <div className="board-caption">
              <span className="turn-chip"><i aria-hidden="true" /> Black to move</span>
              <span className="verified-chip"><span aria-hidden="true">✓</span> {representedLegal} replies verified legal</span>
            </div>
          </div>
          <div className="line-column">
            <div className="line-kicker"><span>Current line</span><span className="move-number">01 / 01</span></div>
            <div className="line-display" data-testid="current-line" aria-live="polite">
              <span className="line-white">1. e4</span>
              {selected ? <span className="line-black">{selected.san}</span> : <span className="line-placeholder">choose a reply</span>}
            </div>
            <p className="line-explanation" data-testid="selection-explanation">{announcement}</p>
            <div className="selected-detail">
              <div className="selected-detail-head">
                <span className="label">Focused response</span>
                <span className="signal-dot" style={{ backgroundColor: topResponse.color }} aria-hidden="true" />
              </div>
              <div className="selected-move">
                <strong>{selected ? selected.san : "—"}</strong>
                <span>{selected ? selected.uci : "Select any slice, bar, or move row"}</span>
              </div>
              <div className="detail-grid">
                <div><span>Share</span><strong>{selected ? formatPct(selected.count) : "—"}</strong></div>
                <div><span>Sample</span><strong>{selected ? formatCount(selected.count) : "—"}</strong></div>
                <div><span>Outcome read</span><strong>{selected ? selected.outcome : "—"}</strong></div>
              </div>
            </div>
            <p className="accessibility-note"><span aria-hidden="true">↳</span> Charts are pointer-friendly; the move rows are the keyboard and screen-reader fallback.</p>
          </div>
        </div>
      </section>

      <section className="data-ribbon" aria-label="Sample context">
        <div><span>Position</span><strong>After 1. e4</strong></div>
        <div><span>Sample</span><strong>{formatCount(TOTAL_GAMES)} games</strong></div>
        <div><span>Corpus window</span><strong>Club + master · 2022–25</strong></div>
        <div><span>Data note</span><strong>Illustrative, not a recommendation</strong></div>
      </section>

      <section className="concepts-section" aria-labelledby="concepts-heading">
        <div className="section-intro">
          <div>
            <p className="eyebrow">Five divergent lenses</p>
            <h2 id="concepts-heading">One distribution. Five jobs.</h2>
          </div>
          <p>All visualizations use Recharts. Click a slice or bar to make the represented legal move the live preview above.</p>
        </div>

        <div className="concept-stack">
          <ConceptCard
            number="01"
            title="Classic labeled pie"
            question="Can I scan the whole reply tree at a glance?"
            tradeoff="Maximum legibility for a small set of meaningful replies; labels become crowded as the tail grows."
          >
            <div className="card-intro-row">
              <p>Familiar, direct, and honest about share. Labels pair SAN with rounded percentage so the chart can stand alone.</p>
              <span className="count-pill">9 replies shown</span>
            </div>
            <div className="chart-shell labeled-pie-shell" aria-label="Labeled pie of Black's responses after 1.e4">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={RESPONSES}
                    dataKey="count"
                    nameKey="san"
                    cx="50%"
                    cy="50%"
                    outerRadius="72%"
                    paddingAngle={1}
                    stroke="#162124"
                    strokeWidth={2}
                    label={(props) => {
                      const name = typeof props.name === "string" ? props.name : "";
                      const percent = typeof props.percent === "number" ? props.percent : 0;
                      return `${name} ${Math.round(percent * 100)}%`;
                    }}
                    labelLine={{ stroke: "#718188", strokeWidth: 1 }}
                    onClick={(entry, index) => handleChartClick(entry, index)}
                  >
                    {RESPONSES.map((response) => <Cell key={response.id} fill={response.color} style={{ cursor: "pointer" }} />)}
                  </Pie>
                  <Tooltip formatter={(value) => `${formatCount(Number(value))} games`} contentStyle={PIE_TOOLTIP_STYLE} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <ChartHint>Click any labeled sector to play that reply. Every sector has a text control below.</ChartHint>
            <ResponseList responses={RESPONSES} selectedId={selectedId} onSelect={selectResponse} />
          </ConceptCard>

          <ConceptCard
            number="02"
            title="Center-of-gravity donut"
            question="What reply should I prepare first?"
            tradeoff="A quiet, compact summary makes the leader memorable; precise comparisons move into the list."
          >
            <div className="donut-layout">
              <div className="donut-chart-shell" aria-label="Donut chart of response share">
                <div className="donut-center" aria-live="polite">
                  <span>Focused reply</span>
                  <strong>{topResponse.san}</strong>
                  <small>{formatPct(topResponse.count)} of games</small>
                </div>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={RESPONSES}
                      dataKey="count"
                      nameKey="san"
                      innerRadius="62%"
                      outerRadius="89%"
                      paddingAngle={3}
                      stroke="#162124"
                      strokeWidth={2}
                      onClick={(entry, index) => handleChartClick(entry, index)}
                    >
                      {RESPONSES.map((response) => <Cell key={response.id} fill={response.color} style={{ cursor: "pointer" }} />)}
                    </Pie>
                    <Tooltip formatter={(value) => `${formatCount(Number(value))} games`} contentStyle={PIE_TOOLTIP_STYLE} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="donut-copy">
                <p className="mini-kicker">Live center summary</p>
                <h3>{topResponse.family}</h3>
                <p>{topResponse.note}</p>
                <div className="micro-stat"><span>Leader</span><strong>e5 · {formatCount(RESPONSES[0].count)} games</strong></div>
                <div className="micro-stat"><span>Next most common</span><strong>c5 · {formatPct(RESPONSES[1].count)}</strong></div>
              </div>
            </div>
            <ChartHint>Click to move the center from the default leader to the reply you want to study.</ChartHint>
            <ResponseList responses={RESPONSES.slice(0, 5)} selectedId={selectedId} onSelect={selectResponse} compact />
            <p className="list-tail-note">The long tail stays available in approach 05.</p>
          </ConceptCard>

          <ConceptCard
            number="03"
            title="Board + response rail"
            question="Can evidence and action live together?"
            tradeoff="The board keeps the trainer in context and makes selection feel immediate; the denser rail costs chart area."
          >
            <div className="board-rail-layout">
              <div className="inline-board-column">
                <BoardView position={position} mini />
                <p><span className="board-mini-label">Preview</span> The same board follows every chart selection.</p>
              </div>
              <div className="response-rail-chart">
                <div className="rail-chart-heading"><span>Top replies</span><strong>share of games</strong></div>
                <div className="rail-chart-shell" aria-label="Bar chart beside board">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={RESPONSES.slice(0, 6)} layout="vertical" margin={{ top: 8, right: 15, bottom: 8, left: 0 }}>
                      <XAxis type="number" hide domain={[0, "dataMax"]} />
                      <YAxis type="category" dataKey="san" width={37} tick={{ fill: "#c5d0cd", fontSize: 12, fontWeight: 700 }} axisLine={false} tickLine={false} />
                      <Tooltip cursor={{ fill: "rgba(143, 212, 155, 0.08)" }} formatter={(value) => `${formatCount(Number(value))} games`} contentStyle={PIE_TOOLTIP_STYLE} />
                      <Bar dataKey="count" radius={[0, 5, 5, 0]} onClick={(entry, index) => handleChartClick(entry, index)}>
                        {RESPONSES.slice(0, 6).map((response) => <Cell key={response.id} fill={response.color} style={{ cursor: "pointer" }} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <p className="rail-footnote">The six most common replies stay visible; rare responses remain keyboard-accessible below.</p>
              </div>
            </div>
            <ResponseList responses={RESPONSES} selectedId={selectedId} onSelect={selectResponse} compact />
          </ConceptCard>

          <ConceptCard
            number="04"
            title="Outcome-encoded nested rings"
            question="Where is the risk, not just the volume?"
            tradeoff="Two dimensions fit one mark—volume outside, score pressure inside—but the legend must explain the encoding."
          >
            <div className="ring-layout">
              <div className="ring-chart-shell" aria-label="Nested ring chart: response volume and outcome signal">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={RESPONSES}
                      dataKey="count"
                      nameKey="san"
                      cx="50%"
                      cy="50%"
                      innerRadius="58%"
                      outerRadius="90%"
                      paddingAngle={1}
                      stroke="#162124"
                      strokeWidth={2}
                      onClick={(entry, index) => handleChartClick(entry, index)}
                    >
                      {RESPONSES.map((response) => <Cell key={`outer-${response.id}`} fill={response.color} style={{ cursor: "pointer" }} />)}
                    </Pie>
                    <Pie
                      data={ringData}
                      dataKey="pressure"
                      nameKey="san"
                      cx="50%"
                      cy="50%"
                      innerRadius="34%"
                      outerRadius="53%"
                      paddingAngle={2}
                      stroke="#162124"
                      strokeWidth={2}
                      onClick={(entry, index) => handleChartClick(entry, index)}
                    >
                      {ringData.map((response) => <Cell key={`inner-${response.id}`} fill={OUTCOME_COLORS[response.outcomeKey]} style={{ cursor: "pointer" }} />)}
                    </Pie>
                    <Tooltip formatter={(value, name) => name === "pressure" ? `${Number(value).toLocaleString()} pressure index` : `${formatCount(Number(value))} games`} contentStyle={PIE_TOOLTIP_STYLE} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="ring-key">
                <div className="legend-title"><span>How to read it</span><strong>click either ring</strong></div>
                <div className="ring-encoding"><i className="encoding-swatch volume" aria-hidden="true" /><span><strong>Outer ring</strong> response volume</span></div>
                <div className="ring-encoding"><i className="encoding-swatch outcome" aria-hidden="true" /><span><strong>Inner ring</strong> outcome signal</span></div>
                <div className="outcome-legend">
                  {(Object.keys(OUTCOME_COLORS) as OutcomeKey[]).map((key) => (
                    <span key={key}><i style={{ backgroundColor: OUTCOME_COLORS[key] }} aria-hidden="true" />{key}</span>
                  ))}
                </div>
              </div>
            </div>
            <ChartHint>Both rings use the same move order, so an outcome slice still plays its represented legal move.</ChartHint>
            <ResponseList responses={RESPONSES.slice(0, 6)} selectedId={selectedId} onSelect={selectResponse} compact />
          </ConceptCard>

          <ConceptCard
            number="05"
            title="Ranked hybrid for the long tail"
            question="How should a long tail collapse on small screens?"
            tradeoff="Rank and count are fastest to compare, while progressive disclosure preserves rare legal replies without false precision."
          >
            <div className="hybrid-heading">
              <div><span className="mini-kicker">Sorted by sample size</span><h3>{expanded ? "All represented replies" : "The useful first six"}</h3></div>
              <button className="disclosure-button" type="button" onClick={() => setExpanded((value) => !value)} aria-expanded={expanded}>
                {expanded ? "Collapse tail" : "Show 3 more"}<span aria-hidden="true">{expanded ? " −" : " +"}</span>
              </button>
            </div>
            <div className="rank-chart-shell" aria-label="Ranked horizontal bar chart of responses">
              <ResponsiveContainer width="100%" height={expanded ? 330 : 260}>
                <BarChart data={visibleRanked} layout="vertical" margin={{ top: 8, right: 45, bottom: 8, left: 0 }}>
                  <XAxis type="number" hide domain={[0, "dataMax"]} />
                  <YAxis type="category" dataKey="san" width={40} tick={{ fill: "#c5d0cd", fontSize: 12, fontWeight: 700 }} axisLine={false} tickLine={false} />
                  <Tooltip cursor={{ fill: "rgba(231, 164, 94, 0.08)" }} formatter={(value) => `${formatCount(Number(value))} games`} contentStyle={PIE_TOOLTIP_STYLE} />
                  <Bar dataKey="count" radius={[0, 5, 5, 0]} onClick={(entry, index) => handleChartClick(entry, index)} label={{ position: "right", fill: "#94a7a8", fontSize: 11, formatter: (value: unknown) => formatPct(Number(value)) }}>
                    {visibleRanked.map((response) => <Cell key={response.id} fill={response.color} style={{ cursor: "pointer" }} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <ChartHint>Rank is the primary reading; expanding keeps rare moves selectable instead of hiding them in “other.”</ChartHint>
            <ResponseList responses={visibleRanked} selectedId={selectedId} onSelect={selectResponse} compact />
            {!expanded && <p className="list-tail-note">Nf6, g6, and a6 are still available through “Show 3 more”.</p>}
          </ConceptCard>
        </div>
      </section>

      <footer className="document-footer">
        <span><strong>Exploration only.</strong> Simulated corpus data; no trainer records are changed.</span>
        <span>React · TypeScript · Recharts · chess.js · react-chessboard</span>
      </footer>
    </main>
  );
}

export default App;
