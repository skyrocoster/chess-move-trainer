import { positionKeyFromFen } from "../features/chess/chessPrimitives";

type OptionalText = string | null | undefined;

export type OpeningsCatalogueKeyInput = {
  search: OptionalText;
  pageSize: number;
  sort: string;
};

export type TrainingRequirementsKeyInput = {
  asOf: string;
  trainerColor: OptionalText;
  openingKey: OptionalText;
  openingMatch: OptionalText;
  trainingRequirementLt: number;
  pageSize: number;
};

export type GameDetailKeyInput = {
  gameUuid: string;
};

export type PreferredMoveKeyInput = {
  positionKey: string;
  today: string;
  tomorrow: string;
};

export type PositionInsightKeyInput = {
  positionKey: string;
  trainerColor: OptionalText;
  asOf: string;
};

export type AnalysisObservationKeyInput = {
  positionKey: string;
};

function normalizeOptionalText(value: OptionalText): string | null {
  const normalized = value?.trim() ?? "";
  return normalized === "" ? null : normalized;
}

function normalizeRequiredText(value: string): string {
  return value.trim();
}

function normalizePositionKey(value: string): string {
  return positionKeyFromFen(value.trim());
}

function normalizeOpeningMatch(value: OptionalText, openingKey: string | null): "reached" | null {
  return openingKey !== null && value === "reached" ? "reached" : null;
}

/**
 * Canonical structural keys for the six frontend server-state families.
 *
 * Every response-affecting input is present in its family's key. Page numbers
 * are deliberately absent from training requirements because that key owns
 * the complete assembled result rather than one transport page.
 */
export const queryKeys = {
  openingsCatalogue(input: OpeningsCatalogueKeyInput) {
    return [
      "openingsCatalogue",
      {
        search: normalizeOptionalText(input.search),
        pageSize: input.pageSize,
        sort: normalizeRequiredText(input.sort),
      },
    ] as const;
  },

  openingsCatalogueSnapshot() {
    return ["openingsCatalogueSnapshot"] as const;
  },

  trainingRequirements(input: TrainingRequirementsKeyInput) {
    const openingKey = normalizeOptionalText(input.openingKey);
    return [
      "trainingRequirements",
      {
        asOf: normalizeRequiredText(input.asOf),
        trainerColor: normalizeOptionalText(input.trainerColor),
        openingKey,
        openingMatch: normalizeOpeningMatch(input.openingMatch, openingKey),
        trainingRequirementLt: input.trainingRequirementLt,
        pageSize: input.pageSize,
      },
    ] as const;
  },

  gameDetail(input: GameDetailKeyInput) {
    return ["gameDetail", normalizeRequiredText(input.gameUuid)] as const;
  },

  preferredMove(input: PreferredMoveKeyInput) {
    return [
      "preferredMove",
      normalizePositionKey(input.positionKey),
      {
        today: normalizeRequiredText(input.today),
        tomorrow: normalizeRequiredText(input.tomorrow),
      },
    ] as const;
  },

  positionInsight(input: PositionInsightKeyInput) {
    return [
      "positionInsight",
      normalizePositionKey(input.positionKey),
      {
        trainerColor: normalizeOptionalText(input.trainerColor),
        asOf: normalizeRequiredText(input.asOf),
      },
    ] as const;
  },

  analysisObservation(input: AnalysisObservationKeyInput) {
    return ["analysisObservation", normalizePositionKey(input.positionKey)] as const;
  },
};

/** Prefixes used when an invalidation applies to a family or position. */
export const queryKeyPrefixes = {
  trainingRequirements: () => ["trainingRequirements"] as const,
  positionInsight: (positionKey: string) =>
    ["positionInsight", normalizePositionKey(positionKey)] as const,
};
