---
type: system_manifest
title: "ALUX Template Bank v1.0"
status: layout-v1
updated: 2026-10-01
owner: Rijal
tags:
  - system
  - assets
  - graphics
  - templates
---

# ALUX Template Bank v1.0

Manifest template grafis untuk After Effects, diturunkan dari 2 script yang sudah diproduksi:
- **EP01** *The Millionaire Map: How Insurance Actually Works* (±10.500 kata, 16 chapter)
- **EP02** *The Millionaire Map: How the Diamond Cartel (De Beers) Actually Works* (±13.900 kata, 10 chapter)

Figma: `aX4ORFo5SAgCqboUpx9hUz`, page **ALUX — Templates**, section `359:20` (*ALUX — Template Bank v1.0*). Sistem visual ikut **Video Standard v1.0** (page Foundations, section `345:2`).

Status: **layout saja.** Aset final (ilustrasi, QR, screenshot headline, footage) belum dibuat; slot-nya sudah ada.

## Kebutuhan dari script (hitungan marker)

| Marker di script | EP01 | EP02 | Template |
|---|---:|---:|---|
| `CHAPTER n:` | 16 | 10 | A02 (utama) · A03 (sub-chapter 5B/5C/7B/8C/9B/9C) |
| `COLD OPEN` | 1 | 1 | A01 setelah cold open |
| `QUICK FACT:` | 5 | 0 | A04 |
| `ON-SCREEN GRAPHIC:` (data) | 9 | 0 | C01–C05, D01–D05 |
| `ON-SCREEN GRAPHIC: file.jpg \| caption` | 15 | 0 | C04, E01, E04, F02, F03, H04 |
| `ILLUSTRATION CARD (square)` | 10 | 0 | F01 |
| `TIMELINE CARD (wide)` | 1 | 0 | E03 |
| `ON-SCREEN CTA` | 4 | 0 | G02, G03, G04 |
| `[VISUAL ASSET]` total | 0 | 45 | C/D/E/F |
| └ `ALUX STAT SEQUENCE nn/03` | 0 | 17 | C02 |
| └ `ALUX STORY VISUAL` | 0 | 4 | E02, E03, E05 |
| `[HISTORICAL IMAGE]` / brand / leadership | 0 | 7 | B01, B02, B03 |
| `[ARCHIVAL AD]` | 0 | 1 | B03 |
| `[IMAGE HERE: headlines/...]` | 0 | 8 | B04 |
| `[QR CODE ON SCREEN]` | 0 | 2 | G02 |

## 40 template (8 famili × 5)

ID = tag `GFX:<id>` di marking script. Semua master 3840×2160, layer `field:*` = kontrol Essential Graphics.

| ID | Nama | Dipakai saat | Fields utama |
|---|---|---|---|
| **A · Structure** ||||
| A01 | Series opener | setelah cold open | series, episode, title, lat/lon, plate |
| A02 | Chapter card (cyan) | tiap chapter utama | number, title, rail list, active index |
| A03 | Sub-chapter on footage | chapter B/C | number, title, progress segments |
| A04 | Quick fact | `QUICK FACT:` | question, answer 1–3 kata, detail, source |
| A05 | Brand wipe | ganti chapter / lompat waktu | direction, edge color |
| **B · People & evidence** ||||
| B01 | Lower third | tokoh muncul pertama | name, role, place/year, credit |
| B02 | Bio card | tokoh pembawa chapter | portrait, name, role, 2–5 fact rows |
| B03 | Archive plate | `[HISTORICAL IMAGE]`, `[ARCHIVAL AD]` | image, year, caption, credit, fig no |
| B04 | Headline clipping | `[IMAGE HERE: headlines/]` | outlet, headline, date, highlight, screenshot |
| B05 | Document excerpt | kutipan memo/iklan/filing | doc, quote ≤6 kata, context, source |
| **C · Numbers** ||||
| C01 | Stat hero | satu angka = satu beat | kicker, value, context, source, tone |
| C02 | Stat sequence 01/03 | `ALUX STAT SEQUENCE` | 3 × (value, label, note), active |
| C03 | Rate counter | angka per detik/hari | value, unit, cycle |
| C04 | Unit grid N/100 | "N out of 100" | value, total, context |
| C05 | Share split | kepemilikan / porsi | rows (period, %), parity line |
| **D · Charts** ||||
| D01 | Line chart | tren waktu | series, x labels, end value |
| D02 | Ranked bars | top-N | rows, highlight |
| D03 | Year delta | satu metrik berubah | A/B value + label, direction |
| D04 | Adoption curve | perilaku jadi norma | endpoints, event marker |
| D05 | Share ring | porsi dari keseluruhan | value, label, headline |
| **E · Systems** ||||
| E01 | Chain flow | uang/risiko pindah tangan | 3–6 nodes, active |
| E02 | Route map | perjalanan fisik | 2–6 stops, route |
| E03 | Timeline | kronologi berskala | range, events, active |
| E04 | Decision flow | percabangan hasil | tree (≤3 level) |
| E05 | To-scale compare | ukuran tak terbayang | A/B value, shape |
| **F · Explain** ||||
| F01 | Illustration card | `ILLUSTRATION CARD (square)` | illustration 1:1, caption |
| F02 | Versus | pilihan A vs B | A/B label, value, note, verdict |
| F03 | Numbered moves | urutan asli | headline, 3–7 items |
| F04 | Definition | jargon kunci | term, definition, aside |
| F05 | Object callout | menunjuk detail di foto | target x/y, value, label |
| **G · Voice & CTA** ||||
| G01 | Kinetic statement | tesis chapter | line 1/2/3, underline word |
| G02 | App CTA + QR | `[QR CODE]`, app CTA | QR (UTM per ep), headline, offer |
| G03 | Subscribe prompt | CTA subscribe | channel, line, button |
| G04 | End screen | outro | next title, slot layout |
| G05 | Format adaptation | Shorts / feed | 9:16 · 4:5 · 1:1 dari template induk |
| **H · Context** ||||
| H01 | Place & time stamp | lompat waktu/tempat | year, place, region, coords |
| H02 | Source & credit kit | semua grafik | 5 tipe label |
| H03 | Locator | tempat pertama disebut | pin, place, context |
| H04 | Price tag | benda + harga | item, price, delta |
| H05 | Viewer question | ajakan komentar | question, 2–3 options |

## Template Library v1.1 (blank) — 76 template, 11 jenis

Figma page **ALUX — Templates**, section `378:20` (*ALUX — Template Library v1.1 (blank)*), di kanan bank v1.0. Semua konten script dikosongkan: teks = lorem ipsum, angka = 0, foto = slot bergaris putus berlabel ukuran. Ini yang dipakai sebagai master AE; bank v1.0 (`359:20`) jadi contoh pemakaian dengan data asli.

ID baru = `<JENIS>-<nn>`. Kolom "v1.0" = asal clone; kosong = varian baru.

| Jenis | ID | Nama | v1.0 |
|---|---|---|---|
| **TTL · Title & structure** (7) | TTL-01 | Series opener | A01 |
| | TTL-02 | Chapter card · cyan | A02 |
| | TTL-03 | Sub-chapter on footage | A03 |
| | TTL-04 | Brand wipe | A05 |
| | TTL-05 | Chapter card · ink | |
| | TTL-06 | Split divider | |
| | TTL-07 | Cold open letterbox 2.39:1 | |
| **PRG · Progress & navigation** (5) | PRG-01 | Segmented bar · top | |
| | PRG-02 | Chapter rail · side | |
| | PRG-03 | Playhead · bottom | |
| | PRG-04 | Ring · corner | |
| | PRG-05 | Agenda list | |
| **PPL · People** (6) | PPL-01 | Lower third · standard | B01 |
| | PPL-02 | Lower third · minimal | |
| | PPL-03 | People row | |
| | PPL-04 | Attributed quote | |
| | PPL-05 | Bio card | B02 |
| | PPL-06 | Relationship pair | |
| **EVD · Evidence & media** (8) | EVD-01 | Archive plate | B03 |
| | EVD-02 | Headline clipping | B04 |
| | EVD-03 | Document excerpt | B05 |
| | EVD-04 | Object callout | F05 |
| | EVD-05 | Triptych | |
| | EVD-06 | Document page | |
| | EVD-07 | Post screenshot | |
| | EVD-08 | Before / after | |
| **NUM · Numbers** (8) | NUM-01 | Stat hero | C01 |
| | NUM-02 | Stat sequence 01/03 | C02 |
| | NUM-03 | Rate counter | C03 |
| | NUM-04 | Unit grid | C04 |
| | NUM-05 | Price tag | H04 |
| | NUM-06 | Share split · bars | C05 |
| | NUM-07 | Stat trio | |
| | NUM-08 | Number vs benchmark | |
| **CHT · Charts** (10) | CHT-01 | Line chart | D01 |
| | CHT-02 | Ranked bars · horizontal | D02 |
| | CHT-03 | Year delta | D03 |
| | CHT-04 | Area curve | D04 |
| | CHT-05 | Share ring | D05 |
| | CHT-06 | Column chart | |
| | CHT-07 | Stacked 100% | |
| | CHT-08 | Waterfall | |
| | CHT-09 | Two-line compare | |
| | CHT-10 | Gauge | |
| **DGM · Diagrams** (10) | DGM-01 | Chain flow | E01 |
| | DGM-02 | Route map | E02 |
| | DGM-03 | Timeline · horizontal | E03 |
| | DGM-04 | Decision tree | E04 |
| | DGM-05 | To-scale compare | E05 |
| | DGM-06 | Timeline · vertical | |
| | DGM-07 | Cycle loop | |
| | DGM-08 | Funnel | |
| | DGM-09 | Ownership tree | |
| | DGM-10 | Overlap | |
| **TXT · Text & explain** (10) | TXT-01 | Quick fact | A04 |
| | TXT-02 | Kinetic statement | G01 |
| | TXT-03 | Versus | F02 |
| | TXT-04 | Numbered list | F03 |
| | TXT-05 | Definition | F04 |
| | TXT-06 | Illustration card | F01 |
| | TXT-07 | Pull quote | |
| | TXT-08 | Myth vs reality | |
| | TXT-09 | Rules grid | |
| | TXT-10 | One word | |
| **CTX · Context labels** (4) | CTX-01 | Place & time stamp | H01 |
| | CTX-02 | Source & credit kit | H02 |
| | CTX-03 | Locator | H03 |
| | CTX-04 | Topic tag | |
| **CTA · Calls to action** (5) | CTA-01 | App + QR | G02 |
| | CTA-02 | Subscribe prompt | G03 |
| | CTA-03 | End screen | G04 |
| | CTA-04 | Viewer question | H05 |
| | CTA-05 | Sponsor break | |
| **SOC · Social formats** (3) | SOC-01 | Format adaptation 9:16 · 4:5 · 1:1 | G05 |
| | SOC-02 | Shorts kit 9:16 | |
| | SOC-03 | Carousel 4:5 | |

## Relasi dengan template v0 (20 komponen lama di section `340:1072`)

v0 tidak dihapus. Pemetaan: Chapter → A02 · Stat ×3 → C01 (tone) · Stamp → H01 · Quick fact → A04 · Still frame → B03 · Illustration card → F01 · Bio → B02 · Lower third → B01 · Chart Compare → D03 · CTA Subscribe → G03 · CTA App → G02 · End screen → G04 · Series opener → A01 · Share → D05 · Versus → F02 · Timeline → E03 · Rank → D02 · Company tag / Logo row → **belum ada di v1** (tidak dipakai di 2 script ini).

## Aturan

- Template tidak diubah per video. Kebutuhan baru = ID baru di sini.
- Semua angka di layar punya `field:source`. Data dummy di layout diberi label dummy di frame.
- Nama file AE: `ALUX_<id>_v<versi>.mogrt`. Satu Essential Graphics control layer dipakai bersama oleh comp 16:9 dan crop G05.
