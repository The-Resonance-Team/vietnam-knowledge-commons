# vnkc (Python SDK)

Two independent surfaces:

- `vnkc.registry` — read and validate VNKC registries/records against the JSON Schemas in
  `/schemas`. No network.
- `vnkc.api` — HTTP client for a running `apps/api` instance. See
  [`data/README.md`](../../data/README.md) for the full endpoint reference and examples.

```bash
uv sync
uv run pytest
uv run ruff check .
```

```python
from vnkc import load_registry, validate_record

registry, errors = load_registry("registry/sources.yaml")
assert not errors, errors
```

```python
from vnkc import VnkcClient

with VnkcClient() as client:                 # defaults to http://localhost:3100/v1
    docs = client.list_legal_docs(limit=20)
```

`vnkc.registry` mirrors `@vnkc/sdk` (TypeScript) through the same JSON Schemas — the
schemas are the single source of truth, both SDKs are thin adapters over them.
`vnkc.api` has no TypeScript counterpart yet.
