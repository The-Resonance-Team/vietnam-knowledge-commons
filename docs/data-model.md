# Data Model

Canonical definitions live in `/schemas` (JSON Schema, draft 2020-12) — this document explains the intent. Both SDKs validate against those files (ADR-0002).

## Entity overview

| Schema                       | Purpose                                                      | Key temporal fields                                   |
| ---------------------------- | ------------------------------------------------------------ | ----------------------------------------------------- |
| `source` / `source-registry` | Candidate/accepted data sources, tiered A–D, license-audited | `last_verified`                                       |
| `legal-document`             | A versioned legal instrument                                 | `issue_date`, `publication_date`, `effective_from/to` |
| `administrative-procedure`   | A TTHC as structured data                                    | `valid_from/to`                                       |
| `official-form`              | Blank-form metadata (never filled forms)                     | `valid_from/to`                                       |
| `organization`               | State bodies, merger-aware                                   | `established_date`, `dissolved_date`                  |
| `jurisdiction`               | Administrative units, merger-aware                           | `valid_from/to`                                       |
| `relationship`               | Typed, effective-dated edges between records                 | `effective_date`                                      |
| `dataset-release`            | Release manifest with per-source license manifest            | `build_timestamp`                                     |
| `provenance`                 | Embedded in every record                                     | `retrieved_at`                                        |

## Design rules

1. **Provenance is not optional.** Every entity embeds a `ProvenanceRecord` (schema-enforced `required`).
2. **Three date families, never conflated**: publication (when the world was told), retrieval (when we fetched), validity (when the law binds). `effective_to: null` means "in force as far as we know" — paired with `status` and `validity_confidence`.
3. **Relationships are data, not prose.** Amendment chains (`amends`/`amended_by`, `replaces`/`replaced_by`, `repeals`/`repealed_by`, `guides`) are first-class arrays on `legal-document` plus standalone `relationship` edges with `effective_date` and exact `citation` (điều/khoản/điểm). This powers the temporal benchmark's hardest cases.
4. **2025 administrative restructuring is modelled, not hard-coded.** `organization` and `jurisdiction` carry `predecessor_*`/`successor_*` links and validity ranges, so pre/post-merger records coexist and "as of" queries stay answerable.
5. **Canonical IDs are URNs**, e.g. `vnkc:legal-doc:luat-dat-dai-2024`, `vnkc:org:bo-tu-phap`. Document numbers (`45/2024/QH15`) are fields, not IDs — numbers get reused across years and authorities.
6. **Never-invent fields**: `procedure_code` (national TTHC code) is optional and must be omitted until verified against the national TTHC database. Unknown dates are `null`, not guesses.
7. **Controlled vocabularies everywhere it matters**: `license_status`, `tier`, `confidence`, `access_method`, `status`, `document_type`, `domain`. CI rejects anything outside the enums.
8. **No personal data** (PDPL 91/2025/QH15): signatory names as document metadata are acceptable; person-lists, ID numbers, and filled forms are prohibited by policy, not just schema.

## Worked example

`examples/legal-document/luat-dat-dai-2024.json` — Luật Đất đai 45/2024/QH15: `replaces: ["45/2013/QH13"]`, `effective_from: 2024-08-01` (moved earlier by Luật 43/2024/QH15), `validity_confidence: partial` until citation-level verification. Note how uncertainty is recorded **in the record** rather than hidden.
