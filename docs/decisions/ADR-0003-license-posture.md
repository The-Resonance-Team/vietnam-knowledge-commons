# ADR-0003: License posture — reference-only by default, never a blanket license

- **Status:** Accepted (2026-07-27)
- **Deciders:** project maintainer, via `/grilling` session

## Context

Research (`docs/research/legal-and-licensing.md`) found: Art. 15.2 of the IP Law excludes legal normative/administrative/judicial documents from copyright; the Law on Data 60/2024 grants positive reuse rights for officially designated _open data_; portal terms of use are unevenly published; no sui generis database right was located (absence unverified). Conclusion: redistribution rights vary **per source**, and several are unknown.

## Decision

1. **Code** (schemas, SDKs, CLI, this repo's original docs): Apache-2.0.
2. **Collected source data**: never under one blanket license. Every record carries a `license_status` from the controlled vocabulary (`verified-open | permission-required | metadata-only | reference-only | unknown | prohibited`), defaulting to `reference-only` when unknown. Every dataset release ships a per-source license manifest (`DatasetRelease.license_manifest`).
3. **Original derived layers** (record structure, benchmarks, evaluation sets): CC-BY-4.0, decided per-release in its dataset card.
4. The eight legal-review items in `docs/research/legal-and-licensing.md` gate the first public data release.

## Consequences

- `pnpm vnkc report-sources` surfaces the license audit; CI rejects records whose `license_status` is outside the vocabulary.
- We can ship metadata and derived structure now; bulk source republication waits for the legal review.
