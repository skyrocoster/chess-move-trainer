import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const dirname = path.dirname(fileURLToPath(import.meta.url));
// frontend/src/api/ -> frontend/src
const srcDir = path.resolve(dirname, "..");

const SOURCE_EXTENSIONS = new Set([".ts", ".tsx"]);
const ALLOWED_RUNTIME_CLIENT_IMPORTS: Record<string, ReadonlySet<string>> = {
  "features/status/StatusPage.tsx": new Set(["getHealthOptions"]),
  "features/analysis/analysisApi.ts": new Set(["getAnalysis", "requestAnalysis"]),
  "features/repertoire-builder/RepertoireBuilderWorkspace.tsx": new Set(["getGame"]),
  "features/position-context/positionContextApi.ts": new Set(["getPositionInsight"]),
  "features/move-response-distribution/moveResponseDistributionApi.ts": new Set([
    "getPositionInsight",
  ]),
  "features/repertoire-builder/preferredMoveApi.ts": new Set([
    "deletePreferredMoves",
    "getPreferredMoves",
    "putPreferredMoves",
  ]),
};

function collectProductionSourceFiles(dir: string): string[] {
  const files: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const entryPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entryPath === path.resolve(dirname)) continue;
      files.push(...collectProductionSourceFiles(entryPath));
    } else if (
      SOURCE_EXTENSIONS.has(path.extname(entry.name)) &&
      !entry.name.includes(".test.") &&
      !entry.name.includes(".stories.")
    ) {
      files.push(entryPath);
    }
  }
  return files;
}

function runtimeClientImportNames(content: string): string[] | null {
  const match = content.match(/import\s+(?!type\b)\{([^}]*)\}\s+from\s+["'][^"']*api\/client["']/m);
  return (
    match?.[1]
      .split(",")
      .map((name) => name.trim().split(/\s+as\s+/)[0] ?? "")
      .filter(Boolean) ?? null
  );
}

describe("generated client adoption guard", () => {
  it("allows only the approved Status, Repertoire, and position-context runtime imports", () => {
    const offenders: string[] = [];
    for (const filePath of collectProductionSourceFiles(srcDir)) {
      const content = readFileSync(filePath, "utf8");
      const relativePath = path.relative(srcDir, filePath).replaceAll(path.sep, "/");
      const names = runtimeClientImportNames(content);
      if (names === null) continue;

      const allowed = ALLOWED_RUNTIME_CLIENT_IMPORTS[relativePath];
      if (allowed === undefined || names.some((name) => !allowed.has(name))) {
        offenders.push(relativePath);
      }
    }
    expect(offenders).toEqual([]);
  });

  it("prohibits direct generated-directory imports outside the central API module", () => {
    const offenders: string[] = [];
    for (const filePath of collectProductionSourceFiles(srcDir)) {
      const content = readFileSync(filePath, "utf8");
      if (content.includes("api/generated")) {
        offenders.push(path.relative(srcDir, filePath).replaceAll(path.sep, "/"));
      }
    }
    expect(offenders).toEqual([]);
  });
});
