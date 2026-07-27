---
title: "VNKC Official Sources Inventory — 2026-07"
date: "2026-07-27"
status: draft
---

# Official Sources Inventory (candidate registry)

Companion machine-readable registry: `registry/sources.yaml`.

Verification method: direct HTTPS fetches (status, redirects, titles), `robots.txt` retrieval for 32 hosts, DNS checks, and targeted web searches for the 2025 restructuring. Anything not observed is marked `unknown`/`unverified` — nothing in the registry is assumed from memory alone.

## Tier definitions

| Tier | Meaning                                                                                                                   | Ground truth?              |
| ---- | ------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| A    | Authoritative primary source — the document published by its issuing authority (or the official database mandated by law) | Yes                        |
| B    | Official first-party explanatory source — ministry/agency guidance, portals, service apps                                 | No — cite back to Tier A   |
| C    | Academic or curated open dataset (non-government)                                                                         | No — curated reference     |
| D    | Secondary discovery source (commercial aggregators, news)                                                                 | **Never** — discovery only |

## Context: the 2025 restructuring (why so many old URLs are dead)

- **Ministries:** from early 2025 Viet Nam consolidated to **14 ministries**. Confirmed dead/moved domains: `mard.gov.vn` (NXDOMAIN), `monre.gov.vn` (404), `mpi.gov.vn` (500/SSL errors), `mic.gov.vn` (NXDOMAIN), `mot.gov.vn`/`mt.gov.vn` (gone/SSL), `molisa.gov.vn` (cert expired; `www.molisa.gov.vn` serves a legacy archive). New/continuing canonical domains verified live: `mae.gov.vn` (Bộ Nông nghiệp và Môi trường = MARD+MONRE), `moc.gov.vn` (Bộ Xây dựng, absorbed Transport), `mst.gov.vn` (Bộ Khoa học và Công nghệ, absorbed MIC), `mof.gov.vn` (Bộ Tài chính, absorbed MPI), `moha.gov.vn` (Bộ Nội vụ, absorbed MOLISA labour functions from 1/3/2025).
- **Provinces:** National Assembly resolution of 12/6/2025 reduced 63 → **34 province-level units** (28 tỉnh + 6 thành phố), operating from 1/7/2025, with **2-tier local government** (province + commune; district level abolished). New merged-province portals verified live: `hochiminhcity.gov.vn`, `phutho.gov.vn`, `bacninh.gov.vn`, `danang.gov.vn`, `hue.gov.vn`, `haiphong.gov.vn`, `cantho.gov.vn`. Legacy portals dead/unreachable: `tphcm.gov.vn`, `thuathienhue.gov.vn`.
- Evidence: chinhphu.vn ministry listing (`https://chinhphu.vn/cac-bo-co-quan-ngang-bo-co-quan-thuoc-chinh-phu`), NA resolution coverage (`https://xaydungchinhsach.chinhphu.vn/chi-tiet-34-don-vi-hanh-chinh-cap-tinh-tu-12-6-2025-119250612141845533.htm`), MOLISA dissolution (`https://tuoitre.vn/khong-con-ten-bo-lao-dong-thuong-binh-xa-hoi-tu-1-3-...`), VSS under MoF from 12/9/2025 (baohiemxahoi.gov.vn + thuvienphapluat.vn coverage).

## Summary table

| id                   | Name                               | Tier | License             | API                     |
| -------------------- | ---------------------------------- | ---- | ------------------- | ----------------------- |
| moj-vbpl             | CSDL quốc gia về VBQPPL (vbpl.vn)  | A    | reference-only      | unknown                 |
| gov-congbao          | Công báo Chính phủ                 | A    | reference-only      | unknown                 |
| gov-vanban           | Cổng văn bản Chính phủ             | A    | reference-only      | unknown                 |
| na-quochoi           | Cổng TTĐT Quốc hội                 | A    | reference-only      | unknown                 |
| nso-statistics       | Cục Thống kê (nso.gov.vn)          | A    | reference-only      | unknown                 |
| mof-dkkd             | Cổng quốc gia đăng ký doanh nghiệp | A    | reference-only      | unknown                 |
| npsp-dichvucong      | Cổng Dịch vụ công Quốc gia         | B    | reference-only      | unknown                 |
| gov-chinhphu         | Cổng TTĐT Chính phủ                | B    | reference-only      | unknown                 |
| mof-finance          | Bộ Tài chính                       | B    | reference-only      | unknown                 |
| gdt-tax              | Cổng ngành Thuế (gdt.gov.vn)       | B    | reference-only      | unknown                 |
| gdt-etax             | Thuế điện tử (doanh nghiệp)        | B    | reference-only      | unknown                 |
| gdt-etax-canhan      | Thuế điện tử (cá nhân)             | B    | reference-only      | unknown                 |
| mof-haiquan          | Tổng cục Hải quan                  | B    | reference-only      | unknown                 |
| bhxh-vss             | BHXH Việt Nam                      | B    | reference-only      | unknown                 |
| moha-noivu           | Bộ Nội vụ                          | B    | reference-only      | unknown                 |
| moh-yte              | Bộ Y tế                            | B    | reference-only      | unknown                 |
| moet-giaoduc         | Bộ GD&ĐT                           | B    | reference-only      | unknown                 |
| mae-nnmt             | Bộ Nông nghiệp và Môi trường       | B    | reference-only      | unknown                 |
| moc-xaydung          | Bộ Xây dựng                        | B    | reference-only      | unknown                 |
| moit-congthuong      | Bộ Công Thương                     | B    | reference-only      | unknown                 |
| moj-tuphap           | Bộ Tư pháp                         | B    | reference-only      | unknown                 |
| bvhttdl-vanhoa       | Bộ VHTT&DL                         | B    | reference-only      | unknown                 |
| bocongan-mps         | Bộ Công an                         | B    | reference-only      | unknown                 |
| mps-dvc              | Cổng DVC Bộ Công an                | B    | reference-only      | unknown                 |
| mofa-ngoaigiao       | Bộ Ngoại giao                      | B    | reference-only      | unknown                 |
| opendata-quocgia     | Cổng dữ liệu mở quốc gia           | B    | reference-only      | unknown (unverified)    |
| hanoi-portal         | Cổng TTĐT TP Hà Nội                | B    | reference-only      | unknown                 |
| hcmc-portal          | Cổng TTĐT TP Hồ Chí Minh           | B    | reference-only      | unknown                 |
| danang-portal        | Cổng TTĐT TP Đà Nẵng               | B    | reference-only      | unknown                 |
| phutho-portal        | Cổng TTĐT tỉnh Phú Thọ             | B    | reference-only      | unknown                 |
| bacninh-portal       | Cổng TTĐT tỉnh Bắc Ninh            | B    | reference-only      | unknown                 |
| odm-vietnam          | Open Development Vietnam           | C    | reference-only      | unknown                 |
| gadm-boundaries      | GADM                               | C    | reference-only      | unknown (bulk download) |
| tvpl-thuvienphapluat | Thư viện Pháp luật                 | D    | permission-required | unknown                 |
| lawnet               | LawNet → thuviennhadat.vn          | D    | permission-required | unknown                 |
| luatvietnam          | Luật Việt Nam                      | D    | permission-required | unknown                 |

**Totals: 36 sources — A: 6, B: 25, C: 2, D: 3. Verified: 35. Unverified: 1.**

## Tier A — authoritative primary sources

### moj-vbpl — Cơ sở dữ liệu quốc gia về VBQPPL (vbpl.vn)

- Publisher: Bộ Tư pháp. Status: live 200. robots.txt: 200, 2 Disallow lines, declares `Sitemap: https://vbpl.vn/sitemap.xml` (verified — sitemap index with per-collection files, e.g. `/sitemap/1.xml` for Trung ương documents; excellent crawl entry point).
- API: none found (`api.vbpl.vn` unreachable; no API links on homepage — only `/gioi-thieu`).
- This is the official national legal database mandated by the Law on Promulgation of Legal Normative Documents — the VNKC backbone for `law`.

### gov-congbao — Công báo Chính phủ

- Publisher: Văn phòng Chính phủ. Live 200. robots.txt 200, no disallows.
- The Official Gazette: the legally authentic publication channel. No API found.

### gov-vanban — Cổng văn bản Chính phủ (vanban.chinhphu.vn)

- Publisher: Văn phòng Chính phủ. Live 200. robots.txt 200, no disallows.
- Nghị định, Nghị quyết, Quyết định, Chỉ thị, Công điện as issued.

### na-quochoi — Cổng TTĐT Quốc hội (quochoi.vn)

- Publisher: Văn phòng Quốc hội. Live 200. robots.txt 200, no disallows.
- Laws/ordinances/resolutions from the issuing authority.

### nso-statistics — Cục Thống kê (nso.gov.vn)

- **Portal move found:** `gso.gov.vn` → (via `www.gso.gov.vn`, which carries an SSL cert mismatch on the bare domain) → **`https://www.nso.gov.vn/`**, title "General Statistics Office of Vietnam". Bare `nso.gov.vn` did not resolve from the test resolver — use the `www` host. robots.txt: 200, 23 Disallow lines.
- NSO is under the Ministry of Finance since the 2025 restructuring.

### mof-dkkd — Cổng quốc gia về đăng ký doanh nghiệp (dangkykinhdoanh.gov.vn)

- Official enterprise registry. Live 200 (SharePoint `/vn/Pages/Trangchu.aspx`). robots.txt 404.
- Moved from ex-MPI to Bộ Tài chính in the 2025 merger. PII caution: records name legal representatives.

## Tier B — official first-party sources

### npsp-dichvucong — Cổng Dịch vụ công Quốc gia (dichvucong.gov.vn)

- **Verified: still canonical at `dichvucong.gov.vn` on 2026-07-27** (200, no replacement found). robots.txt 200, no disallows.
- Hosts the National Administrative Procedures Database (CSDL quốc gia về TTHC). The former standalone `thutuchanhchinh.vn` is **NXDOMAIN** — the TTHC database lives inside the NPSP now. Homepage is a JS app; no public API documented.

### gov-chinhphu — Cổng TTĐT Chính phủ (chinhphu.vn)

- Live 200; robots.txt 200, no disallows. Explanatory/news layer; hosts the canonical ministry list used to verify the 14-ministry structure.

### mof-finance — Bộ Tài chính (mof.gov.vn)

- Live 200; robots.txt 200, no disallows. Absorbed MPI (`mpi.gov.vn` returns 500/SSL errors). Parent ministry for tax, customs, statistics, business registration, and VSS.

### gdt-tax / gdt-etax / gdt-etax-canhan — ngành Thuế

- `gdt.gov.vn` live 200 (→ `/wps/portal`); robots.txt 200, no disallows. `thuedientu.gdt.gov.vn` live 200 (session app). `canhan.gdt.gov.vn` live 200 (session app). `tracuu.gdt.gov.vn` unreachable from test environment.
- Exact post-2025 unit name (Tổng cục Thuế vs Cục Thuế) not yet confirmed — see Unresolved questions.

### mof-haiquan — Tổng cục Hải quan (customs.gov.vn)

- Live 200; robots.txt 200, no disallows. Tariffs, HS codes, customs procedures.

### bhxh-vss — Bảo hiểm xã hội Việt Nam (baohiemxahoi.gov.vn)

- Live 200 (SharePoint `/Pages/default.aspx`); robots.txt 404.
- **Governance change:** VSS is a _đơn vị đặc thù trực thuộc Bộ Tài chính_ from 12/9/2025 (evidence: baohiemxahoi.gov.vn news + thuvienphapluat.vn explainer).

### moha-noivu — Bộ Nội vụ (moha.gov.vn)

- Live 200; robots.txt 200, no disallows.
- **MOLISA dissolved from 1/3/2025**; labour/employment/việc làm functions moved to Bộ Nội vụ (evidence: tuoitre.vn, vneconomy.vn coverage; `molisa.gov.vn` cert expired, `www.molisa.gov.vn` legacy archive 200). MOHA is now the Tier B anchor for the `labor` domain.

### moh-yte, moet-giaoduc, moit-congthuong, moj-tuphap, bvhttdl-vanhoa, mofa-ngoaigiao

- All live 200. robots.txt: moh (no disallows), moet (23 disallows), moit (7), moj (3 + sitemap), bvhttdl (1), mofa (1 + sitemap).
- moj.gov.vn also anchors `civil-status` (hộ tịch); mofa.gov.vn covers consular legalization.

### mae-nnmt — Bộ Nông nghiệp và Môi trường (mae.gov.vn)

- **New merged ministry domain, live 200** (MARD + MONRE). `mard.gov.vn` NXDOMAIN; `www.monre.gov.vn` 404. Tier B anchor for `land`, `environment`, `agriculture`.

### moc-xaydung — Bộ Xây dựng (moc.gov.vn)

- Live 200 (→ `/vn/Pages/Trangchu.aspx`). Absorbed Transport (`mot.gov.vn` NXDOMAIN, `mt.gov.vn` SSL errors). **`xaydung.gov.vn` returns 404 — not the ministry portal; `moc.gov.vn` is canonical.**

### bocongan-mps / mps-dvc — Bộ Công an

- `bocongan.gov.vn` live 200 (robots 200 + sitemap); `dichvucong.bocongan.gov.vn` live 200. Anchors `civil-status` (population database, CCCD, cư trú, hộ chiếu, VNeID).

### opendata-quocgia — Cổng dữ liệu mở (open.data.gov.vn) — **UNVERIFIED**

- MIC-era announcement: open data portal at `https://open.data.gov.vn` under the National Data Portal (`data.gov.vn`). On 2026-07-27 **both returned DNS NXDOMAIN** from the test resolver. Possibly resolver-specific or genuinely down — re-check. Operator ministry is now Bộ KH&CN (`mst.gov.vn`, live 200).

### Provincial portals (post-merger, all Tier B)

- `hanoi.gov.vn` — live 200, robots clean. (Unmerged.)
- `hochiminhcity.gov.vn` — live 200, sitemap declared; legacy `tphcm.gov.vn` unreachable. Merged: HCMC + Bình Dương + BR–VT.
- `danang.gov.vn` — live 200, sitemap; merged with Quảng Nam.
- `phutho.gov.vn` — live 200, 30 robots disallows + sitemap; merged Phú Thọ + Vĩnh Phúc + Hòa Bình.
- `bacninh.gov.vn` — live 200, sitemap; merged Bắc Ninh + Bắc Giang.
- Also verified live (not yet in registry): `haiphong.gov.vn`, `cantho.gov.vn`, `hue.gov.vn`. Dead: `thuathienhue.gov.vn`.

## Tier C — curated open datasets

### odm-vietnam — Open Development Vietnam

- Live 200. Curated land/environment/development datasets. CKAN-style API probe returned HTML (endpoint not confirmed). Per-dataset licenses must be checked before reuse.

### gadm-boundaries — GADM (gadm.org)

- Live 200. Bulk boundary downloads (shapefile/geopackage). Historically academic/non-commercial terms — verify current license. Post-2025 Vietnamese boundaries (34 provinces) may lag.

## Tier D — commercial discovery sources (never ground truth)

### tvpl-thuvienphapluat — thuvienphapluat.vn

- Homepage 403 to default curl UA (bot filtering) — site is up. robots.txt 200, 9 disallows + 2 sitemaps. Paid commercial legal DB; useful for change detection and EN translations; always resolve to Tier A.

### lawnet — lawnet.vn

- **Observed move:** 301 redirect to `https://thuviennhadat.vn/van-ban-phap-luat-viet-nam`. LawNet brand appears absorbed by Thư viện Nhà Đất; relationship unverified. Treat legacy LawNet citations with caution.

### luatvietnam — luatvietnam.vn

- Live 200; robots.txt 403 (bot filtering). Commercial; discovery only.

## Unresolved questions

1. **Who operates the NPSP post-2025?** `dichvucong.gov.vn` is canonical, but the operating authority (Văn phòng Chính phủ vs another body after restructuring) is not confirmed on the site surface.
2. **open.data.gov.vn / data.gov.vn NXDOMAIN** — resolver-specific or national outage/migration? Re-verify from a different network and via Bộ KH&CN announcements.
3. **Exact names of tax and customs units** after the MoF restructure (Tổng cục Thuế/Hải quan vs Cục Thuế/Hải quan) — portal chrome did not confirm; check a recent MoF decree.
4. **Destination of MOLISA's social-welfare/children functions** (Cục Bảo trợ xã hội, Cục Trẻ em) — reported as transferred (likely Bộ Y tế) but not verified on moh.gov.vn in this pass.
5. **Does any public API exist** for vbpl.vn, the NPSP, or the TTHC database? None found; only vbpl.vn's sitemap index is a confirmed machine-readable surface.
6. **LawNet → Thư viện Nhà Đất**: acquisition, rebrand, or domain sale? Unverified.
7. **National surveying/mapping (geography) portal**: `dos.gov.vn` unreachable; the function now sits under Bộ NN&MT but no canonical data portal was confirmed.
8. **Terms-of-use/copyright pages**: none located for any source in this pass (all `tos_url: null`). A dedicated sweep is needed before any bulk ingestion.
9. `gso.gov.vn` bare domain serves a certificate with mismatched SAN while `www.gso.gov.vn` redirects to `www.nso.gov.vn` — cleanup likely in progress; monitor.
10. `nso.gov.vn` bare domain does not resolve while `www.nso.gov.vn` works — confirm whether this is intentional.
