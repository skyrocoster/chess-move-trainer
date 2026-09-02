import { expect, fn, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import type { ReactNode } from "react";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type {
  MoveResponseDistributionClient,
  MoveResponseDistributionResponse,
} from "./moveResponseDistributionApi";
import { MoveResponseDistribution } from "./MoveResponseDistribution";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function response(
  overrides: Partial<MoveResponseDistributionResponse> = {},
): MoveResponseDistributionResponse {
  return {
    fen: FEN,
    color: "white",
    matching_game_count: 4,
    replies: [
      { rank: 1, child_uci: "e2e4", san: "e4", distinct_game_count: 4, opening_name: null },
      {
        rank: 2,
        child_uci: "d2d4",
        san: "d4",
        distinct_game_count: 3,
        opening_name: "Queen's Pawn Game",
      },
      { rank: 3, child_uci: "c2c4", san: "c4", distinct_game_count: 2, opening_name: null },
      { rank: 4, child_uci: "g1f3", san: "Nf3", distinct_game_count: 1, opening_name: null },
      { rank: 5, child_uci: "c2c3", san: "c3", distinct_game_count: 1, opening_name: null },
      { rank: 6, child_uci: "b2b3", san: "b3", distinct_game_count: 1, opening_name: null },
      { rank: 7, child_uci: "f2f4", san: "f4", distinct_game_count: 1, opening_name: null },
    ],
    ...overrides,
  };
}

function resolvedClient(data: MoveResponseDistributionResponse): MoveResponseDistributionClient {
  return async () => ({ status: "success", data });
}

function frame(children: ReactNode, narrow = false) {
  return (
    <main
      style={{
        minBlockSize: "100vh",
        padding: "var(--cmt-spacing-16)",
        background: "var(--md-sys-color-background)",
        color: "var(--md-sys-color-on-background)",
      }}
    >
      <div style={{ inlineSize: narrow ? "160px" : "min(100%, 48rem)", marginInline: "auto" }}>
        {children}
      </div>
    </main>
  );
}

const meta = {
  title: "Application/Move Response Distribution",
  component: MoveResponseDistribution,
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component:
          "Reusable response view for observed replies by selected repertoire colour. Percentages use the matching-game denominator and may overlap across replies.",
      },
    },
  },
  args: {
    fen: FEN,
    color: "white",
    onMoveSelect: fn(),
  },
} satisfies Meta<typeof MoveResponseDistribution>;

export default meta;
type Story = StoryObj<typeof meta>;

export const AvailableWithTail: Story = {
  name: "Available - five common replies and Other tail",
  args: { client: resolvedClient(response()) },
  render: (args) => frame(<MoveResponseDistribution {...args} />),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("White repertoire colour", { exact: true })).toBeVisible();
    await expect(canvas.getByRole("button", { name: /Show other replies/ })).toBeVisible();
    await expect(canvas.getByText(/one game may appear in more than one reply/)).toBeVisible();

    const getSectors = () => canvasElement.querySelectorAll(".recharts-sector");
    expect(getSectors()).toHaveLength(6);
    await userEvent.hover(getSectors()[0]!);
    await expect(canvas.getByRole("tooltip")).toHaveTextContent("e4");
    await expect(canvas.getByRole("tooltip")).toHaveTextContent("4 games");
    await expect(canvas.getByRole("tooltip")).toHaveTextContent("100%");
    await expect(getSectors()[0]).toHaveAttribute("data-hovered", "true");
    await expect(getSectors()[1]).toHaveAttribute("data-hovered", "false");
    expect(args.onMoveSelect).not.toHaveBeenCalled();

    await userEvent.unhover(getSectors()[0]!);
    await expect(canvas.queryByRole("tooltip")).not.toBeInTheDocument();
    await expect(getSectors()[0]).not.toHaveAttribute("data-hovered");

    await userEvent.hover(getSectors()[5]!);
    await expect(canvas.getByRole("tooltip")).toHaveTextContent("Other");
    await expect(canvas.getByRole("tooltip")).toHaveTextContent("2 games");
    await expect(canvas.getByRole("tooltip")).toHaveTextContent("50%");
    expect(args.onMoveSelect).not.toHaveBeenCalled();
    await expect(canvas.getByRole("button", { name: /Show other replies/ })).toHaveAttribute(
      "aria-expanded",
      "false",
    );
  },
};

export const AvailableWithoutTail: Story = {
  name: "Available - no Other tail",
  args: { client: resolvedClient(response({ replies: response().replies.slice(0, 5) })) },
  render: (args) => frame(<MoveResponseDistribution {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("button", { name: /e4, 4 distinct games/ })).toBeVisible();
    await expect(
      canvas.queryByRole("button", { name: /Show other replies/ }),
    ).not.toBeInTheDocument();
  },
};

export const Loading: Story = {
  name: "Loading - replacement-safe request",
  args: { client: async () => new Promise(() => {}) },
  render: (args) => frame(<MoveResponseDistribution {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("status")).toHaveTextContent("Loading move responses");
    await expect(
      canvas.queryByRole("button", { name: /Show other replies/ }),
    ).not.toBeInTheDocument();
  },
};

export const NoGames: Story = {
  name: "No games - successful empty data",
  args: { client: resolvedClient(response({ matching_game_count: 0, replies: [] })) },
  render: (args) => frame(<MoveResponseDistribution {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getAllByText("No matching White repertoire games were found for this position.")[0],
    ).toBeVisible();
    await expect(canvas.queryByRole("img")).not.toBeInTheDocument();
  },
};

let unavailableAttempts = 0;
const unavailableThenSuccess: MoveResponseDistributionClient = async () => {
  unavailableAttempts += 1;
  return unavailableAttempts === 1
    ? { status: "move_response_distribution_unavailable" }
    : { status: "success", data: response() };
};

export const UnavailableWithRetry: Story = {
  name: "Unavailable - retry current request",
  args: { client: unavailableThenSuccess },
  render: (args) => frame(<MoveResponseDistribution {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("alert")).toHaveTextContent("Move response data is unavailable.");
    await userEvent.click(canvas.getByRole("button", { name: "Retry" }));
    await expect(canvas.getByRole("button", { name: /Show other replies/ })).toBeVisible();
  },
};

export const NullableOpeningNames: Story = {
  name: "Nullable opening names",
  args: { client: resolvedClient(response({ replies: response().replies.slice(0, 3) })) },
  render: (args) => frame(<MoveResponseDistribution {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("Queen's Pawn Game", { exact: true })).toBeVisible();
    await expect(canvas.getByRole("button", { name: /e4, 4 distinct games/ })).toBeVisible();
  },
};

export const DenseTinySectorCluster: Story = {
  name: "Dense tiny-sector cluster - user-reported regression layout",
  args: {
    client: resolvedClient({
      fen: FEN,
      color: "white",
      matching_game_count: 10000,
      replies: [
        { rank: 1, child_uci: "e2e4", san: "e4", distinct_game_count: 9804, opening_name: null },
        { rank: 2, child_uci: "d2d4", san: "d4", distinct_game_count: 180, opening_name: null },
        { rank: 3, child_uci: "e2e3", san: "e3", distinct_game_count: 10, opening_name: null },
        { rank: 4, child_uci: "b1c3", san: "Nc3", distinct_game_count: 4, opening_name: null },
        { rank: 5, child_uci: "g1f3", san: "f3", distinct_game_count: 2, opening_name: null },
        { rank: 6, child_uci: "g1g3", san: "g3", distinct_game_count: 1, opening_name: null },
      ],
    }),
  },
  render: (args) => frame(<MoveResponseDistribution {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("e4 98.0%")).toBeVisible();
    await expect(canvas.getByText("Other 0.0%")).toBeVisible();
    await expect(canvas.getByRole("button", { name: /Show other replies/ })).toBeVisible();
  },
};

export const ConstrainedWidth: Story = {
  name: "Constrained width - stacked controls",
  args: { client: resolvedClient(response()) },
  render: (args) => frame(<MoveResponseDistribution {...args} />, true),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("button", { name: /e4, 4 distinct games/ })).toBeVisible();
    await expect(canvas.getByRole("button", { name: /Show other replies/ })).toBeVisible();
  },
};

export const KeyboardAndDisclosure: Story = {
  name: "Keyboard and disclosure semantics",
  args: { client: resolvedClient(response()) },
  render: (args) => frame(<MoveResponseDistribution {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const other = await canvas.findByRole("button", { name: /Show other replies/ });
    await userEvent.tab();
    await userEvent.tab();
    await userEvent.tab();
    await userEvent.click(other);
    await expect(other).toHaveAttribute("aria-expanded", "true");
    await expect(canvas.getByRole("button", { name: /b3/ })).toBeVisible();
  },
};
