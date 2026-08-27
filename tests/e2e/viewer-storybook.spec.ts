import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const BOARD_LABEL =
  "Chess board: standard starting position, White at the bottom";
const STAGE1_GAME_UUID = "0007925c-5a8d-11f0-9740-f690a301000f";
const STORY_IDS = {
  wide: "application-viewer-workspace--wide",
  constrained: "application-viewer-workspace--constrained",
  loadingWide: "application-viewer-workspace--loading-wide",
  blackSubject: "application-viewer-workspace--black-subject",
} as const;

const EVAL_STORY_IDS = {
  neutral: "application-analysis-evaluation-bar--neutral",
  queued: "application-analysis-evaluation-bar--queued",
  bestLine: "application-analysis-evaluation-bar--best-line",
  negativeCp: "application-analysis-evaluation-bar--completed-negative-cp",
  positiveMate: "application-analysis-evaluation-bar--completed-positive-mate",
  negativeMate: "application-analysis-evaluation-bar--completed-negative-mate",
  stale: "application-analysis-evaluation-bar--stale-with-retained-candidate",
  failed: "application-analysis-evaluation-bar--failed-with-retained-candidate",
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

type StageExpectation = {
  orientation: "white" | "black";
  state: "neutral" | "pending" | "best-line";
  value: number;
  shortValue: string;
  accessibleValue: string;
};

async function expectStageGeometry(page: Page, expected: StageExpectation) {
  const stage = page.getByTestId("board-eval-stage");
  const board = stage.locator("[data-board-visual]").first();
  const railShell = page.getByTestId("board-eval-rail-shell");
  const meter = page.getByRole("meter", { name: "Evaluation" });
  const track = meter.locator('[class*="track"]');
  const indicator = meter.locator('[class*="indicator"]');

  await expect(stage).toBeVisible();
  await expect(board).toBeVisible();
  await expect(railShell).toBeVisible();
  await expect(meter).toHaveAttribute("data-orientation", expected.orientation);
  await expect(meter).toHaveAttribute("data-state", expected.state);
  await expect(meter).toHaveAttribute("aria-valuemin", "0");
  await expect(meter).toHaveAttribute("aria-valuemax", "100");
  await expect(meter).toHaveAttribute("aria-valuenow", String(expected.value));
  await expect(meter).toHaveAttribute(
    "aria-valuetext",
    expected.accessibleValue,
  );
  await expect(meter).toContainText(expected.shortValue);

  const boardBox = await board.boundingBox();
  const railBox = await railShell.boundingBox();
  const trackBox = await track.boundingBox();
  const indicatorBox = await indicator.boundingBox();
  const toolbarBox = await page
    .getByRole("toolbar", { name: "Board controls" })
    .boundingBox();

  expect(boardBox).not.toBeNull();
  expect(railBox).not.toBeNull();
  expect(trackBox).not.toBeNull();
  expect(indicatorBox).not.toBeNull();
  expect(toolbarBox).not.toBeNull();
  if (!boardBox || !railBox || !trackBox || !indicatorBox || !toolbarBox) {
    throw new Error("The canonical board/evaluation geometry did not render.");
  }

  expect(Math.abs(boardBox.y - railBox.y)).toBeLessThanOrEqual(1);
  expect(Math.abs(boardBox.height - railBox.height)).toBeLessThanOrEqual(1);
  expect(railBox.width).toBe(30);
  expect(
    Math.abs(railBox.x - (boardBox.x + boardBox.width)),
  ).toBeLessThanOrEqual(0.01);
  expect(Math.abs(toolbarBox.x - boardBox.x)).toBeLessThanOrEqual(1);
  expect(Math.abs(toolbarBox.width - boardBox.width)).toBeLessThanOrEqual(1);
  expect(toolbarBox.y).toBeGreaterThanOrEqual(boardBox.y + boardBox.height - 1);

  const overflow = await stage.evaluate((element) => ({
    clientWidth: element.clientWidth,
    scrollWidth: element.scrollWidth,
  }));
  expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth);

  const trackTopDistance = indicatorBox.y - trackBox.y;
  const trackBottomDistance =
    trackBox.y + trackBox.height - (indicatorBox.y + indicatorBox.height);
  if (expected.orientation === "white") {
    expect(trackBottomDistance).toBeLessThanOrEqual(1);
    expect(trackTopDistance).toBeGreaterThan(1);
  } else {
    expect(trackTopDistance).toBeLessThanOrEqual(1);
    expect(trackBottomDistance).toBeGreaterThan(1);
  }
}

async function expectEvalStory(
  page: Page,
  storyId: string,
  expected: StageExpectation,
) {
  await page.goto(`${STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
  const meter = page.getByRole("meter", { name: "Evaluation" });
  await expect(meter).toBeVisible();
  await expect(meter).toHaveAttribute("data-orientation", expected.orientation);
  await expect(meter).toHaveAttribute("data-state", expected.state);
  await expect(meter).toHaveAttribute("aria-valuenow", String(expected.value));
  await expect(meter).toHaveAttribute(
    "aria-valuetext",
    expected.accessibleValue,
  );
  await expect(meter).toContainText(expected.shortValue);
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

    await expectStageGeometry(page, {
      orientation: "white",
      state: "neutral",
      value: 50,
      shortValue: "0.00",
      accessibleValue: "No analysis yet; evaluation neutral.",
    });
    await expect(
      page.getByTestId("board-eval-rail-shell").locator('[class*="track"]'),
    ).toHaveCSS("box-shadow", "none");

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
      const stageBoxAtSize = await page
        .getByTestId("board-eval-stage")
        .boundingBox();
      expect(boardBoxAtSize).not.toBeNull();
      expect(wrapperBox).not.toBeNull();
      expect(stageBoxAtSize).not.toBeNull();
      expect(boardBoxAtSize?.width ?? 0).toBeLessThanOrEqual(size);
      expect(
        Math.abs(
          (stageBoxAtSize?.x ?? 0) +
            (stageBoxAtSize?.width ?? 0) / 2 -
            ((wrapperBox?.x ?? 0) + (wrapperBox?.width ?? 0) / 2),
        ),
      ).toBeLessThanOrEqual(2);
      await expectStageGeometry(page, {
        orientation: "white",
        state: "neutral",
        value: 50,
        shortValue: "0.00",
        accessibleValue: "No analysis yet; evaluation neutral.",
      });
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

    const constrainedBoard = page.getByRole("group", { name: /ply 1/ });
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

  test("proves representative rail states, Black fill direction, meter semantics, and reduced motion", async ({
    page,
  }) => {
    await expectEvalStory(page, EVAL_STORY_IDS.neutral, {
      orientation: "white",
      state: "neutral",
      value: 50,
      shortValue: "0.00",
      accessibleValue: "No analysis yet; evaluation neutral.",
    });
    await expectEvalStory(page, EVAL_STORY_IDS.queued, {
      orientation: "white",
      state: "pending",
      value: 50,
      shortValue: "0.00",
      accessibleValue: "Analysis queued; evaluation pending.",
    });
    await expectEvalStory(page, EVAL_STORY_IDS.bestLine, {
      orientation: "black",
      state: "best-line",
      value: 51.7,
      shortValue: "+0.34",
      accessibleValue: "best-line evaluation +0.34.",
    });
    await expectEvalStory(page, EVAL_STORY_IDS.negativeCp, {
      orientation: "white",
      state: "best-line",
      value: 48.3,
      shortValue: "-0.34",
      accessibleValue: "best-line evaluation -0.34.",
    });
    await expectEvalStory(page, EVAL_STORY_IDS.positiveMate, {
      orientation: "white",
      state: "best-line",
      value: 100,
      shortValue: "+M3",
      accessibleValue: "best-line evaluation +M3.",
    });
    await expectEvalStory(page, EVAL_STORY_IDS.negativeMate, {
      orientation: "black",
      state: "best-line",
      value: 0,
      shortValue: "-M2",
      accessibleValue: "best-line evaluation -M2.",
    });
    await expectEvalStory(page, EVAL_STORY_IDS.stale, {
      orientation: "white",
      state: "best-line",
      value: 51.7,
      shortValue: "+0.34",
      accessibleValue: "Stale best-line evaluation +0.34.",
    });
    await expectEvalStory(page, EVAL_STORY_IDS.failed, {
      orientation: "black",
      state: "best-line",
      value: 51.7,
      shortValue: "+0.34",
      accessibleValue: "Stale best-line evaluation +0.34.",
    });

    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto(
      `${STORYBOOK_URL}/iframe.html?id=${EVAL_STORY_IDS.bestLine}&viewMode=story`,
    );
    await expect(page.getByRole("meter", { name: "Evaluation" })).toBeVisible();
    await expect(
      page
        .getByRole("meter", { name: "Evaluation" })
        .locator('[class*="indicator"]'),
    ).toHaveCSS("transition-property", "none");

    for (const width of [1280, 320, 480, 640]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(
        `${STORYBOOK_URL}/iframe.html?id=${STORY_IDS.blackSubject}&viewMode=story`,
      );
      await expect(
        page.getByRole("group", { name: /ply 0, Black at the bottom/ }),
      ).toBeVisible();
      await expectStageGeometry(page, {
        orientation: "black",
        state: "neutral",
        value: 50,
        shortValue: "0.00",
        accessibleValue: "No analysis yet; evaluation neutral.",
      });
    }
    await checkA11y(page);
  });
});
