# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root (created lazily by `/domain-modeling` — if absent, proceed silently).
- **`docs/decisions/`** — ADRs that touch the area you're about to work in. (This repo keeps ADRs in `docs/decisions/`, not `docs/adr/`.)
- **`docs/vision.md`, `docs/architecture.md`, `docs/data-model.md`** — the three-layer design and the data rules are load-bearing for any data work.
- **`DATA_POLICY.md`, `DATA_LICENSES.md`** — mandatory before touching ingestion, datasets, or licensing.

## File structure

Single-context repo:

```
/
├── CONTEXT.md          (lazy)
├── docs/
│   ├── decisions/      ← ADRs (ADR-0001-*.md …)
│   ├── research/       ← Phase 0 research outputs
│   └── agents/         ← this directory
└── packages/
```

## Use the glossary's vocabulary

When your output names a domain concept, use the term as defined in `CONTEXT.md` and `docs/data-model.md` (e.g. _source layer_, _canonical knowledge layer_, _ML dataset layer_, _provenance_, _Tier A–D_). Don't drift to synonyms.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0002 (JSON Schema as source of truth) — but worth reopening because…_
