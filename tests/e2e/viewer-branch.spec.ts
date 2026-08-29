import { expect, test, type Locator, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const AFTER_E4_FEN =
  "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1";
const STORY_IDS = {
  boardEmpty: "application-board-interactive-board--empty-origin",
  boardTerminal: "application-board-interactive-board--terminal-state",
  pickerWide: "documentation-demos-promotion-picker--wide-anchored-picker",
  pickerDrawer: "documentation-demos-promotion-picker--constrained-drawer",
  pickerKeyboard:
    "documentation-demos-promotion-picker--native-keyboard-promotion-initiation",
  viewerBranch: "application-viewer-workspace--branch-from-initial-position",
  viewerPromotion: "application-viewer-workspace--branch-promotion",
  candidateActivation:
    "application-viewer-workspace-analysis--candidate-surface",
  candidatePromotion:
    "application-viewer-workspace-analysis--candidate-promotion-surface",
} as const;

function piece(page: Page, square: string) {
  return page.locator(
    `[data-square="${square}"] [aria-roledescription="draggable"]`,
  );
}

function center(box: { x: number; y: number; width: number; height: number }) {
  return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
}

async function expectDropTarget(target: Locator) {
  await expect(target).toHaveCSS("box-shadow", /0px 0px 0px 1px/);
}

async function dragWithMouse(page: Page, source: Locator, target: Locator) {
  const sourceBox = await source.boundingBox();
  const targetBox = await target.boundingBox();
  expect(sourceBox).not.toBeNull();
  expect(targetBox).not.toBeNull();
  const sourcePoint = center(sourceBox!);
  const targetPoint = center(targetBox!);
  await page.mouse.move(sourcePoint.x, sourcePoint.y);
  await page.mouse.down();
  await page.mouse.move(targetPoint.x, targetPoint.y, { steps: 6 });
  await page.mouse.up();
}

async function dragWithTouchOnBoard(
  page: Page,
  sourceSquare: string,
  targetSquare: string,
  boardTestId: string,
) {
  const source = piece(page, sourceSquare);
  const target = page.locator(`[data-square="${targetSquare}"]`);
  const sourceBox = await source.boundingBox();
  const targetBox = await target.boundingBox();
  expect(sourceBox).not.toBeNull();
  expect(targetBox).not.toBeNull();

  const dispatchTouch = async (
    type: string,
    point: { x: number; y: number },
    changed: boolean,
  ) => {
    await page.evaluate(
      ({ sourceSquare, point, type, changed }) => {
        const source = document.querySelector(
          `[data-square="${sourceSquare}"] [aria-roledescription="draggable"]`,
        );
        if (!source) {
          throw new Error(`Missing touch source ${sourceSquare}`);
        }

        const touch = new Touch({
          identifier: 2,
          target: source,
          clientX: point.x,
          clientY: point.y,
          pageX: point.x,
          pageY: point.y,
          screenX: point.x,
          screenY: point.y,
          radiusX: 1,
          radiusY: 1,
          rotationAngle: 0,
          force: 1,
        });

        source.dispatchEvent(
          new TouchEvent(type, {
            bubbles: true,
            cancelable: true,
            touches: changed ? [] : [touch],
            changedTouches: [touch],
          }),
        );
      },
      { sourceSquare, point, type, changed },
    );
  };

  await page.getByTestId(boardTestId).waitFor();
  await dispatchTouch("touchstart", center(sourceBox!), false);
  await expect(source).toHaveAttribute("aria-pressed", "true");
  await dispatchTouch("touchmove", center(targetBox!), false);
  await expectDropTarget(target);
  await dispatchTouch("touchend", center(targetBox!), true);
}

async function openPromotionStory(page: Page, storyId: string) {
  await page.goto(`${STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
  await expect(page.getByTestId("promotion-picker-demo")).toBeVisible();
  await expect(
    page.getByRole("dialog", { name: "Choose a promotion piece" }),
  ).toBeVisible();
}

async function openClosedPromotionStory(page: Page, storyId: string) {
  await page.goto(`${STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
  await expect(page.getByTestId("promotion-picker-demo")).toBeVisible();
  await expect(page.getByRole("dialog")).toHaveCount(0);
}

async function openViewerStory(page: Page, storyId: string) {
  await page.goto(`${STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
  await expect(
    page.getByRole("heading", { name: "Position viewer", level: 1 }),
  ).toBeVisible();
  await expect(page.getByText(/^Ply \d+ of \d+$/)).toBeVisible();
}

async function openInteractiveBoardStory(page: Page, storyId: string) {
  await page.goto(`${STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
  await expect(page.getByTestId("interactive-board-adapter")).toBeVisible();
}

async function checkInteractiveBoardA11y(page: Page) {
  const results = await new AxeBuilder({ page })
    .disableRules(["landmark-one-main", "page-has-heading-one", "region"])
    .include('[data-testid="interactive-board-adapter"]')
    .analyze();
  expect(results.violations).toEqual([]);
}

async function checkPageA11y(page: Page) {
  const results = await new AxeBuilder({ page })
    .disableRules(["landmark-one-main", "page-has-heading-one", "region"])
    .analyze();
  expect(results.violations).toEqual([]);
}

async function checkPromotionA11y(page: Page) {
  const results = await new AxeBuilder({ page })
    .disableRules(["landmark-one-main", "page-has-heading-one", "region"])
    .include('[role="dialog"]')
    .analyze();
  expect(results.violations).toEqual([]);
}

test.describe("MP-11 Stage 2 application-owned promotion picker", () => {
  test("keeps pending pointer promotion unchanged and commits each exact choice", async ({
    page,
  }) => {
    const promotions = [
      ["queen", "e8=Q"],
      ["rook", "e8=R"],
      ["bishop", "e8=B"],
      ["knight", "e8=N"],
    ] as const;

    for (const [name, san] of promotions) {
      await openPromotionStory(page, STORY_IDS.pickerWide);
      await page.keyboard.press("Escape");
      await expect(page.getByRole("dialog")).toHaveCount(0);
      await dragWithMouse(
        page,
        piece(page, "e7"),
        page.locator('[data-square="e8"]'),
      );

      await expect(
        page.getByRole("dialog", { name: "Choose a promotion piece" }),
      ).toBeVisible();
      await expect(piece(page, "e7")).toHaveCount(1);
      await expect(piece(page, "e8")).toHaveCount(0);
      await expect(page.getByTestId("promotion-current-fen")).toContainText(
        "k7/4P3/8/8/8/8/8/4K3 w - - 0 1",
      );

      const choice = page.getByRole("button", { name: `Promote to ${name}` });
      await choice.click();
      await expect(page.getByTestId("promotion-last-san")).toContainText(san);
      await expect(page.getByTestId("promotion-current-fen")).not.toContainText(
        "k7/4P3/8/8/8/8/8/4K3 w - - 0 1",
      );
    }
  });

  test("preserves native touch and keyboard drag-to-promotion initiation", async ({
    page,
  }) => {
    await openPromotionStory(page, STORY_IDS.pickerDrawer);
    await page.keyboard.press("Escape");
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await dragWithTouchOnBoard(page, "e7", "e8", "promotion-board");
    await expect(
      page.getByRole("dialog", { name: "Choose a promotion piece" }),
    ).toBeVisible();
    await expect(piece(page, "e7")).toHaveCount(1);
    await expect(piece(page, "e8")).toHaveCount(0);
    await expect(page.getByTestId("promotion-current-fen")).toContainText(
      "k7/4P3/8/8/8/8/8/4K3 w - - 0 1",
    );

    await openClosedPromotionStory(page, STORY_IDS.pickerKeyboard);
    const keyboardPiece = piece(page, "e7");
    await keyboardPiece.focus();
    await page.keyboard.press("Enter");
    await expect(keyboardPiece).toHaveAttribute("aria-pressed", "true");
    await page.keyboard.press("ArrowUp");
    await page.keyboard.press("ArrowUp");
    await expectDropTarget(page.locator('[data-square="e8"]'));
    await page.keyboard.press("Enter");
    await expect(
      page.getByRole("dialog", { name: "Choose a promotion piece" }),
    ).toBeVisible();
    await page.keyboard.press("Tab");
    await page.keyboard.press("Enter");
    await expect(page.getByTestId("promotion-last-san")).toContainText("e8=R");
  });

  test("renders the anchored wide popover and constrained drawer variants", async ({
    page,
  }) => {
    await openPromotionStory(page, STORY_IDS.pickerWide);
    await expect(page.getByTestId("promotion-popover")).toBeVisible();
    await expect(page.getByTestId("promotion-drawer")).toHaveCount(0);
    await checkPromotionA11y(page);

    await openPromotionStory(page, STORY_IDS.pickerDrawer);
    await expect(page.getByTestId("promotion-drawer")).toBeVisible();
    await expect(page.getByTestId("promotion-popover")).toHaveCount(0);
    await checkPromotionA11y(page);
  });

  test("cancels from Escape, outside press, and touch backdrop with source focus restoration", async ({
    page,
  }) => {
    await openPromotionStory(page, STORY_IDS.pickerWide);
    await page.keyboard.press("Escape");
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(piece(page, "e7")).toBeFocused();
    await expect(page.getByTestId("promotion-current-fen")).toContainText(
      "k7/4P3/8/8/8/8/8/4K3 w - - 0 1",
    );

    await page.getByTestId("promotion-picker-demo").waitFor();
    await page.reload();
    await openPromotionStory(page, STORY_IDS.pickerWide);
    await page
      .getByTestId("promotion-popover-backdrop")
      .click({ position: { x: 2, y: 2 } });
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(piece(page, "e7")).toBeFocused();

    await openPromotionStory(page, STORY_IDS.pickerDrawer);
    await page
      .getByTestId("promotion-drawer-backdrop")
      .click({ position: { x: 2, y: 2 } });
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(piece(page, "e7")).toBeFocused();
    await expect(page.getByTestId("promotion-current-fen")).toContainText(
      "k7/4P3/8/8/8/8/8/4K3 w - - 0 1",
    );
  });

  test("keeps reduced motion and forced-colors states reviewable", async ({
    page,
  }) => {
    await page.emulateMedia({
      forcedColors: "active",
      reducedMotion: "reduce",
    });
    await openPromotionStory(page, STORY_IDS.pickerDrawer);
    await expect(
      page.getByRole("button", { name: "Promote to queen" }),
    ).toBeVisible();
    await expect(page.getByTestId("promotion-drawer")).toHaveCSS(
      "transition-duration",
      "0s",
    );
    await checkPromotionA11y(page);
  });
});

test.describe("MP-11 Stage 3 temporary branch mechanics", () => {
  test("presents and copies exact branch context without changing mechanics", async ({
    page,
  }) => {
    await page
      .context()
      .grantPermissions(["clipboard-read", "clipboard-write"], {
        origin: STORYBOOK_URL,
      });
    await openInteractiveBoardStory(page, STORY_IDS.boardEmpty);

    await expect(page.getByTestId("branch-origin-fen")).toHaveText(
      STARTING_FEN,
    );
    await expect(page.getByTestId("branch-current-fen")).toHaveText(
      STARTING_FEN,
    );
    await expect(page.getByTestId("branch-current-ply")).toHaveText(
      "Current ply 0",
    );
    await expect(
      page.getByRole("button", { name: "Copy branch origin FEN" }),
    ).toHaveCount(1);
    await expect(
      page.getByRole("button", { name: "Copy current branch FEN" }),
    ).toHaveCount(1);
    expect(
      await page.evaluate(() =>
        ["branch-origin-fen", "branch-current-fen"].every(
          (testId) =>
            document
              .querySelector(`[data-testid="${testId}"]`)
              ?.textContent?.split(" ").length === 6,
        ),
      ),
    ).toBe(true);

    await page.getByRole("button", { name: "Copy branch origin FEN" }).click();
    await expect(page.getByTestId("branch-status")).toHaveText(
      "Copied branch origin FEN.",
    );
    await expect
      .poll(() => page.evaluate(() => navigator.clipboard.readText()), {
        timeout: 5000,
      })
      .toBe(STARTING_FEN);

    await dragWithMouse(
      page,
      piece(page, "e2"),
      page.locator('[data-square="e4"]'),
    );
    await expect(page.getByTestId("branch-san")).toHaveText("1. e4");
    await expect(page.getByTestId("branch-current-fen")).toHaveText(
      AFTER_E4_FEN,
    );
    await expect(page.getByTestId("branch-current-ply")).toHaveText(
      "Current ply 1",
    );
    await expect(page.getByRole("button", { name: "Undo" })).toBeEnabled();
    await expect(page.getByRole("button", { name: "Reset" })).toBeEnabled();

    await page.getByRole("button", { name: "Copy current branch FEN" }).click();
    await expect(page.getByTestId("branch-status")).toHaveText(
      "Copied current branch FEN.",
    );
    await expect
      .poll(() => page.evaluate(() => navigator.clipboard.readText()), {
        timeout: 5000,
      })
      .toBe(AFTER_E4_FEN);

    await page.getByRole("button", { name: "Undo" }).click();
    await expect(page.getByTestId("branch-san")).toHaveText(
      "No branch moves yet",
    );
    await expect(page.getByTestId("branch-current-fen")).toHaveText(
      STARTING_FEN,
    );
    await expect(page.getByTestId("branch-current-ply")).toHaveText(
      "Current ply 0",
    );
  });

  test("keeps the panel responsive, wrapped, and below the board at required widths", async ({
    page,
  }) => {
    for (const width of [320, 480, 640]) {
      await page.setViewportSize({ width, height: 900 });
      await openInteractiveBoardStory(page, STORY_IDS.boardEmpty);
      const metrics = await page.evaluate(() => {
        const adapter = document.querySelector(
          '[data-testid="interactive-board-adapter"]',
        );
        const board = adapter
          ?.querySelector('[data-testid="interactive-board"]')
          ?.getBoundingClientRect();
        const panel = adapter?.children[1]?.getBoundingClientRect();
        const copyButtons = [
          ...document.querySelectorAll('[data-testid^="copy-"]'),
        ].map((button) => ({
          name: button.getAttribute("aria-label"),
          height: button.getBoundingClientRect().height,
        }));
        return {
          documentOverflow:
            document.documentElement.scrollWidth >
            document.documentElement.clientWidth,
          bodyOverflow: document.body.scrollWidth > document.body.clientWidth,
          panelBelowBoard: Boolean(board && panel && panel.top >= board.bottom),
          fenHeights: ["branch-origin-fen", "branch-current-fen"].map(
            (testId) =>
              document
                .querySelector(`[data-testid="${testId}"]`)
                ?.getBoundingClientRect().height ?? 0,
          ),
          copyButtons,
          sanWidth:
            document
              .querySelector('[data-testid="branch-san"]')
              ?.getBoundingClientRect().width ?? 0,
          statusWidth:
            document
              .querySelector('[data-testid="branch-status"]')
              ?.getBoundingClientRect().width ?? 0,
        };
      });

      expect(metrics.documentOverflow, `${width}px document overflow`).toBe(
        false,
      );
      expect(metrics.bodyOverflow, `${width}px body overflow`).toBe(false);
      expect(metrics.panelBelowBoard, `${width}px panel position`).toBe(true);
      expect(
        metrics.fenHeights.every((height) => height >= 32),
        `${width}px FEN wrapping`,
      ).toBe(true);
      expect(metrics.copyButtons).toEqual([
        { name: "Copy branch origin FEN", height: 48 },
        { name: "Copy current branch FEN", height: 48 },
      ]);
      expect(metrics.sanWidth).toBeGreaterThan(0);
      expect(metrics.statusWidth).toBeGreaterThan(0);
    }
  });

  test("routes Best and alternative candidates through the displayed branch after Flip", async ({
    page,
  }) => {
    await openViewerStory(page, STORY_IDS.candidateActivation);
    await expect(page.getByText("Analysis complete")).toBeVisible();

    const bestLine = page.getByRole("button", { name: "1. e4" });
    const alternativeLine = page.getByRole("button", { name: "1. d4" });
    await expect(page.getByRole("button", { name: /^1\./ })).toHaveCount(5);
    await expect(bestLine.locator("button")).toHaveCount(0);

    await bestLine.focus();
    await page.keyboard.press("Enter");
    await expect(page.getByTestId("branch-current-fen")).toHaveText(
      AFTER_E4_FEN,
    );
    await expect(page.getByTestId("branch-san")).toHaveText("1. e4");

    await page.getByRole("button", { name: "Flip" }).click();
    await expect(
      page.getByRole("group", { name: /ply 0, Black at the bottom/ }),
    ).toBeVisible();
    await expect(page.getByTestId("branch-current-fen")).toHaveText(
      AFTER_E4_FEN,
    );

    await page
      .getByTestId("interactive-board-adapter")
      .getByRole("button", { name: "Reset" })
      .click();
    await expect(page.getByTestId("branch-current-fen")).toHaveText(
      STARTING_FEN,
    );
    await alternativeLine.click();
    await expect(page.getByTestId("branch-current-fen")).toHaveText(
      "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1",
    );
    await expect(page.getByTestId("branch-san")).toHaveText("1. d4");
    await checkPageA11y(page);
  });

  test("keeps controlled candidate buttons accessible without constrained overflow", async ({
    page,
  }) => {
    for (const width of [320, 480, 640]) {
      await page.setViewportSize({ width, height: 900 });
      await openViewerStory(page, STORY_IDS.candidateActivation);
      await expect(page.getByRole("button", { name: "1. e4" })).toBeVisible();
      const overflow = await page.evaluate(() => ({
        document:
          document.documentElement.scrollWidth <=
          document.documentElement.clientWidth,
        body: document.body.scrollWidth <= document.body.clientWidth,
        panel: [
          ...document.querySelectorAll<HTMLElement>(
            '[aria-labelledby="analysis-panel-heading"]',
          ),
        ].every((element) => element.scrollWidth <= element.clientWidth),
      }));
      expect(overflow.document, `${width}px document overflow`).toBe(true);
      expect(overflow.body, `${width}px body overflow`).toBe(true);
      expect(overflow.panel, `${width}px analysis panel overflow`).toBe(true);
    }
  });

  test("keeps focus, forced colors, reduced motion, and axe accessibility reviewable", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 320, height: 900 });
    await page.emulateMedia({
      forcedColors: "none",
      reducedMotion: "no-preference",
    });
    await openInteractiveBoardStory(page, STORY_IDS.boardEmpty);

    const copyButton = page.getByRole("button", {
      name: "Copy branch origin FEN",
    });
    await copyButton.focus();
    await expect(copyButton).toBeFocused();
    const focusStyle = await copyButton.evaluate((button) => {
      const style = getComputedStyle(button);
      return {
        outlineStyle: style.outlineStyle,
        outlineWidth: style.outlineWidth,
      };
    });
    expect(focusStyle.outlineStyle).not.toBe("none");
    expect(parseFloat(focusStyle.outlineWidth)).toBeGreaterThanOrEqual(2);

    await page.emulateMedia({
      forcedColors: "active",
      reducedMotion: "reduce",
    });
    await expect
      .poll(() =>
        page.evaluate(
          () => window.matchMedia("(forced-colors: active)").matches,
        ),
      )
      .toBe(true);
    await expect
      .poll(() =>
        page.evaluate(
          () => window.matchMedia("(prefers-reduced-motion: reduce)").matches,
        ),
      )
      .toBe(true);
    const mediaStyles = await page.evaluate(() => {
      const panelChild = document.querySelector(
        '[data-testid="interactive-board-adapter"] > :nth-child(2) *',
      );
      const boardChild = document.querySelector(
        '[data-testid="interactive-board"] *',
      );
      const panel = document.querySelector(
        '[data-testid="interactive-board-adapter"] > :nth-child(2)',
      );
      return {
        panelBackground: panel ? getComputedStyle(panel).backgroundColor : "",
        panelBorder: panel ? getComputedStyle(panel).borderColor : "",
        boardAnimation: boardChild
          ? getComputedStyle(boardChild).animationDuration
          : "",
        panelTransition: panelChild
          ? getComputedStyle(panelChild).transitionDuration
          : "",
      };
    });
    expect(mediaStyles.panelBackground).not.toBe("");
    expect(mediaStyles.panelBorder).not.toBe("");
    expect(mediaStyles.boardAnimation).toBe("0s");
    expect(mediaStyles.panelTransition).toBe("0s");
    await checkInteractiveBoardA11y(page);
  });

  test("renders the terminal panel state with its existing status", async ({
    page,
  }) => {
    await openInteractiveBoardStory(page, STORY_IDS.boardTerminal);
    await expect(page.getByTestId("branch-terminal")).toHaveText(
      "Terminal result: Checkmate",
    );
    await expect(page.getByTestId("branch-current-ply")).toHaveText(
      "Current ply 8",
    );
    await expect(page.getByTestId("branch-status")).toHaveText(
      "Make a legal move to start a temporary branch.",
    );
  });

  test("plays from the displayed ply, keeps captured context, gates traversal, and supports Undo", async ({
    page,
  }) => {
    await openViewerStory(page, STORY_IDS.viewerBranch);
    await dragWithMouse(
      page,
      piece(page, "e2"),
      page.locator('[data-square="e4"]'),
    );

    await expect(page.getByTestId("branch-san")).toContainText("1. e4");
    await expect(page.getByText("Ply 0 of 3", { exact: true })).toBeVisible();
    await expect(
      page.getByText("Initial position", { exact: true }),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Previous" })).toBeDisabled();
    await expect(page.getByRole("button", { name: "Next" })).toBeDisabled();

    await page.getByRole("button", { name: "Undo" }).click();
    await expect(page.getByTestId("branch-san")).toContainText(
      "No branch moves yet",
    );
    await expect(page.getByRole("button", { name: "Next" })).toBeEnabled();
  });

  test("plays for the side to move at another ply and discards on replacement load", async ({
    page,
  }) => {
    await openViewerStory(page, STORY_IDS.viewerBranch);
    const ply = page.getByLabel(/Ply/);
    await ply.fill("1");
    await page.getByRole("button", { name: "Load game" }).click();
    await expect(page.getByText("Ply 1 of 3", { exact: true })).toBeVisible();

    await dragWithMouse(
      page,
      piece(page, "e7"),
      page.locator('[data-square="e5"]'),
    );
    await expect(page.getByTestId("branch-san")).toContainText("1... e5");
    await expect(page.getByText("e4", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Previous" })).toBeDisabled();
    await expect(page.getByRole("button", { name: "Next" })).toBeDisabled();

    await ply.fill("0");
    await page.getByRole("button", { name: "Load game" }).click();
    await expect(page.getByText("Ply 0 of 3", { exact: true })).toBeVisible();
    await expect(page.getByTestId("branch-san")).toContainText(
      "No branch moves yet",
    );
    await expect(page.getByRole("button", { name: "Next" })).toBeEnabled();
  });

  test("routes a displayed-ply promotion through the accepted picker", async ({
    page,
  }) => {
    await openViewerStory(page, STORY_IDS.viewerPromotion);
    await dragWithMouse(
      page,
      piece(page, "e7"),
      page.locator('[data-square="e8"]'),
    );

    await expect(
      page.getByRole("dialog", { name: "Choose a promotion piece" }),
    ).toBeVisible();
    await expect(piece(page, "e7")).toHaveCount(1);
    await page.getByRole("button", { name: "Promote to knight" }).click();
    await expect(page.getByTestId("branch-san")).toContainText("1. e8=N");
    await expect(piece(page, "e7")).toHaveCount(0);
    await expect(
      page.getByText("Initial position", { exact: true }),
    ).toBeVisible();
  });

  test("routes a promotion candidate through the accepted picker with focus and FEN parity", async ({
    page,
  }) => {
    await openViewerStory(page, STORY_IDS.candidatePromotion);
    const candidate = page.getByRole("button", { name: /1\. e8=Q/ });
    await expect(page.getByTestId("branch-current-fen")).toHaveText(
      "k7/4P3/8/8/8/8/8/4K3 w - - 0 1",
    );

    await candidate.click();
    const dialog = page.getByRole("dialog", {
      name: "Choose a promotion piece",
    });
    await expect(dialog).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Promote to queen" }),
    ).toBeFocused();
    await expect(page.getByTestId("branch-current-fen")).toHaveText(
      "k7/4P3/8/8/8/8/8/4K3 w - - 0 1",
    );
    await checkPageA11y(page);

    await page.keyboard.press("Escape");
    await expect(dialog).toHaveCount(0);
    await expect(candidate).toBeFocused();
    await expect(page.getByTestId("branch-current-fen")).toHaveText(
      "k7/4P3/8/8/8/8/8/4K3 w - - 0 1",
    );

    await candidate.click();
    await page.getByRole("button", { name: "Promote to queen" }).click();
    await expect(page.getByTestId("branch-san")).toHaveText("1. e8=Q+");
    await expect(page.getByTestId("branch-current-fen")).toHaveText(
      "k3Q3/8/8/8/8/8/8/4K3 b - - 0 1",
    );
  });
});
