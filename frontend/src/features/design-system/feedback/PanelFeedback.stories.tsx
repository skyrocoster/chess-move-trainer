import "../../../styles/cmt-tokens.css";

import type { Meta, StoryObj } from "@storybook/react-vite";

import { PanelFeedback } from "./PanelFeedback";
import styles from "./PanelFeedback.module.css";

const meta = {
  title: "Feedback/PanelMatrix",
  component: PanelFeedback,
  parameters: {
    layout: "fullscreen",
  },
  render: () => (
    <div className={styles.storyGrid}>
      <PanelFeedback
        severity="information"
        heading="Information"
        message="The opening position is ready for review."
      />
      <PanelFeedback
        severity="success"
        heading="Success"
        message="The selected move matches the accepted line."
      />
      <PanelFeedback
        severity="warning"
        heading="Warning"
        message="This move leaves the king exposed to a developing attack."
      />
      <PanelFeedback
        severity="error"
        heading="Error"
        message="The submitted move is not legal in the current position."
      />
    </div>
  ),
} satisfies Meta<typeof PanelFeedback>;

export default meta;

type Story = StoryObj<typeof meta>;

export const AllSeverities: Story = {
  args: {
    severity: "information",
    heading: "Information",
    message: "The opening position is ready for review.",
  },
};
