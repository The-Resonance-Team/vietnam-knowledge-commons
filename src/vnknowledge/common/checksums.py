"""Content checksums in the `sha256:<hex>` form used across provenance records."""

import hashlib


def sha256_hex(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"
