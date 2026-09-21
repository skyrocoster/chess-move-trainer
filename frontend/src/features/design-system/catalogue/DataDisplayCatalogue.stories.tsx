import type { Meta, StoryObj } from "@storybook/react-vite";
import { FamilyPage } from "./FamilyPage";

const meta = {
  title: "Reference/Catalogue/Data Display and Feature Compositions",
  tags: ["status-reference"],
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta;

export default meta;

type Story = StoryObj<typeof meta>;

export const Docs: Story = {
  render: () => (
    <FamilyPage
      family="Data Display and Feature Compositions"
      intro="Data displays (charts, calendars, meters, chess-specific views) plus the larger production compositions that show how shared components are currently assembled inside real features."
      sections={[
        {
          heading: "Foundational content primitives",
          body: "Avatar supplies an image fallback, ScrollArea adds custom scrollbars around a native scroll viewport, and Separator provides an accessible horizontal or vertical boundary. These are deliberately content- and layout-neutral so features can set their own dimensions.",
          links: [
            {
              label: "Content Primitives — Avatar",
              storyId: "production-design-system-base-ui-content-primitives--avatar-examples",
            },
            {
              label: "Content Primitives — Scroll Area",
              storyId: "production-design-system-base-ui-content-primitives--scroll-area-example",
            },
            {
              label: "Content Primitives — Separator",
              storyId: "production-design-system-base-ui-content-primitives--separator-example",
            },
          ],
        },
        {
          heading: "Charts and meters",
          body: "MoveResponseDistribution is a treegame-sector chart feature with a pull-to-parent tag; the distribution overview story set covers loading, empty (NoGames, MatchingGamesWithoutNextMoves), retry, density, keyboard, and constrained-width states. The evaluation bar is the meter-style display. OutcomeTrack shows win/draw/loss shares with an optional unknown segment, and ProgressMeter is the shared determinate progress display with an unavailable state.",
          links: [
            {
              label: "Move Response Distribution Overview — Available With Tail",
              storyId:
                "production-application-move-response-distribution-overview--available-with-tail",
            },
            {
              label: "Move Response Distribution Chart — Available",
              storyId: "production-application-move-response-distribution-chart--available",
            },
            {
              label: "Move Response Distribution Controls — Common Replies",
              storyId: "production-application-move-response-distribution-controls--common-replies",
            },
            {
              label: "Evaluation Bar — BestLine",
              storyId: "production-application-analysis-evaluation-bar--best-line",
              note: "meter display",
            },
            {
              label: "Position Reach Frequency — Positive Black",
              storyId: "production-application-position-reach-frequency--positive-black",
            },
            {
              label: "Outcome Track — With Unknown Segment",
              storyId: "production-design-system-components-outcome-track--with-unknown",
            },
            {
              label: "Progress Meter — Determinate",
              storyId: "production-design-system-components-progress-meter--determinate",
            },
            {
              label: "Progress Meter — Unavailable",
              storyId: "production-design-system-components-progress-meter--unavailable",
            },
          ],
        },
        {
          heading: "Calendars",
          body: "CalendarDate is the shared popover-hosted date field, and the in-development schedule prototype embeds a calendar with draft highlighting (OpenEndedDraft shows an open-ended draft; NarrowCalendar shows narrow behavior).",
          links: [
            {
              label: "Calendar Date — Current Day And Future Disabled",
              storyId:
                "production-design-system-components-calendar-date--current-day-and-future-disabled",
            },
            {
              label: "Preferred Move Effective Dates (In Development) — Calendar With Draft",
              storyId:
                "in-development-application-repertoire-builder-preferred-move-effective-dates--calendar-with-draft",
              note: "interactive production composition",
            },
            {
              label: "Preferred Move Effective Dates (In Development) — Narrow Calendar",
              storyId:
                "in-development-application-repertoire-builder-preferred-move-effective-dates--narrow-calendar",
            },
          ],
        },
        {
          heading: "Chess-specific displays",
          body: "The board adapter family renders FEN positions with coordinates, last-move highlights, black orientation, invalid FEN handling, and expanded position descriptions; the move history component and the line-library tree are chess-specific hierarchical displays.",
          links: [
            {
              label: "Read-only Board — Rich Position",
              storyId: "production-application-board-read-only-board--rich-position",
            },
            {
              label: "Read-only Board — Black Orientation",
              storyId: "production-application-board-read-only-board--black-orientation",
            },
            {
              label: "Read-only Board — Invalid FEN",
              storyId: "production-application-board-read-only-board--invalid-fen",
              note: "error handling",
            },
            {
              label: "Interactive Board — Copy Feedback",
              storyId: "production-application-board-interactive-board--copy-feedback",
            },
            {
              label: "Move History — Interactive",
              storyId: "production-application-move-history--interactive",
              note: "interactive navigation",
            },
            {
              label: "Line Library Tree — Default",
              storyId: "production-design-system-components-line-library-tree--default",
            },
          ],
        },
        {
          heading: "Production feature compositions",
          body: "The repertoire builder workspace stories are the largest compositions that assemble board lanes, preferred move panels, distribution charts, promotions, and keyboard flows together, at wide, medium, and constrained sizes.",
          links: [
            {
              label: "Repertoire Builder Workspace — Candidate Activation",
              storyId:
                "production-application-repertoire-builder-workspace-core--candidate-activation",
              note: "multi-component interaction",
            },
            {
              label: "Repertoire Builder Workspace — Response Distribution Integration",
              storyId:
                "production-application-repertoire-builder-workspace-core--response-distribution-integration",
            },
            {
              label: "Repertoire Builder Workspace Preferred Move — Accessibility And Responsive",
              storyId:
                "production-application-repertoire-builder-workspace-preferred-move--accessibility-and-responsive",
            },
            {
              label: "Reference/Storybook Fixtures — Promotion Picker Harness",
              storyId: "reference-storybook-fixtures-promotion-picker-harness--default",
            },
          ],
        },
      ]}
    />
  ),
};
