/**
 * Hand-maintained TypeScript views of the JSON Schemas in /schemas.
 * The JSON Schemas are the source of truth; these interfaces exist only
 * where code consumes fields directly. Keep them in sync manually —
 * CI validates data against the JSON Schemas, not these types.
 */

export type LicenseStatus =
  | "verified-open"
  | "permission-required"
  | "metadata-only"
  | "reference-only"
  | "unknown"
  | "prohibited";

export type SourceTier = "A" | "B" | "C" | "D";

export type Confidence = "verified" | "partial" | "unverified";

export interface Source {
  id: string;
  name_vi: string;
  name_en?: string;
  publisher: string;
  authority: string;
  url: string;
  tier: SourceTier;
  domains: string[];
  jurisdiction: string;
  document_types?: string[];
  access_method: "html" | "api" | "feed" | "bulk" | "download" | "mixed" | "unknown";
  api?: { status: "yes" | "no" | "unknown"; url?: string | null; notes?: string };
  update_frequency?: "daily" | "weekly" | "monthly" | "irregular" | "unknown";
  tos_url?: string | null;
  robots_txt?: {
    reviewed: boolean;
    allows_scraping?: "yes" | "no" | "partial" | "unknown";
    notes?: string;
  };
  license_status: LicenseStatus;
  attribution?: string;
  pii_risk: "none" | "low" | "medium" | "high";
  stability: "high" | "medium" | "low";
  last_verified: string;
  confidence: Confidence;
  notes?: string;
}

export interface SourceRegistry {
  version: number;
  generated: string;
  sources: Source[];
}
