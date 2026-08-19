import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";
const STORY_IDS = {
  wide: "viewer-workspace--wide",
  constrained: "viewer-workspace--constrained",
} as const;

const WORKSPACE_ROOT = '[class*="workspace"]';
const CONTEXT_PANEL = '[class*="contextDisclosure"]';
const CONSTRAINED_WRAPPER = '[class*="constrainedStory"]';

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

async function expectNoWorkspaceLandmarkAttributes(page: Page, element: ReturnType<Page["locator"]>) {
  const attributes = await element.evaluate((node) => {
    const el = node as HTMLElement;
    return {
      role: el.getAttribute("role"),
      ariaLabel: el.getAttribute("aria-label"),
      ariaLabelledby: el.getAttribute("aria-labelledby"),
    };
  });
  expect(attributes.role).toBeNull();
  expect(attributes.ariaLabel).toBeNull();
  expect(attributes.ariaLabelledby).toBeNull();
}

test.describe("Viewer Workspace Storybook surface", () => {
  test("proves the wide and constrained compositions, layout, axe, and forced colors", async ({
    page,
  }) => {
    await page.emulateMedia({ forcedColors: "active" });

    // Wide story: two balanced 1:1 columns in a centered 66rem workspace.
    await page.goto(`${STORYBOOK_URL}/iframe.html?id=${STORY_IDS.wide}&viewMode=story`);
    await expect(page.getByRole("heading", { level: 1, name: "Position viewer" })).toBeVisible();
    // Allow Storybook's own a11y addon to finish its axe pass before we run ours.
    await page.waitForTimeout(500);

    await expect(page.getByText("One static position - read-only")).toHaveCount(0);
    const board = page.getByRole("img", { name: BOARD_LABEL });
    await expect(board).toBeVisible();
    await expect(page.getByRole("button", { name: "Position picker" })).toBeVisible();
    await expect(page.locator('aside, [role="complementary"]')).toHaveCount(0);

    const workspaceRoot = page.locator(WORKSPACE_ROOT).first();
    const contextPanel = page.locator(CONTEXT_PANEL).first();
    const workspaceBox = await workspaceRoot.boundingBox();
    const boardBox = await board.boundingBox();
    const contextBox = await contextPanel.boundingBox();
    const viewportWidth = await page.evaluate(() => window.innerWidth);

    expect(workspaceBox).not.toBeNull();
    expect(workspaceBox?.width ?? 0).toBeLessThanOrEqual(1056);
    expect(
      Math.abs((workspaceBox?.x ?? 0) + (workspaceBox?.width ?? 0) / 2 - viewportWidth / 2),
    ).toBeLessThanOrEqual(2);

    expect(boardBox).not.toBeNull();
    expect(contextBox).not.toBeNull();
    const workspaceCenter = (workspaceBox?.x ?? 0) + (workspaceBox?.width ?? 0) / 2;
    const boardCenter = (boardBox?.x ?? 0) + (boardBox?.width ?? 0) / 2;
    const contextCenter = (contextBox?.x ?? 0) + (contextBox?.width ?? 0) / 2;
    // Balanced 1:1 columns: the board centers in the left column and the Context panel centers in the
    // right column, symmetric around the workspace center. The inter-column gap shifts the true column
    // centers off the raw bounding-box quarter points, so verify symmetry rather than a quarter offset.
    expect(boardCenter).toBeLessThan(workspaceCenter);
    expect(contextCenter).toBeGreaterThan(workspaceCenter);
    expect(
      Math.abs(Math.abs(boardCenter - workspaceCenter) - Math.abs(contextCenter - workspaceCenter)),
    ).toBeLessThanOrEqual(2);

    await expectNoWorkspaceLandmarkAttributes(page, workspaceRoot);
    await expectNoWorkspaceLandmarkAttributes(page, contextPanel);

    await checkA11y(page);

    // Constrained story: container-query reflow of the approved viewer surface.
    await page.goto(`${STORYBOOK_URL}/iframe.html?id=${STORY_IDS.constrained}&viewMode=story`);
    await expect(board).toBeVisible();
    await page.waitForTimeout(500);

    const wrapper = page.locator(CONSTRAINED_WRAPPER).first();
    await expect(wrapper).toHaveCount(1);
    for (const size of [320, 480, 640]) {
      await wrapper.evaluate((element, width) => {
        (element as HTMLElement).style.inlineSize = `${width}px`;
      }, size);
      await expect(page.getByRole("button", { name: "Position picker" })).toBeVisible();
      const boardBoxAtSize = await board.boundingBox();
      const wrapperBox = await wrapper.boundingBox();
      expect(boardBoxAtSize).not.toBeNull();
      expect(wrapperBox).not.toBeNull();
      expect(boardBoxAtSize?.width ?? 0).toBeLessThanOrEqual(size);
      expect(
        Math.abs(
          (boardBoxAtSize?.x ?? 0) +
            (boardBoxAtSize?.width ?? 0) / 2 -
            ((wrapperBox?.x ?? 0) + (wrapperBox?.width ?? 0) / 2),
        ),
      ).toBeLessThanOrEqual(2);
      await expect(wrapper).toHaveJSProperty("scrollWidth", size);
    }

    const constrainedRoot = page.locator(WORKSPACE_ROOT).first();
    const constrainedPanel = page.locator(CONTEXT_PANEL).first();
    await expectNoWorkspaceLandmarkAttributes(page, constrainedRoot);
    await expectNoWorkspaceLandmarkAttributes(page, constrainedPanel);

    await checkA11y(page);
  });
});