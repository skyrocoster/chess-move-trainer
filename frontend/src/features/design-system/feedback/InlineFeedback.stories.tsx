import type { Meta, StoryObj } from "@storybook/react-vite";
import "../../../styles/cmt-tokens.css";
import { InlineFeedback } from "./InlineFeedback";
import { FEEDBACK_VARIANTS } from "./feedbackTypes";
import type { FeedbackSeverity } from "./feedbackTypes";

const meta = {
  title: "Design System/Feedback/Inline",
  component: InlineFeedback,
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta<typeof InlineFeedback>;

export default meta;

type Story = StoryObj<typeof meta>;

const SEVERITIES: FeedbackSeverity[] = ["information", "success", "warning", "error"];

const MESSAGES: Record<FeedbackSeverity, string> = {
  information: "The position was loaded and is ready for review.",
  success: "The move was recorded and the position updated.",
  warning: "The pasted position is missing the side to move.",
  error: "The move could not be applied to the current position.",
};

const HEADINGS: Record<FeedbackSeverity, string> = {
  information: "Heads up",
  success: "Saved",
  warning: "Check the paste",
  error: "Not applied",
};

export const InlineMatrix: Story = {
  args: {
    severity: "information",
    message: MESSAGES.information,
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
      <h1
        style={{
          margin: "0 0 var(--cmt-spacing-8)",
          fontSize: "20px",
        }}
      >
        Inline feedback
      </h1>
      <p
        style={{
          margin: "0 0 var(--cmt-spacing-16)",
          fontSize: "13px",
          color: "var(--md-sys-color-on-surface-variant)",
        }}
      >
        Transparent, border-first inline presentations of the four severities.
      </p>
      {SEVERITIES.map((severity) => {
        const tokens = FEEDBACK_VARIANTS[severity].tokens;
        return (
          <section key={severity}>
            <h2
              style={{
                margin: "0 0 var(--cmt-spacing-8)",
                fontSize: "14px",
                textTransform: "capitalize",
              }}
            >
              {severity}
            </h2>
            <p
              style={{
                margin: "0 0 var(--cmt-spacing-8)",
                fontSize: "12px",
                color: "var(--md-sys-color-on-surface-variant)",
              }}
            >
              {tokens.accent} / {tokens.onAccent} / {tokens.container} / {tokens.onContainer}
            </p>
            <InlineFeedback
              severity={severity}
              heading={HEADINGS[severity]}
              message={MESSAGES[severity]}
            />
          </section>
        );
      })}
    </main>
  ),
};
