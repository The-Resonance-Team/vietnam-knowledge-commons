---
title: "VNKC Landscape: Existing Projects & Datasets about Viet Nam"
date: 2026-07-27
status: draft
---

# Landscape: existing projects and datasets relevant to VNKC

This document surveys 16 existing projects, datasets, and portals that overlap with the
Viet Nam Knowledge Commons mission (open, verifiable, versioned, machine-readable knowledge
about Viet Nam). Every entry was checked against its primary source (GitHub repo, Hugging Face
dataset page, official paper, or government portal) on **2026-07-27**. Where a fact could not be
verified from a primary source it is marked `unverified`. Licences are quoted exactly as
published; where no licence statement was found we write `unknown` rather than guessing.

Viet Nam's administrative map changed substantially in 2025 (province mergers down to 34
province-level units and a two-tier commune system); several administrative datasets below
have already tracked that change, and GADM has **not** — this is a live data-correctness issue
for any downstream consumer.

## Comparison table

| #   | Name                                         | Maintainer                                       | Scope                                              | License                     | Update status                                    | VNKC relation       |
| --- | -------------------------------------------- | ------------------------------------------------ | -------------------------------------------------- | --------------------------- | ------------------------------------------------ | ------------------- |
| 1   | UTS_VLC                                      | Underthesea NLP                                  | Vietnamese laws/codes full text, in-force snapshot | unknown                     | Active (2026 splits, Jan 2026 correction)        | interoperate        |
| 2   | th1nhng0/vietnamese-legal-documents          | th1nhng0 (individual)                            | 127K legal docs scraped from vbpl.vn               | unknown                     | unverified                                       | reuse               |
| 3   | duyet/vietnamese-legal-instruct              | Duyet Le                                         | 467,732 instruction pairs from legal docs          | CC-BY-4.0                   | Active (2026)                                    | avoid-duplication   |
| 4   | ViLegalMCQ                                   | ntphuc149                                        | Vietnamese legal MCQ dataset                       | Apache-2.0                  | unverified (gated)                               | reuse               |
| 5   | VLSP legal shared tasks (LegalSLM, LTER)     | VLSP community                                   | Legal reasoning/entailment benchmarks              | unknown                     | Active (VLSP 2025, 11th edition)                 | contribute-upstream |
| 6   | VnCoreNLP                                    | Dat Quoc Nguyen et al.                           | Vietnamese NLP pipeline + annotated corpora        | unknown (custom)            | Maintenance mode (2018+)                         | interoperate        |
| 7   | PhoBERT                                      | VinAI Research                                   | Pre-trained Vietnamese LMs (20GB corpus)           | MIT (v1) / AGPL-3.0 (v2)    | Stable, no new releases                          | interoperate        |
| 8   | zalo-ai-legal-text-retrieval-vn              | Zalo AI / GreenNode mirror                       | Legal text retrieval benchmark (61.4K corpus)      | unknown                     | Static (MTEB mirror)                             | reuse               |
| 9   | vietnamese-provinces-database                | Thang Le Quoc                                    | SQL + GIS administrative units, tracks decrees     | MIT                         | Very active (v4.1.0, tracks 2026 decrees)        | reuse               |
| 10  | vietnamadminunits                            | Tran Ngoc Minh Hieu                              | Old↔new address mapping after 2025 merger          | MIT                         | Active (2025)                                    | reuse               |
| 11  | GADM (Vietnam)                               | GADM / UC Berkeley                               | Global admin boundaries v4.1                       | Non-commercial use only     | Stale for VN (pre-merger; v5 announced Jan 2026) | avoid-duplication   |
| 12  | Open Development Vietnam                     | Open Development Mekong                          | Curated Mekong-region open datasets                | CC-BY-SA-4.0                | Active                                           | interoperate        |
| 13  | data.gov.vn                                  | Ministry of Information and Communications (MIC) | National open-data portal                          | unknown                     | Portal live; content depth unverified            | interoperate        |
| 14  | vbpl.vn + ws.vbpl.vn                         | Ministry of Justice                              | National legal database + integration API          | unknown (gov data)          | Active                                           | interoperate        |
| 15  | Wikidata (Viet Nam entities)                 | Wikimedia community                              | General-purpose KG incl. VN entities               | CC0-1.0                     | Continuously updated                             | interoperate        |
| 16  | Vietnamese legal-cases KG (arXiv 2309.09069) | Vuong T. Huy et al.                              | KG of 9,578 court cases                            | unknown (research artifact) | Static (2023)                                    | reuse               |

---

## 1. UTS_VLC — Vietnamese Legal Corpus (Underthesea)

- **URL:** https://huggingface.co/datasets/undertheseanlp/UTS_VLC
- **Maintainer:** Underthesea NLP (undertheseanlp@gmail.com)
- **Scope:** Full text of Vietnamese legislation at the top of the legal hierarchy — Constitution + 305 Laws/Codes in the verified in-force 2026 split; 942 rows total across splits.
- **Size:** 942 documents, 32.1 MB (splits: 2021 = 110, 2023 = 208, 2026_01 = 318 superseded, 2026 = 306).
- **Formats:** Parquet (HF), Markdown per document, plus `database/vn_law.sqlite` reference catalogue and `metadata/2026_sources.json` per-document provenance links.
- **Update status:** Active — January 2026 release corrected after issue #1035; 2026 split validated against vbpl.vn.
- **Provenance:** Full text from official vbpl.vn; cross-referenced against congbao.chinhphu.vn, vanban.chinhphu.vn, vietlaw.quochoi.vn, thuvienphapluat.vn, luatvietnam.vn. In-force filter (Còn hiệu lực ∪ Hết hiệu lực một phần).
- **License:** `unknown` (no licence statement observed on the dataset card; do not assume).
- **Strengths:** Rare example of legal data with explicit per-document provenance links and an in-force-validated snapshot; SQLite catalogue model is close to VNKC's design.
- **Weaknesses:** Only top-of-hierarchy laws/codes — no decrees, circulars, or provincial documents; licence unstated.
- **VNKC recommendation:** `interoperate` — its provenance-per-document and in-force validation are the model to align with, not re-scrape.
- **Evidence:** HF dataset page, publisher Underthesea NLP, accessed 2026-07-27, source type: hf-dataset, confidence: verified (licence: unverified).

## 2. th1nhng0/vietnamese-legal-documents

- **URL:** https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents
- **Maintainer:** th1nhng0 (individual HF user)
- **Scope:** "A comprehensive collection of Vietnamese legal documents — laws, decrees, circulars, decisions, and other normative acts."
- **Size:** ~127K documents (figure cited by the downstream duyet/vietnamese-legal-instruct README).
- **Formats:** HF dataset (Parquet).
- **Update status:** unverified.
- **Provenance:** Scraped from vbpl.vn (Government legal document portal, Ministry of Justice), per downstream documentation.
- **License:** `unknown`.
- **Strengths:** Broadest coverage of document types (decrees + circulars, not just laws); already the upstream of at least one instruction dataset.
- **Weaknesses:** Individual maintainer, no visible validation/provenance chain, licence unstated.
- **VNKC recommendation:** `reuse` — useful bulk raw material, but re-validate against vbpl.vn before treating as canonical.
- **Evidence:** HF dataset page + duyet README, accessed 2026-07-27, source type: hf-dataset, confidence: partial.

## 3. duyet/vietnamese-legal-instruct (vietnamese-legal-documents-dataset)

- **URL:** https://github.com/duyet/vietnamese-legal-documents-dataset and https://huggingface.co/datasets/duyet/vietnamese-legal-instruct
- **Maintainer:** Duyet Le
- **Scope:** Instruction-following dataset over Vietnamese legal documents, 14 QA types (full_text recall, scope, classify, summarize, legal_basis chain, amounts, etc.).
- **Size:** 467,732 training pairs from 127K legal documents (HF size category 100K<n<1M).
- **Formats:** HF dataset + generation source code on GitHub.
- **Update status:** Active (2026, DOI 10.57967/hf/8343).
- **Provenance:** Derived from th1nhng0/vietnamese-legal-documents ← vbpl.vn.
- **License:** CC-BY-4.0 (HF metadata).
- **Strengths:** Explicit provenance chain back to vbpl.vn; legal-hierarchy-aware QA typing; clear licence.
- **Weaknesses:** Synthetic QA (LLM-generated answers need spot-checking); inherits any upstream scrape errors.
- **VNKC recommendation:** `avoid-duplication` — don't rebuild legal instruction data; link to it and focus VNKC effort on the canonical structured layer underneath.
- **Evidence:** GitHub repo + HF metadata, publisher Duyet Le, accessed 2026-07-27, source type: github-repo, confidence: verified.

## 4. ViLegalMCQ

- **URL:** https://huggingface.co/datasets/ntphuc149/ViLegalMCQ
- **Maintainer:** ntphuc149 (HF user)
- **Scope:** Vietnamese legal multiple-choice QA; legal documents reflect Vietnamese law as of a stated temporal snapshot.
- **Size:** ~13 MB total.
- **Formats:** HF dataset; **gated** — requires accepting conditions / sharing contact info.
- **Update status:** unverified.
- **Provenance:** Vietnamese legal documents (detail behind gate).
- **License:** Apache-2.0.
- **Strengths:** Clear permissive licence; temporal scope explicitly acknowledged (rare).
- **Weaknesses:** Gated access limits automated reuse; small.
- **VNKC recommendation:** `reuse` — as an evaluation set for legal-QA over VNKC content.
- **Evidence:** HF dataset page, accessed 2026-07-27, source type: hf-dataset, confidence: verified (size/content details: partial, gated).

## 5. VLSP legal shared tasks (LegalSLM, LTER)

- **URL:** https://vlsp.org.vn/vlsp2025/cfp , https://aclanthology.org/2025.vlsp-1.21/ , https://arxiv.org/abs/2403.03435
- **Maintainer:** VLSP workshop community (11th International Workshop on Vietnamese Language and Speech Processing, 2025).
- **Scope:** Shared tasks benchmarking legal reasoning of Vietnamese small LMs (LegalSLM), legal textual entailment (LTER), and "Legal Landscape (DRiLL)".
- **Size:** Task-scale corpora (unverified counts).
- **Formats:** Shared-task data releases to participants.
- **Update status:** Active — VLSP 2025 proceedings published.
- **Provenance:** Built by task organizers from Vietnamese legal texts.
- **License:** unknown (typically research-use task licences).
- **Strengths:** Community benchmark venue; keeps evaluation methodology honest.
- **Weaknesses:** Task data often restricted to participants; not a canonical corpus.
- **VNKC recommendation:** `contribute-upstream` — offer VNKC-structured legal data as future shared-task material rather than duplicating benchmarks.
- **Evidence:** ACL Anthology + VLSP CFP + arXiv LTER paper, accessed 2026-07-27, source type: paper, confidence: verified.

## 6. VnCoreNLP

- **URL:** https://github.com/vncorenlp/VnCoreNLP (paper: https://aclanthology.org/N18-5012.pdf)
- **Maintainer:** Dat Quoc Nguyen and colleagues.
- **Scope:** Vietnamese NLP annotation pipeline (word segmentation, POS, NER, dependency parsing) plus the annotated corpora it was trained/evaluated on.
- **Size:** Toolkit; corpora sizes per original papers (wseg F1 97.90%, 62K words/sec).
- **Formats:** Java toolkit, Python wrapper (py_vncorenlp), model binaries.
- **Update status:** Maintenance mode — stable since 2018; lightweight components split out (RDRsegmenter, VnMarMoT).
- **Provenance:** Academic corpora (VLSP treebanks etc.).
- **License:** unknown — a custom License file is present in the repo but its terms were not captured here; historically research-oriented. Verify before redistribution.
- **Strengths:** De-facto standard tokenizer/annotator for Vietnamese; needed to process VNKC text consistently with the research ecosystem.
- **Weaknesses:** Licence ambiguity; Java dependency.
- **VNKC recommendation:** `interoperate` — use for text processing; do not re-host its corpora without licence clarity.
- **Evidence:** GitHub repo + NAACL 2018 paper, accessed 2026-07-27, source type: github-repo, confidence: verified (licence: unverified).

## 7. PhoBERT

- **URL:** https://github.com/VinAIResearch/PhoBERT (paper: https://aclanthology.org/2020.findings-emnlp.92.pdf)
- **Maintainer:** VinAI Research (Dat Quoc Nguyen, Anh Tuan Nguyen).
- **Scope:** First public large-scale monolingual Vietnamese pre-trained LMs (base/large); era-defining pre-training corpus (~20GB Vietnamese text per paper — size: partial confidence).
- **Size:** Two model variants; corpus ~20GB (partial).
- **Formats:** Model weights (fairseq/transformers), training corpus not fully re-distributed.
- **Update status:** Stable — no releases published on the repo; PhoBERT v2 added later.
- **Provenance:** Vietnamese news + Wikipedia text.
- **License:** MIT (original) and AGPL-3.0 for PhoBERT v2 (two LICENSE files in repo).
- **Strengths:** Reference encoder for Vietnamese; clear dual licences.
- **Weaknesses:** Corpus itself not versioned/re-distributed as data; v2's AGPL is copyleft.
- **VNKC recommendation:** `interoperate` — consume embeddings/models; VNKC should not re-host the corpus but can publish the _document_ layer models lack.
- **Evidence:** GitHub repo (licences observed) + EMNLP 2020 paper, accessed 2026-07-27, source type: github-repo, confidence: verified (corpus size: partial).

## 8. zalo-ai-legal-text-retrieval-vn

- **URL:** https://huggingface.co/datasets/GreenNode/zalo-ai-legal-text-retrieval-vn (origin: https://challenge.zalo.ai/)
- **Maintainer:** Zalo AI (original challenge); GreenNode mirror as an MTEB dataset ("ZacLegalTextRetrieval").
- **Scope:** Vietnamese legal text retrieval benchmark.
- **Size:** corpus 61.4K rows, queries 818, qrels 793.
- **Formats:** HF dataset (MTEB format: corpus/queries/qrels).
- **Update status:** Static mirror of a past Zalo AI Challenge dataset.
- **Provenance:** Zalo AI Challenge legal domain data.
- **License:** unknown.
- **Strengths:** Ready-made retrieval benchmark in MTEB shape — directly usable to evaluate search over VNKC.
- **Weaknesses:** Licence unknown; one parquet subset currently errors in the HF viewer; static.
- **VNKC recommendation:** `reuse` — evaluation only.
- **Evidence:** HF dataset page, accessed 2026-07-27, source type: hf-dataset, confidence: verified (licence: unverified).

## 9. vietnamese-provinces-database

- **URL:** https://github.com/thanglequoc/vietnamese-provinces-database
- **Maintainer:** Thang Le Quoc.
- **Scope:** SQL + GIS datasets for all Vietnamese administrative units; post-2025-merger structure: 34 provinces, 3,321 commune-level units (two-tier system), optional GeoJSON boundary add-on.
- **Size:** 34 provinces / 3,321 communes (100% coverage claimed); SQL dumps + GeoJSON.
- **Formats:** SQL (multiple dialects), GeoJSON.
- **Update status:** Very active — release table tracks government decrees one-to-one, including 19/2025/QĐ-TTg (01/07/2025 merger) and April 2026 decrees (v3.1.0, v4.x GIS).
- **Provenance:** Government decrees (danhmuchanhchinh.nso.gov.vn); GIS boundaries derived from the official Administrative Units Reference Map (sapnhap.bando.com.vn, Ministry of Agriculture and Environment publishing house).
- **License:** MIT.
- **Strengths:** Decree-by-decree version tracking = de-facto temporal versioning of admin units; official-cartography-derived boundaries; permissive licence.
- **Weaknesses:** Single maintainer; boundaries are a derived add-on, not survey-grade.
- **VNKC recommendation:** `reuse` — adopt as the administrative-units backbone and mirror its decree-versioning pattern for legal documents.
- **Evidence:** GitHub repo incl. decree release table and GIS readme, accessed 2026-07-27, source type: github-repo, confidence: verified.

## 10. vietnamadminunits

- **URL:** https://github.com/tranngocminhhieu/vietnamadminunits
- **Maintainer:** Tran Ngoc Minh Hieu.
- **Scope:** Parser/converter to update and standardize addresses after the July 2025 administrative merger — old→new address mapping for logistics/e-commerce datasets.
- **Size:** unverified (mapping tables for the 2025 merger).
- **Formats:** Code + mapping data.
- **Update status:** Active (2025, merger-focused).
- **Provenance:** 2025 merger decrees / official unit lists.
- **License:** MIT.
- **Strengths:** Solves the painful legacy-address migration problem nobody else packages; MIT.
- **Weaknesses:** Narrow (address conversion only); single maintainer.
- **VNKC recommendation:** `reuse` — the old↔new mapping is exactly the temporal link VNKC needs between pre- and post-merger records.
- **Evidence:** GitHub repo, accessed 2026-07-27, source type: github-repo, confidence: verified (size: unverified).

## 11. GADM (Vietnam layers)

- **URL:** https://gadm.org/ , https://gadm.org/download_country.html
- **Maintainer:** GADM project (UC Berkeley origins).
- **Scope:** Global administrative boundary database; Vietnam country layer.
- **Size:** v4.1 delimits 400,276 administrative areas worldwide.
- **Formats:** Geopackage/shapefile/R formats per country.
- **Update status:** Stale for Viet Nam — v4.1 predates the 2025 mergers; "Version 5 will be released in January 2026" per site (v5 VN content unverified at access date).
- **Provenance:** Compiled from national sources, methodology not fully transparent.
- **License:** Free for academic and other non-commercial use (not open in the OSI sense; commercial use restricted).
- **Strengths:** Familiar global standard; multi-format.
- **Weaknesses:** Non-commercial restriction conflicts with VNKC's open mandate; currently wrong for post-merger Viet Nam.
- **VNKC recommendation:** `avoid-duplication` — do not build on GADM; use #9's MIT/official-cartography boundaries instead.
- **Evidence:** gadm.org data + download pages, accessed 2026-07-27, source type: docs-site, confidence: verified.

## 12. Open Development Vietnam

- **URL:** https://vietnam.opendevelopmentmekong.net/en/data/
- **Maintainer:** Open Development Mekong (East-West Management Institute).
- **Scope:** Curated open datasets on Viet Nam (land, environment, economy, infrastructure, SDGs) within the Mekong datahub.
- **Size:** Hundreds of datasets (unverified count).
- **Formats:** GeoJSON, CSV, PDFs, CKAN API.
- **Update status:** Active.
- **Provenance:** Government and partner sources, curated with metadata.
- **License:** CC-BY-SA-4.0 for original materials (per-dataset licences vary).
- **Strengths:** Proper metadata curation and CKAN API; clear licensing practice — a working example of what VNKC wants to be for civic data.
- **Weaknesses:** Thematic (development/environment), not legal-administrative core; ShareAlike may not suit all VNKC outputs.
- **VNKC recommendation:** `interoperate` — cross-link datasets, align metadata practices (CKAN), don't duplicate their geospatial layers.
- **Evidence:** OD Vietnam data page + OD Mekong licence statements, accessed 2026-07-27, source type: docs-site, confidence: verified.

## 13. data.gov.vn

- **URL:** https://data.gov.vn (launch notice: https://mst.gov.vn/khoi-dong-cong-du-lieu-quoc-gia-datagovvn-197120102.htm)
- **Maintainer:** Ministry of Information and Communications (Bộ TT&TT), launched 31/8 (national open-data portal kickoff).
- **Scope:** National open-data portal aggregating government datasets; complemented by municipal portals (e.g. opendata.hochiminhcity.gov.vn).
- **Size:** unverified.
- **Formats:** Portal downloads/APIs (unverified).
- **Update status:** Portal exists and was live in recent reporting; dataset depth/freshness unverified (portal fetch failed from research environment at access date).
- **Provenance:** Contributing ministries and provinces.
- **License:** unknown (no uniform licence observed).
- **Strengths:** Official upstream — where authoritative government datasets _should_ land.
- **Weaknesses:** Historically thin, inconsistent metadata and no uniform licence; hard to build on programmatically.
- **VNKC recommendation:** `interoperate` — treat as provenance source; VNKC's value-add is normalization, versioning, and licensing clarity the portal lacks.
- **Evidence:** MIC launch announcement (mst.gov.vn) + OD Mekong coverage; accessed 2026-07-27, source type: gov-portal, confidence: partial.

## 14. vbpl.vn — CSDL Quốc gia về Pháp luật (+ ws.vbpl.vn API)

- **URL:** https://vbpl.vn , integration layer https://ws.vbpl.vn (API described in ministry integration guide)
- **Maintainer:** Ministry of Justice (Bộ Tư pháp) — national legal database.
- **Scope:** Authoritative database of central legal normative documents (laws, decrees, circulars, resolutions...), with document metadata and status (hiệu lực).
- **Size:** unverified (full national corpus; 127K documents appear in derived scrapes).
- **Formats:** Web portal; integration API endpoints (`/api/vbpl/document` search & detail) per official integration guide.
- **Update status:** Active — the canonical reference used by every derived dataset above.
- **Provenance:** Primary — published by the state.
- **License:** unknown (government data; no explicit open licence observed).
- **Strengths:** The single source of truth for legal text + status; has a documented data-integration API.
- **Weaknesses:** No open licence; portal is JS-driven (hard to scrape politely); API access terms undocumented publicly.
- **VNKC recommendation:** `interoperate` — cite as provenance root for all legal records; negotiate/seek clarity on API + licence rather than re-scraping at scale.
- **Evidence:** vbpl.vn portal + ministry integration guide PDF (asttmoh.vn mirror) + secondary analysis (phaply.net.vn), accessed 2026-07-27, source type: gov-portal, confidence: verified (API terms: partial).

## 15. Wikidata — Viet Nam entities

- **URL:** https://www.wikidata.org/
- **Maintainer:** Wikimedia community.
- **Scope:** General-purpose knowledge graph; substantial Viet Nam coverage (people, places, administrative units, some laws) but shallow on legal/administrative-procedure structure.
- **Size:** 100M+ items overall; VN-specific count unverified.
- **Formats:** RDF/JSON dumps, SPARQL endpoint, REST API.
- **Update status:** Continuously updated.
- **Provenance:** Crowd-sourced with references; Vietnamese Wikipedia is a major substrate.
- **License:** CC0-1.0.
- **Strengths:** CC0, stable identifiers (QIDs), SPARQL federation — the natural interlinking hub for VNKC entity IDs.
- **Weaknesses:** Inconsistent sourcing depth for VN legal entities; no temporal legal versioning model.
- **VNKC recommendation:** `interoperate` — mint VNKC IDs with `sameAs` links to Wikidata QIDs; contribute well-sourced VN statements upstream.
- **Evidence:** wikidata.org (licence/terms), accessed 2026-07-27, source type: docs-site, confidence: verified. (Note: a Vietnamese DBpedia chapter could not be confirmed from primary sources at access date — unverified.)

## 16. Vietnamese legal-cases knowledge graph (arXiv 2309.09069)

- **URL:** https://arxiv.org/abs/2309.09069
- **Maintainer:** Vuong T. Huy, Ha Thanh Nguyen et al. (academic).
- **Scope:** Heterogeneous knowledge graph constructed over Vietnamese legal cases.
- **Size:** 9,578 published court cases.
- **Formats:** Research artifact (graph construction methodology; Neo4j-style heterogeneous graph).
- **Update status:** Static (v1, 16 Sep 2023).
- **Provenance:** Court cases published by the Supreme People's Court of Viet Nam.
- **License:** unknown (paper is open; dataset availability not confirmed).
- **Strengths:** Demonstrates entity/relation schema for VN case law — useful design input if VNKC ever covers án lệ/bản án.
- **Weaknesses:** Small, static, availability of the actual graph unverified.
- **VNKC recommendation:** `reuse` — borrow the schema ideas; do not depend on the artifact.
- **Evidence:** arXiv abstract page, accessed 2026-07-27, source type: paper, confidence: partial.

---

## Gaps and opportunities for VNKC

1. **Temporal versioning of legal documents is unsolved.** Projects track _current_ in-force status (UTS_VLC) or scrape bulk text (th1nhng0), but nobody publishes amendment-level history (sửa đổi/bãi bỏ chains, consolidated vs. original versions) as structured, queryable data. The provinces-database decree-table pattern (#9) shows the community wants exactly this.
2. **Administrative procedures (TTHC) exist nowhere as structured open data.** All legal corpora cover văn bản quy phạm pháp luật; procedures (components, fees, timelines, forms) on the National Public Service Portal are untouched by every dataset surveyed.
3. **No provenance-chain standard.** Only UTS_VLC ships per-document source links, and only duyet documents a two-hop chain. There is no shared convention (e.g. PROV-O/W3C) linking scraped text → official gazette → promulgating agency.
4. **Licence chaos.** Half the entries are `unknown`/custom/restricted (GADM non-commercial, VnCoreNLP custom, vbpl.vn unstated). A CC0/CC-BY, licence-explicit VNKC layer is itself a contribution.
5. **Pre/post-2025-merger entity linkage is fragile.** Two MIT projects (#9, #10) cover the new map and address conversion, but legal documents, statistics, and forms still reference pre-merger units — nobody maintains a versioned, machine-readable mapping _as knowledge-graph data_ with effective dates.
6. **Machine-readable forms and statistics are absent.** No surveyed project covers government forms (biểu mẫu) or GSO statistics as structured, versioned datasets.
