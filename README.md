# Viet Nam Knowledge Commons (VNKC)

> Verified, versioned, and machine-ready knowledge about Viet Nam.

VNKC builds an open, verifiable, versioned, and machine-readable knowledge foundation about Viet Nam — laws and regulations, administrative procedures and official forms, tax, land, labour, social insurance, statistics, geography, and beyond. It is **national knowledge infrastructure**, not a scraping repository.

**Status: Phase 0** — research, data model, source registry, and validation tooling. No crawling, no bulk datasets yet.

🇻🇳 [README tiếng Việt](./README.vi.md)

## Architecture: three layers, strictly separated

| Layer                   | What                                                                                                                           | Mutable?                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------- |
| **Source**              | Immutable snapshots/references to authoritative material, with provenance, checksums, and licensing status                     | Append-only                               |
| **Canonical knowledge** | Normalized, deduplicated, temporally aware records (documents, procedures, forms, organizations, jurisdictions, relationships) | Versioned, never overwritten              |
| **ML datasets**         | Explicitly versioned derived packages (pretraining, retrieval, instruction tuning, QA, temporal legal reasoning, benchmarks)   | Released, checksummed, license-manifested |

A current-law question is answered through **versioned retrieval with citations** — never through model weights.

## Repository layout

```
schemas/            JSON Schemas (draft 2020-12) — the single source of truth (ADR-0002)
registry/           sources.yaml — 36 tiered, license-audited candidate sources
examples/           Schema-valid example records
docs/               vision, architecture, data-model, research/, decisions/ (ADRs)
dataset-cards/      Dataset card template for releases
packages/
  schemas/          @vnkc/schemas — Ajv validators over /schemas (TypeScript)
  sdk/              @vnkc/sdk — registry loading, validation, reporting (TypeScript)
  cli/              vnkc — the Phase 0 CLI
  sdk-python/       vnkc — the same API in Python (uv)
```

## Quickstart

```bash
pnpm install
pnpm run check        # prettier + typecheck + module boundaries + tests + registry/example validation

pnpm vnkc validate-sources            # validate registry/sources.yaml
pnpm vnkc validate-record --all examples
pnpm vnkc report-sources              # tier / license / confidence audit

cd packages/sdk-python && uv sync && uv run pytest && uv run ruff check .
```

## Ground rules (enforced in CI where possible)

1. **Authoritative sources first.** Tier A–D classification; Tier D is never ground truth.
2. **Every record carries provenance** — source URL, retrieval date, method, checksum, license status, confidence.
3. **Never fabricate** a license, API, endpoint, URL, document number, or legal status. Unknown → `unknown`; license defaults to `reference-only`.
4. **Preserve history.** Publication, retrieval, and legal-validity dates are distinct; "valid as of date X" is a first-class query.
5. **No personal data.** No filled forms, no credentials, no authenticated or sensitive content.
6. **Source material ≠ derived content.** Generated summaries/Q&A are derived data, never legal authority.

See [DATA_POLICY.md](./DATA_POLICY.md), [DATA_LICENSES.md](./DATA_LICENSES.md), and the research in `docs/research/`.

## Licensing

- **Code** (schemas, SDKs, CLI, docs): [Apache-2.0](./LICENSE)
- **Collected source data**: per-source license manifest — see [DATA_LICENSES.md](./DATA_LICENSES.md). There is deliberately **no blanket dataset license**.
- **Original derived datasets**: per-release, in their dataset cards.

## Disclaimer

VNKC is not legal advice. Derived content (summaries, Q&A, instructions) is never a substitute for the authoritative instrument or a qualified professional.
