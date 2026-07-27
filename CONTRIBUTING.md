# Contributing to VNKC

Thanks for helping build open knowledge infrastructure for Viet Nam. This file is the on-ramp; the rules that keep the data trustworthy live in [DATA_POLICY.md](./DATA_POLICY.md) and [DATA_LICENSES.md](./DATA_LICENSES.md).

## Development setup

Requirements: Node ≥ 22, pnpm 10, Python ≥ 3.12, [uv](https://docs.astral.sh/uv/).

```bash
pnpm install
pnpm run check            # the full gate: format, types, module boundaries, tests, registry + example validation
cd packages/sdk-python && uv sync && uv run pytest && uv run ruff check .
```

Pre-commit hooks (Husky + lint-staged) run Prettier, typecheck, and tests on commit.

## Project conventions

- **Packages are deep modules.** Read [packages/README.md](./packages/README.md) first: import only through a package's root entry points, never its `lib/` or another package's `tests/`. `pnpm run lint:boundaries` enforces this. Layering: `schemas ← sdk ← cli`.
- **JSON Schemas in `/schemas` are canonical** (ADR-0002). Change the schema, and both SDKs follow it — never fork the model per language.
- **Vietnamese titles stay in Vietnamese.** English is additional metadata (`name_en`, `title_en`), never a replacement.
- **Tests go through the public interface** of each package (see existing `tests/` folders).

## Data contributions (the important part)

Every source or record contribution **must** include:

1. `provenance` — source URL, retrieval timestamp, method, license status, confidence.
2. A registry entry in `registry/sources.yaml` for new sources, with `robots_txt.reviewed: true` (actually fetch the robots.txt) and a honest `license_status` — `reference-only` when in doubt.
3. No personal data. No filled forms. No fabricated licenses, APIs, URLs, document numbers, or legal statuses.

PRs adding sources or records are rejected if `pnpm vnkc validate-sources` or `pnpm vnkc validate-record --all examples` fails.

## Workflow

1. Open or pick an issue — labels follow `docs/agents/triage-labels.md` (`ready-for-agent` and `ready-for-human` are the grab-ables).
2. Branch, commit (hooks run), push, PR. CI runs the same `pnpm run check` + the Python gate.
3. Architectural changes need an ADR in `docs/decisions/` (copy an existing ADR's shape).
4. Legal/licensing uncertainty is not a blocker to discuss — mark it `unknown`/`reference-only` and link it in the PR; see [DATA_LICENSES.md](./DATA_LICENSES.md).

## Code of conduct

[CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) applies to all project spaces.
