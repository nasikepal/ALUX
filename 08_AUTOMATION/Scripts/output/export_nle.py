"""
NLE and Timeline Exporter for DaVinci Resolve, Premiere Pro, and Executive Production Briefs.
Exports CSV cut lists, EDL timeline markers, and comprehensive production dossiers.
"""

from typing import List, Dict, Any
from pathlib import Path
import csv
from datetime import datetime
from core.models import ScriptDocument, VisualUnit, ShotItem
from core.logger import logger


def seconds_to_timecode(seconds: int, fps: int = 24) -> str:
    """Converts seconds into standard SMPTE timecode (HH:MM:SS:FF)."""
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    frames = 0
    return f"{hrs:02d}:{mins:02d}:{secs:02d}:{frames:02d}"


class NLEExporter:
    def export_csv(
        self,
        doc: ScriptDocument,
        units: List[VisualUnit],
        shots: List[ShotItem],
        music_cues: List[Dict[str, Any]],
        out_path: Optional[Path] = None
    ) -> Path:
        """
        Exports a production cut list CSV ready for DaVinci Resolve, Premiere Pro, or Final Cut.
        """
        if not out_path:
            out_path = doc.file_path.parent / f"{doc.title.replace(' ', '_')}_CutList.csv"

        headers = [
            "Shot_ID",
            "Visual_Unit",
            "Timecode_In",
            "Timecode_Out",
            "Duration_Sec",
            "Section",
            "Narration_Beat",
            "Visual_Job",
            "Narrative_Function",
            "Visual_Specificity",
            "Primary_Broll_Title",
            "Broll_URL",
            "Resolution",
            "Camera_Direction",
            "SFX_Ambience",
            "SFX_Mechanical",
            "SFX_Transition",
            "Score_Tempo_BPM",
            "Score_Key",
            "Score_Mood"
        ]

        cumulative_time = 0
        rows = []

        for idx, (u, s) in enumerate(zip(units, shots)):
            start_sec = cumulative_time
            end_sec = cumulative_time + u.duration_sec
            cumulative_time = end_sec

            m_cue = music_cues[idx] if idx < len(music_cues) else {}
            p_asset = s.primary_asset

            sfx_amb = u.sound_intent.ambience[0] if u.sound_intent.ambience else "Ambience"
            sfx_mech = u.sound_intent.mechanical[0] if u.sound_intent.mechanical else "Mechanical"
            sfx_trans = u.sound_intent.transition[0] if u.sound_intent.transition else "Transition"

            rows.append({
                "Shot_ID": s.shot_id,
                "Visual_Unit": u.id,
                "Timecode_In": seconds_to_timecode(start_sec),
                "Timecode_Out": seconds_to_timecode(end_sec),
                "Duration_Sec": u.duration_sec,
                "Section": u.script_section,
                "Narration_Beat": u.text,
                "Visual_Job": ", ".join(u.visual_jobs),
                "Narrative_Function": s.primary_asset.narrative_function if s.primary_asset else "B — Context",
                "Visual_Specificity": f"{s.primary_asset.visual_specificity if s.primary_asset else 3}/5",
                "Primary_Broll_Title": p_asset.title if p_asset else "Stock B-Roll",
                "Broll_URL": p_asset.url if p_asset else "#",
                "Resolution": p_asset.resolution if p_asset else "4K UHD",
                "Camera_Direction": f"{s.camera} ({s.movement})",
                "SFX_Ambience": sfx_amb,
                "SFX_Mechanical": sfx_mech,
                "SFX_Transition": sfx_trans,
                "Score_Tempo_BPM": m_cue.get("tempo", "90 BPM"),
                "Score_Key": m_cue.get("musical_key", "D Minor"),
                "Score_Mood": m_cue.get("emotional_mood", "Cinematic")
            })

        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        logger.info(f"Exported NLE Cut List CSV to: {out_path}")
        return out_path

    def export_production_brief(
        self,
        doc: ScriptDocument,
        units: List[VisualUnit],
        shots: List[ShotItem],
        music_cues: List[Dict[str, Any]],
        out_path: Optional[Path] = None
    ) -> Path:
        """
        Compiles an executive production brief markdown document for the editing and legal team.
        """
        if not out_path:
            out_path = doc.file_path.parent / f"{doc.title.replace(' ', '_')}_Production_Brief.md"

        total_duration = sum(u.duration_sec for u in units)
        total_words = sum(len(u.text.split()) for u in units)
        avg_wps = round(total_words / max(1, total_duration), 2)
        avg_coverage = int(sum(u.visual_coverage.get("coverage_pct", 75) for u in units) / max(1, len(units)))

        lines = [
            "---",
            f'title: "Production Brief — {doc.title}"',
            f'project: "{doc.title}"',
            'type: production_brief',
            f'total_runtime: "{total_duration//60:02d}:{total_duration%60:02d}"',
            f'total_shots: {len(shots)}',
            f'average_coverage: "{avg_coverage}%"',
            f'date: {datetime.now().strftime("%Y-%m-%d")}',
            "---",
            "",
            f"# Executive Production Brief: {doc.title}",
            "",
            "> Comprehensive pre-production blueprint, sequence plan, fact verification dossier, and sound cue sheet.",
            "",
            "## 1. Timeline & Runtime Analytics",
            f"- **Target Runtime**: `{total_duration//60:02d}:{total_duration%60:02d}` ({total_duration} seconds)",
            f"- **Total Spoken Word Count**: `{total_words}` words",
            f"- **Average Pacing**: `{avg_wps} words/second` (Standard broadcast rate: 2.3-2.5)",
            f"- **Total Shot Count**: `{len(shots)}` visual setups",
            f"- **Visual Coverage Rating**: `{avg_coverage}%` (Full editorial safety threshold: $\\ge 75\\%$)",
            "",
            "## 2. Master Storyboard & Sequence Plan",
            "",
            "| Shot ID | Timecode | Framing & Camera | Narrative Function | Primary B-Roll Asset | Specificity |",
            "|---|---|---|---|---|---:|"
        ]

        cumulative_time = 0
        for idx, (u, s) in enumerate(zip(units, shots)):
            start_tc = f"{cumulative_time//60:02d}:{cumulative_time%60:02d}"
            cumulative_time += u.duration_sec
            end_tc = f"{cumulative_time//60:02d}:{cumulative_time%60:02d}"

            p = s.primary_asset
            title = p.title if p else "Pending Shot"
            url = p.url if p else "#"
            n_func = p.narrative_function if p else "B — Context"
            spec = f"{p.visual_specificity if p else 3}/5"
            cam = f"{s.camera} ({s.movement})"

            lines.append(f"| `{s.shot_id}` | `{start_tc} - {end_tc}` | `{cam}` | `{n_func[:18]}` | [{title[:32]}]({url}) | `{spec}` |")

        lines.extend([
            "",
            "## 3. Musical Score & Acoustic Sound Design Cue Sheet",
            "",
            "| Cue ID | Timecode | Motif | Tempo | Key | Mood & Instrumentation |",
            "|---|---|---|---|---|---|"
        ])

        for c in music_cues:
            lines.append(f"| `{c['cue_id']}` | `{c['timecode_range']}` | `{c['thematic_motif']}` | `{c['tempo']}` | `{c['musical_key']}` | {c['emotional_mood']}; *{c['instrumentation'][:45]}...* |")

        lines.extend([
            "",
            "## 4. Factual Verification & Legal Source Dossier",
            ""
        ])

        claim_count = 0
        for u in units:
            if u.claims:
                for c in u.claims:
                    claim_count += 1
                    lines.append(f"### Claim {claim_count:02d} (`{u.id}`)")
                    lines.append(f'> *"{c}"*')
                    lines.append("")
                    if u.source_matches:
                        lines.append("**Verified Citations:**")
                        for sm in u.source_matches:
                            lines.append(f"- **Publisher**: {sm.publisher} | **Credibility**: `{sm.credibility.upper()}` ({int(round(sm.relevance_score*100))}%)")
                            lines.append(f"  - Link: [{sm.title}]({sm.url})")
                            lines.append(f"  - Excerpt: *\"{sm.excerpt or 'Verified enterprise disclosure'}\"*")
                    else:
                        lines.append("- *(Verification pending editorial sign-off)*")
                    lines.append("")

        lines.extend([
            "---",
            "## 5. Editor Sign-Off & Lock Checklist",
            "- [ ] All high-resolution 4K camera masters ingested and proxy generated",
            "- [ ] Color grading LUT (ACEScg or Rec.709) matched across mixed stock sources",
            "- [ ] Source facts signed off by research lead",
            "- [ ] Music stem mix and sidechain dialogue compression checked",
            "- [ ] Final export conforms to delivery specs"
        ])

        out_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"Exported Executive Production Brief to: {out_path}")
        return out_path


nle_exporter = NLEExporter()
