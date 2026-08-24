import "../../../styles/cmt-tokens.css";

import type { Meta, StoryObj } from "@storybook/react-vite";

import { PageFeedback } from "./PageFeedback";
import styles from "./PageFeedback.module.css";

const meta = {
  title: "Design System/Feedback/Page",
  component: PageFeedback,
  parameters: {
    layout: "fullscreen",
  },
  render: () => (
    <div className={styles.storyGrid}>
      <PageFeedback
        severity="information"
        heading="Information"
        message="This page contains the full move-training session."
      />
      <PageFeedback
        severity="success"
        heading="Success"
        message="All moves on this page match the accepted line."
      />
      <PageFeedback
        severity="warning"
        heading="Warning"
        message="Several moves on this page still await review."
      />
      <PageFeedback
        severity="error"
        heading="Error"
        message="This page contains moves that do not match the accepted line."
      />
    </div>
  ),
} satisfies Meta<typeof PageFeedback>;

export default meta;

type Story = StoryObj<typeof meta>;

export const AllSeverities: Story = {
  args: {
    severity: "information",
    heading: "Information",
    message: "This page contains the full move-training session.",
  },
};
