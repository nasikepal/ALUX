"""
Markdown Output and Script Writer Engine.
Writes production-ready B-Roll, SFX, and Source recommendations back into the Markdown script.
"""

from typing import List, Dict, Any
from pathlib import Path
import yaml
from core.models import ScriptDocument, VisualUnit
from scoring.relevance import render_progress_bar
from core.config import config
from core.logger import logger


class MarkdownWriter:
    def update_script_with_production_data(self, doc: ScriptDocument, units: List[VisualUnit]) -> Path:
        """
        Rewrites/enriches the script note with production-ready Visual Intent,
        B-Roll suggestions, SFX tables, and Source wikilinks.
        """
        # Update metadata
        meta = dict(doc.metadata)
        meta["status"] = "production"
        meta["broll_status"] = "completed"
        meta["research_status"] = "completed"
        meta["source_status"] = "completed"
        meta["visual_units_count"] = len(units)
        total_duration = sum(u.duration_sec for u in units)
        minutes = total_duration // 60
        seconds = total_duration % 60
        meta["duration"] = f"{minutes:02d}:{seconds:02d}"

        lines = [
            "---",
            yaml.dump(meta, sort_keys=False).strip(),
            "---",
            "",
            f"# {doc.title}",
            ""
        ]

        for u in units:
            lines.append(f"## {u.script_section}")
            lines.append(f"> {u.text}")
            lines.append("")

            # Visual Intent block
            lines.append("### Visual Intent")
            for p in u.visual_intent.primary:
                lines.append(f"- **Primary**: {p}")
            for s in u.visual_intent.secondary:
                lines.append(f"- **Secondary**: {s}")
            for a in u.visual_intent.abstract:
                lines.append(f"- *Abstract Concept*: {a}")
            lines.append(f"- **Camera**: `{u.visual_intent.camera}` | **Movement**: `{u.visual_intent.movement}`")
            lines.append(f"- **Lighting**: `{u.visual_intent.lighting}`")
            lines.append("")

            # B-Roll Recommendations
            lines.append(f"### B-Roll Recommendations — {u.id}")
            if u.primary_broll:
                p = u.primary_broll
                pct = int(round(p.relevance_score * 100))
                bar = render_progress_bar(pct)
                lines.append("#### Primary Recommendation")
                lines.append(f"**{p.title}**")
                lines.append(f"Relevance: {bar}")
                lines.append("Why:")
                lines.append(f"> {p.why_reason}")
                lines.append(f"- **Source**: [{p.source}]({p.url})")
                lines.append(f"- **Type**: `{p.asset_type.upper()}` | **Resolution**: `{p.resolution}`")
                lines.append(f"- **License**: {p.license}")
                lines.append(f"- **Target Duration**: {p.duration or f'{u.duration_sec}s'}")
                lines.append("")

            if u.alternative_broll:
                alt = u.alternative_broll
                alt_pct = int(round(alt.relevance_score * 100))
                alt_bar = render_progress_bar(alt_pct)
                lines.append("---")
                lines.append("#### Alternative Option")
                lines.append(f"**{alt.title}**")
                lines.append(f"Relevance: {alt_bar}")
                lines.append(f"- **Source**: [{alt.source}]({alt.url})")
                lines.append(f"- **Type**: `{alt.asset_type.title()}` | **License**: `{alt.license}`")
                lines.append("")

            if u.editorial_news:
                en = u.editorial_news
                lines.append("---")
                lines.append("#### Editorial / News Context")
                lines.append(f"**{en.title}**")
                lines.append(f"- **Publisher**: {en.publisher}")
                lines.append(f"- **Source URL**: [{en.publisher}]({en.url})")
                lines.append(f"- **Published**: {en.published_date}")
                lines.append(f"- **Credibility / Relevance**: `{en.credibility.upper()}` ({int(round(en.relevance_score * 100))}%)")
                lines.append("")

            # Checklist
            lines.append("#### Shot Checklist")
            lines.append(f"- [ ] {u.id} Master B-Roll asset ingested")
            lines.append(f"- [ ] Color profile & framerate matched")
            lines.append(f"- [ ] Edit cut-point trimmed ({u.duration_sec}s)")
            lines.append("")

            # SFX Table
            lines.append("### SFX & Sound Design")
            lines.append("| Layer | Semantic Sound Intent | Asset Match | Relevance |")
            lines.append("|---|---|---|---:|")
            if u.sfx_matches:
                layers = ["Ambience", "Mechanical", "Transition", "Emphasis"]
                for i, asset in enumerate(u.sfx_matches):
                    layer_name = layers[i] if i < len(layers) else "Foley"
                    intent_term = ""
                    if layer_name == "Ambience" and u.sound_intent.ambience:
                        intent_term = u.sound_intent.ambience[0]
                    elif layer_name == "Mechanical" and u.sound_intent.mechanical:
                        intent_term = u.sound_intent.mechanical[0]
                    elif layer_name == "Transition" and u.sound_intent.transition:
                        intent_term = u.sound_intent.transition[0]
                    elif layer_name == "Emphasis" and u.sound_intent.emphasis:
                        intent_term = u.sound_intent.emphasis[0]
                    else:
                        intent_term = asset.title

                    rel_pct = int(round(asset.relevance_score * 100))
                    lines.append(f"| {layer_name} | {intent_term} | [{asset.title}]({asset.url}) | {rel_pct}% |")
            else:
                lines.append("| Ambience | Environmental room tone | [Studio Library](#) | 90% |")
            lines.append("")

            # Claims and Verified Sources
            lines.append("### Claims & Verified Evidence")
            if u.claims:
                for c in u.claims:
                    lines.append(f"**Claim**: *\"{c}\"*")
                    lines.append("Sources:")
                    if u.source_matches:
                        for sm in u.source_matches:
                            safe_pub = sm.publisher.replace('/', '-')
                            safe_title = sm.title[:50].replace('/', '-')
                            lines.append(f"- [[Source - {safe_pub} - {safe_title}]] (`{sm.publisher}` - {int(round(sm.relevance_score * 100))}% credibility)")
                    else:
                        lines.append("- [ ] Source pending verification")
            else:
                lines.append("*(Stylistic narrative beat — no statistical or empirical claims)*")

            lines.append("")
            lines.append("---")
            lines.append("")

        final_content = "\n".join(lines)
        doc.file_path.write_text(final_content, encoding="utf-8")
        logger.info(f"Successfully updated script note: {doc.file_path}")
        return doc.file_path


markdown_writer = MarkdownWriter()
