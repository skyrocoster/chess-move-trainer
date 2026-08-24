import { expect, test, type Locator, type Page } from "@playwright/test";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const STORY_IDS = {
  branch: "application-viewer-workspace--branch-from-initial-position",
  castling: "application-viewer-workspace--branch-castling",
  enPassant: "application-viewer-workspace--branch-en-passant",
  promotion: "application-viewer-workspace--branch-promotion",
  terminal: "application-viewer-workspace--branch-terminal",
} as const;

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const CASTLING_FEN = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1";
const EN_PASSANT_FEN = "4k3/3p4/8/4P3/8/8/8/4K3 b - - 0 1";
const PROMOTION_FEN = "k7/4P3/8/8/8/8/8/4K3 w - - 0 1";
const TERMINAL_FEN = "7k/5Q2/p5K1/8/8/8/8/8 b - - 0 1";

function piece(page: Page, square: string) {
  return page.locator(
    `[data-square="${square}"] [aria-roledescription="draggable"]`,
  );
}

function center(box: { x: number; y: number; width: number; height: number }) {
  return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
}

async function dragWithMouse(page: Page, source: Locator, target: Locator) {
  // boundingBox() does not scroll, and page.mouse events land at raw viewport
  // coordinates; at the default 1280x720 viewport rank 1 sits below the fold,
  // so bring both endpoints into view before reading their boxes.
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

async function openViewerStory(page: Page, storyId: string) {
  await page.goto(`${STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
  await expect(
    page.getByRole("heading", { name: "Position viewer", level: 1 }),
  ).toBeVisible();
  await expect(page.getByText(/^Ply \d+ of \d+$/)).toBeVisible();
}

async function expectFen(page: Page, originFen: string, currentFen: string) {
  await expect(page.getByTestId("branch-origin-fen")).toHaveText(originFen);
  await expect(page.getByTestId("branch-current-fen")).toHaveText(currentFen);
}

test.describe("MP-11 Stage 4 special moves and terminal branch", () => {
  test("rejects an illegal drop without changing displayed SAN or FEN", async ({
    page,
  }) => {
    await openViewerStory(page, STORY_IDS.branch);
    await expectFen(page, STARTING_FEN, STARTING_FEN);

    await dragWithMouse(
      page,
      piece(page, "e2"),
      page.locator('[data-square="e5"]'),
    );

    await expect(page.getByTestId("branch-status")).toContainText("illegal");
    await expect(page.getByTestId("branch-san")).toHaveText(
      "No branch moves yet",
    );
    await expectFen(page, STARTING_FEN, STARTING_FEN);
  });

  test("plays both sides of castling with exact SAN and six-field FEN", async ({
    page,
  }) => {
    await openViewerStory(page, STORY_IDS.castling);
    await expectFen(page, CASTLING_FEN, CASTLING_FEN);

    await dragWithMouse(
      page,
      piece(page, "e1"),
      page.locator('[data-square="g1"]'),
    );
    await expect(page.getByTestId("branch-san")).toHaveText("1. O-O");
    await expectFen(page, CASTLING_FEN, "r3k2r/8/8/8/8/8/8/R4RK1 b kq - 1 1");

    await dragWithMouse(
      page,
      piece(page, "e8"),
      page.locator('[data-square="c8"]'),
    );
    await expect(page.getByTestId("branch-san")).toHaveText(
      "1. O-O 1... O-O-O",
    );
    await expectFen(page, CASTLING_FEN, "2kr3r/8/8/8/8/8/8/R4RK1 w - - 2 2");
  });

  test("plays en passant with the exact target and capture FEN transitions", async ({
    page,
  }) => {
    await openViewerStory(page, STORY_IDS.enPassant);
    await expectFen(page, EN_PASSANT_FEN, EN_PASSANT_FEN);

    await dragWithMouse(
      page,
      piece(page, "d7"),
      page.locator('[data-square="d5"]'),
    );
    await expect(page.getByTestId("branch-san")).toHaveText("1... d5");
    await expectFen(page, EN_PASSANT_FEN, "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 2");

    await dragWithMouse(
      page,
      piece(page, "e5"),
      page.locator('[data-square="d6"]'),
    );
    await expect(page.getByTestId("branch-san")).toHaveText("1... d5 2. exd6");
    await expectFen(page, EN_PASSANT_FEN, "4k3/8/3P4/8/8/8/8/4K3 b - - 0 2");
  });

  test("commits every q/r/b/n promotion choice through the approved picker", async ({
    page,
  }) => {
    const promotions = [
      ["queen", "1. e8=Q+", "k3Q3/8/8/8/8/8/8/4K3 b - - 0 1"],
      ["rook", "1. e8=R+", "k3R3/8/8/8/8/8/8/4K3 b - - 0 1"],
      ["bishop", "1. e8=B", "k3B3/8/8/8/8/8/8/4K3 b - - 0 1"],
      ["knight", "1. e8=N", "k3N3/8/8/8/8/8/8/4K3 b - - 0 1"],
    ] as const;

    for (const [name, san, fen] of promotions) {
      await openViewerStory(page, STORY_IDS.promotion);
      await expectFen(page, PROMOTION_FEN, PROMOTION_FEN);

      await dragWithMouse(
        page,
        piece(page, "e7"),
        page.locator('[data-square="e8"]'),
      );
      await expect(
        page.getByRole("dialog", { name: "Choose a promotion piece" }),
      ).toBeVisible();
      await expectFen(page, PROMOTION_FEN, PROMOTION_FEN);

      await page.getByRole("button", { name: `Promote to ${name}` }).click();
      await expect(page.getByTestId("branch-san")).toHaveText(san);
      await expectFen(page, PROMOTION_FEN, fen);
    }
  });

  test("plays both sides from the deterministic origin through checkmate", async ({
    page,
  }) => {
    await openViewerStory(page, STORY_IDS.terminal);
    await expectFen(page, TERMINAL_FEN, TERMINAL_FEN);

    await dragWithMouse(
      page,
      piece(page, "a6"),
      page.locator('[data-square="a5"]'),
    );
    await expect(page.getByTestId("branch-san")).toHaveText("1... a5");
    await expectFen(page, TERMINAL_FEN, "7k/5Q2/6K1/p7/8/8/8/8 w - - 0 2");

    await dragWithMouse(
      page,
      piece(page, "f7"),
      page.locator('[data-square="g7"]'),
    );
    await expect(page.getByTestId("branch-san")).toHaveText("1... a5 2. Qg7#");
    await expect(page.getByTestId("branch-terminal")).toHaveText(
      "Terminal result: Checkmate",
    );
    await expectFen(page, TERMINAL_FEN, "7k/6Q1/6K1/p7/8/8/8/8 b - - 1 2");
  });
});
