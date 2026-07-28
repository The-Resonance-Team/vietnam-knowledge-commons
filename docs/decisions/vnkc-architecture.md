# Vietnam Knowledge Commons — Domain Model + Architecture

## Scope

**Two domains:**

1. **Administrative units** — province/ward/city post-2025 merger (effective July 1, 2025)
2. **Legal corpus** — all 9 hierarchy levels, full-text searchable, with attached files (PDF/DOCX)

**Sources:**

- vbpl.vn (legal docs, primary)
- thuvienphapluat.vn (legal docs, secondary + files)
- moha.gov.vn (admin units, merger decrees)
- gso.gov.vn (admin units, statistical codes)
- congbao.chinhphu.vn (official gazette, PDFs)
- Ministry sites (ministry-specific docs)

---

## Entity Schema

### 1. AdministrativeUnit

```json
{
  "id": "uuid",
  "code": "string (GSO statistical code)",
  "name": "string (Vietnamese)",
  "name_en": "string (English, optional)",
  "level": "enum (province|district|ward)",
  "valid_from": "date (2025-07-01)",
  "valid_to": "date|null (null = current)",
  "predecessor_ids": ["uuid"],
  "successor_ids": ["uuid"],
  "parent_id": "uuid|null",
  "metadata": {
    "population": "int",
    "area_km2": "float",
    "source_url": "string"
  },
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

**Temporal model:** `valid_from`/`valid_to` track lifecycle. Predecessor/successor arrays track mergers.

### 2. LegalDocument

```json
{
  "id": "uuid",
  "document_type": "enum (hien_phap|bo_luat|luat|nghi_quyet|phap_lenh|nghi_dinh|quyet_dinh|thong_tu|chi_thi)",
  "document_number": "string (e.g., '01/2024/QH15')",
  "title": "string (Vietnamese)",
  "title_en": "string (English, optional)",
  "issue_date": "date",
  "effective_date": "date",
  "expiry_date": "date|null",
  "issuing_body": "string (e.g., 'National Assembly', 'Government', 'Ministry of X')",
  "full_text": "text",
  "applies_to_units": ["uuid (AdministrativeUnit.id)"],
  "scope": "enum (nationwide|provincial|district|ward)",
  "source_id": "uuid (Source.id)",
  "source_url": "string",
  "retrieved_at": "timestamp",
  "file_ids": ["uuid (File.id)"],
  "metadata": {
    "keywords": ["string"],
    "abstract": "text",
    "related_doc_ids": ["uuid"]
  },
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

**Explicit relationship:** `applies_to_units[]` lists all admin units this doc applies to.

### 3. File

```json
{
  "id": "uuid",
  "legal_document_id": "uuid",
  "filename": "string",
  "file_type": "enum (pdf|docx|xlsx|other)",
  "file_size_bytes": "int",
  "storage_url": "string (R2 URL)",
  "source_url": "string (original download URL)",
  "checksum_sha256": "string",
  "retrieved_at": "timestamp",
  "created_at": "timestamp"
}
```

**Storage:** Cloudflare R2 (S3-compatible, free tier 10GB).

### 4. Source

```json
{
  "id": "uuid",
  "name": "string (e.g., 'vbpl.vn')",
  "base_url": "string",
  "source_type": "enum (legal|administrative|gazette|ministry)",
  "license": "string (e.g., 'public domain', 'CC BY')",
  "rate_limit_seconds": "float (1.5)",
  "metadata": {
    "description": "text",
    "contact": "string"
  },
  "created_at": "timestamp"
}
```

### 5. Relationship (temporal)

```json
{
  "id": "uuid",
  "from_entity_type": "enum (LegalDocument|AdministrativeUnit)",
  "from_entity_id": "uuid",
  "to_entity_type": "enum (LegalDocument|AdministrativeUnit)",
  "to_entity_id": "uuid",
  "relationship_type": "enum (amends|replaces|supersedes|implements|applies_to)",
  "valid_from": "date",
  "valid_to": "date|null",
  "metadata": {
    "source_url": "string"
  },
  "created_at": "timestamp"
}
```

---

## Storage Stack

| Component        | Technology       | Purpose                               | Cost                                     |
| ---------------- | ---------------- | ------------------------------------- | ---------------------------------------- |
| Source of truth  | JSON files (git) | Versioned, portable, human-readable   | Free                                     |
| Query cache      | Postgres (Neon)  | Fast queries, relationships, temporal | Free tier                                |
| File storage     | Cloudflare R2    | PDFs, DOCXs                           | Free tier 10GB                           |
| Full-text search | Typesense        | Instant search, Vietnamese diacritics | Free tier (self-host) or Typesense Cloud |

**Flow:**

```
Scrapers → JSON files (git) → Deploy sync → DB (query cache)
```

1. Scrapers write JSON to `data/legal-docs/*.json`, `data/admin-units/*.json`
2. Git commits JSON (versioned, portable)
3. Deploy: `pnpm sync-db` reads JSON → upserts DB
4. API queries DB (fast queries, relationships)
5. JSON = source of truth, DB = query index

---

## Scraping Architecture

**Per-source scrapers** (custom per web style):

```
scripts/ingest/
├── scrapers/
│   ├── vbpl_scraper.py          # vbpl.vn legal docs
│   ├── thuvienphapluat_scraper.py  # thuvienphapluat.vn legal docs + files
│   ├── moha_scraper.py          # moha.gov.vn admin units
│   ├── gso_scraper.py           # gso.gov.vn admin unit codes
│   ├── congbao_scraper.py       # congbao.chinhphu.vn PDFs
│   └── ministry_scraper.py      # Ministry-specific docs
├── lib/
│   ├── base_scraper.py          # Shared utilities (rate limiting, retry)
│   ├── fetchers.py              # Scrapling fetcher wrappers
│   └── storage.py               # Postgres + R2 + Meilisearch clients
└── pipeline/
    ├── scrape_metadata.py       # Phase 1
    ├── scrape_fulltext.py       # Phase 2
    ├── download_files.py        # Phase 3
    ├── index_search.py          # Phase 4
    ├── dedup.py                 # Phase 5
    └── link_relationships.py    # Phase 6
```

**Rate limiting:** 1.5s between requests (all sources).

**Scrapling fetcher tier per source:**

- **vbpl.vn**: `Fetcher` (static HTML, no JS needed)
- **thuvienphapluat.vn**: `Fetcher` or `StealthyFetcher` (test if blocked)
- **moha.gov.vn**: `Fetcher` (test first)
- **gso.gov.vn**: `Fetcher` (test first)
- **congbao.chinhphu.vn**: `Fetcher` (test first, may need `DynamicFetcher` for PDF viewer)

---

## Ingestion Pipeline (6 Phases)

### Phase 1: Scrape Metadata

- Extract title, number, date, type, URL
- Save to Postgres `legal_document` (partial) + `source`
- Output: `output/metadata.json`

### Phase 2: Scrape Full Text

- Extract body content
- Update Postgres `legal_document.full_text`
- Output: `output/fulltext.json`

### Phase 3: Download Files

- Download PDFs/DOCXs from source URLs
- Upload to R2
- Insert `file` records in Postgres
- Output: R2 bucket + Postgres `file` table

### Phase 4: Index for Search

- Push metadata + full text to Meilisearch
- Configure Vietnamese tokenizer, searchable attributes
- Output: Meilisearch index

### Phase 5: Dedup

- Match on `document_number` + `issue_date` + `document_type`
- Merge duplicates, keep canonical version
- Output: Postgres `dedup_log` table

### Phase 6: Link Relationships

- Match `LegalDocument.applies_to_units[]` to `AdministrativeUnit.id`
- Insert `relationship` records
- Output: Postgres `relationship` table

---

## Dedup Strategy

**Metadata match:**

```python
def dedup_key(doc):
    return (
        doc.document_number,
        doc.issue_date,
        doc.document_type
    )
```

**Post-process:**

1. Group docs by `dedup_key`
2. For each group, pick canonical source (vbpl.vn > thuvienphapluat.vn > others)
3. Merge metadata (union of keywords, abstracts)
4. Merge files (keep all unique files)
5. Mark non-canonical as `is_duplicate = true`

---

## Search Indexing

**Meilisearch config:**

```python
{
  "primaryKey": "id",
  "searchableAttributes": [
    "title",
    "document_number",
    "full_text",
    "keywords",
    "issuing_body"
  ],
  "filterableAttributes": [
    "document_type",
    "issue_date",
    "effective_date",
    "scope",
    "applies_to_units"
  ],
  "sortableAttributes": [
    "issue_date",
    "effective_date"
  ]
}
```

**Vietnamese support:** Meilisearch handles Unicode + diacritics natively.

---

## Deployment

**Meilisearch Cloud:**

- Sign up: https://cloud.meilisearch.com
- Free tier: 10K documents, 1 index
- API key → `lib/storage.py`

**Postgres:**

- Docker per CLAUDE.md: `docker compose up -d postgres`
- Connection string → `lib/storage.py`

**Typesense:**

- Docker: `docker compose up -d typesense`
- API key: `xyz` (default, change in prod)
- Endpoint: `http://localhost:8108`

**R2:**

- Cloudflare dashboard → R2 bucket
- S3-compatible API → `lib/storage.py`

---

## Implementation Plan

### Step 1: Database schema

- Create Postgres tables (admin_unit, legal_document, file, source, relationship)
- Write migrations in `scripts/db/migrations/`

### Step 2: Base scraper

- `scripts/ingest/lib/base_scraper.py`
- Rate limiting, retry logic, error handling

### Step 3: vbpl.vn scraper (priority)

- Port `fetch_documents.py` → `scrapers/vbpl_scraper.py`
- Fix Spider or use AsyncFetcher
- Phases 1-2 (metadata + full text)

### Step 4: File downloader

- `scripts/ingest/pipeline/download_files.py`
- R2 upload via boto3

### Step 5: thuvienphapluat scraper

- `scripts/ingest/scrapers/thuvienphapluat_scraper.py`
- Test fetcher tier (Fetcher vs StealthyFetcher)

### Step 6: Admin unit scrapers

- `scripts/ingest/scrapers/moha_scraper.py`
- `scripts/ingest/scrapers/gso_scraper.py`
- Parse tables, extract hierarchy

### Step 7: Search indexing

- `scripts/ingest/pipeline/index_search.py`
- Meilisearch client + indexing

### Step 8: Dedup + linking

- `scripts/ingest/pipeline/dedup.py`
- `scripts/ingest/pipeline/link_relationships.py`

---

## Next Actions

1. **Create Postgres schema** — migrations for 5 tables
2. **Fix vbpl.vn scraper** — port to per-source architecture
3. **Test thuvienphapluat.vn** — determine fetcher tier
4. **Set up R2** — create bucket, get API keys
5. **Set up Meilisearch Cloud** — create index, get API key
6. **Run pipeline** — Phase 1-2 for vbpl.vn first
