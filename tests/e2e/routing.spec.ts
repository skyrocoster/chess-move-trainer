import { expect, test } from "@playwright/test";

test("keeps /viewer as ordinary in-shell Not Found in the approved shell", async ({
  page,
}) => {
  await page.setViewportSize({ width: 680, height: 915 });
  await page.goto("/viewer");

  await expect(page).toHaveURL(/\/viewer$/);
  await expect(page.getByRole("heading", { name: "Page not found", level: 1 })).toBeVisible();
  await expect(
    page.getByText("The page you requested could not be found."),
  ).toBeVisible();

  await expect(page.getByText("Chess Move Trainer", { exact: true })).toBeVisible();
  await expect(page.getByRole("complementary", { name: "Primary navigation" })).toBeVisible();
  await expect(page.getByRole("main")).toBeVisible();

  await expect(page.getByRole("heading", { name: "System status" })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Position viewer" })).toHaveCount(0);
  await expect(page.getByRole("link", { name: "Viewer" })).toHaveCount(0);
  await expect(page.locator('a[href="/viewer"]')).toHaveCount(0);
});
