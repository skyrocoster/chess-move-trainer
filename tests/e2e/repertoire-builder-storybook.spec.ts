import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const STORYBOOK_URL = "http://127.0.0.1:6006";
const STORYBOOK_ROOT = "#storybook-root";
const GAME_UUID = "0007925c-5a8d-11f0-9740-f690a301000f";
const STORY_IDS = {
  wide: "application-repertoire-builder-workspace--wide",
  medium: "application-repertoire-builder-workspace--medium",
  constrained: "application-repertoire-builder-workspace--constrained",
  stagedMy: "application-repertoire-builder-workspace--staged-my",
  storedPrefix: "application-repertoire-builder-workspace--stored-prefix-black-subject",
  opponent: "application-repertoire-builder-workspace--opponent-immediate",
  navigation: "application-repertoire-builder-workspace--navigation-and-replacement",
  flip: "application-repertoire-builder-workspace--flip-cancellation",
  promotion: "application-repertoire-builder-workspace--promotion-preferred",
  zeroPersonal: "application-repertoire-builder-workspace--zero-personal-count",
  absent: "application-repertoire-builder-workspace--absent-unsavable",
  savedChoiceStages: "application-repertoire-builder-workspace--saved-choice-stages-move",
  savedNoStage: "application-repertoire-builder-workspace--saved-no-stage",
  firstChoice: "application-repertoire-builder-workspace--first-choice",
  replacement: "application-repertoire-builder-workspace--replacement-constrained",
  matching: "application-repertoire-builder-workspace--matching",
  savedBoxKeyboard: "application-repertoire-builder-workspace--saved-box-keyboard",
  saveReplacement: "application-repertoire-builder-workspace--save-replacement",
  removeRetainsStaging: "application-repertoire-builder-workspace--remove-retains-staging",
  pendingSave: "application-repertoire-builder-workspace--pending-save",
  pendingRemove: "application-repertoire-builder-workspace--pending-remove",
  saveFailure: "application-repertoire-builder-workspace--save-failure-retention",
  removeFailure: "application-repertoire-builder-workspace--remove-failure-retention",
  accessibility: "application-repertoire-builder-workspace--accessibility-and-responsive",
  readErrors: "application-repertoire-builder-workspace--read-errors",
  unsavable: "application-repertoire-builder-workspace--unsavable-gate",
  responseDistribution: "application-repertoire-builder-workspace--response-distribution-integration",
  responseDistributionDense:
    "application-move-response-distribution--dense-tiny-sector-cluster",
  loading: "application-repertoire-builder-workspace--loading-gate",
  opponentGate: "application-repertoire-builder-workspace--opponent-turn-gate",
  opponentLocal: "application-repertoire-builder-workspace--opponent-local-only",
  boundary699: "application-repertoire-builder-responsive-stage--boundary-699",
  boundary700: "application-repertoire-builder-responsive-stage--boundary-700",
  boundary1039: "application-repertoire-builder-responsive-stage--boundary-1039",
  boundary1040: "application-repertoire-builder-responsive-stage--boundary-1040",
} as const;
const GEOMETRY_TOLERANCE = 4;

type LayoutBounds = {
  x: number;
  y: number;
  width: number;
  height: number;
};

async function openStory(
  page: Page,
  storyId: string,
  width = 1280,
  height = 900,
  expectWorkspaceHeading = true,
) {
  await page.setViewportSize({ width, height });
  await page.goto(`${STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
  await expect(page.locator(STORYBOOK_ROOT)).toBeVisible({ timeout: 30_000 });
  if (expectWorkspaceHeading) {
    await expect(
      page.getByRole("heading", { name: "Repertoire Builder", level: 1 }),
    ).toBeVisible({ timeout: 30_000 });
  }
}

function preferredPanel(page: Page) {
  return page
    .getByTestId("repertoire-session-lane")
    .getByRole("region", { name: "What is saved, and what is staged?" });
}

function responsiveStage(page: Page) {
  return page.getByTestId("repertoire-workspace-stage");
}

async function expectResponsiveComposition(
  page: Page,
  mode: "wide" | "medium" | "narrow",
  separatorLabels: readonly string[],
  expectProductionGrouping = true,
) {
  const stage = responsiveStage(page);
  await expect(stage).toHaveAttribute("data-layout-mode", mode);
  const lanes = stage.locator("[data-lane]");
  await expect(lanes).toHaveCount(3);
  await expect
    .poll(() => lanes.evaluateAll((elements) => elements.map((element) => element.dataset.lane)))
    .toEqual(["board", "session", "engine"]);

  const separators = stage.getByRole("separator");
  await expect(separators).toHaveCount(separatorLabels.length);
  for (const [index, label] of separatorLabels.entries()) {
    await expect(separators.nth(index)).toHaveAccessibleName(label);
  }

  if (mode === "medium" && expectProductionGrouping) {
    const boardRow = page.getByTestId("repertoire-responsive-board-row");
    const lowerGroup = page.getByTestId("repertoire-responsive-medium-group");
    await expect(boardRow.locator('[data-testid="repertoire-board-lane"]')).toHaveCount(1);
    await expect(lowerGroup.locator('[data-testid="repertoire-session-lane"]')).toHaveCount(1);
    await expect(lowerGroup.locator('[data-testid="repertoire-engine-lane"]')).toHaveCount(1);
    await expect(lowerGroup.locator('[data-testid="repertoire-board-lane"]')).toHaveCount(0);

    const [stageBounds, boardRowBounds] = await Promise.all([stage.boundingBox(), boardRow.boundingBox()]);
    if (!stageBounds || !boardRowBounds) throw new Error("Medium lane bounds are missing.");
    expect(boardRowBounds.x).toBeCloseTo(stageBounds.x, 0);
    expect(boardRowBounds.width).toBeCloseTo(stageBounds.width, 0);
  }

  if (mode === "narrow") {
    await expect(stage.getByRole("separator")).toHaveCount(0);
  }

  if (!expectProductionGrouping) return;

  const boardLane = page.getByTestId("repertoire-board-lane");
  const sessionLane = page.getByTestId("repertoire-session-lane");
  const engineLane = page.getByTestId("repertoire-engine-lane");
  const boardEvalStage = boardLane.getByTestId("board-eval-stage");
  const boardControls = boardLane.getByRole("toolbar", { name: "Board controls" });
  const moveHistory = boardLane.getByTestId("board-move-history");
  const [boardBounds, sessionBounds, engineBounds, boardEvalBounds, controlsBounds, historyBounds] =
    await Promise.all([
      boardLane.boundingBox(),
      sessionLane.boundingBox(),
      engineLane.boundingBox(),
      boardEvalStage.boundingBox(),
      boardControls.boundingBox(),
      moveHistory.boundingBox(),
    ]);
  if (!boardBounds || !sessionBounds || !engineBounds || !boardEvalBounds || !controlsBounds || !historyBounds) {
    throw new Error(`Missing ${mode} composition bounds.`);
  }

  if (mode === "wide") {
    expect(boardBounds.x + boardBounds.width).toBeLessThanOrEqual(sessionBounds.x + GEOMETRY_TOLERANCE);
    expect(sessionBounds.x + sessionBounds.width).toBeLessThanOrEqual(engineBounds.x + GEOMETRY_TOLERANCE);
  }

  if (mode === "medium") {
    const boardRowBounds = await page.getByTestId("repertoire-responsive-board-row").boundingBox();
    if (!boardRowBounds) throw new Error("Missing medium Board row bounds.");
    expect(boardRowBounds.y + boardRowBounds.height).toBeLessThanOrEqual(sessionBounds.y + GEOMETRY_TOLERANCE);
    expect(boardRowBounds.y + boardRowBounds.height).toBeLessThanOrEqual(engineBounds.y + GEOMETRY_TOLERANCE);
    expect(sessionBounds.x + sessionBounds.width).toBeLessThanOrEqual(engineBounds.x + GEOMETRY_TOLERANCE);
  }

  if (mode === "narrow") {
    expect(boardBounds.y + boardBounds.height).toBeLessThanOrEqual(sessionBounds.y + GEOMETRY_TOLERANCE);
    expect(sessionBounds.y + sessionBounds.height).toBeLessThanOrEqual(engineBounds.y + GEOMETRY_TOLERANCE);
  }

  expect(boardEvalBounds.y + boardEvalBounds.height).toBeLessThanOrEqual(controlsBounds.y + GEOMETRY_TOLERANCE);
  expect(controlsBounds.y + controlsBounds.height).toBeLessThanOrEqual(historyBounds.y + GEOMETRY_TOLERANCE);

  const formatBounds = (bounds: LayoutBounds) =>
    `x=${bounds.x.toFixed(1)},y=${bounds.y.toFixed(1)},w=${bounds.width.toFixed(1)},h=${bounds.height.toFixed(1)}`;
  console.info(
    `[geometry:${mode}] Board ${formatBounds(boardBounds)}; Session ${formatBounds(sessionBounds)}; ` +
      `Engine ${formatBounds(engineBounds)}; Board/eval ${formatBounds(boardEvalBounds)}; ` +
      `Controls ${formatBounds(controlsBounds)}; MoveHistory ${formatBounds(historyBounds)}`,
  );
}

async function expectPreferredRelationship(
  page: Page,
  state: "empty" | "first-choice" | "saved" | "replacement" | "matching" | "unknown",
) {
  await expect(preferredPanel(page)).toHaveAttribute("data-state", state);
}

async function expectPreferredActions(page: Page, actions: readonly string[]) {
  const actual = (await preferredPanel(page).getByRole("button").allTextContents()).filter((label) =>
    ["Save", "Change effective date", "Remove"].includes(label.trim()),
  );
  expect(actual.map((label) => label.trim())).toEqual(actions);
}

async function expectDeferredDate(page: Page, requests?: string[]) {
  const date = preferredPanel(page).getByRole("button", { name: "Change effective date" });
  const requestCount = requests?.length;
  await expect(date).toBeDisabled();
  await expect(date).toHaveAccessibleDescription("Date changes are temporarily unavailable");
  await date.evaluate((element) => (element as HTMLButtonElement).click());
  await expect(page.getByTestId("calendar-date-popup")).toHaveCount(0);
  if (requestCount !== undefined) expect(requests).toHaveLength(requestCount);
}

async function expectBothRelationshipBoxes(page: Page) {
  await expect(preferredPanel(page).getByTestId("saved-move")).toBeVisible();
  await expect(preferredPanel(page).getByTestId("staged-move")).toBeVisible();
  await expect(preferredPanel(page).getByText("Current saved choice", { exact: true })).toBeVisible();
  await expect(preferredPanel(page).getByText("Staged move", { exact: true })).toBeVisible();
}

async function expectSessionHistory(page: Page, entries: readonly string[]) {
  const history = page.getByTestId("repertoire-board-lane").getByTestId("board-move-history");
  await expect(history).toBeVisible();
  const buttons = history.getByRole("button");
  await expect(buttons).toHaveCount(entries.length);
  for (const [index, name] of entries.entries()) {
    await expect(buttons.nth(index)).toHaveAccessibleName(name);
  }
}

async function expectActiveSessionHistoryEntry(page: Page, name: string) {
  await expect(
    page.getByTestId("repertoire-board-lane").getByTestId("board-move-history").getByRole("button", { name }),
  ).toHaveAttribute("aria-current", "step");
}

async function sharedPositionSummary(page: Page) {
  const row = page.getByTestId("repertoire-session-lane").getByTestId("position-description-row");
  const description = row.getByRole("button", { name: "Position description" });
  await expect(description).toHaveAttribute("aria-expanded", "true");
  const summary = row.locator("[data-position-summary]");
  await expect(summary).toBeVisible();
  return summary;
}

async function expectPositionSquares(page: Page, square: string, count: number) {
  await expect((await sharedPositionSummary(page)).locator(`[data-position-square="${square}"]`)).toHaveCount(count);
}

async function expectNoHorizontalOverflow(page: Page) {
  const dimensions = await page.evaluate(() => ({
    documentClientWidth: document.documentElement.clientWidth,
    documentScrollWidth: document.documentElement.scrollWidth,
    bodyClientWidth: document.body.clientWidth,
    bodyScrollWidth: document.body.scrollWidth,
  }));
  expect(dimensions.documentScrollWidth).toBeLessThanOrEqual(dimensions.documentClientWidth);
  expect(dimensions.bodyScrollWidth).toBeLessThanOrEqual(dimensions.bodyClientWidth);
}

type DistributionLabelBox = {
  text: string;
  left: number;
  right: number;
  top: number;
  bottom: number;
};

async function expectDistributionChartAndControlsClean(page: Page) {
  const distribution = page.getByTestId("move-response-distribution");
  const observations = await distribution.evaluate((element) => {
    const chart = element.querySelector<HTMLElement>(
      '[data-testid="move-response-distribution-chart"]',
    );
    if (!chart) throw new Error("Distribution chart frame is missing.");
    const chartBox = chart.getBoundingClientRect();
    const labels: DistributionLabelBox[] = Array.from(
      element.querySelectorAll<SVGTextElement>("svg text"),
    ).map((text) => {
      const box = text.getBoundingClientRect();
      return {
        text: text.textContent ?? "",
        left: box.left,
        right: box.right,
        top: box.top,
        bottom: box.bottom,
      };
    });
    const sans = Array.from(
      element.querySelectorAll<HTMLElement>('[class*="replySan"]'),
    ).map((san) => {
      const style = getComputedStyle(san);
      return {
        text: san.textContent ?? "",
        whiteSpace: style.whiteSpace,
        height: san.getBoundingClientRect().height,
        lineHeight: Number.parseFloat(style.lineHeight),
      };
    });
    return { chartBox, labels, sans };
  });

  expect(observations.labels.length).toBeGreaterThan(0);
  for (const label of observations.labels) {
    expect(label.text).not.toBe("");
    expect(
      label.left,
      `label "${label.text}" crosses the chart frame's left edge`,
    ).toBeGreaterThanOrEqual(observations.chartBox.left - 1);
    expect(
      label.right,
      `label "${label.text}" crosses the chart frame's right edge`,
    ).toBeLessThanOrEqual(observations.chartBox.right + 1);
  }
  for (let first = 0; first < observations.labels.length; first += 1) {
    for (let second = first + 1; second < observations.labels.length; second += 1) {
      const a = observations.labels[first]!;
      const b = observations.labels[second]!;
      const overlaps =
        a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
      expect(overlaps, `pie labels "${a.text}" and "${b.text}" overlap`).toBe(false);
    }
  }
  for (const san of observations.sans) {
    expect(san.whiteSpace, `SAN "${san.text}" lost nowrap protection`).toBe("nowrap");
    expect(
      san.height,
      `SAN "${san.text}" wrapped across lines`,
    ).toBeLessThanOrEqual(san.lineHeight * 1.5 + 1);
  }
}

async function expectPreferredPanelFidelity(page: Page, expectStacked: boolean) {
  const panel = preferredPanel(page);
  const saved = panel.getByTestId("saved-move");
  const staged = panel.getByTestId("staged-move");
  const connector = saved.locator("xpath=following-sibling::*[1]");
  const connectorNext = connector.locator("xpath=following-sibling::*[1]");
  const consequence = panel.getByTestId("preferred-consequence");

  await expect(panel.getByText("Current saved choice", { exact: true })).toHaveCount(1);
  await expect(panel.getByText("Staged move", { exact: true })).toHaveCount(1);
  await expect(saved).toBeVisible();
  await expect(staged).toBeVisible();
  await expect(
    panel.getByRole("button", {
      name: "Current saved choice: e4; play and stage this move.",
    }),
  ).toBeVisible();

  await expect(connector).toHaveAttribute("aria-hidden", "true");
  await expect(connectorNext).toHaveAttribute("data-testid", "staged-move");
  await expect(connector.locator("svg")).toHaveAttribute("aria-hidden", "true");
  await expect(connector.locator("svg")).toHaveAttribute("focusable", "false");
  await expect(consequence.locator("svg")).toHaveAttribute("aria-hidden", "true");
  await expect(consequence.locator("svg")).toHaveAttribute("focusable", "false");

  const cueStyle = await consequence.locator("svg").evaluate((element) => {
    const style = getComputedStyle(element);
    return { borderRadius: style.borderRadius, height: style.height, width: style.width };
  });
  expect(cueStyle.borderRadius).toBe("50%");
  expect(cueStyle.width).toBe(cueStyle.height);

  const [savedBox, connectorBox, stagedBox] = await Promise.all([
    saved.boundingBox(),
    connector.boundingBox(),
    staged.boundingBox(),
  ]);
  if (!savedBox || !connectorBox || !stagedBox) {
    throw new Error("Preferred move relationship boxes are missing layout bounds.");
  }
  if (expectStacked) {
    expect(savedBox.y + savedBox.height).toBeLessThanOrEqual(connectorBox.y + 1);
    expect(connectorBox.y + connectorBox.height).toBeLessThanOrEqual(stagedBox.y + 1);
    await expect(connector.locator("svg")).toHaveCSS(
      "transform",
      "matrix(0, 1, -1, 0, 0, 0)",
    );
  } else {
    expect(savedBox.x + savedBox.width).toBeLessThanOrEqual(connectorBox.x + 1);
    expect(connectorBox.x + connectorBox.width).toBeLessThanOrEqual(stagedBox.x + 1);
  }

  const panelBounds = await panel.boundingBox();
  if (!panelBounds) throw new Error("Preferred move panel bounds are missing.");
  const actionButtons = ["Save", "Change effective date", "Remove"].map((name) =>
    panel.getByRole("button", { name, exact: true }),
  );
  const actionBounds = await Promise.all(actionButtons.map((button) => button.boundingBox()));
  for (const bounds of actionBounds) {
    if (!bounds) throw new Error("A preferred move action is missing layout bounds.");
    expect(bounds.x).toBeGreaterThanOrEqual(panelBounds.x);
    expect(bounds.x + bounds.width).toBeLessThanOrEqual(panelBounds.x + panelBounds.width + 1);
  }
  const actionRows = new Set(actionBounds.map((bounds) => Math.round(bounds!.y)));
  if (expectStacked) expect(actionRows.size).toBeGreaterThan(1);

  const panelDimensions = await panel.evaluate((element) => ({
    clientWidth: element.clientWidth,
    scrollWidth: element.scrollWidth,
  }));
  expect(panelDimensions.scrollWidth).toBeLessThanOrEqual(panelDimensions.clientWidth);
}

async function checkA11y(page: Page) {
  for (let attempt = 0; attempt < 4; attempt += 1) {
    try {
      const results = await new AxeBuilder({ page })
        .include(STORYBOOK_ROOT)
        .disableRules(["landmark-one-main", "page-has-heading-one", "region"])
        .analyze();
      expect(results.violations).toEqual([]);
      return;
    } catch (error) {
      if (!(error instanceof Error) || !error.message.includes("Axe is already running")) {
        throw error;
      }
      await page.waitForTimeout(250);
    }
  }
  throw new Error("Axe accessibility scan remained busy after bounded retries.");
}

async function panelBounds(page: Page) {
  return page.getByTestId("repertoire-workspace-stage").locator("[data-panel]").evaluateAll((panels) =>
    panels.map((panel) => {
      const bounds = panel.getBoundingClientRect();
      return { width: bounds.width, height: bounds.height, id: panel.id };
    }),
  );
}

function expectPanelMinimums(
  panels: readonly { width: number }[],
  minimums: readonly number[],
) {
  expect(panels).toHaveLength(minimums.length);
  for (const [index, minimum] of minimums.entries()) {
    expect(panels[index]!.width).toBeGreaterThanOrEqual(minimum - 1);
  }
}

function preferredRequestUrls(page: Page) {
  const urls: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/preferred-move")) urls.push(request.url());
  });
  return urls;
}

test.describe("Repertoire Builder Storybook surface", () => {
  test.describe.configure({ timeout: 30_000 });

  test("proves empty relationship boxes, session boundaries, and 412px composition", async ({ page }) => {
    await openStory(page, STORY_IDS.wide);
    await expectResponsiveComposition(page, "wide", [
      "Board and Session boundary",
      "Session and Engine boundary",
    ]);
    await expectPreferredRelationship(page, "empty");
    await expectBothRelationshipBoxes(page);
    await expect(preferredPanel(page).getByText("No saved choice yet.")).toBeVisible();
    await expect(preferredPanel(page).getByText("No move staged.")).toBeVisible();
    await expect(
      preferredPanel(page).getByText("Stage a legal move to propose the first saved choice."),
    ).toBeVisible();
    await expectPreferredActions(page, []);
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);

    await openStory(page, STORY_IDS.constrained, 412, 915);
    await expectResponsiveComposition(page, "narrow", []);
    await expectPreferredRelationship(page, "empty");
    await expectBothRelationshipBoxes(page);
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });

  test("prepares representative wide, medium, and narrow browser evidence", async ({ page }, testInfo) => {
    const cases = [
      { id: STORY_IDS.wide, mode: "wide" as const, width: 1280, labels: ["Board and Session boundary", "Session and Engine boundary"] },
      { id: STORY_IDS.medium, mode: "medium" as const, width: 800, labels: ["Session and Engine boundary"] },
      { id: STORY_IDS.constrained, mode: "narrow" as const, width: 412, labels: [] },
    ];

    for (const entry of cases) {
      await openStory(page, entry.id, entry.width, 1000);
      await expectResponsiveComposition(page, entry.mode, entry.labels);
      await expectNoHorizontalOverflow(page);
      await page.screenshot({
        path: testInfo.outputPath(`repertoire-responsive-${entry.mode}.png`),
        fullPage: true,
      });
    }
  });

  test("proves exact container-width boundary transitions", async ({ page }) => {
    const cases = [
      [STORY_IDS.boundary699, "narrow", 0],
      [STORY_IDS.boundary700, "medium", 1],
      [STORY_IDS.boundary1039, "medium", 1],
      [STORY_IDS.boundary1040, "wide", 2],
    ] as const;

    for (const [storyId, mode, separatorCount] of cases) {
      await openStory(page, storyId, 1200, 900, false);
      await expectResponsiveComposition(
        page,
        mode,
        mode === "wide"
          ? ["Board and Session boundary", "Session and Engine boundary"]
          : mode === "medium"
            ? ["Session and Engine boundary"]
            : [],
        false,
      );
      await expect(responsiveStage(page).getByRole("separator")).toHaveCount(separatorCount);
      await expectNoHorizontalOverflow(page);
    }
  });

  test("proves keyboard resizing, focus, minimums, fixed bounds, and reset", async ({ page }) => {
    await openStory(page, STORY_IDS.wide, 1280, 1000);
    await expectResponsiveComposition(page, "wide", [
      "Board and Session boundary",
      "Session and Engine boundary",
    ]);

    const stage = responsiveStage(page);
    const initialStageBounds = await stage.boundingBox();
    const initialPanels = await panelBounds(page);
    if (!initialStageBounds) throw new Error("Stage bounds are missing before resize.");
    expectPanelMinimums(initialPanels, [320, 280, 360]);

    const firstSeparator = stage.getByRole("separator", { name: "Board and Session boundary" });
    await firstSeparator.focus();
    await expect(firstSeparator).toBeFocused();
    await page.keyboard.press("ArrowRight");
    await expect
      .poll(async () => (await panelBounds(page)).map((panel) => Math.round(panel.width)))
      .not.toEqual(initialPanels.map((panel) => Math.round(panel.width)));

    for (let index = 0; index < 80; index += 1) {
      await page.keyboard.press("ArrowLeft");
    }
    expectPanelMinimums(await panelBounds(page), [320, 280, 360]);

    const secondSeparator = stage.getByRole("separator", { name: "Session and Engine boundary" });
    await secondSeparator.focus();
    for (let index = 0; index < 80; index += 1) {
      await page.keyboard.press("ArrowRight");
    }
    expectPanelMinimums(await panelBounds(page), [320, 280, 360]);

    const finalStageBounds = await stage.boundingBox();
    if (!finalStageBounds) throw new Error("Stage bounds are missing after resize.");
    expect(finalStageBounds.x).toBeCloseTo(initialStageBounds.x, 0);
    expect(finalStageBounds.width).toBeCloseTo(initialStageBounds.width, 0);

    await page.getByRole("button", { name: "Reset panel layout" }).click();
    await expect
      .poll(async () => (await panelBounds(page)).map((panel) => Math.round(panel.width)))
      .toEqual(initialPanels.map((panel) => Math.round(panel.width)));
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });

  test("retains separator semantics in forced-colors and reduced-motion modes", async ({ page }) => {
    await page.emulateMedia({ forcedColors: "active", reducedMotion: "reduce" });
    await openStory(page, STORY_IDS.medium, 800, 1000);
    await expectResponsiveComposition(page, "medium", ["Session and Engine boundary"]);
    await expect(page.getByRole("separator", { name: "Session and Engine boundary" })).toBeVisible();

    const media = await page.evaluate(() => ({
      forcedColors: window.matchMedia("(forced-colors: active)").matches,
      reducedMotion: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    }));
    expect(media).toEqual({ forcedColors: true, reducedMotion: true });
    const transitionDuration = await page
      .getByRole("separator", { name: "Session and Engine boundary" })
      .locator("span")
      .evaluate((element) => getComputedStyle(element).transitionDuration);
    expect(transitionDuration).toBe("0s");
    await expectNoHorizontalOverflow(page);
  });

  test("proves preferred panel fidelity at the desktop session column and 412px", async ({ page }) => {
    const requests = preferredRequestUrls(page);

    await openStory(page, STORY_IDS.replacement, 1280, 900);
    await expectPreferredRelationship(page, "replacement");
    await expectPreferredPanelFidelity(page, true);
    await expect(preferredPanel(page).getByText("Save d4 to replace e4.")).toBeVisible();
    await expect(
      preferredPanel(page).getByText("Date changes are temporarily unavailable", { exact: true }),
    ).toBeVisible();
    await expectPreferredActions(page, ["Save", "Change effective date", "Remove"]);
    await expectDeferredDate(page, requests);
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);

    await openStory(page, STORY_IDS.replacement, 412, 915);
    await expectPreferredRelationship(page, "replacement");
    await expectPreferredPanelFidelity(page, true);
    await expect(preferredPanel(page).getByText("Save d4 to replace e4.")).toBeVisible();
    await expect(
      preferredPanel(page).getByText("Date changes are temporarily unavailable", { exact: true }),
    ).toBeVisible();
    await expectPreferredActions(page, ["Save", "Change effective date", "Remove"]);
    await expectDeferredDate(page, requests);
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);

    expect(requests).toEqual([]);
  });

  test("proves response distribution integration, states, accessibility, and responsive evidence", async ({ page }, testInfo) => {
    const cases = [
      { mode: "wide" as const, width: 1280, height: 1000 },
      { mode: "narrow" as const, width: 497, height: 1000 },
      { mode: "medium" as const, width: 800, height: 1000 },
      { mode: "narrow" as const, width: 412, height: 1000 },
      { mode: "narrow" as const, width: 320, height: 1000 },
    ];

    for (const entry of cases) {
      await openStory(page, STORY_IDS.responseDistribution, entry.width, entry.height);
      await expectResponsiveComposition(
        page,
        entry.mode,
        entry.mode === "wide"
          ? ["Board and Session boundary", "Session and Engine boundary"]
          : entry.mode === "medium"
            ? ["Session and Engine boundary"]
            : [],
      );

      const engineLane = page.getByTestId("repertoire-engine-lane");
      const analysisTab = engineLane.getByRole("tab", { name: "Analysis" });
      const responsesTab = engineLane.getByRole("tab", { name: "Move responses" });
      await expect(engineLane.getByRole("tab")).toHaveCount(2);
      await expect(analysisTab).toHaveAttribute("aria-selected", "true");
      await expect(engineLane.getByTestId("move-response-distribution")).toHaveAttribute(
        "data-embedded",
        "true",
      );
      await expect(engineLane.getByTestId("tabs-panel-move-responses")).toHaveAttribute(
        "hidden",
      );
      await responsesTab.click();
      await expect(responsesTab).toHaveAttribute("aria-selected", "true");
      const distribution = page.getByTestId("move-response-distribution");
      await expect(distribution).toHaveAttribute("data-state", "available");
      await expect(distribution.getByText("Black repertoire colour", { exact: true })).toBeVisible();
      const other = distribution.getByRole("button", { name: /other replies/ });
      await expect(other).toHaveAttribute("aria-expanded", "false");
      await other.focus();
      await expect(other).toBeFocused();
      await other.click();
      await expect(other).toHaveAttribute("aria-expanded", "true");
      await expect(distribution.getByRole("button", { name: /b3, 1 distinct games/ })).toBeVisible();
      await expect(page.getByTestId("session-status")).toContainText(
        "Select a legal move to continue the local line.",
      );
      const panelDimensions = await distribution.evaluate((element) => ({
        clientWidth: element.clientWidth,
        scrollWidth: element.scrollWidth,
      }));
      expect(panelDimensions.scrollWidth).toBeLessThanOrEqual(panelDimensions.clientWidth);
      await expectDistributionChartAndControlsClean(page);
      await expectNoHorizontalOverflow(page);
      await checkA11y(page);
      await page.screenshot({
        path: testInfo.outputPath(`move-response-distribution-${entry.mode}-${entry.width}.png`),
        fullPage: true,
      });

      const common = distribution.getByRole("button", { name: /Nf3, 4 distinct games/ });
      await common.focus();
      await page.keyboard.press("Enter");
      await expect(page.getByTestId("session-status")).toContainText(
        "Opponent move played locally: Nf3.",
      );
      await expect(page.getByTestId("session-origin")).toContainText("Current Ply 3.");
      await analysisTab.click();
      await expect(engineLane.getByTestId("tabs-panel-move-responses")).toHaveAttribute(
        "hidden",
      );
    }

    await page.emulateMedia({ forcedColors: "active", reducedMotion: "reduce" });
    await openStory(page, STORY_IDS.responseDistribution, 800, 1000);
    const media = await page.evaluate(() => ({
      forcedColors: window.matchMedia("(forced-colors: active)").matches,
      reducedMotion: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    }));
    expect(media).toEqual({ forcedColors: true, reducedMotion: true });
    const forcedDistribution = page.getByTestId("move-response-distribution");
    await expect(forcedDistribution).toHaveAttribute("data-state", "available");
    await expect(forcedDistribution.getByRole("button", { name: /Show other replies/ })).toBeVisible();
    const transitionDuration = await forcedDistribution
      .getByRole("button", { name: /Nf3, 4 distinct games/ })
      .first()
      .evaluate((element) => getComputedStyle(element).transitionDuration);
    expect(transitionDuration).toBe("0s");
    await expectNoHorizontalOverflow(page);
  });

  test("proves the dense distribution label cluster stays readable at wide, 497px, and 412px", async ({ page }, testInfo) => {
    const cases = [
      { width: 1280, height: 1000 },
      { width: 497, height: 1000 },
      { width: 412, height: 1000 },
    ] as const;

    for (const entry of cases) {
      await openStory(page, STORY_IDS.responseDistributionDense, entry.width, entry.height, false);
      const distribution = page.getByTestId("move-response-distribution");
      await expect(distribution).toHaveAttribute("data-state", "available");
      await expect(distribution.getByText("e4 98.0%")).toBeVisible();
      await expect(distribution.getByText("Other 0.0%")).toBeVisible();
      await expectDistributionChartAndControlsClean(page);
      await expectNoHorizontalOverflow(page);
      await page.screenshot({
        path: testInfo.outputPath(`move-response-distribution-dense-${entry.width}.png`),
        fullPage: true,
      });
    }
  });

  test("proves all five saved/staged relationship readings and disabled date behavior", async ({ page }) => {
    const requests = preferredRequestUrls(page);

    await openStory(page, STORY_IDS.firstChoice);
    await expectPreferredRelationship(page, "first-choice");
    await expectBothRelationshipBoxes(page);
    await expect(preferredPanel(page).getByText("Save e4 as the current saved choice.")).toBeVisible();
    await expectPreferredActions(page, ["Save", "Change effective date"]);
    await expectDeferredDate(page);

    await openStory(page, STORY_IDS.savedNoStage);
    await expectPreferredRelationship(page, "saved");
    await expectBothRelationshipBoxes(page);
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expect(preferredPanel(page).getByText("No move staged.")).toBeVisible();
    await expectPreferredActions(page, ["Change effective date", "Remove"]);
    await expectDeferredDate(page);

    await openStory(page, STORY_IDS.replacement, 412, 915);
    await expectPreferredRelationship(page, "replacement");
    await expect(preferredPanel(page).getByText("Save d4 to replace e4.")).toBeVisible();
    await expectPreferredActions(page, ["Save", "Change effective date", "Remove"]);
    await expectDeferredDate(page);
    await expectNoHorizontalOverflow(page);

    await openStory(page, STORY_IDS.matching);
    await expectPreferredRelationship(page, "matching");
    await expect(preferredPanel(page).getByText("e4 is already the current saved choice.")).toBeVisible();
    await expectPreferredActions(page, ["Change effective date", "Remove"]);
    await expect(
      preferredPanel(page)
        .getByTestId("preferred-actions")
        .getByRole("button", { name: "Save", exact: true }),
    ).toHaveCount(0);

    expect(requests).toEqual([]);
    await checkA11y(page);
  });

  test("proves saved-box pointer/keyboard staging without history or preferred mutation", async ({ page }) => {
    const requests = preferredRequestUrls(page);
    await openStory(page, STORY_IDS.savedBoxKeyboard);
    await expectPreferredRelationship(page, "matching");
    const savedBox = preferredPanel(page).getByRole("button", {
      name: "Current saved choice: e4; play and stage this move.",
    });
    await expect(savedBox).toBeFocused();
    await expect(savedBox).toHaveAttribute("type", "button");
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText(/e4.*e2e4/);
    await expectPreferredActions(page, ["Change effective date", "Remove"]);
    await expectSessionHistory(page, ["Initial position"]);
    await expectActiveSessionHistoryEntry(page, "Initial position");
    await expectPositionSquares(page, "e2", 0);
    await expectPositionSquares(page, "e4", 1);
    await expectNoHorizontalOverflow(page);
    expect(requests).toEqual([]);
    await checkA11y(page);
  });

  test("proves Save first choice/replacement refresh and board/history invariants", async ({ page }) => {
    await openStory(page, STORY_IDS.saveReplacement);
    await expectPreferredRelationship(page, "saved");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText(/d4.*d2d4/);
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText("No move staged.");
    await expectPositionSquares(page, "d2", 0);
    await expectPositionSquares(page, "d4", 1);
    await expectSessionHistory(page, ["Initial position", "White, move 1, d4"]);
    await expect(
      preferredPanel(page)
        .getByTestId("preferred-actions")
        .getByRole("button", { name: "Save", exact: true }),
    ).toHaveCount(0);
    await expectPreferredActions(page, []);

    await openStory(page, STORY_IDS.firstChoice);
    await expectPreferredRelationship(page, "first-choice");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("No saved choice yet.");
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText(/e4.*e2e4/);
    await expectSessionHistory(page, ["Initial position"]);
    await expectDeferredDate(page);
  });

  test("proves Remove confirmation, cancellation focus, and retained staging", async ({ page }) => {
    await openStory(page, STORY_IDS.removeRetainsStaging);
    await expect(page.getByText("Preferred move removed.", { exact: true })).toBeVisible({
      timeout: 15_000,
    });
    await expectPreferredRelationship(page, "first-choice");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("No saved choice yet.");
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText(/d4.*d2d4/);
    await expectPreferredActions(page, ["Save", "Change effective date"]);
    await expectDeferredDate(page);
    await expectSessionHistory(page, ["Initial position"]);
    await checkA11y(page);
  });

  test("proves pending and failed mutations retain confirmed and staged facts", async ({ page }) => {
    await openStory(page, STORY_IDS.pendingSave);
    await expect(preferredPanel(page).getByText("Saving preferred move...")).toBeVisible();
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText(/d4.*d2d4/);
    await expectPreferredActions(page, ["Save", "Change effective date", "Remove"]);
    await expect(
      preferredPanel(page)
        .getByTestId("preferred-actions")
        .getByRole("button", { name: "Save", exact: true }),
    ).toBeDisabled();

    await openStory(page, STORY_IDS.pendingRemove);
    await expect(preferredPanel(page).getByText("Removing preferred move...")).toBeVisible();
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expectPreferredActions(page, ["Change effective date", "Remove"]);
    await expect(preferredPanel(page).getByRole("button", { name: "Remove" })).toBeDisabled();

    await openStory(page, STORY_IDS.saveFailure);
    await expect(page.getByRole("alert")).toHaveText("The preferred move could not be updated. Try again.");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText(/d4.*d2d4/);

    await openStory(page, STORY_IDS.removeFailure);
    await expect(page.getByRole("alert")).toHaveText("The preferred move could not be updated. Try again.");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expect(preferredPanel(page).getByRole("button", { name: "Remove" })).toBeEnabled();
    await checkA11y(page);
  });

  test("proves gates, typed read feedback, loading, and opponent local history", async ({ page }) => {
    await openStory(page, STORY_IDS.unsavable);
    await expectPreferredRelationship(page, "empty");
    await expect(preferredPanel(page).getByText("This position cannot be saved because it is not in the corpus.")).toBeVisible();
    await expectPreferredActions(page, []);

    await openStory(page, STORY_IDS.loading);
    await expectPreferredRelationship(page, "unknown");
    await expect(preferredPanel(page).getByTestId("preferred-status")).toHaveText("Loading saved choice...");
    await expectPreferredActions(page, []);

    await openStory(page, STORY_IDS.readErrors);
    await expectPreferredRelationship(page, "unknown");
    await expect(page.getByRole("alert")).toHaveCount(2);
    await expectPreferredActions(page, []);

    await openStory(page, STORY_IDS.opponentGate);
    await expectPreferredRelationship(page, "empty");
    await expect(preferredPanel(page).getByText("Wait for your turn to stage or save a preferred move.")).toBeVisible();
    await expectPreferredActions(page, []);
    await expect(preferredPanel(page).getByRole("button", { name: /play and stage this move/ })).toHaveCount(0);

    await openStory(page, STORY_IDS.opponentLocal);
    await expect(page.getByTestId("repertoire-board-lane").getByTestId("board-move-history").getByRole("button")).toHaveCount(4, {
      timeout: 15_000,
    });
    await expectSessionHistory(page, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(page, "White, move 2, Nf3");
    await expectPreferredActions(page, []);
    await checkA11y(page);
  });

  test("proves promotion canonical identity and source/history invariants", async ({ page }) => {
    await openStory(page, STORY_IDS.promotion);
    await expect(preferredPanel(page)).toHaveAttribute("data-state", "first-choice", {
      timeout: 15_000,
    });
    await expectPreferredRelationship(page, "first-choice");
    await expect(preferredPanel(page).getByTestId("staged-move")).toContainText(/e8=N.*e7e8n/);
    await expectSessionHistory(page, ["Initial position"]);
    await expectPositionSquares(page, "e7", 0);
    await expectPositionSquares(page, "e8", 1);
    await expect(page.getByTestId("session-origin")).toHaveText(/Current Ply 0/);
    await checkA11y(page);
  });

  test("proves preserved move-history navigation and responsive focus semantics", async ({ page }) => {
    await openStory(page, STORY_IDS.navigation);
    await expectSessionHistory(page, ["Initial position", "White, move 1, e4", "Black, move 1, e6"]);
    await expectActiveSessionHistoryEntry(page, "Black, move 1, e6");
    await expect(page.getByRole("button", { name: "Next" })).toBeDisabled();

    await openStory(page, STORY_IDS.accessibility, 412, 915);
    const savedBox = preferredPanel(page).getByRole("button", {
      name: "Current saved choice: e4; play and stage this move.",
    });
    await savedBox.focus();
    await expect(savedBox).toBeFocused();
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });
});
