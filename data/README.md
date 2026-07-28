# VNKC Data

JSON-first: files under `data/` are the source of truth; Postgres is a query cache built
from them (`pnpm sync-db`). This doc covers what's actually here, and the three ways to
read it — raw JSON, the REST API, or the Python SDK.

## What's here right now

**27,910 legal documents**, scraped from vbpl.vn (the national legal database), zero
administrative units. See [ADR-0004](../docs/decisions/ADR-0004-legal-doc-identity-and-derivation.md)
for how these numbers were derived and [CONTEXT.md](../CONTEXT.md) for the vocabulary.

| document_type     |  count |     | document_type         | count |
| ----------------- | -----: | --- | --------------------- | ----: |
| circular          | 10,571 |     | consolidated-document |   246 |
| decision          |  8,781 |     | promulgation-order    |   195 |
| decree            |  2,939 |     | ordinance             |    79 |
| joint-circular    |  2,146 |     | historic-ordinance    |    76 |
| resolution        |  1,138 |     | code                  |     7 |
| directive         |    833 |     | other                 |     6 |
| official-dispatch |    546 |     | treaty                |     2 |
| law               |    345 |     |                       |       |

- **17,905 `fetched`** — detail page retrieved, has `issueDate`/`effectiveDate`
- **10,005 `discovered`** — found via a listing page only; citation and type are known, dates aren't
- **jurisdiction**: 27,908 `national`, 2 `provincial` — this scrape covers the central corpus
- **No full text.** Bodies were fetched and hashed but never retained. `title` is a
  _citation_ (`Thông tư 28/2026/TT-BYT của Bộ Y tế`), not a subject — see `subject_slug`
  for the closest thing to a topic (a de-diacriticized URL slug).

Live counts: `data/manifest.json`. Per-source registry: `data/sources/index.json`.

## Layout

```
data/
├── manifest.json                # counts, shard map, last_sync
├── legal-docs/
│   ├── metadata/index.json      # every doc, lightweight (id, number, type, shard)
│   └── shards/shard-XXX.json    # full records, 1000 per shard, 28 shards
├── admin-units/                 # same shape, currently empty
└── sources/index.json           # source registry (vbpl.vn)
```

Per-document `.meta.json` files are deliberately not written — a rebuild changes 28 shard
files instead of 27,904. Shards are produced by
`scripts/ingest/build_data.py`, not `apps/api/scripts/build-shards.ts` (that script is
stale for legal docs; it refuses to run rather than overwrite the shards).

### Record shape

One entry from `legal-docs/shards/shard-001.json`, fields as published (validates against
[`schemas/legal-document.schema.json`](../schemas/legal-document.schema.json)):

```json
{
  "canonical_id": "vnkc:legal-doc:21490",
  "title": "Thông tư 28/2026/TT-BYT của Bộ Y tế",
  "document_type": "circular",
  "document_type_basis": "title_prefix",
  "document_number": "28/2026/TT-BYT",
  "issuing_authority_code": "TT-BYT",
  "subject_slug": "thong-tu-ban-hanh-danh-muc-thuoc-hoa-duoc-...",
  "jurisdiction": "national",
  "status": "unknown",
  "language": "vi",
  "official_url": "https://vbpl.vn/van-ban/chi-tiet/...",
  "issue_date": "2026-07-15",
  "fetch_status": "fetched",
  "provenance": { "source_id": "moj-vbpl", "license_status": "reference-only", "confidence": "unverified", ... }
}
```

Fields the corpus can't supply (`document_number` on ~1,260 rows, all four date fields on
`discovered` rows) are **omitted**, never filled with a sentinel — see CONTEXT.md's
"unknown is not a value."

## Three ways to read this data

### 1. Raw JSON (no server, no dependencies)

Fastest for bulk/offline work — a full pass over the corpus, no network round trips.

```python
import json, pathlib

data_dir = pathlib.Path("data/legal-docs")
index = json.loads((data_dir / "metadata/index.json").read_text())
print(index["count"])  # 27910

for shard_path in sorted((data_dir / "shards").glob("shard-*.json")):
    for doc in json.loads(shard_path.read_text()):
        if doc["document_type"] == "circular" and doc["fetch_status"] == "fetched":
            print(doc["document_number"], doc["title"])
```

### 2. REST API (`apps/api`)

```bash
cd apps/api && pnpm dev   # http://localhost:3100/v1
```

| Method | Route                          | Notes                                                                              |
| ------ | ------------------------------ | ---------------------------------------------------------------------------------- |
| GET    | `/legal-docs?limit=&offset=`   | newest `issueDate` first                                                           |
| GET    | `/legal-docs/search?q=&limit=` | SQL `LIKE` over citation/number/full text — **not** topic search, see caveat below |
| GET    | `/legal-docs/:id`              | `:id` is the DB row uuid, not `canonical_id`                                       |
| GET    | `/admin-units?limit=&offset=`  | currently empty                                                                    |
| GET    | `/admin-units/current`         | units with `validTo` null or future                                                |
| GET    | `/admin-units/code/:code`      | GSO statistical code                                                               |
| GET    | `/admin-units/:id`             |                                                                                    |
| GET    | `/mcp/tools`                   | list of MCP tool definitions                                                       |
| POST   | `/mcp/call`                    | `{name, arguments}` → SSE stream, one `data:` event                                |

```bash
curl 'http://localhost:3100/v1/legal-docs?limit=5'
curl 'http://localhost:3100/v1/legal-docs/search?q=B%E1%BB%99+Y+t%E1%BA%BF'
```

**Search caveat:** `title` (`citationTitle` in the DB) is a citation, not a subject.
Searching "y tế" (health) only matches documents whose _citation_ literally contains that
string — mostly ones issued by the Ministry of Health — not documents _about_ health in
general. Real topic search needs full text, which this corpus doesn't have yet.

### 3. Python SDK (`vnkc.api`)

The `vnkc` package (`packages/sdk-python`) ships a thin HTTP client over the same routes.

```bash
cd packages/sdk-python && uv sync
```

```python
from vnkc import VnkcClient

with VnkcClient() as client:                       # defaults to http://localhost:3100/v1
    docs = client.list_legal_docs(limit=20)
    hits = client.search_legal_docs("Bộ Y tế", limit=10)
    doc = client.get_legal_doc(docs[0]["id"])

    tools = client.list_mcp_tools()
    result = client.call_mcp_tool("search_legal_docs", {"query": "thông tư", "limit": 5})
```

Point it at a different server, or inject a mock transport in tests:

```python
VnkcClient(base_url="https://api.staging.example/v1")
```

Errors surface as `httpx.HTTPStatusError` (bad HTTP status) or `vnkc.VnkcApiError` (the
MCP route replied with an SSE `error` event). Tests: `packages/sdk-python/tests/test_api.py`
(runs against a mock transport — no live server needed).

`vnkc.registry` is a separate, unrelated surface: schema/registry validation against
`/schemas` and `registry/sources.yaml`, no network involved. See its own docstring.

## Sync flow

```
scripts/ingest/output/source_records.json   (raw scrape, not tracked)
        │  scripts/ingest/build_data.py      — parse, derive, validate against /schemas
        ▼
data/legal-docs/{metadata,shards}/           (tracked, source of truth)
        │  apps/api: pnpm sync-db
        ▼
Postgres (query cache — safe to rebuild from data/ at any time)
```

Rebuild: `uv run --project packages/sdk-python python scripts/ingest/build_data.py`
Sync to DB: `cd apps/api && pnpm sync-db` (identity is `sourceUrl`; reruns upsert, not append)

## Known gaps

- **No full text.** Search and any content-based feature are blocked on a re-fetch pass.
- **Admin units are empty.** moha/gso scrapers returned zero usable content (separate,
  unresolved issue — not part of this pipeline).
- **`issuing_authority` (display name) is null everywhere.** Only the raw code
  (`issuing_authority_code`, e.g. `TT-BYT`) is stored — 1,106 distinct codes exist and a
  name map wasn't attempted (see ADR-0004).
- **Central corpus only.** 27,908 of 27,910 records are `national` scope; provincial law
  isn't covered.
