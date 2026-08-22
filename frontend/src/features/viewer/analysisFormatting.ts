import type { EvaluationCandidate } from "./analysisApi";

export function formatScore(candidate: EvaluationCandidate): string {
  if (candidate.score_kind === "cp") {
    const score = candidate.score_value / 100;
    return `${score >= 0 ? "+" : ""}${score.toFixed(2)}`;
  }
  if (candidate.score_kind === "mate_given") {
    return "+M";
  }
  return `${candidate.score_value >= 0 ? "+M" : "-M"}${Math.abs(candidate.score_value)}`;
}
