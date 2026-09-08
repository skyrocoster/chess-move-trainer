import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const dirname = path.dirname(fileURLToPath(import.meta.url));
// frontend/src/api/ -> frontend/src
const srcDir = path.resolve(dirname, "..");

const SOURCE_EXTENSIONS = new Set([".ts", ".tsx"]);

function collectSourceFiles(dir: string): string[] {
  const files: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const entryPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      // The central module and its tests legitimately live under src/api/.
      if (entryPath === path.resolve(dirname)) continue;
      files.push(...collectSourceFiles(entryPath));
    } else if (SOURCE_EXTENSIONS.has(path.extname(entry.name))) {
      files.push(entryPath);
    }
  }
  return files;
}

describe("SETUP-02 no production adoption", () => {
  it("no production module imports the generated directory or the central client module", () => {
    const offenders: string[] = [];
    for (const filePath of collectSourceFiles(srcDir)) {
      const content = readFileSync(filePath, "utf8");
      if (content.includes("api/generated") || content.includes("api/client")) {
        offenders.push(path.relative(srcDir, filePath));
      }
    }
    expect(offenders).toEqual([]);
  });
});
