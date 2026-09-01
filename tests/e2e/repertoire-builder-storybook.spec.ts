import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const STORYBOOK_ROOT = "#storybook-root";
const GAME_UUID = "0007925c-5a8d-11f0-9740-f690a301000f";
const STORY_IDS = {
  wide: "application-repertoire-builder-workspace--wide",
  constrained: "application-repertoire-builder-workspace--constrained",
  stagedMy: "application-repertoire-builder-workspace--staged-my",
  storedPrefix: "application-repertoire-builder-workspace--stored-prefix-black-subject",
  opponent: "application-repertoire-builder-workspace--opponent-immediate",
  navigation: "application-repertoire-builder-workspace--navigation-and-replacement",
  flip: "application-repertoire-builder-workspace--flip-cancellation",
  promotion: "application-repertoire-builder-workspace--promotion-preferred",
  zeroPersonal: "application-repertoire-builder-workspace--zero-personal-count",
  absent: "application-repertoire-builder-workspace--absent-unsavable",
  savedChoiceStages: "application-repertoire-builder-workspace--saved-choice-stages-move",
  savedNoStage: "application-repertoire-builder-workspace--saved-no-stage",
  firstChoice: "application-repertoire-builder-workspace--first-choice",
  replacement: "application-repertoire-builder-workspace--replacement-constrained",
  matching: "application-repertoire-builder-workspace--matching",
  savedBoxKeyboard: "application-repertoire-builder-workspace--saved-box-keyboard",
  saveReplacement: "application-repertoire-builder-workspace--save-replacement",
  removeRetainsStaging: "application-repertoire-builder-workspace--remove-retains-staging",
  pendingSave: "application-repertoire-builder-workspace--pending-save",
  pendingRemove: "application-repertoire-builder-workspace--pending-remove",
  saveFailure: "application-repertoire-builder-workspace--save-failure-retention",
  removeFailure: "application-repertoire-builder-workspace--remove-failure-retention",
  accessibility: "application-repertoire-builder-workspace--accessibility-and-responsive",
  readErrors: "application-repertoire-builder-workspace--read-errors",
  unsavable: "application-repertoire-builder-workspace--unsavable-gate",
  loading: "application-repertoire-builder-workspace--loading-gate",
  opponentGate: "application-repertoire-builder-workspace--opponent-turn-gate",
  opponentLocal: "application-repertoire-builder-workspace--opponent-local-only",
} as const;

async function openStory(
  page: Page,
  storyId: string,
  width = 1280,
  height = 900,
) {
  await page.setViewportSize({ width, height });
  await page.goto(`${STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
  await expect(page.locator(STORYBOOK_ROOT)).toBeVisible({ timeout: 30_000 });
  await expect(
    page.getByRole("heading", { name: "Repertoire Builder", level: 1 }),
  ).toBeVisible({ timeout: 30_000 });
}

function preferredPanel(page: Page) {
  return page.getByRole("region", { name: "What is saved, and what is staged?" });
}

async function expectPreferredRelationship(
  page: Page,
  state: "empty" | "first-choice" | "saved" | "replacement" | "matching" | "unknown",
) {
  await expect(preferredPanel(page)).toHaveAttribute("data-state", state);
}

async function expectPreferredActions(page: Page, actions: readonly string[]) {
  const actual = (await preferredPanel(page).getByRole("button").allTextContents()).filter((label) =>
    ["Save", "Change effective date", "Remove"].includes(label.trim()),
  );
  expect(actual.map((label) => label.trim())).toEqual(actions);
}

async function expectDeferredDate(page: Page) {
  const date = preferredPanel(page).getByRole("button", { name: "Change effective date" });
  await expect(date).toBeDisabled();
  await expect(date).toHaveAccessibleDescription("Date changes are temporarily unavailable");
  await expect(page.getByTestId("calendar-date-popup")).toHaveCount(0);
}

async function expectBothRelationshipBoxes(page: Page) {
  await expect(preferredPanel(page).getByTestId("saved-move")).toBeVisible();
  await expect(preferredPanel(page).getByTestId("staged-move")).toBeVisible();
  await expect(preferredPanel(page).getByText("Current saved choice", { exact: true })).toBeVisible();
  await expect(preferredPanel(page).getByText("Staged move", { exact: true })).toBeVisible();
}

async function expectSessionHistory(page: Page, entries: readonly string[]) {
  const history = page.getByTestId("session-move-history");
  await expect(history).toBeVisible();
  const buttons = history.getByRole("button");
  await expect(buttons).toHaveCount(entries.length);
  for (const [index, name] of entries.entries()) {
    await expect(buttons.nth(index)).toHaveAccessibleName(name);
  }
}

async function expectActiveSessionHistoryEntry(page: Page, name: string) {
  await expect(
    page.getByTestId("session-move-history").getByRole("button", { name }),
  ).toHaveAttribute("aria-current", "step");
}

async function sharedPositionSummary(page: Page) {
  const row = page.getByTestId("position-description-row");
  const description = row.getByRole("button", { name: "Position description" });
  await expect(description).toHaveAttribute("aria-expanded", "true");
  const summary = row.locator("[data-position-summary]");
  await expect(summary).toBeVisible();
  return summary;
}

async function expectPositionSquares(page: Page, square: string, count: number) {
  await expect((await sharedPositionSummary(page)).locator(`[data-position-square="${square}"]`)).toHaveCount(count);
}

async function expectNoHorizontalOverflow(page: Page) {
  const dimensions = await page.evaluate(() => ({
    documentClientWidth: document.documentElement.clientWidth,
    documentScrollWidth: document.documentElement.scrollWidth,
    bodyClientWidth: document.body.clientWidth,
    bodyScrollWidth: document.body.scrollWidth,
  }));
  expect(dimensions.documentScrollWidth).toBeLessThanOrEqual(dimensions.documentClientWidth);
  expect(dimensions.bodyScrollWidth).toBeLessThanOrEqual(dimensions.bodyClientWidth);
}

async function checkA11y(page: Page) {
  for (let attempt = 0; attempt < 4; attempt += 1) {
    try {
      const results = await new AxeBuilder({ page })
        .include(STORYBOOK_ROOT)
        .disableRules(["landmark-one-main", "page-has-heading-one", "region"])
        .analyze();
      expect(results.violations).toEqual([]);
      return;
    } catch (error) {
      if (!(error instanceof Error) || !error.message.includes("Axe is already running")) {
        throw error;
      }
      await page.waitForTimeout(250);
    }
  }
  throw new Error("Axe accessibility scan remained busy after bounded retries.");
}

function preferredRequestUrls(page: Page) {
  const urls: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/preferred-move")) urls.push(request.url());
  });
  return urls;
}

test.describe("Repertoire Builder Storybook surface", () => {
  test.describe.configure({ timeout: 30_000 });

  test("proves empty relationship boxes, session boundaries, and 412px composition", async ({ page }) => {
    await openStory(page, STORY_IDS.wide);
    await expectPreferredRelationship(page, "empty");
    await expectBothRelationshipBoxes(page);
    await expect(preferredPanel(page).getByText("No saved choice yet.")).toBeVisible();
    await expect(preferredPanel(page).getByText("No move staged.")).toBeVisible();
    await expect(
      preferredPanel(page).getByText("Stage a legal move to propose the first saved choice."),
    ).toBeVisible();
    await expectPreferredActions(page, []);
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);

    await openStory(page, STORY_IDS.constrained, 412, 915);
    await expectPreferredRelationship(page, "empty");
    await expectBothRelationshipBoxes(page);
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });

  test("proves all five saved/staged relationship readings and disabled date behavior", async ({ page }) => {
    const requests = preferredRequestUrls(page);

    await openStory(page, STORY_IDS.firstChoice);
    await expectPreferredRelationship(page, "first-choice");
    await expectBothRelationshipBoxes(page);
    await expect(preferredPanel(page).getByText("Save e4 as the current saved choice.")).toBeVisible();
    await expectPreferredActions(page, ["Save", "Change effective date"]);
    await expectDeferredDate(page);

    await openStory(page, STORY_IDS.savedNoStage);
    await expectPreferredRelationship(page, "saved");
    await expectBothRelationshipBoxes(page);
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expect(preferredPanel(page).getByText("No move staged.")).toBeVisible();
    await expectPreferredActions(page, ["Change effective date", "Remove"]);
    await expectDeferredDate(page);

    await openStory(page, STORY_IDS.replacement, 412, 915);
    await expectPreferredRelationship(page, "replacement");
    await expect(preferredPanel(page).getByText("Save d4 to replace e4.")).toBeVisible();
    await expectPreferredActions(page, ["Save", "Change effective date", "Remove"]);
    await expectDeferredDate(page);
    await expectNoHorizontalOverflow(page);

    await openStory(page, STORY_IDS.matching);
    await expectPreferredRelationship(page, "matching");
    await expect(preferredPanel(page).getByText("e4 is already the current saved choice.")).toBeVisible();
    await expectPreferredActions(page, ["Change effective date", "Remove"]);
    await expect(
      preferredPanel(page)
        .getByTestId("preferred-actions")
        .getByRole("button", { name: "Save", exact: true }),
    ).toHaveCount(0);

    expect(requests).toEqual([]);
    await checkA11y(page);
  });

  test("proves saved-box pointer/keyboard staging without history or preferred mutation", async ({ page }) => {
    const requests = preferredRequestUrls(page);
    await openStory(page, STORY_IDS.savedBoxKeyboard);
    await expectPreferredRelationship(page, "matching");
    const savedBox = preferredPanel(page).getByRole("button", {
      name: "Current saved choice: e4; play and stage this move.",
    });
    await expect(savedBox).toBeFocused();
    await expect(savedBox).toHaveAttribute("type", "button");
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText(/e4.*e2e4/);
    await expectPreferredActions(page, ["Change effective date", "Remove"]);
    await expectSessionHistory(page, ["Initial position"]);
    await expectActiveSessionHistoryEntry(page, "Initial position");
    await expectPositionSquares(page, "e2", 0);
    await expectPositionSquares(page, "e4", 1);
    await expectNoHorizontalOverflow(page);
    expect(requests).toEqual([]);
    await checkA11y(page);
  });

  test("proves Save first choice/replacement refresh and board/history invariants", async ({ page }) => {
    await openStory(page, STORY_IDS.saveReplacement);
    await expectPreferredRelationship(page, "saved");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText(/d4.*d2d4/);
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText("No move staged.");
    await expectPositionSquares(page, "d2", 1);
    await expectPositionSquares(page, "d4", 0);
    await expectSessionHistory(page, ["Initial position"]);
    await expect(
      preferredPanel(page)
        .getByTestId("preferred-actions")
        .getByRole("button", { name: "Save", exact: true }),
    ).toHaveCount(0);
    await expectPreferredActions(page, ["Change effective date", "Remove"]);

    await openStory(page, STORY_IDS.firstChoice);
    await expectPreferredRelationship(page, "first-choice");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("No saved choice yet.");
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText(/e4.*e2e4/);
    await expectSessionHistory(page, ["Initial position"]);
    await expectDeferredDate(page);
  });

  test("proves Remove confirmation, cancellation focus, and retained staging", async ({ page }) => {
    await openStory(page, STORY_IDS.removeRetainsStaging);
    await expect(page.getByText("Preferred move removed.", { exact: true })).toBeVisible({
      timeout: 15_000,
    });
    await expectPreferredRelationship(page, "first-choice");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("No saved choice yet.");
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText(/d4.*d2d4/);
    await expectPreferredActions(page, ["Save", "Change effective date"]);
    await expectDeferredDate(page);
    await expectSessionHistory(page, ["Initial position"]);
    await checkA11y(page);
  });

  test("proves pending and failed mutations retain confirmed and staged facts", async ({ page }) => {
    await openStory(page, STORY_IDS.pendingSave);
    await expect(preferredPanel(page).getByText("Saving preferred move...")).toBeVisible();
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText(/d4.*d2d4/);
    await expectPreferredActions(page, ["Save", "Change effective date", "Remove"]);
    await expect(
      preferredPanel(page)
        .getByTestId("preferred-actions")
        .getByRole("button", { name: "Save", exact: true }),
    ).toBeDisabled();

    await openStory(page, STORY_IDS.pendingRemove);
    await expect(preferredPanel(page).getByText("Removing preferred move...")).toBeVisible();
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expectPreferredActions(page, ["Change effective date", "Remove"]);
    await expect(preferredPanel(page).getByRole("button", { name: "Remove" })).toBeDisabled();

    await openStory(page, STORY_IDS.saveFailure);
    await expect(page.getByRole("alert")).toHaveText("The preferred move could not be updated. Try again.");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText(/d4.*d2d4/);

    await openStory(page, STORY_IDS.removeFailure);
    await expect(page.getByRole("alert")).toHaveText("The preferred move could not be updated. Try again.");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expect(preferredPanel(page).getByRole("button", { name: "Remove" })).toBeEnabled();
    await checkA11y(page);
  });

  test("proves gates, typed read feedback, loading, and opponent local history", async ({ page }) => {
    await openStory(page, STORY_IDS.unsavable);
    await expectPreferredRelationship(page, "empty");
    await expect(preferredPanel(page).getByText("This position cannot be saved because it is not in the corpus.")).toBeVisible();
    await expectPreferredActions(page, []);

    await openStory(page, STORY_IDS.loading);
    await expectPreferredRelationship(page, "unknown");
    await expect(preferredPanel(page).getByTestId("preferred-status")).toHaveText("Loading saved choice...");
    await expectPreferredActions(page, []);

    await openStory(page, STORY_IDS.readErrors);
    await expectPreferredRelationship(page, "unknown");
    await expect(page.getByRole("alert")).toHaveCount(2);
    await expectPreferredActions(page, []);

    await openStory(page, STORY_IDS.opponentGate);
    await expectPreferredRelationship(page, "empty");
    await expect(preferredPanel(page).getByText("Wait for your turn to stage or save a preferred move.")).toBeVisible();
    await expectPreferredActions(page, []);
    await expect(preferredPanel(page).getByRole("button", { name: /play and stage this move/ })).toHaveCount(0);

    await openStory(page, STORY_IDS.opponentLocal);
    await expect(page.getByTestId("session-move-history").getByRole("button")).toHaveCount(4, {
      timeout: 15_000,
    });
    await expectSessionHistory(page, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(page, "White, move 2, Nf3");
    await expectPreferredActions(page, []);
    await checkA11y(page);
  });

  test("proves promotion canonical identity and source/history invariants", async ({ page }) => {
    await openStory(page, STORY_IDS.promotion);
    await expect(preferredPanel(page)).toHaveAttribute("data-state", "first-choice", {
      timeout: 15_000,
    });
    await expectPreferredRelationship(page, "first-choice");
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText(/e8=N.*e7e8n/);
    await expectSessionHistory(page, ["Initial position"]);
    await expectPositionSquares(page, "e7", 0);
    await expectPositionSquares(page, "e8", 1);
    await expect(page.getByTestId("session-origin")).toHaveText(/Current Ply 0/);
    await checkA11y(page);
  });

  test("proves preserved move-history navigation and responsive focus semantics", async ({ page }) => {
    await openStory(page, STORY_IDS.navigation);
    await expectSessionHistory(page, ["Initial position", "White, move 1, e4", "Black, move 1, e6"]);
    await expectActiveSessionHistoryEntry(page, "Black, move 1, e6");
    await expect(page.getByRole("button", { name: "Next" })).toBeDisabled();

    await openStory(page, STORY_IDS.accessibility, 412, 915);
    const savedBox = preferredPanel(page).getByRole("button", {
      name: "Current saved choice: e4; play and stage this move.",
    });
    await savedBox.focus();
    await expect(savedBox).toBeFocused();
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });
});
