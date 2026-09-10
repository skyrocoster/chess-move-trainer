import type { ChessSide } from "../chess/chessPrimitives";
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
  occurrence_count: number;
  percentage: number;
  percentageLabel: string;
  accessibleLabel: string;
};

export type MoveResponseDistributionModel = {
  color: ChessSide;
  colorLabel: "White" | "Black";
  matchingGameCount: number;
  outgoingOccurrenceCount: number;
  common: MoveResponseDistributionReplyView[];
  tail: MoveResponseDistributionReplyView[];
  other: MoveResponseDistributionOtherView | null;
  state: "available" | "no-games" | "no-moves";
  message: string;
};

function colorLabel(color: ChessSide): "White" | "Black" {
  return color === "white" ? "White" : "Black";
}

function percentageLabel(value: number): string {
  return `${Number.isInteger(value) ? value : value.toFixed(1)}%`;
}

function percentageOfOutgoingOccurrences(count: number, outgoingOccurrenceCount: number): number {
  return outgoingOccurrenceCount > 0 ? (count / outgoingOccurrenceCount) * 100 : 0;
}

function replyView(
  reply: MoveResponseDistributionReply,
  outgoingOccurrenceCount: number,
): MoveResponseDistributionReplyView {
  const percentage = percentageOfOutgoingOccurrences(
    reply.occurrence_count,
    outgoingOccurrenceCount,
  );
  const formattedPercentage = percentageLabel(percentage);
  return {
    ...reply,
    percentage,
    percentageLabel: formattedPercentage,
    accessibleLabel: `${reply.san}, ${reply.occurrence_count} occurrences, ${formattedPercentage} of outgoing move occurrences`,
  };
}

export function deriveMoveResponseDistributionModel(
  response: MoveResponseDistributionResponse,
): MoveResponseDistributionModel {
  const orderedReplies = [...response.replies].sort(
    (left, right) =>
      right.occurrence_count - left.occurrence_count ||
      (left.child_uci < right.child_uci ? -1 : left.child_uci > right.child_uci ? 1 : 0),
  );
  const views = orderedReplies.map((reply, index) =>
    replyView({ ...reply, rank: index + 1 }, response.outgoing_occurrence_count),
  );
  const common = views.slice(0, 5);
  const tail = views.slice(5);
  const otherCount = tail.reduce((total, reply) => total + reply.occurrence_count, 0);
  const otherPercentage = percentageOfOutgoingOccurrences(
    otherCount,
    response.outgoing_occurrence_count,
  );
  const formattedOtherPercentage = percentageLabel(otherPercentage);
  const label = colorLabel(response.color);
  const state =
    response.matching_game_count === 0
      ? "no-games"
      : response.outgoing_occurrence_count === 0
        ? "no-moves"
        : "available";

  return {
    color: response.color,
    colorLabel: label,
    matchingGameCount: response.matching_game_count,
    outgoingOccurrenceCount: response.outgoing_occurrence_count,
    common,
    tail,
    other:
      tail.length === 0
        ? null
        : {
            kind: "other",
            occurrence_count: otherCount,
            percentage: otherPercentage,
            percentageLabel: formattedOtherPercentage,
            accessibleLabel: `Other replies, ${otherCount} occurrences across ${tail.length} replies, ${formattedOtherPercentage} of outgoing move occurrences`,
          },
    state,
    message:
      response.matching_game_count === 0
        ? `No matching ${label} repertoire games were found for this position.`
        : response.outgoing_occurrence_count === 0
          ? `No recorded next moves were found among ${response.matching_game_count} matching ${label} repertoire games.`
          : `${response.outgoing_occurrence_count} outgoing move occurrences observed in ${response.matching_game_count} matching ${label} repertoire games.`,
  };
}
