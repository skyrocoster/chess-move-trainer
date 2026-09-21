import type { Meta, StoryObj } from "@storybook/react-vite";
import { FamilyPage } from "./FamilyPage";

const meta = {
  title: "Reference/Catalogue/Surfaces and Layout",
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
      family="Surfaces and Layout"
      intro={
        <>
          Panel- and board-like content surfaces and the layout stages that place them. There is
          intentionally no generic Panel, Surface, Card, or shared panel-stack primitive in this
          inventory; every surface below is a feature-level composition.
        </>
      }
      sections={[
        {
          heading: "Shell and page boundaries",
          body: "AppShell is the production shell: it hosts the navigation drawer at narrow widths and the healthy/loading/unavailable page states. PageContentBoundary owns the page-level boundary around content.",
          links: [
            {
              label: "App Shell — Wide Healthy",
              storyId: "production-application-shell-app-shell--wide-healthy",
            },
            {
              label: "App Shell — Constrained Open",
              storyId: "production-application-shell-app-shell--constrained-open",
              note: "drawer open (overlays usage)",
            },
            {
              label: "App Shell — Loading",
              storyId: "production-application-shell-app-shell--loading",
            },
            {
              label: "Page Content Boundary — Healthy Content",
              storyId: "production-application-shell-page-content-boundary--healthy-content",
            },
          ],
        },
        {
          heading: "Analysis, game, and repertoire panels",
          body: "The recurring application surfaces: the analysis panel with its full request lifecycle, the reusable game loader, the preferred move panel with its gates, saves, and overflow variants, and the distribution/inspection panels.",
          links: [
            {
              label: "Analysis Panel — Constrained Ready",
              storyId: "production-application-analysis-analysis-panel--constrained-ready",
            },
            {
              label: "Analysis Panel — ActiveWithResult",
              storyId: "production-application-analysis-analysis-panel--active-with-result",
            },
            {
              label: "Game Loader — Ready",
              storyId: "production-application-game-game-loader--ready",
            },
            {
              label: "Game Loader — Game Not Found",
              storyId: "production-application-game-game-loader--game-not-found",
              note: "error state",
            },
            {
              label: "Preferred Move Panel — EmptyEmpty",
              storyId:
                "production-application-repertoire-builder-preferred-move-panel--empty-empty",
              note: "empty state",
            },
            {
              label: "Preferred Move Panel — First Choice",
              storyId:
                "production-application-repertoire-builder-preferred-move-panel--first-choice",
            },
            {
              label: "Preferred Move Panel — Overflow Long Copy Desktop",
              storyId:
                "production-application-repertoire-builder-preferred-move-panel--overflow-long-copy-desktop",
            },
            {
              label: "Repertoire Session Panel — Session Facts Only",
              storyId:
                "production-application-repertoire-builder-session-panel--session-facts-only",
            },
            {
              label: "Preferred Move Primitives — Primitives",
              storyId:
                "production-application-repertoire-builder-preferred-move-primitives--primitives",
            },
          ],
        },
        {
          heading: "Board surfaces",
          body: "The board adapter family: read-only boards, interactive answer boards with their answer states, the control toolbar, evaluation stage, and position descriptions.",
          links: [
            {
              label: "Read-only Board — Default Valid Starting Position",
              storyId:
                "production-application-board-read-only-board--default-valid-starting-position",
            },
            {
              label: "Read-only Board — Constrained Width",
              storyId: "production-application-board-read-only-board--constrained-width",
              note: "narrow-width behavior",
            },
            {
              label: "Interactive Board — Empty Origin",
              storyId: "production-application-board-interactive-board--empty-origin",
            },
            {
              label: "Interactive Board — Answer Correct",
              storyId: "production-application-board-interactive-board--answer-correct",
              note: "selected/feedback states",
            },
            {
              label: "Board Controls — Initial Boundary",
              storyId: "production-application-board-board-controls--initial-boundary",
            },
            {
              label: "Board Controls — Constrained",
              storyId: "production-application-board-board-controls--constrained",
            },
            {
              label: "Evaluation Stage — Starting Position",
              storyId: "production-application-board-evaluation-stage--starting-position",
            },
            {
              label: "Position Description — Rich Black Orientation",
              storyId: "production-application-board-position-description--rich-black-orientation",
            },
          ],
        },
        {
          heading: "Resizable stages and breakpoints",
          body: "The responsive stages live with their feature owners. The responsive-stage stories pin the exact 699/700 and 1039/1040 container boundary widths, and the workspace stories show wide, medium, and constrained layouts of the full repertoire workspace.",
          links: [
            {
              label: "Repertoire Responsive Stage — Boundary 699",
              storyId: "production-application-repertoire-builder-responsive-stage--boundary-699",
            },
            {
              label: "Repertoire Responsive Stage — Boundary 1040",
              storyId: "production-application-repertoire-builder-responsive-stage--boundary-1040",
            },
            {
              label: "Repertoire Builder Workspace — Wide",
              storyId: "production-application-repertoire-builder-workspace-core--wide",
            },
            {
              label: "Repertoire Builder Workspace — Medium",
              storyId: "production-application-repertoire-builder-workspace-core--medium",
            },
            {
              label: "Repertoire Builder Workspace — Constrained",
              storyId: "production-application-repertoire-builder-workspace-core--constrained",
            },
          ],
        },
        {
          heading: "Borderless / embedded variants",
          body: "Some feature compositions place controls without a panel border; the PositionReachFrequency story set includes the visual variants used standalone and resized (ConstrainedWidth plus ForcedColors and Reduced Motion).",
          links: [
            {
              label: "Position Reach Frequency — Positive White",
              storyId: "production-application-position-reach-frequency--positive-white",
            },
            {
              label: "Position Reach Frequency — Absent",
              storyId: "production-application-position-reach-frequency--absent",
              note: "empty",
            },
            {
              label: "Position Reach Frequency — Constrained Width",
              storyId: "production-application-position-reach-frequency--constrained-width",
            },
          ],
        },
      ]}
    />
  ),
};
