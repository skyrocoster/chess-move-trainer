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

async function expectDescriptionAssociation(
  page: Page,
  graphic: ReturnType<Page["getByRole"]>,
) {
  const descriptionId = await graphic.getAttribute("aria-describedby");

  expect(descriptionId).toMatch(/^board-position-description-/);
  if (!descriptionId) {
    throw new Error("The static board has no generated description id.");
  }

  const description = page.locator(`[id="${descriptionId}"]`);
  await expect(description).toHaveCount(1);
  await expect(
    page.locator(`[aria-describedby="${descriptionId}"]`),
  ).toHaveCount(1);
  return description;
}

async function expectStaticGraphic(page: Page, label: string) {
  const graphic = page.getByRole("img", { name: label });

  await expect(graphic).toBeVisible();
  await expect(graphic).toHaveAttribute("aria-label", label);
  await expectDescriptionAssociation(page, graphic);
  await expect(graphic).not.toHaveAttribute("tabindex");
  await expect(
    graphic.locator("[role], [tabindex], [aria-roledescription], [aria-live]"),
  ).toHaveCount(0);

  const packageBoard = graphic.locator('[aria-hidden="true"][inert]');
  await expect(packageBoard).toHaveCount(1);
  await expect(packageBoard).toHaveCSS("pointer-events", "none");
  await expect(page.locator('[aria-roledescription="draggable"]')).toHaveCount(
    0,
  );

  return graphic;
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
  test("exercises starting, rich, and black stories, static behavior, axe, and forced colors", async ({
    page,
  }) => {
    await page.emulateMedia({ forcedColors: "active" });

    await openStory(page, STORY_IDS.starting);
    const startingGraphic = await expectStaticGraphic(
      page,
      "Starting position",
    );
    await expect(page.locator("[data-square] span")).not.toHaveCount(0);
    await expect(startingGraphic).toHaveCSS(
      "background-color",
      "rgb(255, 255, 255)",
    );
    await expect(startingGraphic).toHaveCSS("border-top-color", "rgb(0, 0, 0)");
    expect(
      await page.evaluate(
        () => window.matchMedia("(forced-colors: active)").matches,
      ),
    ).toBe(true);
    const startingDescription = await expectDescriptionAssociation(
      page,
      startingGraphic,
    );
    const startingDescriptionId =
      await startingGraphic.getAttribute("aria-describedby");
    if (!startingDescriptionId) {
      throw new Error("The starting static board lost its description id.");
    }
    await expect(startingDescription).toContainText(
      "Orientation: White at the bottom. Side to move: White.",
    );
    await checkA11y(page);

    const summary = page.getByText("Position description");
    const details = summary.locator("..");
    await expect(details).not.toHaveAttribute("data-open");
    await summary.focus();
    await expect(summary).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(details).toHaveAttribute("data-open");
    await expect(startingGraphic).toHaveAttribute(
      "aria-describedby",
      startingDescriptionId,
    );
    await page.keyboard.press("Enter");
    await expect(details).not.toHaveAttribute("data-open");

    await openStory(page, STORY_IDS.rich);
    const richGraphic = await expectStaticGraphic(
      page,
      "Rich position with complete game state",
    );
    const richDescription = await expectDescriptionAssociation(
      page,
      richGraphic,
    );
    await expect(richDescription).toContainText("Side to move: Black");
    await expect(richDescription).toContainText("En-passant target: e3.");
    await expect(richDescription).toContainText("Fullmove number: 8.");
    await checkA11y(page);

    await openStory(page, STORY_IDS.black);
    const blackGraphic = await expectStaticGraphic(
      page,
      "Starting position from Black's side",
    );
    const blackDescription = await expectDescriptionAssociation(
      page,
      blackGraphic,
    );
    await expect(blackDescription).toContainText(
      "Orientation: Black at the bottom.",
    );
    await checkA11y(page);
  });

  test("exercises hidden, constrained, and invalid stories, sizing, axe, and forced colors", async ({
    page,
  }) => {
    await page.emulateMedia({ forcedColors: "active" });

    await openStory(page, STORY_IDS.hidden);
    await expectStaticGraphic(page, "Starting position without coordinates");
    await expect(page.locator("[data-square] span")).toHaveCount(0);
    await checkA11y(page);

    await openStory(page, STORY_IDS.constrained);
    await expectStaticGraphic(
      page,
      "Starting position in a constrained container",
    );
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
    await expect(page.getByRole("status")).toBeVisible();
    await checkA11y(page);
  });

  test("exercises the expanded position description story, axe, and forced colors", async ({
    page,
  }) => {
    await page.emulateMedia({ forcedColors: "active" });

    await openStory(page, STORY_IDS.expanded);
    const expandedGraphic = await expectStaticGraphic(
      page,
      "Rich position with expanded description",
    );
    const expandedDetails = page
      .getByRole("button", {
        name: "Position description",
      })
      .locator("..");
    await expect(expandedDetails).toHaveAttribute("data-open");
    await expect(page.getByLabel("Position description")).toContainText(
      "Side to move: Black.",
    );
    await expectDescriptionAssociation(page, expandedGraphic);
    await checkA11y(page);
  });
});
