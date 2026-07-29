# Legal Corpus

Vietnamese legal documents — laws, decrees, circulars, and resolutions.

## Dataset card

- **Source:** vbpl.vn (Tier A — Ministry of Justice)
- **Records:** ~27,910 documents
- **Schema:** `schemas/legal-document.schema.json`
- **License:** reference-only (source data); CC-BY-4.0 (derived)
- **Version:** 0.1.0

## Structure

```
releases/
  v0.1.0/
    manifest.json        # Record counts, schema version, generation info
    statistics.json      # Aggregate stats (by type, authority, date)
    sources.json         # Source provenance for this release
    licenses.json        # License information
    checksums.sha256     # File integrity verification
```

## Quality

- Identity key: source URL (not document number)
- Placeholder values: never used; missing fields omitted
- Provenance: every record carries fetch metadata

See `docs/quality-policy.md` for details.
