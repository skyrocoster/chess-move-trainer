import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const BOARD_LABEL =
  "Chess board: standard starting position, White at the bottom";
const STAGE1_GAME_UUID = "0007925c-5a8d-11f0-9740-f690a301000f";
const STORY_IDS = {
  wide: "viewer-mp-08-viewer-workspace--wide",
  constrained: "viewer-mp-08-viewer-workspace--constrained",
  loadingWide: "viewer-mp-08-viewer-workspace--loading-wide",
} as const;

const WORKSPACE_ROOT = '[class*="workspace"]';
const CONTEXT_PANEL = '[class*="context"]';
const CONSTRAINED_WRAPPER = '[class*="constrained"]';

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

async function expectNoWorkspaceLandmarkAttributes(
  page: Page,
  element: ReturnType<Page["locator"]>,
) {
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
    await page.goto(
      `${STORYBOOK_URL}/iframe.html?id=${STORY_IDS.wide}&viewMode=story`,
    );
    await expect(
      page.getByRole("heading", { level: 1, name: "Position viewer" }),
    ).toBeVisible();
    // Allow Storybook's own a11y addon to finish its axe pass before we run ours.
    await page.waitForTimeout(500);

    await expect(page.getByText("One static position - read-only")).toHaveCount(
      0,
    );
    const board = page.getByRole("img", { name: BOARD_LABEL });
    await expect(board).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Game Loader" }),
    ).toBeVisible();
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
      Math.abs(
        (workspaceBox?.x ?? 0) +
          (workspaceBox?.width ?? 0) / 2 -
          viewportWidth / 2,
      ),
    ).toBeLessThanOrEqual(2);

    expect(boardBox).not.toBeNull();
    expect(contextBox).not.toBeNull();
    const workspaceCenter =
      (workspaceBox?.x ?? 0) + (workspaceBox?.width ?? 0) / 2;
    const boardCenter = (boardBox?.x ?? 0) + (boardBox?.width ?? 0) / 2;
    const contextCenter = (contextBox?.x ?? 0) + (contextBox?.width ?? 0) / 2;
    // Balanced 1:1 columns: the board centers in the left column and the Context panel centers in the
    // right column, symmetric around the workspace center. The inter-column gap shifts the true column
    // centers off the raw bounding-box quarter points, so verify symmetry rather than a quarter offset.
    expect(boardCenter).toBeLessThan(workspaceCenter);
    expect(contextCenter).toBeGreaterThan(workspaceCenter);
    expect(
      Math.abs(
        Math.abs(boardCenter - workspaceCenter) -
          Math.abs(contextCenter - workspaceCenter),
      ),
    ).toBeLessThanOrEqual(2);

    await expectNoWorkspaceLandmarkAttributes(page, workspaceRoot);
    await expectNoWorkspaceLandmarkAttributes(page, contextPanel);

    await checkA11y(page);

    // Constrained story: container-query reflow of the approved viewer surface.
    await page.goto(
      `${STORYBOOK_URL}/iframe.html?id=${STORY_IDS.constrained}&viewMode=story`,
    );
    await expect(board).toBeVisible();
    await page.waitForTimeout(500);

    const wrapper = page.locator(CONSTRAINED_WRAPPER).first();
    await expect(wrapper).toHaveCount(1);
    for (const size of [320, 480, 640]) {
      await wrapper.evaluate((element, width) => {
        (element as HTMLElement).style.inlineSize = `${width}px`;
      }, size);
      await expect(
        page.getByRole("button", { name: "Game Loader" }),
      ).toBeVisible();
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

  test("keeps the board toolbar compact, responsive, and operable in both viewer compositions", async ({
    page,
  }) => {
    await page.goto(
      `${STORYBOOK_URL}/iframe.html?id=${STORY_IDS.wide}&viewMode=story`,
    );

    const wideBoard = page.getByRole("img", { name: BOARD_LABEL });
    const wideToolbar = page.getByRole("toolbar", { name: "Board controls" });
    const wideButtons = wideToolbar.getByRole("button");
    await expect(wideToolbar).toBeVisible();
    await expect(wideButtons).toHaveCount(2);
    await expect(page.getByRole("button", { name: "Previous" })).toBeDisabled();
    await expect(page.getByRole("button", { name: "Next" })).toBeDisabled();
    await expect(
      wideToolbar.getByText("Previous", { exact: true }),
    ).toBeVisible();
    await expect(wideToolbar.getByText("Next", { exact: true })).toBeVisible();

    const wideBoardBox = await wideBoard.boundingBox();
    const wideToolbarBox = await wideToolbar.boundingBox();
    const wideButtonBoxes = await wideButtons.evaluateAll((buttons) =>
      buttons.map((button) => button.getBoundingClientRect().width),
    );
    expect(wideBoardBox).not.toBeNull();
    expect(wideToolbarBox).not.toBeNull();
    expect(wideToolbarBox?.y ?? 0).toBeGreaterThanOrEqual(
      (wideBoardBox?.y ?? 0) + (wideBoardBox?.height ?? 0),
    );
    expect(
      Math.abs((wideToolbarBox?.x ?? 0) - (wideBoardBox?.x ?? 0)),
    ).toBeLessThanOrEqual(2);
    expect(
      Math.abs((wideToolbarBox?.width ?? 0) - (wideBoardBox?.width ?? 0)),
    ).toBeLessThanOrEqual(2);
    expect(
      wideButtonBoxes.reduce((total, width) => total + width, 0),
    ).toBeLessThan((wideToolbarBox?.width ?? 0) * 0.75);

    // Loaded intermediate coverage in the canonical constrained production
    // composition: perform the workspace's real load flow to reach ply 1.
    await page.goto(
      `${STORYBOOK_URL}/iframe.html?id=${STORY_IDS.constrained}&viewMode=story`,
    );
    await page.getByLabel("Game UUID").fill(STAGE1_GAME_UUID);
    await page.getByLabel(/Ply/).fill("1");
    await page.getByRole("button", { name: "Load game" }).click();
    await expect(page.getByText("Ply 1 of 3", { exact: true })).toBeVisible();

    const wrapper = page.locator(CONSTRAINED_WRAPPER).first();
    await wrapper.evaluate((element) => {
      (element as HTMLElement).style.inlineSize = "320px";
    });

    const constrainedBoard = page.getByRole("img", { name: /ply 1/ });
    const constrainedToolbar = page.getByRole("toolbar", {
      name: "Board controls",
    });
    const previous = constrainedToolbar.getByRole("button", {
      name: "Previous",
    });
    const next = constrainedToolbar.getByRole("button", { name: "Next" });
    await expect(constrainedToolbar.getByRole("button")).toHaveCount(2);
    await expect(
      constrainedToolbar.getByText("Previous", { exact: true }),
    ).toBeHidden();
    await expect(
      constrainedToolbar.getByText("Next", { exact: true }),
    ).toBeHidden();
    await expect(previous).toBeEnabled();
    await expect(next).toBeEnabled();
    await expect(constrainedToolbar).toHaveJSProperty(
      "scrollWidth",
      await constrainedToolbar.evaluate((element) => element.clientWidth),
    );

    const constrainedBoardBox = await constrainedBoard.boundingBox();
    const constrainedToolbarBox = await constrainedToolbar.boundingBox();
    expect(constrainedBoardBox).not.toBeNull();
    expect(constrainedToolbarBox).not.toBeNull();
    expect(constrainedToolbarBox?.y ?? 0).toBeGreaterThanOrEqual(
      (constrainedBoardBox?.y ?? 0) + (constrainedBoardBox?.height ?? 0),
    );

    await previous.focus();
    await page.keyboard.press("ArrowRight");
    await expect(next).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(page.getByText("Ply 2 of 3", { exact: true })).toBeVisible();

    await page.goto(
      `${STORYBOOK_URL}/iframe.html?id=${STORY_IDS.loadingWide}&viewMode=story`,
    );
    const loadingToolbar = page.getByRole("toolbar", {
      name: "Board controls",
    });
    await expect(
      loadingToolbar.getByRole("button", { name: "Previous" }),
    ).toBeDisabled();
    await expect(
      loadingToolbar.getByRole("button", { name: "Next" }),
    ).toBeDisabled();
  });
});
