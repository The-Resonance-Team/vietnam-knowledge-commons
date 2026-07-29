"""Text normalization applied at ingest, per DATA_POLICY.md."""

import unicodedata


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)
