import AxeBuilder from "@axe-core/playwright";
import { expect, type Page } from "@playwright/test";

export const STORYBOOK_URL = "http://127.0.0.1:6006";
export const STORYBOOK_ROOT = "#storybook-root";
export const GAME_UUID = "0007925c-5a8d-11f0-9740-f690a301000f";
export const STORY_IDS = {
  wide: "application-repertoire-builder-workspace--wide",
  medium: "application-repertoire-builder-workspace--medium",
  constrained: "application-repertoire-builder-workspace--constrained",
  importedGameSession: "application-repertoire-builder-workspace--imported-game-session",
  stagedMy: "application-repertoire-builder-workspace--staged-my",
  selectedPositionAnalysisLifecycle:
    "application-repertoire-builder-workspace--selected-position-analysis-lifecycle",
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
  cleanPreferredTimeline:
    "application-repertoire-builder-workspace--clean-preferred-timeline-novel-parent",
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
export const GEOMETRY_TOLERANCE = 4;

export type LayoutBounds = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export async function openStory(
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

export function preferredPanel(page: Page) {
  return page
    .getByTestId("repertoire-session-lane")
    .getByRole("region", { name: "Preferred move" });
}

export function responsiveStage(page: Page) {
  return page.getByTestId("repertoire-workspace-stage");
}

export async function expectResponsiveComposition(
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
}

export async function expectPreferredRelationship(
  page: Page,
  state: "empty" | "first-choice" | "saved" | "replacement" | "matching" | "unknown",
) {
  await expect(preferredPanel(page)).toHaveAttribute("data-state", state);
}

export async function expectPreferredActions(page: Page, actions: readonly string[]) {
  const actual = (await preferredPanel(page).getByRole("button").allTextContents())
    .map((label) => label.trim())
    .filter((label) => label === "Remove" || label.startsWith("Save "))
    .map((label) => (label.startsWith("Save ") ? "Save" : label));
  expect(actual).toEqual(actions);
}

export async function expectDateFreePreferredPanel(page: Page) {
  const panel = preferredPanel(page);
  await expect(panel.getByTestId("effective-date")).toHaveCount(0);
  await expect(panel.getByTestId("calendar-date-popup")).toHaveCount(0);
  await expect(panel.getByRole("button", { name: /effective date|calendar|future|schedule/i })).toHaveCount(0);
  await expect(panel).not.toContainText(/effective date|calendar|future schedule/i);
}

export async function expectBothRelationshipBoxes(page: Page) {
  await expect(preferredPanel(page).getByTestId("saved-move")).toBeVisible();
  await expect(preferredPanel(page).getByTestId("selected-move")).toBeVisible();
  await expect(preferredPanel(page).getByText("Current saved choice", { exact: true })).toBeVisible();
  await expect(preferredPanel(page).getByText("Selected move", { exact: true })).toBeVisible();
}

export async function expectSessionHistory(page: Page, entries: readonly string[]) {
  const history = page.getByTestId("repertoire-board-lane").getByTestId("board-move-history");
  await expect(history).toBeVisible();
  const buttons = history.getByRole("button");
  await expect(buttons).toHaveCount(entries.length);
  for (const [index, name] of entries.entries()) {
    await expect(buttons.nth(index)).toHaveAccessibleName(name);
  }
}

export async function expectActiveSessionHistoryEntry(page: Page, name: string) {
  await expect(
    page.getByTestId("repertoire-board-lane").getByTestId("board-move-history").getByRole("button", { name }),
  ).toHaveAttribute("aria-current", "step");
}

export async function sharedPositionSummary(page: Page) {
  const row = page.getByTestId("repertoire-session-lane").getByTestId("position-description-row");
  const description = row.getByRole("button", { name: "Position description" });
  await expect(description).toHaveAttribute("aria-expanded", "true");
  const summary = row.locator("[data-position-summary]");
  await expect(summary).toBeVisible();
  return summary;
}

export async function expectPositionSquares(page: Page, square: string, count: number) {
  await expect((await sharedPositionSummary(page)).locator(`[data-position-square="${square}"]`)).toHaveCount(count);
}

export async function expectNoHorizontalOverflow(page: Page) {
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

export async function expectDistributionChartAndControlsClean(page: Page) {
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

export async function expectPreferredPanelFidelity(page: Page, expectStacked: boolean) {
  const panel = preferredPanel(page);
  const saved = panel.getByTestId("saved-move");
  const selected = panel.getByTestId("selected-move");
  const connector = saved.locator("xpath=following-sibling::*[1]");
  const connectorNext = connector.locator("xpath=following-sibling::*[1]");
  const consequence = panel.getByTestId("preferred-consequence");

  await expect(panel.getByText("Current saved choice", { exact: true })).toHaveCount(1);
  await expect(panel.getByText("Selected move", { exact: true })).toHaveCount(1);
  await expect(saved).toBeVisible();
  await expect(selected).toBeVisible();
  await expect(
    panel.getByRole("button", {
      name: "Current saved choice: e4; play this move.",
    }),
  ).toBeVisible();

  await expect(connector).toHaveAttribute("aria-hidden", "true");
  await expect(connectorNext).toHaveAttribute("data-testid", "selected-move");
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

  const [savedBox, connectorBox, selectedBox] = await Promise.all([
    saved.boundingBox(),
    connector.boundingBox(),
    selected.boundingBox(),
  ]);
  if (!savedBox || !connectorBox || !selectedBox) {
    throw new Error("Preferred move relationship boxes are missing layout bounds.");
  }
  if (expectStacked) {
    expect(savedBox.y + savedBox.height).toBeLessThanOrEqual(connectorBox.y + 1);
    expect(connectorBox.y + connectorBox.height).toBeLessThanOrEqual(selectedBox.y + 1);
    await expect(connector.locator("svg")).toHaveCSS(
      "transform",
      "matrix(0, 1, -1, 0, 0, 0)",
    );
  } else {
    expect(savedBox.x + savedBox.width).toBeLessThanOrEqual(connectorBox.x + 1);
    expect(connectorBox.x + connectorBox.width).toBeLessThanOrEqual(selectedBox.x + 1);
  }

  const panelBounds = await panel.boundingBox();
  if (!panelBounds) throw new Error("Preferred move panel bounds are missing.");
  const actionButtons = ["Save", "Remove"].map((name) =>
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

export async function checkA11y(page: Page) {
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

export async function panelBounds(page: Page) {
  return page.getByTestId("repertoire-workspace-stage").locator("[data-panel]").evaluateAll((panels) =>
    panels.map((panel) => {
      const bounds = panel.getBoundingClientRect();
      return { width: bounds.width, height: bounds.height, id: panel.id };
    }),
  );
}

export function expectPanelMinimums(
  panels: readonly { width: number }[],
  minimums: readonly number[],
) {
  expect(panels).toHaveLength(minimums.length);
  for (const [index, minimum] of minimums.entries()) {
    expect(panels[index]!.width).toBeGreaterThanOrEqual(minimum - 1);
  }
}

export function preferredRequestUrls(page: Page) {
  const urls: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/preferred-move")) urls.push(request.url());
  });
  return urls;
}
