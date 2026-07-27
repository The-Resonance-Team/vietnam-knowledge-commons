# Roadmap

Phase gate rule: no phase starts until the previous phase's validation is green and its open risks are written down.

## Phase 0 — Foundation (current)

Research, data model, source registry, validation CLI, governance. **Done when:** `pnpm run check` and the Python gate are green in CI; 30+ sources registered with provenance and license status; legal-review items enumerated. No crawling.

## First 30 days

- Legal-review items from `docs/research/legal-and-licensing.md` sent for professional review.
- `examples/` coverage for all 10 schemas (organization, jurisdiction, relationship examples pending).
- First ingestion spike: **vbpl.vn sitemap-based, read-only**, producing source-layer snapshots for ~50 core national laws (land, labour, tax, social insurance) — checksums + provenance only, no content republication.
- Temporal-relationship seeding: hand-verify `replaces`/`amends` edges for the MVP document set.

## First 90 days

- Canonical-layer pipeline v1: HTML → normalized records for the MVP domains (national legal documents; tax, land, labour, social insurance, pensions, benefits).
- Administrative procedures + official forms from the National Public Service Portal (`dichvucong.gov.vn`) — metadata and blank forms only.
- Quality pipeline: NFC normalization, dedup, date-consistency, relationship-integrity checks from DATA_POLICY.md.
- First **internal** canonical dataset build (not public — gated on legal review).

## First public dataset release

- Scope: `vnkc/legal-documents` v0.1.0 — metadata + structure + relationships for the MVP set, with per-source license manifest and dataset card.
- Publication: GitHub Releases (manifest + small artifacts) and Hugging Face Hub (ML-facing package) — storage strategy per ADR to be written after the ingestion spike measures real volumes (Git+LFS/DVC vs object storage; Parquet + JSONL formats).
- Versioning convention: semver for dataset content (`MAJOR` breaking schema/semantic changes, `MINOR` new sources/fields, `PATCH` corrections), plus immutable build timestamp and source-snapshot pins in the manifest.

## Community and expert review

- Public contribution guide is live (CONTRIBUTING.md); recruit 3–5 Vietnamese legal/administrative domain reviewers (GOVERNANCE.md).
- Triage cadence: weekly; `ready-for-agent` label feeds AFK agents.

## Later phases (expansion)

1. Retrieval + evaluation datasets (QA over MVP corpus with citation-spans; temporal benchmark per DATA_POLICY.md).
2. Statistics (nso.gov.vn), administrative geography with 2025-merger lineage, education, health.
3. Culture, language, history.
4. Instruction-tuning and safety/benchmark packages.

## Monorepo → org

Stays a monorepo until a split trigger in ADR-0001 fires (artifact size, independent maintainers, diverging cadences). Revisit at first public release.
