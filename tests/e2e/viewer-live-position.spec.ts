import { expect, test, type Page } from "@playwright/test";

const GAME_UUID = "0007925c-5a8d-11f0-9740-f690a301000f";
const SOURCE_URL = "https://www.chess.com/game/live/140399891142";
const START_BOARD_LABEL =
  "Chess board: standard starting position, White at the bottom";

async function loadGame(page: Page, ply = "") {
  await page.getByLabel("Game UUID").fill(GAME_UUID);
  await page.getByRole("textbox", { name: "Ply (optional)" }).fill(ply);
  await page.getByRole("button", { name: "Load game" }).click();
}

test("loads the full corpus game and traverses all positions in memory", async ({
  page,
}) => {
  const positionRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes(`/api/games/${GAME_UUID}/positions`)) {
      positionRequests.push(request.url());
    }
  });

  await page.goto("/viewer");
  await loadGame(page);

  await expect(
    page.getByRole("group", { name: /ply 0, Black at the bottom/ }),
  ).toBeVisible();
  await expect(page.getByText("Ply 0 of 82", { exact: true })).toBeVisible();
  await expect(
    page.getByText("Initial position", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Chess.com game" }),
  ).toHaveAttribute("href", SOURCE_URL);
  await expect(
    page.getByRole("link", { name: "Chess.com game" }),
  ).toHaveAttribute("target", "_blank");
  await expect(
    page.getByRole("textbox", { name: "Ply (optional)" }),
  ).toHaveValue("");
  expect(positionRequests).toHaveLength(1);
  expect(positionRequests[0]).not.toContain("/positions/0");

  const next = page.getByRole("button", { name: "Next" });
  await next.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByText("Ply 1 of 82", { exact: true })).toBeVisible();
  await expect(page.getByText("e4", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("textbox", { name: "Ply (optional)" }),
  ).toHaveValue("");
  expect(positionRequests).toHaveLength(1);
  expect(page.url()).toMatch(/\/viewer$/);
  await expect(next).toBeFocused();

  await page.getByRole("button", { name: "Previous" }).focus();
  await page.keyboard.press("Space");
  await expect(page.getByText("Ply 0 of 82", { exact: true })).toBeVisible();

  await next.click();
  for (let ply = 2; ply <= 82; ply += 1) {
    await next.click();
  }
  await expect(page.getByText("Ply 82 of 82", { exact: true })).toBeVisible();
  await expect(next).toBeDisabled();
  await expect(page.getByRole("button", { name: "Previous" })).toBeEnabled();
  expect(positionRequests).toHaveLength(1);

  await page.locator("form").getByRole("button", { name: "Reset" }).click();
  await expect(
    page.getByRole("img", { name: START_BOARD_LABEL }),
  ).toBeVisible();
  await expect(page.getByText("No game loaded")).toHaveCount(2);
  await expect(page.getByLabel("Game UUID")).toHaveValue("");
  await expect(
    page.getByRole("textbox", { name: "Ply (optional)" }),
  ).toHaveValue("");
  await expect(page).toHaveURL(/\/viewer$/);
});

test("loads an explicit useful initial Ply and maps typed game and position failures", async ({
  page,
}) => {
  await page.goto("/viewer");
  await loadGame(page, "41");
  await expect(page.getByText("Ply 41 of 82", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("textbox", { name: "Ply (optional)" }),
  ).toHaveValue("41");

  await page
    .getByLabel("Game UUID")
    .fill("33333333-3333-4333-8333-333333333333");
  await page.getByRole("textbox", { name: "Ply (optional)" }).fill("");
  await page.getByRole("button", { name: "Load game" }).click();
  await expect(
    page.getByRole("heading", { name: "Game not found", level: 2 }),
  ).toBeVisible();
  await expect(
    page.getByRole("group", { name: /ply 41, Black at the bottom/ }),
  ).toBeVisible();

  await page.getByLabel("Game UUID").fill(GAME_UUID);
  await page.getByRole("textbox", { name: "Ply (optional)" }).fill("999999");
  await page.getByRole("button", { name: "Load game" }).click();
  await expect(
    page.getByRole("heading", { name: "Position not found", level: 2 }),
  ).toBeVisible();
  await expect(
    page.getByRole("group", { name: /ply 41, Black at the bottom/ }),
  ).toBeVisible();
});

test("keeps the root status page and proves the per-ply URL is unavailable", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "System status" }),
  ).toBeVisible();
  await expect(page.getByRole("status")).toHaveText(/healthy/);

  const response = await page.request.get(
    `http://localhost:5666/api/games/${GAME_UUID}/positions/0`,
  );
  expect(response.status()).toBe(404);
});
