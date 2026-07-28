#!/usr/bin/env python3
"""Transform raw vbpl scrape -> data/ (JSON source of truth).

Input:  scripts/ingest/output/source_records.json  (27,912 raw rows)
Output: data/legal-docs/{metadata/index.json,shards/shard-XXX.json}
        data/sources/index.json
        data/manifest.json

Why this file re-parses instead of using legal_documents.json:
the scraper wrote `document_type="law"` on every row and overwrote
`document_number` with vbpl's own enabling law (91/2015/QH13) on 9,503
rows. legal_documents.json deduped on that corrupt field and collapsed
~26k documents down to 4,209. The `title` field survived intact and
carries type + number + authority, so we recover all three from it.

See docs/decisions/ADR-0004-legal-doc-identity-and-derivation.md
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "scripts" / "ingest" / "output" / "source_records.json"
DATA = REPO / "data"
SHARD_SIZE = 1000
SOURCE_ID = "moj-vbpl"

# vbpl page titles read "<Type> <number> của <body> | CSDL quốc gia về pháp luật".
# Matches 99% of rows (27,906/27,912).
TITLE_RE = re.compile(r"^(?P<type>.+?)\s+(?P<num>\S+)\s+của\s+(?P<body>.+?)\s*\|\s*CSDL")
# Fallback for titles with no "của <body>" segment, e.g. "Luật 142/2025/QH15 | CSDL".
TITLE_NOBODY_RE = re.compile(r"^(?P<type>.+?)\s+(?P<num>\S+)\s*\|\s*CSDL")

# Values are the canonical English vocabulary from
# schemas/legal-document.schema.json (ADR-0002 makes it authoritative over the
# Vietnamese slugs in schema.prisma).
#
# Ordering is longest-prefix-first and load-bearing: "Bộ luật" must be tested
# before "Luật", "Sắc lệnh" before "Lệnh", and "Thông tư liên tịch" before
# "Thông tư" — otherwise the shorter prefix swallows the longer one.
TYPE_BY_PREFIX = [
    ("Hiến pháp", "constitution"),
    ("Bộ luật", "code"),
    ("Nghị quyết", "resolution"),
    ("Nghị định", "decree"),
    ("Pháp lệnh", "ordinance"),
    ("Quyết định", "decision"),
    ("Thông tư liên tịch", "joint-circular"),
    ("Thông tư", "circular"),
    ("Chỉ thị", "directive"),
    ("Công văn", "official-dispatch"),
    ("Văn bản hợp nhất", "consolidated-document"),
    ("Sắc lệnh", "historic-ordinance"),
    ("Hiệp định", "treaty"),
    ("Luật", "law"),
    ("Lệnh", "promulgation-order"),
]

# Only consulted when the title prefix yields nothing (19 rows). The suffix
# encodes the *issuing body*, not the type, so it is a weak signal: a
# "Nghị quyết ... /QH13" is a resolution, not a law. Kept deliberately small.
TYPE_BY_SUFFIX = [
    ("TTLT", "joint-circular"),
    ("TT", "circular"),
    ("NĐ", "decree"),
    ("QĐ", "decision"),
    ("QD", "decision"),
    ("NQ", "resolution"),
    ("CT", "directive"),
    ("PL", "ordinance"),
]

# vbpl covers both central and local instruments. The only honest signal in the
# data is the issuing-body token: People's Committees / People's Councils issue
# provincial instruments, everything else is central.
LOCAL_BODY_RE = re.compile(r"\b(UBND|HĐND|HDND)\b", re.IGNORECASE)

# A real document number starts with digits: "28/2026/TT-BYT", "462-TC/VP".
# Rejects the ~1,262 rows where the title had no parseable number and the
# regex grabbed a stray token ("số", "BTC", "TC/QÐ/TCCB").
NUMBER_OK_RE = re.compile(r"^\d+[/\-]")
# Trailing id in the vbpl URL: "...--21490" or "...--<uuid>". 1:1 with source_url.
URL_ID_RE = re.compile(r"--([0-9a-fA-F][0-9a-fA-F\-]*)$")
SHA_EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
CHECKSUM_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def clean(s: str | None) -> str | None:
    """Strip the site-chrome suffix and non-breaking spaces."""
    if not s:
        return None
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s*\|\s*CSDL quốc gia về pháp luật\s*$", "", s)
    return re.sub(r"\s+", " ", s).strip() or None


def parse_title(title: str | None) -> tuple[str | None, str | None, str | None]:
    """-> (type_phrase, number, body). Body is captured but NOT used as the
    issuing authority: measured agreement with the number suffix is 100% for
    TT-BTC but 0% for QĐ-TTg, where it reads 'Tài khoản trung ương'."""
    if not title:
        return None, None, None
    t = title.replace("\xa0", " ")
    m = TITLE_RE.match(t) or TITLE_NOBODY_RE.match(t)
    if not m:
        return None, None, None
    g = m.groupdict()
    return g["type"].strip(), g["num"].strip(), (g.get("body") or "").strip() or None


def classify(type_phrase: str | None, number: str | None) -> tuple[str, str]:
    """-> (document_type, basis). Prefix if present, else suffix, else khac."""
    if type_phrase:
        for prefix, val in TYPE_BY_PREFIX:
            if type_phrase.startswith(prefix):
                return val, "title_prefix"
    if number:
        tail = number.split("/")[-1].upper()
        for prefix, val in TYPE_BY_SUFFIX:
            if tail.startswith(prefix):
                return val, "number_suffix"
    return "other", "fallback"


def authority_code(number: str | None) -> str | None:
    """Verbatim issuing-body token from the number ('28/2026/TT-BYT' -> 'TT-BYT').

    Stored raw on purpose. There are 1,106 distinct tokens and the top 30 cover
    only 80% of rows, so a hand-written token->name map would silently mislabel
    a long tail. Mapping to display names is a later, separately-verified pass.
    """
    if not number:
        return None
    tail = number.split("/")[-1].strip()
    return tail or None


def url_id(source_url: str) -> str:
    """Stable per-document id. 1:1 with source_url across all 27,904 rows
    that carry one; the 8 that don't fall back to their slug.

    Output must satisfy the canonical_id pattern `[a-z0-9]+(-[a-z0-9]+)*`,
    so runs of any other character collapse to a single hyphen.
    """
    m = URL_ID_RE.search(source_url)
    raw = m.group(1) if m else source_url.rstrip("/").rsplit("/", 1)[-1]
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", raw.lower())).strip("-")


def subject_slug(source_url: str) -> str | None:
    """The document's actual subject. The `title` field is a *citation*
    ('Thông tư 28/2026/TT-BYT của Bộ Y tế') and says nothing about content;
    only the URL slug carries the topic, de-diacriticized."""
    tail = source_url.rstrip("/").rsplit("/", 1)[-1]
    tail = URL_ID_RE.sub("", tail)
    return tail or None


def transform(row: dict) -> dict:
    """-> one record conforming to schemas/legal-document.schema.json.

    Fields the corpus cannot supply are omitted rather than filled with
    sentinels, so a consumer can always tell "unknown" from "asserted".
    """
    src = row["source_url"]
    type_phrase, raw_number, _body = parse_title(row.get("title"))
    number_ok = bool(raw_number and NUMBER_OK_RE.match(raw_number))
    number = raw_number if number_ok else None
    doc_type, basis = classify(type_phrase, number)
    code = authority_code(number)

    checksum = (row.get("content_checksum") or "").strip()
    fetched = bool(row.get("status_code")) and SHA_EMPTY not in checksum
    if not CHECKSUM_RE.match(checksum):
        checksum = ""

    prov = {
        "source_id": SOURCE_ID,
        "source_url": src,
        "retrieved_at": row.get("retrieved_at"),
        "retrieval_method": "html",
        # vbpl.vn publishes official texts but states no redistribution
        # licence; DATA_POLICY.md defaults such sources to reference-only.
        "license_status": "reference-only",
        "confidence": "unverified",
    }
    if fetched and checksum:
        prov["content_checksum"] = checksum

    rec = {
        "canonical_id": f"vnkc:legal-doc:{url_id(src).lower()}",
        "title": clean(row.get("title")),
        "document_type": doc_type,
        "document_type_basis": basis,
        "jurisdiction": "provincial" if code and LOCAL_BODY_RE.search(code) else "national",
        "status": "unknown",
        "language": "vi",
        "official_url": src,
        "retrieved_at": row.get("retrieved_at"),
        "version": 1,
        "validity_confidence": "unverified",
        "fetch_status": "fetched" if fetched else "discovered",
        "provenance": prov,
    }
    if number:
        rec["document_number"] = number
    elif raw_number:
        rec["document_number_raw"] = raw_number
    if code:
        rec["issuing_authority_code"] = code
    if row.get("issue_date"):
        rec["issue_date"] = row["issue_date"]
    if row.get("effective_date"):
        rec["effective_from"] = row["effective_date"]
    if (slug := subject_slug(src)):
        rec["subject_slug"] = slug
    if fetched and checksum:
        rec["content_checksum"] = checksum
    return rec


def _validator():
    """Validator for legal-document.schema.json with its sibling $refs resolved.

    ADR-0002 makes the hand-authored schemas in /schemas canonical, so the build
    validates against them rather than trusting this file's own field list.
    """
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource

    schema_dir = REPO / "schemas"
    registry = Registry().with_resources(
        (p.name, Resource.from_contents(json.loads(p.read_text(encoding="utf-8"))))
        for p in schema_dir.glob("*.schema.json")
    )
    root = json.loads((schema_dir / "legal-document.schema.json").read_text(encoding="utf-8"))
    return Draft202012Validator(root, registry=registry)


def validate_all(records: list[dict]) -> dict:
    """-> {} when every record conforms, else a sample of failures.

    Non-fatal by design: the count lands in manifest.json so a regression is
    visible in the diff rather than silently shipped.
    """
    try:
        v = _validator()
    except ImportError:
        return {"skipped": "jsonschema/referencing not installed"}
    bad: list[str] = []
    for r in records:
        err = next(v.iter_errors(r), None)
        if err is not None:
            bad.append(f"{r.get('canonical_id')}: {err.message[:120]}")
    return {} if not bad else {"count": len(bad), "sample": bad[:5]}


def build(raw_path: Path, out_dir: Path) -> dict:
    rows = json.loads(raw_path.read_text(encoding="utf-8"))

    records: list[dict] = []
    seen: set[str] = set()
    dropped_listing = 0
    for row in rows:
        src = row.get("source_url") or ""
        # The two listing pages are not documents.
        if "/van-ban/chi-tiet/" not in src:
            dropped_listing += 1
            continue
        rec = transform(row)
        if rec["canonical_id"] in seen:
            continue
        seen.add(rec["canonical_id"])
        records.append(rec)

    records.sort(key=lambda r: r["canonical_id"])

    docs_dir = out_dir / "legal-docs"
    (docs_dir / "metadata").mkdir(parents=True, exist_ok=True)
    shard_dir = docs_dir / "shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    for stale in shard_dir.glob("shard-*.json"):
        stale.unlink()

    # Shards hold the full records; per-document .meta.json files are
    # deliberately not written (28 files change per rebuild instead of 27,904).
    index = []
    for i in range(0, len(records), SHARD_SIZE):
        chunk = records[i : i + SHARD_SIZE]
        name = f"shard-{i // SHARD_SIZE + 1:03d}"
        (shard_dir / f"{name}.json").write_text(
            json.dumps(chunk, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        for r in chunk:
            index.append(
                {
                    "canonical_id": r["canonical_id"],
                    "document_number": r.get("document_number"),
                    "document_type": r["document_type"],
                    "issue_date": r.get("issue_date"),
                    "fetch_status": r["fetch_status"],
                    "shard": name,
                }
            )

    n_shards = (len(records) + SHARD_SIZE - 1) // SHARD_SIZE
    (docs_dir / "metadata" / "index.json").write_text(
        json.dumps({"version": "1.0", "count": len(index), "docs": index},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    (out_dir / "sources").mkdir(parents=True, exist_ok=True)
    (out_dir / "sources" / "index.json").write_text(
        json.dumps(
            {
                "version": "1.0",
                "sources": [
                    {
                        "id": SOURCE_ID,
                        "name": "vbpl.vn",
                        "base_url": "https://vbpl.vn",
                        "source_type": "legal",
                        "document_count": len(records),
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    by_type = Counter(r["document_type"] for r in records)
    by_status = Counter(r["fetch_status"] for r in records)
    stats = {
        "input_rows": len(rows),
        "dropped_listing_pages": dropped_listing,
        "records": len(records),
        "shards": n_shards,
        "by_type": dict(by_type.most_common()),
        "by_fetch_status": dict(by_status),
        "with_document_number": sum(1 for r in records if r.get("document_number")),
        "with_issue_date": sum(1 for r in records if r.get("issue_date")),
        "with_authority_code": sum(1 for r in records if r.get("issuing_authority_code")),
        "by_jurisdiction": dict(Counter(r["jurisdiction"] for r in records)),
        "type_basis": dict(Counter(r["document_type_basis"] for r in records)),
        "schema_invalid": validate_all(records),
    }

    (out_dir / "manifest.json").write_text(
        json.dumps(
            {
                "version": "1.0",
                "description": "Vietnam Knowledge Commons data index",
                "legal_documents": {
                    "count": len(records),
                    "index_file": "legal-docs/metadata/index.json",
                    "shards": "legal-docs/shards/",
                    "shard_size": SHARD_SIZE,
                    "shard_count": n_shards,
                },
                "administrative_units": {
                    "count": 0,
                    "index_file": "admin-units/metadata/index.json",
                    "shards": "admin-units/shards/",
                    "shard_size": SHARD_SIZE,
                },
                "sources": {"index_file": "sources/index.json"},
                "stats": stats,
                "last_sync": datetime.now(UTC).isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return stats


def demo() -> None:
    """Self-check on the failure modes this parser exists to handle."""
    # Corrupt number field is ignored; title carries the truth.
    r = transform({
        "source_url": "https://vbpl.vn/van-ban/chi-tiet/thong-tu-abc--21490",
        "title": "Thông tư 28/2026/TT-BYT của Bộ Y tế | CSDL quốc gia về pháp luật",
        "document_number": "91/2015/QH13",  # site chrome, must not win
        "issue_date": "2026-07-15", "status_code": 200,
        "content_checksum": "sha256:abc", "retrieved_at": "2026-07-28T00:00:00Z",
    })
    assert r["document_number"] == "28/2026/TT-BYT", r["document_number"]
    assert r["document_type"] == "circular"
    assert r["document_type_basis"] == "title_prefix"
    assert r["issuing_authority_code"] == "TT-BYT"
    assert r["title"] == "Thông tư 28/2026/TT-BYT của Bộ Y tế"
    assert r["canonical_id"] == "vnkc:legal-doc:21490"
    assert r["fetch_status"] == "fetched"
    assert r["jurisdiction"] == "national"

    # Never-fetched stub: empty-string checksum + no status_code.
    r = transform({
        "source_url": "https://vbpl.vn/van-ban/chi-tiet/quyet-dinh-xyz--17877",
        "title": "Quyết định 31/2005/QĐ-BGTVT của Bộ Xây dựng | CSDL quốc gia về pháp luật",
        "document_number": None, "issue_date": None,
        "content_checksum": f"sha256:{SHA_EMPTY}", "retrieved_at": "2026-07-28T00:00:00Z",
    })
    assert r["fetch_status"] == "discovered"
    assert r["document_number"] == "31/2005/QĐ-BGTVT"
    # Unknown must stay distinguishable from asserted: omitted, not sentinel.
    assert "content_checksum" not in r
    assert "issue_date" not in r

    # Junk token rejected, but the row survives with a type.
    r = transform({
        "source_url": "https://vbpl.vn/van-ban/chi-tiet/sac-lenh--537",
        "title": "Sắc lệnh số của Chính phủ | CSDL quốc gia về pháp luật",
        "content_checksum": "", "retrieved_at": "2026-07-28T00:00:00Z",
    })
    assert "document_number" not in r
    assert r["document_number_raw"] == "số"
    assert r["document_type"] == "historic-ordinance", r["document_type"]

    # Longest-prefix-first: "Bộ luật" must not be swallowed by "Luật",
    # nor "Thông tư liên tịch" by "Thông tư".
    r = transform({
        "source_url": "https://vbpl.vn/van-ban/chi-tiet/bo-luat--1",
        "title": "Bộ luật 91/2015/QH13 của Quốc hội | CSDL quốc gia về pháp luật",
        "content_checksum": "", "retrieved_at": "x",
    })
    assert r["document_type"] == "code", r["document_type"]
    r = transform({
        "source_url": "https://vbpl.vn/van-ban/chi-tiet/ttlt--3",
        "title": "Thông tư liên tịch 05/2026/TTLT-BCA của Bộ Công an | CSDL quốc gia về pháp luật",
        "content_checksum": "", "retrieved_at": "x",
    })
    assert r["document_type"] == "joint-circular", r["document_type"]

    # nbsp + title with no "của <body>" segment still parses.
    r = transform({
        "source_url": "https://vbpl.vn/van-ban/chi-tiet/qd--2",
        "title": "Quyết định 34/2020/QĐ-TTg\xa0 | CSDL quốc gia về pháp luật",
        "content_checksum": "", "retrieved_at": "x",
    })
    assert r["document_number"] == "34/2020/QĐ-TTg", r["document_number"]
    assert r["issuing_authority_code"] == "QĐ-TTg"

    # People's Committee instruments are provincial, not national.
    r = transform({
        "source_url": "https://vbpl.vn/van-ban/chi-tiet/qd-ubnd--4",
        "title": "Quyết định 12/2020/QĐ-UBND của UBND tỉnh Nghệ An | CSDL quốc gia về pháp luật",
        "content_checksum": "", "retrieved_at": "x",
    })
    assert r["jurisdiction"] == "provincial", r["jurisdiction"]
    print("demo: ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="run self-check and exit")
    ap.add_argument("--raw", type=Path, default=RAW)
    ap.add_argument("--out", type=Path, default=DATA)
    args = ap.parse_args()

    if args.demo:
        demo()
    else:
        demo()
        stats = build(args.raw, args.out)
        print(json.dumps(stats, ensure_ascii=False, indent=2))
