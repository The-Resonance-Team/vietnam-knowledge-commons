# ADR-0002: Hand-authored JSON Schemas as the single source of truth

- **Status:** Accepted (2026-07-27)
- **Deciders:** project maintainer, via `/grilling` session (revises the earlier zod-emission plan, flagged in-session)

## Context

The spec requires JSON Schemas for the data model. The grilling session initially recommended authoring in Zod and emitting `.json`. But the monorepo is polyglot (ADR-0001): a zod-first pipeline makes TypeScript the privileged language and forces the Python SDK to consume a generated artifact it can't author.

## Decision

JSON Schema (draft 2020-12) files in `/schemas` are **hand-authored and canonical**. Both SDKs are thin adapters over them: Ajv (TypeScript, `@vnkc/schemas`) and `jsonschema`+`referencing` (Python, `vnkc`). No generation step, no dual source.

## Consequences

- Cross-file `$ref` uses relative `$id`s (`provenance.schema.json`); both validators resolve them.
- Hand-written TS interfaces exist only where code consumes fields (`packages/schemas/types.ts`); CI validates data against the JSON Schemas, not the types.
- Both SDKs resolve `/schemas` relative to the repo root — monorepo-local. If the packages are ever published standalone, the JSON files must be bundled into them (publish-time work, deferred).
