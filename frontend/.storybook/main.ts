import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  stories: [
    "../src/features/design-system/**/*.stories.@(ts|tsx)",
    "../src/features/move-history/**/*.stories.@(ts|tsx)",
    "../src/features/app-shell/**/*.stories.@(ts|tsx)",
    "../src/features/status/**/*.stories.@(ts|tsx)",
    "../src/features/analysis/**/*.stories.@(ts|tsx)",
    "../src/features/board-adapter/**/*.stories.@(ts|tsx)",
    "../src/features/repertoire-builder/**/*.stories.@(ts|tsx)",
    "../src/features/openings/**/*.stories.@(ts|tsx)",
    "../src/features/viewer/**/*.stories.@(ts|tsx)",
  ],
  addons: ["@storybook/addon-a11y", "@storybook/addon-vitest"],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
};

export default config;
