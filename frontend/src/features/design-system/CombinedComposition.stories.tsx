import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";

import type { Meta, StoryObj } from "@storybook/react-vite";

import { CombinedComposition } from "./CombinedComposition";

const meta = {
  title: "Composition/TournamentAnalysisDesk",
  component: CombinedComposition,
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta<typeof CombinedComposition>;

export default meta;

type Story = StoryObj<typeof meta>;

export const TournamentAnalysisDesk: Story = {};
