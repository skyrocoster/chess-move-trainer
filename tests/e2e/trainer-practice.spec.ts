import { expect, test, type Page, type Route } from "@playwright/test";

const OPENING_KEY = "B10:Caro-Kann Defense";
const ITALIAN_KEY = "C20:Italian Game";
const AS_OF = "2026-09-14";
const REPRESENTATIVE_FEN =
  "rnbqkbnr/pp2pppp/8/3p4/8/1B6/PPPP1PPP/RNBQK1NR b KQkq - 0 1";
const TRAINING_ERROR = {
  code: "position_training_requirements_unavailable",
  message: "safe test failure",
};

const OPENING_ITEMS = [
  {
    key: OPENING_KEY,
    eco: "B10",
    name: "Caro-Kann Defense",
    route_count: 2,
    games_reached: 12,
    games_deepest: 9,
  },
  {
    key: ITALIAN_KEY,
    eco: "C20",
    name: "Italian Game",
    route_count: 1,
    games_reached: 8,
    games_deepest: 6,
  },
];

const TRAINING_ITEM = {
  fen: "fen-e2e",
  trainer_color: "white",
  preferred_move_uci: "e2e4",
  encounters: 4,
  hits: 1,
  misses: 3,
  observed_success_rate: 0.25,
  game_balance: -0.5,
  effective_training_balance: -0.75,
  training_adjustment: -0.25,
  training_updated_on: null,
  training_requirement: -0.75,
  training_required: true,
  correct_answers_needed: 2,
};

const TRAINING_RESPONSE_BASE = {
  as_of: AS_OF,
  scoring_policy: {
    target_success_rate: 0.8,
    game_hit_weight: 1,
    game_miss_weight: 1,
    training_curve: "linear",
    training_credit_half_life_days: 30,
  },
  page: 1,
  page_size: 100,
};

test.setTimeout(90_000);

async function fulfillJson(route: Route, data: unknown, status = 200) {
  await route.fulfill({
    body: JSON.stringify(data),
    contentType: "application/json",
    headers: {
      "access-control-allow-origin": "http://localhost:8444",
      "access-control-expose-headers": "X-Openings-Catalogue-Version",
      "X-Openings-Catalogue-Version": "e2e-v1",
    },
    status,
  });
}

async function mockCatalogue(page: Page, paginated = false) {
  const requests: URL[] = [];
  await page.route("**/api/openings**", async (route) => {
    const url = new URL(route.request().url());
    requests.push(url);
    const pageNumber = Number(url.searchParams.get("page"));
    const items = paginated
      ? pageNumber === 1
        ? [OPENING_ITEMS[0]]
        : [OPENING_ITEMS[1]]
      : OPENING_ITEMS;
    await fulfillJson(route, {
      has_next: paginated && pageNumber === 1,
      items,
      page: pageNumber,
      page_size: 100,
      total: paginated ? 2 : OPENING_ITEMS.length,
      total_pages: paginated ? 2 : 1,
    });
  });
  return requests;
}

function trainingResponse(
  items: readonly object[] = [TRAINING_ITEM],
  total = items.length,
) {
  return { ...TRAINING_RESPONSE_BASE, items, total };
}

async function navigateToTrainer(page: Page) {
  await page.goto("http://localhost:8444/");
  await page.getByRole("link", { name: "Trainer Practice" }).click();
  await expect(page).toHaveURL(/\/trainer$/);
  await expect(page.getByRole("heading", { name: "Trainer Practice", level: 1 })).toBeVisible({
    timeout: 30_000,
  });
}

async function chooseSpecificOpening(page: Page, name: RegExp | string = /B10 Caro-Kann Defense/) {
  const opening = page.getByRole("combobox", { name: "Opening" });
  await opening.click();
  await page.getByRole("option", { name }).click();
  return opening;
}

async function chooseAllOpenings(page: Page) {
  const opening = page.getByRole("combobox", { name: "Opening" });
  await opening.click();
  await page.getByRole("option", { name: "All openings" }).click();
  return opening;
}

async function chooseAsOfDate(page: Page, dayName = /September 14th, 2026/) {
  await page.getByRole("button", { name: /as_of:/ }).click();
  const dialog = page.getByRole("dialog", { name: "as_of" });
  await expect(dialog).toBeVisible({ timeout: 30_000 });
  await dialog.getByRole("button", { name: dayName }).click();
}

test("retrieves live Caro-Kann training positions from shell navigation", async ({ page }) => {
  const catalogueRequests = await mockCatalogue(page, true);
  const trainingRequests: URL[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (request.method() !== "GET") return;
    if (url.pathname === "/api/positions/training-requirements") {
      trainingRequests.push(url);
    }
  });

  await navigateToTrainer(page);

  const opening = page.getByRole("combobox", { name: "Opening" });
  await opening.click();
  await expect(page.getByRole("option", { name: /B10 Caro-Kann Defense/ })).toBeVisible({
    timeout: 30_000,
  });
  const catalogueRequestCountAfterCompleteLoad = catalogueRequests.length;
  await opening.fill("Caro-Kann Defense");
  await expect(page.getByRole("option", { name: /B10 Caro-Kann Defense/ })).toBeVisible();
  expect(catalogueRequests).toHaveLength(catalogueRequestCountAfterCompleteLoad);
  await page.getByRole("option", { name: /B10 Caro-Kann Defense/ }).click();

  await page.getByRole("radio", { name: "Black" }).click();
  await chooseAsOfDate(page);

  const requestPromise = page.waitForRequest((request) => {
    const url = new URL(request.url());
    return (
      request.method() === "GET" &&
      url.pathname === "/api/positions/training-requirements" &&
      url.searchParams.get("opening_key") === OPENING_KEY
    );
  });
  await page.getByRole("button", { name: "Find training positions" }).click();

  const requestUrl = new URL((await requestPromise).url());
  expect(requestUrl.searchParams.get("as_of")).toBe(AS_OF);
  expect(requestUrl.searchParams.get("training_requirement_lt")).toBe("0");
  expect(requestUrl.searchParams.get("opening_key")).toBe(OPENING_KEY);
  expect(requestUrl.searchParams.get("opening_match")).toBe("reached");
  expect(requestUrl.searchParams.get("trainer_color")).toBe("black");
  expect(requestUrl.searchParams.get("page")).toBe("1");
  expect(requestUrl.searchParams.get("page_size")).toBe("100");
  expect(catalogueRequests.every((url) => url.searchParams.get("search") === null)).toBe(true);

  await expect(page.getByRole("heading", { name: "training-required positions" })).toBeVisible({
    timeout: 75_000,
  });
  await expect(page.getByRole("list", { name: "training-required positions" })).toBeVisible({
    timeout: 75_000,
  });
  await expect(page.getByText(REPRESENTATIVE_FEN, { exact: true })).toBeVisible({
    timeout: 75_000,
  });
  await expect(page.getByText("g8f6", { exact: true })).toBeVisible({ timeout: 75_000 });

  const total = Number(
    await page.locator("dt").filter({ hasText: "total" }).locator("xpath=..").locator("dd").innerText(),
  );
  expect(await page.getByRole("list", { name: "training-required positions" }).getByRole("listitem").count()).toBe(
    total,
  );
  const retrievedPages = [
    ...new Set(
      trainingRequests.map((url) => Number(url.searchParams.get("page"))),
    ),
  ].sort((left, right) => left - right);
  expect(retrievedPages).toEqual(Array.from({ length: Math.ceil(total / 100) }, (_, index) => index + 1));

  await expect(page.getByRole("heading", { name: /board|session/i })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /board|session/i })).toHaveCount(0);
  await expect(page.getByRole("link", { name: /board|session/i })).toHaveCount(0);
});

test("loads every catalogue page and filters locally without per-keystroke requests", async ({ page }) => {
  const catalogueRequests = await mockCatalogue(page, true);
  await navigateToTrainer(page);

  const opening = page.getByRole("combobox", { name: "Opening" });
  await opening.click();
  await expect(page.getByRole("option", { name: /B10 Caro-Kann Defense/ })).toBeVisible();
  expect(catalogueRequests.map((url) => Number(url.searchParams.get("page")))).toEqual([1, 2]);
  expect(catalogueRequests.every((url) => url.searchParams.get("search") === null)).toBe(true);
  const completeLoadRequestCount = catalogueRequests.length;
  const findButton = page.locator("form").getByRole("button", {
    name: "Find training positions",
    includeHidden: true,
  });

  await opening.pressSequentially("Italian");
  await expect(page.getByRole("option", { name: /C20 Italian Game/ })).toBeVisible();
  expect(catalogueRequests).toHaveLength(completeLoadRequestCount);
  await expect(findButton).toBeDisabled();
});

test("selects committed text on focus or click, then typing replaces it", async ({ page }) => {
  const catalogueRequests = await mockCatalogue(page);
  await navigateToTrainer(page);

  const opening = await chooseSpecificOpening(page);
  await expect(opening).toHaveValue("Caro-Kann Defense");
  await opening.click();
  await expect
    .poll(async () => opening.evaluate((input: HTMLInputElement) => [input.selectionStart, input.selectionEnd]))
    .toEqual([0, "Caro-Kann Defense".length]);
  await opening.pressSequentially("no-match");
  await expect(opening).toHaveValue("no-match");
  await expect(
    page.locator("form").getByRole("button", {
      name: "Find training positions",
      includeHidden: true,
    }),
  ).toBeDisabled();
  expect(catalogueRequests).toHaveLength(1);
});

test("clearing a specific opening is uncommitted rather than All openings", async ({ page }) => {
  await mockCatalogue(page);
  await navigateToTrainer(page);

  const opening = await chooseSpecificOpening(page);
  const findButton = page.getByRole("button", { name: "Find training positions" });
  await expect(findButton).toBeEnabled();
  await page.getByRole("button", { name: "Clear selection" }).click();
  await expect(opening).toHaveValue("");
  await expect(opening).not.toHaveValue("All openings");
  await expect(findButton).toBeDisabled();

  await opening.click();
  const allOption = page.getByRole("option", { name: "All openings" });
  await expect(allOption).toBeVisible();
  await expect(allOption).not.toHaveAttribute("data-selected");
});

test("keeps All openings and Learner colour independent in the request", async ({ page }) => {
  await mockCatalogue(page);
  const trainingRequests: URL[] = [];
  await page.route("**/api/positions/training-requirements**", async (route) => {
    trainingRequests.push(new URL(route.request().url()));
    await fulfillJson(route, trainingResponse());
  });
  await navigateToTrainer(page);

  const opening = await chooseAllOpenings(page);
  await page.getByRole("radio", { name: "White" }).click();
  await expect(opening).toHaveValue("All openings");
  await chooseAsOfDate(page);
  await page.getByRole("button", { name: "Find training positions" }).click();
  await expect(page.getByText("fen-e2e", { exact: true })).toBeVisible();

  const requestUrl = trainingRequests[0];
  expect(requestUrl).toBeDefined();
  expect(requestUrl?.searchParams.get("opening_key")).toBeNull();
  expect(requestUrl?.searchParams.get("opening_match")).toBeNull();
  expect(requestUrl?.searchParams.get("trainer_color")).toBe("white");
  expect(requestUrl?.searchParams.get("as_of")).toBe(AS_OF);
  expect(requestUrl?.searchParams.get("training_requirement_lt")).toBe("0");
  expect(requestUrl?.searchParams.get("page")).toBe("1");
  expect(requestUrl?.searchParams.get("page_size")).toBe("100");
});

test("keeps loading and empty training results in place", async ({ page }) => {
  await mockCatalogue(page);
  let releaseTraining!: () => void;
  const trainingGate = new Promise<void>((resolve) => {
    releaseTraining = resolve;
  });
  await page.route("**/api/positions/training-requirements**", async (route) => {
    await trainingGate;
    await fulfillJson(route, trainingResponse());
  });
  await navigateToTrainer(page);

  await chooseAllOpenings(page);
  await page.getByRole("button", { name: "Find training positions" }).click();
  await expect(page.getByRole("status")).toHaveText("Loading training-required positions...");
  await expect(page.getByRole("heading", { name: "Trainer Practice", level: 1 })).toBeVisible();
  await expect(page.getByRole("combobox", { name: "Opening" })).toBeVisible();
  releaseTraining();
  await expect(page.getByText("fen-e2e", { exact: true })).toBeVisible();

  await page.unroute("**/api/positions/training-requirements**");
  await page.route("**/api/positions/training-requirements**", async (route) => {
    await fulfillJson(route, trainingResponse([], 0));
  });
  await page.getByRole("radio", { name: "Black" }).click();
  await page.getByRole("button", { name: "Find training positions" }).click();
  await expect(page.getByText("No positions currently require training for these filters.")).toBeVisible();
  await expect(page.getByRole("heading", { name: "training-required positions" })).toBeVisible();
  await expect(page.getByRole("list", { name: "training-required positions" })).toHaveCount(0);
});

test("keeps stale-date and retrieval-error feedback in place", async ({ page }) => {
  await mockCatalogue(page);
  let responseStatus = 409;
  await page.route("**/api/positions/training-requirements**", async (route) => {
    await fulfillJson(
      route,
      responseStatus === 409
        ? { code: "training_requirements_stale", message: "stale test response" }
        : TRAINING_ERROR,
      responseStatus,
    );
  });
  await navigateToTrainer(page);

  await chooseAllOpenings(page);
  await page.getByRole("button", { name: "Find training positions" }).click();
  await expect(page.getByRole("alert")).toContainText("Training requirements changed after this date.");
  await expect(page.getByRole("heading", { name: "Trainer Practice", level: 1 })).toBeVisible();
  await expect(page.getByRole("combobox", { name: "Opening" })).toBeVisible();

  responseStatus = 503;
  await page.getByRole("radio", { name: "Black" }).click();
  await page.getByRole("button", { name: "Find training positions" }).click();
  await expect(page.getByRole("alert")).toContainText("Training-required positions could not be loaded.");
  await expect(page.getByRole("combobox", { name: "Opening" })).toBeVisible();
});
