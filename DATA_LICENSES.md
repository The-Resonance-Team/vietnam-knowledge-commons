# Data Licenses

How VNKC thinks about redistribution. Legal research behind this file: [`docs/research/legal-and-licensing.md`](./docs/research/legal-and-licensing.md). Governance: ADR-0003.

## The one rule above all

**There is no blanket license on collected data.** Different sources carry different rights; pretending otherwise is how open-data projects get taken down. Every record and every release is explicit about what it may do.

## Code vs data

| What                                                                                    | License                                              |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| Code: JSON Schemas, SDKs, CLI, CI, this repo's original documentation                   | [Apache-2.0](./LICENSE)                              |
| Collected source material                                                               | **per-source** — see the controlled vocabulary below |
| Original derived content (record structure, benchmarks, evaluation sets, dataset cards) | CC-BY-4.0, decided per-release in the dataset card   |

## Controlled license vocabulary

Every source and record carries exactly one `license_status`:

| Status                | Meaning                                                                                                  | May we redistribute content?      |
| --------------------- | -------------------------------------------------------------------------------------------------------- | --------------------------------- |
| `verified-open`       | Reuse rights verified against a cited basis (e.g. officially designated open data under the Law on Data) | Yes, with attribution             |
| `permission-required` | Reuse plausible but needs explicit permission from the authority                                         | Not yet — obtain permission first |
| `metadata-only`       | We publish bibliographic metadata, never the content                                                     | Metadata yes, content no          |
| `reference-only`      | **Default.** We link and cite; we do not republish content                                               | No — link out                     |
| `unknown`             | Not yet assessed (treat exactly like `reference-only`)                                                   | No                                |
| `prohibited`          | Source terms prohibit reuse                                                                              | No; do not ingest content         |

Relevant findings (cited in the research doc):

- **Art. 15.2, Law 50/2005/QH11 (IP Law)**: legal normative, administrative, and judicial documents and their official translations are excluded from copyright protection. This removes _copyright_ as a barrier for those texts — it does not grant a positive right, and does not cover commentary, collections, website design, or forms with creative content.
- **Law on Data 60/2024/QH15, Điều 35.3(c)**: anyone may freely exploit and use officially designated **open data** — the strongest positive redistribution basis, but only for data so designated.
- Portals commonly require **attribution** ("ghi rõ nguồn …"). We record each portal's requirement in `registry/sources.yaml` → `attribution`.

## Release manifests

Every `DatasetRelease` ships a `license_manifest` enumerating every contributing source with its `license_status`, license (SPDX where one applies), and required attribution. Releases are gated on: no `unknown`/`prohibited` entries, PII sweep clean, checksums verified.

## Professional review

The unresolved items in `docs/research/legal-and-licensing.md` (8 items, incl. database-rights absence confirmation and portal ToS gaps) gate the first public **content** release. This file is engineering policy, not legal advice.
