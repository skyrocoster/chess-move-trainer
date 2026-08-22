import { expect, test, type Locator, type Page } from "@playwright/test";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const STORY_IDS = {
  branch: "viewer-mp-11-stage-5-analysis--branch-analysis",
  stale: "viewer-mp-11-stage-5-analysis--stale-result",
  failed: "viewer-mp-11-stage-5-analysis--failed-retry",
  running: "viewer-mp-11-stage-5-analysis--running-observation",
} as const;

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const AFTER_E4_FEN =
  "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1";
const NOVEL_BRANCH_FEN =
  "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2";
const GAME_UUID = "0007925c-5a8d-11f0-9740-f690a301000f";

function piece(page: Page, square: string) {
  return page.locator(
    `[data-square="${square}"] [aria-roledescription="draggable"]`,
  );
}

function center(box: { x: number; y: number; width: number; height: number }) {
  return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
}

async function dragWithMouse(page: Page, source: Locator, target: Locator) {
  await source.scrollIntoViewIfNeeded();
  await target.scrollIntoViewIfNeeded();
  const sourceBox = await source.boundingBox();
  const targetBox = await target.boundingBox();
  expect(sourceBox).not.toBeNull();
  expect(targetBox).not.toBeNull();
  const sourcePoint = center(sourceBox!);
  const targetPoint = center(targetBox!);
  await page.mouse.move(sourcePoint.x, sourcePoint.y);
  await page.mouse.down();
  await page.mouse.move(targetPoint.x, targetPoint.y, { steps: 20 });
  await page.mouse.up();
}

async function openStory(page: Page, storyId: string) {
  await page.goto(`${STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
  await expect(
    page.getByRole("heading", { name: "Position viewer", level: 1 }),
  ).toBeVisible();
  await page.getByLabel("Game UUID").fill(GAME_UUID);
  await page.getByRole("button", { name: "Load game" }).click();
  await expect(page.getByText(/^Ply \d+ of \d+$/)).toBeVisible();
}

async function expectCurrentFen(page: Page, fen: string) {
  await expect(page.getByTestId("branch-current-fen")).toHaveText(fen);
}

async function expectAnalysisState(page: Page, state: string) {
  await expect(
    page.locator('[role="status"]').filter({ hasText: state }).last(),
  ).toBeVisible();
}

test.describe("MP-11 Stage 5 analysis integration", () => {
  test("observes stored results, queues only the novel current branch FEN, and reuses it", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.branch);
    await expectAnalysisState(page, "Analysis complete");
    await expectCurrentFen(page, STARTING_FEN);
    await expect(page.getByTestId("stage5-enqueue-log")).toHaveText(
      "No deliberate analysis actions",
    );

    await dragWithMouse(
      page,
      piece(page, "e2"),
      page.locator('[data-square="e4"]'),
    );
    await expectCurrentFen(page, AFTER_E4_FEN);
    await dragWithMouse(
      page,
      piece(page, "c7"),
      page.locator('[data-square="c5"]'),
    );
    await expectCurrentFen(page, NOVEL_BRANCH_FEN);
    await expect(
      page.getByText("Analysis available on request", { exact: true }),
    ).toBeVisible();
    await expect(page.getByTestId("stage5-enqueue-log")).toHaveText(
      "No deliberate analysis actions",
    );

    await page.getByRole("button", { name: "Analyze position" }).click();
    await expectAnalysisState(page, "Analysis queued");
    await expect(page.getByTestId("stage5-enqueue-log")).toHaveText(
      `analyze: ${NOVEL_BRANCH_FEN}`,
    );
    await expectAnalysisState(page, "Analysis complete");

    await page
      .getByTestId("interactive-board-adapter")
      .getByRole("button", { name: "Reset" })
      .click();
    await expectCurrentFen(page, STARTING_FEN);
    await expectAnalysisState(page, "Analysis complete");
    await expect(page.getByTestId("stage5-enqueue-log")).toHaveText(
      `analyze: ${NOVEL_BRANCH_FEN}`,
    );
  });

  test("keeps stale results behind deliberate Update", async ({ page }) => {
    await openStory(page, STORY_IDS.stale);
    await expectAnalysisState(page, "Stale analysis");
    await expect(
      page.getByRole("button", { name: "Update analysis" }),
    ).toBeVisible();
    await expect(page.getByTestId("stage5-enqueue-log")).toHaveText(
      "No deliberate analysis actions",
    );

    await page.getByRole("button", { name: "Update analysis" }).click();
    await expectAnalysisState(page, "Analysis queued");
    await expect(page.getByTestId("stage5-enqueue-log")).toHaveText(
      `update: ${STARTING_FEN}`,
    );
    await expectAnalysisState(page, "Analysis complete");
  });

  test("keeps failed results durable until deliberate Retry", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.failed);
    await expectAnalysisState(page, "Analysis failed");
    await expect(
      page.getByRole("button", { name: "Retry analysis" }),
    ).toBeVisible();
    await expect(page.getByTestId("stage5-enqueue-log")).toHaveText(
      "No deliberate analysis actions",
    );

    await page.getByRole("button", { name: "Retry analysis" }).click();
    await expectAnalysisState(page, "Analysis queued");
    await expect(page.getByTestId("stage5-enqueue-log")).toHaveText(
      `retry: ${STARTING_FEN}`,
    );
    await expectAnalysisState(page, "Analysis complete");
  });

  test("aborts observation only, without exposing cancellation or enqueueing", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.running);
    await expectAnalysisState(page, "Analysis running");
    await expect(
      page.getByRole("button", { name: /Analyze|Update|Retry analysis/ }),
    ).toHaveCount(0);
    await expect(page.getByRole("button", { name: /cancel/i })).toHaveCount(0);

    await dragWithMouse(
      page,
      piece(page, "e2"),
      page.locator('[data-square="e4"]'),
    );
    await expectCurrentFen(page, AFTER_E4_FEN);
    await expect(
      page.getByText("Analysis available on request", { exact: true }),
    ).toBeVisible();
    await expect(page.getByTestId("stage5-enqueue-log")).toHaveText(
      "No deliberate analysis actions",
    );
    await expect(page.getByTestId("stage5-abort-log")).toContainText(
      "aborted observation",
    );
  });
});
