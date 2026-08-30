import { describe, expect, it } from "vitest";
import {
  openingLineLibraryFailureFromHttp,
  openingLineLibraryResponseToData,
  parseOpeningLineLibraryError,
  parseOpeningLineLibraryResponse,
  OpeningLineLibraryContractError,
} from "./openingsApi";
import { SYNTHETIC_OPENING_RESPONSE } from "./openingLineLibraryFixtures";

describe("opening Line Library API boundary", () => {
  it("parses the strict production JSON names and normalized graph", () => {
    const parsed = parseOpeningLineLibraryResponse(SYNTHETIC_OPENING_RESPONSE);

    expect(parsed.roots).toEqual(["synthetic-opening-root"]);
    expect(parsed.nodes["synthetic-transposition-reference"]).toMatchObject({
      kind: "reference",
      selectable: false,
      target_id: "synthetic-line-sicilian",
    });
    expect(parsed.filters.map((filter) => [filter.key, filter.type])).toEqual([
      ["search", "search"],
      ["eco", "range"],
      ["appears_in_my_games", "toggle"],
    ]);
    expect(parsed.sorts[0]).toEqual({
      key: "default",
      label: "Synthetic backend order",
      default: true,
      direction: "asc",
    });
  });

  it("maps the transport boundary to the generic selector without changing production names", () => {
    const data = openingLineLibraryResponseToData(
      parseOpeningLineLibraryResponse(SYNTHETIC_OPENING_RESPONSE),
    );

    expect(data.filters).toEqual([
      { id: "search", label: "Search", kind: "search", options: [] },
      { id: "eco", label: "ECO code/range", kind: "text", options: [] },
      { id: "appears_in_my_games", label: "Appears in my games", kind: "boolean", options: [] },
    ]);
    expect(data.nodes["synthetic-transposition-reference"]).toMatchObject({
      kind: "reference",
      selectable: false,
      reference_target: "synthetic-line-sicilian",
    });
  });

  it("rejects extra fields and malformed disabled, leaf, and reference nodes", () => {
    const extraField = structuredClone(SYNTHETIC_OPENING_RESPONSE) as unknown as Record<
      string,
      unknown
    >;
    extraField.unexpected = true;
    expect(() => parseOpeningLineLibraryResponse(extraField)).toThrow(
      OpeningLineLibraryContractError,
    );

    const badNode = structuredClone(SYNTHETIC_OPENING_RESPONSE) as unknown as {
      nodes: Record<string, Record<string, unknown>>;
    };
    badNode.nodes["synthetic-line-sicilian"].disabled = true;
    badNode.nodes["synthetic-line-sicilian"].disabled_reason = null;
    expect(() => parseOpeningLineLibraryResponse(badNode)).toThrow(
      /disabled nodes require a reason/,
    );

    const badReference = structuredClone(SYNTHETIC_OPENING_RESPONSE) as unknown as {
      nodes: Record<string, Record<string, unknown>>;
    };
    badReference.nodes["synthetic-transposition-reference"].target_id = "missing";
    expect(() => parseOpeningLineLibraryResponse(badReference)).toThrow(/reference target_id/);
  });

  it("rejects invalid filter declarations, graph links, and selection limits", () => {
    const invalidFilter = structuredClone(SYNTHETIC_OPENING_RESPONSE) as unknown as {
      filters: Array<Record<string, unknown>>;
    };
    invalidFilter.filters[1].range_end = null;
    expect(() => parseOpeningLineLibraryResponse(invalidFilter)).toThrow(
      /requires distinct range bounds/,
    );

    const invalidRoot = structuredClone(SYNTHETIC_OPENING_RESPONSE) as unknown as Record<
      string,
      unknown
    >;
    invalidRoot.roots = ["missing"];
    expect(() => parseOpeningLineLibraryResponse(invalidRoot)).toThrow(/roots must address nodes/);

    const invalidLimit = structuredClone(SYNTHETIC_OPENING_RESPONSE) as unknown as Record<
      string,
      unknown
    >;
    invalidLimit.selection_limit = -1;
    expect(() => parseOpeningLineLibraryResponse(invalidLimit)).toThrow(/selection_limit/);
  });

  it("parses only the typed production error body", () => {
    expect(parseOpeningLineLibraryError({ code: "invalid_filter", message: "Bad ECO" })).toEqual({
      code: "invalid_filter",
      message: "Bad ECO",
    });
    expect(
      parseOpeningLineLibraryError({ code: "invalid_filter", message: "Bad ECO", extra: true }),
    ).toBeNull();
    expect(parseOpeningLineLibraryError({ code: "not-a-code", message: "Bad" })).toBeNull();
  });

  it("maps matching HTTP statuses and malformed bodies to typed failures", () => {
    expect(
      openingLineLibraryFailureFromHttp(422, { code: "invalid_filter", message: "Bad ECO" }),
    ).toEqual({
      status: "invalid_filter",
      message: "Bad ECO",
    });
    expect(
      openingLineLibraryFailureFromHttp(503, {
        code: "line_library_unavailable",
        message: "Opening Line Library unavailable",
      }),
    ).toEqual({ status: "line_library_unavailable", message: "Opening Line Library unavailable" });
    expect(
      openingLineLibraryFailureFromHttp(500, { code: "invalid_filter", message: "wrong status" }),
    ).toEqual({
      status: "unexpected_failure",
      message: "Unable to serve opening Line Library",
    });
    expect(openingLineLibraryFailureFromHttp(503, null)).toEqual({
      status: "unexpected_failure",
      message: "Unable to serve opening Line Library",
    });
  });
});
