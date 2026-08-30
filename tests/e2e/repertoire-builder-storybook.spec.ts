import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const STORYBOOK_ROOT = "#storybook-root";
const GAME_UUID = "0007925c-5a8d-11f0-9740-f690a301000f";
const STORY_IDS = {
  wide: "application-repertoire-builder-workspace--wide",
  constrained: "application-repertoire-builder-workspace--constrained",
  stagedMy: "application-repertoire-builder-workspace--staged-my",
  storedPrefix:
    "application-repertoire-builder-workspace--stored-prefix-black-subject",
  opponent: "application-repertoire-builder-workspace--opponent-immediate",
  navigation:
    "application-repertoire-builder-workspace--navigation-and-replacement",
  flip: "application-repertoire-builder-workspace--flip-cancellation",
  promotion: "application-repertoire-builder-workspace--promotion",
  unassigned: "application-repertoire-builder-workspace--unassigned-savable",
  zeroPersonal: "application-repertoire-builder-workspace--zero-personal-count",
  absent: "application-repertoire-builder-workspace--absent-unsavable",
  assigned: "application-repertoire-builder-workspace--assigned-read-only",
  boardPlay: "application-repertoire-builder-workspace--assigned-board-play",
  assignedToday: "application-repertoire-builder-workspace--assigned-today",
  unsavedPlayed: "application-repertoire-builder-workspace--unsaved-played-constrained",
  keyboard: "application-repertoire-builder-workspace--keyboard-and-accessibility",
  replacement: "application-repertoire-builder-workspace--edit-replacement",
  datedAdd: "application-repertoire-builder-workspace--dated-add",
  mutationFailure: "application-repertoire-builder-workspace--mutation-failure",
  remove: "application-repertoire-builder-workspace--remove-confirmation",
  readErrors: "application-repertoire-builder-workspace--read-errors",
  opponentLocal:
    "application-repertoire-builder-workspace--opponent-local-only",
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

async function sharedPositionSummary(page: Page) {
  const row = page.getByTestId("position-description-row");
  const description = row.getByRole("button", { name: "Position description" });
  await expect(description).toHaveAttribute("aria-expanded", "true");
  const summary = row.locator("[data-position-summary]");
  await expect(summary).toBeVisible();
  return summary;
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

async function expectPreferredMoveState(
  page: Page,
  state: "no-saved" | "saved" | "matching-played" | "unsaved-played",
) {
  await expect(page.getByRole("region", { name: "Preferred move" })).toHaveAttribute(
    "data-state",
    state,
  );
}

async function expectPositionReachFrequency(
  page: Page,
  state: "available" | "absent" | "unavailable",
  color: "White" | "Black",
  fraction?: string,
  percentage?: string,
) {
  const panel = page.locator(`section[data-state="${state}"]`).filter({
    has: page.getByRole("heading", { name: "Position reach frequency" }),
  });
  await expect(panel).toHaveCount(1);
  await expect(panel.getByText(`${color} repertoire colour`, { exact: true })).toBeVisible();
  if (fraction !== undefined) {
    await expect(panel.getByText(fraction, { exact: true })).toBeVisible();
  }
  if (percentage !== undefined) {
    await expect(panel.getByText(percentage, { exact: true })).toBeVisible();
  }
  if (state === "available") {
    await expect(
      panel.getByRole("meter", { name: `Position reach frequency as ${color}` }),
    ).toBeVisible();
  } else {
    await expect(panel.getByRole("meter")).toHaveCount(0);
  }
}

async function expectActiveSessionHistoryEntry(page: Page, name: string) {
  await expect(
    page.getByTestId("session-move-history").getByRole("button", { name }),
  ).toHaveAttribute("aria-current", "step");
}

async function expectNoHorizontalOverflow(page: Page) {
  const dimensions = await page.evaluate(() => ({
    documentClientWidth: document.documentElement.clientWidth,
    documentScrollWidth: document.documentElement.scrollWidth,
    bodyClientWidth: document.body.clientWidth,
    bodyScrollWidth: document.body.scrollWidth,
  }));
  expect(dimensions.documentScrollWidth).toBeLessThanOrEqual(
    dimensions.documentClientWidth,
  );
  expect(dimensions.bodyScrollWidth).toBeLessThanOrEqual(
    dimensions.bodyClientWidth,
  );
}

type RailExpectation = {
  orientation: "white" | "black";
  state: "neutral" | "pending" | "best-line";
  value: number;
  shortValue: string;
  accessibleValue: string;
};

async function expectRailGeometry(page: Page, expected: RailExpectation) {
  const stage = page.getByTestId("board-eval-stage");
  const board = stage.locator("[data-board-visual]");
  const rail = page.getByTestId("board-eval-rail-shell");
  const meter = page.getByRole("meter", { name: "Evaluation" });
  const track = meter.locator('[class*="track"]');
  const indicator = meter.locator('[class*="indicator"]');

  await expect(stage).toBeVisible();
  await expect(board).toBeVisible();
  await expect(rail).toBeVisible();
  await expect(
    stage.filter({ has: page.locator("[data-board-visual]") }),
  ).toHaveCount(1);
  await expect(
    stage.filter({ has: page.getByTestId("board-eval-rail-shell") }),
  ).toHaveCount(1);
  await expect(meter).toHaveAttribute("data-orientation", expected.orientation);
  await expect(meter).toHaveAttribute("data-state", expected.state);
  await expect(meter).toHaveAttribute("aria-valuemin", "0");
  await expect(meter).toHaveAttribute("aria-valuemax", "100");
  await expect(meter).toHaveAttribute("aria-valuenow", String(expected.value));
  await expect(meter).toHaveAttribute("aria-valuetext", expected.accessibleValue);
  await expect(meter).toContainText(expected.shortValue);

  const boardBox = await board.boundingBox();
  const railBox = await rail.boundingBox();
  const trackBox = await track.boundingBox();
  const indicatorBox = await indicator.boundingBox();
  expect(boardBox).not.toBeNull();
  expect(railBox).not.toBeNull();
  expect(trackBox).not.toBeNull();
  expect(indicatorBox).not.toBeNull();
  if (!boardBox || !railBox || !trackBox || !indicatorBox) {
    throw new Error("The repertoire board/evaluation geometry did not render.");
  }
  expect(railBox.width).toBe(30);
  expect(Math.abs(railBox.x - (boardBox.x + boardBox.width))).toBeLessThanOrEqual(0.01);
  expect(Math.abs(boardBox.y - railBox.y)).toBeLessThanOrEqual(1);
  expect(Math.abs(boardBox.height - railBox.height)).toBeLessThanOrEqual(1);
  const overflow = await stage.evaluate((element) => ({
    clientWidth: element.clientWidth,
    scrollWidth: element.scrollWidth,
  }));
  expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth);
  const topDistance = indicatorBox.y - trackBox.y;
  const bottomDistance = trackBox.y + trackBox.height - (indicatorBox.y + indicatorBox.height);
  if (expected.orientation === "white") {
    expect(bottomDistance).toBeLessThanOrEqual(1);
    expect(topDistance).toBeGreaterThan(1);
  } else {
    expect(topDistance).toBeLessThanOrEqual(1);
    expect(bottomDistance).toBeGreaterThan(1);
  }
}

async function expectSessionPlacement(page: Page, placement: "wide" | "constrained") {
  const stageBox = await page.getByTestId("board-eval-stage").boundingBox();
  const railBox = await page.getByTestId("board-eval-rail-shell").boundingBox();
  const sessionBox = await page.getByTestId("repertoire-session").boundingBox();
  expect(stageBox).not.toBeNull();
  expect(railBox).not.toBeNull();
  expect(sessionBox).not.toBeNull();
  if (!stageBox || !railBox || !sessionBox) {
    throw new Error("The repertoire placement geometry did not render.");
  }

  if (placement === "wide") {
    expect(sessionBox.x).toBeGreaterThanOrEqual(railBox.x + railBox.width);
  } else {
    expect(sessionBox.y).toBeGreaterThanOrEqual(stageBox.y + stageBox.height);
  }
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
      if (
        !(error instanceof Error) ||
        !error.message.includes("Axe is already running")
      ) {
        throw error;
      }
      await page.waitForTimeout(250);
    }
  }
  throw new Error(
    "Axe accessibility scan remained busy after bounded retries.",
  );
}

test.describe("Repertoire Builder Storybook surface", () => {
  test.describe.configure({ timeout: 30_000 });

  test("proves the standard workspace at wide and constrained widths", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.wide, 1280, 900);
    await expect(
      page.getByRole("group", {
        name: "Chess board: standard starting position, White at the bottom",
      }),
    ).toBeVisible();
    const session = page.getByTestId("repertoire-session");
    await expect(session).toBeVisible();
    await expect(session.getByTestId("session-move-history")).toBeVisible();
    await expect(session.getByTestId("session-san-history")).toHaveCount(0);
    await expect(session.getByTestId("session-status")).toHaveAttribute(
      "role",
      "status",
    );
    await expect(session.getByRole("heading", { name: "Preferred move" })).toBeVisible();
    await expectPreferredMoveState(page, "no-saved");
    await expectPositionReachFrequency(page, "available", "White", "3 / 10 games", "30%");
    await expectRailGeometry(page, {
      orientation: "white",
      state: "neutral",
      value: 50,
      shortValue: "0.00",
      accessibleValue: "No analysis yet; evaluation neutral.",
    });
    await expectSessionPlacement(page, "wide");
    const summary = await sharedPositionSummary(page);
    await expect(summary).toContainText("OrientationWhite at the bottom");
    await expect(summary).toContainText("Side to moveWhite");
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);

    await openStory(page, STORY_IDS.constrained, 412, 915);
    await expect(
      page.getByRole("group", {
        name: "Chess board: standard starting position, White at the bottom",
      }),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Flip" })).toBeVisible();
    await expectRailGeometry(page, {
      orientation: "white",
      state: "neutral",
      value: 50,
      shortValue: "0.00",
      accessibleValue: "No analysis yet; evaluation neutral.",
    });
    await expectSessionPlacement(page, "constrained");
    await expectPreferredMoveState(page, "no-saved");
    await expectPositionReachFrequency(page, "available", "White", "3 / 10 games", "30%");
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);

    await openStory(page, STORY_IDS.stagedMy, 1280, 900);
    await expect(page.getByTestId("session-origin")).toHaveText(/Current Ply 0/);
    const widePreview = await sharedPositionSummary(page);
    await expect(widePreview.locator('[data-position-square="e2"]')).toHaveCount(0);
    await expect(widePreview.locator('[data-position-square="e4"]')).toHaveCount(1);
    await expect(widePreview).toContainText("Side to moveBlack");
    await expectSessionHistory(page, ["Initial position"]);
    await expectRailGeometry(page, {
      orientation: "white",
      state: "best-line",
      value: 51.7,
      shortValue: "+0.34",
      accessibleValue: "best-line evaluation +0.34.",
    });
    await expectPreferredMoveState(page, "unsaved-played");
    await expect(page.getByTestId("played-move")).toHaveText("Played move: e4 (e2e4)");
    await expect(page.getByText("This move is not saved as your preferred move.")).toBeVisible();
    await expectPositionReachFrequency(page, "available", "White", "3 / 10 games", "30%");
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);

    await openStory(page, STORY_IDS.stagedMy, 412, 915);
    await expect(page.getByTestId("session-origin")).toHaveText(/Current Ply 0/);
    const constrainedPreview = await sharedPositionSummary(page);
    await expect(constrainedPreview.locator('[data-position-square="e2"]')).toHaveCount(0);
    await expect(constrainedPreview.locator('[data-position-square="e4"]')).toHaveCount(1);
    await expect(constrainedPreview).toContainText("Side to moveBlack");
    await expectSessionHistory(page, ["Initial position"]);
    await expectRailGeometry(page, {
      orientation: "white",
      state: "best-line",
      value: 51.7,
      shortValue: "+0.34",
      accessibleValue: "best-line evaluation +0.34.",
    });
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });

  test("proves the complete stored prefix, Black subject, and opponent move", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.storedPrefix);
    await expect(
      page.getByRole("group", {
        name: `Chess board: game ${GAME_UUID}, ply 2, Black at the bottom`,
      }),
    ).toBeVisible();
    await expectSessionHistory(page, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
    ]);
    await expectActiveSessionHistoryEntry(page, "Black, move 1, e5");
    await expectPreferredMoveState(page, "no-saved");
    await expectPositionReachFrequency(page, "available", "Black", "2 / 10 games", "20%");
    await expectRailGeometry(page, {
      orientation: "black",
      state: "neutral",
      value: 50,
      shortValue: "0.00",
      accessibleValue: "No analysis yet; evaluation neutral.",
    });
    const summary = await sharedPositionSummary(page);
    await expect(summary).toContainText("OrientationBlack at the bottom");
    await expect(summary).toContainText("Side to moveWhite");
    await checkA11y(page);

    await openStory(page, STORY_IDS.opponent);
    await expectSessionHistory(page, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(page, "White, move 2, Nf3");
    await expect(page.getByTestId("session-status")).toHaveText(
      "Opponent move played locally: Nf3.",
    );
    await expect(page.getByTestId("session-origin")).toHaveText(/Current Ply 3/);
    await expect(
      page.getByRole("group", {
        name: `Chess board: game ${GAME_UUID}, ply 3, Black at the bottom`,
      }),
    ).toBeVisible();
    await expect(page.getByTestId("preferred-context")).toHaveText(
      "Seen in 2 games as Black",
    );
    await expectPreferredMoveState(page, "no-saved");
    await expectPositionReachFrequency(page, "available", "Black", "2 / 10 games", "20%");
    await expectRailGeometry(page, {
      orientation: "black",
      state: "best-line",
      value: 51.7,
      shortValue: "+0.34",
      accessibleValue: "best-line evaluation +0.34.",
    });
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
    await page.screenshot({
      path: "test-results/repertoire-r1-wide.png",
      fullPage: true,
    });

    await openStory(page, STORY_IDS.opponent, 480, 1000);
    await expectSessionHistory(page, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(page, "White, move 2, Nf3");
    await expect(
      page.getByRole("group", {
        name: `Chess board: game ${GAME_UUID}, ply 3, Black at the bottom`,
      }),
    ).toBeVisible();
    await expect(page.getByTestId("preferred-context")).toHaveText(
      "Seen in 2 games as Black",
    );
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
    await page.screenshot({
      path: "test-results/repertoire-r1-constrained.png",
      fullPage: true,
    });
  });

  test("proves navigation, replacement truncation, and Flip cancellation", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.opponent);
    await expectSessionHistory(page, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    const storedPrefixEntry = page.getByRole("button", { name: "White, move 1, e4" });
    await storedPrefixEntry.click();
    await expectActiveSessionHistoryEntry(page, "White, move 1, e4");
    await expect(storedPrefixEntry).toBeFocused();
    await expect(storedPrefixEntry).toBeVisible();
    await expect(page.getByTestId("session-origin")).toHaveText(/Current Ply 1/);
    await expect(
      page.getByRole("group", {
        name: `Chess board: game ${GAME_UUID}, ply 1, Black at the bottom`,
      }),
    ).toBeVisible();
    await page.getByRole("button", { name: "Position description" }).click();
    await expect((await sharedPositionSummary(page))).toContainText("Side to moveBlack");
    await expect(page.getByTestId("preferred-context")).toHaveText(
      "Seen in 2 games as Black",
    );
    await expectPreferredMoveState(page, "no-saved");
    await expectPositionReachFrequency(page, "available", "Black", "2 / 10 games", "20%");

    await storedPrefixEntry.press("ArrowRight");
    const storedBlackEntry = page.getByRole("button", { name: "Black, move 1, e5" });
    await expectActiveSessionHistoryEntry(page, "Black, move 1, e5");
    await expect(storedBlackEntry).toBeFocused();
    await expect(page.getByTestId("session-origin")).toHaveText(/Current Ply 2/);
    await expect(
      page.getByRole("group", {
        name: `Chess board: game ${GAME_UUID}, ply 2, Black at the bottom`,
      }),
    ).toBeVisible();
    await expect((await sharedPositionSummary(page))).toContainText("Side to moveWhite");

    await storedBlackEntry.press("Home");
    const initialEntry = page.getByRole("button", { name: "Initial position" });
    await expectActiveSessionHistoryEntry(page, "Initial position");
    await expect(initialEntry).toBeFocused();
    await expect(page.getByRole("button", { name: "Previous" })).toBeDisabled();
    await expect(page.getByTestId("session-origin")).toHaveText(/Current Ply 0/);
    await expect(
      page.getByRole("group", {
        name: `Chess board: game ${GAME_UUID}, ply 0, Black at the bottom`,
      }),
    ).toBeVisible();

    await initialEntry.press("End");
    const localEntry = page.getByRole("button", { name: "White, move 2, Nf3" });
    await expectActiveSessionHistoryEntry(page, "White, move 2, Nf3");
    await expect(localEntry).toBeFocused();
    await expect(page.getByRole("button", { name: "Next" })).toBeDisabled();
    await page.getByRole("button", { name: "Previous" }).click();
    await expectActiveSessionHistoryEntry(page, "Black, move 1, e5");
    await page.getByRole("button", { name: "Next" }).click();
    await expectActiveSessionHistoryEntry(page, "White, move 2, Nf3");
    await expectNoHorizontalOverflow(page);

    await openStory(page, STORY_IDS.navigation);
    await expectSessionHistory(page, ["Initial position", "White, move 1, e4", "Black, move 1, e6"]);
    await expectActiveSessionHistoryEntry(page, "Black, move 1, e6");
    await expect(page.getByRole("button", { name: "Next" })).toBeDisabled();

    await openStory(page, STORY_IDS.flip);
    // The story's play function already asserts the transient
    // "Flipped to Black at the bottom." state and the cleared position
    // deterministically. The E2E proof verifies the final post-play
    // state: the board remains flipped and the scenario completed.
    await expect(page.getByTestId("session-status")).toHaveText(
      "Opponent move played locally: e4.",
    );
    const summary = await sharedPositionSummary(page);
    await expect(summary).toContainText("OrientationBlack at the bottom");
    await expect(
      summary.locator('[data-position-piece="p"] [data-position-square="e4"]'),
    ).toHaveCount(1);
    await expectRailGeometry(page, {
      orientation: "black",
      state: "best-line",
      value: 51.7,
      shortValue: "+0.34",
      accessibleValue: "best-line evaluation +0.34.",
    });
    await expectNoHorizontalOverflow(page);
  });

  test("proves promotion cancellation-safe selection and keyboard-visible controls", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.promotion);
    await expectSessionHistory(page, ["Initial position"]);
    await expect(page.getByTestId("session-origin")).toHaveText(
      /Current Ply 0/,
    );
    const summary = await sharedPositionSummary(page);
    await expect(summary).toContainText("Side to moveBlack");
    await expect(
      summary.locator(
        '[data-position-side="b"] [data-position-piece="k"] [data-position-square="a8"]',
      ),
    ).toHaveCount(1);
    await expect(
      summary.locator(
        '[data-position-side="w"] [data-position-piece="n"] [data-position-square="e8"]',
      ),
    ).toHaveCount(1);
    await expect(
      summary.locator(
        '[data-position-side="w"] [data-position-piece="k"] [data-position-square="e1"]',
      ),
    ).toHaveCount(1);
    await expect(summary.locator("[data-position-square]")).toHaveCount(3);
    await expect(
      summary.locator('[data-position-fact="castling-white"]'),
    ).toContainText("Castling · White -");
    await expect(
      summary.locator('[data-position-fact="castling-black"]'),
    ).toContainText("Castling · Black -");
    await expect(
      summary.locator('[data-position-fact="en-passant"]'),
    ).toContainText("En-passant target -");
    await expect(
      summary.locator('[data-position-fact="halfmove"]'),
    ).toContainText("Halfmove clock 0");
    await expect(
      summary.locator('[data-position-fact="fullmove"]'),
    ).toContainText("Fullmove 1");
    await expect(
      page.getByRole("button", { name: "Position description" }),
    ).toBeVisible();
    await checkA11y(page);
  });

  test("proves preferred-move assignment, context safety, and replacement", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.unassigned);
    await expect(page.getByText("Seen in 3 games as White")).toBeVisible();
    await expectPreferredMoveState(page, "saved");
    await expect(page.getByTestId("saved-move")).toHaveText(
      "Saved move: e4 (e2e4)",
    );
    await expect(
      page.getByRole("button", { name: "Effective date: 2026-08-29" }),
    ).toBeVisible();
    await expectPositionReachFrequency(page, "available", "White", "3 / 10 games", "30%");
    await checkA11y(page);

    await openStory(page, STORY_IDS.zeroPersonal);
    await expect(page.getByText("Never seen as White")).toBeVisible();
    await expectPositionReachFrequency(page, "available", "White", "0 / 10 games", "0%");
    await expect(
      page.getByText(
        "This position cannot be saved because it is not in the corpus.",
      ),
    ).toHaveCount(0);

    await openStory(page, STORY_IDS.absent);
    await expectPreferredMoveState(page, "no-saved");
    await expectPositionReachFrequency(page, "absent", "White");
    await expect(
      page.getByText(
        "This position cannot be saved because it is not in the corpus.",
      ),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Add" })).toHaveCount(0);
    await checkA11y(page);

    await openStory(page, STORY_IDS.assigned);
    await expectPreferredMoveState(page, "matching-played");
    await expect(page.getByTestId("played-move")).toHaveText(
      "Played move: e4 (e2e4)",
    );
    await expect(page.getByText("This move matches your preferred move.")).toBeVisible();
    await expect(page.getByTestId("effective-date")).toHaveText("Effective from 2026-01-01");
    await expect(page.getByTestId("session-status")).toHaveText(
      "Saved move played locally: e4.",
    );
    await expectSessionHistory(page, ["Initial position", "White, move 1, e4"]);
    await expectActiveSessionHistoryEntry(page, "White, move 1, e4");
    await expect(page.getByTestId("saved-move")).toHaveCount(0);

    await openStory(page, STORY_IDS.boardPlay);
    await expectPreferredMoveState(page, "matching-played");
    await expect(page.getByTestId("session-status")).toHaveText(
      "Saved move played locally: e4.",
    );
    await expectSessionHistory(page, ["Initial position", "White, move 1, e4"]);
    await expectActiveSessionHistoryEntry(page, "White, move 1, e4");
    await expect(page.getByTestId("saved-move")).toHaveCount(0);

    await openStory(page, STORY_IDS.unsavedPlayed, 412, 915);
    await expectPreferredMoveState(page, "unsaved-played");
    await expect(page.getByTestId("played-move")).toHaveText(
      "Played move: d4 (d2d4)",
    );
    await expect(page.getByText("This move is not saved as your preferred move.")).toBeVisible();
    await expect(page.getByRole("button", { name: "Edit" })).toBeEnabled();
    await expectPositionReachFrequency(page, "available", "White", "5 / 10 games", "50%");
    await expect(page.getByTestId("session-origin")).toHaveText(/Current Ply 0/);
    await expectSessionHistory(page, ["Initial position"]);
    await expectNoHorizontalOverflow(page);

    await openStory(page, STORY_IDS.assignedToday, 1280, 900);
    await expectPreferredMoveState(page, "saved");
    await expect(page.getByTestId("effective-date")).toHaveText("Effective from Today");
    await expect(page.getByRole("button", { name: /Effective date: \d{4}-\d{2}-\d{2}/ })).toBeVisible();

    await openStory(page, STORY_IDS.replacement);
    await expect(page.getByText("Preferred move replaced.")).toBeVisible();
    await expect(page.getByTestId("saved-move")).toHaveText(
      "Saved move: d4 (d2d4)",
    );
    const replacementSummary = await sharedPositionSummary(page);
    await expect(
      replacementSummary.locator('[data-position-square="d2"]'),
    ).toHaveCount(1);
    await expect(
      replacementSummary.locator('[data-position-square="d4"]'),
    ).toHaveCount(0);
    await expectSessionHistory(page, ["Initial position"]);
    await checkA11y(page);
  });

  test("proves dated success, failed retention, confirmation, and local opponent play", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.datedAdd);
    await expect(page.getByText("Preferred move added.")).toBeVisible();
    await expect(
      page.getByRole("button", { name: /Effective date: \d{4}-\d{2}-\d{2}/ }),
    ).toBeVisible();
    await expect(page.getByTestId("effective-date")).toHaveText("Effective from Today");

    await openStory(page, STORY_IDS.mutationFailure);
    await expect(page.getByRole("alert")).toHaveText(
      "The selected date cannot be in the future.",
    );
    await expect(page.getByTestId("session-status")).toHaveText(
      "My move staged: e4.",
    );
    await expect(
      page.getByText("My move staged: e4.", { exact: true }),
    ).toHaveCount(1);
    await expect(
      page.getByRole("button", { name: /Effective date: \d{4}-\d{2}-\d{2}/ }),
    ).toBeVisible();
    const failedSummary = await sharedPositionSummary(page);
    await expect(
      failedSummary.locator('[data-position-square="e2"]'),
    ).toHaveCount(0);
    await expect(
      failedSummary.locator('[data-position-square="e4"]'),
    ).toHaveCount(1);
    await expectSessionHistory(page, ["Initial position"]);

    await openStory(page, STORY_IDS.remove);
    await expect(page.getByText("Preferred move removed.")).toBeVisible();
    await expect(page.getByTestId("saved-move")).toHaveCount(0);
    await expect(
      page.getByRole("button", { name: "Effective date: Choose date" }),
    ).toBeVisible();
    await checkA11y(page);

    await openStory(page, STORY_IDS.readErrors);
    await expect(page.getByRole("alert")).toHaveCount(2);
    await expectPreferredMoveState(page, "no-saved");
    await expectPositionReachFrequency(page, "unavailable", "White");

    await openStory(page, STORY_IDS.opponentLocal);
    await expectSessionHistory(page, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(page, "White, move 2, Nf3");
    await expect(page.getByTestId("session-status")).toHaveText(
      "Opponent move played locally: Nf3.",
    );
    await expect(page.getByTestId("saved-move")).toHaveCount(0);
    await expectPreferredMoveState(page, "no-saved");
    await expectPositionReachFrequency(page, "available", "Black", "2 / 10 games", "20%");
    await expect(page.getByRole("alert")).toHaveCount(0);
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });

  test("proves constrained keyboard focus and visible synchronized controls", async ({ page }) => {
    await openStory(page, STORY_IDS.keyboard, 412, 915);
    await expectPreferredMoveState(page, "unsaved-played");
    const candidate = page.getByRole("button", { name: "1. e4" });
    await expect(candidate).toBeVisible();
    await candidate.focus();
    await candidate.press("Enter");
    await expect(candidate).toBeFocused();
    await expectPreferredMoveState(page, "unsaved-played");
    await expect(page.getByTestId("played-move")).toHaveText("Played move: e4 (e2e4)");
    await expect(page.getByTestId("session-origin")).toHaveText(/Current Ply 0/);
    await expectSessionHistory(page, ["Initial position"]);
    await expectActiveSessionHistoryEntry(page, "Initial position");
    await expect(page.getByRole("button", { name: "Position description" })).toBeVisible();
    await expectPositionReachFrequency(page, "available", "White", "3 / 10 games", "30%");
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });
});
