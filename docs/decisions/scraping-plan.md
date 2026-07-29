# Scraping Plan — Raw → Structured

## Flow

```
Scrapers → .scratch/{source}/*.json (raw dump)
  ↓
Filter/clean scripts
  ↓
data/{entity-type}/metadata/ + fulltext/ + files/
  ↓
pnpm build-shards → data/{entity-type}/shards/
  ↓
pnpm sync-db → Postgres + Typesense
```

## Phase 1: Raw Scraping → .scratch/

### 1.1 vbpl.vn (Legal Docs — Primary)

**Status:** Partially done (4,209 docs fetched, 166K URLs remaining)

**Scraper:** `scripts/ingest/vbpl_spider.py` (broken) or `scripts/ingest/fetch_documents.py` (working, sequential)

**Output:** `.scratch/vbpl/raw_docs.json` (array of raw HTML + metadata)

**Fields to extract:**

- Document number (Số văn bản)
- Document type (Loại văn bản)
- Title (Trích yếu)
- Issue date (Ngày ban hành)
- Effective date (Ngày hiệu lực)
- Issuing body (Cơ quan ban hành)
- Full text (Nội dung)
- PDF link (if available)
- Source URL

**Rate limit:** 1.5s between requests

**Priority:** HIGH (already 4.2K docs, continue from there)

---

### 1.2 thuvienphapluat.vn (Legal Docs — Secondary + Files)

**Scraper:** `scripts/scrapers/thuvienphapluat_scraper.py` (new)

**Output:** `.scratch/thuvienphapluat/raw_docs.json`

**Fields to extract:**

- Same as vbpl.vn
- PDF/DOCX download links
- Related documents (amends, replaces, etc.)
- Keywords/tags

**Rate limit:** 1.5s (test first, may need StealthyFetcher if blocked)

**Priority:** HIGH (has files + metadata)

---

### 1.3 moha.gov.vn (Administrative Units — Merger Decrees)

**Scraper:** `scripts/scrapers/moha_scraper.py` (new)

**Output:** `.scratch/moha/raw_units.json`

**Fields to extract:**

- Province/city (Tỉnh/Thành phố)
- District (Quận/Huyện)
- Ward (Phường/Xã)
- Merger decisions (Nghị quyết sáp nhập)
- Effective dates (2025-07-01)
- Predecessor/successor relationships

**Rate limit:** 1.5s

**Priority:** MEDIUM (need post-2025 merger data)

---

### 1.4 gso.gov.vn (Administrative Unit Codes)

**Scraper:** `scripts/scrapers/gso_scraper.py` (new)

**Output:** `.scratch/gso/raw_codes.json`

**Fields to extract:**

- GSO statistical codes (Mã thống kê)
- Unit names (Vietnamese + English)
- Population
- Area (km²)
- Hierarchy (parent → child)

**Rate limit:** 1.5s

**Priority:** MEDIUM (statistical codes for admin units)

---

### 1.5 congbao.chinhphu.vn (Official Gazette — PDFs)

**Scraper:** `scripts/scrapers/congbao_scraper.py` (new)

**Output:** `.scratch/congbao/raw_pdfs.json`

**Fields to extract:**

- PDF download URLs
- Document references (link to vbpl.vn docs)
- Publication dates
- Issue numbers

**Rate limit:** 1.5s

**Fetcher tier:** May need `DynamicFetcher` (PDF viewer JS)

**Priority:** LOW (files secondary, can fetch later)

---

## Phase 2: Filter + Clean → data/

### 2.1 Filter Script

**Script:** `scripts/filter-raw.ts`

**Input:** `.scratch/{source}/raw_*.json`

**Output:**

- `data/legal-docs/metadata/{id}.meta.json` (one file per doc)
- `data/legal-docs/fulltext/{id}.txt` (full text)
- `data/legal-docs/files/{id}.files.json` (file references)
- `data/admin-units/metadata/{code}.meta.json` (one file per unit)
- `data/sources/index.json` (source registry)

**Filtering logic:**

- Dedup: group by `(documentNumber, issueDate, documentType)`
- Canonical source: vbpl.vn > thuvienphapluat.vn > others
- Merge metadata (union of keywords, abstracts)
- Merge files (keep all unique files)
- Validate: required fields present, dates valid

**Output:** `data/legal-docs/metadata/index.json` (lightweight index)

---

### 2.2 Relationship Extraction

**Script:** `scripts/extract-relationships.ts`

**Input:** `data/legal-docs/metadata/*.meta.json`

**Output:** `data/relationships.json`

**Extract:**

- Amends/replaces/supersedes relationships (from "related docs" fields)
- Applies-to relationships (from scope + jurisdiction fields)
- Temporal validity (from effective/expiry dates)

---

## Phase 3: Build Shards → data/shards/

**Script:** `scripts/build-shards.ts` (already created)

**Input:** `data/*/metadata/` + `data/*/fulltext/`

**Output:** `data/*/shards/shard-XXX.json` (1000 entities per shard)

---

## Phase 4: Sync to DB

**Script:** `scripts/sync-db.ts` (already created)

**Input:** `data/*/shards/`

**Output:** Postgres + Typesense

---

## Implementation Order

1. **Fix vbpl.vn scraper** (already have 4.2K docs, continue)
   - Fix `vbpl_spider.py` or use `fetch_documents.py` with concurrency
   - Output → `.scratch/vbpl/raw_docs.json`

2. **Build thuvienphapluat scraper** (files + metadata)
   - Test fetcher tier (Fetcher vs StealthyFetcher)
   - Output → `.scratch/thuvienphapluat/raw_docs.json`

3. **Build moha scraper** (admin units)
   - Parse merger decisions
   - Output → `.scratch/moha/raw_units.json`

4. **Build gso scraper** (admin unit codes)
   - Parse statistical tables
   - Output → `.scratch/gso/raw_codes.json`

5. **Build filter script** (raw → structured)
   - Dedup, validate, merge
   - Output → `data/*/metadata/` + `data/*/fulltext/`

6. **Build relationship extractor**
   - Extract amends/replaces/applies-to
   - Output → `data/relationships.json`

7. **Run pipeline**
   - `pnpm build-shards`
   - `pnpm sync-db`

8. **Test API**
   - `GET /v1/legal-docs`
   - `GET /v1/admin-units/current`
   - `POST /v1/mcp/call` (search_legal_docs)

---

## File Structure

```
.scratch/                    # Raw scraped data (gitignored)
├── vbpl/
│   ├── raw_docs.json       # Array of raw docs
│   └── progress.json       # Resume state
├── thuvienphapluat/
│   ├── raw_docs.json
│   └── progress.json
├── moha/
│   └── raw_units.json
├── gso/
│   └── raw_codes.json
└── congbao/
    └── raw_pdfs.json

scripts/
├── scrapers/
│   ├── vbpl_scraper.py     # Fix existing
│   ├── thuvienphapluat_scraper.py
│   ├── moha_scraper.py
│   ├── gso_scraper.py
│   └── congbao_scraper.py
├── filter-raw.ts           # Raw → structured
└── extract-relationships.ts

data/                        # Structured data (git-tracked)
├── legal-docs/
│   ├── metadata/
│   │   ├── index.json
│   │   └── {id}.meta.json
│   ├── fulltext/
│   │   └── {id}.txt
│   ├── files/
│   │   └── {id}.files.json
│   └── shards/
│       └── shard-XXX.json
├── admin-units/
│   ├── metadata/
│   │   ├── index.json
│   │   └── {code}.meta.json
│   └── shards/
│       └── shard-XXX.json
├── relationships.json
├── sources/
│   └── index.json
└── manifest.json
```

---

## Rate Limiting Strategy

**Per source:** 1.5s between requests (all gov sites)

**Concurrency:** Sequential per source (no parallel requests to same domain)

**Resume:** Each scraper tracks progress in `progress.json` (last URL, last ID)

**Retry:** 3 retries with exponential backoff (1s, 2s, 4s)

---

## Estimated Volumes

| Source              | Entities          | Est. time (sequential)     |
| ------------------- | ----------------- | -------------------------- |
| vbpl.vn             | 17K docs          | 7 hours (166K URLs × 1.5s) |
| thuvienphapluat.vn  | 15K docs          | 6 hours                    |
| moha.gov.vn         | 1K units          | 25 min                     |
| gso.gov.vn          | 1K units          | 25 min                     |
| congbao.chinhphu.vn | 10K PDFs          | 4 hours                    |
| **Total**           | **~44K entities** | **~17 hours**              |

**Note:** Can run overnight. Resume if interrupted.

---

## Next Actions

1. Fix `vbpl_spider.py` or enhance `fetch_documents.py` with concurrency
2. Test thuvienphapluat.vn (determine fetcher tier)
3. Build moha/gso scrapers (admin units)
4. Build filter script (raw → structured)
5. Run pipeline end-to-end
