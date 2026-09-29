import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { StatusView, type StatusDetail, type StatusViewState } from "./StatusView";

const meta = {
  title: "Production/Application/Status/Status View",
  tags: ["status-production"],
  component: StatusView,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof StatusView>;

export default meta;
type Story = StoryObj<typeof meta>;

const detail: StatusDetail = {
  workers: [
    { service: "worker", index: 1, running: true },
    { service: "worker-six", index: 1, running: false },
    { service: "worker-six", index: 2, running: false },
  ],
  analysis: { positions: 1200, analyzed: 1000, queued: 20, running: 4, remaining: 176 },
  lastGameAt: "2026-09-20T12:00:00+00:00",
};

const frame = (state: StatusViewState) => (
  <main
    style={{
      minHeight: "100vh",
      padding: "var(--cmt-spacing-24)",
      background: "var(--md-sys-color-background)",
      color: "var(--md-sys-color-on-background)",
    }}
  >
    <StatusView state={state} />
  </main>
);

export const Loading: Story = {
  args: { state: { kind: "loading" } },
  render: () => frame({ kind: "loading" }),
};

export const Healthy: Story = {
  args: { state: { kind: "success" } },
  render: () => frame({ kind: "success" }),
};

export const HealthyWithDetail: Story = {
  args: { state: { kind: "success", detail } },
  render: () => frame({ kind: "success", detail }),
};

export const WorkersStopped: Story = {
  args: {
    state: {
      kind: "success",
      detail: { ...detail, workers: [], analysis: null, lastGameAt: null },
    },
  },
  render: () =>
    frame({
      kind: "success",
      detail: { ...detail, workers: [], analysis: null, lastGameAt: null },
    }),
};

export const Unavailable: Story = {
  args: { state: { kind: "error" } },
  render: () => frame({ kind: "error" }),
};
