import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../../styles/cmt-tokens.css";
import { FeedbackCore } from "./FeedbackCore";
import { FEEDBACK_VARIANTS } from "./feedbackTypes";
import type { FeedbackSeverity } from "./feedbackTypes";

const meta = {
  title: "Feedback/SemanticVariants",
  component: FeedbackCore,
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta<typeof FeedbackCore>;

export default meta;

type Story = StoryObj<typeof meta>;

const SEVERITIES: FeedbackSeverity[] = ["information", "success", "warning", "error"];

const MESSAGES: Record<FeedbackSeverity, string> = {
  information: "The position was loaded and is ready for review.",
  success: "The move was recorded and the position updated.",
  warning: "The pasted position is missing the side to move.",
  error: "The move could not be applied to the current position.",
};

export const SemanticVariants: Story = {
  args: {
    severity: "information",
    message: "The position was loaded and is ready for review.",
  },
  render: () => (
    <main
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "var(--cmt-spacing-24)",
        padding: "var(--cmt-spacing-24)",
        minHeight: "100vh",
        backgroundColor: "var(--md-sys-color-surface)",
        color: "var(--md-sys-color-on-surface)",
        fontFamily: "system-ui",
      }}
    >
      {SEVERITIES.map((severity) => {
        const tokens = FEEDBACK_VARIANTS[severity].tokens;
        return (
          <section key={severity}>
            <h2
              style={{
                margin: "0 0 var(--cmt-spacing-8)",
                fontSize: "16px",
                textTransform: "capitalize",
              }}
            >
              {severity}
            </h2>
            <p
              style={{
                margin: "0 0 var(--cmt-spacing-8)",
                fontSize: "13px",
                color: "var(--md-sys-color-on-surface-variant)",
              }}
            >
              {tokens.accent} / {tokens.onAccent} / {tokens.container} / {tokens.onContainer}
            </p>
            <FeedbackCore
              severity={severity}
              heading={severity === "information" ? "Heads up" : undefined}
              message={MESSAGES[severity]}
            />
          </section>
        );
      })}
    </main>
  ),
};
