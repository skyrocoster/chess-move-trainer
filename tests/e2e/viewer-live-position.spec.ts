import { expect, test } from "@playwright/test";

const GAME_UUID = "0007925c-5a8d-11f0-9740-f690a301000f";
const PLY = "0";
const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

test("loads a full-corpus position and handles a missing occurrence", async ({ page }) => {
  await page.goto("/viewer");

  await page.getByLabel("Game UUID").fill(GAME_UUID);
  await page.locator("#ply").fill(PLY);
  await page.getByRole("button", { name: "Load position" }).click();

  await expect(
    page.getByRole("img", { name: `Chess board: game ${GAME_UUID}, ply 0, Black at the bottom` }),
  ).toBeVisible();
  await expect(page.getByText(GAME_UUID, { exact: true })).toBeVisible();
  await expect(page.getByText(FEN, { exact: true })).toBeVisible();
  await expect(page.getByText("Black", { exact: true }).last()).toBeVisible();

  await page.locator("#ply").fill("999999");
  await page.getByRole("button", { name: "Load position" }).click();

  await expect(page.getByText("Position not found", { exact: true })).toBeVisible();
  await expect(page.getByRole("img")).toHaveCount(0);
});
