# ADR-0001: Monorepo with polyglot packages; org split deferred

- **Status:** Accepted (2026-07-27)
- **Deciders:** project maintainer, via `/grilling` session

## Context

VNKC will eventually span: source registry, JSON Schemas, validators, SDKs (TypeScript + Python), ingestion pipelines, dataset artifacts, benchmarks, documentation. The spec asked whether the long-term home is a monorepo or a GitHub org with separate repos.

The deciding axis is **coupling**: things that change together belong together. Schemas, validators, SDKs, CLI, and registry change in lockstep — cross-repo PR chains for every schema tweak would be ceremony. Dataset _artifacts_ (bulk Parquet/JSONL) have different size, cadence, and consumers — but they don't exist yet.

## Decision

One pnpm-workspace monorepo: `packages/{schemas, sdk, cli}` (TypeScript) + `packages/sdk-python` (uv). GitHub is the public control plane; bulk data storage is decided per-release (see ROADMAP), not by repo topology.

## Split triggers (revisit when ANY fires)

1. Dataset artifacts exceed practical Git/LFS limits for this repo.
2. A subproject gains independent maintainers who need separate access control.
3. Release cadences actually diverge (schema releases decoupled from SDK releases).

## Consequences

- One CI pipeline, one issue tracker, one set of governance docs — right-sized for Phase 0.
- Python and TypeScript coexist; the JSON Schemas in `/schemas` are the shared contract (ADR-0002).
