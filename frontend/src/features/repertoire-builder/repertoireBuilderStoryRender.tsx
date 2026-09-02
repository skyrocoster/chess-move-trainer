import type { ComponentProps, ReactNode } from "react";

import type { Game } from "../viewer/gameModel";
import { storyAnalysisClient } from "../viewer/viewerStoryHelpers";
import { VIEWER_GAME } from "../viewer/viewerFixtures";
import RepertoireBuilderWorkspace from "./RepertoireBuilderWorkspace";
import {
  storyPositionContextClient,
  storyMoveResponseDistributionClient,
  storyPreferredMoveClient,
  type StoryPositionContextOptions,
  type StoryPreferredMoveOptions,
} from "./repertoireBuilderStoryHelpers";

export const BLACK_SUBJECT_GAME: Game = { ...VIEWER_GAME, subject_color: "black" };

export const constrainedViewport = {
  viewport: {
    defaultViewport: "cmt-repertoire-constrained",
    options: {
      "cmt-repertoire-constrained": {
        name: "Constrained workspace",
        styles: { width: "412px", height: "915px" },
      },
    },
  },
};

export const mediumViewport = {
  viewport: {
    defaultViewport: "cmt-repertoire-medium",
    options: {
      "cmt-repertoire-medium": {
        name: "Medium workspace",
        styles: { width: "800px", height: "1000px" },
      },
    },
  },
};

export const R2_ASSIGNED_CONTEXT = {
  overall_exists: true,
  white_count: 5,
  black_count: 1,
};

function frame(children: ReactNode) {
  return <main>{children}</main>;
}

export function workspace(
  props: ComponentProps<typeof RepertoireBuilderWorkspace> = {},
  preferredOptions: StoryPreferredMoveOptions = {},
  contextOptions: StoryPositionContextOptions = {},
) {
  const analysisClient = props.analysisClient ?? storyAnalysisClient();
  const preferredMoveClient =
    props.preferredMoveClient ?? storyPreferredMoveClient(preferredOptions);
  const positionContextClient =
    props.positionContextClient ?? storyPositionContextClient(contextOptions);
  const moveResponseDistributionClient =
    props.moveResponseDistributionClient ?? storyMoveResponseDistributionClient();
  return frame(
    <RepertoireBuilderWorkspace
      {...props}
      analysisClient={analysisClient}
      preferredMoveClient={preferredMoveClient}
      positionContextClient={positionContextClient}
      moveResponseDistributionClient={moveResponseDistributionClient}
    />,
  );
}

export function assignedWorkspace(
  props: ComponentProps<typeof RepertoireBuilderWorkspace> = {},
  preferredOptions: StoryPreferredMoveOptions = {},
  contextOptions: StoryPositionContextOptions = {},
) {
  return workspace(
    props,
    { relationship: "saved", ...preferredOptions },
    { ...R2_ASSIGNED_CONTEXT, ...contextOptions },
  );
}
