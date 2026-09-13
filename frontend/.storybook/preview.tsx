import type { Preview } from "@storybook/react-vite";
import "../src/app.css";
import "../src/styles/material/material-theme-builder-css-export/css/dark.css";
import { storybookViewports } from "../src/storybook/viewports";

const preview: Preview = {
  decorators: [
    (Story) => (
      <div className="dark">
        <Story />
      </div>
    ),
  ],
  parameters: {
    a11y: {
      test: "error",
    },
    viewport: {
      options: storybookViewports,
    },
    options: {
      storySort: {
        order: [
          "Production",
          ["Application", "Design System"],
          "In Development",
          ["Application"],
          "Reference",
          ["Design System", "Compositions", "Reviews", "Storybook Fixtures"],
        ],
      },
    },
  },
};

export default preview;
