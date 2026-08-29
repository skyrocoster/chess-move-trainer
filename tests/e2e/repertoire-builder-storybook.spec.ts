import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const STORYBOOK_ROOT = "#storybook-root";
const GAME_UUID = "0007925c-5a8d-11f0-9740-f690a301000f";
const STORY_IDS = {
  wide: "application-repertoire-builder-workspace--wide",
  constrained: "application-repertoire-builder-workspace--constrained",
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
    await expect(page.getByTestId("session-san-history")).toHaveText(
      "1. e4 1... e5",
    );
    const summary = await sharedPositionSummary(page);
    await expect(summary).toContainText("OrientationBlack at the bottom");
    await expect(summary).toContainText("Side to moveWhite");
    await checkA11y(page);

    await openStory(page, STORY_IDS.opponent);
    await expect(page.getByTestId("session-san-history")).toHaveText(
      "1. e4 1... e5 2. Nf3",
    );
    await expect(page.getByTestId("session-status")).toHaveText(
      "Opponent move played locally: Nf3.",
    );
    await expect(page.getByTestId("staged-move")).toHaveCount(0);
  });

  test("proves navigation, replacement truncation, and Flip cancellation", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.navigation);
    await expect(page.getByTestId("session-san-history")).toHaveText(
      "1. e4 1... e6",
    );
    await expect(page.getByRole("button", { name: "Next" })).toBeDisabled();

    await openStory(page, STORY_IDS.flip);
    await expect(page.getByTestId("staged-move")).toHaveCount(0);
    const summary = await sharedPositionSummary(page);
    await expect(
      summary.locator('[data-position-piece="p"] [data-position-square="e4"]'),
    ).toHaveCount(1);
    await expectNoHorizontalOverflow(page);
  });

  test("proves promotion cancellation-safe selection and keyboard-visible controls", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.promotion);
    await expect(page.getByTestId("session-san-history")).toHaveText("1. e8=N");
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
    await expect(page.getByTestId("saved-move")).toHaveText(
      "Saved move: e4 (e2e4)",
    );
    await expect(
      page.getByRole("button", { name: "Effective date: Choose date" }),
    ).toBeVisible();
    await checkA11y(page);

    await openStory(page, STORY_IDS.zeroPersonal);
    await expect(page.getByText("Never seen as White")).toBeVisible();
    await expect(
      page.getByText(
        "This position cannot be saved because it is not in the corpus.",
      ),
    ).toHaveCount(0);

    await openStory(page, STORY_IDS.absent);
    await expect(
      page.getByText(
        "This position cannot be saved because it is not in the corpus.",
      ),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Add" })).toHaveCount(0);
    await checkA11y(page);

    await openStory(page, STORY_IDS.assigned);
    await expect(page.getByTestId("session-status")).toHaveText(
      "Saved move played locally: e4.",
    );
    await expect(page.getByTestId("session-san-history")).toHaveText("1. e4");
    await expect(page.getByTestId("saved-move")).toHaveCount(0);

    await openStory(page, STORY_IDS.replacement);
    await expect(page.getByText("Preferred move replaced.")).toBeVisible();
    await expect(page.getByTestId("saved-move")).toHaveText(
      "Saved move: d4 (d2d4)",
    );
    await checkA11y(page);
  });

  test("proves dated success, failed retention, confirmation, and local opponent play", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.datedAdd);
    await expect(page.getByText("Preferred move added.")).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Effective date: Choose date" }),
    ).toBeVisible();

    await openStory(page, STORY_IDS.mutationFailure);
    await expect(page.getByRole("alert")).toHaveText(
      "The selected date cannot be in the future.",
    );
    await expect(page.getByTestId("staged-move")).toContainText("e4");
    await expect(
      page.getByRole("button", { name: /Effective date: \d{4}-\d{2}-\d{2}/ }),
    ).toBeVisible();

    await openStory(page, STORY_IDS.remove);
    await expect(page.getByText("Preferred move removed.")).toBeVisible();
    await expect(page.getByTestId("saved-move")).toHaveCount(0);
    await expect(
      page.getByRole("button", { name: "Effective date: Choose date" }),
    ).toBeVisible();
    await checkA11y(page);

    await openStory(page, STORY_IDS.readErrors);
    await expect(page.getByRole("alert")).toHaveCount(2);

    await openStory(page, STORY_IDS.opponentLocal);
    await expect(page.getByTestId("session-san-history")).toHaveText(
      "1. e4 1... e5 2. Nf3",
    );
    await expect(page.getByTestId("session-status")).toHaveText(
      "Opponent move played locally: Nf3.",
    );
    await expect(page.getByTestId("saved-move")).toHaveCount(0);
    await expect(page.getByRole("alert")).toHaveCount(0);
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });
});
