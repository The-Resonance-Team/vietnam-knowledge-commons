"""Extract body and subject text from a vbpl.vn document's raw fetch payload.

vbpl.vn's detail pages are a client-rendered Next.js app: a plain GET only
carries SSR `<head>` metadata, not the document itself. The document is
fetched by the page's own client-side JS as a POST to the *same* official_url,
with a `next-action` header identifying a compiled Server Action and a JSON
array `[doc_id]` body (doc_id is the trailing id segment of the URL, i.e. the
tail of canonical_id). One POST response carries everything we need, as React
Server Components wire format ("Flight" protocol): numbered rows, most as
`<id>:T<hex-byte-len>,<utf8-bytes>` (a text chunk) or `<id>:<json>` (a
structured value). This response carries (at least) two rows we use:

- row "2": the body HTML (see extract_body).
- row "1": vbpl's own structured document record -- `title` (its long-form
  gist, distinct from the short citation our own corpus calls `title`),
  `docAbs` (a true abstract field, when populated), `docNum`, `agencyName`,
  etc. (see extract_subject).

ponytail: BODY_ACTION_ID is a hash of vbpl.vn's compiled server action and
will break on their next redeploy. If fetches start returning no rows,
re-derive it by opening a document page in a browser, inspecting the network
tab for the POST to the same URL, and reading its `next-action` request
header.
"""

import html
import json
import re
from typing import Any

from vnknowledge.normalize.text import nfc

BODY_ACTION_ID = "0fb12b3561faa05adec51a82efb3e4f4f427f07b"

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t\f\v]+")
_BODY_ROW_RE = re.compile(rb"(?:^|\n)\d+:T([0-9a-f]+),")
_METADATA_ROW_RE = re.compile(r'(?<!\d)1:(\{"id":)')


def _strip_html(fragment: str) -> str:
    text = fragment.replace("&nbsp;", " ")
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _WS_RE.sub(" ", text)
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line).strip()


def extract_body(rsc_text: str) -> str | None:
    """Flat body text from row "2" of a vbpl.vn RSC response, or None.

    RSC text rows are framed as `<id>:T<hex-byte-length>,<utf8-bytes>` -- the
    length is a byte count in hex, not a character count, so slicing happens
    on the UTF-8-encoded bytes rather than on `rsc_text` directly.
    """
    raw = rsc_text.encode("utf-8")
    match = _BODY_ROW_RE.search(raw)
    if not match:
        return None
    length = int(match.group(1), 16)
    start = match.end()
    text = _strip_html(raw[start : start + length].decode("utf-8"))
    return nfc(text) if text else None


def _find_document_record(rsc_text: str) -> dict[str, Any] | None:
    match = _METADATA_ROW_RE.search(rsc_text)
    if not match:
        return None
    try:
        record, _ = json.JSONDecoder().raw_decode(rsc_text, match.start(1))
    except json.JSONDecodeError:
        return None
    return record if isinstance(record, dict) else None


def extract_subject(rsc_text: str) -> str | None:
    """The document's subject, from row "1"'s structured record: `docAbs` (a
    true abstract) when vbpl.vn has populated it, else `title` (which in
    practice carries the substantive gist, not just the citation). Never
    generates a subject -- returns None if row "1" is missing, unparseable, or
    carries neither field."""
    record = _find_document_record(rsc_text)
    if record is None:
        return None
    subject = record.get("docAbs") or record.get("title")
    if not isinstance(subject, str) or not subject.strip():
        return None
    return nfc(subject.strip())
