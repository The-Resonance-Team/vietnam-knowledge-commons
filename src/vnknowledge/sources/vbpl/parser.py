"""Extract body and subject text from vbpl.vn raw fetch payloads.

vbpl.vn's detail pages are a client-rendered Next.js app: the initial GET only
carries SSR `<head>` metadata (title, SEO description, dates). The document body
itself is fetched by the page's own client-side JS as a POST to the same
official_url, with a `next-action` header identifying a compiled Server Action
and a JSON array `[doc_id]` body (doc_id is the trailing id segment of the URL,
i.e. the tail of canonical_id). The response is React Server Components wire
format; the body HTML is the payload of a `<n>:T<byte-len>,<html>` text segment.

ponytail: BODY_ACTION_ID is a hash of vbpl.vn's compiled server action and will
break on their next redeploy. If fetches start returning no text segment,
re-derive it by opening a document page in a browser, inspecting the network
tab for the POST to the same URL, and reading its `next-action` request header.
"""

import html
import re

from vnknowledge.normalize.text import nfc

BODY_ACTION_ID = "0fb12b3561faa05adec51a82efb3e4f4f427f07b"

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t\f\v]+")
_RSC_TEXT_SEGMENT_RE = re.compile(rb"(?:^|\n)\d+:T([0-9a-f]+),")
_SUBJECT_META_RE = re.compile(r'<meta name="description" content="([^"]*)"')
_SUBJECT_WRAPPER_RE = re.compile(
    r"^Tra cứu [^,]+,\s*(.+?)\s*Xem toàn văn và hiệu lực\.?\s*$", re.DOTALL
)


def _strip_html(fragment: str) -> str:
    text = fragment.replace("&nbsp;", " ")
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _WS_RE.sub(" ", text)
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line).strip()


def extract_body(rsc_text: str) -> str | None:
    """Flat body text from a vbpl.vn RSC (Server Action) response, or None.

    RSC text segments are framed as `<id>:T<hex-byte-length>,<utf8-bytes>` — the
    length is a byte count in hex, not a character count, so slicing happens on
    the UTF-8-encoded bytes rather than on `rsc_text` directly.
    """
    raw = rsc_text.encode("utf-8")
    match = _RSC_TEXT_SEGMENT_RE.search(raw)
    if not match:
        return None
    length = int(match.group(1), 16)
    start = match.end()
    text = _strip_html(raw[start : start + length].decode("utf-8"))
    return nfc(text) if text else None


def extract_subject(page_html: str) -> str | None:
    """The document's subject, extracted verbatim from vbpl.vn's SEO meta
    description (itself generated from the site's own trích yếu field), with
    the surrounding 'Tra cứu <cite>, ... Xem toàn văn và hiệu lực.' template
    stripped. Returns None if the meta tag is absent or doesn't match the
    template — never generates a subject."""
    match = _SUBJECT_META_RE.search(page_html)
    if not match:
        return None
    raw = html.unescape(match.group(1))
    wrapped = _SUBJECT_WRAPPER_RE.match(raw)
    if not wrapped:
        return None
    subject = wrapped.group(1).strip()
    return nfc(subject) if subject else None
