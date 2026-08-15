import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

// The shared Playwright config uses baseURL http://localhost:8444 for the
// production / browser proof. This verification-only spec targets the
// Storybook dev server (port 6006) instead, so status.spec.ts keeps its
// 8444 baseURL untouched.
test.use({ baseURL: "http://localhost:6006" });

test("renders the fully rendered Foundation Check with zero axe violations", async ({
  page,
}) => {
  await page.goto(
    "/iframe.html?id=foundation-development-only-css-check--global-and-module-css&viewMode=story",
  );

  // Await the fully rendered Foundation Check: the development-only label and
  // the static board proof section (react-chessboard in read-only mode).
  await expect(page.getByText("Development-only Foundation Check")).toBeVisible();
  await expect(page.getByText("Development-only static board proof")).toBeVisible();

  // react-chessboard 5.12.0 renders one unnamed `role="button"` draggable
  // wrapper per piece (`[aria-roledescription="draggable"]`), even in
  // read-only static mode. Those are third-party internals whose accessible
  // board contract is owned by the future MP-04 board adapter, not by MP-01's
  // temporary Foundation Check, so they are excluded here (mirroring the
  // shipped Stage 9 Vitest/axe scoping). All application-owned Foundation
  // Check content remains fully axe-checked.
  const results = await new AxeBuilder({ page })
    .exclude('[aria-roledescription="draggable"]')
    .analyze();

  expect(results.violations).toEqual([]);
});
