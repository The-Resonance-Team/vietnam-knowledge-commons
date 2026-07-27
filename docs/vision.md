# Vision

**Verified, versioned, and machine-ready knowledge about Viet Nam.**

## Why

Vietnamese knowledge on the web is abundant but structurally poor for machines: laws exist as HTML pages and PDF scans across dozens of portals; administrative procedures are prose; versions vanish when pages are overwritten; provenance is unverifiable; licensing is unstated. LLMs trained on this inherit its worst property — confident, current-sounding, unverifiable answers.

VNKC fixes the foundation, not the model: an open, provenance-first, temporally aware knowledge layer that any model, product, or citizen can query — with citations that resolve to authoritative sources, and "valid as of date X" as a first-class question.

## What we are building

1. **A verified data foundation** for Vietnamese language-model work: pretraining corpora, retrieval corpora, instruction-tuning sets, QA and temporal-legal-reasoning benchmarks — every record traceable to its source.
2. **Practical, authoritative knowledge about living and operating in Viet Nam**: laws, tax, land, labour, social insurance, civil status, administrative procedures, official forms, business registration, healthcare, education, transport, statistics, geography, environment, agriculture, history, language, culture.

## What we are not

- Not a scraper repository. Source snapshots are means; the canonical knowledge layer is the product.
- Not legal advice. Derived content (summaries, Q&A, instructions) is never legal authority.
- Not a mirror. When licensing forbids republication, we link and cite (`reference-only`) rather than copy.

## How we decide

- Authoritative sources first; Tier D is never ground truth.
- Every record carries provenance; every research claim carries a citation.
- Never fabricate a license, API, endpoint, URL, document number, or legal status.
- History is append-only; publication, retrieval, and validity dates are distinct.
- Vietnamese titles stay Vietnamese; English is metadata.
- See [DATA_POLICY.md](../DATA_POLICY.md), [DATA_LICENSES.md](../DATA_LICENSES.md), and ADRs in `docs/decisions/`.

## Success looks like

A developer can ask "which land law applied on 2015-06-01, and what did Điều X say then?" and get a cited, version-correct answer from open data — without trusting anyone's word, including ours.
