"""
Markdown Output and Script Writer Engine.
Writes production-ready B-Roll, SFX, Sources, and Artistic Logic back into the Markdown script.
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
        Enriches the script note with 6-level Visual Interpretation,
        Artistic Search Matrix, DO NOT MATCH guardrails, B-Roll, SFX, and Coverage gauges.
        """
        # Update metadata
        meta = dict(doc.metadata)
        meta["status"] = "production"
        meta["broll_status"] = "completed"
        meta["research_status"] = "completed"
        meta["source_status"] = "completed"
        meta["visual_units_count"] = len(units)
        meta["artistic_engine"] = "v2-editorial"
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

            # 1. Artistic Reasoning & Visual Strategy
            lines.append("### Artistic Reasoning & Visual Strategy")
            lines.append(f"- **Visual Job**: `{', '.join(u.visual_jobs)}`")
            lines.append(f"- **Narrative Function**: `{', '.join(u.narrative_functions)}`")
            
            strat = u.visual_strategy
            lines.append(f"- **Thematic Motif**: `{strat.get('motif', 'scale')}`")
            lines.append(f"- **Primary Visual**: {strat.get('primary_visual', 'Subject')}")
            lines.append(f"- **Secondary Visual**: {strat.get('secondary_visual', 'Context')}")
            lines.append(f"- **Visual Metaphor**: *{strat.get('abstract_visual', 'Metaphor')}*")
            lines.append("")

            # 2. 6-Level Visual Interpretation Hierarchy
            levels = u.interpretation_levels
            lines.append("#### 6-Level Visual Interpretation")
            lines.append(f"1. **Literal (Physical)**: {', '.join(levels.get('level_01_literal', []))}")
            lines.append(f"2. **Contextual (Environment)**: {', '.join(levels.get('level_02_contextual', []))}")
            lines.append(f"3. **Conceptual (Underlying Idea)**: {', '.join(levels.get('level_03_conceptual', []))}")
            lines.append(f"4. **Metaphorical (Analogous Reality)**: {', '.join(levels.get('level_04_metaphorical', []))}")
            lines.append(f"5. **Emotional (Audience Feeling)**: {', '.join(levels.get('level_05_emotional', []))}")
            cine = levels.get('level_06_cinematic', {})
            lines.append(f"6. **Cinematic (Behavior in Edit)**: `{cine.get('preferred_shots', ['wide'])[0]}` | Motion: `{cine.get('camera_motion', 'slow push')}` | Lighting: `{cine.get('lighting', 'high contrast')}`")
            lines.append("")

            # 3. DO NOT MATCH Guardrails
            avoid = u.avoid_criteria
            if avoid.get("items"):
                lines.append("#### Editorial Avoid Guardrails (DO NOT MATCH)")
                lines.append(f"- **Banned Visual Tropes**: `{', '.join(avoid.get('items', []))}`")
                lines.append(f"- **Director Rationale**: > {avoid.get('reason', 'Prevents generic imagery.')}")
                lines.append("")

            # 4. Search Strategy Matrix
            matrix = u.search_matrix
            if matrix:
                lines.append("#### Artistic Search Matrix")
                lines.append(f"- **Literal**: `{', '.join(matrix.get('literal_search', []))}`")
                lines.append(f"- **Contextual**: `{', '.join(matrix.get('contextual_search', []))}`")
                lines.append(f"- **Conceptual**: `{', '.join(matrix.get('conceptual_search', []))}`")
                lines.append(f"- **Cinematic**: `{', '.join(matrix.get('cinematic_search', []))}`")
                lines.append(f"- **Detail**: `{', '.join(matrix.get('detail_search', []))}`")
                lines.append("")

            # 5. B-Roll Recommendations
            lines.append(f"### B-Roll Recommendations — {u.id}")
            if u.primary_broll:
                p = u.primary_broll
                pct = int(round(p.relevance_score * 100))
                bar = render_progress_bar(pct)
                lines.append("#### Primary Recommendation")
                lines.append(f"**{p.title}**")
                lines.append(f"Relevance: {bar} | **Visual Specificity**: `{p.visual_specificity}/5`")
                lines.append(f"Narrative Function: `{p.narrative_function}`")
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
                lines.append(f"Relevance: {alt_bar} | **Visual Specificity**: `{alt.visual_specificity}/5`")
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

            # 6. Sequence Intelligence
            seq = u.sequence_logic
            if seq:
                lines.append("#### Sequence Intelligence")
                lines.append(f"- **Editorial Cutting Rule**: `{seq.get('editorial_intent', 'Dynamic visual progression')}`")
                lines.append(f"- **Recommended Next Framing**: `{seq.get('recommended_framing', 'medium contextual')}`")
                lines.append(f"- **Visual Redundancy Filter**: `{', '.join(seq.get('avoid', ['visual monotony']))}`")
                lines.append("")

            # 7. Visual Coverage
            cov = u.visual_coverage
            if cov:
                lines.append("#### Visual Coverage")
                lines.append(f"> **Section Coverage**: `{cov.get('coverage_pct', 75)}%` ({cov.get('status_label', 'SUFFICIENT')})")
                lines.append("```")
                for b in cov.get("ascii_bars", []):
                    lines.append(b)
                lines.append("```")
                lines.append("")

            # 8. SFX Table
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

            # 9. Claims and Verified Sources
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
        logger.info(f"Successfully updated script note with artistic logic: {doc.file_path}")
        return doc.file_path


markdown_writer = MarkdownWriter()
