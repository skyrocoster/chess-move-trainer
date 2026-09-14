import { expect, test } from "@playwright/test";

const OPENING_KEY = "B10:Caro-Kann Defense";
const AS_OF = "2026-09-14";
const REPRESENTATIVE_FEN =
  "rnbqkbnr/pp2pppp/8/3p4/8/1B6/PPPP1PPP/RNBQK1NR b KQkq - 0 1";

test.setTimeout(90_000);

test("retrieves live Caro-Kann training positions from shell navigation", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Trainer Practice" }).click();
  await expect(page).toHaveURL(/\/trainer$/);
  await expect(page.getByRole("heading", { name: "Trainer Practice", level: 1 })).toBeVisible();

  await page.getByLabel("Search openings").fill("Caro-Kann Defense");
  await page.getByRole("button", { name: "Search opening catalogue" }).click();

  const opening = page.locator("#trainer-practice-opening");
  await expect(page.getByRole("option", { name: "Caro-Kann Defense (B10)" })).toHaveCount(1, {
    timeout: 30_000,
  });
  await opening.selectOption({ value: OPENING_KEY });
  await page.getByLabel("Learner colour").selectOption("black");
  await page.getByLabel("as_of").fill(AS_OF);

  const requestPromise = page.waitForRequest((request) => {
    const url = new URL(request.url());
    return (
      request.method() === "GET" &&
      url.pathname === "/api/positions/training-requirements" &&
      url.searchParams.get("opening_key") === OPENING_KEY
    );
  });
  await page.getByRole("button", { name: "Retrieve training positions" }).click();

  const requestUrl = new URL((await requestPromise).url());
  expect(requestUrl.searchParams.get("as_of")).toBe(AS_OF);
  expect(requestUrl.searchParams.get("training_requirement_lt")).toBe("0");
  expect(requestUrl.searchParams.get("opening_key")).toBe(OPENING_KEY);
  expect(requestUrl.searchParams.get("opening_match")).toBe("reached");
  expect(requestUrl.searchParams.get("trainer_color")).toBe("black");
  expect(requestUrl.searchParams.get("page")).toBe("1");
  expect(requestUrl.searchParams.get("page_size")).toBe("100");

  await expect(page.getByRole("heading", { name: "training-required positions" })).toBeVisible({
    timeout: 75_000,
  });
  await expect(page.getByRole("list", { name: "training-required positions" })).toBeVisible({
    timeout: 75_000,
  });
  await expect(page.getByText(REPRESENTATIVE_FEN, { exact: true })).toBeVisible({
    timeout: 75_000,
  });
  await expect(page.getByText("g8f6", { exact: true })).toBeVisible({ timeout: 75_000 });

  await expect(page.getByRole("heading", { name: /board|session/i })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /board|session/i })).toHaveCount(0);
  await expect(page.getByRole("link", { name: /board|session/i })).toHaveCount(0);
});
