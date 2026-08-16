import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const here = dirname(fileURLToPath(import.meta.url));
const materialDir = join(here, "../../styles/material");
const previewPath = join(here, "../../../.storybook/preview.tsx");

const EXPORT_DIR = "material-theme-builder-css-export";
const ARCHIVE_HASH = "3c52785020f13710d531247cf71707aee7a308bdf8a84af98e1dfeab328c6608";
const RUNTIME_MEMBER_HASH = "e52f0cbbeb21b2d56cb22db7dddbd99ba7611b6bf55fae04003c12350382e0fb";
const SIX_MEMBERS = [
  "css/light.css",
  "css/light-mc.css",
  "css/light-hc.css",
  "css/dark.css",
  "css/dark-mc.css",
  "css/dark-hc.css",
];

const provenance = JSON.parse(
  readFileSync(join(materialDir, "material-theme-provenance.json"), "utf8"),
) as {
  schemaVersion: number;
  generator: { name: string; version: string };
  artifact: {
    archive: string;
    runtimeMember: string;
    archiveSha256: string;
    runtimeMemberSha256: string;
    members: string[];
  };
  ownership: { runtimeThemeGeneration: boolean };
};

const sha256Of = (filePath: string) =>
  createHash("sha256").update(readFileSync(filePath)).digest("hex");

describe("Material theme artifact contract", () => {
  it("records schemaVersion 1 from the library generator", () => {
    expect(provenance.schemaVersion).toBe(1);
    expect(provenance.generator.name).toBe("@material/material-color-utilities");
    expect(provenance.generator.version).toBe("0.4.0");
  });

  it("records the exact six archive members with css/dark.css as the runtime member", () => {
    expect(provenance.artifact.members).toEqual(SIX_MEMBERS);
    expect(provenance.artifact.runtimeMember).toBe("css/dark.css");
    expect(provenance.artifact.archive).toBe("material-theme-builder-css-export.zip");
  });

  it("records the two actual SHA-256 hashes", () => {
    expect(provenance.artifact.archiveSha256).toBe(ARCHIVE_HASH);
    expect(provenance.artifact.runtimeMemberSha256).toBe(RUNTIME_MEMBER_HASH);
  });

  it("matches the recorded hashes against the unmodified artifacts", () => {
    expect(sha256Of(join(materialDir, provenance.artifact.archive))).toBe(ARCHIVE_HASH);
    expect(sha256Of(join(materialDir, EXPORT_DIR, provenance.artifact.runtimeMember))).toBe(
      RUNTIME_MEMBER_HASH,
    );
  });

  it("exposes --md-sys-color-* roles from the extracted dark.css", () => {
    const darkCss = readFileSync(join(materialDir, EXPORT_DIR, "css/dark.css"), "utf8");

    expect(darkCss).toContain(":root");
    expect(darkCss).toContain("--md-sys-color-primary:");
    expect(darkCss).toContain("--md-sys-color-on-primary:");
    expect(darkCss).toContain("--md-sys-color-surface-tint:");
  });

  it("keeps the repository-owned .dark preview wrapper as the dark-only runtime import", () => {
    const preview = readFileSync(previewPath, "utf8");

    expect(preview).toContain("css/dark.css");
    expect(preview).toContain('className="dark"');
    for (const variant of [
      "css/light.css",
      "css/light-mc.css",
      "css/light-hc.css",
      "css/dark-mc.css",
      "css/dark-hc.css",
    ]) {
      expect(preview).not.toContain(variant);
    }
  });

  it("declares no runtime theme generation", () => {
    expect(provenance.ownership.runtimeThemeGeneration).toBe(false);
  });
});
