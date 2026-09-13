import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import {
  PreferredMoveSchedulePrototype,
  type PreferredMoveSchedulePeriod,
} from "./PreferredMoveSchedulePrototype";
import { storyViewport } from "../../storybook/viewports";

const PERIODS: PreferredMoveSchedulePeriod[] = [
  {
    id: "e4-september",
    move: { san: "e4", uci: "e2e4" },
    effectiveFrom: "2026-09-01",
    effectiveUntil: "2026-09-14",
  },
  {
    id: "no-preference",
    move: null,
    effectiveFrom: "2026-09-14",
    effectiveUntil: "2026-09-21",
  },
  {
    id: "nf3-autumn",
    move: { san: "Nf3", uci: "g1f3" },
    effectiveFrom: "2026-09-21",
    effectiveUntil: "2026-10-06",
  },
  {
    id: "d4-ongoing",
    move: { san: "d4", uci: "d2d4" },
    effectiveFrom: "2026-10-06",
    effectiveUntil: null,
  },
];

const meta = {
  title: "In Development/Application/Repertoire Builder/Preferred Move Effective Dates",
  tags: ["status-in-development"],
  component: PreferredMoveSchedulePrototype,
  parameters: {
    layout: "fullscreen",
    a11y: { test: "error" },
  },
  args: {
    selectedMove: { san: "Nf3", uci: "g1f3" },
    periods: PERIODS,
    initialDate: "2026-09-01",
    initialSelection: {
      effectiveFrom: "2026-09-24",
      effectiveUntil: "2026-10-04",
    },
    onApply: fn(),
  },
} satisfies Meta<typeof PreferredMoveSchedulePrototype>;

export default meta;
type Story = StoryObj<typeof meta>;

export const CalendarWithDraft: Story = {
  name: "Calendar with a draft range",
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getByRole("heading", { name: "Effective-date schedule" }),
    ).toBeVisible();
    await expect(
      canvas.getByRole("region", { name: "Preferred move effective-date calendar" }),
    ).toBeVisible();
    await expect(canvas.getByText("4 periods")).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Use Nf3" })).toBeEnabled();

    await userEvent.click(canvas.getByRole("button", { name: "Use Nf3" }));

    await expect(args.onApply).toHaveBeenCalledWith("assign", {
      effectiveFrom: "2026-09-24",
      effectiveUntil: "2026-10-04",
    });
    await expect(canvas.getByRole("status")).toHaveTextContent(
      "Nf3 drafted for Sep 24, 2026 – Oct 3, 2026.",
    );
  },
};

export const OpenEndedDraft: Story = {
  name: "Draft continuing indefinitely",
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("checkbox", { name: "Continue indefinitely" }));
    await expect(canvas.getByRole("heading", { name: "From Sep 24, 2026 onward" })).toBeVisible();

    await userEvent.click(canvas.getByRole("button", { name: "No preferred move" }));

    await expect(args.onApply).toHaveBeenCalledWith("no_preference", {
      effectiveFrom: "2026-09-24",
      effectiveUntil: null,
    });
  },
};

export const NarrowCalendar: Story = {
  name: "Responsive — 390px calendar and schedule",
  parameters: storyViewport("phone-390"),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getByRole("region", { name: "Preferred move effective-date calendar" }),
    ).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Use Nf3" })).toBeVisible();
    await expect(canvasElement.ownerDocument.documentElement.scrollWidth).toBeLessThanOrEqual(
      canvasElement.ownerDocument.documentElement.clientWidth,
    );
  },
};
