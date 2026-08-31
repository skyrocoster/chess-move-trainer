import { expect, userEvent, within } from "storybook/test";

export async function sharedPositionSummary(canvasElement: HTMLElement): Promise<HTMLElement> {
  const description = canvasElement.querySelector(
    '[data-testid="position-description-row"] button',
  );
  if (!(description instanceof HTMLElement)) {
    throw new Error("The shared position description trigger is missing.");
  }
  if (description.getAttribute("aria-expanded") === "false") {
    await userEvent.click(description);
  }
  const summary = canvasElement.querySelector(
    '[data-testid="position-description-row"] [data-position-summary]',
  );
  if (!(summary instanceof HTMLElement)) {
    throw new Error("The shared position summary is missing.");
  }
  return summary;
}

export async function expectPositionSquares(
  canvasElement: HTMLElement,
  square: string,
  count: number,
): Promise<void> {
  const summary = await sharedPositionSummary(canvasElement);
  await expect(summary.querySelectorAll(`[data-position-square="${square}"]`)).toHaveLength(count);
}

export async function expectSessionBoundary(canvasElement: HTMLElement): Promise<void> {
  const canvas = within(canvasElement);
  const session = canvas.getByTestId("repertoire-session");
  const sessionContent = within(session);
  await expect(session).toBeVisible();
  await expect(sessionContent.getByTestId("session-move-history")).toBeVisible();
  await expect(sessionContent.queryByTestId("session-san-history")).not.toBeInTheDocument();
  const status = sessionContent.getByTestId("session-status");
  await expect(status).toBeVisible();
  await expect(status).toHaveAttribute("role", "status");
  await expect(status).toHaveAttribute("aria-live", "polite");
  await expect(sessionContent.getByRole("heading", { name: "Preferred move" })).toBeVisible();
}

export async function expectSessionHistory(
  canvasElement: HTMLElement,
  entries: readonly string[],
): Promise<void> {
  const history = within(canvasElement).getByTestId("session-move-history");
  const buttons = within(history).getAllByRole("button");
  await expect(buttons).toHaveLength(entries.length);
  for (const [index, name] of entries.entries()) {
    await expect(buttons[index]).toHaveAccessibleName(name);
  }
}

export async function expectActiveSessionHistoryEntry(
  canvasElement: HTMLElement,
  name: string,
): Promise<void> {
  await expect(
    within(within(canvasElement).getByTestId("session-move-history")).getByRole("button", {
      name,
    }),
  ).toHaveAttribute("aria-current", "step");
}

export async function expectSingleStagedStatus(canvasElement: HTMLElement): Promise<void> {
  const canvas = within(canvasElement);
  const session = within(canvas.getByTestId("repertoire-session"));
  await expect(session.getByTestId("session-status")).toHaveTextContent("My move staged: e4.");
  await expect(canvas.getAllByText("My move staged: e4.", { exact: true })).toHaveLength(1);
}

export async function expectPreferredMoveState(
  canvasElement: HTMLElement,
  state: "empty" | "first-choice" | "saved" | "replacement" | "matching",
): Promise<void> {
  const panel = canvasElement.querySelector(`section[aria-labelledby="preferred-move-heading"]`);
  if (!(panel instanceof HTMLElement)) {
    throw new Error("The preferred move panel is missing.");
  }
  await expect(panel).toHaveAttribute("data-state", state);
  await expect(panel).toBeVisible();
}

export async function expectPositionReachFrequency(
  canvasElement: HTMLElement,
  state: "available" | "absent" | "unavailable",
  color: "White" | "Black",
  fraction?: string,
  percentage?: string,
): Promise<void> {
  const panel = canvasElement.querySelector(`section[data-state="${state}"] h2`);
  if (!(panel instanceof HTMLElement) || panel.textContent !== "Position reach frequency") {
    throw new Error(`The ${state} position reach frequency panel is missing.`);
  }
  const section = panel.closest("section");
  if (!(section instanceof HTMLElement)) {
    throw new Error("The position reach frequency section is missing.");
  }
  const scoped = within(section);
  await expect(scoped.getByText(`${color} repertoire colour`, { exact: true })).toBeVisible();
  if (fraction !== undefined) {
    await expect(scoped.getByText(fraction, { exact: true })).toBeVisible();
  }
  if (percentage !== undefined) {
    await expect(scoped.getByText(percentage, { exact: true })).toBeVisible();
  }
  if (state === "available") {
    await expect(
      scoped.getByRole("meter", { name: `Position reach frequency as ${color}` }),
    ).toBeVisible();
  } else {
    await expect(scoped.queryByRole("meter")).not.toBeInTheDocument();
  }
}
