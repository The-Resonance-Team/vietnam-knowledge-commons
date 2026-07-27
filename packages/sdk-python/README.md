# vnkc (Python SDK)

Read and validate VNKC registries and records against the JSON Schemas in `/schemas`.

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

Mirrors `@vnkc/sdk` (TypeScript) through the same JSON Schemas — the schemas are the single source of truth, both SDKs are thin adapters over them.
