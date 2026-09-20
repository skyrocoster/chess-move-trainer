import type { Meta, StoryObj } from "@storybook/react-vite";
import { FamilyPage } from "./FamilyPage";

const meta = {
  title: "Reference/Catalogue/Feedback and Status",
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
      family="Feedback and Status"
      intro={
        <>
          The shared feedback components and the recurring status presentations. The FeedbackCore
          variant matrix is the source of truth for the four severities (information, success,
          warning, error); the panel, page, and inline levels wrap it for their layouts.
        </>
      }
      sections={[
        {
          heading: "Shared feedback levels",
          body: "PanelFeedback sits inside panel-sized regions, PageFeedback sits at the top of a page region, and InlineFeedback carries the same semantics inline. All three delegate a fixed severity map so only consumer props (severity, message, optional heading) vary; the callers pass the live-region role and aria-live attributes that their flow needs — the components add no default live-region semantics on purpose. Coverage comes from Reference/Design System/Feedback Semantic Variants (the shared matrix) plus the per-level stories.",
        },
        {
          heading: "Links",
          links: [
            {
              label: "FeedbackCore — Semantic Variants",
              storyId: "reference-design-system-feedback-semantic-variants--semantic-variants",
              note: "all four severities",
            },
            {
              label: "PanelFeedback — All Severities",
              storyId: "production-design-system-feedback-panel--all-severities",
            },
            {
              label: "PageFeedback — All Severities",
              storyId: "production-design-system-feedback-page--all-severities",
            },
            {
              label: "InlineFeedback — Inline Matrix",
              storyId: "production-design-system-feedback-inline--inline-matrix",
            },
          ],
        },
        {
          heading: "Loading, empty, and retry presentations in features",
          body: "There is no shared spinner or skeleton component. Loading and empty states are composed per feature with the same Materials/themes and feedback tokens. The links below are the representative loading, empty, error, and unavailable stories already in the Production group.",
          links: [
            {
              label: "StatusView — Loading",
              storyId: "production-application-status-status-view--loading",
            },
            {
              label: "StatusView — Unavailable",
              storyId: "production-application-status-status-view--unavailable",
            },
            {
              label: "Line Library — Loading",
              storyId: "production-design-system-components-line-library--loading",
            },
            {
              label: "Line Library — Empty",
              storyId: "production-design-system-components-line-library--empty",
            },
            {
              label: "Move Response Distribution — Loading",
              storyId: "production-application-move-response-distribution-overview--loading",
            },
            {
              label: "Move Response Distribution — No Games",
              storyId: "production-application-move-response-distribution-overview--no-games",
              note: "empty",
            },
            {
              label: "Move Response Distribution — Unavailable With Retry",
              storyId:
                "production-application-move-response-distribution-overview--unavailable-with-retry",
              note: "error with retry",
            },
            {
              label: "Analysis Panel — Request Error",
              storyId: "production-application-analysis-analysis-panel--request-error",
              note: "error",
            },
            {
              label: "Analysis Panel — Request Pending",
              storyId: "production-application-analysis-analysis-panel--request-pending",
              note: "queued/running states",
            },
            {
              label: "Analysis Panel — Terminal Empty",
              storyId: "production-application-analysis-analysis-panel--terminal-empty",
            },
            {
              label: "Preferred Move Panel — Loading",
              storyId: "production-application-repertoire-builder-preferred-move-panel--loading",
            },
            {
              label: "Preferred Move Panel — Read Error",
              storyId: "production-application-repertoire-builder-preferred-move-panel--read-error",
            },
            {
              label: "Page Not Found — Default",
              storyId: "production-application-shell-page-not-found--default",
            },
          ],
        },
        {
          heading: "Meters and progress displays",
          body: "The only meter-like display today is the engine evaluation bar: a horizontal bar with a best-line marker and clamped range handling. There is no generic progress-bar component.",
          links: [
            {
              label: "Evaluation Bar — Running",
              storyId: "production-application-analysis-evaluation-bar--running",
            },
            {
              label: "Evaluation Bar — Completed Positive Mate",
              storyId: "production-application-analysis-evaluation-bar--completed-positive-mate",
            },
          ],
        },
      ]}
    />
  ),
};
