import { expect, fn, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { GameLoader } from "./GameLoader";
import styles from "./Stage1Story.module.css";
import { STAGE1_GAME_UUID } from "./stage1GameTypes";

const meta = {
  title: "Application/Viewer/Game Loader",
  component: GameLoader,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof GameLoader>;

export default meta;
type Story = StoryObj<typeof meta>;

const frame = (children: React.ReactNode) => <main className={styles.frame}>{children}</main>;
const constrained = (children: React.ReactNode) => (
  <main className={styles.frame}>
    <div className={styles.constrained}>{children}</div>
  </main>
);

export const Empty: Story = {
  render: () => frame(<GameLoader />),
};

export const Loading: Story = {
  args: { status: "loading", gameUuid: STAGE1_GAME_UUID, ply: "" },
  render: (args) => frame(<GameLoader {...args} />),
};

export const GameNotFound: Story = {
  args: { status: "game_not_found", gameUuid: STAGE1_GAME_UUID },
  render: (args) => frame(<GameLoader {...args} />),
};

export const PositionNotFound: Story = {
  args: { status: "position_not_found", gameUuid: STAGE1_GAME_UUID, ply: "99" },
  render: (args) => frame(<GameLoader {...args} />),
};

export const CorpusUnavailable: Story = {
  args: { status: "corpus_unavailable", gameUuid: STAGE1_GAME_UUID },
  render: (args) => frame(<GameLoader {...args} />),
};

export const GameUnavailable: Story = {
  args: { status: "game_unavailable", gameUuid: STAGE1_GAME_UUID },
  render: (args) => frame(<GameLoader {...args} />),
};

export const UnableToLoadGame: Story = {
  args: { status: "unexpected_failure", gameUuid: STAGE1_GAME_UUID },
  render: (args) => frame(<GameLoader {...args} />),
};

export const Constrained: Story = {
  args: { gameUuid: STAGE1_GAME_UUID },
  render: (args) => constrained(<GameLoader {...args} />),
};

export const ValidationAndRetry: Story = {
  name: "Validation, submit, and reset",
  args: {
    onGameUuidChange: fn(),
    onPlyChange: fn(),
    onSubmit: fn(),
    onReset: fn(),
  },
  render: (args) => frame(<GameLoader {...args} />),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("button", { name: "Load game" }));
    await expect(canvas.getByRole("alert")).toHaveTextContent("valid game UUID");
    await expect(args.onSubmit).not.toHaveBeenCalled();
    await expect(canvas.getByRole("button", { name: "Game Loader" })).toHaveAttribute(
      "aria-expanded",
      "true",
    );

    const gameUuid = canvas.getByRole("textbox", { name: "Game UUID" });
    const ply = canvas.getByRole("textbox", { name: /Ply/ });
    await userEvent.type(gameUuid, STAGE1_GAME_UUID);
    await userEvent.type(ply, "2");
    await userEvent.click(canvas.getByRole("button", { name: "Load game" }));
    await expect(args.onGameUuidChange).toHaveBeenLastCalledWith(STAGE1_GAME_UUID);
    await expect(args.onPlyChange).toHaveBeenLastCalledWith("2");
    await expect(args.onSubmit).toHaveBeenCalledTimes(1);
    await expect(args.onSubmit).toHaveBeenCalledWith({ gameUuid: STAGE1_GAME_UUID, ply: "2" });

    await userEvent.click(canvas.getByRole("button", { name: "Reset" }));
    await expect(gameUuid).toHaveValue("");
    await expect(ply).toHaveValue("");
    await expect(args.onGameUuidChange).toHaveBeenLastCalledWith("");
    await expect(args.onPlyChange).toHaveBeenLastCalledWith("");
    await expect(args.onReset).toHaveBeenCalledTimes(1);
  },
};
