import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const STORY_IDS = {
  starting:
    "application-board-read-only-board--default-valid-starting-position",
  rich: "application-board-read-only-board--rich-position",
  black: "application-board-read-only-board--black-orientation",
  hidden: "application-board-read-only-board--hidden-coordinates",
  constrained: "application-board-read-only-board--constrained-width",
  invalid: "application-board-read-only-board--invalid-fen",
  expanded: "application-board-read-only-board--expanded-position-description",
} as const;

async function openStory(page: Page, storyId: string) {
  await page.goto(`${STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
  await expect(
    page.locator('[class*="adapter"], [class*="unavailable"]').first(),
  ).toBeVisible();
  // Allow Storybook's own a11y addon to finish its axe pass before we run ours.
  await page.waitForTimeout(500);
}

async function checkA11y(page: Page) {
  const results = await new AxeBuilder({ page })
    .disableRules([
      // Storybook iframe pages have no application-level landmarks/headings;
      // these rules are page-structure concerns, not component-owned failures.
      "landmark-one-main",
      "page-has-heading-one",
      "region",
    ])
    .analyze();
  expect(results.violations).toEqual([]);
}

test.describe("Board Adapter Storybook surface", () => {
  test("exercises all seven stories, static behavior, sizing, axe, and forced colors", async ({
    page,
  }) => {
    await page.emulateMedia({ forcedColors: "active" });

    await openStory(page, STORY_IDS.starting);
    await expect(
      page.getByRole("img", { name: "Starting position" }),
    ).toBeVisible();
    await expect(
      page.locator('[role="img"] [role], [role="img"] [tabindex]'),
    ).toHaveCount(0);
    await expect(
      page.locator('[aria-roledescription="draggable"]'),
    ).toHaveCount(0);
    await checkA11y(page);

    const summary = page.getByText("Position description");
    const details = summary.locator("..");
    await expect(details).not.toHaveAttribute("data-open");
    await summary.focus();
    await page.keyboard.press("Enter");
    await expect(details).toHaveAttribute("data-open");
    await expect(
      page.getByRole("img", { name: "Starting position" }),
    ).toHaveAttribute("aria-describedby", /.+/);
    await page.keyboard.press("Enter");
    await expect(details).not.toHaveAttribute("data-open");

    await openStory(page, STORY_IDS.rich);
    const richGraphic = page.getByRole("img", {
      name: "Rich position with complete game state",
    });
    const richDescription = page.locator(
      `#${await richGraphic.getAttribute("aria-describedby")}`,
    );
    await expect(richDescription).toContainText("Side to move: Black");
    await expect(richDescription).toContainText("En-passant target: e3.");
    await expect(richDescription).toContainText("Fullmove number: 8.");
    await checkA11y(page);

    await openStory(page, STORY_IDS.black);
    await expect(
      page.getByRole("img", { name: "Starting position from Black's side" }),
    ).toBeVisible();
    const blackGraphic = page.locator('[role="img"]');
    const blackDescription = page.locator(
      `#${await blackGraphic.getAttribute("aria-describedby")}`,
    );
    await expect(blackDescription).toContainText(
      "Orientation: Black at the bottom.",
    );
    await checkA11y(page);

    await openStory(page, STORY_IDS.hidden);
    await expect(page.locator("[data-square] span")).toHaveCount(0);
    await checkA11y(page);

    await openStory(page, STORY_IDS.constrained);
    const constrainedContainer = page.locator('[class*="constrainedStory"]');
    await expect(constrainedContainer).toHaveCount(1);
    for (const size of [320, 480, 640]) {
      await constrainedContainer.evaluate((element, width) => {
        (element as HTMLElement).style.inlineSize = `${width}px`;
      }, size);
      const boardBox = await page.getByRole("img").boundingBox();
      expect(boardBox).not.toBeNull();
      expect(
        Math.abs((boardBox?.width ?? 0) - (boardBox?.height ?? 0)),
      ).toBeLessThanOrEqual(1);
      expect(boardBox?.width ?? 0).toBeLessThanOrEqual(size);
      await expect(constrainedContainer).toHaveJSProperty("scrollWidth", size);
    }
    await checkA11y(page);

    await openStory(page, STORY_IDS.invalid);
    await expect(page.getByText("Position unavailable")).toBeVisible();
    await expect(page.getByRole("img")).toHaveCount(0);
    await checkA11y(page);

    await openStory(page, STORY_IDS.expanded);
    await expect(
      page.getByText("Position description").locator(".."),
    ).toHaveAttribute("data-open");
    await expect(page.getByRole("img")).toHaveAttribute(
      "aria-describedby",
      /.+/,
    );
    await checkA11y(page);
  });
});
