import { describe, expect, it } from "vitest";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadRegistry, summarizeRegistry, validateRegistry } from "../index.js";

const REGISTRY = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../../../registry/sources.yaml",
);

describe("sdk", () => {
  it("loads and validates the committed registry", () => {
    const { registry, errors } = loadRegistry(REGISTRY);
    expect(errors, errors.join("\n")).toEqual([]);
    expect(registry.sources.length).toBeGreaterThanOrEqual(30);
  });

  it("summarizes tiers, licenses and confidence", () => {
    const { registry } = loadRegistry(REGISTRY);
    const summary = summarizeRegistry(registry);
    expect(summary.total).toBe(registry.sources.length);
    expect(summary.tierA.length).toBeGreaterThanOrEqual(3);
    expect(summary.byLicense["prohibited"] ?? 0).toBe(0);
  });

  it("flags duplicate source ids", () => {
    const { registry } = loadRegistry(REGISTRY);
    const dup = {
      ...registry,
      sources: [registry.sources[0], registry.sources[0]],
    };
    expect(validateRegistry(dup).join(" ")).toContain("duplicate id");
  });

  it("flags Tier D sources marked verified-open", () => {
    const { registry } = loadRegistry(REGISTRY);
    const bad = {
      ...registry,
      sources: [
        { ...registry.sources[0], tier: "D", license_status: "verified-open" },
        ...registry.sources.slice(1),
      ],
    };
    expect(validateRegistry(bad).join(" ")).toContain("Tier D");
  });
});
