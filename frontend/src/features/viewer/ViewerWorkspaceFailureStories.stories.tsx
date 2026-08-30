import { expect, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import ViewerWorkspace from "./ViewerWorkspace";
import type { GameLookupFailure } from "./positionApi";
import styles from "./Stage1Story.module.css";
import { failureLookup, storyAnalysisClient, submit } from "./viewerStoryHelpers";

const meta = {
  title: "Application/Viewer/Workspace/Failures",
  component: ViewerWorkspace,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof ViewerWorkspace>;
export default meta;
type Story = StoryObj<typeof meta>;
const frame = (children: React.ReactNode) => <main className={styles.frame}>{children}</main>;

function failureStory(status: GameLookupFailure): Story {
  const heading =
    status === "game_not_found"
      ? "Game not found"
      : status === "position_not_found"
        ? "Position not found"
        : status === "corpus_unavailable"
          ? "Corpus unavailable"
          : status === "game_unavailable"
            ? "Game unavailable"
            : "Unable to load game";
  return {
    args: { lookup: failureLookup(status) },
    render: (args) => frame(<ViewerWorkspace analysisClient={storyAnalysisClient()} {...args} />),
    play: async ({ canvasElement }) => {
      const canvas = within(canvasElement);
      await submit(canvas);
      await expect(canvas.getByRole("heading", { name: heading, level: 2 })).toBeVisible();
      await expect(
        canvas.queryByRole("group", { name: "Position recurrence" }),
      ).not.toBeInTheDocument();
    },
  };
}

export const GameNotFound: Story = {
  name: "Game not found - Wide",
  ...failureStory("game_not_found"),
};
export const PositionNotFound: Story = {
  name: "Position not found - Wide",
  ...failureStory("position_not_found"),
};
export const CorpusUnavailable: Story = {
  name: "Corpus unavailable - Wide",
  ...failureStory("corpus_unavailable"),
};
export const GameUnavailable: Story = {
  name: "Game unavailable - Wide",
  ...failureStory("game_unavailable"),
};
export const UnableToLoadGame: Story = {
  name: "Unable to load game - Wide",
  ...failureStory("unexpected_failure"),
};
