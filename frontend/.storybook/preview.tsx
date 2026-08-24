import type { Preview } from "@storybook/react-vite";
import "../src/app.css";
import "../src/styles/material/material-theme-builder-css-export/css/dark.css";

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
  },
};

export default preview;
