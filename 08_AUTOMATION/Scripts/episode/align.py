"""
Script sentences <-> whisper word timestamps.

The script text is known, so this is matching, not recognition: tokens from both sides are
normalized and aligned with difflib. Voice actors drift from the page (added words, dropped
words, numbers read differently) — unmatched tokens are tolerated and sentence bounds are
taken from the first/last matched word, with interpolation for sentences nothing matched in.
"""

import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_TOKEN = re.compile(r"[a-z]+(?:'[a-z]+)?|\d+")


def normalize(text: str) -> List[str]:
    text = text.lower().replace("’", "'").replace("‘", "'")
    return _TOKEN.findall(text)


def _ts_to_sec(ts: str) -> float:
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def load_whisper_words(path: Path) -> List[Dict[str, Any]]:
    """whisper-cli `-ml 1 -sow -oj` output -> [{token, start, end}] with one entry per normalized token."""
    data = json.loads(path.read_text(encoding="utf-8"))
    words = []
    for seg in data.get("transcription", []):
        if "offsets" in seg:
            start, end = seg["offsets"]["from"] / 1000.0, seg["offsets"]["to"] / 1000.0
        else:
            start = _ts_to_sec(seg["timestamps"]["from"])
            end = _ts_to_sec(seg["timestamps"]["to"])
        for tok in normalize(seg.get("text", "")):
            words.append({"token": tok, "start": start, "end": end})
    return words


def align_sentences(sentences: List[Dict[str, Any]], words: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Adds `start`, `end`, `match` (share of the sentence's tokens found in the VO) to each sentence."""
    script_tokens: List[str] = []
    owner: List[int] = []  # script token index -> sentence index
    for si, s in enumerate(sentences):
        toks = normalize(s["text"])
        script_tokens.extend(toks)
        owner.extend([si] * len(toks))

    vo_tokens = [w["token"] for w in words]
    sm = SequenceMatcher(None, script_tokens, vo_tokens, autojunk=False)

    hits: List[List[int]] = [[] for _ in sentences]  # word indices per sentence
    for a, b, size in sm.get_matching_blocks():
        for k in range(size):
            hits[owner[a + k]].append(b + k)

    total = [0] * len(sentences)
    for si in owner:
        total[si] += 1

    for si, s in enumerate(sentences):
        h = hits[si]
        s["match"] = round(len(h) / total[si], 2) if total[si] else 0.0
        if h:
            s["start"] = round(words[min(h)]["start"], 3)
            s["end"] = round(words[max(h)]["end"], 3)
        else:
            s["start"] = s["end"] = None

    _interpolate(sentences)
    _close_gaps(sentences)

    matched = sum(1 for s in sentences if s["match"] >= 0.5)
    return {
        "sentences": len(sentences),
        "well_matched": matched,
        "token_coverage": round(sum(len(h) for h in hits) / max(1, len(script_tokens)), 3),
        "vo_tokens_used": round(sum(len(h) for h in hits) / max(1, len(vo_tokens)), 3),
        "low_confidence": [s["id"] for s in sentences if s["match"] < 0.5],
    }


def _interpolate(sentences: List[Dict[str, Any]]) -> None:
    """Sentences with no matched token get the gap between their timed neighbours."""
    i = 0
    n = len(sentences)
    while i < n:
        if sentences[i]["start"] is not None:
            i += 1
            continue
        j = i
        while j < n and sentences[j]["start"] is None:
            j += 1
        left = sentences[i - 1]["end"] if i > 0 else 0.0
        right = sentences[j]["start"] if j < n else left
        step = (right - left) / (j - i) if j > i else 0
        for k in range(i, j):
            sentences[k]["start"] = round(left + step * (k - i), 3)
            sentences[k]["end"] = round(left + step * (k - i + 1), 3)
            sentences[k]["interpolated"] = True
        i = j


def _close_gaps(sentences: List[Dict[str, Any]]) -> None:
    """Footage slots must tile the timeline: each sentence runs until the next one starts."""
    for a, b in zip(sentences, sentences[1:]):
        if b["start"] is not None and a["end"] is not None and b["start"] > a["end"]:
            a["slot_end"] = b["start"]
        else:
            a["slot_end"] = a["end"]
    if sentences:
        sentences[-1]["slot_end"] = sentences[-1]["end"]
