import userEvent from "@testing-library/user-event";
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import "./RepertoireBuilderWorkspace.testSetup";
import type { MoveResponseDistributionResult } from "../move-response-distribution/moveResponseDistributionApi";
import {
  moveResponseDistributionResponse,
  renderWorkspace,
  STARTING_FEN,
} from "./repertoireBuilderTestHelpers";

afterEach(() => cleanup());

describe("RepertoireBuilderWorkspace move response distribution", () => {
  it("clears distribution replies during replacement and ignores a stale canonical response", async () => {
    const user = userEvent.setup();
    const pending: Array<{
      resolve: (result: MoveResponseDistributionResult) => void;
      signal?: AbortSignal;
    }> = [];
    const client = vi.fn(
      (_fen: string, _color: "white" | "black", signal?: AbortSignal) =>
        new Promise<MoveResponseDistributionResult>((resolve) => {
          pending.push({ resolve, signal });
        }),
    );
    renderWorkspace({ moveResponseDistributionClient: client });
    await waitFor(() => expect(client).toHaveBeenCalledOnce());

    await user.click(screen.getByRole("button", { name: "Flip" }));
    expect(pending[0]?.signal?.aborted).toBe(true);
    expect(screen.getByTestId("move-response-distribution")).toHaveAttribute(
      "data-state",
      "loading",
    );
    expect(screen.queryByRole("button", { name: /Show other replies/ })).not.toBeInTheDocument();

    pending[0]!.resolve({
      status: "success",
      data: moveResponseDistributionResponse(STARTING_FEN, "white"),
    });
    await waitFor(() => expect(client).toHaveBeenCalledTimes(2));
    expect(screen.getByTestId("move-response-distribution")).toHaveAttribute(
      "data-state",
      "loading",
    );
    expect(screen.queryByText("White repertoire colour", { exact: true })).not.toBeInTheDocument();

    pending[1]!.resolve({
      status: "success",
      data: moveResponseDistributionResponse(STARTING_FEN, "black"),
    });
    await waitFor(() =>
      expect(screen.getByTestId("move-response-distribution")).toHaveAttribute(
        "data-state",
        "available",
      ),
    );
    expect(
      within(screen.getByTestId("move-response-distribution")).getByText(
        "Black repertoire colour",
        {
          exact: true,
        },
      ),
    ).toBeVisible();
  });
});
