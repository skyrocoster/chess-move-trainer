import { expect, test } from "@playwright/test";

const viewerLabel = "Chess board: standard starting position, White at the bottom";

test("renders the viewer route at wide and constrained sizes", async ({ page }) => {
  for (const width of [1920, 412]) {
    await page.setViewportSize({ width, height: 915 });
    await page.goto("/viewer");

    await expect(page).toHaveURL(/\/viewer$/);
    await expect(page.getByRole("heading", { name: "Position viewer", level: 1 })).toBeVisible();
    await expect(page.getByRole("img", { name: viewerLabel })).toBeVisible();
    await expect(page.locator('a[href="/viewer"]').first()).toHaveAttribute("aria-current", "page");
    await expect(page.locator('a[href="/"]').filter({ hasText: "Status" }).first()).not.toHaveAttribute(
      "aria-current",
      "page",
    );
  }
});

test("shows the in-shell Page not found state without redirecting", async ({ page }) => {
  await page.goto("/does-not-exist");

  await expect(page).toHaveURL(/\/does-not-exist$/);
  await expect(page.getByRole("heading", { name: "Page not found", level: 1 })).toBeVisible();
  await expect(page.getByText("The page you requested could not be found.")).toBeVisible();
  await expect(page.getByRole("heading", { name: "System status" })).not.toBeVisible();
});
