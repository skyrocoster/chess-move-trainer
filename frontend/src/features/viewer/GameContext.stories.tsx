import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { GameContext } from "./GameContext";
import { PositionContext } from "./PositionContext";
import type { PositionContextResponse } from "./positionContextApi";
import styles from "./Stage1Story.module.css";
import { MISSING_SOURCE_GAME, UNSAFE_SOURCE_GAME, VIEWER_GAME } from "./viewerFixtures";

const meta = {
  title: "Application/Viewer/Game Context",
  component: GameContext,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof GameContext>;

export default meta;
type Story = StoryObj<typeof meta>;

const frame = (children: React.ReactNode) => <main className={styles.frame}>{children}</main>;
const constrained = (children: React.ReactNode) => (
  <main className={styles.frame}>
    <div className={styles.constrained}>{children}</div>
  </main>
);

const finalPosition = VIEWER_GAME.positions.at(-1);
const positionContext: PositionContextResponse = {
  fen: VIEWER_GAME.positions[2].fen,
  overall_exists: true,
  white_count: 2,
  black_count: 1,
  white_total: 3,
  black_total: 2,
};

const emptyPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  const disclosureButton = canvas.getByRole("button", { name: "Game Context" });

  await expect(disclosureButton).toHaveAttribute("aria-expanded", "true");
  await expect(canvas.getByText("No game loaded")).toBeVisible();
  await userEvent.click(disclosureButton);
  await expect(disclosureButton).toHaveAttribute("aria-expanded", "false");
  await expect(canvas.queryByText("No game loaded")).not.toBeInTheDocument();
  await userEvent.click(disclosureButton);
  await expect(canvas.getByText("No game loaded")).toBeVisible();
};

const defaultOpenPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  const disclosureButton = canvas.getByRole("button", { name: "Game Context" });
  const contextText = canvas.getByText("Ply 0 of 3", { exact: true });

  await expect(disclosureButton).toHaveAttribute("aria-expanded", "true");
  await expect(contextText).toBeVisible();
  await userEvent.click(disclosureButton);
  await expect(disclosureButton).toHaveAttribute("aria-expanded", "false");
  await expect(canvas.queryByText("Ply 0 of 3", { exact: true })).not.toBeInTheDocument();
  await userEvent.click(disclosureButton);
  await expect(canvas.getByText("Ply 0 of 3", { exact: true })).toBeVisible();
};

const composedPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  const disclosureButton = canvas.getByRole("button", { name: "Game Context" });
  const sourceLink = canvas.getByRole("link", { name: "Chess.com game" });
  const recurrence = canvas.getByRole("group", { name: "Position recurrence" });
  const analysisChild = canvas.getByTestId("analysis-child");

  await expect(canvas.getByText("Ply 2 of 3")).toBeVisible();
  await expect(canvas.getByText("e5", { exact: true })).toBeVisible();
  await expect(recurrence).toBeVisible();
  await expect(canvas.getByText("Seen in 2 games as White", { exact: true })).toBeVisible();
  await expect(canvas.getByText("Seen in 1 games as Black", { exact: true })).toBeVisible();
  await expect(sourceLink.compareDocumentPosition(analysisChild)).toBe(
    Node.DOCUMENT_POSITION_FOLLOWING,
  );
  await expect(sourceLink.compareDocumentPosition(recurrence)).toBe(
    Node.DOCUMENT_POSITION_FOLLOWING,
  );
  await expect(recurrence.compareDocumentPosition(analysisChild)).toBe(
    Node.DOCUMENT_POSITION_FOLLOWING,
  );
  await expect(disclosureButton).toHaveAttribute("aria-expanded", "true");

  await userEvent.click(disclosureButton);
  await expect(canvas.queryByTestId("analysis-child")).not.toBeInTheDocument();
  await userEvent.click(disclosureButton);
  await expect(canvas.getByTestId("analysis-child")).toBeVisible();
};

const expectNotation = async (canvasElement: HTMLElement, ply: string, notation: string) => {
  const canvas = within(canvasElement);
  await expect(canvas.getByText(`Ply ${ply} of 3`, { exact: true })).toBeVisible();
  await expect(canvas.getByLabelText(notation)).toHaveTextContent(notation);
};

export const Empty: Story = {
  render: () => frame(<GameContext />),
  play: emptyPlay,
};

export const InitialPosition: Story = {
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[0] },
  render: (args) => frame(<GameContext {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const sourceLink = canvas.getByRole("link", { name: "Chess.com game" });
    await expect(canvas.getByText("Ply 0 of 3", { exact: true })).toBeVisible();
    await expect(canvas.getByText("Initial position", { exact: true })).toBeVisible();
    await expect(sourceLink).toHaveAttribute("href", VIEWER_GAME.source_url);
    await expect(sourceLink).toHaveAttribute("target", "_blank");
    await expect(sourceLink).toHaveAttribute("rel", "noopener noreferrer");
    await expect(sourceLink.querySelector("svg")).toHaveAttribute("aria-hidden", "true");
  },
};

export const SafeSource: Story = {
  name: "Source - safe Chess.com link",
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[1] },
  render: (args) => frame(<GameContext {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("link", { name: "Chess.com game" })).toBeVisible();
    await expect(canvas.getByText("Ply 1 of 3", { exact: true })).toBeVisible();
  },
};

export const WhiteMove: Story = {
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[1] },
  render: (args) => frame(<GameContext {...args} />),
  play: async ({ canvasElement }) => expectNotation(canvasElement, "1", "1. e4"),
};

export const BlackMove: Story = {
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[2] },
  render: (args) => frame(<GameContext {...args} />),
  play: async ({ canvasElement }) => expectNotation(canvasElement, "2", "1... e5"),
};

export const IntermediatePosition: Story = {
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[2] },
  render: (args) => frame(<GameContext {...args} />),
  play: async ({ canvasElement }) => expectNotation(canvasElement, "2", "1... e5"),
};

export const FinalPosition: Story = {
  args: { game: VIEWER_GAME, position: finalPosition },
  render: (args) => frame(<GameContext {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    if (!finalPosition) {
      throw new Error("Viewer fixture has no final position");
    }
    await expect(canvas.getByText("Ply 3 of 3", { exact: true })).toBeVisible();
    await expect(canvas.getByLabelText("2. Nf3")).toHaveTextContent("2. Nf3");
  },
};

export const BlackSubject: Story = {
  args: {
    game: { ...VIEWER_GAME, subject_color: "black" },
    position: VIEWER_GAME.positions[1],
  },
  render: (args) => frame(<GameContext {...args} />),
};

export const UnsafeSource: Story = {
  args: { game: UNSAFE_SOURCE_GAME, position: UNSAFE_SOURCE_GAME.positions[1] },
  render: (args) => frame(<GameContext {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("Source unavailable")).toBeVisible();
    await expect(canvas.queryByRole("link", { name: "Chess.com game" })).not.toBeInTheDocument();
  },
};

export const MissingSource: Story = {
  args: { game: MISSING_SOURCE_GAME, position: MISSING_SOURCE_GAME.positions[1] },
  render: (args) => frame(<GameContext {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("Source unavailable")).toBeVisible();
    await expect(canvas.queryByRole("link", { name: "Chess.com game" })).not.toBeInTheDocument();
  },
};

export const Constrained: Story = {
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[2] },
  render: (args) => constrained(<GameContext {...args} />),
};

export const DefaultOpen: Story = {
  name: "Default open disclosure",
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[0] },
  render: (args) => frame(<GameContext {...args} />),
  play: defaultOpenPlay,
};

export const ComposedAnalysis: Story = {
  name: "Composed - controlled analysis child",
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[2] },
  render: (args) =>
    frame(
      <GameContext {...args}>
        <PositionContext context={positionContext} />
        <div data-testid="analysis-child">Controlled analysis presentation</div>
      </GameContext>,
    ),
  play: composedPlay,
};

export const Accessibility: Story = {
  name: "Accessibility - populated context",
  parameters: { a11y: { disable: false } },
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[1] },
  render: (args) => frame(<GameContext {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("button", { name: "Game Context" })).toHaveAttribute(
      "aria-expanded",
      "true",
    );
    await expect(canvas.getByText("Ply 1 of 3", { exact: true })).toBeVisible();
    await expect(canvas.getByLabelText("1. e4")).toHaveTextContent("1. e4");
  },
};

export const ForcedColorsAndReducedMotion: Story = {
  name: "Media emulation - forced colors and reduced motion",
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[2] },
  render: (args) => constrained(<GameContext {...args} />),
  parameters: {
    docs: {
      description: {
        story:
          "Review this constrained state with forced colors and prefers-reduced-motion emulation enabled in the browser.",
      },
    },
  },
};
