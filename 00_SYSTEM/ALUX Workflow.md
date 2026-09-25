---
type: system_workflow
title: "ALUX Workflow — Script ke Timeline"
status: draft-v0
updated: 2026-09-25
owner: Rijal
tags:
  - system
  - workflow
---

# ALUX Workflow — Script ke Timeline (draft v0)

Format baru: **footage (B-roll + A-roll) sebagai badan video, motion graphic tipis sebagai penjelas.** Bukan animasi penuh lagi.

Input dari klien: **script mentah + file voice over.** Output: timeline Premiere siap revisi.

```
 SCRIPT + VO (klien)
      │
 [1] MARKING ─────────── script ditandai per beat: FTG / AROLL / GFX:<tipe>
      │                   (Claude bikin draft, manusia approve)
      ▼
 [2] TIMING ──────────── whisper lokal → timestamp per kata → dicocokkan ke beat
      │                   hasil: timeline.json (sumber kebenaran timing)
      ├──────────────┐
      ▼              ▼
 [3a] FOOTAGE     [3b] GRAPHIC
  sourcing per     tiap GFX beat → template dari Asset Manifest
  shot ID          (MOGRT untuk tipe standar, Figma untuk yang bespoke)
      │              │
      └──────┬───────┘
             ▼
 [4] ASSEMBLY ────────── Claude Bridge → Premiere: pasang VO, chapter marker,
                          footage per slot, MOGRT, SFX, musik
             ▼
 [5] REVISI ──────────── revisi masuk sebagai edit timeline.json → assembly ulang bagian itu
```

## Prinsip

1. **`timeline.json` adalah sumber kebenaran, bukan project Premiere.** Semua tahap membaca/menulis ke situ. Premiere cuma *eksekutor*. Alasannya: data bisa diperiksa, di-diff, dipakai ulang oleh Figma/AE, dan tidak tergantung Premiere sedang terbuka.
2. **Timestamp diambil dari whisper, bukan transcript Premiere.** Whisper lokal (`whisper-cli` + `large-v3-turbo`) sudah terpasang, keluar timestamp per kata, VO 10 menit selesai dalam hitungan detik–menit. Karena teks script sudah diketahui, tugasnya tinggal *mencocokkan*, bukan menebak — akurat. Catatan: whisper menulis angka sebagai digit ("eleven" → `11`), jadi pencocokan wajib menormalisasi angka.
3. **Rasio motion : footage adalah hasil, bukan target.** Target kasar 30–40% GFX. Kalau marking keluar di luar 25–45%, itu sinyal untuk dicek, bukan dipaksa.
4. **Claude mengusulkan, manusia mengunci.** Marking, pilihan footage, dan sumber klaim selalu lewat approval orang sebelum masuk timeline.

## [1] Marking — format (draft, dikunci setelah Asset Manifest final)

Satu beat per baris. Tag di depan. Data untuk grafik di belakang `||`.

```markdown
[FTG] Warren Buffett bought his first stock at age eleven.
[AROLL] ...
[GFX:bio] Born in Omaha in 1930, he started as a paperboy. || name=Warren Buffett; born=1930; role=CEO, Berkshire Hathaway
[GFX:stat] Today, his company is worth nine hundred billion dollars. || value=$900B; label=Berkshire Hathaway market cap; source=CLAIM-003
[FTG] But he still lives in the same house he bought in 1958.
```

| Tag | Arti |
|---|---|
| `FTG` | B-roll footage sesuai narasi |
| `AROLL` | A-roll (definisi untuk ALUX: **belum dikunci**) |
| `GFX:<tipe>` | Motion graphic; `<tipe>` = ID template di [[Asset Manifest]] |
| `CH` | Pergantian chapter / nomor item (listicle) |

Setiap angka/klaim di beat GFX wajib punya `source=` yang menunjuk ke klaim yang sudah diverifikasi di Research Inbox.

## [2] Timing

- Input: file VO dari klien + script yang sudah di-mark.
- `whisper-cli -m ~/.cache/whisper/ggml-large-v3-turbo.bin -f vo.wav -ml 1 -sow -oj` → timestamp per kata.
- Pencocokan beat ↔ kata → `timeline.json` berisi `in`/`out` tiap beat.

## [4] Assembly — Claude Bridge

Panel CEP `com.feugee.claudebridge` di Premiere menjalankan ExtendScript yang dikirim lewat folder `~/Library/Application Support/ClaudeBridge/inbox` (`ppro.sh`). Sudah jalan, perlu dirapikan jadi perintah tetap (pasang VO, marker chapter, taruh klip per slot, taruh MOGRT + isi teks, SFX, musik) — bukan eval bebas.

## Status implementasi (2026-09-25) — sudah jalan di episode 001

```bash
# 1. docx + VO -> script.json, words.json, timeline.json, marking.md
.venv/bin/python 08_AUTOMATION/Scripts/episode_cli.py build /Users/royale/Documents/ALUX/001
# 2. Premiere harus terbuka dengan project + panel Claude Bridge aktif
.venv/bin/python 08_AUTOMATION/Scripts/episode_cli.py premiere /Users/royale/Documents/ALUX/001
```

Episode folder: `material/` (docx + VO dari klien) · `build/` (hasil generate) · `project/` (Premiere) · `assets/`.

| Tahap | Hasil di ep. 001 |
|---|---|
| Ingest docx | 18 section · 494 kalimat · 44 cue klien · 46 baris sumber di back matter |
| Transkripsi | 53 menit VO ≈ 5 menit (`whisper-cli` large-v3-turbo) |
| Alignment | 491/494 kalimat cocok (96% token) |
| Timeline | 494 slot · 44 GFX klien = **12% durasi** · + 26 saran = 16% |
| Premiere | sequence 3840×2160 @ 24 fps · VO WAV di A1 · 89 marker (chapter merah, GFX klien oranye, saran kuning) |

Temuan yang mengubah desain:
- **Docx klien sudah terstruktur**: `Heading 1` = chapter, *italic* = arahan (tidak dibaca VO), normal = narasi. Sesudah heading `END` = daftar sumber.
- **Arahan grafik klien tidak konsisten posisinya**: chart data ditaruh *sebelum* paragrafnya, gambar & kartu *sesudah*. Makanya grafik dijangkarkan ke kalimat yang angka/kata kuncinya paling cocok, bukan ke posisinya di docx.
- **VO MP3 selalu didecode jadi WAV master** (`build/vo_master_48k.wav`) — durasi dari header MP3 meleset ~3 detik dibanding hasil decode.
- **Rasio grafik dari klien cuma ~12%**, jauh di bawah target 30–40%. Sisanya harus keputusan kreatif kita.

## Pertanyaan terbuka

- [x] A-roll: tidak ada, full B-roll.
- [x] Footage: Envato Elements, **download manual** (ToS melarang scraping) ke library lokal, lalu metadata dibangun otomatis.
- [x] Spec: 4K, 24 fps footage, motion 12 fps, durasi ±1 jam.
- [x] VO: satu file utuh per script.
- [ ] Tim pakai Claude Code atau Antigravity? (satu saja — skill & MCP config beda format)
