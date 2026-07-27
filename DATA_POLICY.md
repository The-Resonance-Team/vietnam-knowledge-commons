# Data Policy

The rules that keep VNKC trustworthy. [DATA_LICENSES.md](./DATA_LICENSES.md) covers redistribution; this file covers collection, quality, and dataset construction.

## Collection rules

1. **Authoritative sources first.** Tier A (authoritative primary) preferred; Tier B (official explanatory) for context; Tier C (curated open datasets) with review; **Tier D (secondary discovery) is never ground truth** for legal or administrative claims.
2. **Provenance is mandatory.** Every record carries source URL, retrieval timestamp, method, license status, and confidence. No provenance → not a record.
3. **Never fabricate.** License, API, endpoint, URL, document number, legal status — unknown is marked `unknown`; license defaults to `reference-only`.
4. **Structured over scraped.** Prefer official APIs, feeds, bulk exports, and downloads over HTML parsing. Respect robots.txt, terms of use, and rate limits. Never bypass CAPTCHAs, authentication, or access controls.
5. **No personal data.** No filled forms, no credentials, no authenticated or sensitive content. Signatory names as document metadata are acceptable; person-lists and ID numbers are not (PDPL 91/2025/QH15 — see research doc).
6. **Dates are three different things.** Publication date, retrieval date, and legal validity are stored separately. "Valid as of date X" is a first-class query.
7. **History is append-only.** New versions never overwrite old ones.

## Quality checks (measurable; CI where marked)

| Check                                                                             | Threshold                                             | Where                              |
| --------------------------------------------------------------------------------- | ----------------------------------------------------- | ---------------------------------- |
| Schema validity                                                                   | 100% of records                                       | CI (Ajv + `jsonschema`)            |
| Missing provenance                                                                | 0 records                                             | CI (schema `required`)             |
| Controlled license vocabulary                                                     | 100%                                                  | CI (schema enum)                   |
| Duplicate registry IDs                                                            | 0                                                     | CI (SDK cross-checks, TS + Python) |
| UTF-8 + Unicode NFC                                                               | all text normalized at ingest                         | pipeline (Phase 1+)                |
| Vietnamese diacritics intact; no mojibake / wrong-script characters               | 0 defects                                             | pipeline + review                  |
| Exact/near-duplicate detection (checksum + simhash)                               | flagged, human-reviewed                               | pipeline                           |
| OCR confidence                                                                    | ≥ 98% auto-accept; 90–98% manual review; < 90% reject | pipeline                           |
| Checksum integrity (sha256)                                                       | verified on every snapshot read                       | pipeline                           |
| Broken links (official_url reachable)                                             | re-checked quarterly                                  | scheduled job                      |
| Legal-date consistency (issue ≤ effective_from; effective_to null while in-force) | 100%                                                  | pipeline                           |
| Relationship integrity (both endpoints exist; inverse pairs agree)                | 100%                                                  | pipeline                           |
| Source-vs-derived separation                                                      | derived content in separate packages, labelled        | repo layout                        |
| License eligibility for release                                                   | every source in manifest                              | release gate                       |
| PII detection sweep                                                               | 0 findings before release                             | release gate                       |
| Citation-span correctness (quoted text matches source span)                       | sampled manual review                                 | expert review                      |
| Stale/superseded records (in-force claim vs newer amending doc)                   | flagged on re-ingest                                  | pipeline                           |

## Split rules (train / validation / test)

Leakage prevention for ML datasets — split by **document family**, not by row:

- Versions of the same document stay in one split.
- An amending document and every document it amends stay in one split (follow `amends`/`amended_by` transitively).
- Documents from the same source family (e.g. a law + its guiding decree + guiding circular) default to one split.
- Generated questions derived from a document inherit that document's split.

## Temporal benchmark (planned)

A future evaluation set must include: amended laws; repealed laws; conflicting dates; central vs local jurisdiction conflicts; missing-evidence questions; questions that require **refusing to answer without an "as of" date**; answers that must quote or cite the authoritative provision.
