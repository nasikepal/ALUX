"""
graphics_map.json + VO word timestamps -> graphics_cues.json / .csv: the final, frame-accurate schedule
the editor drops graphics onto.

Rules
- Each graphic enters on the spoken word it illustrates (a number, a name, a place), not on the start of
  its sentence: the in-point is that word's start minus a short lead. Graphics with nothing specific to
  key on (caption cards, chapters) enter on their sentence / section start.
- Out-points follow the narration span the graphic covers, clamped to per-type min/max durations.
- Two tracks: FULL (full-frame graphics, V3) and OVERLAY (over footage, V4). Nothing on the same track
  overlaps; overlays never sit on top of a full-frame graphic. Every adjustment is reported.
- Verification: each cue carries the words actually spoken at its in-point, so a human can confirm it
  without scrubbing the audio.
"""

import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .timeline import FPS, tc, _numbers, _keywords

LEAD = 0.25            # enter slightly before the key word lands
GAP = 1 / FPS          # one frame between cues on the same track
FULL = {"still", "chart", "illustration", "quickfact", "timeline", "rank", "logos", "explainer", "chapter",
        "opener", "cta_end", "share", "versus"}
OVERLAY = {"stat", "stamp", "bio", "lower", "company", "cta"}
# (min, max) seconds on screen
DUR = {"chapter": (3.0, 5.0), "stamp": (3.0, 3.0), "opener": (5.0, 5.0), "quickfact": (4.0, 6.0),
       "bio": (5.0, 6.0), "lower": (4.0, 5.0), "company": (4.5, 5.0), "cta": (6.0, 7.0), "stat": (3.5, 8.0),
       "still": (4.0, 14.0), "chart": (7.0, 12.0), "illustration": (4.0, 10.0), "timeline": (6.0, 10.0),
       "rank": (5.0, 9.0), "logos": (5.0, 8.0), "explainer": (8.0, 60.0), "cta_end": (10.0, 45.0)}


def load_words(path: Path) -> List[Dict[str, Any]]:
    """whisper-cli JSON (-oj or -ojf, with or without DTW) -> [{text, start, end}] in seconds."""
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for seg in data.get("transcription", []):
        txt = seg.get("text", "").strip()
        if not txt:
            continue
        o = seg.get("offsets", {})
        start, end = o.get("from", 0) / 1000.0, o.get("to", 0) / 1000.0
        toks = seg.get("tokens") or []
        dtw = [t.get("t_dtw") for t in toks if t.get("t_dtw", -1) not in (-1, None) and not t.get("text", "").startswith("[")]
        if dtw:
            start = min(dtw) / 100.0  # t_dtw is in centiseconds
        out.append({"text": txt, "start": start, "end": max(end, start)})
    return out


def _norm(word: str) -> str:
    return re.sub(r"[^\w.]", "", word.lower()).strip(".")


def _kind(item: Dict[str, Any], fill: Dict[str, Any]) -> str:
    t = item["type"]
    tpl = (fill.get(item["map_id"]) or {}).get("template", "")
    if t == "cta":
        return "cta_end" if tpl == "endscreen" else "cta"
    if t == "chart":
        return {"share": "share", "versus": "versus"}.get(tpl, "chart")
    return t


def _keys(item: Dict[str, Any], fill_entry: Dict[str, Any]) -> Tuple[set, set]:
    """(numbers, words) that identify the moment this graphic is about."""
    t = item["type"]
    text = " ".join(str(x) for x in (item.get("content"), item.get("data")) if x)
    props = " ".join(str(v) for v in (fill_entry or {}).get("props", {}).values())
    if t in ("bio", "lower", "company"):
        name = item["content"].replace("Corp. of America", "")
        return set(), {w.lower() for w in re.findall(r"[A-Za-z]{3,}", name)} - {"the"}
    if t == "stamp":
        return _numbers(text), {w.lower() for w in re.findall(r"[A-Za-z]{4,}", item["content"])}
    if t == "rank":
        return set(), {"allianz"}
    if t == "logos":
        return set(), {"apollo"}
    if t == "opener":
        return set(), {"millionaire"}
    if t == "cta":
        tpl = (fill_entry or {}).get("template", "")
        return set(), {"subscribe"} if tpl == "cta_subscribe" else ({"app"} if tpl == "cta_app" else set())
    if t in ("chapter", "illustration", "quickfact", "explainer", "timeline"):
        return set(), set()
    return _numbers(text + " " + props), set()


def _find_phrase(words, phrase: str, near: float, radius: float = 90.0) -> Optional[Dict[str, Any]]:
    """First word of `phrase` (as transcribed), nearest to `near` within `radius` seconds."""
    p = [_norm(x) for x in phrase.split()]
    best = None
    for i in range(len(words) - len(p) + 1):
        if abs(words[i]["start"] - near) > radius:
            continue
        if all(_norm(words[i + k]["text"]) == p[k] for k in range(len(p))):
            if best is None or abs(words[i]["start"] - near) < abs(best["start"] - near):
                best = words[i]
    return best


def _find_key(words, t0, t1, nums: set, kws: set) -> Optional[Dict[str, Any]]:
    nums = nums | {n.split(".")[0] for n in nums}  # "94.1%" on screen is read as "94%"
    for w in words:
        if w["start"] < t0:
            continue
        if w["start"] > t1:
            break
        n = _norm(w["text"])
        if kws and (n in kws or n.rstrip("s") in kws):
            return w
        if nums and (_numbers(w["text"]) & nums):
            return w
    return None


def spoken(words, t0, seconds=2.5, limit=10) -> str:
    return " ".join(w["text"] for w in words if t0 - 0.05 <= w["start"] < t0 + seconds)[:120].strip()


def build_cues(tl: Dict[str, Any], gmap: List[Dict[str, Any]], fill: Dict[str, Any],
               words: List[Dict[str, Any]], assets: Dict[str, str],
               phrases: Optional[Dict[str, str]] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
    drop = dict((phrases or {}).get("_drop", {}))
    phrases = {k: v for k, v in (phrases or {}).items() if not k.startswith("_")}
    slots = tl["slots"]
    sent_by_slot = {s["id"]: i for i, s in enumerate(slots)}
    gfx_by_id = {g["id"]: g for g in tl["graphics"]}
    chapters = {c["title"]: c for c in tl["chapters"]}
    vo_end = tl["vo"]["duration"]
    log: List[str] = []
    cues = []

    for it in gmap:
        if it["map_id"] in drop:
            log.append(f"{it['map_id']}: dropped — {drop[it['map_id']]}")
            continue
        kind = _kind(it, fill)
        entry = fill.get(it["map_id"]) or {}
        # narration span this graphic belongs to
        if it.get("slot"):
            idx = [sent_by_slot[it["slot"]]]
        elif it.get("id") in gfx_by_id and gfx_by_id[it["id"]]["sentence_idx"]:
            idx = gfx_by_id[it["id"]]["sentence_idx"]
        else:
            idx = []
        if kind == "chapter":
            title = it["content"]
            first = next(i for i, s in enumerate(slots) if s["start"] >= chapters[title]["start"] - 0.01)
            prev_end = slots[first - 1]["end"] if first else 0.0
            f0 = slots[first]["start"]
            spoken_ch = [w for w in words if f0 - 12 <= w["start"] < f0 + 0.3 and _norm(w["text"]) == "chapter"]
            if spoken_ch:  # narrator reads the title: card enters on "Chapter", holds until the title is read
                key = spoken_ch[-1]
                t_in = key["start"] - 0.15
                span_end = f0 + 0.4
            else:          # title not read: card sits in the pause before the chapter's first line
                key = None
                t_in = max(prev_end + 0.1, f0 - 0.5)
                span_end = t_in + 3.0
        else:
            if not idx:  # fall back to the nearest sentence
                idx = [min(range(len(slots)), key=lambda i: abs(slots[i]["start"] - it["start"]))]
            s0, s1 = slots[idx[0]], slots[idx[-1]]
            nums, kws = _keys(it, entry)
            if it["map_id"] in phrases:
                key = _find_phrase(words, phrases[it["map_id"]], s0["start"])
                if key is None:
                    log.append(f"{it['map_id']}: phrase \"{phrases[it['map_id']]}\" not found in the VO — kept sentence start")
                    t_in, span_end = s0["start"], s1["end"]
                else:
                    t_in = key["start"] - LEAD
                    # narration span: from the phrase to the end of the sentence it sits in (or the anchor span)
                    k_sent = next((sl for sl in slots if sl["start"] - 0.3 <= key["start"] <= sl["end"] + 0.3), s1)
                    # the client cue marks where the idea ends: hold through it when the phrase comes first
                    span_end = max(k_sent["end"], s1["end"] if s1["end"] > key["start"] else 0)
            else:
                key = _find_key(words, s0["start"] - 0.3, s1["end"] + 0.2, nums, kws) if (nums or kws) else None
                t_in = (key["start"] - LEAD) if key else s0["start"]
                t_in = max(t_in, s0["start"] - 0.3)
                span_end = s1["end"]
            if kind == "explainer":
                # the whole explanation, until its section ends (the next full-frame graphic trims it further)
                para = slots[idx[0]].get("section")
                j = idx[-1]
                while j + 1 < len(slots) and slots[j + 1]["section"] == para and slots[j + 1]["start"] - t_in < DUR["explainer"][1]:
                    j += 1
                span_end = slots[j]["end"]
            if kind == "cta_end":
                span_end = vo_end
        t_in = max(0.0, t_in)
        lo, hi = DUR.get(kind, (4.0, 10.0))
        t_out = min(max(span_end, t_in + lo), t_in + hi, vo_end)
        cues.append({
            "id": it["map_id"], "type": it["type"], "kind": kind, "template": entry.get("template", ""),
            "track": "FULL" if kind in FULL else "OVERLAY", "status": "HOLD" if entry.get("hold") else "ready",
            "origin": it["origin"], "content": it["content"], "asset": assets.get(it["map_id"], ""),
            "source": entry.get("source") or it.get("source") or "",
            "in": t_in, "out": t_out, "key": key["text"] if key else "", "key_at": key["start"] if key else None,
        })

    cues.sort(key=lambda c: c["in"])
    ends = [c for c in cues if c["kind"] == "cta_end"]
    for extra in ends[1:]:
        log.append(f"{extra['id']}: merged into {ends[0]['id']} (same end screen)")
        ends[0]["content"] += " + " + extra["content"]
        cues.remove(extra)
    _resolve(cues, log)
    for c in cues:
        f_in, f_out = round(c["in"] * FPS), round(c["out"] * FPS)
        c.update(frame_in=f_in, frame_out=f_out, frames=f_out - f_in, tc_in=tc(f_in / FPS), tc_out=tc(f_out / FPS),
                 duration=round((f_out - f_in) / FPS, 3),
                 spoken=spoken(words, c["key_at"] if c["key_at"] is not None and c["key_at"] >= c["in"] else c["in"]))
    return cues, log


def _resolve(cues: List[Dict[str, Any]], log: List[str]) -> None:
    """No overlaps within a track; overlays wait for full-frame graphics to leave. Chapter cards win."""
    for ch in (c for c in cues if c["kind"] == "chapter"):
        for c in cues:
            if c is ch or c["track"] != "FULL" or c["kind"] == "chapter":
                continue
            if c["in"] < ch["out"] and ch["in"] < c["out"]:
                dur = c["out"] - c["in"]
                log.append(f"{c['id']}: in moved to after chapter card {ch['id']}")
                c["in"] = ch["out"] + GAP
                c["out"] = c["in"] + max(dur, DUR.get(c["kind"], (3, 0))[0])
    cues.sort(key=lambda c: c["in"])
    for track in ("FULL", "OVERLAY"):
        prev = None
        for c in (x for x in cues if x["track"] == track):
            if prev and c["in"] < prev["out"] + GAP:
                lo_prev = DUR.get(prev["kind"], (3.0, 0))[0]
                if c["in"] - GAP - prev["in"] >= min(lo_prev, 2.5):
                    log.append(f"{prev['id']}: out trimmed {prev['out'] - (c['in'] - GAP):.2f}s so {c['id']} can enter on its word")
                    prev["out"] = c["in"] - GAP
                else:
                    shift = prev["out"] + GAP - c["in"]
                    log.append(f"{c['id']}: in shifted +{shift:.2f}s after {prev['id']} ({prev['kind']})")
                    dur = c["out"] - c["in"]
                    c["in"] = prev["out"] + GAP
                    c["out"] = max(c["out"], c["in"] + min(dur, DUR.get(c["kind"], (3, 0))[0]))
            prev = c
    full = [c for c in cues if c["track"] == "FULL"]
    for o in (c for c in cues if c["track"] == "OVERLAY"):
        for f in full:
            if o["in"] < f["out"] and f["in"] < o["out"]:
                shift = f["out"] + GAP - o["in"]
                log.append(f"{o['id']}: overlay moved +{shift:.2f}s to clear full-frame {f['id']}")
                dur = o["out"] - o["in"]
                o["in"] = f["out"] + GAP
                o["out"] = o["in"] + dur
    cues.sort(key=lambda c: c["in"])


def write_outputs(cues: List[Dict[str, Any]], log: List[str], build: Path) -> Tuple[Path, Path]:
    j = build / "graphics_cues.json"
    j.write_text(json.dumps({"fps": FPS, "cues": cues, "adjustments": log}, indent=2, ensure_ascii=False), encoding="utf-8")
    c = build / "graphics_cues.csv"
    cols = ["id", "track", "kind", "template", "status", "tc_in", "tc_out", "duration", "frames", "asset", "content",
            "key", "spoken", "source"]
    with open(c, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(cues)
    md = build / "graphics_cue_sheet.md"
    lines = ["---", "type: episode_cue_sheet", f"cues: {len(cues)}", f"fps: {FPS}", "---", "",
             f"# Graphics cue sheet ({FPS} fps)", "",
             "Timecodes are locked to the spoken word in the VO. The Premiere markers carry the same ID, in, out and "
             "duration: drop each asset on its marker.", "",
             "- **V3** = full-frame graphic · **V4** = over footage", "- *Masuk pada* = the VO words at the in-point", "",
             "| ID | Track | Jenis | TC in | TC out | Durasi | Aset | Masuk pada |", "|---|---|---|---|---|---:|---|---|"]
    for x in cues:
        asset = x["asset"].replace("assets/graphics/", "") if x["asset"] else "—"
        hold = " ⚠️ HOLD" if x["status"] == "HOLD" else ""
        lines.append(f"| {x['id']}{hold} | {'V3' if x['track'] == 'FULL' else 'V4'} | {x['kind']} | `{x['tc_in']}` | "
                     f"`{x['tc_out']}` | {x['duration']:.2f}s ({x['frames']}f) | {asset} | {x['spoken'][:48].replace('|', '/')} |")
    lines += ["", "## Adjustments", ""] + [f"- {a}" for a in log]
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return j, c
