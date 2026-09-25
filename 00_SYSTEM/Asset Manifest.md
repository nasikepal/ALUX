---
type: system_manifest
title: "ALUX Asset Manifest"
status: draft-v0
updated: 2026-09-25
owner: Rijal
tags:
  - system
  - assets
  - graphics
---

# ALUX Asset Manifest (draft v0)

Daftar semua aset standar yang harus ada sebelum produksi bisa diotomasi. **ID di kolom pertama = tag `GFX:<id>` di marking script** ([[ALUX Workflow]]).

Urutan kerja: **Lapis 0 dulu, baru template.** Bikin template sebelum brand dikunci = kerja dua kali.

## Lapis 0 — Fondasi brand (Rijal siapkan duluan)

- [ ] **Brand scrape ALUX** — ambil 5–10 video ALUX terbaru, screenshot semua grafiknya, catat pola: font, warna, cara angka muncul, durasi grafik di layar, transisi
- [ ] **Logo & lockup** — versi terang/gelap, clear space, ukuran minimum di 4K
- [ ] **Warna** — token HEX + aturan pemakaian (bg, aksen, teks, positif/negatif untuk grafik)
- [ ] **Tipografi** — font display + body, lisensi font untuk semua anggota tim, type scale di 3840×2160
- [ ] **Grid & safe area** — margin, title-safe, posisi baku lower third & source label
- [ ] **Motion language** — kurva easing baku, durasi in/out, stagger, aturan "tipis" (maks. berapa elemen gerak sekaligus)
- [ ] **Tekstur & finishing** — grain, vignette, shadow (kalau ada)
- [ ] **Sound signature** — whoosh/hit/tick standar untuk grafik muncul
- [ ] **Spec teknis** — resolusi, fps, color space, codec export MOGRT

## Lapis 1a — Tipe yang dipakai klien di script (prioritas)

Diambil dari script episode 001 (*How Insurance Actually Works*, 53 menit): klien sudah menandai grafik sendiri. Tipe ini yang pertama dibuat templatenya karena **pasti muncul di tiap episode**.

| ID | Penanda di script klien | Muncul di ep. 001 | Data yang diisi | Format | Status |
|---|---|---:|---|---|---|
| `still` | `ON-SCREEN GRAPHIC: file.jpg \| caption` | 15 | file gambar + caption | MOGRT (frame + caption) | ☐ |
| `chart` | `ON-SCREEN GRAPHIC: <data>, source: ...` | 8 | angka + label + sumber | MOGRT per bentuk chart | ☐ |
| `illustration` | `ILLUSTRATION CARD (square)` + caption | 10 | ilustrasi persegi + caption | FIGMA → MOGRT | ☐ |
| `quickfact` | `QUICK FACT: <pertanyaan>` | 5 | judul pertanyaan | MOGRT | ☐ |
| `cta` | `ON-SCREEN CTA: ...` | 4 | subscribe / app / end card | MOGRT | ☐ |
| `timeline` | `TIMELINE CARD (wide)` + caption | 1 | tahun + peristiwa | FIGMA → MOGRT | ☐ |
| `explainer` | `ON-SCREEN GRAPHIC:` berupa brief animasi | 1 | bespoke | animasi manual | — |
| `chapter` | `Heading 1` di docx (yang berawalan CHAPTER) | 16 | nomor + judul chapter | MOGRT | ☐ |
| `stat` | *(saran otomatis)* angka diucapkan tanpa grafik | 10 | angka + label | MOGRT | ☐ |

> [!question] Belum jelas
> File `.jpg` di `ON-SCREEN GRAPHIC` (mis. `10-nineteen-in-100-denied.jpg`) — dikirim klien jadi, atau kita yang bikin dari nama file itu?

## Lapis 1b — Template tambahan (setelah 1a beres)

Kolom **Format**: `MOGRT` = dibuat di AE, diisi otomatis di Premiere oleh Claude Bridge (tipe berulang). `FIGMA` = dirakit lewat Figma MCP dari komponen standar (tipe bespoke/kompleks).

| ID | Nama | Dipakai saat narasi... | Data yang diisi | Format | Status |
|---|---|---|---|---|---|
| `title` | Title sequence / opener | awal video | judul episode | MOGRT | ☐ |
| `chapter` | Chapter / nomor item | pindah bagian atau nomor listicle | nomor, judul | MOGRT | ☐ |
| `lower` | Lower third / name tag | tokoh pertama kali muncul | nama, jabatan | MOGRT | ☐ |
| `bio` | Bio card tokoh | biografi singkat | foto, nama, lahir, peran, 2–3 fakta | FIGMA → MOGRT | ☐ |
| `stat` | Angka besar | menyebut satu angka kunci | nilai, satuan, label | MOGRT | ☐ |
| `percent` | Persentase (ring/bar) | menyebut persen | nilai %, label | MOGRT | ☐ |
| `bar` | Bar chart | membandingkan beberapa nilai | 2–6 pasang label=nilai | MOGRT | ☐ |
| `line` | Line chart / growth | tren dari waktu ke waktu | deret tahun=nilai | MOGRT | ☐ |
| `versus` | Perbandingan A vs B | membandingkan dua hal | 2 label, 2 nilai/gambar | FIGMA → MOGRT | ☐ |
| `rank` | Ranking / daftar | urutan atau top-N | item berurutan | MOGRT | ☐ |
| `timeline` | Timeline | kronologi | tahun + peristiwa | FIGMA → MOGRT | ☐ |
| `map` | Peta / lokasi | menyebut tempat | lokasi, label | FIGMA | ☐ |
| `quote` | Kutipan | mengutip seseorang | teks, nama | MOGRT | ☐ |
| `price` | Price tag | menyebut harga barang | nama barang, harga | MOGRT | ☐ |
| `kinetic` | Teks kunci di atas footage | kata yang perlu ditekankan | 1–4 kata | MOGRT | ☐ |
| `source` | Label sumber | setiap angka/klaim di layar | nama sumber, tahun | MOGRT | ☐ |
| `endcard` | End screen | penutup | — | MOGRT | ☐ |
| `wipe` | Transisi brand | pindah chapter | — | MOGRT | ☐ |

## Lapis 2 — Library pendukung

- [ ] Paket SFX grafik (terikat ke sound signature)
- [ ] Library musik berlisensi + tagging mood
- [ ] Folder footage dengan penamaan per shot ID (`SH-001_...`) supaya assembly bisa menaruh klip otomatis
- [ ] Komponen Figma: satu file library, tiap template = satu komponen dengan variant, teks sebagai properti (supaya MCP cukup mengisi data, tidak menggambar)

## Aturan standar

- Template tidak boleh diubah per video. Kebutuhan baru = tambah ID baru di manifest, bukan modifikasi lokal.
- Semua angka di layar wajib ada `source` yang sudah terverifikasi.
- Nama file: `ALUX_<id>_v<versi>.mogrt`.
