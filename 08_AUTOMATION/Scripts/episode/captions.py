"""
VO + client script -> broadcast captions (SRT) timed to the spoken words.

What is said comes from the VO (captions must match the audio); how it is spelled comes from the
script wherever the two agree. Whisper hears words well but misspells names ("Barban" for Barbon) and
sometimes mishears ("afloat" for "of float"); the script spells everything right but the VO was not
always read from the same draft. So:

  equal spans       -> script spelling and punctuation, VO timing
  near-miss words   -> script spelling (same word, misheard/misspelled)          [logged]
  VO-only words     -> kept as heard (ad-libs, chapter titles read aloud)       [logged]
  script-only words -> dropped (not in the audio)                               [logged]
  conflicting words -> kept as heard, flagged for a human to listen             [REVIEW]

Layout follows common subtitle practice: <= 42 characters per line, <= 2 lines, >= 5/6 s on screen,
reading speed <= 20 characters/second where the gaps allow it, breaks at pauses and phrase boundaries,
never ending a line on a function word.
"""

import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Tuple

FPS = 24
MAX_LINE = 42
MAX_LINES = 2
MIN_DUR = 5 / 6
MAX_DUR = 6.0
MAX_CPS = 20.0
PAUSE = 0.45          # a silence this long always ends a caption
TAIL = 0.25           # caption lingers this long after the last word when there is room
PREROLL = 0.12        # and may appear this much before the first word, if the previous one is gone
MIN_GAP = 2 / FPS     # frames between consecutive captions
FUNCTION_WORDS = {"a", "an", "the", "of", "to", "and", "or", "but", "in", "on", "at", "for", "with", "by", "from",
                  "as", "that", "is", "are", "was", "were", "be", "if", "so", "your", "you", "their", "its", "his",
                  "her", "our", "my", "this", "these", "those", "than", "then", "into", "onto", "not", "no", "who"}


def key(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def is_num(k: str) -> bool:
    return bool(re.search(r"\d", k))


def title_case_heading(h: str) -> str:
    small = {"a", "an", "the", "of", "in", "on", "for", "to", "and", "as", "at", "by", "or"}
    words = h.split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        cap = i == 0 or i == len(words) - 1 or lw.strip(":,") not in small or words[i - 1].endswith(":")
        out.append("-".join(p[:1].upper() + p[1:] for p in lw.split("-")) if cap else lw)
    return " ".join(out).replace("'S", "'s")


def script_words(script: Dict[str, Any]) -> List[str]:
    """Narration surface words in order, with numbered chapter headings where the narrator may read them."""
    out: List[str] = []
    sec_title = {s["id"]: s["title"] for s in script["sections"]}
    seen = set()
    for b in script["blocks"]:
        if b["kind"] != "narration":
            continue
        sec = b["section"]
        if sec not in seen:
            seen.add(sec)
            t = sec_title.get(sec, "")
            if t.upper().startswith("CHAPTER"):
                num, _, rest = t.partition(":")          # "CHAPTER 5B" / "THE COMPANY THAT ..."
                heading = (num.title() + ":").split() + title_case_heading(rest.strip()).split()
                heading[-1] += "."            # a title is a sentence of its own
                out += heading
        para = b["text"].split()
        if para and not re.search(r"[.?!:;,\"”'—)]$", para[-1]):
            para[-1] += "."           # the script often leaves a paragraph without its full stop
        out += para
    return out


def _window_keys(words: List[Dict[str, Any]], t0: float, t1: float) -> List[str]:
    return [key(w["text"]) for w in words if t0 - 0.35 <= w["start"] <= t1 + 0.05 and key(w["text"])]


def _is_name(script_words: List[str], j: int) -> bool:
    w = script_words[j]
    sentence_start = j == 0 or re.search(r"[.?!:]$", script_words[j - 1]) is not None
    return w[:1].isupper() and not sentence_start


class Speech:
    """RMS of the VO (16-bit mono WAV) in a time window: is someone speaking there?"""
    def __init__(self, wav: Path):
        import array, wave
        with wave.open(str(wav), "rb") as w:
            self.rate = w.getframerate()
            self.x = array.array("h", w.readframes(w.getnframes()))
        n = len(self.x)
        step = self.rate // 100  # 10 ms
        self.frames = [max(abs(v) for v in self.x[i:i + step]) if i + step <= n else 0 for i in range(0, n, step)]
        voiced = sorted(self.frames)
        self.floor = voiced[len(voiced) // 10]            # quiet reference (pauses)
        self.speech = voiced[len(voiced) // 2]            # typical speech level

    def present(self, t0: float, t1: float) -> bool:
        a, b = int(t0 * 100), max(int(t1 * 100), int(t0 * 100) + 1)
        seg = self.frames[a:b]
        return bool(seg) and max(seg) > self.floor + 0.35 * (self.speech - self.floor)


def relisten(wav: Path, t0: float, t1: float, candidates: List[str], whisper_models: List[Tuple[Path, List[str]]]) -> Tuple[str, str]:
    """
    Tie-break by re-transcribing just this stretch of audio several ways. Returns (winner, evidence);
    winner is "" when no candidate is heard by a majority.
    """
    import subprocess, tempfile
    clip = Path(tempfile.mkdtemp()) / "clip.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{max(0.0, t0 - 0.6):.2f}", "-t", f"{t1 - t0 + 1.6:.2f}",
                    "-i", str(wav), str(clip)], check=True)
    heard = []
    for model, extra in whisper_models:
        r = subprocess.run(["whisper-cli", "-m", str(model), "-f", str(clip), "-l", "en", "-nt", "-np"] + extra,
                           capture_output=True, text=True)
        heard.append(" ".join(r.stdout.split()))
    def toks(t):
        return [key(x) for x in t.replace("-", " ").split() if key(x)]

    def said(c, h):
        c_t, h_t = toks(c), toks(h)
        if c_t and any(h_t[i:i + len(c_t)] == c_t for i in range(len(h_t) - len(c_t) + 1)):
            return True
        return bool(is_num(key(c)) or _values(c)) and bool(set(_values(c)) & set(_values(h)))

    # candidates that say the same thing ("Seventy-two" / "72") are one candidate; keep the first spelling
    uniq = []
    for c in candidates:
        if not toks(c):
            continue
        if any(toks(c) == toks(u) or (_values(c) and _values(c) == _values(u)) for u in uniq):
            continue
        uniq.append(c)
    votes = {c: sum(1 for h in heard if said(c, h)) for c in uniq}
    best = sorted(votes.items(), key=lambda kv: -kv[1])
    evidence = " / ".join(heard)
    if best and best[0][1] >= 2 and (len(best) == 1 or best[1][1] < best[0][1]):
        return best[0][0], evidence
    return "", evidence


def merge(vo: List[Dict[str, Any]], script: List[str],
          check: List[Dict[str, Any]] = None, speech: "Speech" = None,
          tiebreak=None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Caption words = VO words and timing, script spelling where they agree. `check` is an independent
    second transcription used as a tie-breaker wherever the VO and the script disagree.
    Returns (words, log); log entries of kind "REVIEW" need a human to listen.
    """
    vk = [key(w["text"]) for w in vo]
    sk = [key(x) for x in script]
    sm = SequenceMatcher(None, vk, sk, autojunk=False)
    out: List[Dict[str, Any]] = []
    log: List[Dict[str, Any]] = []
    # word-level agreement between the two independent transcriptions
    agree, alt = set(), []
    if check is not None:
        ck = [key(w["text"]) for w in check]
        for op2, a1, a2, b1, b2 in SequenceMatcher(None, vk, ck, autojunk=False).get_opcodes():
            if op2 == "equal":
                agree.update(range(a1, a2))
            elif op2 == "replace":
                alt.append((a1, a2, "".join(ck[b1:b2]), " ".join(w["text"] for w in check[b1:b2])))

    def spread(v, s, j0=None):
        t0, t1 = v[0]["start"], v[-1]["end"]
        step = (t1 - t0) / len(s)
        return [{"text": x, "start": t0 + k * step, "end": t0 + (k + 1) * step, **({"sidx": j0 + k} if j0 is not None else {})}
                for k, x in enumerate(s)]

    def verify(i1, i2, s, what):
        """VO words vo[i1:i2] disagree with script span s: the 2nd pass, then the audio, decide."""
        v = [{**w, "src": "vo"} if not s else w for w in vo[i1:i2] if key(w["text"])]
        if not v:
            return []
        vtxt, stxt = " ".join(x["text"] for x in v), " ".join(s)
        sj = "".join(key(x) for x in s)
        if check is not None:
            if all(i in agree for i in range(i1, i2) if key(vo[i]["text"])):
                log.append({"t": v[0]["start"], "kind": "confirmed by 2nd pass", "why": what, "vo": vtxt, "script": stxt})
                return v
            for a1, a2, cj, ctxt in alt:
                if a1 < i2 and i1 < a2 and sj and cj == sj:
                    log.append({"t": v[0]["start"], "kind": "fixed by 2nd pass", "why": what, "vo": vtxt, "script": stxt})
                    return spread(v, s)
        if not s and speech is not None and all(speech.present(w["start"], max(w["end"], w["start"] + 0.12)) for w in v) \
                and len(v) <= 3:
            log.append({"t": v[0]["start"], "kind": "kept: short VO-only words, speech present", "vo": vtxt, "script": ""})
            return v
        p2 = ""
        alt_txt = ""
        if check is not None:
            p2 = " ".join(w["text"] for w in check if v[0]["start"] - 0.8 <= w["start"] <= v[-1]["end"] + 0.8)
            alt_txt = next((ctxt for a1, a2, cj, ctxt in alt if a1 < i2 and i1 < a2), "")
        if tiebreak is not None:
            cands = [c for c in dict.fromkeys([vtxt, stxt, alt_txt]) if c]
            win, ev = tiebreak(v[0]["start"], v[-1]["end"], cands)
            if win:
                log.append({"t": v[0]["start"], "kind": "decided by re-listening the clip", "why": what, "vo": vtxt,
                            "script": stxt, "pass2": alt_txt, "chosen": win, "evidence": ev})
                if win == vtxt:
                    return v
                return spread(v, win.split())
        log.append({"t": v[0]["start"], "kind": "REVIEW", "why": what, "vo": vtxt, "script": stxt, "pass2": p2})
        return v

    for op, i1, i2, j1, j2 in sm.get_opcodes():
        v, s = vo[i1:i2], script[j1:j2]
        if op == "equal":
            out.extend({**w, "text": x, "sidx": j1 + k, "vo_text": w["text"]} for k, (w, x) in enumerate(zip(v, s)))
        elif op == "insert":            # script words the VO does not have
            if check is not None and i1 > 0:
                t0 = vo[i1 - 1]["end"]
                t1 = vo[i1]["start"] if i1 < len(vo) else t0 + 1
                c = "".join(_window_keys(check, t0 + 0.3, t1 - 0.05))
                sj = "".join(key(x) for x in s)
                if sj and len(sj) > 3 and sj in c:
                    log.append({"t": t0, "kind": "REVIEW", "why": "2nd pass hears script words the 1st pass missed",
                                "vo": "", "script": " ".join(s)})
            log.append({"t": vo[min(i1, len(vo) - 1)]["start"], "kind": "script-only (not spoken)", "vo": "", "script": " ".join(s)})
        elif op == "delete":            # words only in the VO (ad-libs, chapter titles read aloud)
            out.extend(verify(i1, i2, [], "VO-only words"))
        else:                           # replace
            vj, sj = "".join(vk[i1:i2]), "".join(sk[j1:j2])
            nums = is_num(vj) or is_num(sj)
            both_heard = check is not None and all(i in agree for i in range(i1, i2))
            vo_txt, s_txt = " ".join(x["text"] for x in v), " ".join(s)
            if vj == sj:                # same letters: spacing/hyphen/punctuation only
                if "/" in vo_txt or (re.search(r"\d+-\w", vo_txt) and "-" not in s_txt) or \
                        (vo_txt.count("-") > s_txt.count("-") and re.search(r"\d|\b(one|two|three|four|five|six|seven|eight|nine|ten)-", vo_txt, re.I)):
                    out.extend(v)       # URLs keep their slash; numeric compounds keep their hyphens ("35-year-old")
                else:
                    out.extend(spread(v, s, j1))
                log.append({"t": v[0]["start"], "kind": "format from script", "vo": " ".join(x["text"] for x in v), "script": " ".join(s)})
            elif s and s[0] == "Chapter" and not any(key(x["text"]) == "chapter" for x in v):
                out.extend(verify(i1, i2, [], "VO-only words"))  # title not read aloud; keep what was said
                log.append({"t": v[0]["start"], "kind": "chapter title not read aloud", "vo": " ".join(x["text"] for x in v), "script": " ".join(s)})
            elif nums:
                extra = [x for x in v if re.search(r"[a-z]", x["text"], re.I) and not _values(x["text"])
                         and key(x["text"]) not in {"percent", "dollars", "dollar", "times", "a", "and"}
                         and key(x["text"]) not in sk[j1:j2]]
                if _same_number(vo_txt, s_txt) and not extra:
                    out.extend(spread(v, s, j1))   # same value: the client's written form ("Nineteen", "14.1 billion dollars")
                elif _same_number(vo_txt, s_txt):
                    out.extend(v)                  # same value but the narrator said more ("Now 20 years ago"): keep it all
                    log.append({"t": v[0]["start"], "kind": "kept VO (extra spoken words)", "vo": vo_txt, "script": s_txt})
                else:
                    out.extend(verify(i1, i2, s, "number differs"))
            elif len(v) == len(s) and all(_is_name(script, j1 + k) and SequenceMatcher(None, vk[i1 + k], sk[j1 + k]).ratio() >= 0.6
                                          for k in range(len(s))):
                out.extend({**w, "text": x, "sidx": j1 + k} for k, (w, x) in enumerate(zip(v, s)))  # names: script spelling
                log.append({"t": v[0]["start"], "kind": "name spelling from script", "vo": " ".join(x["text"] for x in v), "script": " ".join(s)})
            elif SequenceMatcher(None, vj, sj).ratio() >= 0.88 and not both_heard:
                out.extend(spread(v, s, j1))                            # near-identical sound, runs disagree ("afloat" / "of float")
                log.append({"t": v[0]["start"], "kind": "mishearing fixed from script", "vo": vo_txt, "script": s_txt})
            elif SequenceMatcher(None, vj, sj).ratio() >= 0.88:
                out.extend(v)                                           # both runs heard it: the narrator said it ("we are", "costs")
                log.append({"t": v[0]["start"], "kind": "kept VO (both runs agree)", "vo": vo_txt, "script": s_txt})
            else:
                out.extend(verify(i1, i2, s, "wording differs"))
    return title_headings(fix_punct(fix_case(boundary_punct(tidy(out)), script), script), script), log


def boundary_punct(words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Where script words meet words the narrator changed, the sentence ends where the VO ends it:
    "cheap protection [at all.] Now they're" -> "cheap protection. Now they're";
    "borrow against later. [on.]" -> "borrow against later on."
    """
    for i, w in enumerate(words):
        if "sidx" not in w or "vo_text" not in w:
            continue
        nxt = words[i + 1] if i + 1 < len(words) else None
        if nxt is not None and nxt.get("sidx") == w["sidx"] + 1:
            continue                                   # script continues as written: keep its punctuation
        vo_end = re.search(r"[.?!]$", w["vo_text"])
        sc_end = re.search(r"[.?!]$", w["text"])
        if vo_end and not sc_end:
            words[i] = {**w, "text": re.sub(r"[,;:]$", "", w["text"]) + vo_end.group()}
        elif sc_end and not vo_end and nxt is not None and "sidx" not in nxt and not _ABBR.search(w["text"]):
            # the narrator ran on: "number. [but] here's" -> "number, but here's"; "built for. [so] start" -> "built for, so start"
            after = key(words[i + 2]["text"]) if i + 2 < len(words) else ""
            joined = key(nxt["text"]) in COORD | {"so"} and nxt["text"][:1].lower() == nxt["text"][:1] \
                and not (key(nxt["text"]) == "or" and after == "not")          # "ruin them or not" takes no comma
            words[i] = {**w, "text": w["text"][:-1] + ("," if joined else "")}
    return words


def heading_spans(script: List[str]) -> List[Tuple[int, int]]:
    """Script index ranges of the chapter titles script_words() inserted ("Chapter", "5B:", ..., "People.")."""
    spans, j = [], 0
    while j < len(script) - 1:
        if script[j] == "Chapter" and re.fullmatch(r"\d+[A-Z]?:", script[j + 1]):
            k = j + 1
            while k < len(script) and not script[k].endswith("."):
                k += 1
            spans.append((j, k + 1))
            j = k + 1
        else:
            j += 1
    return spans


def title_headings(words: List[Dict[str, Any]], script: List[str]) -> List[Dict[str, Any]]:
    """
    Chapter titles read aloud are written exactly as the script's heading (title case, colon, full stop) and
    tagged, so segment() keeps each one whole on a caption of its own. Only words matched to the heading's own
    script range are touched: the sentence the narrator starts right after it keeps its normal case.
    """
    for a, b in heading_spans(script):
        idx = [i for i, w in enumerate(words) if w.get("sidx") is not None and a <= w["sidx"] < b]
        if not idx or key(script[a]) != key(words[idx[0]]["text"]):
            continue                                            # the title was not read aloud
        idx = list(range(idx[0], idx[-1] + 1))                  # contiguous run, VO words inside it included
        for i in idx:
            j = words[i].get("sidx")
            text = script[j] if j is not None and a <= j < b else words[i]["text"]
            words[i] = {**words[i], "text": text.rstrip("."), "heading": a}
        words[idx[-1]]["text"] += "."
        nxt = idx[-1] + 1
        if nxt < len(words) and words[nxt]["text"][:1].islower():
            words[nxt] = {**words[nxt], "text": words[nxt]["text"][:1].upper() + words[nxt]["text"][1:]}
        if nxt + 1 < len(words) and key(words[nxt]["text"]) in DISCOURSE and not re.search(r"[,.?!:;]$", words[nxt]["text"]):
            words[nxt] = {**words[nxt], "text": words[nxt]["text"] + ","}   # "Now, picture London" like every other opener
    return words


def tidy(words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Drop tokens that are only punctuation (a stray '–'); write spoken URLs the way they are typed."""
    words = [w for w in words if key(w["text"])]
    out: List[Dict[str, Any]] = []
    i = 0
    while i < len(words):
        w = words[i]
        # "alux.com slash app" -> "alux.com/app"
        if i + 2 < len(words) and key(words[i + 1]["text"]) == "slash" and re.search(r"\.\w{2,}$", w["text"].rstrip(",.")):
            tail = words[i + 2]["text"]
            out.append({**w, "text": w["text"].rstrip(",.") + "/" + tail, "end": words[i + 2]["end"]})
            i += 3
            continue
        out.append(w)
        i += 1
    return out


def script_names(script: List[str]) -> set:
    """Words the script capitalizes mid-sentence and never writes in lower case: names and titles."""
    names = {"I"}
    lower_seen = {re.sub(r"[^\w'-]", "", w) for w in script if w[:1].islower()}
    for j, w in enumerate(script):
        if j and w[:1].isupper() and not re.search(r"[.?!:]$", script[j - 1]):
            c = re.sub(r"[^\w'-]", "", w)
            if c[:1].lower() + c[1:] not in lower_seen:
                names.add(c)
    return names


def fix_case(words: List[Dict[str, Any]], script: List[str]) -> List[Dict[str, Any]]:
    """
    A capital that exists only because the word opened a sentence in the script is wrong once the narrator
    put words in front of it ("Now, Health insurance ..."). Every other capital in the script (names,
    titles, "Wall Street", "Founding Fathers") is kept as written.
    """
    names = script_names(script)
    for i in range(1, len(words)):
        w = words[i]
        j = w.get("sidx")
        acronym = len(w["text"]) > 1 and w["text"].rstrip(".,;:?!").isupper()
        if j is None or not w["text"][:1].isupper() or acronym or re.sub(r"[^\w'-]", "", w["text"]) in names:
            continue
        opened_sentence = j == 0 or re.search(r"[.?!:]$", script[j - 1]) is not None
        mid_sentence_now = not re.search(r"[.?!:\"“]$", words[i - 1]["text"])
        if opened_sentence and mid_sentence_now and w["text"] != "I" and not w["text"].startswith("I'"):
            words[i] = {**w, "text": w["text"][:1].lower() + w["text"][1:]}
    if words and words[0]["text"][:1].islower():
        words[0] = {**words[0], "text": words[0]["text"][:1].upper() + words[0]["text"][1:]}
    return words


_ABBR = re.compile(r"^([A-Z]\.)+$|\.(com|org|net|io)\b", re.I)
DISCOURSE = {"now", "well", "so", "alright", "okay", "actually"}
COORD = {"but", "and", "or"}


def fix_punct(words: List[Dict[str, Any]], script_: List[str]) -> List[Dict[str, Any]]:
    """
    Sentence punctuation around words the narrator added: "number. but here's" -> "number, but here's";
    "Now two doors" -> "Now, two doors"; and a capital after every full stop.
    """
    for i in range(1, len(words)):
        w, prev = words[i], words[i - 1]
        k = key(w["text"])
        if w.get("src") == "vo" and k in COORD and prev["text"].endswith(".") and not _ABBR.search(prev["text"]):
            words[i - 1] = {**prev, "text": prev["text"][:-1] + ","}
            words[i] = {**w, "text": w["text"][:1].lower() + w["text"][1:]}
            continue
        if re.search(r"[.?!]$", prev["text"]) and not _ABBR.search(prev["text"]) and w["text"][:1].islower():
            words[i] = {**w, "text": w["text"][:1].upper() + w["text"][1:]}
    for i in range(len(words) - 1):
        w, nxt = words[i], words[i + 1]
        starts = i == 0 or re.search(r"[.?!]$", words[i - 1]["text"])
        if starts and w["text"].lower() in DISCOURSE and not re.search(r"[,.?!:;]$", w["text"]) and w["text"][:1].isupper():
            words[i] = {**w, "text": w["text"] + ","}
            j = nxt.get("sidx")
            opened = j is not None and (j == 0 or re.search(r"[.?!:]$", script_[j - 1]) is not None)
            acronym = len(nxt["text"]) > 1 and nxt["text"].rstrip(".,;:?!").isupper()
            if nxt["text"][:1].isupper() and opened and not acronym and nxt["text"] != "I" \
                    and re.sub(r"[^\w'-]", "", nxt["text"]) not in script_names(script_):
                words[i + 1] = {**nxt, "text": nxt["text"][:1].lower() + nxt["text"][1:]}
    return words


_WORDNUM = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                       "fourteen fifteen sixteen seventeen eighteen nineteen".split())}
_TENS = {w: 10 * (i + 2) for i, w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())}


def _values(text: str) -> List[float]:
    t = text.lower().replace(",", "")
    vals = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", t)]
    pat = r"\b(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[- ](one|two|three|four|five|six|seven|eight|nine))?\b"
    for m in re.finditer(pat, t):
        vals.append(_TENS[m.group(1)] + (_WORDNUM[m.group(2)] if m.group(2) else 0))
    t = re.sub(pat, " ", t)                                 # "seventy-nine" is 79, not 70 and 9
    for w, n in _WORDNUM.items():
        if re.search(rf"\b{w}\b", t):
            vals.append(n)
    return sorted(vals)


def _same_number(a: str, b: str) -> bool:
    va, vb = _values(a), _values(b)
    return bool(va) and bool(set(va) & set(vb)) and not (set(va) ^ set(vb)) - {100.0, 1000.0, 1e6, 1e9}


# ---------------------------------------------------------------------------------------------------
def is_heading(cap: List[Dict[str, Any]]) -> bool:
    return bool(cap) and cap[0].get("heading") is not None


def fits(text: str) -> bool:
    """True if the text fits on <= 2 lines of <= 42 characters."""
    if len(text) <= MAX_LINE:
        return True
    words = text.split()
    return any(len(" ".join(words[:i])) <= MAX_LINE and len(" ".join(words[i:])) <= MAX_LINE for i in range(1, len(words)))


def segment(words: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    caps, cur = [], []
    for i, w in enumerate(words):
        if cur:
            text = " ".join(x["text"] for x in cur + [w])
            gap = w["start"] - cur[-1]["end"]
            dur = w["end"] - cur[0]["start"]
            sentence_end = re.search(r"[.?!:]\W*$", cur[-1]["text"]) is not None
            same_heading = w.get("heading") is not None and cur[-1].get("heading") == w.get("heading")
            if same_heading and fits(text):
                cur.append(w)           # a chapter title is never split
                continue
            edge = w.get("heading") != cur[-1].get("heading")      # a title starts or ends: caption boundary
            if (edge or gap >= PAUSE or not fits(text) or dur > MAX_DUR
                    or (sentence_end and cur[-1]["end"] - cur[0]["start"] >= 1.0)):
                caps.append(cur)
                cur = []
        cur.append(w)
    if cur:
        caps.append(cur)
    # never end a caption on a dangling function word: push it to the next caption
    for a, b in zip(caps, caps[1:]):
        while len(a) > 1 and not is_heading(a) and not is_heading(b) and key(a[-1]["text"]) in FUNCTION_WORDS and not re.search(r"[.,?!;:]$", a[-1]["text"]) \
                and fits(" ".join(x["text"] for x in [a[-1]] + b)):
            b.insert(0, a.pop())
    caps = [c for c in caps if c]
    return merge_short(caps)


def merge_short(caps: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
    """A flash of one or two words is hard to read: fold it into a neighbour when it fits and they are close."""
    def dur(c):
        return c[-1]["end"] - c[0]["start"]

    def text(c):
        return " ".join(w["text"] for w in c)

    changed = True
    while changed:
        changed = False
        for i, c in enumerate(caps):
            if (dur(c) >= MIN_DUR + 0.15 and len(text(c)) >= 14) or is_heading(c):
                continue
            prev_ok = i > 0 and not is_heading(caps[i - 1]) and c[0]["start"] - caps[i - 1][-1]["end"] < 1.0 and fits(text(caps[i - 1] + c)) \
                and dur(caps[i - 1] + c) <= MAX_DUR + 1.0
            next_ok = i + 1 < len(caps) and not is_heading(caps[i + 1]) and caps[i + 1][0]["start"] - c[-1]["end"] < 1.0 and fits(text(c + caps[i + 1])) \
                and dur(c + caps[i + 1]) <= MAX_DUR + 1.0
            # a caption that ends a sentence joins what came before; one that opens a sentence joins what follows
            ends_sentence = re.search(r"[.?!]$", c[-1]["text"]) is not None
            if prev_ok and (ends_sentence or not next_ok):
                caps[i - 1] = caps[i - 1] + c
            elif next_ok:
                caps[i + 1] = c + caps[i + 1]
            elif i > 0 and len(caps[i - 1]) > 3:
                # neighbours are full: take the tail of the previous caption (from its last comma, else last
                # few words) so the orphan becomes a readable phrase ("... right" / "now." -> "right now.")
                p = caps[i - 1]
                cut = max((k + 1 for k in range(len(p) - 1) if re.search(r"[,;:]$", p[k]["text"])), default=0)
                if cut == 0 or len(p) - cut > 6:
                    cut = len(p) - min(3, len(p) - 2)
                moved = p[cut:]
                if not fits(text(moved + c)) or cut < 2:
                    continue
                caps[i - 1], caps[i] = p[:cut], moved + c
                changed = True
                break
            else:
                continue
            del caps[i]
            changed = True
            break
    return caps


def break_lines(text: str) -> str:
    if len(text) <= MAX_LINE:
        return text
    words = text.split()
    best, best_score = None, 1e9
    for i in range(1, len(words)):
        l1, l2 = " ".join(words[:i]), " ".join(words[i:])
        if len(l1) > MAX_LINE or len(l2) > MAX_LINE:
            continue
        score = abs(len(l1) - len(l2))                                  # balanced
        if re.search(r"[,.;:?!]$", words[i - 1]):
            score -= 20                                                 # break after punctuation
        if key(words[i - 1]) in FUNCTION_WORDS:
            score += 30                                                 # not after a function word
        if key(words[i]) in {"and", "but", "or", "so", "because", "which", "who", "that", "when", "while"}:
            score -= 8                                                  # before a conjunction
        if len(l2) > len(l1) + 12:
            score += 6                                                  # prefer a longer top line (pyramid)
        if score < best_score:
            best, best_score = (l1, l2), score
    if best is None:  # cannot fit: split in the middle (segmenter keeps this rare)
        mid = len(words) // 2
        best = (" ".join(words[:mid]), " ".join(words[mid:]))
    return best[0] + "\n" + best[1]


def time_captions(caps: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    out = []
    for i, c in enumerate(caps):
        text = " ".join(w["text"] for w in c)
        prev_out = out[-1]["f_out"] / FPS if out else 0.0
        t_in = max(c[0]["start"] - PREROLL, prev_out + MIN_GAP, 0.0)
        t_in = min(t_in, c[0]["start"])
        nxt = caps[i + 1][0]["start"] - PREROLL if i + 1 < len(caps) else c[-1]["end"] + 2
        t_out = min(c[-1]["end"] + TAIL, nxt - MIN_GAP)
        need = max(MIN_DUR, len(text) / MAX_CPS)
        if t_out - t_in < need:
            t_out = min(t_in + need, nxt - MIN_GAP)
        f_in, f_out = round(t_in * FPS), round(t_out * FPS)
        if out and f_in <= out[-1]["f_out"]:
            f_in = out[-1]["f_out"] + 1
        f_out = max(f_out, f_in + 1)
        out.append({"i": len(out) + 1, "f_in": f_in, "f_out": f_out, "text": break_lines(text),
                    "cps": round(len(text) / ((f_out - f_in) / FPS), 1)})
    return out


def srt_time(f: int) -> str:
    ms = round(f / FPS * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(caps: List[Dict[str, Any]], path: Path) -> Path:
    blocks = [f"{c['i']}\n{srt_time(c['f_in'])} --> {srt_time(c['f_out'])}\n{c['text']}\n" for c in caps]
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path


def qc(caps: List[Dict[str, Any]]) -> Dict[str, Any]:
    lines = [l for c in caps for l in c["text"].split("\n")]
    return {
        "captions": len(caps),
        "max_line_chars": max(len(l) for l in lines),
        "lines_over_42": sum(1 for l in lines if len(l) > MAX_LINE),
        "over_2_lines": sum(1 for c in caps if c["text"].count("\n") > 1),
        "under_min_duration": sum(1 for c in caps if (c["f_out"] - c["f_in"]) / FPS < MIN_DUR - 1e-6),
        "over_20_cps": sum(1 for c in caps if c["cps"] > MAX_CPS),
        "overlaps": sum(1 for a, b in zip(caps, caps[1:]) if b["f_in"] <= a["f_out"]),
        "ending_on_function_word": sum(1 for c in caps if key(c["text"].split()[-1]) in FUNCTION_WORDS
                                       and not re.search(r"[.,?!;:]$", c["text"])),
    }
