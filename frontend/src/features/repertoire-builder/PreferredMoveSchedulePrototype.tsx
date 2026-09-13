import "@fullcalendar/react/skeleton.css";
import "@fullcalendar/react/themes/monarch/theme.css";

import FullCalendar, {
  type CalendarRef,
  type DateSelectInfo,
  type EventInput,
} from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/react/daygrid";
import interactionPlugin from "@fullcalendar/react/interaction";
import monarchThemePlugin from "@fullcalendar/react/themes/monarch";
import { useEffect, useMemo, useRef, useState } from "react";

import { Button } from "../design-system/Button";
import styles from "./PreferredMoveSchedulePrototype.module.css";

export type PreferredMoveSchedulePeriod = {
  id: string;
  move: { san: string; uci: string } | null;
  effectiveFrom: string;
  effectiveUntil: string | null;
};

export type PreferredMoveScheduleRange = {
  effectiveFrom: string;
  effectiveUntil: string | null;
};

export type PreferredMoveScheduleAction = "assign" | "no_preference" | "clear";

export type PreferredMoveSchedulePrototypeProps = {
  selectedMove: { san: string; uci: string };
  periods: PreferredMoveSchedulePeriod[];
  initialDate: string;
  initialSelection?: { effectiveFrom: string; effectiveUntil: string };
  onApply?: (action: PreferredMoveScheduleAction, range: PreferredMoveScheduleRange) => void;
};

function parseIsoDay(value: string): Date {
  return new Date(`${value}T12:00:00.000Z`);
}

function formatDay(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(parseIsoDay(value));
}

function previousDay(value: string): string {
  const date = parseIsoDay(value);
  date.setUTCDate(date.getUTCDate() - 1);
  return date.toISOString().slice(0, 10);
}

function oneYearAfter(value: string): string {
  const date = parseIsoDay(value);
  date.setUTCFullYear(date.getUTCFullYear() + 1);
  return date.toISOString().slice(0, 10);
}

function formatRange(range: PreferredMoveScheduleRange): string {
  if (range.effectiveUntil === null) return `From ${formatDay(range.effectiveFrom)} onward`;
  const inclusiveEnd = previousDay(range.effectiveUntil);
  if (inclusiveEnd === range.effectiveFrom) return formatDay(range.effectiveFrom);
  return `${formatDay(range.effectiveFrom)} – ${formatDay(inclusiveEnd)}`;
}

function actionLabel(action: PreferredMoveScheduleAction, moveSan: string): string {
  switch (action) {
    case "assign":
      return moveSan;
    case "no_preference":
      return "No preferred move";
    case "clear":
      return "Unconfigured";
  }
}

export function PreferredMoveSchedulePrototype({
  selectedMove,
  periods,
  initialDate,
  initialSelection,
  onApply = () => undefined,
}: PreferredMoveSchedulePrototypeProps) {
  const calendarRef = useRef<CalendarRef>(null);
  const [draft, setDraft] = useState<PreferredMoveScheduleRange | null>(
    initialSelection ?? null,
  );
  const [continuesIndefinitely, setContinuesIndefinitely] = useState(false);
  const [feedback, setFeedback] = useState("");

  const calendarEvents = useMemo<EventInput[]>(() => {
    const openEndedDisplayUntil = oneYearAfter(initialDate);

    return periods.map((period) => {
      const isSelectedMove = period.move?.uci === selectedMove.uci;
      const eventClass = period.move
        ? isSelectedMove
          ? styles.selectedMovePeriod
          : styles.movePeriod
        : styles.noPreferencePeriod;

      return {
        id: period.id,
        title: period.move
          ? `${period.move.san} · ${period.move.uci}${period.effectiveUntil ? "" : " · ongoing"}`
          : "No preferred move",
        start: period.effectiveFrom,
        end: period.effectiveUntil ?? openEndedDisplayUntil,
        allDay: true,
        className: eventClass,
        extendedProps: {
          effectiveUntil: period.effectiveUntil,
        },
      };
    });
  }, [initialDate, periods, selectedMove.uci]);

  useEffect(() => {
    if (!initialSelection) return;
    calendarRef.current?.getApi().select(
      initialSelection.effectiveFrom,
      initialSelection.effectiveUntil,
    );
  }, [initialSelection]);

  const handleSelect = (selection: DateSelectInfo) => {
    setDraft({ effectiveFrom: selection.startStr, effectiveUntil: selection.endStr });
    setContinuesIndefinitely(false);
    setFeedback("");
  };

  const applyDraft = (action: PreferredMoveScheduleAction) => {
    if (!draft) return;
    const range = {
      effectiveFrom: draft.effectiveFrom,
      effectiveUntil: continuesIndefinitely ? null : draft.effectiveUntil,
    };
    onApply(action, range);
    setFeedback(`${actionLabel(action, selectedMove.san)} drafted for ${formatRange(range)}.`);
  };

  const displayedDraft = draft
    ? {
        effectiveFrom: draft.effectiveFrom,
        effectiveUntil: continuesIndefinitely ? null : draft.effectiveUntil,
      }
    : null;

  return (
    <main className={styles.frame}>
      <section className={styles.prototype} aria-labelledby="preferred-schedule-heading">
        <header className={styles.header}>
          <div>
            <p className={styles.eyebrow}>Preferred move</p>
            <h1 className={styles.heading} id="preferred-schedule-heading">
              Effective-date schedule
            </h1>
            <p className={styles.introduction}>
              Drag across dates to choose when the selected move should apply. Existing periods
              remain visible while you make the change.
            </p>
          </div>
          <div className={styles.selectedMove} aria-label="Selected move">
            <span>Selected move</span>
            <strong>{selectedMove.san}</strong>
            <small>{selectedMove.uci}</small>
          </div>
        </header>

        <div className={styles.legend} aria-label="Calendar legend">
          <span><i className={styles.moveSwatch} aria-hidden="true" />Preferred move</span>
          <span><i className={styles.selectedSwatch} aria-hidden="true" />Selected move</span>
          <span><i className={styles.emptySwatch} aria-hidden="true" />No preference</span>
          <span><i className={styles.unconfiguredSwatch} aria-hidden="true" />Unconfigured</span>
        </div>

        <div className={styles.content}>
          <section className={styles.calendarPanel} aria-label="Preferred move effective-date calendar">
            <div className={styles.calendar}>
              <FullCalendar
                ref={calendarRef}
                plugins={[monarchThemePlugin, dayGridPlugin, interactionPlugin]}
                colorScheme="dark"
                initialView="dayGridMonth"
                initialDate={initialDate}
                timeZone="UTC"
                height="auto"
                fixedWeekCount={false}
                dayMaxEventRows={2}
                selectable
                selectMirror
                selectMinDistance={4}
                unselectAuto={false}
                select={handleSelect}
                events={calendarEvents}
                eventContent={(eventInfo) => (
                  <span className={styles.eventContent}>{eventInfo.event.title}</span>
                )}
                dayHeaderContent={(dayInfo) => <span>{dayInfo.text}</span>}
                dayHeaderDidMount={(dayInfo) => {
                  if (dayInfo.el.querySelector(`.${styles.visuallyHidden}`)) return;
                  const accessibleText = document.createElement("span");
                  accessibleText.className = styles.visuallyHidden;
                  accessibleText.textContent = dayInfo.weekdayText;
                  dayInfo.el.append(accessibleText);
                }}
                headerToolbar={{ start: "title", center: "", end: "today prev,next" }}
              />
            </div>
          </section>

          <aside className={styles.schedulePanel} aria-label="Schedule details">
            <section className={styles.draftCard} aria-labelledby="draft-heading">
              <div>
                <p className={styles.cardLabel}>Draft change</p>
                <h2 className={styles.cardHeading} id="draft-heading">
                  {displayedDraft ? formatRange(displayedDraft) : "Choose a date range"}
                </h2>
              </div>

              {draft ? (
                <>
                  <label className={styles.ongoingControl}>
                    <input
                      type="checkbox"
                      checked={continuesIndefinitely}
                      onChange={(event) => setContinuesIndefinitely(event.target.checked)}
                    />
                    Continue indefinitely
                  </label>
                  <div className={styles.actions} aria-label="Apply draft change">
                    <Button size="sm" onClick={() => applyDraft("assign")}>
                      Use {selectedMove.san}
                    </Button>
                    <Button size="sm" variant="secondary" onClick={() => applyDraft("no_preference")}>
                      No preferred move
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => applyDraft("clear")}>
                      Clear dates
                    </Button>
                  </div>
                </>
              ) : (
                <p className={styles.draftHint}>Drag or click between a start and end date.</p>
              )}

              <p className={styles.feedback} role="status" aria-live="polite">
                {feedback}
              </p>
            </section>

            <section className={styles.periodListSection} aria-labelledby="period-list-heading">
              <div className={styles.periodListHeader}>
                <h2 id="period-list-heading">Current schedule</h2>
                <span>{periods.length} periods</span>
              </div>
              <ol className={styles.periodList}>
                {periods.map((period) => (
                  <li key={period.id}>
                    <i
                      className={period.move ? styles.moveSwatch : styles.emptySwatch}
                      aria-hidden="true"
                    />
                    <span>
                      <strong>{period.move?.san ?? "No preferred move"}</strong>
                      <small>{formatRange(period)}</small>
                    </span>
                  </li>
                ))}
              </ol>
            </section>
          </aside>
        </div>
      </section>
    </main>
  );
}
