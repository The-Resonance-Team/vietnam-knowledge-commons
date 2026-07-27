# VNKC — agent instructions

Viet Nam Knowledge Commons: verified, versioned, machine-ready knowledge about Viet Nam.
Mission, architecture (source / canonical / ML layers), and data rules: `docs/vision.md`,
`docs/architecture.md`, `DATA_POLICY.md`. Read `DATA_LICENSES.md` before touching anything
about redistribution.

## Hard rules for agents

- **Never fabricate** a license, API, endpoint, URL, document number, or legal status. Unknown → mark `unknown`; license defaults to `reference-only`.
- Every record carries `provenance`. Every factual research claim carries source URL, publisher, access date, source type, confidence.
- No personal data, no filled forms, no credentials. No crawling — Phase 0 is validation only.
- Vietnamese titles stay in Vietnamese; English is additional metadata, never a replacement.

## Commands

```bash
pnpm install && pnpm run check   # prettier + typecheck + boundaries + tests + registry/example validation
pnpm vnkc validate-sources       # validate registry/sources.yaml
pnpm vnkc validate-record --all examples
pnpm vnkc report-sources
cd packages/sdk-python && uv sync && uv run pytest && uv run ruff check .
```

Packages are deep modules — see [packages/README.md](./packages/README.md) before adding or importing one (entry points at package root; `lib/` and `tests/` are private; `schemas ← sdk ← cli` layering; no barrels).

## Agent skills

### Issue tracker

Issues live in GitHub Issues of `The-Resonance-Team/vietnam-knowledge-commons` via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical labels, unmodified: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` (created lazily by `/domain-modeling`) + ADRs in `docs/decisions/`. See `docs/agents/domain.md`.
