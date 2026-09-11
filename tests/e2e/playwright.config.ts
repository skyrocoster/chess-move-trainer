import { defineConfig } from "@playwright/test";

const STORYBOOK_TEST_FILES = new Set([
  "board-adapter-storybook.spec.ts",
  "design-system-accessibility-storybook.spec.ts",
  "responsive-shell-storybook.spec.ts",
  "repertoire-builder-storybook.spec.ts",
  "repertoire-builder-storybook-behaviors.spec.ts",
  "analysis-panel-storybook.spec.ts",
  "line-library-storybook.spec.ts",
]);

const APP_TEST_FILES = new Set([
  "responsive-shell.spec.ts",
  "shell-routing.spec.ts",
  "status-page.spec.ts",
]);

function selectedTestFiles() {
  return process.argv
    .map((argument) => argument.split(/[\\/]/).pop() ?? argument)
    .map((argument) => argument.replace(/:\d+$/, ""))
    .filter((argument) => /(?:spec|test)\.[cm]?[jt]sx?$/.test(argument));
}

function serverProfile() {
  const selected = selectedTestFiles();
  if (selected.length === 0) {
    return "all";
  }
  if (selected.every((file) => STORYBOOK_TEST_FILES.has(file))) {
    return "storybook";
  }
  if (selected.every((file) => APP_TEST_FILES.has(file))) {
    return "app";
  }
  return "all";
}

const appWebServers = [
  {
    command:
      ".venv\\Scripts\\python.exe -m uvicorn backend.app.main:app --host localhost --port 5666",
    url: "http://localhost:5666/api/health",
    cwd: process.cwd(),
    reuseExistingServer: true,
  },
  {
    command: "npm run dev --prefix frontend",
    url: "http://localhost:8444",
    cwd: process.cwd(),
    reuseExistingServer: true,
  },
];

const storybookWebServer = {
  command: "npm run storybook --prefix frontend",
  url: "http://localhost:6006",
  cwd: process.cwd(),
  reuseExistingServer: true,
  timeout: 30_000,
};

const profile = serverProfile();

export default defineConfig({
  testDir: ".",
  fullyParallel: true,
  workers: 2,
  timeout: 15_000,
  use: { baseURL: "http://localhost:8444", headless: true },
  webServer:
    profile === "storybook"
      ? storybookWebServer
      : profile === "app"
        ? appWebServers
        : [...appWebServers, storybookWebServer],
});
