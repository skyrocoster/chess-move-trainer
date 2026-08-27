import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const STORYBOOK_ROOT = "#storybook-root";
const STORY_IDS = {
  loading: "application-analysis-analysis-panel--loading",
  missing: "application-analysis-analysis-panel--missing",
  queued: "application-analysis-analysis-panel--queued",
  running: "application-analysis-analysis-panel--running",
  complete: "application-analysis-analysis-panel--complete",
  constrainedComplete:
    "application-analysis-analysis-panel--constrained-complete",
  stale: "application-analysis-analysis-panel--stale",
  failed: "application-analysis-analysis-panel--failed",
  observationError: "application-analysis-analysis-panel--observation-error",
  actionPending: "application-analysis-analysis-panel--action-pending",
  actionError: "application-analysis-analysis-panel--action-error",
  terminalEmpty: "application-analysis-analysis-panel--terminal-empty",
} as const;

async function openStory(
  page: Page,
  storyId: string,
  width = 1280,
  height = 900,
) {
  await page.setViewportSize({ width, height });
  await page.goto(`${STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
  await expect(page.locator(STORYBOOK_ROOT)).toBeVisible();
  await expect(
    page.getByRole("heading", { level: 2, name: "Analysis" }),
  ).toBeVisible();
  // Let the Storybook a11y addon finish its own check before focused proof.
  await page.waitForTimeout(500);
}

async function checkA11y(page: Page) {
  const results = await new AxeBuilder({ page })
    .include(STORYBOOK_ROOT)
    .disableRules([
      // Storybook's iframe is not the application document and has no h1.
      "landmark-one-main",
      "page-has-heading-one",
      "region",
    ])
    .analyze();
  expect(results.violations).toEqual([]);
}

async function expectNoHorizontalOverflow(page: Page) {
  const dimensions = await page.evaluate(() => ({
    documentClientWidth: document.documentElement.clientWidth,
    documentScrollWidth: document.documentElement.scrollWidth,
    frame: (() => {
      const element = document.querySelector("main");
      return element
        ? {
            clientWidth: element.clientWidth,
            scrollWidth: element.scrollWidth,
          }
        : null;
    })(),
    panel: (() => {
      const element = document.querySelector('[class*="panel"]');
      return element
        ? {
            clientWidth: element.clientWidth,
            scrollWidth: element.scrollWidth,
          }
        : null;
    })(),
  }));

  expect(dimensions.documentScrollWidth).toBeLessThanOrEqual(
    dimensions.documentClientWidth,
  );
  expect(dimensions.frame).not.toBeNull();
  expect(dimensions.frame?.scrollWidth).toBe(dimensions.frame?.clientWidth);
  expect(dimensions.panel).not.toBeNull();
  expect(dimensions.panel?.scrollWidth).toBe(dimensions.panel?.clientWidth);
}

async function expectBestLineGeometry(page: Page) {
  const figure = page.getByRole("figure");
  const track = figure.getByRole("img", {
    name: "Win 42 percent, draw 30 percent, loss 28 percent",
  });
  await expect(track).toBeVisible();

  const segmentWidths = await track
    .locator(":scope > span")
    .evaluateAll((segments) =>
      segments.map((segment) => segment.getBoundingClientRect().width),
    );
  expect(segmentWidths).toHaveLength(3);
  const totalWidth = segmentWidths.reduce((sum, width) => sum + width, 0);
  expect(totalWidth).toBeGreaterThan(0);
  expect(segmentWidths[0] / totalWidth).toBeCloseTo(0.42, 1);
  expect(segmentWidths[1] / totalWidth).toBeCloseTo(0.3, 1);
  expect(segmentWidths[2] / totalWidth).toBeCloseTo(0.28, 1);

  await expect(figure.getByText("42.0%", { exact: true })).toBeVisible();
  await expect(figure.getByText("30.0%", { exact: true })).toBeVisible();
  await expect(figure.getByText("28.0%", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("img", {
      name: "Line 2: Win 20 percent, draw 30 percent, loss 50 percent",
    }),
  ).toBeVisible();
}

test.describe("Analysis Panel Storybook surface", () => {
  test.describe.configure({ timeout: 60_000 });

  test("covers every controlled state, semantic region, and focused axe proof", async ({
    page,
  }) => {
    const states = [
      {
        id: STORY_IDS.loading,
        status: "Loading evaluation…",
        role: "status" as const,
      },
      {
        id: STORY_IDS.missing,
        status: "Analysis available on request",
        role: "status" as const,
        note: "Analyze this displayed position deliberately",
      },
      {
        id: STORY_IDS.queued,
        status: "Analysis queued",
        role: "status" as const,
        note: "waiting for analysis",
      },
      {
        id: STORY_IDS.running,
        status: "Analysis running",
        role: "status" as const,
        note: "Analysis is in progress",
      },
      {
        id: STORY_IDS.complete,
        status: "Analysis complete",
        role: "status" as const,
      },
      {
        id: STORY_IDS.stale,
        status: "Stale analysis",
        role: "status" as const,
        note: "earlier position",
      },
      {
        id: STORY_IDS.failed,
        status: "Analysis failed",
        role: "status" as const,
        alert: "No complete result was published",
      },
      {
        id: STORY_IDS.observationError,
        status: "Evaluation unavailable",
        role: "status" as const,
        alert: "Evaluation data is unavailable",
      },
      {
        id: STORY_IDS.actionPending,
        status: "Analysis available on request",
        role: "status" as const,
      },
      {
        id: STORY_IDS.actionError,
        status: "Analysis available on request",
        role: "status" as const,
        alert: "analysis action could not be submitted",
      },
      {
        id: STORY_IDS.terminalEmpty,
        status: "Analysis complete",
        role: "status" as const,
        note: "terminal position",
      },
    ];

    for (const state of states) {
      await openStory(page, state.id);
      await expect(page.getByRole(state.role)).toHaveText(state.status);
      if (state.note) {
        await expect(page.getByRole("note")).toContainText(state.note);
      }
      if (state.alert) {
        await expect(page.getByRole("alert")).toContainText(state.alert);
      }
      await checkA11y(page);
    }

    await openStory(page, STORY_IDS.complete);
    await expect(
      page.getByRole("heading", { level: 3, name: "Best line" }),
    ).toBeVisible();
    await expect(
      page.getByText("Displayed position · ply 12 · depth 28 · 5 lines"),
    ).toBeVisible();
    await expectBestLineGeometry(page);
    await expect(
      page.getByRole("list", { name: "Ranked analysis lines" }),
    ).toBeVisible();
    await expect(page.getByRole("listitem")).toHaveCount(4);
    await expect(page.getByText("Line unavailable")).toBeVisible();
    await checkA11y(page);

    await openStory(page, STORY_IDS.terminalEmpty);
    await expect(
      page.getByText(
        "No candidate lines are available for this terminal position.",
      ),
    ).toBeVisible();
    await expect(page.getByRole("figure")).toHaveCount(0);
    await expect(
      page.getByRole("list", { name: "Ranked analysis lines" }),
    ).toHaveCount(0);
  });

  test("keeps actions deliberate, callback-safe, and visibly focused", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.missing);
    const analyze = page.getByRole("button", { name: "Analyze position" });
    await analyze.focus();
    await expect(analyze).toBeFocused();
    await analyze.click();
    await expect(analyze).toBeVisible();
    await expect(page.getByRole("status")).toHaveText(
      "Analysis available on request",
    );

    await openStory(page, STORY_IDS.stale);
    const update = page.getByRole("button", { name: "Update analysis" });
    await update.focus();
    await expect(update).toBeFocused();
    await update.click();
    await expect(page.getByRole("status")).toHaveText("Stale analysis");

    await openStory(page, STORY_IDS.failed);
    const retry = page.getByRole("button", { name: "Retry analysis" });
    await retry.focus();
    await expect(retry).toBeFocused();
    await retry.click();
    await expect(page.getByRole("status")).toHaveText("Analysis failed");

    await openStory(page, STORY_IDS.observationError);
    const retryObservation = page.getByRole("button", {
      name: "Retry observation",
    });
    await retryObservation.focus();
    await expect(retryObservation).toBeFocused();
    await retryObservation.click();
    await expect(page.getByRole("status")).toHaveText("Evaluation unavailable");

    await openStory(page, STORY_IDS.actionPending);
    await expect(
      page.getByRole("button", { name: "Analyze position" }),
    ).toBeDisabled();
  });

  test("keeps the approved panel geometry bounded at 320, 480, and 640px", async ({
    page,
  }) => {
    await openStory(page, STORY_IDS.constrainedComplete);
    const frame = page.getByTestId("analysis-panel-constrained-frame");
    const panel = page.locator('[class*="panel"]').first();

    for (const width of [320, 480, 640]) {
      await frame.evaluate((element, nextWidth) => {
        (element as HTMLElement).style.inlineSize = `${nextWidth}px`;
      }, width);
      await expect
        .poll(() => frame.evaluate((element) => element.clientWidth))
        .toBe(width);
      await expectNoHorizontalOverflow(page);
      await expect(panel).toBeVisible();
    }

    const actions = page.locator('[class*="actions"]').first();
    const actionButton = page.getByRole("button", { name: "Update analysis" });
    const actionsWidth = await actions.evaluate(
      (element) => element.clientWidth,
    );
    const buttonWidth = (await actionButton.boundingBox())?.width ?? 0;
    expect(Math.abs(buttonWidth - actionsWidth)).toBeLessThanOrEqual(1);
    await expectBestLineGeometry(page);
  });

  test("proves reduced-motion and forced-colors-safe presentation", async ({
    page,
  }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await openStory(page, STORY_IDS.constrainedComplete);
    expect(
      await page.evaluate(
        () => window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      ),
    ).toBe(true);

    const motionDurations = await page
      .locator('[class*="panel"], [class*="panel"] *')
      .evaluateAll((elements) =>
        elements.map((element) => {
          const style = getComputedStyle(element);
          return [style.transitionDuration, style.animationDuration];
        }),
      );
    const durationMs = (duration: string) =>
      duration.endsWith("ms")
        ? Number.parseFloat(duration)
        : Number.parseFloat(duration) * 1000;
    expect(
      motionDurations.every(([transition, animation]) =>
        [transition, animation].every(
          (duration) => durationMs(duration) <= 0.01,
        ),
      ),
    ).toBe(true);
    await expectNoHorizontalOverflow(page);

    await page.emulateMedia({ forcedColors: "active" });
    await openStory(page, STORY_IDS.constrainedComplete);
    expect(
      await page.evaluate(
        () => window.matchMedia("(forced-colors: active)").matches,
      ),
    ).toBe(true);
    const panel = page.locator('[class*="panel"]').first();
    await expect(panel).toHaveCSS("box-shadow", "none");
    const forcedColors = await panel.evaluate((element) => {
      const style = getComputedStyle(element);
      return {
        background: style.backgroundColor,
        border: style.borderTopColor,
      };
    });
    expect(forcedColors.background).not.toBe("rgba(0, 0, 0, 0)");
    expect(forcedColors.border).not.toBe("rgba(0, 0, 0, 0)");
    await expectBestLineGeometry(page);
    await checkA11y(page);
  });
});
