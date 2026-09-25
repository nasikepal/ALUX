"""
Client script (.docx) -> script.json

ALUX scripts follow a stable convention:
  Title style      -> episode title
  Heading 1        -> section / chapter
  italic paragraph -> direction (not spoken): ON-SCREEN GRAPHIC, ILLUSTRATION CARD, TIMELINE CARD,
                      QUICK FACT, ON-SCREEN CTA, plus the caption line that follows a CARD
  normal paragraph -> spoken narration
Only narration is expected in the voice over; directions become cues.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from docx import Document

CUE_PATTERNS = [
    ("cta", re.compile(r"^ON-SCREEN CTA:\s*(.*)$", re.I)),
    ("graphic", re.compile(r"^ON-SCREEN GRAPHIC:\s*(.*)$", re.I)),
    ("illustration", re.compile(r"^ILLUSTRATION CARD\b\s*(\(.*?\))?\s*(.*)$", re.I)),
    ("timeline", re.compile(r"^TIMELINE CARD\b\s*(\(.*?\))?\s*(.*)$", re.I)),
    ("quickfact", re.compile(r"^QUICK FACT:\s*(.*)$", re.I)),
]
# Cards announce a type on one line and carry their caption on the next italic line.
CAPTIONED = {"illustration", "timeline"}

# Abbreviations that must not end a sentence.
_ABBR = r"(?<!\bU\.S)(?<!\bMr)(?<!\bMrs)(?<!\bDr)(?<!\bSt)(?<!\bvs)(?<!\bInc)(?<!\bNo)"
_SENT_SPLIT = re.compile(_ABBR + r"(?<=[.!?])[\"”’)]?\s+(?=[\"“‘(]?[A-Z0-9$])")


def split_sentences(text: str) -> List[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text.strip()) if s.strip()]


def _is_italic(p) -> bool:
    runs = [r for r in p.runs if r.text.strip()]
    return bool(runs) and all(r.italic for r in runs)


def _parse_graphic(body: str) -> Dict[str, Any]:
    """ON-SCREEN GRAPHIC is either `file.jpg | caption` (client still) or a data brief with `source:`."""
    m = re.match(r"^\s*([\w\-]+\.(?:jpg|jpeg|png|psd|ai|svg|mp4|mov))\s*\|\s*(.*)$", body, re.I)
    if m:
        return {"variant": "still", "file": m.group(1), "caption": m.group(2).strip()}
    src = None
    sm = re.search(r"[,;]?\s*source[s]?:\s*(.*)$", body, re.I)
    if sm:
        src = sm.group(1).strip()
        body = body[: sm.start()].strip()
    variant = "data" if re.search(r"\d", body) and src else "brief"
    return {"variant": variant, "description": body, "source": src}


def ingest(docx_path: Path) -> Dict[str, Any]:
    doc = Document(str(docx_path))
    title = ""
    meta: List[str] = []
    sections: List[Dict[str, Any]] = []
    blocks: List[Dict[str, Any]] = []
    pending_caption: Optional[Dict[str, Any]] = None
    section_id: Optional[str] = None
    n_sent = 0
    n_para = 0
    in_back_matter = False
    references: List[str] = []

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        style = p.style.name

        if style == "Title":
            title = text
            continue
        if style.startswith("Heading"):
            # Everything after the END heading is back matter (sources list), never read by the VO.
            if in_back_matter or text.strip().upper() == "END":
                in_back_matter = True
                continue
            section_id = f"S{len(sections) + 1:02d}"
            sections.append({"id": section_id, "title": text})
            pending_caption = None
            continue

        if in_back_matter:
            references.append(text)
            continue

        if _is_italic(p):
            if section_id is None:
                meta.append(text)
                continue
            if pending_caption is not None:
                pending_caption["cue"]["caption"] = text
                pending_caption = None
                continue
            for cue_type, pat in CUE_PATTERNS:
                m = pat.match(text)
                if not m:
                    continue
                cue: Dict[str, Any] = {"type": cue_type, "raw": text}
                if cue_type == "graphic":
                    cue.update(_parse_graphic(m.group(1)))
                elif cue_type in CAPTIONED:
                    cue["shape"] = (m.group(1) or "").strip("() ")
                    cue["caption"] = m.group(2).strip() or None
                else:
                    cue["text"] = m.group(1).strip()
                block = {"id": f"C{sum(1 for b in blocks if b['kind'] == 'cue') + 1:03d}",
                         "kind": "cue", "section": section_id, "cue": cue}
                blocks.append(block)
                if cue_type in CAPTIONED and not cue["caption"]:
                    pending_caption = block
                break
            else:
                # Unknown italic line: keep it visible as a direction rather than dropping it.
                blocks.append({"id": f"C{sum(1 for b in blocks if b['kind'] == 'cue') + 1:03d}",
                               "kind": "cue", "section": section_id,
                               "cue": {"type": "note", "text": text, "raw": text}})
            continue

        if section_id is None:
            meta.append(text)
            continue
        pending_caption = None
        n_para += 1
        for s in split_sentences(text):
            n_sent += 1
            blocks.append({"id": f"B{n_sent:04d}", "kind": "narration", "section": section_id,
                           "para": n_para, "text": s})

    return {
        "title": title,
        "meta": meta,
        "source_file": str(docx_path),
        "sections": sections,
        "blocks": blocks,
        "references": references,
    }
