"""
Production OS Command-Line Interface and Workflow Orchestrator.
Executes individual pipeline stages or the full end-to-end production automation.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from core.config import config
from core.logger import logger, console
from pipeline.script import script_parser
from pipeline.visual import visual_analyzer
from pipeline.sfx import sfx_analyzer
from pipeline.footage import footage_pipeline
from pipeline.source import source_pipeline
from pipeline.shots import shot_planner
from artistic_logic.music_engine import music_score_engine
from output.markdown import markdown_writer
from output.export_nle import nle_exporter
from providers.local_media import local_media_provider


def run_pipeline(script_path: Path):
    """Executes the full end-to-end production pipeline on a target script note."""
    console.print(Panel.fit(f"[bold cyan]RUNNING PRODUCTION OS PIPELINE[/bold cyan]\nTarget: {script_path.name}", border_style="cyan"))

    # 1. Parse Script Note
    with console.status("[bold green]Parsing Markdown script and YAML frontmatter..."):
        doc = script_parser.parse_file(script_path)
    console.print(f"[bold green][OK][/bold green] Parsed [bold]{len(doc.sections)}[/bold] script sections.")

    # 2. Visual Intent & Semantic Analysis
    with console.status("[bold green]Deconstructing narrative into physical Visual Intent..."):
        for unit in doc.visual_units:
            visual_analyzer.analyze_unit(unit)
    console.print(f"[bold green][OK][/bold green] Derived Visual Intent for [bold]{len(doc.visual_units)}[/bold] Visual Units.")

    # 3. SFX and Sound Intent
    with console.status("[bold green]Mapping acoustic sound layers (Ambience, Foley, Risers, Impacts)..."):
        for unit in doc.visual_units:
            sfx_analyzer.analyze_sound_intent(unit)
    console.print(f"[bold green][OK][/bold green] Generated SFX cues for [bold]{len(doc.visual_units)}[/bold] units.")

    # 4. B-Roll Footage Discovery with Artistic Logic & 9-Factor Editorial Scoring
    with console.status("[bold green]Running Artistic Interpretation & 9-Factor Editorial Scoring with Sequence Logic..."):
        prev_shot_meta = None
        for idx, unit in enumerate(doc.visual_units):
            footage_pipeline.find_broll_for_unit(unit, previous_shot_meta=prev_shot_meta, beat_index=idx+1)
            if unit.primary_broll:
                prev_shot_meta = {
                    "framing": unit.visual_intent.camera,
                    "subject": unit.visual_strategy.get("literal", [""])[0],
                    "motion": unit.visual_intent.movement
                }
    console.print("[bold green][OK][/bold green] Ranked B-Roll recommendations with 9-Factor Editorial Scoring & Sequence Logic.")

    # 5. Factual Claim Extraction & Source Validation
    with console.status("[bold green]Validating claims, writing Source Notes & Research Inbox triage cards..."):
        for unit in doc.visual_units:
            source_pipeline.process_claims_for_unit(unit)
    console.print("[bold green][OK][/bold green] Generated permanent Source Notes and Research Inbox items.")

    # 6. Shot Planner Generation
    with console.status("[bold green]Building individual Shot Cards and Master Shot Planner..."):
        shots = shot_planner.create_shots_from_units(doc.visual_units, doc.title)
    console.print(f"[bold green][OK][/bold green] Created [bold]{len(shots)}[/bold] production shots in 05_SHOTS/B-Roll/.")

    # 7. Musical Score & Emotional Trajectory
    with console.status("[bold green]Composing musical pacing, BPM, and instrumentation cues..."):
        music_cues = music_score_engine.analyze_score_trajectory(doc.visual_units)
    console.print(f"[bold green][OK][/bold green] Generated [bold]{len(music_cues)}[/bold] dynamic score cues.")

    # 8. Write Back to Script Note
    with console.status("[bold green]Writing production-ready B-Roll, SFX, Score, and Sources back to Markdown..."):
        updated_file = markdown_writer.update_script_with_production_data(doc, doc.visual_units, music_cues)
    console.print(f"[bold green][OK][/bold green] Script successfully updated: [bold green]{updated_file.name}[/bold green]")

    # 9. Export NLE Cut List CSV & Executive Production Brief
    with console.status("[bold green]Generating DaVinci/Premiere NLE Cut List CSV & Executive Brief..."):
        csv_file = nle_exporter.export_csv(doc, doc.visual_units, shots, music_cues)
        brief_file = nle_exporter.export_production_brief(doc, doc.visual_units, shots, music_cues)
    console.print(f"[bold green][OK][/bold green] Exported NLE Cut List: [bold cyan]{csv_file.name}[/bold cyan]")
    console.print(f"[bold green][OK][/bold green] Exported Executive Brief: [bold cyan]{brief_file.name}[/bold cyan]")

    # Display Summary Table
    table = Table(title="Production OS — Artistic Logic & Editorial Summary", border_style="green")
    table.add_column("Unit ID", style="cyan", no_wrap=True)
    table.add_column("Section", style="white")
    table.add_column("Visual Job & Function", style="magenta")
    table.add_column("Spec", justify="center", style="blue")
    table.add_column("Top B-Roll Recommendation", style="yellow")
    table.add_column("Score", justify="right", style="green")
    table.add_column("Coverage", justify="right", style="cyan")

    for u in doc.visual_units:
        primary_title = u.primary_broll.title if u.primary_broll else "N/A"
        score = f"{int(round((u.primary_broll.relevance_score if u.primary_broll else 0.85)*100))}%"
        job_func = f"{u.visual_jobs[0] if u.visual_jobs else 'context'} / {u.narrative_functions[0][:1] if u.narrative_functions else 'B'}"
        spec = f"{u.primary_broll.visual_specificity if u.primary_broll else 3}/5"
        cov = f"{u.visual_coverage.get('coverage_pct', 75)}%"
        table.add_row(u.id, u.script_section[:18], job_func, spec, primary_title[:28], score, cov)

    console.print(table)


def create_new_script(title: str, project: str, format_type: str = "youtube"):
    target_dir = config.scripts_dir / "Draft"
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{title.replace(' ', '_')}.md"
    file_path = target_dir / filename

    content = f"""---
type: script
project: "{project}"
status: draft
format: {format_type}
duration: 05:00
language: en
created: {datetime.now().strftime('%Y-%m-%d')}
research_status: pending
broll_status: pending
source_status: pending
---

# {title}

## 01 — Hook
> Enter your hook narration line here.

### Visual Intent
- Visual concept 1
- Visual concept 2

### B-Roll
- [ ] B-roll target 1

### Sources
- [ ] Source claim to verify

## 02 — Context & Core Problem
> Narration line explaining the background or conflict.

### Visual Intent
- Contextual concept 1

### B-Roll
- [ ] B-roll shot 2

### Sources
- [ ] Fact check item

## 03 — Climax / Revelation
> The pivotal insight or factual data point.

### Visual Intent
- Climax visual

### B-Roll
- [ ] Climax b-roll

### Sources
- [ ] Statistical source
"""
    file_path.write_text(content, encoding="utf-8")
    console.print(f"[bold green][OK] Created new script template at:[/bold green] {file_path}")
    return file_path


def main():
    parser = argparse.ArgumentParser(description="Obsidian Production OS Pipeline CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Pipeline command (full run)
    p_pipe = subparsers.add_parser("pipeline", help="Run full end-to-end pipeline on script")
    p_pipe.add_argument("script", type=str, help="Path to script markdown note")

    # Analyze command
    p_ana = subparsers.add_parser("analyze", help="Extract visual units and visual intent")
    p_ana.add_argument("script", type=str, help="Path to script markdown note")

    # B-roll command
    p_broll = subparsers.add_parser("broll", help="Search and rank B-roll footage")
    p_broll.add_argument("script", type=str, help="Path to script markdown note")

    # SFX command
    p_sfx = subparsers.add_parser("sfx", help="Search and match SFX cues")
    p_sfx.add_argument("script", type=str, help="Path to script markdown note")

    # News command
    p_news = subparsers.add_parser("news", help="Verify claims and create source notes")
    p_news.add_argument("script", type=str, help="Path to script markdown note")

    # Shots command
    p_shots = subparsers.add_parser("shots", help="Build shot list and shot planner")
    p_shots.add_argument("script", type=str, help="Path to script markdown note")

    # Music command
    p_mus = subparsers.add_parser("music", help="Analyze narrative arc and compose score cues")
    p_mus.add_argument("script", type=str, help="Path to script markdown note")

    # Export command
    p_exp = subparsers.add_parser("export", help="Export DaVinci/Premiere CSV Cut List & Executive Brief")
    p_exp.add_argument("script", type=str, help="Path to script markdown note")

    # New script
    p_new = subparsers.add_parser("new-script", help="Scaffold a new production script")
    p_new.add_argument("--title", required=True, help="Title of script")
    p_new.add_argument("--project", required=True, help="Project name")
    p_new.add_argument("--format", default="youtube", help="Video format")

    # Index local media
    p_idx = subparsers.add_parser("index-local", help="Scan and index local asset library")
    p_idx.add_argument("--dir", type=str, help="Custom folder path to scan")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command in ["pipeline", "export", "music", "analyze", "broll", "sfx", "news", "shots"]:
        script_file = Path(args.script)
        if not script_file.is_absolute():
            script_file = config.vault_root / script_file
        if not script_file.exists():
            console.print(f"[bold red]Error: Script file not found: {script_file}[/bold red]")
            sys.exit(1)
        run_pipeline(script_file)

    elif args.command == "new-script":
        create_new_script(args.title, args.project, args.format)

    elif args.command == "index-local":
        scan_dir = [Path(args.dir)] if args.dir else None
        count = local_media_provider.build_index(scan_dir)
        console.print(f"[bold green][OK] Successfully indexed {count} local media assets.[/bold green]")


if __name__ == "__main__":
    main()
