---
# Dataset card frontmatter (Hugging Face compatible)
license: other # see "License manifest" — collected data is per-source, never blanket-licensed
language:
  - vi
pretty_name: ""
---

# Dataset Card — vnkc/<name> v<version>

## Summary

One paragraph: what this package contains, which layer it belongs to (source / canonical / ML dataset), and the build date.

## Composition

- Row counts per record type
- Source snapshots (source IDs + retrieval ranges + checksums from the release manifest)
- Formats (JSONL / Parquet / …) and schema version

## Provenance and license manifest

| Source ID | Tier | license_status | Attribution |
| --------- | ---- | -------------- | ----------- |
| …         | …    | …              | …           |

Every row must match `DatasetRelease.license_manifest`. If any source is not `verified-open`, say exactly what redistributing this package does and does not include.

## Quality metrics

From the release manifest: dedup rate, date-consistency pass rate, relationship-integrity pass rate, OCR confidence distribution (if applicable), PII sweep result.

## Intended uses / Prohibited uses

Must include: **not legal advice**; derived content is never a substitute for the authoritative instrument.

## Known limitations

Be honest: coverage gaps, unverified fields, review status.

## Citation

See CITATION.cff; cite the exact dataset version and build timestamp.
