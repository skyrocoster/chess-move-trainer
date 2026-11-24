import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ["recharts"],
  },
  test: {
    projects: [
      {
        extends: true,
        test: {
          name: "unit",
          environment: "jsdom",
          setupFiles: ["./src/test-setup.ts"],
          include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
          // The real-server health check runs through the focused API config
          // (frontend/vitest.api.config.ts), not the fast unit project.
          exclude: ["src/api/healthClient.test.ts"],
          // Cap the unit project at six workers.
          maxWorkers: 6,
          sequence: {
            groupOrder: 1,
          },
        },
      },
    ],
  },
});
