import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";

import type { Meta, StoryObj } from "@storybook/react-vite";

import { CombinedComposition } from "./CombinedComposition";

const meta = {
  title: "Documentation/Compositions/Tournament Analysis Desk",
  component: CombinedComposition,
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component:
          "Storybook-only composition fixture demonstrating production design-system treatments without application behavior.",
      },
    },
  },
} satisfies Meta<typeof CombinedComposition>;

export default meta;

type Story = StoryObj<typeof meta>;

export const TournamentAnalysisDesk: Story = {};
