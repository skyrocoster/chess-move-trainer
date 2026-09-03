import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import {
  PreferredMovePanelExploration,
  type PreferredMoveExplorationState,
} from "./PreferredMovePanelExploration";

const STATES: PreferredMoveExplorationState[] = [
  "staging_new",
  "not_in_corpus",
  "idle_saved",
  "matches",
];

const constrainedViewport = {
  viewport: {
    defaultViewport: "preferred-move-narrow",
    options: {
      "preferred-move-narrow": {
        name: "Preferred move narrow",
        styles: { width: "480px", height: "800px" },
      },
    },
  },
};

const meta = {
  title: "Exploration/Preferred Move Panel",
  component: PreferredMovePanelExploration,
  parameters: {
    layout: "fullscreen",
    a11y: { test: "error" },
  },
  argTypes: {
    state: {
      control: { type: "select" },
      options: STATES,
    },
  },
  args: {
    onSave: fn(),
    onRemove: fn(),
  },
} satisfies Meta<typeof PreferredMovePanelExploration>;

export default meta;
type Story = StoryObj<typeof meta>;

function getCard(canvasElement: HTMLElement) {
  const canvas = within(canvasElement);
  return {
    canvas,
    card: canvas.getByTestId("preferred-exploration-card"),
    saved: canvas.getByRole("region", { name: "Saved" }),
    staged: canvas.getByRole("region", { name: "Staged" }),
  };
}

async function expectCardDimensions(canvasElement: HTMLElement) {
  const { card, saved, staged } = getCard(canvasElement);
  const isNarrow = canvasElement.ownerDocument.defaultView?.matchMedia("(max-width: 40rem)").matches;
  await expect(card.getBoundingClientRect().height).toBe(isNarrow ? 360 : 256);
  await expect(saved.getBoundingClientRect().height).toBe(88);
  await expect(staged.getBoundingClientRect().height).toBe(88);
}

export const StagingNew: Story = {
  name: "State - staging new move",
  args: { state: "staging_new" },
  play: async ({ args, canvasElement }) => {
    const { canvas } = getCard(canvasElement);
    await expectCardDimensions(canvasElement);
    await expect(canvas.getByRole("status")).toHaveTextContent("Ready to save");
    await expect(canvas.getByRole("region", { name: "Saved" })).toHaveTextContent("None yet");
    await expect(canvas.getByRole("region", { name: "Staged" })).toHaveTextContent("Nce2");
    await expect(canvas.getByRole("button", { name: "Save Nce2" })).toBeEnabled();
    await expect(canvas.queryByRole("button", { name: "Remove" })).not.toBeInTheDocument();
    await userEvent.click(canvas.getByRole("button", { name: "Save Nce2" }));
    await expect(args.onSave).toHaveBeenCalledOnce();
  },
};

export const NotInCorpus: Story = {
  name: "State - not in corpus",
  args: { state: "not_in_corpus" },
  play: async ({ canvasElement }) => {
    const { canvas } = getCard(canvasElement);
    await expectCardDimensions(canvasElement);
    await expect(canvas.getByRole("status")).toHaveTextContent("Not in Corpus");
    await expect(canvas.getByText("This position isn't in your corpus, so it can't be saved yet.")).toBeVisible();
    await expect(canvas.getByRole("region", { name: "Saved" })).toHaveTextContent("Nce2");
    await expect(canvas.getByRole("region", { name: "Staged" })).toHaveTextContent("No move staged");
    await expect(canvas.queryByRole("button")).not.toBeInTheDocument();
  },
};

export const IdleSaved: Story = {
  name: "State - saved with nothing staged",
  args: { state: "idle_saved" },
  play: async ({ args, canvasElement }) => {
    const { canvas } = getCard(canvasElement);
    await expectCardDimensions(canvasElement);
    await expect(canvas.getByRole("status")).toHaveTextContent("Saved");
    await expect(canvas.getByRole("region", { name: "Saved" })).toHaveTextContent("e4");
    await expect(canvas.getByRole("region", { name: "Staged" })).toHaveTextContent(
      "Stage a move to propose replacing e4",
    );
    await expect(canvas.queryByRole("button", { name: /Save/ })).not.toBeInTheDocument();
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeEnabled();
    await userEvent.click(canvas.getByRole("button", { name: "Remove" }));
    await expect(args.onRemove).toHaveBeenCalledOnce();
  },
};

export const Matches: Story = {
  name: "State - staged move matches saved",
  args: { state: "matches" },
  play: async ({ args, canvasElement }) => {
    const { canvas } = getCard(canvasElement);
    await expectCardDimensions(canvasElement);
    await expect(canvas.getByRole("status")).toHaveTextContent("Already saved");
    await expect(canvas.getByRole("region", { name: "Saved" })).toHaveTextContent("e4");
    await expect(canvas.getByRole("region", { name: "Staged" })).toHaveTextContent("e4");
    await expect(canvas.getByRole("button", { name: "Matches saved" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Remove" })).toBeEnabled();
    await expect(
      canvas.getAllByRole("button").map((button) => button.textContent?.trim()),
    ).toEqual(["Matches saved", "Remove"]);
    await expect(canvas.getByTestId("preferred-exploration-connector")).toHaveAttribute(
      "aria-hidden",
      "true",
    );
    await expect(canvas.getByRole("button", { name: "Remove" }).querySelector("svg")).toHaveAttribute(
      "aria-hidden",
      "true",
    );
    await userEvent.click(canvas.getByRole("button", { name: "Remove" }));
    await expect(args.onRemove).toHaveBeenCalledOnce();
  },
};

export const NarrowStacking: Story = {
  name: "Responsive - 480px Saved to Staged stacking",
  args: { state: "staging_new" },
  parameters: constrainedViewport,
  play: async ({ canvasElement }) => {
    const { card, saved, staged } = getCard(canvasElement);
    const relationship = canvasElement.querySelector('[data-testid="preferred-exploration-relationship"]');
    if (!(relationship instanceof HTMLElement)) throw new Error("The relationship layout is missing.");
    await expect(card.getBoundingClientRect().height).toBe(360);
    await expect(saved.getBoundingClientRect().height).toBe(88);
    await expect(staged.getBoundingClientRect().height).toBe(88);
    await expect(relationship.children).toHaveLength(3);
    await expect(relationship.children[0]).toBe(saved);
    await expect(relationship.children[2]).toBe(staged);
    await expect(canvasElement.ownerDocument.documentElement.scrollWidth).toBeLessThanOrEqual(
      canvasElement.ownerDocument.documentElement.clientWidth,
    );
  },
};
