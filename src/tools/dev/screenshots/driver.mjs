#!/usr/bin/env node
// Playwright driver for `sg screenshot`.
//
// The Python command writes request.json and invokes this file with Node. The
// driver captures every job in one browser session, writes manifest.json, and
// reports page/console/network problems so a reviewer can see them without
// opening developer tools.

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { pathToFileURL } from "node:url";

const DETAIL_LIMIT = 50;

function log(message) {
  process.stderr.write(`${message}\n`);
}

function fail(message) {
  process.stderr.write(`screenshot: ${message}\n`);
  process.exit(1);
}

function errorText(error) {
  const text = error instanceof Error ? error.message : String(error);
  return text.length <= 2_000 ? text : `${text.slice(0, 1_999)}…`;
}

async function loadChromium(repositoryRoot) {
  const candidates = [];
  try {
    candidates.push(await import("playwright"));
  } catch (primaryError) {
    const fallback = path.join(repositoryRoot, "frontend", "node_modules", "playwright", "index.mjs");
    try {
      candidates.push(await import(pathToFileURL(fallback).href));
    } catch {
      fail(
        `Playwright is unavailable (${errorText(primaryError)}). Run \`npm ci\` in the` +
          " repository root and `npx playwright install chromium` once.",
      );
    }
  }
  const playwright = candidates.at(-1);
  if (!playwright || !playwright.chromium) {
    fail("The Playwright package does not expose Chromium. Reinstall the root npm packages.");
  }
  return playwright.chromium;
}

function appendLimited(list, value, counts, key) {
  counts[key] += 1;
  if (list.length < DETAIL_LIMIT) {
    list.push(value);
  }
}

const WRITE_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);
const ACTION_TIMEOUT_MS = 5_000;
const SETTLE_TIMEOUT_MS = 2_000;
const OPTIONAL_TIMEOUT_MS = 1_000;

/** Return the configured rule when a response is a documented empty state. */
function expectedHttpError(rules, method, url, status) {
  let pathname;
  try {
    pathname = new URL(url).pathname;
  } catch {
    return null;
  }
  return (
    rules.find(
      (rule) =>
        rule.status === status && rule.method === method && new RegExp(rule.path).test(pathname),
    ) || null
  );
}

function describeAction(action) {
  const target = action.target
    ? Object.entries(action.target)
        .map(([key, value]) => `${key}=${JSON.stringify(value)}`)
        .join(" ")
    : "";
  const extra = action.kind === "press" ? ` ${action.key}` : "";
  return `${action.kind} ${target}${extra}`.trim();
}

function locate(page, target) {
  const exact = target.exact !== false;
  let locator;
  if (target.role) {
    locator = page.getByRole(target.role, target.name ? { name: target.name, exact } : {});
  } else if (target.label) locator = page.getByLabel(target.label, { exact });
  else if (target.text) locator = page.getByText(target.text, { exact });
  else locator = page.locator(target.css);
  return Number.isInteger(target.nth) ? locator.nth(target.nth) : locator;
}

async function runAction(page, action, timeout) {
  if (action.kind === "press") {
    await page.keyboard.press(action.key);
    return;
  }
  const locator = locate(page, action.target);
  if (action.optional) {
    // Layouts differ by viewport: skip a step whose control is not there.
    const present = await locator
      .waitFor({ state: "visible", timeout: OPTIONAL_TIMEOUT_MS })
      .then(() => true)
      .catch(() => false);
    if (!present) return "skipped";
  }
  if (action.kind === "fill") await locator.fill(action.text ?? "", { timeout });
  else if (action.kind === "click") await locator.click({ timeout });
  else if (action.kind === "wait_for") await locator.waitFor({ state: "visible", timeout });
  else if (action.kind === "scroll")
    await locator.evaluate((element) => element.scrollIntoView({ block: "start" }), undefined, {
      timeout,
    });
  else throw new Error(`unknown action kind ${action.kind}`);
}

// reducedMotion does not stop CSS transitions, so wait for every finite
// animation and transition on the page to finish (bounded).
async function settleAnimations(page) {
  await page
    .evaluate(
      (limit) =>
        Promise.race([
          Promise.allSettled(
            document
              .getAnimations()
              .filter((animation) => {
                const timing = animation.effect && animation.effect.getComputedTiming();
                return timing && Number.isFinite(timing.endTime);
              })
              .map((animation) => animation.finished),
          ),
          new Promise((resolve) => setTimeout(resolve, limit)),
        ]),
      SETTLE_TIMEOUT_MS,
    )
    .catch(() => {});
}

async function captureJob(browser, job, expectedHttpErrors) {
  const started = performance.now();
  const counts = {
    console_errors: 0,
    page_errors: 0,
    failed_requests: 0,
    http_errors: 0,
    blocked_writes: 0,
    expected_http_errors: 0,
    expected_console_errors: 0,
  };
  const result = {
    name: job.name,
    description: job.description || "",
    url: job.url,
    file: job.file,
    relative_file: job.relative_file,
    viewport: job.viewport.name,
    viewport_width: job.viewport.width,
    viewport_height: job.viewport.height,
    width: null,
    height: null,
    title: "",
    status_code: null,
    full_page: Boolean(job.full_page),
    selector: job.selector || "",
    duration_ms: 0,
    console_errors: [],
    page_errors: [],
    failed_requests: [],
    http_errors: [],
    blocked_writes: [],
    expected_http_errors: [],
    expects_writes: Boolean(job.expects_writes),
    actions: [],
    counts,
    bytes: null,
    error: null,
  };

  let context;
  let collecting = true;
  try {
    context = await browser.newContext({
      viewport: { width: job.viewport.width, height: job.viewport.height },
      deviceScaleFactor: 1,
      reducedMotion: "reduce",
      // A service worker could send requests that context.route cannot see.
      serviceWorkers: "block",
    });
    // Read-only guard: a capture must never change data, so every POST, PUT,
    // PATCH and DELETE is aborted and recorded, whatever its origin or path.
    await context.route("**/*", (route) => {
      const request = route.request();
      if (WRITE_METHODS.has(request.method())) {
        if (collecting) {
          appendLimited(
            result.blocked_writes,
            { url: request.url(), method: request.method() },
            counts,
            "blocked_writes",
          );
        }
        return route.abort("blockedbyclient");
      }
      return route.continue();
    });
    const page = await context.newPage();

    page.on("console", (message) => {
      if (!collecting || message.type() !== "error") return;
      const text = message.text().slice(0, 2_000);
      // Chromium logs a failed resource separately from the response event. Suppress the
      // duplicate only when the documented optional-state rule matches its URL and status.
      const status = Number((/status of ([0-9]{3})/.exec(text) || [])[1] || 0);
      const location = message.location();
      if (status && expectedHttpError(expectedHttpErrors, "GET", location.url, status)) {
        counts.expected_console_errors += 1;
        return;
      }
      appendLimited(result.console_errors, { type: message.type(), text }, counts, "console_errors");
    });
    page.on("pageerror", (error) => {
      if (!collecting) return;
      appendLimited(result.page_errors, errorText(error), counts, "page_errors");
    });
    page.on("requestfailed", (request) => {
      if (!collecting) return;
      if (WRITE_METHODS.has(request.method()) && request.failure()?.errorText.includes("BLOCKEDBYCLIENT")) return;
      const failure = request.failure();
      appendLimited(
        result.failed_requests,
        {
          url: request.url(),
          method: request.method(),
          resource_type: request.resourceType(),
          failure: failure ? failure.errorText : "request failed",
        },
        counts,
        "failed_requests",
      );
    });
    page.on("response", (response) => {
      if (!collecting || response.status() < 400) return;
      const status = response.status();
      const expected = expectedHttpError(
        expectedHttpErrors,
        response.request().method(),
        response.url(),
        status,
      );
      if (expected) {
        appendLimited(
          result.expected_http_errors,
          { url: response.url(), status, reason: expected.reason },
          counts,
          "expected_http_errors",
        );
        return;
      }
      appendLimited(
        result.http_errors,
        { url: response.url(), status },
        counts,
        "http_errors",
      );
    });

    const response = await page.goto(job.url, {
      waitUntil: "load",
      timeout: job.timeout_ms,
    });
    result.status_code = response ? response.status() : null;
    result.title = await page.title().catch(() => "");

    await page
      .evaluate(() => (document.fonts ? document.fonts.ready : Promise.resolve()))
      .catch(() => {});
    await page
      .waitForLoadState("networkidle", { timeout: Math.min(2_000, job.timeout_ms) })
      .catch(() => {});
    const actionTimeout = Math.min(ACTION_TIMEOUT_MS, job.timeout_ms);
    for (const [index, action] of (job.actions || []).entries()) {
      const record = { kind: action.kind, description: describeAction(action), ok: false };
      result.actions.push(record);
      try {
        // A wait is explicitly open-ended; use the capture timeout instead of the click budget.
        const timeout = action.kind === "wait_for" ? job.timeout_ms : actionTimeout;
        const outcome = await runAction(page, action, timeout);
        if (outcome === "skipped") record.skipped = true;
        record.ok = true;
      } catch (error) {
        throw new Error(
          `${job.name}: action ${index + 1} (${record.description}) failed: ${errorText(error)}`,
        );
      }
    }
    if (job.wait_for) {
      await page
        .locator(job.wait_for)
        .filter({ visible: true })
        .first()
        .waitFor({ state: "visible", timeout: job.timeout_ms });
    }
    // Images created in script (map portrait tokens) are not in document.images; let their requests finish.
    await page
      .waitForLoadState("networkidle", { timeout: Math.min(2_000, job.timeout_ms) })
      .catch(() => {});
    if (job.wait_ms > 0) {
      await page.waitForTimeout(job.wait_ms);
    }
    // Images load after the page "load" event when they are rendered later (list rows, inspectors), so
    // wait for every visible <img> to be decoded; a broken one counts as finished. Offscreen lazy images
    // are deliberately not fetched until they scroll into view, so waiting for them only burns the timeout.
    await page
      .evaluate(
        (limitMs) =>
          Promise.race([
            Promise.all(
              // decode() resolves once the image is loaded and ready to paint (rejects when broken).
              Array.from(document.images)
                .filter((img) => {
                  if (img.loading !== "lazy") return true;
                  const box = img.getBoundingClientRect();
                  return (
                    box.width > 0 &&
                    box.height > 0 &&
                    box.bottom > 0 &&
                    box.top < window.innerHeight &&
                    box.right > 0 &&
                    box.left < window.innerWidth
                  );
                })
                .map((img) => img.decode().catch(() => {})),
            ),
            new Promise((resolve) => setTimeout(resolve, limitMs)),
          ]),
        Math.min(15_000, job.timeout_ms),
      )
      .catch(() => {});
    await settleAnimations(page);
    await page
      .evaluate(
        () =>
          new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))),
      )
      .catch(() => {});

    await fs.mkdir(path.dirname(job.file), { recursive: true });
    if (job.selector) {
      const locator = page.locator(job.selector).filter({ visible: true }).first();
      await locator.waitFor({ state: "visible", timeout: job.timeout_ms });
      const box = await locator.boundingBox();
      result.width = box ? Math.round(box.width) : null;
      result.height = box ? Math.round(box.height) : null;
      await locator.screenshot({
        path: job.file,
        animations: "disabled",
        caret: "hide",
        timeout: job.timeout_ms,
      });
    } else {
      const size = await page
        .evaluate(() => ({
          width: Math.max(
            document.documentElement.scrollWidth,
            document.body ? document.body.scrollWidth : 0,
            window.innerWidth,
          ),
          height: Math.max(
            document.documentElement.scrollHeight,
            document.body ? document.body.scrollHeight : 0,
            window.innerHeight,
          ),
        }))
        .catch(() => null);
      result.width = job.full_page && size ? Math.ceil(size.width) : job.viewport.width;
      result.height = job.full_page && size ? Math.ceil(size.height) : job.viewport.height;
      await page.screenshot({
        path: job.file,
        fullPage: Boolean(job.full_page),
        animations: "disabled",
        caret: "hide",
        timeout: job.timeout_ms,
      });
    }

    const stat = await fs.stat(job.file);
    result.bytes = stat.size;
    if (stat.size === 0) {
      throw new Error("the screenshot file is empty");
    }
  } catch (error) {
    result.error = errorText(error);
  } finally {
    collecting = false;
    if (context) {
      await context.close().catch(() => {});
    }
    result.duration_ms = Math.round(performance.now() - started);
  }
  return result;
}

function summaries(screenshots, skipped) {
  const summary = {
    requested: screenshots.length,
    captured: 0,
    failed: 0,
    console_errors: 0,
    page_errors: 0,
    failed_requests: 0,
    http_errors: 0,
    blocked_writes: 0,
    unexpected_blocked_writes: 0,
    expected_http_errors: 0,
    expected_console_errors: 0,
    skipped: skipped.length,
  };
  for (const screenshot of screenshots) {
    if (screenshot.error) {
      summary.failed += 1;
    } else {
      summary.captured += 1;
    }
    for (const key of [
      "console_errors",
      "page_errors",
      "failed_requests",
      "http_errors",
      "expected_http_errors",
      "expected_console_errors",
    ]) {
      summary[key] += screenshot.counts[key] || 0;
    }
    summary.blocked_writes += screenshot.counts.blocked_writes || 0;
    if (!screenshot.expects_writes) {
      summary.unexpected_blocked_writes += screenshot.counts.blocked_writes || 0;
    }
  }
  return summary;
}

async function run(plan) {
  const chromium = await loadChromium(plan.repository_root || process.cwd());
  const started = new Date().toISOString();
  const startedAt = performance.now();
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
  } catch (error) {
    fail(
      `Could not launch Chromium: ${errorText(error)}.` +
        " Run `npx playwright install chromium` once on this machine.",
    );
  }

  const screenshots = new Array(plan.jobs.length);
  let nextJob = 0;
  async function captureNextJob() {
    while (nextJob < plan.jobs.length) {
      const index = nextJob++;
      const job = plan.jobs[index];
      log(`[${index + 1}/${plan.jobs.length}] ${job.viewport.name} ${job.name}`);
      const result = await captureJob(browser, job, plan.expected_http_errors || []);
      screenshots[index] = result;
      if (result.error) {
        log(`  failed: ${result.error}`);
      }
    }
  }
  try {
    // Each capture owns its context and write guard; keep at most two active,
    // matching the browser-test worker limit while retaining catalogue order.
    await Promise.all(Array.from({ length: Math.min(2, plan.jobs.length) }, captureNextJob));
  } finally {
    await browser.close().catch(() => {});
  }

  return {
    version: 1,
    run_id: plan.run_id,
    started_at: started,
    finished_at: new Date().toISOString(),
    duration_ms: Math.round(performance.now() - startedAt),
    base_url: plan.base_url,
    output_dir: plan.output_dir,
    relative_output_dir: plan.relative_output_dir,
    viewports: plan.viewports,
    full_page: plan.full_page,
    expected_http_errors: plan.expected_http_errors || [],
    screenshots,
    skipped: plan.skipped || [],
    summary: summaries(screenshots, plan.skipped || []),
  };
}

async function main() {
  const requestPath = process.argv[2];
  if (!requestPath) {
    fail("Usage: node driver.mjs <request.json>");
  }
  let plan;
  try {
    plan = JSON.parse(await fs.readFile(requestPath, "utf8"));
  } catch (error) {
    fail(`Could not read the screenshot request at ${requestPath}: ${errorText(error)}`);
  }
  if (
    !plan ||
    !Array.isArray(plan.jobs) ||
    (plan.jobs.length === 0 && !(plan.skipped && plan.skipped.length))
  ) {
    fail("The screenshot request contains no jobs.");
  }
  if (!plan.output_dir) {
    fail("The screenshot request has no output directory.");
  }

  await fs.mkdir(plan.output_dir, { recursive: true });
  const manifest = await run(plan);
  const manifestPath = path.join(plan.output_dir, "manifest.json");
  await fs.writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  log(`Manifest: ${manifestPath}`);
}

await main();
