"""
script.json + aligned sentences -> timeline.json (the single source of truth for an episode).

Every sentence is a slot on the timeline. A slot is FTG (B-roll footage) unless a graphic covers it.
Graphics come from two places:
  origin=client : the client's own directions in the script (ON-SCREEN GRAPHIC, cards, quick facts, CTAs)
  origin=auto   : suggestions from rules (chapter cards, numbers spoken without a client graphic)
Auto suggestions are proposals for a human to accept or drop, never locked in silently.
"""

import re
from typing import Any, Dict, List, Optional

FPS = 24               # footage / sequence frame rate
MOTION_FPS = 12        # motion graphics animate on twos inside the 24 fps sequence
MIN_GFX_SEC = 4.0      # a graphic shorter than this can't be read
MAX_GFX_SEC = 12.0     # longer than this and a static graphic starts to drag
CHAPTER_CARD_SEC = 3.0

# client cue type -> Asset Manifest template id
CUE_TEMPLATE = {
    ("graphic", "still"): "still",
    ("graphic", "data"): "chart",
    ("graphic", "brief"): "explainer",
    ("illustration", None): "illustration",
    ("timeline", None): "timeline",
    ("quickfact", None): "quickfact",
    ("cta", None): "cta",
}
# Cues that introduce what comes next rather than illustrate what was just said.
FORWARD_CUES = {"quickfact"}

# A sentence worth a stat card: money, a percentage, or a big quantity — not "a hundred years".
_STAT = re.compile(
    r"(\$\s?\d|\d[\d.,]*\s?(?:%|percent|million|billion|trillion)|"
    r"\b(?:million|billion|trillion)\b|\bpercent\b|\bout of (?:every )?(?:a )?hundred\b)", re.I)

_UNITS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen".split())}
_TENS = {w: 10 * (i + 2) for i, w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())}
_STOP = set("""the and that this with from have been were they their them than then what when where which
while into over just about only also even more most much very your you our its it's his her who whom
would could should there here those these because every other some said says like make made""".split())


def _numbers(text: str) -> set:
    """Numbers mentioned in text, whether written as digits or words ("thirty-seven" -> 37)."""
    t = text.lower()
    found = set()
    for m in re.findall(r"\d+(?:\.\d+)?", t.replace(",", "")):
        found.add(m.rstrip("0").rstrip(".") if "." in m else m)
    for m in re.finditer(r"\b(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[- ](one|two|three|four|five|six|seven|eight|nine))?\b", t):
        found.add(str(_TENS[m.group(1)] + (_UNITS[m.group(2)] if m.group(2) else 0)))
    for w, n in _UNITS.items():
        if n >= 2 and re.search(rf"\b{w}\b", t):
            found.add(str(n))
    return found


def _keywords(text: str) -> set:
    return {w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in _STOP}


def _affinity(cue_text: str, sentence: str) -> float:
    return 2.0 * len(_numbers(cue_text) & _numbers(sentence)) + len(_keywords(cue_text) & _keywords(sentence))


def frames(sec: float) -> int:
    return int(round(sec * FPS))


def tc(sec: float) -> str:
    f = frames(sec)
    h, rem = divmod(f, FPS * 3600)
    m, rem = divmod(rem, FPS * 60)
    s, fr = divmod(rem, FPS)
    return f"{h:02d}:{m:02d}:{s:02d}:{fr:02d}"


def _span_back(sents: List[Dict[str, Any]], last_idx: int) -> List[int]:
    """Grow a graphic span backwards from a sentence until it is readable, without crossing a paragraph."""
    idx = [last_idx]
    para = sents[last_idx]["para"]
    while True:
        dur = sents[idx[-1]]["slot_end"] - sents[idx[0]]["start"]
        prev = idx[0] - 1
        if dur >= MIN_GFX_SEC or prev < 0 or sents[prev]["para"] != para:
            break
        if sents[idx[-1]]["slot_end"] - sents[prev]["start"] > MAX_GFX_SEC:
            break
        idx.insert(0, prev)
    return idx


def _span_forward(sents: List[Dict[str, Any]], first_idx: int) -> List[int]:
    idx = [first_idx]
    para = sents[first_idx]["para"]
    while True:
        dur = sents[idx[-1]]["slot_end"] - sents[idx[0]]["start"]
        nxt = idx[-1] + 1
        if dur >= MIN_GFX_SEC or nxt >= len(sents) or sents[nxt]["para"] != para:
            break
        if sents[nxt]["slot_end"] - sents[idx[0]]["start"] > MAX_GFX_SEC:
            break
        idx.append(nxt)
    return idx


def build_timeline(script: Dict[str, Any], sentences: List[Dict[str, Any]], vo: Dict[str, Any],
                   align_report: Dict[str, Any]) -> Dict[str, Any]:
    duration = vo["duration"]
    sid_to_idx = {s["id"]: i for i, s in enumerate(sentences)}
    for s in sentences:  # whisper can overshoot the file end by a few hundred ms
        s["end"] = min(s["end"], duration)
        s["slot_end"] = min(s.get("slot_end", s["end"]), duration)

    graphics: List[Dict[str, Any]] = []

    # 1. Client directions, anchored to the narration they talk about
    covered: set = set()
    for pos, block in enumerate(script["blocks"]):
        if block["kind"] != "cue" or block["cue"]["type"] == "note":
            continue
        span = _anchor(block, pos, script["blocks"], sentences, sid_to_idx, covered)
        if span:
            graphics.append(_graphic_from_cue(block, sentences, span))
            covered.update(span)

    # 2. Auto suggestions: key numbers spoken in a paragraph the client gave no graphic.
    #    Adjacent stat sentences in one paragraph share one card.
    client_paras = {sentences[i]["para"] for i in covered}
    i = 0
    while i < len(sentences):
        s = sentences[i]
        if i in covered or s["para"] in client_paras or not _STAT.search(s["text"]):
            i += 1
            continue
        span = [i]
        while (i + 1 < len(sentences) and i + 1 not in covered and sentences[i + 1]["para"] == s["para"]
               and _STAT.search(sentences[i + 1]["text"])
               and sentences[i + 1]["slot_end"] - s["start"] <= MAX_GFX_SEC):
            i += 1
            span.append(i)
        graphics.append({
            "id": None, "origin": "auto", "status": "suggested", "template": "stat",
            "label": " ".join(sentences[k]["text"] for k in span), "cue_ref": None, "sentence_idx": span,
            "start": s["start"], "end": min(sentences[span[-1]]["slot_end"], s["start"] + MAX_GFX_SEC),
        })
        covered.update(span)
        i += 1

    # 3. Chapters: marker for every section, suggested title card for numbered chapters
    chapters = []
    for sec in script["sections"]:
        first = next((s for s in sentences if s["section"] == sec["id"]), None)
        if first is None:
            continue
        chapters.append({"id": sec["id"], "title": sec["title"], "start": first["start"]})
        if re.match(r"^CHAPTER\b", sec["title"], re.I):
            graphics.append({
                "id": None, "origin": "auto", "status": "suggested", "template": "chapter",
                "label": sec["title"], "cue_ref": None, "sentence_idx": [],
                "start": first["start"], "end": first["start"] + CHAPTER_CARD_SEC,
            })

    graphics.sort(key=lambda g: g["start"])
    for n, g in enumerate(graphics, 1):
        g["id"] = f"GFX-{n:03d}"
        g["tc_in"], g["tc_out"] = tc(g["start"]), tc(g["end"])
        g["duration"] = round(g["end"] - g["start"], 2)

    # 4. Slots: one per sentence, FTG unless covered by a graphic
    gfx_by_sentence: Dict[int, str] = {}
    for g in graphics:
        for i in g["sentence_idx"]:
            gfx_by_sentence.setdefault(i, g["id"])
    slots = []
    for i, s in enumerate(sentences):
        slots.append({
            "id": f"SH-{i + 1:04d}", "sentence": s["id"], "section": s["section"],
            "kind": "GFX" if i in gfx_by_sentence else "FTG", "gfx": gfx_by_sentence.get(i),
            "text": s["text"], "start": s["start"], "end": s["slot_end"],
            "tc_in": tc(s["start"]), "tc_out": tc(s["slot_end"]),
            "match": s["match"], "interpolated": s.get("interpolated", False),
            "footage": None,
        })

    stats = _ratio_stats(graphics, duration)
    return {
        "version": 1,
        "title": script["title"],
        "fps": FPS,
        "motion_fps": MOTION_FPS,
        "resolution": [3840, 2160],
        "vo": vo,
        "alignment": align_report,
        "stats": stats,
        "chapters": chapters,
        "graphics": graphics,
        "slots": slots,
        "references": script.get("references", []),
    }


def _anchor(block: Dict[str, Any], pos: int, blocks: List[Dict[str, Any]], sents: List[Dict[str, Any]],
            sid_to_idx: Dict[str, int], covered: set) -> List[int]:
    """
    Where a client cue lands. Clients place cues inconsistently (data charts before the paragraph that
    reads the numbers, stills and cards after), so the cue goes to the sentence in the neighbouring
    paragraphs that shares the most numbers/keywords with it. Cues with nothing to match on (a caption
    card) fall back to position: quick facts introduce what follows, everything else closes what preceded.
    Cues never stack: a span already taken shifts to the next free sentences.
    """
    cue = block["cue"]
    cue_text = " ".join(str(cue.get(k) or "") for k in ("caption", "text", "description", "file", "raw"))

    prev_idx = next((sid_to_idx[b["id"]] for b in reversed(blocks[:pos]) if b["kind"] == "narration"), None)
    next_idx = next((sid_to_idx[b["id"]] for b in blocks[pos + 1:] if b["kind"] == "narration"), None)

    window: List[int] = []
    if prev_idx is not None:
        window += [k for k in range(len(sents)) if sents[k]["para"] == sents[prev_idx]["para"]]
    if next_idx is not None:
        window += [k for k in range(len(sents)) if sents[k]["para"] == sents[next_idx]["para"]]

    best, best_score = None, 0.0
    for k in window:
        sc = _affinity(cue_text, sents[k]["text"])
        if sc > best_score:
            best, best_score = k, sc

    if best is not None and best_score >= 3:
        span = _span_forward(sents, best) if cue["type"] in FORWARD_CUES else _span_back(sents, best)
    elif cue["type"] in FORWARD_CUES and next_idx is not None:
        span = _span_forward(sents, next_idx)
    elif prev_idx is not None:
        span = _span_back(sents, prev_idx)
    elif next_idx is not None:
        span = _span_forward(sents, next_idx)
    else:
        return []

    if covered.intersection(span):
        start = max(covered.intersection(range(span[0], len(sents)))) + 1
        while start in covered:
            start += 1
        if start >= len(sents):
            return []
        span = _span_forward(sents, start)
    return span


def _graphic_from_cue(block: Dict[str, Any], sentences: List[Dict[str, Any]], span: List[int]) -> Dict[str, Any]:
    cue = block["cue"]
    template = CUE_TEMPLATE.get((cue["type"], cue.get("variant")), cue["type"])
    label = cue.get("caption") or cue.get("text") or cue.get("description") or cue["raw"]
    g = {
        "id": None, "origin": "client", "status": "approved", "template": template,
        "label": label, "cue_ref": block["id"], "sentence_idx": span,
        "start": sentences[span[0]]["start"], "end": sentences[span[-1]]["slot_end"],
    }
    for k in ("file", "source", "description", "shape"):
        if cue.get(k):
            g[k] = cue[k]
    return g


def _union_seconds(ranges: List[List[float]]) -> float:
    total, cur_s, cur_e = 0.0, None, None
    for s, e in sorted(ranges):
        if cur_e is None or s > cur_e:
            if cur_e is not None:
                total += cur_e - cur_s
            cur_s, cur_e = s, e
        else:
            cur_e = max(cur_e, e)
    if cur_e is not None:
        total += cur_e - cur_s
    return total


def _ratio_stats(graphics: List[Dict[str, Any]], duration: float) -> Dict[str, Any]:
    client = [[g["start"], g["end"]] for g in graphics if g["origin"] == "client"]
    everything = [[g["start"], g["end"]] for g in graphics]
    c = _union_seconds(client)
    a = _union_seconds(everything)
    return {
        "duration_sec": round(duration, 2),
        "gfx_count_client": len(client),
        "gfx_count_with_suggestions": len(everything),
        "gfx_share_client": round(c / duration, 3),
        "gfx_share_with_suggestions": round(a / duration, 3),
        "target_band": [0.25, 0.45],
    }
