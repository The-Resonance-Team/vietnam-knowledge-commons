# Architecture

## Three layers, strictly separated

```
┌──────────────────────────────────────────────────────────────┐
│ ML DATASET LAYER                                             │
│ Versioned derived packages: pretraining, retrieval,          │
│ instruction tuning, QA, temporal legal reasoning, benchmarks │
│ → dataset cards + license manifests + checksums              │
└──────────────────────────▲───────────────────────────────────┘
                           │ derived from (never edits)
┌──────────────────────────┴───────────────────────────────────┐
│ CANONICAL KNOWLEDGE LAYER                                    │
│ Normalized, deduplicated, temporally aware records:          │
│ LegalDocument, AdministrativeProcedure, OfficialForm,        │
│ Organization, Jurisdiction, Relationship + Provenance        │
│ → "valid as of date X" queries, relationship graph           │
└──────────────────────────▲───────────────────────────────────┘
                           │ ingested from (never edits)
┌──────────────────────────┴───────────────────────────────────┐
│ SOURCE LAYER                                                 │
│ Immutable snapshots / references to authoritative material   │
│ + provenance, retrieval metadata, checksums, license status  │
│ → append-only; registry/sources.yaml is the candidate list   │
└──────────────────────────────────────────────────────────────┘
```

Rules: data flows up, edits never flow down. A current-law question is answered by **versioned retrieval with citations** from the canonical layer — fine-tuned weights are not a source of truth.

## Phase 0 module map (this repo)

```
schemas/                    JSON Schemas — canonical data model (ADR-0002)
registry/sources.yaml       36 tiered, license-audited candidate sources
examples/                   schema-valid example records

packages/
  schemas/    @vnkc/schemas   Ajv validators over /schemas        (TS)
  sdk/        @vnkc/sdk       load/validate/report registry       (TS)
  cli/        vnkc            validate-sources / validate-record / report-sources
  sdk-python/ vnkc            same API over the same schemas      (Python)
```

Packages are **deep modules** ([packages/README.md](../packages/README.md)): entry points at the package root, `lib/` and `tests/` private, layering `schemas ← sdk ← cli` enforced by dependency-cruiser.

## Key decisions

- **ADR-0001** — monorepo (polyglot pnpm workspace), org split deferred with explicit triggers.
- **ADR-0002** — hand-authored JSON Schemas are the single source of truth; both SDKs are thin adapters (Ajv / `jsonschema`+`referencing`).
- **ADR-0003** — code Apache-2.0; collected data per-source license manifests; `reference-only` default.

## Storage and publication (strategy, not yet committed)

Git for code, schemas, manifests, small samples. Dataset release candidates: GitHub Releases (manifests, small artifacts) + Hugging Face Hub (ML-facing packages); raw snapshots in object storage, content-addressed by sha256. Formats: JSONL + Parquet. The decision ADR comes after the first ingestion spike measures real volumes (ROADMAP, first-90-days).

## What Phase 0 deliberately does not have

No crawlers, no databases, no APIs, no bulk storage. The CLI validates local files and never touches the network.
