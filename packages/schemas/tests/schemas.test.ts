import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SCHEMA_KINDS, loadSchema, validateRecord } from "../index.js";

// Tests import only entry points (deep-module rule) — compute the repo root locally.
const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");

describe("schemas package", () => {
  it("every kind has a loadable schema file", () => {
    for (const kind of SCHEMA_KINDS) {
      const schema = loadSchema(kind) as { $id?: string };
      expect(schema.$id).toBe(`${kind}.schema.json`);
    }
  });

  it("validates the committed examples", () => {
    const examplesDir = path.join(REPO_ROOT, "examples");
    const kinds = fs
      .readdirSync(examplesDir, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => d.name);
    expect(kinds.length).toBeGreaterThan(0);
    for (const kind of kinds) {
      for (const file of fs.readdirSync(path.join(examplesDir, kind))) {
        if (!file.endsWith(".json")) continue;
        const data = JSON.parse(fs.readFileSync(path.join(examplesDir, kind, file), "utf8"));
        const result = validateRecord(kind as (typeof SCHEMA_KINDS)[number], data);
        expect(result.errors, `${kind}/${file}`).toEqual([]);
        expect(result.valid, `${kind}/${file}`).toBe(true);
      }
    }
  });

  it("rejects a legal document missing provenance", () => {
    const result = validateRecord("legal-document", {
      canonical_id: "vnkc:legal-doc:fake",
      document_number: "00/0000/XX00",
      title: "Văn bản giả",
      document_type: "law",
      issuing_authority: "Quốc hội",
      jurisdiction: "national",
      issue_date: "2024-01-01",
      status: "in-force",
      language: "vi",
      official_url: "https://example.gov.vn/doc/1",
    });
    expect(result.valid).toBe(false);
    expect(result.errors.join(" ")).toContain("provenance");
  });

  it("rejects a source with an uncontrolled license_status", () => {
    const result = validateRecord("source", {
      id: "bad-source",
      name_vi: "Nguồn xấu",
      publisher: "X",
      authority: "X",
      url: "https://example.vn",
      tier: "A",
      domains: ["law"],
      jurisdiction: "national",
      access_method: "html",
      license_status: "public-domain-bro", // not in the controlled vocabulary
      pii_risk: "none",
      stability: "high",
      last_verified: "2026-07-27",
      confidence: "verified",
    });
    expect(result.valid).toBe(false);
    expect(result.errors.join(" ")).toContain("license_status");
  });
});
