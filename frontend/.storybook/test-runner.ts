import type { TestRunnerConfig } from "@storybook/test-runner";

const config: TestRunnerConfig = {
  async preVisit(page, context) {
    const isConstrained =
      context.title === "Application/Shell" &&
      (context.name === "ConstrainedOpen" ||
        context.name === "ConstrainedClosed" ||
        context.id === "application-shell--constrained-open" ||
        context.id === "application-shell--constrained-closed");

    await page.setViewportSize(
      isConstrained ? { width: 412, height: 915 } : { width: 1280, height: 720 },
    );
  },
};

export default config;
