import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { BoardAdapter, type BoardAdapterProps, STARTING_FEN } from "./BoardAdapter";
import styles from "./BoardAdapter.module.css";

const RICH_FEN = "rn1qk2r/1bp1bpp1/pp1ppn1p/8/4PB2/2NP1NP1/PPPQ1PBP/R3K2R b KQkq e3 0 8";
const INVALID_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 99";

const meta = {
  title: "Application/Board/Read-only Board",
  component: BoardAdapter,
} satisfies Meta<typeof BoardAdapter>;

export default meta;

type Story = StoryObj<typeof meta>;

const startingArgs: BoardAdapterProps = {
  fen: STARTING_FEN,
  label: "Starting position",
};

export const DefaultValidStartingPosition: Story = {
  name: "Default valid starting position",
  args: startingArgs,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const graphic = canvas.getByRole("img", { name: "Starting position" });

    const descriptionId = graphic.getAttribute("aria-describedby");
    if (!descriptionId || !/^board-position-description-/.test(descriptionId)) {
      throw new Error("The static board has no generated description id.");
    }
    await expect(canvasElement.ownerDocument.getElementById(descriptionId)).toHaveTextContent(
      "Orientation: White at the bottom. Side to move: White.",
    );
    await expect(
      graphic.querySelectorAll("[role], [tabindex], [aria-roledescription]"),
    ).toHaveLength(0);
    await expect(graphic.querySelector('[aria-hidden="true"][inert]')).toBeTruthy();

    const trigger = canvas.getByRole("button", { name: "Position description" });
    await expect(trigger).toHaveAttribute("aria-expanded", "false");
    await trigger.focus();
    await expect(trigger).toHaveFocus();
    await userEvent.keyboard("{Enter}");
    await expect(trigger).toHaveAttribute("aria-expanded", "true");
    await expect(graphic).toHaveAttribute("aria-describedby", descriptionId);
    await userEvent.keyboard("{Enter}");
    await expect(trigger).toHaveAttribute("aria-expanded", "false");
  },
};

export const RichPosition: Story = {
  name: "Rich position",
  args: {
    fen: RICH_FEN,
    label: "Rich position with complete game state",
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const graphic = canvas.getByRole("img", {
      name: "Rich position with complete game state",
    });
    const descriptionId = graphic.getAttribute("aria-describedby");

    if (!descriptionId) {
      throw new Error("The rich static board has no generated description id.");
    }
    const description = canvasElement.ownerDocument.getElementById(descriptionId);
    await expect(description).toHaveTextContent("Side to move: Black.");
    await expect(description).toHaveTextContent("En-passant target: e3.");
    await expect(description).toHaveTextContent("Fullmove number: 8.");
  },
};

export const BlackOrientation: Story = {
  name: "Black orientation",
  args: {
    ...startingArgs,
    orientation: "black",
    label: "Starting position from Black's side",
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const graphic = canvas.getByRole("img", {
      name: "Starting position from Black's side",
    });
    const descriptionId = graphic.getAttribute("aria-describedby");

    if (!descriptionId) {
      throw new Error("The Black-oriented static board has no generated description id.");
    }
    await expect(canvasElement.ownerDocument.getElementById(descriptionId)).toHaveTextContent(
      "Orientation: Black at the bottom.",
    );
  },
};

export const HiddenCoordinates: Story = {
  name: "Hidden coordinates",
  args: {
    ...startingArgs,
    showCoordinates: false,
    label: "Starting position without coordinates",
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const graphic = canvas.getByRole("img", {
      name: "Starting position without coordinates",
    });

    await expect(graphic.querySelectorAll("[data-square] span")).toHaveLength(0);
  },
};

export const ConstrainedWidth: Story = {
  name: "Constrained-width sizing",
  render: (args) => (
    <div className={styles.constrainedStory}>
      <BoardAdapter {...args} />
    </div>
  ),
  args: {
    ...startingArgs,
    label: "Starting position in a constrained container",
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const graphic = canvas.getByRole("img", {
      name: "Starting position in a constrained container",
    });
    const bounds = graphic.getBoundingClientRect();

    if (bounds.width <= 0 || Math.abs(bounds.width - bounds.height) > 0.5) {
      throw new Error("The constrained static board is not a visible square.");
    }
  },
};

export const InvalidFen: Story = {
  name: "Invalid FEN",
  args: {
    fen: INVALID_FEN,
    label: "Unavailable invalid position",
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await expect(canvas.getByRole("status")).toBeVisible();
    await expect(canvas.getByText("Position unavailable")).toBeVisible();
    await expect(canvasElement.querySelectorAll('[role="img"]')).toHaveLength(0);
  },
};

export const ExpandedPositionDescription: Story = {
  name: "Expanded Position description",
  args: {
    fen: RICH_FEN,
    label: "Rich position with expanded description",
    showCoordinates: true,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole("button", { name: "Position description" });

    await expect(trigger).toHaveAttribute("aria-expanded", "false");
    await trigger.focus();
    await userEvent.keyboard("{Enter}");
    await expect(trigger).toHaveAttribute("aria-expanded", "true");
    const descriptionPanel = canvasElement.querySelector('[aria-label="Position description"]');
    if (!descriptionPanel) {
      throw new Error("The expanded position description is missing.");
    }
    await expect(descriptionPanel).toHaveTextContent("Side to move: Black.");
  },
};
