import eslint from "@eslint/js";
import tseslint from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";

export default tseslint.config(
  { ignores: ["dist", "node_modules", "storybook-static", "src/api/generated"] },
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    plugins: { "react-hooks": reactHooks, "react-refresh": reactRefresh },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
    },
  },
  {
    files: [
      "**/*.test.{ts,tsx}",
      "src/test-utils/**",
      "src/features/repertoire-builder/repertoireBuilderTestHelpers.tsx",
      "src/features/repertoire-builder/PreferredMovePanelSections.tsx",
    ],
    rules: {
      "react-refresh/only-export-components": "off",
    },
  },
);
