import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import ViewerWorkspace from "./ViewerWorkspace";
import {
  defaultLookup,
  mockCorpusUnavailable,
  mockPositionNotFound,
  mockStoredPositionInvalid,
  mockSuccessBlack,
  mockSuccessWhite,
  mockUnexpectedFailure,
  type LookupResult,
  type PositionLookup,
} from "./positionLookup";
import styles from "./ViewerWorkspace.module.css";

const GAME_UUID = "0101b08a-ce8b-11ee-b2fd-e90263e5548c";
const PLY = "8";
const START_BOARD_LABEL = "Chess board: standard starting position, White at the bottom";

const meta = {
  title: "Viewer Workspace",
  component: ViewerWorkspace,
  args: { lookup: defaultLookup },
} satisfies Meta<typeof ViewerWorkspace>;

export default meta;

type Story = StoryObj<typeof meta>;

function constrainedViewer(args: { lookup?: PositionLookup } = {}) {
  return (
    <div className={styles.constrainedStory}>
      <ViewerWorkspace {...args} />
    </div>
  );
}

async function submitForm(canvas: ReturnType<typeof within>, uuid = GAME_UUID, ply = PLY) {
  await userEvent.type(canvas.getByLabelText("Game UUID"), uuid);
  await userEvent.type(canvas.getByLabelText("Ply"), ply);
  await userEvent.click(canvas.getByRole("button", { name: "Load position" }));
}

const invalidInputPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  await userEvent.type(canvas.getByLabelText("Game UUID"), "not-a-uuid");
  await userEvent.type(canvas.getByLabelText("Ply"), "-3");
  await userEvent.click(canvas.getByRole("button", { name: "Load position" }));
  await expect(canvas.getByRole("alert")).toBeVisible();
};

const pendingLookup: PositionLookup = () => new Promise<LookupResult>(() => {});

const loadingPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  await submitForm(canvas);
  await expect(canvas.getByText("Loading the requested position...")).toBeVisible();
  await expect(canvas.getByRole("button", { name: "Load position" })).toBeDisabled();
  await expect(canvas.getByRole("img", { name: START_BOARD_LABEL })).toBeVisible();
};

const successPlay =
  (subjectColor: "White" | "Black") =>
  async ({ canvasElement }: { canvasElement: HTMLElement }) => {
    const canvas = within(canvasElement);
    await submitForm(canvas);
    await expect(
      canvas.getByRole("img", {
        name: new RegExp(`ply ${PLY}, ${subjectColor} at the bottom`),
      }),
    ).toBeVisible();
  };

const failurePlay =
  (heading: string) =>
  async ({ canvasElement }: { canvasElement: HTMLElement }) => {
    const canvas = within(canvasElement);
    await submitForm(canvas);
    await expect(canvas.getByText(heading)).toBeVisible();
  };

const resetPlay: NonNullable<Story["play"]> = async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  await submitForm(canvas);
  await expect(
    canvas.getByRole("img", { name: new RegExp(`ply ${PLY}, White at the bottom`) }),
  ).toBeVisible();
  await userEvent.click(canvas.getByRole("button", { name: "Reset viewer" }));
  await expect(canvas.getByRole("img", { name: START_BOARD_LABEL })).toBeVisible();
  await expect((canvas.getByLabelText("Game UUID") as HTMLInputElement).value).toBe("");
  await expect((canvas.getByLabelText("Ply") as HTMLInputElement).value).toBe("");
};

export const Wide: Story = {
  name: "Wide",
};

export const Constrained: Story = {
  name: "Constrained",
  render: () => constrainedViewer(),
};

export const InvalidInputWide: Story = {
  name: "Invalid input - Wide",
  play: invalidInputPlay,
};

export const InvalidInputConstrained: Story = {
  name: "Invalid input - Constrained",
  render: (args) => constrainedViewer(args as { lookup?: PositionLookup }),
  play: invalidInputPlay,
};

export const LoadingWide: Story = {
  name: "Loading - Wide",
  args: { lookup: pendingLookup },
  play: loadingPlay,
};

export const LoadingConstrained: Story = {
  name: "Loading - Constrained",
  args: { lookup: pendingLookup },
  render: (args) => constrainedViewer(args as { lookup?: PositionLookup }),
  play: loadingPlay,
};

export const SuccessWhiteWide: Story = {
  name: "Successful retrieval (White) - Wide",
  args: { lookup: mockSuccessWhite },
  play: successPlay("White"),
};

export const SuccessWhiteConstrained: Story = {
  name: "Successful retrieval (White) - Constrained",
  args: { lookup: mockSuccessWhite },
  render: (args) => constrainedViewer(args as { lookup?: PositionLookup }),
  play: successPlay("White"),
};

export const SuccessBlackWide: Story = {
  name: "Successful retrieval (Black) - Wide",
  args: { lookup: mockSuccessBlack },
  play: successPlay("Black"),
};

export const SuccessBlackConstrained: Story = {
  name: "Successful retrieval (Black) - Constrained",
  args: { lookup: mockSuccessBlack },
  render: (args) => constrainedViewer(args as { lookup?: PositionLookup }),
  play: successPlay("Black"),
};

export const PositionNotFoundWide: Story = {
  name: "Position not found - Wide",
  args: { lookup: mockPositionNotFound },
  play: failurePlay("Position not found"),
};

export const PositionNotFoundConstrained: Story = {
  name: "Position not found - Constrained",
  args: { lookup: mockPositionNotFound },
  render: (args) => constrainedViewer(args as { lookup?: PositionLookup }),
  play: failurePlay("Position not found"),
};

export const CorpusUnavailableWide: Story = {
  name: "Corpus unavailable - Wide",
  args: { lookup: mockCorpusUnavailable },
  play: failurePlay("Corpus unavailable"),
};

export const CorpusUnavailableConstrained: Story = {
  name: "Corpus unavailable - Constrained",
  args: { lookup: mockCorpusUnavailable },
  render: (args) => constrainedViewer(args as { lookup?: PositionLookup }),
  play: failurePlay("Corpus unavailable"),
};

export const StoredPositionInvalidWide: Story = {
  name: "Stored position unavailable - Wide",
  args: { lookup: mockStoredPositionInvalid },
  play: failurePlay("Stored position unavailable"),
};

export const StoredPositionInvalidConstrained: Story = {
  name: "Stored position unavailable - Constrained",
  args: { lookup: mockStoredPositionInvalid },
  render: (args) => constrainedViewer(args as { lookup?: PositionLookup }),
  play: failurePlay("Stored position unavailable"),
};

export const UnexpectedFailureWide: Story = {
  name: "Unexpected request failure - Wide",
  args: { lookup: mockUnexpectedFailure },
  play: failurePlay("Unable to load position"),
};

export const UnexpectedFailureConstrained: Story = {
  name: "Unexpected request failure - Constrained",
  args: { lookup: mockUnexpectedFailure },
  render: (args) => constrainedViewer(args as { lookup?: PositionLookup }),
  play: failurePlay("Unable to load position"),
};

export const ResetWide: Story = {
  name: "Reset viewer - Wide",
  args: { lookup: mockSuccessWhite },
  play: resetPlay,
};

export const ResetConstrained: Story = {
  name: "Reset viewer - Constrained",
  args: { lookup: mockSuccessWhite },
  render: (args) => constrainedViewer(args as { lookup?: PositionLookup }),
  play: resetPlay,
};
