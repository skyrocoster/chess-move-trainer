import { expect, test } from "@playwright/test";
import {
  STORY_IDS,
  checkA11y,
  expectBothRelationshipBoxes,
  expectDateFreePreferredPanel,
  expectNoHorizontalOverflow,
  expectPanelMinimums,
  expectPreferredActions,
  expectPreferredPanelFidelity,
  expectPreferredRelationship,
  expectResponsiveComposition,
  openStory,
  panelBounds,
  preferredPanel,
  preferredRequestUrls,
  responsiveStage,
} from "./repertoire-builder-storybook-helpers";

test.describe("Repertoire Builder Storybook workspace", () => {
  test.describe.configure({ timeout: 30_000 });

  test("shows empty relationship boxes and session boundaries at wide and 412px", async ({
    page,
  }) => {
    await test.step("wide composition", async () => {
      await openStory(page, STORY_IDS.wide);
      await expectResponsiveComposition(page, "wide", [
        "Board and Session boundary",
        "Session and Engine boundary",
      ]);
      await expectPreferredRelationship(page, "empty");
      await expectBothRelationshipBoxes(page);
      await expect(preferredPanel(page).getByText("None yet")).toBeVisible();
      await expect(preferredPanel(page).getByText("No move selected.")).toBeVisible();
      await expect(
        preferredPanel(page).getByText("Play a legal move to select the first saved choice."),
      ).toBeVisible();
      await expectPreferredActions(page, []);
      await expectNoHorizontalOverflow(page);
      await checkA11y(page);
    });

    await test.step("narrow composition at 412px", async () => {
      await openStory(page, STORY_IDS.constrained, 412, 915);
      await expectResponsiveComposition(page, "narrow", []);
      await expectPreferredRelationship(page, "empty");
      await expectBothRelationshipBoxes(page);
      await expectNoHorizontalOverflow(page);
      await checkA11y(page);
    });
  });

  test("captures wide, medium, and narrow responsive evidence with axe proof", async ({
    page,
  }, testInfo) => {
    const cases = [
      { id: STORY_IDS.wide, mode: "wide" as const, width: 1280, labels: ["Board and Session boundary", "Session and Engine boundary"] },
      { id: STORY_IDS.medium, mode: "medium" as const, width: 800, labels: ["Session and Engine boundary"] },
      { id: STORY_IDS.constrained, mode: "narrow" as const, width: 412, labels: [] },
    ];

    for (const entry of cases) {
      await test.step(`${entry.mode} evidence at ${entry.width}px`, async () => {
        await openStory(page, entry.id, entry.width, 1000);
        await expectResponsiveComposition(page, entry.mode, entry.labels);
        await expectNoHorizontalOverflow(page);
        await checkA11y(page);
        await page.screenshot({
          path: testInfo.outputPath(`repertoire-responsive-${entry.mode}.png`),
          fullPage: true,
        });
      });
    }
  });

  test("shows exact container-width boundary transitions", async ({ page }) => {
    const cases = [
      [STORY_IDS.boundary699, "narrow", 0],
      [STORY_IDS.boundary700, "medium", 1],
      [STORY_IDS.boundary1039, "medium", 1],
      [STORY_IDS.boundary1040, "wide", 2],
    ] as const;

    for (const [storyId, mode, separatorCount] of cases) {
      await test.step(`${mode} boundary ${storyId}`, async () => {
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
      });
    }
  });

  test("supports keyboard resizing with focus, minimums, fixed bounds, and reset", async ({
    page,
  }) => {
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

  test("shows the replacement preferred panel at desktop width and 412px", async ({ page }) => {
    const requests = preferredRequestUrls(page);

    for (const viewport of [
      { width: 1280, height: 900, label: "desktop" },
      { width: 412, height: 915, label: "constrained" },
    ]) {
      await test.step(`${viewport.label} replacement panel`, async () => {
        await openStory(page, STORY_IDS.replacement, viewport.width, viewport.height);
        await expectPreferredRelationship(page, "replacement");
        await expectPreferredPanelFidelity(page, true);
        await expect(preferredPanel(page).getByText("Save d4 to replace e4.")).toBeVisible();
        await expectPreferredActions(page, ["Save", "Remove"]);
        await expectDateFreePreferredPanel(page);
        await expectNoHorizontalOverflow(page);
        await checkA11y(page);
      });
    }

    expect(requests).toEqual([]);
  });

  test("uses current-day parent transition operations for the clean preferred timeline", async ({
    page,
  }) => {
    const legacyRequests = preferredRequestUrls(page);
    await openStory(page, STORY_IDS.cleanPreferredTimeline);

    const panel = preferredPanel(page);
    const requestLog = page.getByTestId("clean-preferred-request-log");
    await expect
      .poll(async () => JSON.parse((await requestLog.textContent()) ?? "[]").length, {
        timeout: 30_000,
      })
      .toBe(5);
    const requests = JSON.parse((await requestLog.textContent()) ?? "[]") as Array<Record<string, string>>;
    expect(requests).toHaveLength(5);
    expect(requests.map((request) => request.method)).toEqual([
      "GET",
      "PUT",
      "GET",
      "DELETE",
      "GET",
    ]);

    const parentFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
    const firstGet = requests[0]!;
    const save = requests[1]!;
    const refreshedGet = requests[2]!;
    const remove = requests[3]!;
    const finalGet = requests[4]!;
    expect(firstGet).toMatchObject({ method: "GET", fen: parentFen });
    expect(refreshedGet).toEqual(firstGet);
    expect(finalGet).toEqual(firstGet);
    expect(firstGet.from).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(firstGet.until).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(save).toEqual({
      method: "PUT",
      fen: parentFen,
      move_uci: "e2e4",
      effective_from: firstGet.from,
    });
    expect(remove).toEqual({ method: "DELETE", fen: parentFen, effective_from: firstGet.from });
    for (const request of requests) expect(request).not.toHaveProperty("effective_until");

    await expectPreferredRelationship(page, "first-choice");
    await expect(panel.getByTestId("saved-move")).toContainText("None yet");
    await expect(panel.getByTestId("selected-move")).toContainText(/e4.*e2e4/);
    await expect(panel.getByRole("button", { name: "Save e4", exact: true })).toBeVisible();
    await expectPreferredActions(page, ["Save"]);
    await expectDateFreePreferredPanel(page);
    expect(legacyRequests).toEqual([]);
    await expectNoHorizontalOverflow(page);
    await checkA11y(page);
  });
});
