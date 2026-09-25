"""timeline.json -> marking.md: the human review sheet (open in Obsidian)."""

from pathlib import Path
from typing import Any, Dict

KIND_ICON = {"FTG": "🎞️ FTG", "GFX": "✳️ GFX"}


def _mmss(sec: float) -> str:
    return f"{int(sec // 60):02d}:{int(sec % 60):02d}"


def write_review(tl: Dict[str, Any], path: Path) -> Path:
    st, al = tl["stats"], tl["alignment"]
    band = st["target_band"]
    lines = [
        "---",
        "type: episode_marking",
        f'title: "{tl["title"]}"',
        f"slots: {len(tl['slots'])}",
        f"gfx_share_client: {st['gfx_share_client']}",
        f"gfx_share_with_suggestions: {st['gfx_share_with_suggestions']}",
        "---",
        "",
        f"# Marking — {tl['title']}",
        "",
        f"- **Durasi VO**: {_mmss(st['duration_sec'])} · **{len(tl['slots'])} slot** (1 kalimat = 1 slot) · "
        f"{tl['resolution'][0]}×{tl['resolution'][1]} @ {tl['fps']} fps (motion @ {tl['motion_fps']})",
        f"- **Alignment**: {al['well_matched']}/{al['sentences']} kalimat cocok dengan VO · "
        f"coverage {al['token_coverage']:.0%}"
        + (f" · cek manual: {', '.join(al['low_confidence'])}" if al["low_confidence"] else ""),
        f"- **GFX dari klien**: {st['gfx_count_client']} grafik = **{st['gfx_share_client']:.0%}** durasi",
        f"- **+ saran otomatis**: {st['gfx_count_with_suggestions']} grafik = **{st['gfx_share_with_suggestions']:.0%}** durasi "
        f"(target {band[0]:.0%}–{band[1]:.0%})",
        "",
        "> [!note] Cara review",
        "> `approved` = arahan klien, tinggal dikerjakan. `suggested` = usulan otomatis (angka tanpa grafik, kartu chapter) — "
        "ubah jadi approved atau hapus di `timeline.json`.",
        "",
        "## Daftar grafik",
        "",
        "| ID | TC in | Durasi | Template | Asal | Status | Isi |",
        "|---|---|---:|---|---|---|---|",
    ]
    for g in tl["graphics"]:
        label = str(g["label"]).replace("|", "/")[:110]
        extra = f" · `{g['file']}`" if g.get("file") else ""
        lines.append(f"| {g['id']} | `{g['tc_in']}` | {g['duration']}s | `{g['template']}` | {g['origin']} | "
                     f"{g['status']} | {label}{extra} |")

    gfx_by_id = {g["id"]: g for g in tl["graphics"]}
    for ch in tl["chapters"]:
        lines += ["", f"## {ch['title']}  `{_mmss(ch['start'])}`", "",
                  "| Slot | TC in | Dur | Jenis | Narasi |", "|---|---|---:|---|---|"]
        for s in (x for x in tl["slots"] if x["section"] == ch["id"]):
            kind = KIND_ICON[s["kind"]]
            if s["gfx"]:
                g = gfx_by_id[s["gfx"]]
                kind += f" `{g['template']}`" + (" *(saran)*" if g["status"] == "suggested" else "")
            warn = " ⚠️" if s["match"] < 0.5 else ""
            text = s["text"].replace("|", "/")
            lines.append(f"| {s['id']} | `{s['tc_in']}` | {s['end'] - s['start']:.1f}s | {kind} | {text}{warn} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
