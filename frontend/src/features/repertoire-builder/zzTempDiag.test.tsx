import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it } from "vitest";

import { storyCandidateAnalysisClient } from "../viewer/viewerStoryHelpers";
import RepertoireBuilderWorkspace from "./RepertoireBuilderWorkspace";
import {
  storyPositionContextClient,
  storyPreferredMoveClient,
} from "./repertoireBuilderStoryHelpers";

it("reproduces first-choice-from-empty save flow", async () => {
  const user = userEvent.setup();
  render(
    <main>
      <RepertoireBuilderWorkspace
        analysisClient={storyCandidateAnalysisClient(["e2e4"])}
        preferredMoveClient={storyPreferredMoveClient({ relationship: "empty" })}
        positionContextClient={storyPositionContextClient({
          overall_exists: true,
          white_count: 3,
          black_count: 2,
        })}
      />
    </main>,
  );
  await screen.findByTestId("repertoire-session");
  await user.click(await screen.findByRole("button", { name: "1. e4" }));
  await screen.findByText("My move staged: e4.");
  const save = screen.getByRole("button", { name: "Save" });
  expect(save).toBeEnabled();
  await user.click(save);
  await new Promise((resolve) => setTimeout(resolve, 1000));
  // eslint-disable-next-line no-console
  console.log("STATUS:", JSON.stringify(screen.getByTestId("session-status").textContent));
  // eslint-disable-next-line no-console
  console.log("ALERT:", JSON.stringify(screen.queryByRole("alert")?.textContent ?? null));
  // eslint-disable-next-line no-console
  console.log("SAVED-MOVE:", JSON.stringify(screen.getByTestId("saved-move").textContent));
  // eslint-disable-next-line no-console
  console.log("STAGED-MOVE:", JSON.stringify(screen.getByTestId("staged-move").textContent));
  expect(screen.getByTestId("session-status")).toHaveTextContent("Preferred move saved.");
});
