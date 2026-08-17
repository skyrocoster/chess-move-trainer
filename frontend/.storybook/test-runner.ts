import type { TestRunnerConfig } from "@storybook/test-runner";

const config: TestRunnerConfig = {
  async preVisit(page, context) {
    const isConstrained =
      context.title === "App Shell/AppShell" &&
      (context.name === "ConstrainedOpen" ||
        context.name === "ConstrainedClosed" ||
        context.id === "app-shell-appshell--constrained-open" ||
        context.id === "app-shell-appshell--constrained-closed");

    await page.setViewportSize(
      isConstrained ? { width: 412, height: 915 } : { width: 1280, height: 720 },
    );
  },
};

export default config;
