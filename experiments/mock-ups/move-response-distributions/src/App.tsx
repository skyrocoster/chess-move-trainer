import { useState, type ReactNode } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

type ResponseMove = {
  id: string;
  san: string;
  uci: string;
  count: number;
  family: string;
  note: string;
  color: string;
  isGroup?: boolean;
};

type DisplayResponse = ResponseMove & {
  pct: number;
  legal: boolean;
};

type ChartEntry = {
  payload?: DisplayResponse;
};

const TOTAL_GAMES = 12_480;

const RESPONSE_SEEDS: ResponseMove[] = [
  {
    id: "e5",
    san: "e5",
    uci: "e7e5",
    count: 4_118,
    family: "Open game",
    note: "Classical development; the centre opens immediately.",
    color: "#e4b76c",
  },
  {
    id: "c5",
    san: "c5",
    uci: "c7c5",
    count: 3_331,
    family: "Sicilian",
    note: "The most ambitious reply, trading symmetry for counterplay.",
    color: "#55bda9",
  },
  {
    id: "c6",
    san: "c6",
    uci: "c7c6",
    count: 1_548,
    family: "Caro-Kann",
    note: "A sturdy centre with a clear light-squared bishop plan.",
    color: "#86a9ef",
  },
  {
    id: "e6",
    san: "e6",
    uci: "e7e6",
    count: 1_228,
    family: "French",
    note: "Black accepts a cramped start to challenge the centre later.",
    color: "#bc8de2",
  },
  {
    id: "d6",
    san: "d6",
    uci: "d7d6",
    count: 742,
    family: "Pirc",
    note: "Flexible and provocative, but White gets the first space claim.",
    color: "#ee8e6c",
  },
  {
    id: "d5",
    san: "d5",
    uci: "d7d5",
    count: 618,
    family: "Scandinavian",
    note: "Immediate contact in the centre; the queen decision follows.",
    color: "#db83a9",
  },
  {
    id: "Nf6",
    san: "Nf6",
    uci: "g8f6",
    count: 493,
    family: "Alekhine",
    note: "Invites White to build a pawn centre and then attacks it.",
    color: "#5eafca",
  },
  {
    id: "g6",
    san: "g6",
    uci: "g7g6",
    count: 402,
    family: "Modern",
    note: "The king-side fianchetto keeps the central commitment hidden.",
    color: "#a5c96b",
  },
  {
    id: "a6",
    san: "a6",
    uci: "a7a6",
    count: 80,
    family: "Rare sidestep",
    note: "A rare waiting move; keep it available without giving it equal weight.",
    color: "#89969a",
  },
];

const BASE_BOARD = new Chess();
BASE_BOARD.move({ from: "e2", to: "e4" });
const AFTER_E4_FEN = BASE_BOARD.fen();
const LEGAL_UCIS = new Set(
  BASE_BOARD.moves({ verbose: true }).map((move) => `${move.from}${move.to}${move.promotion ?? ""}`),
);
const RESPONSES: DisplayResponse[] = RESPONSE_SEEDS.map((response) => ({
  ...response,
  pct: (response.count / TOTAL_GAMES) * 100,
  legal: LEGAL_UCIS.has(response.uci),
}));
const COMMON_RESPONSES = RESPONSES.slice(0, 5);
const TAIL_RESPONSES = RESPONSES.slice(5);
const TAIL_TOTAL = TAIL_RESPONSES.reduce((sum, response) => sum + response.count, 0);
const OTHER_RESPONSE: DisplayResponse = {
  id: "other",
  san: "Other",
  uci: "",
  count: TAIL_TOTAL,
  family: "4 rare replies",
  note: "A grouped slice keeps the common replies readable while preserving a path to every response.",
  color: "#687879",
  isGroup: true,
  pct: (TAIL_TOTAL / TOTAL_GAMES) * 100,
  legal: false,
};
const GROUPED_RESPONSES = [...COMMON_RESPONSES, OTHER_RESPONSE];

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

function getResponseFromEntry(entry: unknown, fallback?: DisplayResponse) {
  if (entry && typeof entry === "object") {
    const candidate = entry as ChartEntry;
    if (candidate.payload?.id) return candidate.payload;
  }
  return fallback;
}

function OutsidePieLabel({
  cx = 0,
  cy = 0,
  midAngle = 0,
  outerRadius = 0,
  percent = 0,
  name = "",
}: {
  cx?: number;
  cy?: number;
  midAngle?: number;
  outerRadius?: number;
  percent?: number;
  name?: string;
}) {
  const radians = Math.PI / 180;
  const lineRadius = Number(outerRadius) + 3;
  const labelRadius = Number(outerRadius) + 22;
  const lineX = Number(cx) + lineRadius * Math.cos(-midAngle * radians);
  const lineY = Number(cy) + lineRadius * Math.sin(-midAngle * radians);
  const labelX = Number(cx) + labelRadius * Math.cos(-midAngle * radians);
  const labelY = Number(cy) + labelRadius * Math.sin(-midAngle * radians);
  const anchor = labelX >= Number(cx) ? "start" : "end";

  return (
    <g>
      <line x1={lineX} y1={lineY} x2={labelX} y2={labelY} stroke="#718188" strokeWidth={1} />
      <text
        x={labelX}
        y={labelY}
        textAnchor={anchor}
        dominantBaseline="central"
        fill="#e3e8e2"
        fontSize={11}
        fontWeight={760}
      >
        {name} {Math.round(percent * 100)}%
      </text>
    </g>
  );
}

function ReplyPie({
  onSelect,
}: {
  onSelect: (response: DisplayResponse) => void;
}) {
  return (
    <div className="pie-chart" aria-label="Pie chart of common Black replies and the grouped rare-reply tail">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={GROUPED_RESPONSES}
            dataKey="count"
            nameKey="san"
            cx="50%"
            cy="50%"
            outerRadius="67%"
            paddingAngle={1.2}
            stroke="#162124"
            strokeWidth={2}
            label={(props) => <OutsidePieLabel {...props} />}
            labelLine={false}
            onClick={(entry, index) => {
              const response = getResponseFromEntry(entry, GROUPED_RESPONSES[index]);
              if (response) onSelect(response);
            }}
          >
            {GROUPED_RESPONSES.map((response) => (
              <Cell key={response.id} fill={response.color} style={{ cursor: "pointer" }} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value, _name, item) => {
              const payload = (item as { payload?: DisplayResponse }).payload;
              return `${formatCount(Number(value))} games${payload?.isGroup ? " · disclosure" : ""}`;
            }}
            contentStyle={PIE_TOOLTIP_STYLE}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

function BoardView({ position }: { position: string }) {
  return (
    <div className="board-frame" aria-label="Simulated live chess board">
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
            borderRadius: "13px",
            overflow: "hidden",
            boxShadow: "0 18px 38px rgba(0, 0, 0, 0.28)",
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

function ReplyControl({
  response,
  selectedId,
  expanded,
  onSelect,
  onToggleOther,
  tail = false,
}: {
  response: DisplayResponse;
  selectedId: string | null;
  expanded: boolean;
  onSelect: (id: string) => void;
  onToggleOther: () => void;
  tail?: boolean;
}) {
  const isOther = response.isGroup;
  const isSelected = !isOther && selectedId === response.id;

  return (
    <button
      className={`reply-control${isSelected ? " is-selected" : ""}${isOther ? " is-disclosure" : ""}${tail ? " is-tail" : ""}`}
      type="button"
      onClick={() => (isOther ? onToggleOther() : onSelect(response.id))}
      aria-pressed={isOther ? undefined : isSelected}
      aria-expanded={isOther ? expanded : undefined}
      aria-controls={isOther ? "rare-reply-controls" : undefined}
      data-testid={`reply-control-${response.id}`}
      title={isOther ? "Show or hide the four rare replies" : `Play ${response.san}`}
    >
      <span className="reply-swatch" style={{ backgroundColor: response.color }} aria-hidden="true" />
      <span className="reply-copy">
        <strong>{response.san}</strong>
        <small>{isOther ? "4 replies · disclosure" : `${response.family} · ${response.uci}`}</small>
      </span>
      <span className="reply-share">
        <strong>{formatPct(response.count)}</strong>
        <small>{isOther ? "grouped share" : "of games"}</small>
      </span>
      <span className="reply-action" aria-hidden="true">
        {isOther ? (expanded ? "−" : "+") : "↗"}
      </span>
    </button>
  );
}

function SectionLabel({ children }: { children: ReactNode }) {
  return <p className="eyebrow">{children}</p>;
}

function App() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [position, setPosition] = useState(AFTER_E4_FEN);
  const [otherOpen, setOtherOpen] = useState(false);
  const [announcement, setAnnouncement] = useState(
    "Choose a common reply, or open Other to inspect the four rare responses.",
  );

  const selected = RESPONSES.find((response) => response.id === selectedId) ?? null;
  const legalCount = RESPONSES.filter((response) => response.legal).length;

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
      `Previewing 1. e4 ${played.san}. ${response.family}; ${formatPct(response.count)} of the simulated games chose this reply.`,
    );
  }

  function toggleOther() {
    setOtherOpen((wasOpen) => {
      const nextOpen = !wasOpen;
      setAnnouncement(
        nextOpen
          ? "Other is open. Choose d5, Nf6, g6, or a6 to play and focus that response."
          : "Other is grouped again. Its four responses remain one disclosure away.",
      );
      return nextOpen;
    });
  }

  function handleChartSelection(response: DisplayResponse) {
    if (response.isGroup) {
      toggleOther();
    } else {
      selectResponse(response.id);
    }
  }

  function resetPosition() {
    setSelectedId(null);
    setPosition(AFTER_E4_FEN);
    setAnnouncement("Position reset to after 1. e4. Choose a reply to preview it.");
  }

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
            <SectionLabel>Response distribution · selected direction 01C</SectionLabel>
            <h1>Keep the common moves<br /><em>in the clear.</em></h1>
            <p className="hero-copy">
              Five frequent replies stay named on the pie. The long tail is still close, grouped behind one honest
              disclosure.
            </p>
          </div>
          <aside className="hero-aside">
            <span className="aside-index">Grouped tail with disclosure</span>
            <p>Other is a way to reveal rare moves, never a move to play.</p>
            <span className="aside-formula">common share → rare detail</span>
          </aside>
        </div>
      </header>

      <section className="live-workbench" aria-labelledby="workbench-heading">
        <div className="workbench-heading">
          <div>
            <SectionLabel>Shared workbench</SectionLabel>
            <h2 id="workbench-heading">Every response stays playable.</h2>
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
              <span className="verified-chip"><span aria-hidden="true">✓</span> {legalCount} replies verified legal</span>
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
                <span className="signal-dot" style={{ backgroundColor: selected?.color ?? "#687879" }} aria-hidden="true" />
              </div>
              <div className="selected-move">
                <strong>{selected?.san ?? "—"}</strong>
                <span>{selected?.uci ?? "Select a sector or response control"}</span>
              </div>
              <div className="detail-grid">
                <div><span>Share</span><strong>{selected ? formatPct(selected.count) : "—"}</strong></div>
                <div><span>Sample</span><strong>{selected ? formatCount(selected.count) : "—"}</strong></div>
                <div><span>Read</span><strong>{selected ? selected.family : "—"}</strong></div>
              </div>
            </div>
            <p className="accessibility-note"><span aria-hidden="true">↳</span> Use the response controls for keyboard and screen-reader access.</p>
          </div>
        </div>
      </section>

      <section className="data-ribbon" aria-label="Sample context">
        <div><span>Position</span><strong>After 1. e4</strong></div>
        <div><span>Sample</span><strong>{formatCount(TOTAL_GAMES)} games</strong></div>
        <div><span>Window</span><strong>Club + master · 2022–25</strong></div>
        <div><span>Data</span><strong>Illustrative, simulated</strong></div>
      </section>

      <section className="distribution-section" aria-labelledby="distribution-heading">
        <div className="section-intro">
          <div>
            <SectionLabel>Black replies after 1. e4</SectionLabel>
            <h2 id="distribution-heading">The tail stays one step away.</h2>
          </div>
          <div className="state-chip" aria-live="polite">
            <span className={`state-dot${otherOpen ? " is-open" : ""}`} aria-hidden="true" />
            Other {otherOpen ? "open" : "grouped"}
          </div>
        </div>

        <div className="distribution-card">
          <div className="distribution-heading">
            <div>
              <h3>Reply share</h3>
              <p>Direct share encoding · SAN + rounded percentage</p>
            </div>
            <span className="sample-note">{formatCount(TOTAL_GAMES)} simulated games</span>
          </div>

          <div className="distribution-layout">
            <div className="chart-panel">
              <ReplyPie onSelect={handleChartSelection} />
              <p className="chart-caption"><span aria-hidden="true">⌁</span> Click a sector to play it. Click Other to disclose its four rare replies.</p>
            </div>

            <div className="controls-panel">
              <div className="control-heading">
                <div>
                  <span className="label">Response controls</span>
                  <strong>Common replies</strong>
                </div>
                <span>5 + Other</span>
              </div>
              <div className="reply-list" aria-label="Common move response controls">
                {COMMON_RESPONSES.map((response) => (
                  <ReplyControl
                    key={response.id}
                    response={response}
                    selectedId={selectedId}
                    expanded={otherOpen}
                    onSelect={selectResponse}
                    onToggleOther={toggleOther}
                  />
                ))}
                <ReplyControl
                  response={OTHER_RESPONSE}
                  selectedId={selectedId}
                  expanded={otherOpen}
                  onSelect={selectResponse}
                  onToggleOther={toggleOther}
                />
              </div>

              <div className="other-note">
                <span className="other-note-mark" style={{ backgroundColor: OTHER_RESPONSE.color }} aria-hidden="true" />
                <div>
                  <strong>Other is a disclosure, not a move.</strong>
                  <p>{otherOpen ? "The individual tail controls are ready below." : "Open it when you need the lower-volume replies."}</p>
                </div>
              </div>

              <button className="inspect-button" type="button" onClick={toggleOther} aria-expanded={otherOpen} aria-controls="rare-reply-controls">
                <span>{otherOpen ? "Hide rare replies" : "Inspect 4 rare replies"}</span>
                <span aria-hidden="true">{otherOpen ? "−" : "+"}</span>
              </button>

              {otherOpen && (
                <div className="tail-disclosure" id="rare-reply-controls">
                  <div className="tail-heading">
                    <span>Less common replies</span>
                    <strong>Individual play controls</strong>
                  </div>
                  <div className="reply-list tail-list" aria-label="Rare move response controls">
                    {TAIL_RESPONSES.map((response) => (
                      <ReplyControl
                        key={response.id}
                        response={response}
                        selectedId={selectedId}
                        expanded={otherOpen}
                        onSelect={selectResponse}
                        onToggleOther={toggleOther}
                        tail
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <footer className="document-footer">
        <span><strong>Exploration only.</strong> Simulated corpus data; no trainer records are changed.</span>
        <span>01C · grouped tail with disclosure</span>
      </footer>
    </main>
  );
}

export default App;
