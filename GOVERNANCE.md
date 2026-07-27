# Governance

VNKC is young; this document is intentionally short and will grow with the contributor base.

## Roles

- **Maintainers** — The Resonance Team. Merge PRs, cut releases, own the roadmap, arbitrate disputes.
- **Contributors** — anyone with a merged PR.
- **Domain reviewers** _(planned, see ROADMAP)_ — Vietnamese legal/administrative professionals who review canonical records and dataset releases before they are marked `verified`.

## Decisions

- **Lazy consensus** for routine changes: a PR with no maintainer objection after 7 days may be merged by a maintainer.
- **ADRs** (`docs/decisions/`) for architectural or data-model decisions. An ADR is accepted when a maintainer merges it.
- **Data-policy changes** (anything in `DATA_POLICY.md` or `DATA_LICENSES.md`) require maintainer approval **and** a linked issue explaining the legal/licensing rationale.

## Principles that outrank convenience

1. Accuracy over coverage. An empty field marked `unknown` beats a guessed one.
2. Provenance over volume. A record without provenance is not a record.
3. Legal caution over release speed. `reference-only` is the default; promotion to `verified-open` needs cited evidence.

## Trademark and naming

"Viet Nam Knowledge Commons" and "VNKC" name this project. Derivative datasets must not imply endorsement; attribute per the license manifest.

## Changes to this document

By PR with maintainer approval. Material governance changes are announced in an issue first.
