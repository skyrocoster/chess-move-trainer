import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { MockedGameViewer, type MockedViewerScenario } from "./MockedGameViewer";
import styles from "./Stage1Story.module.css";

const meta = {
  title: "Viewer/Stage 1/Mocked Game Viewer",
  component: MockedGameViewer,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof MockedGameViewer>;

export default meta;
type Story = StoryObj<typeof meta>;

const frame = (children: React.ReactNode) => <main className={styles.frame}>{children}</main>;
const constrained = (children: React.ReactNode) => (
  <main className={styles.frame}>
    <div className={styles.constrained}>{children}</div>
  </main>
);

function wide(scenario: MockedViewerScenario) {
  return frame(<MockedGameViewer scenario={scenario} />);
}

function narrow(scenario: MockedViewerScenario) {
  return constrained(<MockedGameViewer scenario={scenario} />);
}

export const EmptyWide: Story = {
  name: "Empty - Wide",
  render: () => wide("empty"),
};

export const EmptyConstrained: Story = {
  name: "Empty - Constrained",
  render: () => narrow("empty"),
};

export const LoadingWide: Story = {
  name: "Loading - Wide",
  render: () => wide("loading"),
};

export const LoadingConstrained: Story = {
  name: "Loading - Constrained",
  render: () => narrow("loading"),
};

export const ReplacementLoadingWide: Story = {
  name: "Replacement loading - Wide",
  render: () => wide("replacement_loading"),
};

export const ReplacementLoadingConstrained: Story = {
  name: "Replacement loading - Constrained",
  render: () => narrow("replacement_loading"),
};

export const InitialBoundaryWide: Story = {
  name: "Initial boundary - Wide",
  render: () => wide("initial"),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("button", { name: "Previous" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Next" })).toBeEnabled();
    await expect(canvas.getByText("Initial position")).toBeVisible();
  },
};

export const IntermediateWide: Story = {
  name: "Success intermediate - Wide",
  render: () => wide("intermediate"),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("Ply 1 of 3")).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Next" }));
    await expect(canvas.getByText("Ply 2 of 3")).toBeVisible();
  },
};

export const IntermediateConstrained: Story = {
  name: "Success intermediate - Constrained",
  render: () => narrow("intermediate"),
};

export const FinalBoundaryWide: Story = {
  name: "Final boundary - Wide",
  render: () => wide("final"),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("button", { name: "Previous" })).toBeEnabled();
    await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
    await expect(canvas.getByText("Ply 3 of 3")).toBeVisible();
  },
};

export const BlackSubjectWide: Story = {
  name: "Success Black subject - Wide",
  render: () => wide("black_subject"),
};

export const BlackSubjectConstrained: Story = {
  name: "Success Black subject - Constrained",
  render: () => narrow("black_subject"),
};

export const UnsafeSourceWide: Story = {
  name: "Unsafe source - Wide",
  render: () => wide("unsafe_source"),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("Source unavailable")).toBeVisible();
    await expect(canvas.queryByRole("link", { name: "Chess.com game" })).not.toBeInTheDocument();
  },
};

export const MissingSourceConstrained: Story = {
  name: "Missing source - Constrained",
  render: () => narrow("missing_source"),
};

export const GameNotFoundWide: Story = {
  name: "Game not found - Wide",
  render: () => wide("game_not_found"),
};

export const PositionNotFoundWide: Story = {
  name: "Position not found - Wide",
  render: () => wide("position_not_found"),
};

export const CorpusUnavailableWide: Story = {
  name: "Corpus unavailable - Wide",
  render: () => wide("corpus_unavailable"),
};

export const GameUnavailableWide: Story = {
  name: "Game unavailable - Wide",
  render: () => wide("game_unavailable"),
};

export const UnableToLoadGameWide: Story = {
  name: "Unable to load game - Wide",
  render: () => wide("unexpected_failure"),
};

export const GameNotFoundConstrained: Story = {
  name: "Game not found - Constrained",
  render: () => narrow("game_not_found"),
};

export const PositionNotFoundConstrained: Story = {
  name: "Position not found - Constrained",
  render: () => narrow("position_not_found"),
};

export const CorpusUnavailableConstrained: Story = {
  name: "Corpus unavailable - Constrained",
  render: () => narrow("corpus_unavailable"),
};

export const GameUnavailableConstrained: Story = {
  name: "Game unavailable - Constrained",
  render: () => narrow("game_unavailable"),
};

export const UnableToLoadGameConstrained: Story = {
  name: "Unable to load game - Constrained",
  render: () => narrow("unexpected_failure"),
};

export const ReplacementFailureWide: Story = {
  name: "Replacement failure preserves prior game - Wide",
  render: () => wide("replacement_failure"),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("Game unavailable")).toBeVisible();
    await expect(canvas.getByText("Ply 1 of 3")).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Next" })).toBeEnabled();
  },
};

export const ResetToEmpty: Story = {
  name: "Reset - returns to empty state",
  render: () => wide("intermediate"),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("button", { name: "Reset" }));
    await expect(canvas.getAllByText("No game loaded")).toHaveLength(2);
    await expect(canvas.getByRole("button", { name: "Previous" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
  },
};
