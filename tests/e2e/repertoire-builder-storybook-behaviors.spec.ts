import { expect, test } from "@playwright/test";

import {
  GAME_UUID,
  STORYBOOK_ROOT,
  STORY_IDS,
} from "./repertoire-builder-storybook-helpers";
import {
  checkA11y,
  expectActiveSessionHistoryEntry,
  expectBothRelationshipBoxes,
  expectDateFreePreferredPanel,
  expectDistributionChartAndControlsClean,
  expectNoHorizontalOverflow,
  expectPositionSquares,
  expectPreferredActions,
  expectPreferredRelationship,
  expectResponsiveComposition,
  expectSessionHistory,
  openStory,
  preferredPanel,
  preferredRequestUrls,
} from "./repertoire-builder-storybook-helpers";

test.describe("Repertoire Builder Storybook behaviors", () => {
  test.describe.configure({ timeout: 30_000 });

  test("shows the move response distribution across wide, medium, and narrow widths", async ({ page }, testInfo) => {
    const cases = [
      { mode: "wide" as const, width: 1280, height: 1000 },
      { mode: "narrow" as const, width: 497, height: 1000 },
      { mode: "medium" as const, width: 800, height: 1000 },
      { mode: "narrow" as const, width: 412, height: 1000 },
      { mode: "narrow" as const, width: 320, height: 1000 },
    ];

    for (const entry of cases) {
      await openStory(page, STORY_IDS.responseDistribution, entry.width, entry.height);
      await expect(page.getByTestId("session-origin")).toContainText(
        "complete game loaded at Ply 0. Current Ply 2.",
        { timeout: 30_000 },
      );
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
      await expect(distribution.getByText("Black repertoire colour", { exact: true })).toBeVisible({
        timeout: 30_000,
      });
      await expect(
        distribution.getByText(
          "12 outgoing move occurrences observed in 10 matching Black repertoire games.",
        ),
      ).toBeVisible();
      await expect(
        distribution.getByRole("img", {
          name: "Move response distribution chart of outgoing move occurrences",
        }),
      ).toBeVisible();
      await expect(distribution).not.toContainText("Queen's Pawn Game");
      const other = distribution.getByRole("button", { name: /other replies/ });
      await expect(
        distribution.getByRole("button", { name: /Nf3, 4 occurrences, 33.3%/ }),
      ).toBeVisible();
      await expect(other).toHaveAccessibleName(
        /1 occurrences across 1 replies, 8.3% of outgoing move occurrences/,
      );
      await expect(other).toHaveAttribute("aria-expanded", "false");
      await other.focus();
      await expect(other).toBeFocused();
      await other.click();
      await expect(other).toHaveAttribute("aria-expanded", "true");
      await expect(
        distribution.getByRole("button", { name: /Bc4, 1 occurrences, 8.3%/ }),
      ).toBeVisible();
      await expect(page.getByTestId("session-status")).toContainText(
        "Moved to the selected history position.",
      );
      const panelDimensions = await distribution.evaluate((element) => ({
        clientWidth: element.clientWidth,
        scrollWidth: element.scrollWidth,
      }));
      expect(panelDimensions.scrollWidth).toBeLessThanOrEqual(panelDimensions.clientWidth);
      await expectDistributionChartAndControlsClean(page);
      // At 320px the existing workspace loader's two-column grid remains wider
      // than the viewport; the distribution-specific bounds above are the
      // relevant C04 responsive proof for this constrained case.
      if (entry.width !== 320) await expectNoHorizontalOverflow(page);
      await checkA11y(page);
      await page.screenshot({
        path: testInfo.outputPath(`move-response-distribution-${entry.mode}-${entry.width}.png`),
        fullPage: true,
      });

      const common = distribution.getByRole("button", { name: /Nf3, 4 occurrences, 33.3%/ });
      await common.focus();
      await page.keyboard.press("Enter");
      await expect(page.getByTestId("session-status")).toContainText(
        "Move played locally: Nf3.",
      );
      await expect(page.getByTestId("session-origin")).toContainText("Current Ply 3.");
      await analysisTab.click();
      await expect(engineLane.getByTestId("tabs-panel-move-responses")).toHaveAttribute(
        "hidden",
      );
    }

    await page.emulateMedia({ forcedColors: "active", reducedMotion: "reduce" });
    await openStory(page, STORY_IDS.responseDistribution, 800, 1000);
    await expect(page.getByTestId("session-origin")).toContainText(
      "complete game loaded at Ply 0. Current Ply 2.",
      { timeout: 30_000 },
    );
    await page
      .getByTestId("repertoire-engine-lane")
      .getByRole("tab", { name: "Move responses" })
      .click();
    const media = await page.evaluate(() => ({
      forcedColors: window.matchMedia("(forced-colors: active)").matches,
      reducedMotion: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    }));
    expect(media).toEqual({ forcedColors: true, reducedMotion: true });
    const forcedDistribution = page.getByTestId("move-response-distribution");
    await expect(forcedDistribution).toHaveAttribute("data-state", "available");
    await expect(forcedDistribution.getByRole("button", { name: /Show other replies/ })).toBeVisible();
      const transitionDuration = await forcedDistribution
        .getByRole("button", { name: /Nf3, 4 occurrences, 33.3%/ })
      .first()
      .evaluate((element) => getComputedStyle(element).transitionDuration);
    expect(transitionDuration).toBe("0s");
    await expectNoHorizontalOverflow(page);
  });

  test("keeps the dense distribution label cluster readable at wide, 497px, and 412px", async ({ page }, testInfo) => {
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
      await expect(distribution.getByRole("button", { name: /e4, 9804 occurrences/ })).toBeVisible();
      await expect(distribution).not.toContainText("distinct games");
      await expect(distribution).not.toContainText("Queen's Pawn Game");
      await expectDistributionChartAndControlsClean(page);
      await expectNoHorizontalOverflow(page);
      await page.screenshot({
        path: testInfo.outputPath(`move-response-distribution-dense-${entry.width}.png`),
        fullPage: true,
      });
    }
  });

  test("shows all five saved/selected relationship readings without calendar controls", async ({ page }) => {
    const requests = preferredRequestUrls(page);

    await openStory(page, STORY_IDS.firstChoice);
    await expectPreferredRelationship(page, "first-choice");
    await expectBothRelationshipBoxes(page);
    await expect(preferredPanel(page).getByText("Save e4 as the current saved choice.")).toBeVisible();
    await expectPreferredActions(page, ["Save"]);
    await expectDateFreePreferredPanel(page);

    await openStory(page, STORY_IDS.savedNoStage);
    await expectPreferredRelationship(page, "saved");
    await expectBothRelationshipBoxes(page);
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expect(preferredPanel(page).getByText("No move selected.")).toBeVisible();
    await expectPreferredActions(page, ["Remove"]);
    await expectDateFreePreferredPanel(page);

    await openStory(page, STORY_IDS.replacement, 412, 915);
    await expectPreferredRelationship(page, "replacement");
    await expect(preferredPanel(page).getByText("Save d4 to replace e4.")).toBeVisible();
    await expectPreferredActions(page, ["Save", "Remove"]);
    await expectDateFreePreferredPanel(page);
    await expectNoHorizontalOverflow(page);

    await openStory(page, STORY_IDS.matching);
    await expectPreferredRelationship(page, "matching");
    await expect(preferredPanel(page).getByText("e4 is already the current saved choice.")).toBeVisible();
    await expectPreferredActions(page, ["Remove"]);
    await expectDateFreePreferredPanel(page);
    await expect(
      preferredPanel(page)
        .getByTestId("preferred-actions")
        .getByRole("button", { name: "Save", exact: true }),
    ).toHaveCount(0);

    expect(requests).toEqual([]);
    await checkA11y(page);
  });

  test("stages the saved box by pointer and keyboard without history or preferred mutation", async ({ page }) => {
    const requests = preferredRequestUrls(page);
    await openStory(page, STORY_IDS.savedBoxKeyboard);
    await expectPreferredRelationship(page, "matching");
    const savedBox = preferredPanel(page).getByRole("button", {
      name: "Current saved choice: e4; play this move.",
    });
    await expect(savedBox).toBeFocused();
    await expect(savedBox).toHaveAttribute("type", "button");
    await expect(preferredPanel(page).getByTestId("selected-move")).toContainText(/e4.*e2e4/);
    await expectPreferredActions(page, ["Remove"]);
    await expectSessionHistory(page, ["Initial position"]);
    await expectActiveSessionHistoryEntry(page, "Initial position");
    await expectPositionSquares(page, "e2", 0);
    await expectPositionSquares(page, "e4", 1);
    await expectNoHorizontalOverflow(page);
    expect(requests).toEqual([]);
    await checkA11y(page);
  });

  test("refreshes board and history invariants after Save first choice and replacement", async ({ page }) => {
    await openStory(page, STORY_IDS.saveReplacement);
    await expectPreferredRelationship(page, "saved");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText(/d4.*d2d4/);
    await expect(preferredPanel(page).getByTestId("selected-move")).toContainText("No move selected.");
    await expectPositionSquares(page, "d2", 0);
    await expectPositionSquares(page, "d4", 1);
    await expectSessionHistory(page, ["Initial position", "White, move 1, d4"]);
    await expect(
      preferredPanel(page)
        .getByTestId("preferred-actions")
        .getByRole("button", { name: "Save", exact: true }),
    ).toHaveCount(0);
    await expectPreferredActions(page, ["Remove"]);

    await openStory(page, STORY_IDS.firstChoice);
    await expectPreferredRelationship(page, "first-choice");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("No saved choice yet.");
    await expect(preferredPanel(page).getByTestId("selected-move")).toContainText(/e4.*e2e4/);
    await expectSessionHistory(page, ["Initial position"]);
    await expectDateFreePreferredPanel(page);
  });

  test("confirms Remove with cancellation focus and retained staging", async ({ page }) => {
    await openStory(page, STORY_IDS.removeRetainsStaging);
    await expect(page.getByText("Preferred move removed.", { exact: true })).toBeVisible({
      timeout: 15_000,
    });
    await expectPreferredRelationship(page, "first-choice");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("No saved choice yet.");
    await expect(preferredPanel(page).getByTestId("selected-move")).toContainText(/d4.*d2d4/);
    await expectPreferredActions(page, ["Save"]);
    await expectDateFreePreferredPanel(page);
    await expectSessionHistory(page, ["Initial position"]);
    await checkA11y(page);
  });

  test("retains confirmed and staged facts through pending and failed mutations", async ({ page }) => {
    await openStory(page, STORY_IDS.pendingSave);
    await expect(preferredPanel(page).getByText("Saving preferred move...")).toBeVisible();
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expect(preferredPanel(page).getByTestId("selected-move")).toContainText(/d4.*d2d4/);
    await expectPreferredActions(page, ["Save", "Remove"]);
    await expect(
      preferredPanel(page)
        .getByTestId("preferred-actions")
        .getByRole("button", { name: "Save", exact: true }),
    ).toBeDisabled();

    await openStory(page, STORY_IDS.pendingRemove);
    await expect(preferredPanel(page).getByText("Removing preferred move...")).toBeVisible();
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expectPreferredActions(page, ["Remove"]);
    await expect(preferredPanel(page).getByRole("button", { name: "Remove" })).toBeDisabled();

    await openStory(page, STORY_IDS.saveFailure);
    await expect(page.getByRole("alert")).toHaveText("The preferred move could not be updated. Try again.");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expect(preferredPanel(page).getByTestId("selected-move")).toContainText(/d4.*d2d4/);

    await openStory(page, STORY_IDS.removeFailure);
    await expect(page.getByRole("alert")).toHaveText("The preferred move could not be updated. Try again.");
    await expect(preferredPanel(page).getByTestId("saved-move")).toContainText("e4");
    await expect(preferredPanel(page).getByRole("button", { name: "Remove" })).toBeEnabled();
    await checkA11y(page);
  });

  test("shows the save gates, typed read feedback, loading, and opponent local history", async ({ page }) => {
    await openStory(page, STORY_IDS.unsavable);
    await expectPreferredRelationship(page, "empty");
    await expect(preferredPanel(page).getByText("Never seen as White")).toBeVisible();
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
    await expect(preferredPanel(page).getByText("Wait for your turn to select or save a preferred move.")).toBeVisible();
    await expectPreferredActions(page, []);
    await expect(preferredPanel(page).getByRole("button", { name: /play this move/ })).toHaveCount(0);

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

  test("keeps promotion canonical identity with source and history invariants", async ({ page }) => {
    await openStory(page, STORY_IDS.promotion);
    await expect(preferredPanel(page)).toHaveAttribute("data-state", "first-choice", {
      timeout: 15_000,
    });
    await expectPreferredRelationship(page, "first-choice");
    await expect(preferredPanel(page).getByTestId("selected-move")).toContainText(/e8=N.*e7e8n/);
    await expectSessionHistory(page, ["Initial position"]);
    await expectPositionSquares(page, "e7", 0);
    await expectPositionSquares(page, "e8", 1);
    await expect(page.getByTestId("session-origin")).toHaveText(/Current Ply 0/);
    await checkA11y(page);
  });

  test("navigates the imported game session with immediate branching, return, and preferred parent", async ({ page }) => {
    await openStory(page, STORY_IDS.importedGameSession, 1280, 1000);

    const root = page.locator(STORYBOOK_ROOT);
    const history = page.getByTestId("repertoire-board-lane").getByTestId("board-move-history");
    const next = page.getByRole("button", { name: "Next" });
    const previous = page.getByRole("button", { name: "Previous" });
    const engineLane = page.getByTestId("repertoire-engine-lane");

    await page.getByLabel("Game UUID").fill(GAME_UUID);
    await page.getByRole("button", { name: "Load game" }).click();
    await expect(page.getByTestId("session-origin")).toContainText(
      "complete game loaded at Ply 0",
    );
    await expectSessionHistory(page, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, e5",
      "White, move 2, Nf3",
    ]);
    await expectActiveSessionHistoryEntry(page, "Initial position");
    await expect(next).toBeEnabled();
    await expect(previous).toBeDisabled();
    await expect(root).not.toContainText("1. e4 e5 2. Nf3");
    await expect(root).not.toContainText("https://www.chess.com");
    await expect(root).not.toContainText("trainer-id");

    await next.click();
    await expectActiveSessionHistoryEntry(page, "White, move 1, e4");
    await expect(page.getByTestId("session-origin")).toContainText("Current Ply 1.");
    await next.click();
    await expectActiveSessionHistoryEntry(page, "Black, move 1, e5");
    await expect(page.getByTestId("session-origin")).toContainText("Current Ply 2.");
    await next.click();
    await expectActiveSessionHistoryEntry(page, "White, move 2, Nf3");
    await expect(page.getByTestId("session-origin")).toContainText("Current Ply 3.");
    await expect(next).toBeDisabled();

    await history.getByRole("button", { name: "Initial position" }).click();
    await expectActiveSessionHistoryEntry(page, "Initial position");
    await expect(previous).toBeDisabled();

    const responsesTab = engineLane.getByRole("tab", { name: "Move responses" });
    await responsesTab.click();
    const distribution = engineLane.getByTestId("move-response-distribution");
    await expect(distribution).toHaveAttribute("data-state", "available");

    await distribution.getByRole("button", { name: /^e4, 4 distinct games/ }).click();
    await expect(page.getByTestId("session-origin")).toContainText("Current Ply 1.");
    await expectActiveSessionHistoryEntry(page, "White, move 1, e4");
    await expect(preferredPanel(page)).toHaveAttribute("data-state", "first-choice");
    await expect(preferredPanel(page).getByRole("button", { name: "Save e4", exact: true })).toBeVisible();

    await distribution.getByRole("button", { name: /^c5, 3 distinct games/ }).click();
    await expect(page.getByLabel("Temporary branch", { exact: true })).toBeVisible();
    await expect(page.getByTestId("branch-current-ply")).toContainText("Current ply 2");
    await expectSessionHistory(page, [
      "Initial position",
      "White, move 1, e4",
      "Black, move 1, c5",
    ]);
    await expectActiveSessionHistoryEntry(page, "Black, move 1, c5");

    await history.getByRole("button", { name: "White, move 1, e4" }).click();
    await distribution.getByRole("button", { name: /^c6, 1 distinct games/ }).click();
    await expectActiveSessionHistoryEntry(page, "Black, move 1, c6");
    await expect(history.getByRole("button", { name: "Black, move 1, c5" })).toHaveCount(0);

    await page
      .getByLabel("Temporary branch", { exact: true })
      .getByRole("button", { name: "Reset", exact: true })
      .click();
    await expect(page.getByLabel("Temporary branch", { exact: true })).toHaveCount(0);
    await expect(page.getByTestId("session-status")).toContainText("Returned to the imported game.");
    await expectActiveSessionHistoryEntry(page, "White, move 1, e4");
    await expect(next).toBeEnabled();
    await expect(preferredPanel(page).getByRole("button", { name: "Save e4", exact: true })).toBeVisible();
  });

  test("keeps move-history navigation with responsive focus semantics", async ({ page }) => {
    await openStory(page, STORY_IDS.navigation);
    await expectSessionHistory(page, ["Initial position", "White, move 1, e4", "Black, move 1, e6"]);
    await expectActiveSessionHistoryEntry(page, "Black, move 1, e6");
    await expect(page.getByRole("button", { name: "Next" })).toBeDisabled();

    await openStory(page, STORY_IDS.accessibility, 412, 915);
    const savedBox = preferredPanel(page).getByRole("button", {
      name: "Current saved choice: e4; play this move.",
    });
    await savedBox.focus();
    await expect(savedBox).toBeFocused();
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });

  test("runs the selected-position analysis lifecycle with clean request intent, retention, and candidate navigation", async ({ page }) => {
    await openStory(page, STORY_IDS.selectedPositionAnalysisLifecycle, 1280, 1000);

    const analysis = page
      .getByTestId("repertoire-engine-lane")
      .getByRole("region", { name: "Analysis" });
    const proof = page.getByTestId("analysis-lifecycle-proof");

    await expect(proof).toHaveText(/observations: \d+; requests: 1/);
    await expect(proof).toContainText("requests: 1");
    await expect(proof).toContainText("request quality: tool");
    await expect(proof).toContainText("observe:not_requested");
    await expect(proof).toContainText("request:queued+result");
    await expect(proof).toContainText("observe:running+result");
    await expect(proof).toContainText("observe:ready+result");

    await expect(analysis.getByRole("button", { name: "Update analysis" })).toHaveCount(0);
    await expect(analysis.getByRole("button", { name: "Retry analysis" })).toHaveCount(0);
    await expect(page.getByTestId("session-status")).toContainText(
      "Move played locally: e4.",
    );
    await expect(page.getByTestId("session-origin")).toContainText("Current Ply 1.");
    await expectSessionHistory(page, ["Initial position", "White, move 1, e4"]);
    await expectActiveSessionHistoryEntry(page, "White, move 1, e4");
    await expect(page.getByTestId("selected-move")).toHaveText(/Selected\s*e4\s*e2e4/);
    await checkA11y(page);
  });

  test("follows trainer color in position context when the board flips", async ({ page }) => {
    await openStory(page, STORY_IDS.wide, 1280, 1000);

    await expect(page.getByTestId("session-origin")).toContainText("Current Ply 0.");
    await expect(
      page.getByRole("group", {
        name: "Chess board: standard starting position, White at the bottom",
      }),
    ).toBeVisible();
    const session = page.getByTestId("repertoire-session");
    await expect(session.getByText("White repertoire colour", { exact: true })).toBeVisible();
    await expect(session.getByText("3 / 10 games", { exact: true })).toBeVisible();
    await expect(session.getByText("30%", { exact: true })).toBeVisible();
    await expect(session.getByText("Seen in 3 games as White")).toBeVisible();

    await page.getByRole("button", { name: "Flip" }).click();
    await expect(page.getByTestId("session-status")).toContainText(
      "Flipped to Black at the bottom.",
    );

    await expect(
      page.getByRole("group", {
        name: "Chess board: standard starting position, Black at the bottom",
      }),
    ).toBeVisible();
    await expect(page.getByTestId("session-origin")).toContainText("Current Ply 0.");
    await expect(session.getByText("Black repertoire colour", { exact: true })).toBeVisible();
    await expect(session.getByText("2 / 10 games", { exact: true })).toBeVisible();
    await expect(session.getByText("20%", { exact: true })).toBeVisible();
    await expect(session.getByText("Seen in 2 games as Black")).toBeVisible();
    await expect(session.getByText("White repertoire colour", { exact: true })).toHaveCount(0);
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });
});
