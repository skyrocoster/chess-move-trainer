import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import { GameLoader, type GameLoaderStatus } from "./GameLoader";

const meta = {
  title: "Production/Application/Game/Game Loader",
  tags: ["status-production"],
  parameters: { layout: "centered" },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

function GameLoaderHarness({
  initialGameUuid = "35b42696-b283-4722-8f16-92297d19301f",
  status = "idle",
}: {
  initialGameUuid?: string;
  status?: GameLoaderStatus;
}) {
  const [gameUuid, setGameUuid] = useState(initialGameUuid);
  return (
    <div style={{ width: "min(42rem, 90vw)" }}>
      <GameLoader
        status={status}
        gameUuid={gameUuid}
        onGameUuidChange={setGameUuid}
        onSubmit={fn()}
        onReset={fn()}
      />
    </div>
  );
}

export const Ready: Story = {
  render: () => <GameLoaderHarness />,
};

export const Loading: Story = {
  render: () => <GameLoaderHarness status="loading" />,
};

export const GameNotFound: Story = {
  render: () => <GameLoaderHarness status="game_not_found" />,
};

export const CorpusUnavailable: Story = {
  render: () => <GameLoaderHarness status="corpus_unavailable" />,
};

export const ValidationError: Story = {
  render: () => <GameLoaderHarness initialGameUuid="not-a-uuid" />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("button", { name: "Load game" }));
    await expect(canvas.getByRole("alert")).toHaveTextContent("Enter a valid game UUID.");
  },
};
