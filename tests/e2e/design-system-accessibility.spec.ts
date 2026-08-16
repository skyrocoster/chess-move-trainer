import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

// The shared Playwright config uses baseURL http://localhost:8444 for the
// production / browser proof. This verification-only spec targets the
// Storybook dev server (port 6006) instead, mirroring the foundation
// accessibility spec precedent.
test.use({ baseURL: "http://localhost:6006" });

// Story id for the Acceptance/ResponsiveAccessibilityReview fixture:
// sanitize(title) + "--" + sanitize(startCase(exportName)).
const STORY_ID = "acceptance-responsiveaccessibilityreview--responsive-accessibility-review";
const STORY_URL = `/iframe.html?id=${STORY_ID}&viewMode=story`;
const LONG_MESSAGE = /deliberately long message/;

async function assertFixtureStates(
  page: Page,
  viewport: { width: number; height: number },
): Promise<void> {
  await page.setViewportSize(viewport);
  await page.goto(STORY_URL);

  // Fully rendered review fixture: all presentation levels inside the
  // constrained review container plus the focus specimens.
  await expect(
    page.getByRole("heading", { name: "Responsive and accessibility review" }),
  ).toBeVisible();
  await expect(page.getByTestId("core-information")).toBeVisible();
  await expect(page.getByTestId("core-warning")).toBeVisible();
  await expect(page.getByTestId("core-error")).toBeVisible();
  await expect(page.getByRole("button", { name: "Focus specimen one" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Focus specimen two" })).toBeVisible();

  // Long-message wrapping: the panel message must stay inside the
  // constrained review container without horizontal overflow, and the
  // document must not overflow horizontally at either review size.
  const message = page.getByText(LONG_MESSAGE);
  await expect(message).toBeVisible();
  const messageOverflows = await message.evaluate((el) => el.scrollWidth > el.clientWidth);
  expect(messageOverflows).toBe(false);
  const documentOverflows = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  );
  expect(documentOverflows).toBe(false);

  // Focus treatment: the centralized 2px primary focus ring with 2px
  // surface separation is applied to the focused specimen.
  const focusSpecimen = page.getByRole("button", { name: "Focus specimen one" });
  await focusSpecimen.focus();
  await expect(focusSpecimen).toBeFocused();
  const outline = await focusSpecimen.evaluate((el) => {
    const style = getComputedStyle(el);
    return {
      style: style.outlineStyle,
      width: style.outlineWidth,
      offset: style.outlineOffset,
    };
  });
  expect(outline.style).toBe("solid");
  expect(outline.width).toBe("2px");
  expect(outline.offset).toBe("2px");

  // Automated axe is supplemental, not the human WCAG decision: the
  // coordinator performs the human responsive/accessibility gate. This run
  // covers the contrast-relevant rendered states of every presentation
  // level at the current viewport.
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
}

test("review fixture passes axe, wrapping, and focus at 1920x1080", async ({ page }) => {
  await assertFixtureStates(page, { width: 1920, height: 1080 });
});

test("review fixture passes axe, wrapping, and focus at 412x915 portrait", async ({ page }) => {
  await assertFixtureStates(page, { width: 412, height: 915 });
});
