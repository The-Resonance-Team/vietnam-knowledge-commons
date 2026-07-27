import fs from "node:fs";
import { parse } from "yaml";
import { validateRecord } from "@vnkc/schemas";
import type { SourceRegistry } from "@vnkc/schemas/types.js";

export interface RegistryLoadResult {
  registry: SourceRegistry;
  errors: string[];
}

export function loadRegistry(path: string): RegistryLoadResult {
  const raw = parse(fs.readFileSync(path, "utf8")) as unknown;
  const errors = validateRegistry(raw);
  return { registry: raw as SourceRegistry, errors };
}

export function validateRegistry(raw: unknown): string[] {
  const result = validateRecord("source-registry", raw);
  if (!result.valid) return result.errors;

  // Cross-entry checks the JSON Schema can't express.
  const registry = raw as SourceRegistry;
  const errors: string[] = [];
  const seen = new Map<string, number>();
  registry.sources.forEach((source, i) => {
    const count = seen.get(source.id) ?? 0;
    seen.set(source.id, count + 1);
    if (count > 0) errors.push(`sources[${i}]: duplicate id '${source.id}'`);
    if (source.tier === "D" && source.license_status === "verified-open") {
      errors.push(
        `sources[${i}] (${source.id}): Tier D discovery sources must not be marked verified-open — they are never ground truth`,
      );
    }
    if (source.robots_txt?.reviewed === false && source.confidence === "verified") {
      errors.push(
        `sources[${i}] (${source.id}): confidence 'verified' requires robots_txt.reviewed: true`,
      );
    }
  });
  return errors;
}
