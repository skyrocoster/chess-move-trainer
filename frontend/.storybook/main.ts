import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  stories: [
    "../src/features/foundation/**/*.stories.@(ts|tsx)",
    "../src/features/design-system/**/*.stories.@(ts|tsx)",
    "../src/features/app-shell/**/*.stories.@(ts|tsx)",
    "../src/features/board-adapter/**/*.stories.@(ts|tsx)",
  ],
  addons: ["@storybook/addon-a11y"],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
};

export default config;
