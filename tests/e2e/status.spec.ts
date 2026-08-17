import { expect, test } from "@playwright/test";

test("shows the live backend health status", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Chess Move Trainer", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "System status" })).toBeVisible();
  await expect(page.getByRole("status")).toHaveText(/healthy/);
});

test("shows an accessible unavailable state", async ({ page }) => {
  await page.route("**/api/health", (route) => route.abort("connectionrefused"));
  await page.goto("/");
  await expect(page.getByRole("alert")).toContainText("Backend unavailable");
});
