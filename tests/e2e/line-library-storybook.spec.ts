import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { retryAxeWhenBusy } from "./axeBusyRetry";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const STORYBOOK_ROOT = "#storybook-root";
const SYNTHETIC_NOTICE =
  "Synthetic in-memory fixture only — IDs and values are not authoritative production data.";
const STORY_IDS = {
  browserSelectionAndCommit:
    "application-openings-opening-line-library--browser-selection-and-commit",
  textSearch: "application-openings-opening-line-library--text-search-scenario",
  ecoRange: "application-openings-opening-line-library--eco-range-scenario",
  acceptedCorpus:
    "application-openings-opening-line-library--accepted-corpus-scenario",
  disabledAndReference:
    "application-openings-opening-line-library--disabled-and-transposition-reference",
  selectionLimit:
    "application-openings-opening-line-library--declared-synthetic-selection-limit",
  initialLoading:
    "application-openings-opening-line-library--initial-loading",
  staleRefresh: "application-openings-opening-line-library--stale-refresh",
  failureAndRetry:
    "application-openings-opening-line-library--failure-and-retry",
  emptyResult: "application-openings-opening-line-library--empty-result",
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
}

async function expectNoHorizontalOverflow(page: Page) {
  const dimensions = await page.evaluate(() => ({
    documentClientWidth: document.documentElement.clientWidth,
    documentScrollWidth: document.documentElement.scrollWidth,
    bodyClientWidth: document.body.clientWidth,
    bodyScrollWidth: document.body.scrollWidth,
    root: (() => {
      const element = document.querySelector("#storybook-root");
      return element
        ? { clientWidth: element.clientWidth, scrollWidth: element.scrollWidth }
        : null;
    })(),
  }));

  expect(dimensions.documentScrollWidth).toBeLessThanOrEqual(
    dimensions.documentClientWidth,
  );
  expect(dimensions.bodyScrollWidth).toBeLessThanOrEqual(
    dimensions.bodyClientWidth,
  );
  expect(dimensions.root).not.toBeNull();
  expect(dimensions.root?.scrollWidth).toBe(dimensions.root?.clientWidth);
}

async function checkA11y(page: Page) {
  const results = await retryAxeWhenBusy(page, () =>
    new AxeBuilder({ page })
      .include(STORYBOOK_ROOT)
      .disableRules(["landmark-one-main", "page-has-heading-one", "region"])
      .analyze(),
  );
  expect(results.violations).toEqual([]);
}

async function expectOpeningSurface(page: Page) {
  await expect(
    page.getByRole("heading", { level: 2, name: "Synthetic opening picker" }),
  ).toBeVisible();
  await expect(page.getByText(SYNTHETIC_NOTICE)).toBeVisible();
  await expect(page.getByRole("tree")).toBeVisible();
}

test.describe("Opening Line Library Storybook surface", () => {
  test.describe.configure({ timeout: 60_000 });

  test("proves the synthetic opening specialization, keyboard focus, selection, and commit", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.browserSelectionAndCommit);
    await expectOpeningSurface(page);

    const sicilian = page.getByRole("treeitem", {
      name: /Synthetic Sicilian branch/,
    });
    const sicilianCheckbox = page.getByRole("checkbox", {
      name: /Select Synthetic Sicilian branch/,
    });
    await expect(sicilian).toBeVisible();
    await expect(sicilianCheckbox).toBeChecked();

    await sicilianCheckbox.click();
    await expect(sicilianCheckbox).not.toBeChecked();
    await sicilian.focus();
    await expect(sicilian).toBeFocused();
    await sicilian.press("Enter");
    await expect(sicilianCheckbox).toBeChecked();
    await expect(
      page.getByRole("button", { name: "Apply selection" }),
    ).toBeVisible();
    await checkA11y(page);
  });

  test("proves the approved synthetic filter scenarios", async ({ page }) => {
    await openStory(page, STORY_IDS.textSearch);
    await expectOpeningSurface(page);
    await expect(page.getByRole("searchbox", { name: "Search" })).toHaveValue(
      "Caro",
    );
    await expect(
      page.getByRole("treeitem", { name: /Synthetic Caro-Kann branch/ }),
    ).toBeVisible();
    await expect(
      page.getByRole("treeitem", { name: /Synthetic English branch/ }),
    ).toHaveCount(0);
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);

    await openStory(page, STORY_IDS.ecoRange);
    await expectOpeningSurface(page);
    await expect(page.getByRole("textbox", { name: "ECO code/range" })).toHaveValue(
      "B00:B99",
    );
    await expect(
      page.getByRole("treeitem", { name: /Synthetic Sicilian branch/ }),
    ).toBeVisible();
    await expect(
      page.getByRole("treeitem", { name: /Synthetic English branch/ }),
    ).toHaveCount(0);
    await expectNoHorizontalOverflow(page);

    await openStory(page, STORY_IDS.acceptedCorpus);
    await expectOpeningSurface(page);
    await expect(
      page.getByRole("checkbox", { name: "Appears in my games" }),
    ).toBeChecked();
    await expect(
      page.getByRole("treeitem", { name: /Synthetic Sicilian branch/ }),
    ).toBeVisible();
    await expect(
      page.getByRole("treeitem", { name: /Synthetic English branch/ }),
    ).toHaveCount(0);
    await expectNoHorizontalOverflow(page);
  });

  test("proves disabled rows, references, and the declared selection limit", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.disabledAndReference);
    await expectOpeningSurface(page);
    await expect(
      page.getByRole("treeitem", { name: /Synthetic unavailable branch/ }),
    ).toHaveAttribute("aria-disabled", "true");
    await expect(
      page.getByRole("checkbox", { name: /Select Synthetic transposition reference/ }),
    ).toHaveCount(0);
    await expect(
      page.getByRole("button", { name: "Target: synthetic-line-sicilian" }),
    ).toBeVisible();
    await checkA11y(page);

    await openStory(page, STORY_IDS.selectionLimit);
    await expectOpeningSurface(page);
    await expect(
      page.getByRole("checkbox", { name: /Select Synthetic central family/ }),
    ).not.toBeChecked();
    await expect(
      page.getByRole("checkbox", { name: /Select Synthetic Sicilian branch/ }),
    ).not.toBeChecked();
    await expectNoHorizontalOverflow(page);
  });

  test("proves loading, stale, error-retry, and empty states", async ({ page }) => {
    await openStory(page, STORY_IDS.initialLoading);
    await expect(page.getByRole("status")).toContainText("Loading lines");
    await checkA11y(page);

    await openStory(page, STORY_IDS.staleRefresh);
    await expectOpeningSurface(page);
    await expect(page.getByRole("status")).toContainText("Updating results");
    await expect(
      page.getByRole("treeitem", { name: /Synthetic Sicilian branch/ }),
    ).toHaveAttribute("aria-disabled", "true");
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);

    await openStory(page, STORY_IDS.failureAndRetry);
    await expectOpeningSurface(page);
    await expect(
      page.getByRole("treeitem", { name: /Synthetic Sicilian branch/ }),
    ).toBeVisible();
    await expect(page.getByRole("alert")).toHaveCount(0);
    await checkA11y(page);

    await openStory(page, STORY_IDS.emptyResult);
    await expect(page.getByRole("status")).toContainText("No lines match");
    await expect(page.getByRole("tree")).toHaveCount(0);
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });

  test("keeps the opening picker accessible and bounded at responsive viewports", async ({
    page,
  }) => {
    for (const viewport of [
      { width: 1280, height: 900 },
      { width: 640, height: 900 },
      { width: 412, height: 915 },
    ]) {
      await openStory(
        page,
        STORY_IDS.browserSelectionAndCommit,
        viewport.width,
        viewport.height,
      );
      await expectOpeningSurface(page);
      await expectNoHorizontalOverflow(page);
      await checkA11y(page);
    }
  });
});
