import type { Meta, StoryObj } from "@storybook/react-vite";
import { FamilyPage } from "./FamilyPage";

const meta = {
  title: "Reference/Catalogue/Overlays",
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
      family="Overlays"
      intro={
        <>
          Shared Dialog, PreviewCard, Toast, and Tooltip wrappers now cover common reusable overlay
          behavior. Popover and Drawer remain composed locally where their feature-specific anchors,
          responsive changes, and content require it.
        </>
      }
      caution="A shared AlertDialog component does not exist. The remove-confirmation alert dialog in the preferred move workflow is composed inline from Base UI primitives inside PreferredMovePanelSections; it is only reachable through the workspace flow stories."
      sections={[
        {
          heading: "Reusable overlays",
          body: "Dialog owns the standard modal surface and dismissal, PreviewCard adds non-interrupting link previews, ToastProvider supplies a shared notification queue, and Tooltip provides short sighted-user hints. Each wrapper supports controlled state or consumer content where the Base UI primitive does.",
          links: [
            {
              label: "Overlays — Dialog",
              storyId: "production-design-system-base-ui-overlays--dialog-example",
            },
            {
              label: "Overlays — Preview Card",
              storyId: "production-design-system-base-ui-overlays--preview-card-example",
            },
            {
              label: "Overlays — Toast",
              storyId: "production-design-system-base-ui-overlays--toast-example",
            },
            {
              label: "Overlays — Tooltip",
              storyId: "production-design-system-base-ui-overlays--tooltip-example",
            },
          ],
        },
        {
          heading: "Popover-based overlays",
          body: "CalendarDate is a popover-hosted date picker (Base UI Popover, modal) with blank, selected, disabled-future-dates, clearable, keyboard, constrained-width, and forced-colors stories. PromotionPicker renders its picker as a popover at wide viewports.",
          links: [
            {
              label: "Calendar Date — Keyboard And Focus",
              storyId: "production-design-system-components-calendar-date--keyboard-and-focus",
              note: "interactive open and closed",
            },
            {
              label: "Calendar Date — Selected",
              storyId: "production-design-system-components-calendar-date--selected",
              note: "selected state",
            },
            {
              label: "Promotion Picker — Wide Anchored Picker",
              storyId: "production-application-board-promotion-picker--wide-anchored-picker",
              note: "popover variant",
            },
          ],
        },
        {
          heading: "Drawer-based overlays",
          body: "PromotionPicker switches to a Base UI Drawer at constrained widths, and AppShell opens its navigation as a drawer at narrow widths. Both keep focus management inside the Base UI drawer.",
          links: [
            {
              label: "Promotion Picker — Constrained Drawer",
              storyId: "production-application-board-promotion-picker--constrained-drawer",
            },
            {
              label: "App Shell — Constrained Open",
              storyId: "production-application-shell-app-shell--constrained-open",
            },
          ],
        },
        {
          heading: "Alert dialog",
          body: "Only one alert dialog exists in the application: the remove preferred move confirmation. The workspace preferred-move stories exercise it interactively (open and confirmed states included).",
          links: [
            {
              label: "Repertoire Builder Workspace Preferred Move — Save Replacement",
              storyId:
                "production-application-repertoire-builder-workspace-preferred-move--save-replacement",
              note: "alert dialog interaction",
            },
            {
              label: "Preferred Move Workflow — Opponent Turn Gate",
              storyId:
                "production-application-repertoire-builder-workspace-preferred-move-workflow--opponent-turn-gate",
              note: "workflow context",
            },
          ],
        },
        {
          heading: "Overlay reference composition",
          body: "The tournament analysis desk reference composition assembles several surface and overlay patterns in one controlled scene, useful for seeing them placed together.",
          links: [
            {
              label: "Reference/Compositions — Tournament Analysis Desk",
              storyId: "reference-compositions-tournament-analysis-desk--tournament-analysis-desk",
            },
          ],
        },
      ]}
    />
  ),
};
