"""
Script Parsing and Segmentation Engine.
Deconstructs Markdown script notes into deterministic sections and Visual Units.
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple
import re
import yaml
from core.models import ScriptDocument, VisualUnit
from core.config import config
from core.logger import logger


class ScriptParser:
    def __init__(self):
        self.wps = config.words_per_second

    def parse_file(self, file_path: Path) -> ScriptDocument:
        raw_content = file_path.read_text(encoding="utf-8")
        metadata, body = self.extract_frontmatter(raw_content)
        title = metadata.get("project") or metadata.get("title") or file_path.stem
        
        doc = ScriptDocument(
            file_path=file_path,
            title=title,
            metadata=metadata,
            raw_content=raw_content
        )
        
        doc.sections = self.extract_sections(body)
        doc.visual_units = self.segment_into_visual_units(doc.sections)
        return doc

    @staticmethod
    def extract_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
        metadata = {}
        body = text
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1]) or {}
                    body = parts[2]
                except Exception as e:
                    logger.warning(f"Error parsing YAML frontmatter: {e}")
        return metadata, body

    @staticmethod
    def extract_sections(body: str) -> List[Dict[str, Any]]:
        """
        Extracts H2 sections (e.g. ## 01 — Hook, ## 02 — Context, etc.)
        and captures their narration lines and subsections.
        """
        sections = []
        # Pattern to split by H2 headers
        pattern = r"(^##\s+.*?)(?=(?:^##\s+)|\Z)"
        matches = re.findall(pattern, body, flags=re.MULTILINE | re.DOTALL)
        
        for idx, sec_text in enumerate(matches):
            lines = sec_text.strip().splitlines()
            header_line = lines[0].strip()
            # Clean header title
            title = re.sub(r"^##\s*", "", header_line).strip()
            
            # Extract narration lines (prefer blockquotes > line, or plain paragraphs before any H3)
            narration_lines = []
            in_h3 = False
            for line in lines[1:]:
                stripped = line.strip()
                if stripped.startswith("###"):
                    in_h3 = True
                    continue
                if not in_h3:
                    if stripped.startswith(">"):
                        narration_lines.append(stripped.lstrip("> ").strip())
                    elif stripped and not stripped.startswith(("-", "*", "|", "[", "#")):
                        narration_lines.append(stripped)

            narration = " ".join(narration_lines).strip()
            sections.append({
                "index": idx + 1,
                "title": title,
                "header_line": header_line,
                "narration": narration,
                "raw_section": sec_text
            })

        # Fallback if no H2 sections found: treat paragraphs as units
        if not sections:
            paragraphs = [p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("#")]
            for idx, p in enumerate(paragraphs):
                sections.append({
                    "index": idx + 1,
                    "title": f"Beat {idx + 1:02d}",
                    "header_line": f"## Beat {idx + 1:02d}",
                    "narration": p,
                    "raw_section": p
                })

        return sections

    def segment_into_visual_units(self, sections: List[Dict[str, Any]]) -> List[VisualUnit]:
        """
        Converts parsed sections into formal Visual Units with duration calculation.
        """
        visual_units = []
        for sec in sections:
            vu_id = f"VU-{sec['index']:03d}"
            text = sec["narration"]
            word_count = len(text.split()) if text else 12
            duration = max(4, int(round(word_count / self.wps)))

            unit = VisualUnit(
                id=vu_id,
                script_section=sec["title"],
                text=text or sec["title"],
                duration_sec=duration
            )
            visual_units.append(unit)

        return visual_units


script_parser = ScriptParser()
