import { expect, test, type Locator, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const STORY_IDS = {
  pickerWide: "documentation-demos-promotion-picker--wide-anchored-picker",
  pickerDrawer: "documentation-demos-promotion-picker--constrained-drawer",
  pickerKeyboard:
    "documentation-demos-promotion-picker--native-keyboard-promotion-initiation",
  viewerBranch: "application-viewer-workspace--branch-from-initial-position",
  viewerPromotion: "application-viewer-workspace--branch-promotion",
} as const;

function piece(page: Page, square: string) {
  return page.locator(
    `[data-square="${square}"] [aria-roledescription="draggable"]`,
  );
}

function center(box: { x: number; y: number; width: number; height: number }) {
  return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
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
  await page.waitForTimeout(50);
  await dispatchTouch("touchmove", center(targetBox!), false);
  await page.waitForTimeout(50);
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
    await page.waitForTimeout(100);
    await page.keyboard.press("ArrowUp");
    await page.keyboard.press("ArrowUp");
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
});
