"""
Shot Planner and Pre-Production Breakdown Engine.
Generates machine-readable Shot cards and the master visual Shot Planner.
"""

from typing import List, Dict, Any
from pathlib import Path
import yaml
from core.models import VisualUnit, ShotItem
from scoring.relevance import render_progress_bar
from core.config import config
from core.logger import logger


class ShotPlanner:
    def create_shots_from_units(self, units: List[VisualUnit], project_name: str) -> List[ShotItem]:
        shots = []
        for idx, u in enumerate(units):
            shot_id = f"SH-{idx+1:03d}"
            primary_asset = u.primary_broll
            vis_desc = primary_asset.title if primary_asset else (u.visual_intent.primary[0] if u.visual_intent.primary else u.script_section)

            shot = ShotItem(
                shot_id=shot_id,
                visual_unit_id=u.id,
                duration_sec=u.duration_sec,
                priority="high" if idx < 3 else "medium",
                shot_type="b-roll",
                visual_description=vis_desc,
                camera=u.visual_intent.camera,
                movement=u.visual_intent.movement,
                transition="cut" if idx > 0 else "fade-in",
                source=primary_asset.source if primary_asset else "stock",
                primary_asset=primary_asset,
                status="planned"
            )
            shots.append(shot)

            # Write individual shot note
            self.write_shot_note(shot, u, project_name)

        # Write Master Shot Planner
        self.write_master_shot_planner(shots, units, project_name)
        return shots

    def write_shot_note(self, shot: ShotItem, unit: VisualUnit, project_name: str) -> Path:
        target_dir = config.shots_dir / "B-Roll"
        target_dir.mkdir(parents=True, exist_ok=True)
        import re
        safe_desc = re.sub(r'[\\/*?:"<>|]', "", shot.visual_description)
        safe_desc = re.sub(r"\s+", " ", safe_desc).strip()
        filename = f"{shot.shot_id} - {safe_desc[:40]}.md"
        file_path = target_dir / filename

        frontmatter = {
            "type": "shot",
            "shot_id": shot.shot_id,
            "project": project_name,
            "visual_unit": unit.id,
            "duration": shot.duration_sec,
            "priority": shot.priority,
            "shot_type": shot.shot_type,
            "camera": shot.camera,
            "movement": shot.movement,
            "transition": shot.transition,
            "status": shot.status,
            "relevance": int(round((shot.primary_asset.relevance_score if shot.primary_asset else 0.85) * 100))
        }

        progress = render_progress_bar(frontmatter["relevance"])
        sfx_name = unit.sfx_matches[0].title if unit.sfx_matches else "Default Ambience"
        news_name = unit.editorial_news.title if unit.editorial_news else "Supporting Context"

        content = f"""---
{yaml.dump(frontmatter, sort_keys=False).strip()}
---

# Shot {shot.shot_id} — {shot.visual_description}

```
┌────────────────────────────────────────────────────────┐
│ {shot.shot_id} — {unit.script_section[:35].ljust(44)} │
│                                                        │
│ "{unit.text[:42]}..."                                  │
│                                                        │
│ {progress}                           │
│                                                        │
│ 🎥 Footage : {shot.visual_description[:38].ljust(40)} │
│ 🔊 SFX     : {sfx_name[:38].ljust(40)} │
│ 📰 Source  : {news_name[:38].ljust(40)} │
│                                                        │
│ Status: [{shot.status.upper()}] | Duration: {shot.duration_sec}s | Type: {shot.shot_type}   │
└────────────────────────────────────────────────────────┘
```

## Director Notes & Cinematic Direction
- **Camera Setup**: `{shot.camera}`
- **Camera Movement**: `{shot.movement}`
- **Lighting Mood**: `{unit.visual_intent.lighting}`
- **Transition In/Out**: `{shot.transition}`

## Script Alignment
> {unit.text}

## Asset Specifications
- **Primary Asset**: {f"[{shot.primary_asset.title}]({shot.primary_asset.url})" if shot.primary_asset else "Pending Selection"}
- **License**: `{shot.primary_asset.license if shot.primary_asset else 'N/A'}`
- **Resolution**: `{shot.primary_asset.resolution if shot.primary_asset else '4K'}`
- **Source Platform**: `{shot.source}`
"""
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def write_master_shot_planner(self, shots: List[ShotItem], units: List[VisualUnit], project_name: str) -> Path:
        target_path = config.shots_dir / "Shot_Planner.md"
        
        cards = []
        for s, u in zip(shots, units):
            score_pct = int(round((s.primary_asset.relevance_score if s.primary_asset else 0.85) * 100))
            bar = render_progress_bar(score_pct)
            sfx_term = u.sound_intent.ambience[0] if u.sound_intent.ambience else "Ambience"
            source_term = u.editorial_news.title if u.editorial_news else "Source verification"

            card = f"""### {s.shot_id} — [[{s.shot_id} - {s.visual_description[:35]}|{s.visual_description}]]
> **Narration**: "{u.text}"

- **Relevance**: `{bar}`
- 🎥 **Footage**: [{s.visual_description}]({s.primary_asset.url if s.primary_asset else '#'}) (`{s.source}`)
- 🔊 **SFX**: `{sfx_term}`
- 📰 **Source**: `{source_term[:50]}`
- ⏱️ **Duration**: `{s.duration_sec}s` | **Camera**: `{s.camera}` | **Status**: `{s.status}`

---
"""
            cards.append(card)

        content = f"""---
type: shot_planner
project: "{project_name}"
total_shots: {len(shots)}
total_duration: {sum(s.duration_sec for s in shots)}s
updated: 2026-09-24
---

# Master Shot Planner — {project_name}

> Production storyboard and shot-by-shot asset mapping board.

## Visual Shot Deck

{"".join(cards)}

## Shot Database Query (Dataview)

```dataview
TABLE duration AS "Duration (s)", priority AS "Priority", shot_type AS "Type", camera AS "Camera", relevance AS "Relevance %", status AS "Status"
FROM "05_SHOTS/B-Roll"
WHERE type = "shot"
SORT shot_id ASC
```
"""
        target_path.write_text(content, encoding="utf-8")
        return target_path


shot_planner = ShotPlanner()
