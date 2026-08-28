import { expect, test, type Locator, type Page } from "@playwright/test";
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
const CANONICAL_STORY_COUNT = 7;

const RICH_SPOKEN_DESCRIPTION = [
  "Orientation: White at the bottom. Side to move: Black.",
  "Occupied squares in stable FEN order: black rook at a8, black knight at b8, black queen at d8, black king at e8, black rook at h8, black bishop at b7, black pawn at c7, black bishop at e7, black pawn at f7, black pawn at g7, black pawn at a6, black pawn at b6, black pawn at d6, black pawn at e6, black knight at f6, black pawn at h6, white pawn at e4, white bishop at f4, white knight at c3, white pawn at d3, white knight at f3, white pawn at g3, white pawn at a2, white pawn at b2, white pawn at c2, white queen at d2, white pawn at f2, white bishop at g2, white pawn at h2, white rook at a1, white king at e1, white rook at h1.",
  "Castling rights: White may castle kingside and queenside; Black may castle kingside and queenside.",
  "En-passant target: e3. Halfmove clock: 0. Fullmove number: 8.",
].join(" ");

async function openStory(page: Page, storyId: string) {
  await page.goto(`${STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
  await expect(
    page.locator('[class*="adapter"], [class*="unavailable"]').first(),
  ).toBeVisible();
  // Allow Storybook's own a11y addon to finish its axe pass before we run ours.
  await page.waitForTimeout(500);
}

async function expectDescriptionAssociation(page: Page, graphic: Locator) {
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

async function expectValidSurface(page: Page, graphic: Locator) {
  const description = await expectDescriptionAssociation(page, graphic);

  await expect(page.locator('[role="status"]')).toHaveCount(1);
  await expect(
    page.locator('[role="status"][aria-live="polite"][aria-atomic="true"]'),
  ).toHaveCount(1);
  await expect(page.locator("[aria-live]")).toHaveCount(1);

  return {
    description,
    descriptionId: await graphic.getAttribute("aria-describedby"),
  };
}

async function expectHiddenVisualDescription(page: Page) {
  const summary = page.locator("[data-position-summary]");
  await expect(summary).toHaveCount(1);
  await expect(summary).toBeVisible();
  const visualDescription = summary.locator("..");
  await expect(visualDescription).toHaveAttribute("aria-hidden", "true");
  await expect(visualDescription).toHaveAttribute("inert", "");
  await expect(visualDescription).toHaveJSProperty("inert", true);
  await expect(
    visualDescription.locator(
      'button, a, input, select, textarea, [contenteditable="true"], [tabindex], [role], [aria-live]',
    ),
  ).toHaveCount(0);

  return {
    summary,
    visualDescription,
  };
}

async function expectRichGroupedSummary(page: Page) {
  const summary = page.locator("[data-position-summary]");
  await expect(summary).toBeVisible();
  await expect(summary.locator("[data-position-metadata]")).toHaveCount(1);
  await expect(
    summary.locator('[data-position-metadata-item="orientation"]'),
  ).toContainText("OrientationWhite at the bottom");
  await expect(
    summary.locator('[data-position-metadata-item="side-to-move"]'),
  ).toContainText("Side to moveBlack");

  const inventories = summary.locator("[data-position-side]");
  await expect(inventories).toHaveCount(2);
  await expect(summary.locator('[data-position-side="w"]')).toHaveAttribute(
    "data-position-side-to-move",
    "false",
  );
  await expect(summary.locator('[data-position-side="b"]')).toHaveAttribute(
    "data-position-side-to-move",
    "true",
  );
  await expect(summary.locator('[data-position-side="w"]')).toContainText(
    "WhiteKinge1Queend2Rooksa1h1Bishopsf4g2Knightsc3f3Pawnse4d3g3a2b2c2f2h2",
  );
  await expect(summary.locator('[data-position-side="b"]')).toContainText(
    "BlackKinge8Queend8Rooksa8h8Bishopsb7e7Knightsb8f6Pawnsc7f7g7a6b6d6e6h6",
  );
  await expect(summary.locator("[data-position-piece]")).toHaveCount(12);
  await expect(summary.locator("[data-position-square]")).toHaveCount(32);

  const facts = summary.locator("[data-position-fact]");
  await expect(facts).toHaveCount(5);
  await expect(
    summary.locator('[data-position-fact="castling-white"]'),
  ).toContainText("K + Q");
  await expect(
    summary.locator('[data-position-fact="castling-black"]'),
  ).toContainText("K + Q");
  await expect(
    summary.locator('[data-position-fact="en-passant"]'),
  ).toContainText("e3");
  await expect(
    summary.locator('[data-position-fact="halfmove"]'),
  ).toContainText("0");
  await expect(
    summary.locator('[data-position-fact="fullmove"]'),
  ).toContainText("8");
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
    await page.emulateMedia({
      forcedColors: "active",
      reducedMotion: "reduce",
    });

    expect(Object.values(STORY_IDS)).toHaveLength(CANONICAL_STORY_COUNT);
    expect(new Set(Object.values(STORY_IDS)).size).toBe(CANONICAL_STORY_COUNT);

    await openStory(page, STORY_IDS.starting);
    const startingGraphic = await expectStaticGraphic(
      page,
      "Starting position",
    );
    const startingSurface = await expectValidSurface(page, startingGraphic);
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
    const startingDescription = startingSurface.description;
    const startingDescriptionId = startingSurface.descriptionId;
    if (!startingDescriptionId) {
      throw new Error("The starting static board lost its description id.");
    }
    await expect(startingDescription).toContainText(
      "Orientation: White at the bottom. Side to move: White.",
    );
    await checkA11y(page);

    const summary = page.getByRole("button", { name: "Position description" });
    const details = summary.locator("..");
    await expect(details).not.toHaveAttribute("data-open");
    await expect(summary).toHaveAttribute("aria-expanded", "false");
    await summary.focus();
    await expect(summary).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(details).toHaveAttribute("data-open");
    await expect(summary).toBeFocused();
    await expectHiddenVisualDescription(page);
    await expect(startingGraphic).toHaveAttribute(
      "aria-describedby",
      startingDescriptionId,
    );
    await page.keyboard.press("Space");
    await expect(details).not.toHaveAttribute("data-open");
    await expect(summary).toBeFocused();

    await openStory(page, STORY_IDS.rich);
    const richGraphic = await expectStaticGraphic(
      page,
      "Rich position with complete game state",
    );
    const richSurface = await expectValidSurface(page, richGraphic);
    await expect(richSurface.description).toHaveText(RICH_SPOKEN_DESCRIPTION);
    const richTrigger = page.getByRole("button", {
      name: "Position description",
    });
    await richTrigger.focus();
    await page.keyboard.press("Enter");
    await expect(richTrigger).toHaveAttribute("aria-expanded", "true");
    await expectHiddenVisualDescription(page);
    await expectRichGroupedSummary(page);
    await checkA11y(page);

    await openStory(page, STORY_IDS.black);
    const blackGraphic = await expectStaticGraphic(
      page,
      "Starting position from Black's side",
    );
    const blackSurface = await expectValidSurface(page, blackGraphic);
    await expect(blackSurface.description).toContainText(
      "Orientation: Black at the bottom.",
    );
    const blackTrigger = page.getByRole("button", {
      name: "Position description",
    });
    await blackTrigger.focus();
    await page.keyboard.press("Enter");
    await expectHiddenVisualDescription(page);
    await expect(
      page.locator('[data-position-metadata-item="orientation"]'),
    ).toContainText("Black at the bottom");
    await checkA11y(page);
  });

  test("exercises hidden, constrained, and invalid stories, sizing, axe, and forced colors", async ({
    page,
  }) => {
    await page.emulateMedia({
      forcedColors: "active",
      reducedMotion: "reduce",
    });

    await openStory(page, STORY_IDS.hidden);
    const hiddenGraphic = await expectStaticGraphic(
      page,
      "Starting position without coordinates",
    );
    await expectValidSurface(page, hiddenGraphic);
    await expect(page.locator("[data-square] span")).toHaveCount(0);
    await checkA11y(page);

    await openStory(page, STORY_IDS.constrained);
    const constrainedGraphic = await expectStaticGraphic(
      page,
      "Starting position in a constrained container",
    );
    await expectValidSurface(page, constrainedGraphic);
    const constrainedContainer = page.locator('[class*="constrainedStory"]');
    await expect(constrainedContainer).toHaveCount(1);
    const constrainedTrigger = page.getByRole("button", {
      name: "Position description",
    });
    await constrainedTrigger.focus();
    await page.keyboard.press("Enter");
    await expectHiddenVisualDescription(page);
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
      const metrics = await page.evaluate(() => {
        const root = document.documentElement;
        const body = document.body;
        const container = document.querySelector('[class*="constrainedStory"]');
        const summary = document.querySelector("[data-position-summary]");
        if (
          !(container instanceof HTMLElement) ||
          !(summary instanceof HTMLElement)
        ) {
          throw new Error("The constrained Board Adapter surface is missing.");
        }
        return {
          containerClientWidth: container.clientWidth,
          containerScrollWidth: container.scrollWidth,
          summaryClientWidth: summary.clientWidth,
          summaryScrollWidth: summary.scrollWidth,
          documentClientWidth: root.clientWidth,
          documentScrollWidth: root.scrollWidth,
          bodyClientWidth: body.clientWidth,
          bodyScrollWidth: body.scrollWidth,
        };
      });
      expect(metrics.containerClientWidth).toBe(size);
      expect(metrics.containerScrollWidth).toBeLessThanOrEqual(
        metrics.containerClientWidth,
      );
      expect(metrics.summaryScrollWidth).toBeLessThanOrEqual(
        metrics.summaryClientWidth,
      );
      expect(metrics.documentScrollWidth).toBeLessThanOrEqual(
        metrics.documentClientWidth,
      );
      expect(metrics.bodyScrollWidth).toBeLessThanOrEqual(
        metrics.bodyClientWidth,
      );
    }
    await checkA11y(page);

    await openStory(page, STORY_IDS.invalid);
    await expect(page.getByText("Position unavailable")).toBeVisible();
    await expect(page.getByRole("img")).toHaveCount(0);
    await expect(page.getByRole("status")).toHaveCount(1);
    await expect(
      page.getByRole("button", { name: "Position description" }),
    ).toHaveCount(0);
    await checkA11y(page);
  });

  test("exercises the expanded position description story, axe, forced colors, and reduced motion", async ({
    page,
  }) => {
    await page.emulateMedia({
      forcedColors: "active",
      reducedMotion: "reduce",
    });

    await openStory(page, STORY_IDS.expanded);
    const expandedGraphic = await expectStaticGraphic(
      page,
      "Rich position with expanded description",
    );
    const expandedSurface = await expectValidSurface(page, expandedGraphic);
    const expandedVisual = await expectHiddenVisualDescription(page);
    await expect(expandedSurface.description).toHaveText(
      RICH_SPOKEN_DESCRIPTION,
    );
    const expandedDetails = page
      .getByRole("button", {
        name: "Position description",
      })
      .locator("..");
    await expect(expandedDetails).toHaveAttribute("data-open");
    await expectRichGroupedSummary(page);
    const growthMetrics = await expandedVisual.summary.evaluate((summary) => {
      const disclosure = summary.parentElement;
      if (!disclosure) {
        throw new Error(
          "The expanded visual description has no disclosure body.",
        );
      }
      return [summary, disclosure].map((element) => {
        const style = getComputedStyle(element);
        return {
          clientHeight: element.clientHeight,
          scrollHeight: element.scrollHeight,
          overflowY: style.overflowY,
          maxHeight: style.maxHeight,
        };
      });
    });
    for (const metrics of growthMetrics) {
      expect(metrics.scrollHeight).toBe(metrics.clientHeight);
      expect(metrics.overflowY).not.toMatch(/auto|scroll/);
      expect(metrics.maxHeight).toBe("none");
    }
    expect(
      await page.evaluate(
        () => window.matchMedia("(forced-colors: active)").matches,
      ),
    ).toBe(true);
    expect(
      await page.evaluate(
        () => window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      ),
    ).toBe(true);
    await expect(expandedVisual.summary).toHaveCSS("animation-duration", "0s");
    await expect(expandedVisual.summary).toHaveCSS("transition-duration", "0s");
    await expect(expandedGraphic).toHaveAttribute(
      "aria-describedby",
      expandedSurface.descriptionId ?? "",
    );
    await checkA11y(page);
  });
});
