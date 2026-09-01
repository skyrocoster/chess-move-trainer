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
  await expect(
    sessionContent.getByRole("heading", { name: "What is saved, and what is staged?" }),
  ).toBeVisible();
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
  return expectStagedStatus(canvasElement, "e4");
}

export async function expectStagedStatus(canvasElement: HTMLElement, san: string): Promise<void> {
  const canvas = within(canvasElement);
  const session = within(canvas.getByTestId("repertoire-session"));
  const status = `My move staged: ${san}.`;
  await expect(session.getByTestId("session-status")).toHaveTextContent(status);
  await expect(canvas.getAllByText(status, { exact: true })).toHaveLength(1);
}

export async function expectPreferredMoveState(
  canvasElement: HTMLElement,
  state: "empty" | "first-choice" | "saved" | "replacement" | "matching" | "unknown",
): Promise<void> {
  const panel = canvasElement.querySelector(`section[aria-labelledby="preferred-move-heading"]`);
  if (!(panel instanceof HTMLElement)) {
    throw new Error("The preferred move panel is missing.");
  }
  await expect(panel).toHaveAttribute("data-state", state);
  await expect(panel).toBeVisible();
}

export async function expectPreferredActions(
  canvasElement: HTMLElement,
  actions: readonly string[],
): Promise<void> {
  const panel = canvasElement.querySelector('section[aria-labelledby="preferred-move-heading"]');
  if (!(panel instanceof HTMLElement)) {
    throw new Error("The preferred move panel is missing.");
  }
  const actual = within(panel)
    .queryAllByRole("button")
    .map((button) => button.textContent?.trim() ?? "")
    .filter((label) => ["Save", "Change effective date", "Remove"].includes(label));
  await expect(actual).toEqual(actions);
}

export async function expectDeferredDateAction(canvasElement: HTMLElement): Promise<void> {
  const panel = canvasElement.querySelector('section[aria-labelledby="preferred-move-heading"]');
  if (!(panel instanceof HTMLElement)) {
    throw new Error("The preferred move panel is missing.");
  }
  const scoped = within(panel);
  const date = scoped.getByRole("button", { name: "Change effective date" });
  await expect(date).toBeDisabled();
  await expect(date).toHaveAccessibleDescription("Date changes are temporarily unavailable");
  await expect(scoped.queryByTestId("calendar-date-popup")).not.toBeInTheDocument();
}

export async function expectNoPreferredActions(canvasElement: HTMLElement): Promise<void> {
  const panel = canvasElement.querySelector('section[aria-labelledby="preferred-move-heading"]');
  if (!(panel instanceof HTMLElement)) {
    throw new Error("The preferred move panel is missing.");
  }
  const scoped = within(panel);
  for (const label of ["Add", "Edit", "Cancel edit", "Save replacement", "Play saved move"]) {
    await expect(scoped.queryByRole("button", { name: label })).not.toBeInTheDocument();
  }
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
