import type { Source, SourceRegistry } from "@vnkc/schemas/types.js";

export interface RegistrySummary {
  total: number;
  byTier: Record<string, number>;
  byLicense: Record<string, number>;
  byConfidence: Record<string, number>;
  withApi: Source[];
  tierA: Source[];
  needsReview: Source[];
}

function countBy<T extends string>(items: T[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const item of items) out[item] = (out[item] ?? 0) + 1;
  return out;
}

export function summarizeRegistry(registry: SourceRegistry): RegistrySummary {
  const sources = registry.sources;
  return {
    total: sources.length,
    byTier: countBy(sources.map((s) => s.tier)),
    byLicense: countBy(sources.map((s) => s.license_status)),
    byConfidence: countBy(sources.map((s) => s.confidence)),
    withApi: sources.filter((s) => s.api?.status === "yes"),
    tierA: sources.filter((s) => s.tier === "A"),
    needsReview: sources.filter(
      (s) => s.license_status === "unknown" || s.confidence === "unverified",
    ),
  };
}

export function formatRegistryReport(registry: SourceRegistry): string {
  const s = summarizeRegistry(registry);
  const lines: string[] = [
    `VNKC source registry — generated ${registry.generated}, ${s.total} sources`,
    "",
    `Tiers:       ${fmt(s.byTier)}`,
    `License:     ${fmt(s.byLicense)}`,
    `Confidence:  ${fmt(s.byConfidence)}`,
    "",
    `Tier A (authoritative primary): ${s.tierA.length}`,
    ...s.tierA.map((src) => `  - ${src.id} — ${src.name_en ?? src.name_vi} <${src.url}>`),
    "",
    `Sources with a confirmed API: ${s.withApi.length}`,
    ...s.withApi.map((src) => `  - ${src.id} <${src.api?.url}>`),
    "",
    `Needs legal/verification review: ${s.needsReview.length}`,
    ...s.needsReview.map(
      (src) => `  - ${src.id} (license: ${src.license_status}, confidence: ${src.confidence})`,
    ),
  ];
  return lines.join("\n");
}

function fmt(counts: Record<string, number>): string {
  return (
    Object.entries(counts)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `${k}=${v}`)
      .join(" ") || "(none)"
  );
}
