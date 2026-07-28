# Data Structure (Scalable)

## Layout

```
data/
├── manifest.json                    # Global index (counts, paths)
├── legal-docs/
│   ├── metadata/
│   │   ├── index.json              # All doc IDs + lightweight metadata
│   │   └── {doc_id}.meta.json      # Individual metadata (optional)
│   ├── fulltext/
│   │   └── {doc_id}.txt            # Full text content (separate from metadata)
│   ├── files/
│   │   └── {doc_id}.files.json     # File references (R2 URLs, checksums)
│   └── shards/
│       ├── shard-001.json          # 1000 docs per shard (full records)
│       ├── shard-002.json
│       └── ...
├── admin-units/
│   ├── metadata/
│   │   ├── index.json              # All unit codes + lightweight metadata
│   │   └── {code}.meta.json        # Individual metadata (optional)
│   └── shards/
│       ├── shard-001.json          # 1000 units per shard
│       └── ...
└── sources/
    └── index.json                  # Source registry
```

## Why this structure?

**Scalability:**

- 17K+ docs → 17 shard files (1000 docs each) = manageable
- Metadata separate from fulltext → fast index reads
- Shards = parallel processing, smaller git diffs

**Query patterns:**

- List all docs → read `metadata/index.json` (lightweight)
- Get full doc → read `shards/shard-XXX.json` or `metadata/{id}.meta.json` + `fulltext/{id}.txt`
- Search → load index, filter, then fetch full records

**Git-friendly:**

- Index files small (KB)
- Shard files ~1MB each
- Fulltext separate → metadata changes don't bloat fulltext history

## Sync flow

1. Scrapers write to `metadata/`, `fulltext/`, `files/`
2. Build shards: `scripts/build-shards.ts` → `shards/shard-XXX.json`
3. Update `manifest.json` (counts, last_sync)
4. `pnpm sync-db` → reads shards → upserts DB

## Shard format

```json
// legal-docs/shards/shard-001.json
{
  "shard_id": "shard-001",
  "docs": [
    {
      "id": "uuid",
      "documentType": "luat",
      "documentNumber": "01/2024/QH15",
      "title": "Luật XYZ",
      "issueDate": "2024-01-01",
      "effectiveDate": "2024-07-01",
      "issuingBody": "National Assembly",
      "fullText": "...",
      "scope": "nationwide",
      "sourceId": "uuid",
      "sourceUrl": "https://vbpl.vn/...",
      "retrievedAt": "2026-07-28T00:00:00Z",
      "keywords": ["xyz"],
      "abstract": "..."
    }
    // ... 999 more docs
  ]
}
```

## Index format

```json
// legal-docs/metadata/index.json
{
  "version": "1.0",
  "count": 17000,
  "docs": [
    {
      "id": "uuid",
      "documentNumber": "01/2024/QH15",
      "documentType": "luat",
      "issueDate": "2024-01-01",
      "shard": "shard-001"
    }
    // ... 17000 entries (lightweight, ~100 bytes each = 1.7MB total)
  ]
}
```
