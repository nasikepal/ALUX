# ALUX — OBSIDIAN PRODUCTION OS

> **Enterprise-Grade Video Pre-Production Command Center & Automation Engine**
> Converts narrative scripts into structured Visual Units, queries local & external footage archives with 6-factor relevance scoring, maps acoustic sound design, and verifies claims into permanent citation notes.

---

## 1. System Architecture

The vault operates across 5 decoupled layers:

```
┌────────────────────────────────────────────────────────┐
│                   LAYER 1 — OBSIDIAN                   │
│   • Dashboard.md (Command Center)                      │
│   • 02_SCRIPTS/ (Machine-readable script notes)        │
│   • 05_SHOTS/ (Shot planner & storyboard deck)         │
│   • 06_SOURCES/ & 03_RESEARCH/ (Citation notes & inbox)│
└──────────────────────────┬─────────────────────────────┘
                           │ QuickAdd / CLI Bridge
                           ▼
┌────────────────────────────────────────────────────────┐
│               LAYER 2 — AUTOMATION ENGINE              │
│   • Python 3.14 (.venv) CLI in 08_AUTOMATION/Scripts/   │
│   • Markdown parser & YAML frontmatter updater         │
│   • 6-Factor Relevance Scoring Engine                  │
└──────────────────────────┬─────────────────────────────┘
                           │ Semantic Decomposition
                           ▼
┌────────────────────────────────────────────────────────┐
│                   LAYER 3 — AI / NLP                   │
│   • Script Segmentation (Visual Units VU-001..N)       │
│   • Physical Visual Intent (Subject, Camera, Lighting) │
│   • Acoustic Sound Intent (Ambience, Foley, Hits)      │
└──────────────────────────┬─────────────────────────────┘
                           │ Asset Resolution
              ┌────────────┴────────────┐
              ▼                         ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│ LAYER 5 — LOCAL MEDIA     │ │ LAYER 4 — WEB SOURCES    │
│ • D:\MEDIA_LIBRARY        │ │ • Wikimedia Commons      │
│ • 04_MEDIA/ (In-house)    │ │ • Internet Archive       │
│ • Local JSON Index        │ │ • Pexels & Pixabay       │
│ • Zero API cost priority  │ │ • Reuters & Bloomberg    │
└───────────────────────────┘ └──────────────────────────┘
```

---

## 2. Directory Hierarchy

```
ALUX/
├── 00_SYSTEM/
│   ├── Dashboard.md        # Command center with Dataview tables & quick launchers
│   ├── Automation.md       # Pipeline architecture & CLI syntax reference
│   ├── Settings.md         # Relevance scoring weights & local asset paths
│   └── Workflows.md        # Visual SOP and production stage guidelines
├── 01_PROJECTS/
│   ├── Active/             # Ongoing project command files (e.g. The_Rise_of_AI.md)
│   ├── Archive/            # Completed production records
│   └── Templates/          # Project scaffolds
├── 02_SCRIPTS/
│   ├── Draft/              # Scripts in progress (e.g. The_Rise_of_AI.md)
│   ├── Research/           # Fact check & visual unit development
│   ├── Production/         # Locked scripts with approved B-roll & SFX
│   └── Published/          # Delivered and uploaded video records
├── 03_RESEARCH/
│   ├── _INBOX/             # Triage inbox for discovered sources (Human-in-the-loop)
│   ├── News/               # Journalistic reports
│   ├── Articles/           # Long-form essays & analyses
│   ├── References/         # Historical benchmarks
│   ├── People/             # Biographies & key figures
│   ├── Companies/          # Corporate intelligence dossiers
│   └── Topics/             # Thematic research files
├── 04_MEDIA/
│   ├── Footage/            # Master raw/ingested B-roll
│   ├── SFX/                # In-house sound design & Foley library
│   ├── Music/              # Scored themes & background tracks
│   ├── Images/             # Stills, photographs, and figures
│   └── Graphics/           # Motion design assets & 3D models
├── 05_SHOTS/
│   ├── B-Roll/             # Individual shot cards (SH-001, SH-002...)
│   ├── A-Roll/             # Main presenter / interview clips
│   ├── Motion/             # Kinetic graphics & title sequences
│   ├── Archive/            # Unused shot candidates
│   └── Shot_Planner.md     # Master storyboard deck & Dataview shot table
├── 06_SOURCES/
│   ├── News/               # Permanent verified source notes
│   ├── YouTube/            # Video reference links
│   ├── Websites/           # Web citations
│   ├── Papers/             # Academic literature
│   └── Social/             # Social media & public statements
├── 07_DATABASE/
│   ├── People/             # Structured entity cards
│   ├── Companies/          # Capitalization & corporate entities
│   ├── Topics/             # Subject matter graphs
│   ├── Locations/          # Geographic sites & facilities
│   └── Keywords/           # Tag indices
├── 08_AUTOMATION/
│   ├── Scripts/            # Python 3.14 pipeline engine
│   │   ├── core/           # Config, models, logger, errors
│   │   ├── pipeline/       # Script, visual, footage, sfx, source, shots
│   │   ├── providers/      # Local media, Wikimedia, Archive, Stock, News
│   │   ├── scoring/        # 6-factor relevance engine
│   │   ├── output/         # Markdown writer & frontmatter updater
│   │   ├── cli.py          # Unified CLI orchestrator
│   │   └── run_pipeline_quickadd.js  # QuickAdd Obsidian user script
│   ├── Search/             # Local asset cache (local_media_index.json)
│   └── Logs/               # Persistent run logs
├── 99_TEMPLATES/
│   ├── Script_Template.md
│   ├── Project_Template.md
│   ├── Visual_Unit_Template.md
│   ├── Shot_Template.md
│   ├── Source_Template.md
│   ├── Research_Inbox_Template.md
│   └── SFX_Asset_Template.md
├── run_pipeline.bat        # 1-Click Windows launcher for active script
├── create_script.bat       # Interactive script scaffolder
└── index_media.bat         # Re-indexes in-house media library
```

---

## 3. Mathematical Relevance Scoring Engine

Candidate footage and audio assets are evaluated using a 6-factor composite score:

$$S = 100 \times \left( 0.30 \cdot S_{\text{vis}} + 0.25 \cdot S_{\text{script}} + 0.15 \cdot S_{\text{entity}} + 0.10 \cdot S_{\text{temporal}} + 0.10 \cdot S_{\text{geo}} + 0.10 \cdot S_{\text{source}} \right)$$

1. **$S_{\text{vis}}$ (Visual Similarity - 30%)**: Overlap between asset title/tags and derived physical visual intent (primary, secondary, abstract).
2. **$S_{\text{script}}$ (Script Relevance - 25%)**: Contextual alignment with spoken narration line.
3. **$S_{\text{entity}}$ (Entity Match - 15%)**: Specific detection of named companies, hardware, or people.
4. **$S_{\text{temporal}}$ (Temporal Relevance - 10%)**: Verification of chronological alignment (e.g., 2026 frontier vs historical archival).
5. **$S_{\text{geo}}$ (Geographic Relevance - 10%)**: Verification of physical site or universal neutral setting.
6. **$S_{\text{source}}$ (Source Quality - 10%)**: Asset resolution (4K vs 1080p), license (commercial royalty-free vs editorial), and framerate.

---

## 4. Operational Execution Guide

### Method A: 1-Click Windows Launcher
Double-click `run_pipeline.bat` from the root of the vault.
- Press `Enter` to run on the default flagship script (`02_SCRIPTS/Draft/The_Rise_of_AI.md`) or type the relative path to any script in `02_SCRIPTS/`.

### Method B: Obsidian QuickAdd Hotkey
Inside Obsidian:
1. Open any script in `02_SCRIPTS/Draft/`.
2. Press `Ctrl + P` -> Select `QuickAdd: Run Production OS Pipeline`.
3. The script executes asynchronously, displays notification banners, and updates the note in place.

### Method C: Command Line Interface (CLI)
Using the vault's embedded Python runtime:
```powershell
# Run full end-to-end pipeline
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" pipeline "02_SCRIPTS\Draft\The_Rise_of_AI.md"

# Scaffold a new script
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" new-script --title "Project Title" --project "Project Name"

# Re-index internal media library
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" index-local
```
