import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  stories: [
    "../src/features/design-system/**/*.stories.@(ts|tsx)",
    "../src/features/move-history/**/*.stories.@(ts|tsx)",
    "../src/features/move-response-distribution/**/*.stories.@(ts|tsx)",
    "../src/features/app-shell/**/*.stories.@(ts|tsx)",
    "../src/features/status/**/*.stories.@(ts|tsx)",
    "../src/features/analysis/**/*.stories.@(ts|tsx)",
    "../src/features/board-adapter/**/*.stories.@(ts|tsx)",
    "../src/features/repertoire-builder/**/*.stories.@(ts|tsx)",
    "../src/features/openings/**/*.stories.@(ts|tsx)",
    "../src/features/position-reach-frequency/**/*.stories.@(ts|tsx)",
  ],
  addons: ["@storybook/addon-a11y", "@storybook/addon-vitest"],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
  viteFinal: (config) => {
    // The static Storybook build bundles the monolithic axe-core engine
    // (@storybook/addon-a11y) and the preview iframe runtime, which exceed
    // Vite's default 500 kB chunk-size advisory. These are Storybook tooling
    // chunks, not application code; the app build stays code-split and below
    // the default limit.
    config.build ??= {};
    config.build.chunkSizeWarningLimit = 1600;
    return config;
  },
};

export default config;
