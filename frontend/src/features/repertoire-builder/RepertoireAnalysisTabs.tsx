import { AnalysisPanel, type AnalysisPanelProps } from "../analysis/AnalysisPanel";
import { Tabs, type TabDefinition } from "../design-system/Tabs";
import {
  MoveResponseDistribution,
  type MoveResponseDistributionProps,
} from "../move-response-distribution/MoveResponseDistribution";

export type RepertoireAnalysisTabsProps = {
  analysis: Omit<AnalysisPanelProps, "embedded">;
  moveResponseDistribution: Omit<MoveResponseDistributionProps, "embedded">;
};

export function RepertoireAnalysisTabs({
  analysis,
  moveResponseDistribution,
}: RepertoireAnalysisTabsProps) {
  const tabs: readonly TabDefinition[] = [
    {
      id: "analysis",
      label: "Analysis",
      content: <AnalysisPanel {...analysis} embedded />,
    },
    {
      id: "move-responses",
      label: "Move responses",
      content: <MoveResponseDistribution {...moveResponseDistribution} embedded />,
    },
  ];

  return <Tabs ariaLabel="Analysis and move responses" defaultSelectedId="analysis" tabs={tabs} />;
}
