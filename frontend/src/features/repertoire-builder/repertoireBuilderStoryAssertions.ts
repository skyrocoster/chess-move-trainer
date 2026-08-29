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
  await expect(sessionContent.getByTestId("session-san-history")).toBeVisible();
  const status = sessionContent.getByTestId("session-status");
  await expect(status).toBeVisible();
  await expect(status).toHaveAttribute("role", "status");
  await expect(status).toHaveAttribute("aria-live", "polite");
  await expect(sessionContent.getByRole("heading", { name: "Preferred move" })).toBeVisible();
}

export async function expectSingleStagedStatus(canvasElement: HTMLElement): Promise<void> {
  const canvas = within(canvasElement);
  const session = within(canvas.getByTestId("repertoire-session"));
  await expect(session.getByTestId("session-status")).toHaveTextContent("My move staged: e4.");
  await expect(canvas.getAllByText("My move staged: e4.", { exact: true })).toHaveLength(1);
}
