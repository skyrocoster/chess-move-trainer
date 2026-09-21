import type { Meta, StoryObj } from "@storybook/react-vite";
import { FamilyPage } from "./FamilyPage";

const meta = {
  title: "Reference/Catalogue/Navigation and Content Switching",
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
      family="Navigation and Content Switching"
      intro="The components currently used to switch visible content or navigate hierarchical data. Coverage is provided by the existing Production stories; each link notes the states it shows."
      sections={[
        {
          heading: "Menus and primary navigation",
          body: "Menu, ContextMenu, and Menubar share one action/link definition, while NavigationMenu handles direct links and popup link groups. All four keep keyboard and focus behavior in Base UI and leave destinations and commands caller-owned.",
          links: [
            {
              label: "Menus and Navigation — Menu",
              storyId: "production-design-system-base-ui-menus-and-navigation--menu-example",
            },
            {
              label: "Menus and Navigation — Context Menu",
              storyId:
                "production-design-system-base-ui-menus-and-navigation--context-menu-example",
            },
            {
              label: "Menus and Navigation — Menubar",
              storyId: "production-design-system-base-ui-menus-and-navigation--menubar-example",
            },
            {
              label: "Menus and Navigation — Navigation Menu",
              storyId:
                "production-design-system-base-ui-menus-and-navigation--navigation-menu-example",
            },
          ],
        },
        {
          heading: "Tabs",
          body: "Token-driven tabs built on Base UI's Tabs primitive. Stories cover the default presentation, the disabled state, controlled usage, and overflow handling when the tab strip is too long.",
          links: [
            {
              label: "Tabs — Default",
              storyId: "production-design-system-components-tabs--default",
            },
            {
              label: "Tabs — Disabled",
              storyId: "production-design-system-components-tabs--disabled",
            },
            {
              label: "Tabs — Controlled",
              storyId: "production-design-system-components-tabs--controlled",
              note: "interactive controlled example",
            },
            {
              label: "Tabs — Overflow",
              storyId: "production-design-system-components-tabs--overflow",
            },
          ],
        },
        {
          heading: "Disclosure",
          body: "Expand/collapse region built on Base UI's Disclosure primitive with a rotatable trigger chevron. Stories cover collapsed-by-default, open-by-default, and long content.",
          links: [
            {
              label: "Disclosure — Collapsed By Default",
              storyId: "production-design-system-components-disclosure--collapsed-by-default",
            },
            {
              label: "Disclosure — Open By Default",
              storyId: "production-design-system-components-disclosure--open-by-default",
              note: "expanded state",
            },
            {
              label: "Disclosure — With Long Content",
              storyId: "production-design-system-components-disclosure--with-long-content",
            },
          ],
        },
        {
          heading: "Accordion",
          body: "Data-driven multi-item disclosure built on Base UI Accordion. Consumers provide stable values, summaries, and arbitrary panel content, and may opt into controlled or multi-panel state.",
          links: [
            {
              label: "Content Primitives — Accordion",
              storyId: "production-design-system-base-ui-content-primitives--accordion-example",
            },
          ],
        },
        {
          heading: "Line family (tree controls)",
          body: "The line-library feature covers repository browsing: LineLibrary assembles filters plus the tree with loading, empty, and error states; the tree supports selection; the filters exist in explicit-apply and immediate-apply modes with a disabled state. The opening line library production story shows the same family in the full application context, including search, ECO range filter, and stale refresh.",
          links: [
            {
              label: "Line Library — Default",
              storyId: "production-design-system-components-line-library--default",
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
              label: "Line Library — Error State",
              storyId: "production-design-system-components-line-library--error-state",
            },
            {
              label: "Line Library Tree — With Selection",
              storyId: "production-design-system-components-line-library-tree--with-selection",
              note: "selected state",
            },
            {
              label: "Line Library Filters — Disabled",
              storyId: "production-design-system-components-line-library-filters--disabled",
            },
            {
              label: "Opening Line Library — Browser Selection And Commit",
              storyId:
                "production-application-openings-opening-line-library--browser-selection-and-commit",
              note: "interactive production context",
            },
          ],
        },
      ]}
    />
  ),
};
