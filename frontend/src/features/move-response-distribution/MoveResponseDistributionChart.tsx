import { useId, useState } from "react";
import { Cell, Pie, PieChart, Tooltip } from "recharts";
import type { TooltipContentProps } from "recharts";

import type {
  MoveResponseDistributionOtherView,
  MoveResponseDistributionReplyView,
} from "./moveResponseDistributionModel";
import styles from "./MoveResponseDistribution.module.css";

type MoveChartItem =
  | {
      kind: "reply";
      key: string;
      label: string;
      value: number;
      percentageLabel: string;
      childUci: string;
    }
  | {
      kind: "other";
      key: "other";
      label: "Other";
      value: number;
      percentageLabel: string;
    };

export type MoveResponseDistributionChartProps = {
  replies: readonly MoveResponseDistributionReplyView[];
  other: MoveResponseDistributionOtherView | null;
  otherExpanded: boolean;
  onMoveSelect: (childUci: string) => void;
  onOtherToggle: () => void;
};

const SECTOR_COLORS = [
  "var(--md-sys-color-primary)",
  "var(--md-sys-color-secondary)",
  "var(--md-sys-color-tertiary)",
  "var(--md-sys-color-primary-container)",
  "var(--md-sys-color-secondary-container)",
  "var(--md-sys-color-outline)",
] as const;

// The chart is a fixed square, so the label geometry below can mirror the
// Recharts pie math exactly: with paddingAngle 0 and startAngle 0 -> endAngle
// 360, sector mid angles are (cumulative + fraction / 2) * 360 degrees, and
// Recharts maps an angle to x = cx + r * cos(angle), y = cy - r * sin(angle).
const CHART_SIZE = 240;
const CHART_MARGIN = 20;
const OUTER_RADIUS_RATIO = 0.6;
const LEADER_LINE_START_INSET = 2;
const LABEL_RADIUS_OFFSET = 10;
const LABEL_MIN_GAP = 18;
const LABEL_EDGE_INSET = 3;
const LABEL_CHAR_WIDTH = 6.2;
const LABEL_PIE_CLEARANCE = 4;

type PieLabelLayout = {
  x: number;
  y: number;
  anchor: "start" | "end";
  lineX: number;
  lineY: number;
};

type LabelSideEntry = {
  key: string;
  anchor: "start" | "end";
  textWidth: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
};

function labelText(item: MoveChartItem): string {
  return `${item.label} ${item.percentageLabel}`;
}

// Pull a resolved label stack back inside the frame without losing the
// minimum vertical gap: first lower any stack that runs past the bottom
// edge, then raise any stack that runs past the top edge.
function clampLabelStack(entries: LabelSideEntry[]) {
  const maxY = CHART_SIZE - LABEL_EDGE_INSET;
  if (entries[entries.length - 1]!.y > maxY) {
    for (let index = entries.length - 1; index >= 0; index -= 1) {
      const current = entries[index]!;
      const below = entries[index + 1];
      const ceiling = below ? below.y - LABEL_MIN_GAP : maxY;
      current.y = Math.min(current.y, ceiling);
    }
  }
  const minY = LABEL_EDGE_INSET;
  if (entries[0]!.y < minY) {
    for (let index = 0; index < entries.length; index += 1) {
      const current = entries[index]!;
      const above = entries[index - 1];
      const floor = above ? above.y + LABEL_MIN_GAP : minY;
      current.y = Math.max(current.y, floor);
    }
  }
}

// Nudge labels on one side apart vertically so their texts cannot overlap,
// then balance the resolved stack around the side's natural centroid and
// clamp it back inside the frame. A dense run of tiny adjacent sectors
// (whose leader lines all leave the pie edge from nearly the same point)
// therefore spreads symmetrically above and below its convergence point
// with a readable gap instead of hanging in a cramped stack below it.
// Labels keep their horizontal anchor position; only y moves, so the
// resolved leaders fan out without crossing one another.
function resolveLabelSide(entries: LabelSideEntry[]) {
  if (entries.length === 0) return;
  entries.sort((a, b) => a.y - b.y);
  const naturalCentroid = entries.reduce((sum, entry) => sum + entry.y, 0) / entries.length;
  for (let index = 1; index < entries.length; index += 1) {
    const previous = entries[index - 1]!;
    const current = entries[index]!;
    if (current.y - previous.y < LABEL_MIN_GAP) {
      current.y = previous.y + LABEL_MIN_GAP;
    }
  }
  clampLabelStack(entries);
  const span = (entries.length - 1) * LABEL_MIN_GAP;
  const desiredCentroid = Math.min(
    Math.max(naturalCentroid, LABEL_EDGE_INSET + span / 2),
    CHART_SIZE - LABEL_EDGE_INSET - span / 2,
  );
  const resolvedCentroid = entries.reduce((sum, entry) => sum + entry.y, 0) / entries.length;
  const delta = desiredCentroid - resolvedCentroid;
  if (delta !== 0) {
    for (const entry of entries) entry.y += delta;
    clampLabelStack(entries);
  }
}

function computePieLabelLayouts(items: readonly MoveChartItem[]): Map<string, PieLabelLayout> {
  const layouts = new Map<string, PieLabelLayout>();
  const total = items.reduce((sum, item) => sum + item.value, 0);
  if (total <= 0) return layouts;

  const center = CHART_SIZE / 2;
  const maxPieRadius = (CHART_SIZE - CHART_MARGIN * 2) / 2;
  const outerRadius = maxPieRadius * OUTER_RADIUS_RATIO;
  const idealRadius = outerRadius + LABEL_RADIUS_OFFSET;
  const leaderRadius = outerRadius + LEADER_LINE_START_INSET;

  const right: LabelSideEntry[] = [];
  const left: LabelSideEntry[] = [];
  let cumulative = 0;
  for (const item of items) {
    const fraction = item.value / total;
    // cumulative + fraction / 2 is a fraction of the full circle, so it maps
    // to radians with a full 2 * Math.PI turn.
    const midAngle = (cumulative + fraction / 2) * 2 * Math.PI;
    cumulative += fraction;
    const vx = Math.cos(midAngle);
    const vy = -Math.sin(midAngle);
    const anchor = vx >= 0 ? "start" : "end";
    const entry: LabelSideEntry = {
      key: item.key,
      anchor,
      textWidth: labelText(item).length * LABEL_CHAR_WIDTH,
      x: center + idealRadius * vx,
      y: center + idealRadius * vy,
      vx,
      vy,
    };
    (anchor === "start" ? right : left).push(entry);
  }

  resolveLabelSide(right);
  resolveLabelSide(left);
  for (const entry of [...right, ...left]) {
    // Keep the anchored text inside the frame by pulling it inward when it
    // would cross the frame edge.
    const inwardLimit =
      entry.anchor === "start"
        ? CHART_SIZE - LABEL_EDGE_INSET - entry.textWidth
        : LABEL_EDGE_INSET + entry.textWidth;
    let x =
      entry.anchor === "start" ? Math.min(entry.x, inwardLimit) : Math.max(entry.x, inwardLimit);
    // Keep the text clear of the pie disc at the label's final height (the
    // y resolution can move a label well away from its sector). When the
    // clearance and the frame limit conflict, staying inside the frame wins.
    const verticalOffset = entry.y - center;
    const pieHalfChord = Math.sqrt(
      Math.max(0, outerRadius * outerRadius - verticalOffset * verticalOffset),
    );
    const clearX =
      entry.anchor === "start"
        ? center + pieHalfChord + LABEL_PIE_CLEARANCE
        : center - pieHalfChord - LABEL_PIE_CLEARANCE;
    x = entry.anchor === "start" ? Math.max(x, clearX) : Math.min(x, clearX);
    x = entry.anchor === "start" ? Math.min(x, inwardLimit) : Math.max(x, inwardLimit);
    layouts.set(entry.key, {
      x,
      y: entry.y,
      anchor: entry.anchor,
      lineX: center + leaderRadius * entry.vx,
      lineY: center + leaderRadius * entry.vy,
    });
  }
  return layouts;
}

function isMoveChartItem(value: unknown): value is MoveChartItem {
  if (typeof value !== "object" || value === null || !("kind" in value)) return false;
  return value.kind === "reply" || value.kind === "other";
}

function renderTooltip({ active, payload }: TooltipContentProps) {
  if (!active || !payload?.length) return null;
  const item = payload[0]?.payload;
  if (!isMoveChartItem(item)) return null;

  return (
    <div className={styles.tooltip} role="tooltip">
      <strong className={styles.tooltipLabel}>{item.label}</strong>
      <span className={styles.tooltipMetric}>{item.value} games</span>
      <span className={styles.tooltipMetric}>{item.percentageLabel}</span>
    </div>
  );
}

export function MoveResponseDistributionChart({
  replies,
  other,
  otherExpanded,
  onMoveSelect,
  onOtherToggle,
}: MoveResponseDistributionChartProps) {
  const descriptionId = useId();
  const [hoveredKey, setHoveredKey] = useState<string | null>(null);
  const data: MoveChartItem[] = [
    ...replies.map((reply) => ({
      kind: "reply" as const,
      key: reply.child_uci,
      label: reply.san,
      value: reply.distinct_game_count,
      percentageLabel: reply.percentageLabel,
      childUci: reply.child_uci,
    })),
    ...(other
      ? [
          {
            kind: "other" as const,
            key: "other" as const,
            label: "Other" as const,
            value: other.distinct_game_count,
            percentageLabel: other.percentageLabel,
          },
        ]
      : []),
  ];
  const visibleHoveredKey = data.some((item) => item.key === hoveredKey) ? hoveredKey : null;
  const labelLayouts = computePieLabelLayouts(data);

  function handleChartClick(_entry: unknown, index: number) {
    const item = data[index];
    if (!item) return;
    if (item.kind === "other") {
      onOtherToggle();
      return;
    }
    onMoveSelect(item.childUci);
  }

  function handleChartMouseEnter(_entry: unknown, index: number) {
    setHoveredKey(data[index]?.key ?? null);
  }

  function handleChartMouseLeave() {
    setHoveredKey(null);
  }

  function renderLabel(labelProps: unknown) {
    if (typeof labelProps !== "object" || labelProps === null || !("payload" in labelProps)) {
      return null;
    }
    const payload = labelProps.payload;
    if (!isMoveChartItem(payload)) return null;
    const layout = labelLayouts.get(payload.key);
    if (!layout) return null;
    return (
      <g className={styles.chartLabel} pointerEvents="none">
        <line
          x1={layout.lineX}
          y1={layout.lineY}
          x2={layout.x}
          y2={layout.y}
          stroke="currentColor"
          strokeOpacity={0.55}
          strokeWidth={1}
        />
        <text
          x={layout.x}
          y={layout.y}
          textAnchor={layout.anchor}
          dominantBaseline="central"
          fill="currentColor"
          fontSize={11}
          fontWeight={600}
        >
          {labelText(payload)}
        </text>
      </g>
    );
  }

  return (
    <div
      className={styles.chartFrame}
      data-testid="move-response-distribution-chart"
      role="img"
      aria-label="Move response distribution chart"
      aria-describedby={descriptionId}
      data-other-expanded={otherExpanded ? "true" : "false"}
    >
      <p className={styles.visuallyHidden} id={descriptionId}>
        Pie chart of replies by distinct matching games. The text controls provide the complete
        keyboard-operable reply list.
      </p>
      <PieChart
        width={CHART_SIZE}
        height={CHART_SIZE}
        margin={{
          top: CHART_MARGIN,
          right: CHART_MARGIN,
          bottom: CHART_MARGIN,
          left: CHART_MARGIN,
        }}
      >
        <Pie
          data={data}
          dataKey="value"
          nameKey="label"
          cx="50%"
          cy="50%"
          outerRadius="60%"
          label={renderLabel}
          labelLine={false}
          isAnimationActive={false}
          onClick={handleChartClick}
          onMouseEnter={handleChartMouseEnter}
          onMouseLeave={handleChartMouseLeave}
        >
          {data.map((item, index) => {
            const isHovered = visibleHoveredKey !== null;
            const isHoveredSector = item.key === visibleHoveredKey;
            return (
              <Cell
                key={item.key}
                fill={SECTOR_COLORS[index % SECTOR_COLORS.length]}
                data-hovered={isHovered ? (isHoveredSector ? "true" : "false") : undefined}
              />
            );
          })}
        </Pie>
        {/* Snapping (not animated) keeps the tooltip pinned to the cursor;
            escaping the view box stops the chart clamping it away from the
            mouse when the cursor is near the chart edge. */}
        <Tooltip
          trigger="hover"
          content={renderTooltip}
          isAnimationActive={false}
          allowEscapeViewBox={{ x: true, y: true }}
        />
      </PieChart>
    </div>
  );
}
