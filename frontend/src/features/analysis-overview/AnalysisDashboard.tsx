import { useId, type ReactNode } from "react";

import type { StatisticsOverviewResponse } from "../../api/client";
import { Disclosure } from "../design-system/Disclosure";
import { OutcomeTrack } from "../design-system/OutcomeTrack";
import { ProgressMeter } from "../design-system/ProgressMeter";
import { Tabs } from "../design-system/Tabs";
import {
  formatCategory,
  formatDecimal,
  formatInteger,
  formatMonth,
  formatRate,
  formatSignedInteger,
  outcomeLabel,
  type OutcomeRecord,
} from "./analysisOverviewFormatting";
import styles from "./AnalysisDashboard.module.css";
import detailsStyles from "./AnalysisDetails.module.css";

type AnalysisDashboardProps = {
  data: StatisticsOverviewResponse;
};

type CategoryPerformance = StatisticsOverviewResponse["games"]["by_time_class"][number];

function OutcomeBar({ record, compact = false }: { record: OutcomeRecord; compact?: boolean }) {
  return (
    <OutcomeTrack
      compact={compact}
      values={{
        wins: record.win_count,
        draws: record.draw_count,
        losses: record.loss_count,
        unknown: record.unknown_count,
      }}
      accessibleLabel={outcomeLabel(record)}
    />
  );
}

function MetricCard({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <div className={styles.metricCard}>
      <dt>{label}</dt>
      <dd>{value}</dd>
      {note ? <p>{note}</p> : null}
    </div>
  );
}

function SectionHeading({ children, note }: { children: ReactNode; note?: string }) {
  return (
    <div className={styles.sectionHeading}>
      <h2>{children}</h2>
      {note ? <p>{note}</p> : null}
    </div>
  );
}

function BreakdownList({
  title,
  items,
  emptyMessage = "No games are available for this breakdown.",
}: {
  title: string;
  items: CategoryPerformance[];
  emptyMessage?: string;
}) {
  const headingId = useId();
  return (
    <section className={styles.breakdownCard} aria-labelledby={headingId}>
      <h3 id={headingId}>{title}</h3>
      {items.length === 0 ? (
        <p className={styles.muted}>{emptyMessage}</p>
      ) : (
        <ul className={styles.breakdownList}>
          {items.map((item) => (
            <li key={item.category}>
              <div className={styles.breakdownHeader}>
                <span>{formatCategory(item.category)}</span>
                <strong>{formatRate(item.record.score_rate)}</strong>
              </div>
              <OutcomeBar record={item.record} compact />
              <p>
                {formatInteger(item.record.total_count)} games · {item.record.win_count}W ·{" "}
                {item.record.draw_count}D · {item.record.loss_count}L
              </p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function RecordScorecard({ data }: AnalysisDashboardProps) {
  const record = data.games.record;
  const rating = data.games.trainer_rating_progression;
  return (
    <section className={styles.scorecard} aria-labelledby="analysis-record-heading">
      <div className={styles.scoreLead}>
        <p className={styles.eyebrow}>Selected record</p>
        <h2 id="analysis-record-heading">Your results</h2>
        <strong className={styles.scoreRate}>{formatRate(record.score_rate)}</strong>
        <p>Score rate from games with a known result.</p>
      </div>
      <div className={styles.recordBody}>
        <div className={styles.recordTopline}>
          <strong>{formatInteger(record.total_count)} games</strong>
          <span>{outcomeLabel(record)}</span>
        </div>
        <OutcomeBar record={record} />
        <dl className={styles.outcomeLegend}>
          <div className={styles.winMetric}>
            <dt>Wins</dt>
            <dd>{formatInteger(record.win_count)}</dd>
          </div>
          <div className={styles.drawMetric}>
            <dt>Draws</dt>
            <dd>{formatInteger(record.draw_count)}</dd>
          </div>
          <div className={styles.lossMetric}>
            <dt>Losses</dt>
            <dd>{formatInteger(record.loss_count)}</dd>
          </div>
          {record.unknown_count > 0 ? (
            <div className={styles.unknownMetric}>
              <dt>Unknown</dt>
              <dd>{formatInteger(record.unknown_count)}</dd>
            </div>
          ) : null}
          <div>
            <dt>Rating change</dt>
            <dd>{formatSignedInteger(rating.change)}</dd>
          </div>
        </dl>
      </div>
    </section>
  );
}

function RecentForm({ data }: AnalysisDashboardProps) {
  return (
    <section>
      <SectionHeading note="The latest dated games inside the selected scope.">
        Recent form
      </SectionHeading>
      <div className={styles.recentGrid}>
        {data.activity.recent_form.map((window) => (
          <article className={styles.recentCard} key={window.requested_game_count}>
            <span>Last {window.requested_game_count}</span>
            <strong>{formatRate(window.record.score_rate)}</strong>
            <OutcomeBar record={window.record} compact />
            <p>
              {formatInteger(window.dated_game_count)} dated{" "}
              {window.dated_game_count === 1 ? "game" : "games"}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}

function MonthlyActivity({ data }: AnalysisDashboardProps) {
  return (
    <section>
      <SectionHeading note="Results are grouped by the UTC month in which each game started.">
        Month by month
      </SectionHeading>
      {data.activity.by_month.length === 0 ? (
        <p className={detailsStyles.emptySection}>No dated games are available in this scope.</p>
      ) : (
        <ol className={styles.monthList}>
          {data.activity.by_month.map((month) => (
            <li key={month.period}>
              <div>
                <strong>{formatMonth(month.period)}</strong>
                <span>{formatInteger(month.record.total_count)} games</span>
              </div>
              <OutcomeBar record={month.record} compact />
              <strong>{formatRate(month.record.score_rate)}</strong>
              <span className={styles.monthRating}>
                Avg rating {formatInteger(month.average_trainer_rating)}
              </span>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

function PerformancePanel({ data }: AnalysisDashboardProps) {
  const progression = data.games.trainer_rating_progression;
  const streak = data.activity.streaks;
  const currentStreak =
    streak.current_kind === null
      ? "No current streak"
      : `${streak.current_count} ${streak.current_kind}${streak.current_count === 1 ? "" : "s"}`;

  return (
    <div className={styles.tabContent}>
      <RecordScorecard data={data} />
      <dl className={styles.metricGrid}>
        <MetricCard label="Current rating" value={formatInteger(progression.last_rating)} />
        <MetricCard label="Peak rating" value={formatInteger(progression.peak_rating)} />
        <MetricCard
          label="Average rating"
          value={formatInteger(data.games.trainer_rating.average)}
        />
        <MetricCard label="Current streak" value={currentStreak} />
      </dl>
      <RecentForm data={data} />
      <MonthlyActivity data={data} />
      <section>
        <SectionHeading note="Compare score rate and record across common game cuts.">
          Performance breakdown
        </SectionHeading>
        <div className={styles.breakdownGrid}>
          <BreakdownList title="By time class" items={data.games.by_time_class} />
          <BreakdownList title="By colour" items={data.games.by_trainer_color} />
          <BreakdownList title="By rating matchup" items={data.games.by_rating_difference} />
          <BreakdownList title="By game length" items={data.games.by_length_plies} />
        </div>
      </section>
      <Disclosure summary="More game breakdowns">
        <div className={styles.disclosureGrid}>
          <BreakdownList title="By time control" items={data.games.by_time_control} />
          <BreakdownList title="By termination" items={data.games.by_termination_reason} />
        </div>
      </Disclosure>
    </div>
  );
}

function OpeningsPanel({ data }: AnalysisDashboardProps) {
  const openings = data.openings;
  return (
    <div className={styles.tabContent}>
      <dl className={styles.metricGrid}>
        <MetricCard
          label="Classified games"
          value={formatInteger(openings.classified_game_count)}
        />
        <MetricCard
          label="Unclassified games"
          value={formatInteger(openings.unclassified_game_count)}
        />
        <MetricCard
          label="Distinct openings"
          value={formatInteger(openings.distinct_opening_count)}
        />
        <MetricCard label="Openings shown" value={formatInteger(openings.returned_opening_count)} />
      </dl>
      <section>
        <SectionHeading note="Ordered by the backend report for the selected game scope.">
          Opening results
        </SectionHeading>
        {openings.openings.length === 0 ? (
          <p className={detailsStyles.emptySection}>
            No classified openings are available in this scope.
          </p>
        ) : (
          <div
            className={detailsStyles.tableScroller}
            tabIndex={0}
            role="region"
            aria-label="Opening results"
          >
            <table className={detailsStyles.dataTable}>
              <thead>
                <tr>
                  <th scope="col">Opening</th>
                  <th scope="col">Games</th>
                  <th scope="col">Record</th>
                  <th scope="col">Score</th>
                  <th scope="col">Avg rating</th>
                </tr>
              </thead>
              <tbody>
                {openings.openings.map((opening) => (
                  <tr key={opening.key}>
                    <th scope="row">
                      <span className={detailsStyles.eco}>{opening.eco}</span>
                      {opening.name}
                    </th>
                    <td>{formatInteger(opening.record.total_count)}</td>
                    <td>
                      {opening.record.win_count}W · {opening.record.draw_count}D ·{" "}
                      {opening.record.loss_count}L
                    </td>
                    <td>{formatRate(opening.record.score_rate)}</td>
                    <td>{formatInteger(opening.average_trainer_rating)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function CoverageCard({
  title,
  rate,
  detail,
}: {
  title: string;
  rate: number | null;
  detail: string;
}) {
  const percentValue = rate === null ? null : Math.min(1, Math.max(0, rate)) * 100;
  return (
    <article className={detailsStyles.coverageCard}>
      <div className={detailsStyles.coverageHeading}>
        <h3>{title}</h3>
        <strong>{formatRate(rate)}</strong>
      </div>
      <ProgressMeter
        value={percentValue}
        label={title}
        valueText={rate === null ? "No coverage data" : formatRate(rate)}
      />
      <p>{detail}</p>
    </article>
  );
}

const DATA_QUALITY_LABELS: Record<string, string> = {
  missing_outcome_count: "Missing result",
  missing_trainer_rating_count: "Missing learner rating",
  missing_opponent_rating_count: "Missing opponent rating",
  missing_started_at_count: "Missing start time",
  invalid_started_at_count: "Invalid start time",
  missing_ended_at_count: "Missing end time",
  invalid_ended_at_count: "Invalid end time",
  negative_duration_count: "Negative duration",
  missing_time_class_count: "Missing time class",
  missing_time_control_count: "Missing time control",
  missing_termination_reason_count: "Missing termination reason",
  missing_opponent_count: "Missing opponent",
};

function DataQuality({ data }: AnalysisDashboardProps) {
  const issues = Object.entries(data.data_quality).filter(([, count]) => count > 0);
  return (
    <Disclosure
      summary={`Data quality${issues.length === 0 ? " · no flagged gaps" : ` · ${issues.length} flagged fields`}`}
    >
      {issues.length === 0 ? (
        <p className={detailsStyles.qualityClear}>
          No data gaps were flagged for games in this scope.
        </p>
      ) : (
        <dl className={detailsStyles.qualityGrid}>
          {issues.map(([key, count]) => (
            <div key={key}>
              <dt>{DATA_QUALITY_LABELS[key] ?? formatCategory(key)}</dt>
              <dd>{formatInteger(count)}</dd>
            </div>
          ))}
        </dl>
      )}
    </Disclosure>
  );
}

function PreparationPanel({ data }: AnalysisDashboardProps) {
  const analysis = data.analysis;
  const repertoire = data.repertoire;
  const positions = data.positions;
  const balances = repertoire.training_balances;
  return (
    <div className={styles.tabContent}>
      <section>
        <SectionHeading note="Coverage is recalculated inside the selected game scope.">
          Preparation coverage
        </SectionHeading>
        <div className={detailsStyles.coverageGrid}>
          <CoverageCard
            title="Engine analysis"
            rate={analysis.ready_coverage_rate}
            detail={`${formatInteger(analysis.ready_position_count)} of ${formatInteger(analysis.scoped_position_count)} positions ready`}
          />
          <CoverageCard
            title="Move preferences"
            rate={repertoire.preference_coverage_rate}
            detail={`${formatInteger(repertoire.move_preference_position_count)} preferred · ${formatInteger(repertoire.unconfigured_position_count)} unconfigured`}
          />
          <CoverageCard
            title="Preferred-move adherence"
            rate={repertoire.preferred_move_adherence_rate}
            detail={`${formatInteger(repertoire.preferred_move_played_count)} of ${formatInteger(repertoire.preferred_move_opportunity_count)} opportunities`}
          />
        </div>
      </section>

      <section>
        <SectionHeading note="Training balance uses the snapshot date shown above the report.">
          Training readiness
        </SectionHeading>
        <dl className={styles.metricGrid}>
          <MetricCard label="Needs work" value={formatInteger(balances.negative_count)} />
          <MetricCard label="At zero" value={formatInteger(balances.zero_count)} />
          <MetricCard label="Positive balance" value={formatInteger(balances.positive_count)} />
          <MetricCard label="Average balance" value={formatDecimal(balances.summary.average)} />
        </dl>
      </section>

      <section>
        <SectionHeading note="Queue counts show the current engine-analysis state.">
          Position coverage
        </SectionHeading>
        <dl className={styles.metricGrid}>
          <MetricCard
            label="Observed positions"
            value={formatInteger(positions.observed_position_count)}
          />
          <MetricCard
            label="Repeated positions"
            value={formatInteger(positions.repeated_position_count)}
          />
          <MetricCard label="Queued" value={formatInteger(analysis.queued_position_count)} />
          <MetricCard label="Running" value={formatInteger(analysis.running_position_count)} />
        </dl>
        {positions.recurring_positions.length > 0 ? (
          <div
            className={detailsStyles.tableScroller}
            tabIndex={0}
            role="region"
            aria-label="Recurring positions"
          >
            <table className={`${detailsStyles.dataTable} ${detailsStyles.positionTable}`}>
              <thead>
                <tr>
                  <th scope="col">Position FEN</th>
                  <th scope="col">Games</th>
                  <th scope="col">Occurrences</th>
                </tr>
              </thead>
              <tbody>
                {positions.recurring_positions.map((position) => (
                  <tr key={position.fen}>
                    <th scope="row">{position.fen}</th>
                    <td>{formatInteger(position.distinct_game_count)}</td>
                    <td>{formatInteger(position.occurrence_count)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className={detailsStyles.emptySection}>
            No recurring positions are available in this scope.
          </p>
        )}
      </section>
      <DataQuality data={data} />
    </div>
  );
}

export function AnalysisDashboard({ data }: AnalysisDashboardProps) {
  return (
    <Tabs
      ariaLabel="Analysis sections"
      tabs={[
        { id: "performance", label: "Performance", content: <PerformancePanel data={data} /> },
        { id: "openings", label: "Openings", content: <OpeningsPanel data={data} /> },
        { id: "preparation", label: "Preparation", content: <PreparationPanel data={data} /> },
      ]}
    />
  );
}
