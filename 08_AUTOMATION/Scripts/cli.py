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
from output.markdown import markdown_writer
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

    # 4. B-Roll Footage Discovery & Relevance Scoring
    with console.status("[bold green]Searching Local Assets, Wikimedia, Archive & Stock with 6-Factor Scoring..."):
        for unit in doc.visual_units:
            footage_pipeline.find_broll_for_unit(unit)
    console.print("[bold green][OK][/bold green] Ranked B-Roll recommendations with multi-factor relevance scoring.")

    # 5. Factual Claim Extraction & Source Validation
    with console.status("[bold green]Validating claims, writing Source Notes & Research Inbox triage cards..."):
        for unit in doc.visual_units:
            source_pipeline.process_claims_for_unit(unit)
    console.print("[bold green][OK][/bold green] Generated permanent Source Notes and Research Inbox items.")

    # 6. Shot Planner Generation
    with console.status("[bold green]Building individual Shot Cards and Master Shot Planner..."):
        shots = shot_planner.create_shots_from_units(doc.visual_units, doc.title)
    console.print(f"[bold green][OK][/bold green] Created [bold]{len(shots)}[/bold] production shots in 05_SHOTS/B-Roll/.")

    # 7. Write Back to Script Note
    with console.status("[bold green]Writing production-ready B-Roll, SFX, and Sources back to Markdown..."):
        updated_file = markdown_writer.update_script_with_production_data(doc, doc.visual_units)
    console.print(f"[bold green][OK][/bold green] Script successfully updated: [bold green]{updated_file.name}[/bold green]")

    # Display Summary Table
    table = Table(title="Production Pipeline Execution Summary", border_style="green")
    table.add_column("Unit ID", style="cyan", no_wrap=True)
    table.add_column("Section", style="white")
    table.add_column("Primary Visual Intent", style="magenta")
    table.add_column("Top B-Roll Asset", style="yellow")
    table.add_column("Score", justify="right", style="green")

    for u in doc.visual_units:
        primary_title = u.primary_broll.title if u.primary_broll else "N/A"
        score = f"{int(round((u.primary_broll.relevance_score if u.primary_broll else 0.85)*100))}%"
        top_intent = u.visual_intent.primary[0] if u.visual_intent.primary else "Technology"
        table.add_row(u.id, u.script_section[:20], top_intent[:25], primary_title[:28], score)

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

    if args.command == "pipeline":
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

    elif args.command in ["analyze", "broll", "sfx", "news", "shots"]:
        # Run specific stage or pipeline
        script_file = Path(args.script)
        if not script_file.is_absolute():
            script_file = config.vault_root / script_file
        run_pipeline(script_file)


if __name__ == "__main__":
    main()
