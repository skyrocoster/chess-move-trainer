import { expect, test, type Page } from "@playwright/test";

const desktopWidths = [1920, 680];
const constrainedWidths = [412, 679];

async function openProduction(page: Page, width: number) {
  await page.setViewportSize({ width, height: 915 });
  await page.goto("/");
  await expect(page).toHaveURL(/\/$/);
  await expect(
    page.getByText("Chess Move Trainer", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "System status" }),
  ).toBeVisible();
  const statusLink = page
    .locator('a[href="/"]')
    .filter({ hasText: "Status" })
    .first();
  await expect(statusLink).toHaveAttribute("href", "/");
  await expect(statusLink).toHaveAttribute("aria-current", "page");
  const viewerLink = page
    .locator('a[href="/viewer"]')
    .filter({ hasText: "Viewer" })
    .first();
  await expect(viewerLink).toHaveAttribute("href", "/viewer");
  await expect(viewerLink).not.toHaveAttribute("aria-current", "page");
}

async function expectNoHorizontalOverflow(page: Page) {
  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));

  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.clientWidth);
}

test("uses the approved shell at desktop and breakpoint widths", async ({
  page,
}) => {
  for (const width of desktopWidths) {
    await openProduction(page, width);
    await expect(
      page.getByRole("complementary", { name: "Primary navigation" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Open navigation menu" }),
    ).toBeHidden();
    await expect(page.locator("main")).toHaveCSS("padding-left", "24px");
  }

  for (const width of constrainedWidths) {
    await openProduction(page, width);
    await expect(
      page.getByRole("complementary", { name: "Primary navigation" }),
    ).toBeHidden();
    await expect(
      page.getByRole("button", { name: "Open navigation menu" }),
    ).toBeVisible();
    await expect(page.locator("main")).toHaveCSS("padding-left", "16px");
  }
});

test("keeps the Repertoire Builder route usable across desktop and constrained widths", async ({
  page,
}) => {
  for (const width of desktopWidths) {
    await page.setViewportSize({ width, height: 915 });
    await page.goto("/repertoire");
    await expect(page).toHaveURL(/\/repertoire$/);
    await expect(
      page.getByRole("heading", { name: "Repertoire Builder", level: 1 }),
    ).toBeVisible({ timeout: 10_000 });
    await expect(
      page.getByRole("group", {
        name: "Chess board: standard starting position, White at the bottom",
      }),
    ).toBeVisible();
    await expect(
      page.getByRole("complementary", { name: "Primary navigation" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Open navigation menu" }),
    ).toBeHidden();
    await expect(
      page
        .locator('a[href="/repertoire"]')
        .filter({ hasText: "Repertoire Builder" })
        .first(),
    ).toHaveAttribute("aria-current", "page");
    await expectNoHorizontalOverflow(page);
  }

  for (const width of constrainedWidths) {
    await page.setViewportSize({ width, height: 915 });
    await page.goto("/repertoire");
    await expect(page).toHaveURL(/\/repertoire$/);
    await expect(
      page.getByRole("heading", { name: "Repertoire Builder", level: 1 }),
    ).toBeVisible({ timeout: 10_000 });
    await expect(
      page.getByRole("group", {
        name: "Chess board: standard starting position, White at the bottom",
      }),
    ).toBeVisible();
    await expect(
      page.getByRole("complementary", { name: "Primary navigation" }),
    ).toBeHidden();
    await expect(
      page.getByRole("button", { name: "Open navigation menu" }),
    ).toBeVisible();

    const trigger = page.getByRole("button", { name: "Open navigation menu" });
    await trigger.click();
    const drawer = page.getByRole("dialog");
    const repertoireLink = drawer.getByRole("link", {
      name: "Repertoire Builder",
    });
    await expect(repertoireLink).toHaveAttribute("aria-current", "page");
    await repertoireLink.click();
    await expect(page).toHaveURL(/\/repertoire$/);
    await expect(drawer).toBeHidden();
    await expectNoHorizontalOverflow(page);
  }
});

test("supports drawer focus containment and every required dismissal path", async ({
  page,
}) => {
  await openProduction(page, 412);
  const trigger = page.getByRole("button", { name: "Open navigation menu" });

  await trigger.click();
  const drawer = page.getByRole("dialog");
  const close = drawer.getByRole("button", { name: "Close navigation menu" });
  const status = drawer.getByRole("link", { name: "Status" });
  const viewer = drawer.getByRole("link", { name: "Viewer" });
  const repertoire = drawer.getByRole("link", { name: "Repertoire Builder" });
  await expect(drawer).toBeVisible();
  await expect(
    drawer.getByRole("heading", { name: "Navigation" }),
  ).toBeVisible();
  await expect(close).toBeFocused();
  await expect(viewer).toHaveAttribute("href", "/viewer");
  await expect(repertoire).toHaveAttribute("href", "/repertoire");

  await page.keyboard.press("Tab");
  await expect(status).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(viewer).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(repertoire).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(close).toBeFocused();

  await close.click();
  await expect(drawer).toBeHidden();
  await expect(trigger).toBeFocused();

  await trigger.click();
  await page.keyboard.press("Escape");
  await expect(drawer).toBeHidden();
  await expect(trigger).toBeFocused();

  await trigger.click();
  await page
    .locator('[data-testid="drawer-backdrop"]')
    .click({ position: { x: 380, y: 450 } });
  await expect(drawer).toBeHidden();
  await expect(trigger).toBeFocused();

  await trigger.click();
  await status.click();
  await expect(page).toHaveURL(/\/$/);
  await expect(drawer).toBeHidden();
});

test("removes shell motion when reduced motion is requested", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await openProduction(page, 412);
  await page.getByRole("button", { name: "Open navigation menu" }).click();

  await expect(page.locator('[data-testid="drawer-backdrop"]')).toHaveCSS(
    "transition-duration",
    "0s",
  );
  await expect(page.getByRole("dialog")).toHaveCSS("transition-duration", "0s");
});

test("keeps the shell available for an unavailable backend", async ({
  page,
}) => {
  await page.route("**/api/health", (route) =>
    route.abort("connectionrefused"),
  );
  await page.setViewportSize({ width: 680, height: 915 });
  await page.goto("/");

  await expect(
    page.getByText("Chess Move Trainer", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "System status" }),
  ).toBeVisible();
  await expect(page.getByRole("alert")).toContainText("Backend unavailable");
  await expect(
    page.getByRole("link", { name: "Status" }).first(),
  ).toHaveAttribute("href", "/");
  await expect(page.locator('a[href="/viewer"]')).toHaveCount(1);
});

test("closes the drawer when Viewer is selected", async ({ page }) => {
  await openProduction(page, 412);
  const trigger = page.getByRole("button", { name: "Open navigation menu" });

  await trigger.click();
  const drawer = page.getByRole("dialog");
  await drawer.getByRole("link", { name: "Viewer" }).click();

  await expect(page).toHaveURL(/\/viewer$/);
  await expect(drawer).toBeHidden();
  await expect(
    page.getByRole("heading", { name: "Position viewer" }),
  ).toBeVisible();
});
