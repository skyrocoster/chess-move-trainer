import { QueryClient } from "@tanstack/react-query";
import { describe, expect, it, vi } from "vitest";

import {
  invalidateAnalysisObservation,
  invalidatePositionInsight,
  invalidatePreferredMove,
  invalidateTrainingRequirements,
} from "./queryInvalidation";

describe("query invalidation", () => {
  it("uses exact keys for one preferred move and analysis observation", async () => {
    const queryClient = new QueryClient();
    const invalidateQueries = vi.spyOn(queryClient, "invalidateQueries").mockResolvedValue();

    await invalidatePreferredMove(queryClient, {
      positionKey: "position",
      today: "2026-09-14",
      tomorrow: "2026-09-15",
    });
    await invalidateAnalysisObservation(queryClient, "position");

    expect(invalidateQueries).toHaveBeenNthCalledWith(1, {
      queryKey: ["preferredMove", "position", { today: "2026-09-14", tomorrow: "2026-09-15" }],
      exact: true,
    });
    expect(invalidateQueries).toHaveBeenNthCalledWith(2, {
      queryKey: ["analysisObservation", "position"],
      exact: true,
    });
  });

  it("uses only the approved family prefixes for broad invalidation", async () => {
    const queryClient = new QueryClient();
    const invalidateQueries = vi.spyOn(queryClient, "invalidateQueries").mockResolvedValue();

    await invalidateTrainingRequirements(queryClient);
    await invalidatePositionInsight(queryClient, "position");

    expect(invalidateQueries).toHaveBeenNthCalledWith(1, {
      queryKey: ["trainingRequirements"],
    });
    expect(invalidateQueries).toHaveBeenNthCalledWith(2, {
      queryKey: ["positionInsight", "position"],
    });
  });
});
