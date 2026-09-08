import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import * as generatedSdk from "./generated/sdk.gen";

const dirname = path.dirname(fileURLToPath(import.meta.url));

describe("SETUP-02 generated SDK surface", () => {
  it("exports exactly one operation request function: getHealth", () => {
    const functionExports = Object.keys(generatedSdk).filter(
      (key) => typeof (generatedSdk as Record<string, unknown>)[key] === "function",
    );
    expect(functionExports).toEqual(["getHealth"]);
    expect(typeof generatedSdk.getHealth).toBe("function");
  });

  it("checked-in contract contains only the approved health operation", () => {
    // Read the checked-in contract from disk so the test does not depend on
    // JSON module resolution settings.
    const contractPath = path.resolve(dirname, "generated", "openapi.json");
    const contract = JSON.parse(readFileSync(contractPath, "utf8")) as {
      paths: Record<string, Record<string, { operationId?: string }>>;
      components: { schemas: Record<string, unknown> };
    };

    expect(Object.keys(contract.paths)).toEqual(["/api/health"]);
    expect(Object.keys(contract.paths["/api/health"])).toEqual(["get"]);
    expect(contract.paths["/api/health"].get?.operationId).toBe("getHealth");
    expect(Object.keys(contract.components.schemas)).toEqual(["HealthResponse"]);
  });
});
