import type { ReactNode } from "react";
import { expect, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { RepertoireResponsiveStage } from "./RepertoireResponsiveStage";

function lane(testId: string, name: string): ReactNode {
  return (
    <section
      data-lane={testId.replace("fixture-", "")}
      data-testid={testId}
      aria-label={`${name} lane`}
      style={{
        minBlockSize: "180px",
        padding: "var(--cmt-spacing-16)",
        background: "var(--md-sys-color-surface-container)",
        color: "var(--md-sys-color-on-surface)",
      }}
    >
      <h2>{name}</h2>
      <p>Representative {name.toLowerCase()} fixture.</p>
    </section>
  );
}

const boardLane = lane("fixture-board", "Board");
const sessionLane = lane("fixture-session", "Session");
const engineLane = lane("fixture-engine", "Engine");

function boundaryFrame(width: number) {
  return (
    <main style={{ minBlockSize: "100vh", padding: "var(--cmt-spacing-24)" }}>
      <div style={{ inlineSize: `${width}px`, maxInlineSize: "100%", marginInline: "auto" }}>
        <RepertoireResponsiveStage board={boardLane} session={sessionLane} engine={engineLane} />
      </div>
    </main>
  );
}

const meta = {
  title: "Application/Repertoire Builder/Responsive Stage",
  component: RepertoireResponsiveStage,
  parameters: { layout: "fullscreen" },
  args: { board: boardLane, session: sessionLane, engine: engineLane },
} satisfies Meta<typeof RepertoireResponsiveStage>;

export default meta;
type Story = StoryObj<typeof meta>;

async function verifyBoundary(canvasElement: HTMLElement, mode: string, separatorCount: number) {
  const canvas = within(canvasElement);
  const stage = canvas.getByTestId("repertoire-workspace-stage");
  const stageQueries = within(stage);
  await expect(stage).toHaveAttribute("data-layout-mode", mode);
  await expect(stageQueries.queryAllByRole("separator")).toHaveLength(separatorCount);
  await expect(
    Array.from(stage.querySelectorAll("[data-lane]")).map((lane) =>
      lane.getAttribute("data-testid"),
    ),
  ).toEqual(["fixture-board", "fixture-session", "fixture-engine"]);
  await expect(stageQueries.getByTestId("fixture-session")).toBeVisible();
  await expect(stageQueries.getByTestId("fixture-engine")).toBeVisible();
}

export const Boundary699: Story = {
  name: "Boundary - 699px narrow",
  render: () => boundaryFrame(699),
  play: async ({ canvasElement }) => verifyBoundary(canvasElement, "narrow", 0),
};

export const Boundary700: Story = {
  name: "Boundary - 700px medium",
  render: () => boundaryFrame(700),
  play: async ({ canvasElement }) => verifyBoundary(canvasElement, "medium", 1),
};

export const Boundary1039: Story = {
  name: "Boundary - 1039px medium",
  render: () => boundaryFrame(1039),
  play: async ({ canvasElement }) => verifyBoundary(canvasElement, "medium", 1),
};

export const Boundary1040: Story = {
  name: "Boundary - 1040px wide",
  render: () => boundaryFrame(1040),
  play: async ({ canvasElement }) => verifyBoundary(canvasElement, "wide", 2),
};
