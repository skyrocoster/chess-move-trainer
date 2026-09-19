import { QueryClientProvider } from "@tanstack/react-query";
import type { Preview } from "@storybook/react-vite";
import { useState, type ReactNode } from "react";
import "../src/app.css";
import "../src/styles/material/material-theme-builder-css-export/css/dark.css";
import { storybookViewports } from "../src/storybook/viewports";
import { createTestQueryClient } from "../src/test-utils/QueryClientTestProvider";

function StorybookQueryClientProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(createTestQueryClient);
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

const preview: Preview = {
  decorators: [
    (Story) => (
      <StorybookQueryClientProvider>
        <div className="dark">
          <Story />
        </div>
      </StorybookQueryClientProvider>
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
          ["Catalogue", "Design System", "Compositions", "Reviews", "Storybook Fixtures"],
        ],
      },
    },
  },
};

export default preview;
