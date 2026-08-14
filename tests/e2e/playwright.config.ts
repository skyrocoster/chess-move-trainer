import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  timeout: 15_000,
  use: { baseURL: "http://localhost:8444", headless: true },
  webServer: [
    {
      command: ".venv\\Scripts\\python.exe -m uvicorn backend.app.main:app --host localhost --port 5666",
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
  ],
});
