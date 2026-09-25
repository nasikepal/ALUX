"""
Union of several transcriptions of the same VO into one complete, well-timed word list.

No single whisper run was complete on EP001: the whole-file runs skipped four read-aloud chapter titles
after long pauses (and drifted up to 3.5 s there); the chunked DTW run has accurate timing but lost a line
that fell on a chunk boundary. So:

  primary     = chunked + DTW (timing)
  gap filler  = words present in BOTH secondary runs but missing from the primary, re-timed to sit between
                the primary's neighbouring words (offset taken from the nearest matched word)
"""

import json
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .captions import key


def union(primary: List[Dict[str, Any]], a: List[Dict[str, Any]], b: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    p = [w for w in primary if key(w["text"])]
    a = [w for w in a if key(w["text"])]
    b = [w for w in b if key(w["text"])]
    pk, ak, bk = [key(w["text"]) for w in p], [key(w["text"]) for w in a], [key(w["text"]) for w in b]

    # which words of `a` does `b` also have? (two independent runs agree they were spoken)
    a_in_b = set()
    for op, i1, i2, j1, j2 in SequenceMatcher(None, ak, bk, autojunk=False).get_opcodes():
        if op == "equal":
            a_in_b.update(range(i1, i2))

    out: List[Dict[str, Any]] = []
    log: List[Dict[str, Any]] = []
    for op, i1, i2, j1, j2 in SequenceMatcher(None, pk, ak, autojunk=False).get_opcodes():
        if op in ("equal", "replace", "delete"):
            out.extend(p[i1:i2])            # primary wins wherever it has words
        if op == "insert" or (op == "replace" and (j2 - j1) > (i2 - i1) + 2):
            miss = [k for k in range(j1, j2) if k in a_in_b]
            if op == "replace":
                continue                    # a partial disagreement, not a dropped line: leave to caption QC
            if not miss:
                continue
            # offset between runs from the nearest matched neighbour
            left_p = out[-1] if out else None
            left_a = a[j1 - 1] if j1 > 0 else None
            offset = (left_p["start"] - left_a["start"]) if (left_p and left_a) else 0.0
            right_start = p[i2]["start"] if i2 < len(p) else float("inf")
            def place(off):
                lo, res = (left_p["end"] if left_p else 0.0), []
                for k in miss:
                    st = max(a[k]["start"] + off, lo)
                    en = max(a[k]["end"] + off, st + 0.05)
                    res.append({"text": a[k]["text"], "start": st, "end": en})
                    lo = en
                return res

            ins = place(offset)
            if ins and ins[-1]["end"] > right_start - 0.02:
                raw = place(0.0)          # the secondary run's own timing, if it fits the gap
                if raw[-1]["end"] <= right_start - 0.02:
                    ins = raw
            # the inserted words must sit between the primary's neighbours: redistribute if they overshoot
            left_end = left_p["end"] if left_p else 0.0
            if ins and (ins[-1]["end"] > right_start - 0.02 or ins[0]["start"] >= right_start):
                t0 = min(left_end, right_start - 0.05 * len(ins) - 0.02)
                t1 = right_start - 0.02
                step = max(t1 - t0, 0.05 * len(ins)) / len(ins)
                for n, w in enumerate(ins):
                    w["start"], w["end"] = t0 + n * step, t0 + (n + 1) * step
            out.extend(ins)
            log.append({"t": ins[0]["start"], "added": " ".join(w["text"] for w in ins)})
    return repair_ends(out), log


def repair_ends(words: List[Dict[str, Any]], typical: float = 0.32) -> List[Dict[str, Any]]:
    """
    DTW fixes word starts but whisper's word ends stay coarse (often end <= start). A word ends just before
    the next one starts, capped at a typical word length so real pauses stay visible.
    """
    for i, w in enumerate(words):
        nxt = words[i + 1]["start"] if i + 1 < len(words) else w["start"] + typical
        end = w["end"] if w["end"] > w["start"] + 0.05 else w["start"] + typical
        w["end"] = max(w["start"] + 0.05, min(end, nxt - 0.01, w["start"] + max(typical, 0.08 * len(w["text"]))))
    return words


def to_whisper_json(words: List[Dict[str, Any]], path: Path, method: str) -> Path:
    segs = [{"text": " " + w["text"], "offsets": {"from": int(round(w["start"] * 1000)), "to": int(round(w["end"] * 1000))}}
            for w in words]
    path.write_text(json.dumps({"transcription": segs, "method": method}, ensure_ascii=False), encoding="utf-8")
    return path
