# ADR-0004: Legal document identity is the source page, and type/number are derived from the title

- **Status:** Accepted (2026-07-28)
- **Deciders:** project maintainer, via `/grill-with-docs` session
- **Supersedes:** the `[document_number, issue_date, document_type]` uniqueness key in `apps/api/prisma/schema.prisma`

## Context

The vbpl.vn scrape produced 27,912 rows in `scripts/ingest/output/source_records.json`.
Three of its parsed fields turned out to be unusable:

- `document_type` was the literal string `"law"` on **all 27,912** rows — a value not
  present in any of our vocabularies.
- `document_number` was overwritten with `91/2015/QH13` — vbpl.vn's _own enabling law_,
  picked up from site chrome — on **9,503** rows. Those rows carry **9,076 distinct
  titles**, so they are 9,076 genuinely different documents with one poisoned field,
  not duplicates.
- `status` was `"unknown"` on all rows; `issuing_authority` was never populated.

The downstream `legal_documents.json` deduplicated on `document_number` and so collapsed
those 9,503 documents into one, retaining **4,209 of ~26,000** records. Roughly 84% of the
corpus was lost to a parsing bug, silently, because the dedup key trusted a corrupt field.

`title` survived intact on 100% of rows and matches
`<Type> <number> của <body> | CSDL quốc gia về pháp luật` on **27,906 / 27,912 (99%)**.

## Decision

### 1. Identity is `source_url`, not `document_number`

`@@unique([documentNumber, issueDate, documentType])` is replaced by `@@unique([sourceUrl])`.
One scraped page yields one record. `canonical_id` derives from the stable id in the vbpl
URL (`…--21490`, or a UUID on newer documents), which is present and distinct on
**27,904 / 27,912** rows.

This is deliberately at odds with Vietnamese legal practice, where the document number
_is_ the citation key. It is a statement about our **pipeline**, not about the law: a
number we parsed is evidence, and evidence can be wrong, whereas the page we fetched it
from is a fact. Merging on parsed evidence is what destroyed 84% of the corpus once
already. `document_number` remains as an indexed attribute, and collapsing reprints onto
a legal-citation key stays available as a later, reversible pass.

### 2. Type comes from the title prefix; authority comes from the number suffix

These are orthogonal signals and conflating them is what produced `"law"` everywhere:

- The **prefix** names the type — `Thông tư` → `circular`.
- The **suffix** names the issuing body — `TT-BYT` → Ministry of Health.

Measured on the corpus: where both signals resolve they agree on 21,980 rows; the
disagreements are the suffix misfiring, e.g. a `Nghị quyết …/QH13` is a resolution of the
National Assembly, not a law. So the prefix is authoritative, the suffix a fallback used
on 19 rows, and `other` the last resort on 6. Final coverage: **27,885 by prefix**.

Corroboration for treating the title body as unusable — agreement between the title's
`của <body>` and the authority encoded in the number:

| Number suffix | n     | Title body agrees |
| ------------- | ----- | ----------------- |
| `TT-BTC`      | 2,250 | 100%              |
| `TT-BYT`      | 469   | 99%               |
| `NĐ-CP`       | 2,654 | **1%**            |
| `QĐ-TTg`      | 2,758 | **0%**            |

For central-government instruments the field reads `Tài khoản trung ương` ("central
account") — a sidebar widget, not an authority.

### 3. `issuing_authority_code` is stored raw; no display-name mapping

The suffix is kept verbatim (`TT-BYT`) and `issuing_authority` is left null. There are
**1,106 distinct suffix tokens**; the 30 most common cover only 80% of records and 198 are
needed for 95%. A hand-written token→name map would be confidently right on the head and
silently wrong across a 908-token tail, which is worse than null because nothing
downstream could tell the two apart.

### 4. `fetched` vs `discovered` records are both published

10,005 rows have the empty-string SHA-256 as their content checksum and no `status_code`,
`issue_date`, or `effective_date` — they were discovered on listing pages and never
fetched. They are published with `fetch_status: "discovered"`; their titles still yield
type, number, and authority, and they double as the worklist for the re-fetch pass.

### 5. `required` in `legal-document.schema.json` is relaxed

`document_number`, `issuing_authority`, and `issue_date` move out of `required`. They are
not universally knowable from source, and requiring them is precisely the mechanism that
truncated the corpus to 4,209. Fields that cannot be supplied are **omitted** rather than
filled with sentinels, so a consumer can always distinguish "unknown" from "asserted".

## Consequences

- `data/legal-docs/` holds **27,910** records across 28 shards, all validating against the
  canonical schema. Per-document `.meta.json` files are not written: a rebuild changes 28
  files instead of 27,904.
- `issueDate`, `effectiveDate`, `issuingBody`, and `documentNumber` become nullable in
  Prisma. The enum extension and the nullability change are one migration.
- The canonical vocabulary is the **English** one in `schemas/legal-document.schema.json`
  (ADR-0002). `DocumentType` in `schema.prisma` mirrors it via `@map`, since Prisma enum
  identifiers cannot contain hyphens.
- **The corpus has no full text and no true titles.** `title` is a citation
  (`Thông tư 28/2026/TT-BYT của Bộ Y tế`); the subject survives only as a de-diacriticized
  URL slug, kept in `subject_slug`. Topic search will not work on this data until a
  re-fetch retrieves document bodies. Typesense would currently index citations.
- `jurisdiction` resolves to `national` on 27,908 records — this scrape covered the
  central (`trung-uong`) corpus. Provincial coverage is future work.
