# ADR-0005: `moj-vbpl` body/subject text is republished under a verified-open posture

- **Status:** Accepted (2026-07-29)
- **Deciders:** project maintainer, via `/grill-with-docs` session
- **Supersedes:** `moj-vbpl`'s default `license_status: reference-only` in `registry/sources.yaml`, as set by ADR-0003

## Context

Issue #3 asks the corpus to carry document body text, so it is usable for RAG, NLP, and
full-text search. ADR-0003 defaults every source's `license_status` to `reference-only`
("we link and cite; we do not republish content") until the eight items in
`docs/research/legal-and-licensing.md` clear professional legal review, and names "bulk
source republication" as one of the things that wait for that review.

That default was written pending review, not because the research found high risk. The
research doc's own opinion (§1) is that the body text of a Vietnamese law, decree,
circular, decision, or administrative document published on vbpl.vn is excluded from
copyright under Article 15.2 of the IP Law (50/2005/QH11): "storing, transforming, and
re-publishing those texts carries low copyright risk under the statute." The residual
risks it names are narrower than the blanket default suggests — portal attribution
notices, copying vbpl.vn's own presentation/editorial additions, and misclassifying
non-normative content (news, FAQs) on the same domain as if it were a legal document.

## Decision

`moj-vbpl`'s `license_status` moves from `reference-only` to `verified-open`, on the basis
of the Art. 15.2 statutory exclusion already documented in the research doc — not on a
completed professional legal review, which remains outstanding. This is a deliberate,
informed bet on the statute reading, made explicit here rather than left implicit in a
registry field.

This does not extend to non-`moj-vbpl` sources, vbpl.vn's page presentation/design, or any
editorial commentary the portal adds beyond the document text itself. Each source keeps
its own `license_status`, decided on its own facts, per ADR-0003's per-source model.

## Consequences

- `registry/sources.yaml` → `moj-vbpl.license_status: verified-open`, with a note citing
  `docs/research/legal-and-licensing.md` §1.
- The professional legal review in ADR-0003 has not been obtained; this ADR records that
  the project chose to proceed on the documented statutory reading rather than wait. A
  future review that disagrees supersedes this ADR specifically — the per-source model
  itself (ADR-0003) is unchanged, and every other source stays gated as before.
- `legal-corpus-fulltext.json` (Phase 3 of issue #3) is eligible to publish under this
  posture. The existing metadata-only `legal-corpus.json` release is unaffected in
  substance — it was already published; this just changes the recorded `license_status`
  going forward.
