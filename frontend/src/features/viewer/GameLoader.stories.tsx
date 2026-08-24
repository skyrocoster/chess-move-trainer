import { expect, fn, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState, type ReactNode } from "react";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { GameLoader, type GameLoaderProps } from "./GameLoader";
import styles from "./Stage1Story.module.css";
import { VIEWER_GAME_UUID } from "./viewerFixtures";

const frame = (children: ReactNode) => <main className={styles.frame}>{children}</main>;
const constrained = (children: ReactNode) => (
  <main className={styles.frame}>
    <div className={styles.constrained}>{children}</div>
  </main>
);

type ControlledStoryProps = Omit<
  GameLoaderProps,
  "gameUuid" | "ply" | "onGameUuidChange" | "onPlyChange"
> & {
  gameUuid?: string;
  ply?: string;
  onGameUuidChange?: (value: string) => void;
  onPlyChange?: (value: string) => void;
};

function ControlledGameLoader({
  gameUuid: initialGameUuid = "",
  ply: initialPly = "",
  onGameUuidChange,
  onPlyChange,
  ...props
}: ControlledStoryProps) {
  const [gameUuid, setGameUuid] = useState(initialGameUuid);
  const [ply, setPly] = useState(initialPly);

  return (
    <GameLoader
      {...props}
      gameUuid={gameUuid}
      ply={ply}
      onGameUuidChange={(value) => {
        setGameUuid(value);
        onGameUuidChange?.(value);
      }}
      onPlyChange={(value) => {
        setPly(value);
        onPlyChange?.(value);
      }}
    />
  );
}

const meta = {
  title: "Application/Viewer/Game Loader",
  component: ControlledGameLoader,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof ControlledGameLoader>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Empty: Story = {
  render: () => frame(<ControlledGameLoader />),
};

export const Loading: Story = {
  args: { status: "loading", gameUuid: VIEWER_GAME_UUID, ply: "" },
  render: (args) => frame(<ControlledGameLoader {...args} />),
};

export const GameNotFound: Story = {
  args: { status: "game_not_found", gameUuid: VIEWER_GAME_UUID },
  render: (args) => frame(<ControlledGameLoader {...args} />),
};

export const PositionNotFound: Story = {
  args: { status: "position_not_found", gameUuid: VIEWER_GAME_UUID, ply: "99" },
  render: (args) => frame(<ControlledGameLoader {...args} />),
};

export const CorpusUnavailable: Story = {
  args: { status: "corpus_unavailable", gameUuid: VIEWER_GAME_UUID },
  render: (args) => frame(<ControlledGameLoader {...args} />),
};

export const GameUnavailable: Story = {
  args: { status: "game_unavailable", gameUuid: VIEWER_GAME_UUID },
  render: (args) => frame(<ControlledGameLoader {...args} />),
};

export const UnableToLoadGame: Story = {
  args: { status: "unexpected_failure", gameUuid: VIEWER_GAME_UUID },
  render: (args) => frame(<ControlledGameLoader {...args} />),
};

export const Constrained: Story = {
  args: { gameUuid: VIEWER_GAME_UUID },
  render: (args) => constrained(<ControlledGameLoader {...args} />),
};

export const ValidationAndRetry: Story = {
  name: "Validation, submit, and reset",
  args: {
    onGameUuidChange: fn(),
    onPlyChange: fn(),
    onSubmit: fn(),
    onReset: fn(),
  },
  render: (args) => frame(<ControlledGameLoader {...args} />),
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
    await userEvent.type(gameUuid, VIEWER_GAME_UUID);
    await userEvent.type(ply, "2");
    await userEvent.click(canvas.getByRole("button", { name: "Load game" }));
    await expect(args.onGameUuidChange).toHaveBeenLastCalledWith(VIEWER_GAME_UUID);
    await expect(args.onPlyChange).toHaveBeenLastCalledWith("2");
    await expect(args.onSubmit).toHaveBeenCalledTimes(1);
    await expect(args.onSubmit).toHaveBeenCalledWith({ gameUuid: VIEWER_GAME_UUID, ply: "2" });

    await userEvent.click(canvas.getByRole("button", { name: "Reset" }));
    await expect(gameUuid).toHaveValue("");
    await expect(ply).toHaveValue("");
    await expect(args.onGameUuidChange).toHaveBeenLastCalledWith("");
    await expect(args.onPlyChange).toHaveBeenLastCalledWith("");
    await expect(args.onReset).toHaveBeenCalledTimes(1);
  },
};

export const TrimmedSubmission: Story = {
  name: "Trimmed submission values",
  args: {
    onGameUuidChange: fn(),
    onPlyChange: fn(),
    onSubmit: fn(),
  },
  render: (args) => frame(<ControlledGameLoader {...args} />),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.type(
      canvas.getByRole("textbox", { name: "Game UUID" }),
      ` ${VIEWER_GAME_UUID} `,
    );
    await userEvent.type(canvas.getByRole("textbox", { name: /Ply/ }), " 2 ");
    await userEvent.click(canvas.getByRole("button", { name: "Load game" }));

    await expect(args.onSubmit).toHaveBeenCalledWith({
      gameUuid: VIEWER_GAME_UUID,
      ply: "2",
    });
  },
};

export const DisclosureAndKeyboard: Story = {
  name: "Disclosure and keyboard focus",
  render: () => frame(<ControlledGameLoader />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const disclosure = canvas.getByRole("button", { name: "Game Loader" });

    await expect(disclosure).toHaveAttribute("aria-expanded", "true");
    await userEvent.click(disclosure);
    await expect(disclosure).toHaveAttribute("aria-expanded", "false");
    await expect(canvas.queryByRole("textbox", { name: "Game UUID" })).not.toBeInTheDocument();

    await userEvent.click(disclosure);
    await expect(disclosure).toHaveAttribute("aria-expanded", "true");
    await expect(disclosure).toHaveFocus();
    await userEvent.tab();
    await expect(canvas.getByRole("textbox", { name: "Game UUID" })).toHaveFocus();
    await userEvent.tab();
    await expect(canvas.getByRole("textbox", { name: /Ply/ })).toHaveFocus();
    await userEvent.tab();
    await expect(canvas.getByRole("button", { name: "Load game" })).toHaveFocus();
    await userEvent.tab();
    await expect(canvas.getByRole("button", { name: "Reset" })).toHaveFocus();
  },
};
