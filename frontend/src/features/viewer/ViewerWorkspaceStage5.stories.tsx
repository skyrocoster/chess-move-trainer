import type { Meta, StoryObj } from "@storybook/react-vite";

import { Stage5AnalysisStory } from "./stage5AnalysisStorySupport";

const meta = {
  title: "Viewer/MP-11/Stage 5 Analysis",
  component: Stage5AnalysisStory,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof Stage5AnalysisStory>;

export default meta;
type Story = StoryObj<typeof meta>;

export const BranchAnalysis: Story = {
  name: "Branch analysis - deliberate current FEN",
  args: { scenario: "branch" },
};

export const StaleResult: Story = {
  name: "Stale result - deliberate Update",
  args: { scenario: "stale" },
};

export const FailedRetry: Story = {
  name: "Failed result - deliberate Retry",
  args: { scenario: "failed" },
};

export const RunningObservation: Story = {
  name: "Running observation - no cancellation action",
  args: { scenario: "running" },
};
