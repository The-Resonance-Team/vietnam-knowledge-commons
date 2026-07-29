# Vietnam Knowledge Commons

Open, versioned, machine-readable knowledge about Vietnam: the legal corpus and the
administrative units it applies to. This is the project's glossary — the words we use and
the ones we have deliberately retired.

## Language

### Records and provenance

**Source record**:
One row as a scraper observed it, before any interpretation. Lives under `data/raw/` or
`data/interim/`, ephemeral — may be deleted after processing. Never in `datasets/`.
_Avoid_: raw doc, scraped doc, draft

**Legal document**:
One published, schema-conforming record. Its identity is the source page it came from,
not the number printed on it.
_Avoid_: doc, legal doc record

**Fetched record**:
A legal document whose source page was actually retrieved. Has dates and a content
checksum.

**Discovered record**:
A legal document found on a listing page but whose detail page was never retrieved. Has a
citation and nothing else — no dates, no checksum, no body. It is a real document we know
exists, not a failure to be discarded.
_Avoid_: stub, incomplete doc, failed fetch

**Canonical id**:
The `vnkc:legal-doc:<id>` identifier, derived from the stable id in the source URL. The
one thing that makes two observations the same document.

### Naming a document

**Citation title**:
The formal reference — `Thông tư 28/2026/TT-BYT của Bộ Y tế`. Identifies a document and
says nothing about what it contains. This is what the `title` field currently holds.
_Avoid_: title (unqualified — it implies subject matter this corpus does not carry)

**Subject**:
What a document is actually about. Currently survives only as a de-diacriticized URL slug
in `subject_slug`; the real subject arrives with full text.
_Avoid_: description, summary

**Document number**:
The official number, e.g. `28/2026/TT-BYT`. Recovered by parsing, therefore evidence
rather than fact — it can be absent or unparseable, and is never an identity key.

**Document type**:
What kind of instrument this is — circular, decree, resolution. Named by the **prefix** of
the citation title. Controlled vocabulary in `registry/document-types.yaml`; validated by
`schemas/legal-document.schema.json`.
_Avoid_: category, doc class

**Issuing authority**:
The body that issued the document. Named by the **suffix** of the document number
(`TT-BYT` → Ministry of Health) — a different signal from document type, and never
inferred from the type. Controlled vocabulary in `registry/authorities.yaml`.
_Avoid_: issuing body, publisher

**Issuing authority code**:
The suffix token stored verbatim (`TT-BYT`), unresolved to a display name. A code is
something we read off the document; an authority is something we would have to assert.

### Administrative units

**Administrative unit**:
A province, district, or ward, valid over a stated period. Units are temporal: they merge,
split, and are renamed, so a unit is always "as of" a date.
_Avoid_: region, locality, area

**Predecessor / successor**:
The relationship between administrative units across a merger, split, or rename. Never
"parent/child" — that is the containment hierarchy, a different relationship.

### Datasets and publication

**Dataset**:
A published, versioned collection of structured records. Lives under `datasets/`. Immutable
once released — changes produce a new release, not a mutation.
_Avoid_: data, corpus

**Release**:
A specific versioned snapshot of a dataset. Contains `manifest.json`, `statistics.json`,
`sources.json`, `licenses.json`, `checksums.sha256`. Once published, never mutated.
_Avoid_: version, snapshot

### Registry

**Registry**:
The controlled vocabularies that normalize raw data into canonical terms. Lives under
`registry/`. Contains `sources.yaml`, `authorities.yaml`, `jurisdictions.yaml`,
`document-types.yaml`, `licenses.yaml`.
_Avoid_: vocabulary, controlled list

**Source (registry entry)**:
A record in `registry/sources.yaml` describing an upstream data source — its URL, license,
access method, and reliability tier. Not the same as a "source record" (scraped data).
_Avoid_: upstream, provider

**Jurisdiction**:
The geographic or administrative scope a document applies to. Controlled vocabulary in
`registry/jurisdictions.yaml`. Distinct from issuing authority — a document can be issued
by the Ministry of Health but apply to a specific province.
_Avoid_: region, locality, scope

## Notes

- **Evidence vs. fact.** Anything parsed out of a page is evidence and may be wrong;
  anything about the fetch itself (which URL, when, what checksum) is fact. Identity and
  uniqueness keys are built only on facts. See ADR-0004.
- **Unknown is not a value.** A field we cannot supply is omitted, never filled with
  `"unknown"`, `""`, or a placeholder date, so consumers can distinguish absence from
  assertion.
