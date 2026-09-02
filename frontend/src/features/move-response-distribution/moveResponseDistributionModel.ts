import type { ChessSide } from "../viewer/chessPrimitives";
import type {
  MoveResponseDistributionReply,
  MoveResponseDistributionResponse,
} from "./moveResponseDistributionApi";

export type MoveResponseDistributionReplyView = MoveResponseDistributionReply & {
  percentage: number;
  percentageLabel: string;
  accessibleLabel: string;
};

export type MoveResponseDistributionOtherView = {
  kind: "other";
  distinct_game_count: number;
  percentage: number;
  percentageLabel: string;
  accessibleLabel: string;
};

export type MoveResponseDistributionModel = {
  color: ChessSide;
  colorLabel: "White" | "Black";
  matchingGameCount: number;
  common: MoveResponseDistributionReplyView[];
  tail: MoveResponseDistributionReplyView[];
  other: MoveResponseDistributionOtherView | null;
  state: "available" | "no-games";
  message: string;
  overlapNote: string;
};

function colorLabel(color: ChessSide): "White" | "Black" {
  return color === "white" ? "White" : "Black";
}

function percentageLabel(value: number): string {
  return `${Number.isInteger(value) ? value : value.toFixed(1)}%`;
}

function percentageOfMatchingGames(count: number, matchingGameCount: number): number {
  return matchingGameCount > 0 ? (count / matchingGameCount) * 100 : 0;
}

function replyView(
  reply: MoveResponseDistributionReply,
  matchingGameCount: number,
): MoveResponseDistributionReplyView {
  const percentage = percentageOfMatchingGames(reply.distinct_game_count, matchingGameCount);
  const formattedPercentage = percentageLabel(percentage);
  const openingName = reply.opening_name ? `, ${reply.opening_name}` : "";
  return {
    ...reply,
    percentage,
    percentageLabel: formattedPercentage,
    accessibleLabel: `${reply.san}, ${reply.distinct_game_count} distinct games, ${formattedPercentage} of matching games${openingName}`,
  };
}

export function deriveMoveResponseDistributionModel(
  response: MoveResponseDistributionResponse,
): MoveResponseDistributionModel {
  const orderedReplies = [...response.replies].sort((left, right) => left.rank - right.rank);
  const views = orderedReplies.map((reply) => replyView(reply, response.matching_game_count));
  const common = views.slice(0, 5);
  const tail = views.slice(5);
  const otherCount = tail.reduce((total, reply) => total + reply.distinct_game_count, 0);
  const otherPercentage = percentageOfMatchingGames(otherCount, response.matching_game_count);
  const formattedOtherPercentage = percentageLabel(otherPercentage);
  const label = colorLabel(response.color);

  return {
    color: response.color,
    colorLabel: label,
    matchingGameCount: response.matching_game_count,
    common,
    tail,
    other:
      tail.length === 0
        ? null
        : {
            kind: "other",
            distinct_game_count: otherCount,
            percentage: otherPercentage,
            percentageLabel: formattedOtherPercentage,
            accessibleLabel: `Other replies, ${otherCount} distinct games across ${tail.length} replies, ${formattedOtherPercentage} of matching games`,
          },
    state: response.matching_game_count === 0 || views.length === 0 ? "no-games" : "available",
    message:
      response.matching_game_count === 0
        ? `No matching ${label} repertoire games were found for this position.`
        : views.length === 0
          ? `No recorded replies were found among ${response.matching_game_count} matching ${label} repertoire games.`
          : `Replies observed in ${response.matching_game_count} matching ${label} repertoire games.`,
    overlapNote:
      "Percentages are calculated per reply from matching games; one game may appear in more than one reply.",
  };
}
