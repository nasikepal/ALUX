"""
Markdown Output and Script Writer Engine.
Enforces rational constraints to convert raw narration into production-ready
Visual Markdown Panel Breakdowns with bidirectional Obsidian graph links.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml
from core.models import ScriptDocument, VisualUnit
from scoring.relevance import render_progress_bar
from core.config import config
from core.logger import logger
from pipeline.source import source_note_name


class MarkdownWriter:
    def update_script_with_production_data(
        self,
        doc: ScriptDocument,
        units: List[VisualUnit],
        music_cues: Optional[List[Dict[str, Any]]] = None
    ) -> Path:
        """
        Enriches the script note into a conformed Visual Markdown Panel Breakdown
        adhering to rational pacing, artistic transduction, and graph link constraints.
        """
        # Update metadata
        meta = dict(doc.metadata)
        meta["status"] = "production"
        # Statuses describe what the pipeline actually found — "completed" is never claimed on a
        # human's behalf. Sources only become verified after Research Inbox review.
        has_claims = any(u.claims for u in units)
        any_unsourced = any(u.unsourced_claims for u in units)
        meta["broll_status"] = "candidates_found" if all(u.primary_broll for u in units) else "needs_sourcing"
        meta["research_status"] = "needs_research" if any_unsourced else ("needs_review" if has_claims else "no_claims")
        meta["source_status"] = meta["research_status"]
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
            "",
            "> [!info|system] 🧭 Production OS Graph Navigation",
            "> **Core System Links**: [[00_SYSTEM/Dashboard|Command Dashboard]] • [[00_SYSTEM/Automation|Automation Engine]] • [[00_SYSTEM/ARTISTIC_LOGIC_ENGINE|Artistic Logic]] • [[00_SYSTEM/Settings|Scoring Rules]] • [[05_SHOTS/Shot_Planner|Master Storyboard]]",
            "",
            "---",
            ""
        ]

        cumulative_sec = 0

        for u_idx, u in enumerate(units):
            start_sec = cumulative_sec
            end_sec = cumulative_sec + u.duration_sec
            cumulative_sec = end_sec
            tc_range = f"{start_sec//60:02d}:{start_sec%60:02d} — {end_sec//60:02d}:{end_sec%60:02d}"

            word_count = len(u.text.split())
            wps = round(word_count / max(u.duration_sec, 1), 2)

            lines.append(f"## {u.script_section}")
            lines.append(f"> {u.text}")
            lines.append("")

            # 1. Master Visual Markdown Panel Breakdown (Two-Column A/V Table)
            p = u.primary_broll
            if p:
                p_title = f"[{p.title}]({p.url})"
            elif u.broll_search_links:
                p_title = "⚠️ **NO ASSET FOUND** — search: " + " · ".join(
                    f"[{l['label']}]({l['url']})" for l in u.broll_search_links[:2])
            else:
                p_title = "⚠️ **NO ASSET FOUND**"
            p_spec = f"`{p.visual_specificity}/5`" if p else "`—`"
            p_score = f"`{int(round(p.relevance_score * 100))}%`" if p else "`—`"

            # Claims summary for panel
            claims_summary = ""
            if u.claims and u.source_matches:
                claims_links = []
                for sm in u.source_matches[:2]:
                    claims_links.append(f"[[{source_note_name(sm)}\\|{sm.publisher}]] (`{sm.verification_status}`)")
                if u.unsourced_claims:
                    claims_links.append(f"⚠️ {len(u.unsourced_claims)} claim(s) unsourced")
                claims_summary = "<br>".join(claims_links)
            elif u.claims:
                claims_summary = f"⚠️ **UNSOURCED**: *{u.claims[0][:40]}...*"
            else:
                claims_summary = "*Narrative beat (stylistic)*"

            # Sound & Score summary for panel
            ambience_txt = u.sound_intent.ambience[0] if u.sound_intent and u.sound_intent.ambience else "Atmospheric room tone"
            mech_txt = u.sound_intent.mechanical[0] if u.sound_intent and u.sound_intent.mechanical else "Tactile operation"
            trans_txt = u.sound_intent.transition[0] if u.sound_intent and u.sound_intent.transition else "Cinematic whoosh"
            impact_txt = u.sound_intent.emphasis[0] if u.sound_intent and u.sound_intent.emphasis else "Sub bass hit"

            mc = music_cues[u_idx] if (music_cues and u_idx < len(music_cues)) else None
            score_summary = f"**Score Cue**: `{mc['cue_id']}` ({mc['tempo']}, {mc['musical_key']})<br>*{mc['emotional_mood']}*" if mc else "**Score**: Thematic bed"

            cine = u.interpretation_levels.get("level_06_cinematic", {})
            framing_txt = cine.get("preferred_shots", [u.visual_intent.camera])[0]
            motion_txt = cine.get("camera_motion", u.visual_intent.movement)
            lighting_txt = cine.get("lighting", u.visual_intent.lighting)
            avoid_txt = ", ".join(u.avoid_criteria.get("items", ["slop_tropes"])[:3])

            lines.append(f"### Visual Markdown Panel — {u.id}")
            lines.append("")
            lines.append("| AUDIO / VO TRACK | VISUAL DIRECTION & B-ROLL SPEC | ACOUSTIC & MUSIC TRACK |")
            lines.append("|---|---|---|")
            lines.append(
                f"| **Timecode**: `{tc_range}` ({u.duration_sec}s)<br>"
                f"**Pacing**: `{word_count} words` ({wps} wps)<br><br>"
                f"**Visual Job**: `{', '.join(u.visual_jobs)}`<br>"
                f"**Function**: `{', '.join(u.narrative_functions)}`<br><br>"
                f"📰 **Claims & Proof**:<br>{claims_summary} "
                f"| **Framing**: `{framing_txt}`<br>"
                f"**Movement**: `{motion_txt}`<br>"
                f"**Lighting**: `{lighting_txt}`<br><br>"
                f"🎬 **Primary Asset**:<br>{p_title}<br>"
                f"**Specificity**: {p_spec} • **Relevance**: {p_score}<br><br>"
                f"🚫 **Avoid**: `{avoid_txt}` "
                f"| 🔊 **Ambience**: `{ambience_txt}`<br>"
                f"⚙️ **Mechanical**: `{mech_txt}`<br>"
                f"💨 **Transition**: `{trans_txt}`<br>"
                f"💥 **Impact**: `{impact_txt}`<br><br>"
                f"🎵 {score_summary} |"
            )
            lines.append("")

            # 2. Collapsible Directorial Callouts
            strat = u.visual_strategy
            levels = u.interpretation_levels

            lines.append("> [!quote|artistic] 🎨 Artistic Reasoning & 6-Level Interpretation Hierarchy")
            lines.append(f"> - **Thematic Motif**: `{strat.get('motif', 'scale')}` (Evaluated via [[00_SYSTEM/ARTISTIC_LOGIC_ENGINE|Artistic Logic Engine]])")
            lines.append(f"> - **Primary Visual**: {strat.get('primary_visual', 'Subject')}")
            lines.append(f"> - **Secondary Visual**: {strat.get('secondary_visual', 'Context')}")
            lines.append(f"> - **Visual Metaphor**: *{strat.get('abstract_visual', 'Metaphor')}*")
            lines.append("> ")
            lines.append(f"> 1. **Literal**: {', '.join(levels.get('level_01_literal', []))}")
            lines.append(f"> 2. **Contextual**: {', '.join(levels.get('level_02_contextual', []))}")
            lines.append(f"> 3. **Conceptual**: {', '.join(levels.get('level_03_conceptual', []))}")
            lines.append(f"> 4. **Metaphorical**: {', '.join(levels.get('level_04_metaphorical', []))}")
            lines.append(f"> 5. **Emotional**: {', '.join(levels.get('level_05_emotional', []))}")
            lines.append(f"> 6. **Cinematic**: `{framing_txt}` | Motion: `{motion_txt}` | Lighting: `{lighting_txt}`")
            lines.append("")

            # Avoid Guardrails
            avoid = u.avoid_criteria
            if avoid.get("items"):
                lines.append("> [!warning|avoid] 🚫 Editorial Avoid Guardrails (DO NOT MATCH)")
                lines.append(f"> - **Banned Visual Tropes**: `{', '.join(avoid.get('items', []))}`")
                lines.append(f"> - **Director Rationale**: > {avoid.get('reason', 'Prevents generic imagery.')}")
                lines.append("")

            # B-Roll Shot Candidates
            lines.append("> [!example|broll] 🎬 Shot Candidate Cards & Scored Assets")
            if u.primary_broll:
                p_pct = int(round(p.relevance_score * 100))
                p_bar = render_progress_bar(p_pct)
                lines.append(f"> - **Primary Recommendation**: **[{p.title}]({p.url})**")
                lines.append(f">   - **Relevance**: {p_bar} `{p_pct}%` | **Specificity**: `{p.visual_specificity}/5`")
                lines.append(f">   - **Director Note**: > {p.why_reason}")
                lines.append(f">   - **Specs**: Source: `{p.source}` | Type: `{p.asset_type.upper()}` | Res: `{p.resolution}` | License: `{p.license}`")
            else:
                lines.append("> - **Primary Recommendation**: ⚠️ none — no real asset was found by any provider")
            if u.broll_search_links:
                links = " · ".join(f"[{l['label']}]({l['url']})" for l in u.broll_search_links)
                lines.append(f"> - **Manual search links** (not assets — license/resolution unknown until you pick a clip): {links}")

            if u.alternative_broll:
                alt = u.alternative_broll
                alt_pct = int(round(alt.relevance_score * 100))
                alt_bar = render_progress_bar(alt_pct)
                lines.append(f"> - **Alternative Candidate**: **[{alt.title}]({alt.url})**")
                lines.append(f">   - **Relevance**: {alt_bar} `{alt_pct}%` | **Specificity**: `{alt.visual_specificity}/5`")
                lines.append(f">   - **Specs**: Source: `{alt.source}` | Type: `{alt.asset_type.title()}` | License: `{alt.license}`")
            lines.append("")

            # Sequence Intelligence & Coverage
            seq = u.sequence_logic
            cov = u.visual_coverage
            lines.append("> [!note|sequence] 🎯 Sequence Intelligence & Visual Coverage")
            if seq:
                lines.append(f"> - **Editorial Cutting Rule**: `{seq.get('editorial_intent', 'Dynamic visual progression')}`")
                lines.append(f"> - **Recommended Next Framing**: `{seq.get('recommended_framing', 'medium contextual')}`")
                lines.append(f"> - **Redundancy Filter**: `{', '.join(seq.get('avoid', ['visual monotony']))}`")
            if cov:
                lines.append(f"> - **Section Coverage**: `{cov.get('coverage_pct', 75)}%` ({cov.get('status_label', 'SUFFICIENT')}) (Target: $\\ge 75\\%$)")
            lines.append("")

            # Acoustic SFX Table
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

                    if asset.asset_type == "search_link":
                        lines.append(f"| {layer_name} | {intent_term} | ⚠️ no file — [search {asset.source.replace(' search', '')}]({asset.url}) | — |")
                    else:
                        rel_pct = int(round(asset.relevance_score * 100))
                        lines.append(f"| {layer_name} | {intent_term} | [{asset.title}]({asset.url}) | {rel_pct}% |")
            else:
                lines.append("| — | — | ⚠️ no SFX analysis ran | — |")
            lines.append("")

            # Musical Score Direction
            if mc:
                lines.append("### Musical Score Direction")
                lines.append(f"- **Cue**: `{mc['cue_id']}` ({mc['timecode_range']})")
                lines.append(f"- **Tempo & Key**: `{mc['tempo']}` | Key: `{mc['musical_key']}`")
                lines.append(f"- **Emotional Tone**: *{mc['emotional_mood']}*")
                lines.append(f"- **Instrumentation**: {mc['instrumentation']}")
                lines.append(f"- **Style Reference**: `{mc['reference_style']}`")
                track = mc['matched_asset']
                if track.asset_type == "search_link":
                    lines.append(f"- **Thematic Track**: ⚠️ no local track — [{track.source}]({track.url})")
                else:
                    lines.append(f"- **Thematic Track**: [{track.title}]({track.url})")
                lines.append("")

            # Claims and candidate sources — nothing here is verified until a human accepts it
            lines.append("### Claims & Evidence (unverified until Research Inbox sign-off)")
            if u.claims:
                for c in u.claims:
                    lines.append(f"**Claim**: *\"{c}\"*")
                    lines.append("Sources:")
                    claim_sources = [sm for sm in u.source_matches if sm.claim_text == c]
                    if claim_sources:
                        for sm in claim_sources:
                            lines.append(
                                f"- [[{source_note_name(sm)}]] (`{sm.publisher}` · reputation `{sm.credibility}` · "
                                f"keyword match {int(round(sm.relevance_score * 100))}% · `{sm.verification_status}`)"
                            )
                    else:
                        leads = u.unsourced_claims.get(c, [])
                        lead_txt = " — leads: " + " · ".join(f"[{l['label']}]({l['url']})" for l in leads[:3]) if leads else ""
                        lines.append(f"- [ ] ⚠️ **No source found** — do not put on screen{lead_txt}")
            else:
                lines.append("*(Stylistic narrative beat — no statistical or empirical claims)*")

            lines.append("")
            lines.append("---")
            lines.append("")

        final_content = "\n".join(lines)
        doc.file_path.write_text(final_content, encoding="utf-8")
        logger.info(f"Successfully updated script note with visual markdown panel breakdown: {doc.file_path}")
        return doc.file_path


markdown_writer = MarkdownWriter()
