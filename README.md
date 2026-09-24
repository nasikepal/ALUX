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
│   • SCRIPT PARSER (Visual Units VU-001..N)             │
│   • ARTISTIC LOGIC ENGINE (6-Level Hierarchy)          │
│     - Visual Job (13 types) & Narrative Function (A-J) │
│     - Conceptual & Metaphorical Transduction           │
│     - DO NOT MATCH Guardrails (Anti-Pattern Filter)    │
│     - Multi-Tier Search Matrix (Literal..Detail)       │
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
│   ├── Dashboard.md               # Command center with Dataview tables & quick launchers
│   ├── ARTISTIC_LOGIC_ENGINE.md   # Canonical artistic reasoning & editorial specification
│   ├── Automation.md              # Pipeline architecture & CLI syntax reference
│   ├── Settings.md                # 9-Factor scoring weights & penalty configs
│   └── Workflows.md               # Visual SOP and production stage guidelines
├── 01_PROJECTS/
│   ├── Active/                    # Ongoing project command files (e.g. The_Rise_of_AI.md)
│   ├── Archive/                   # Completed production records
│   └── Templates/                 # Project scaffolds
├── 02_SCRIPTS/
│   ├── Draft/                     # Scripts in progress (e.g. The_Rise_of_AI.md)
│   ├── Research/                  # Fact check & visual unit development
│   ├── Production/                # Locked scripts with approved B-roll & SFX
│   └── Published/                 # Delivered and uploaded video records
├── 03_RESEARCH/
│   ├── _INBOX/                    # Triage inbox for discovered sources (Human-in-the-loop)
│   ├── News/                      # Journalistic reports
│   ├── Articles/                  # Long-form essays & analyses
│   ├── References/                # Historical benchmarks
│   ├── People/                    # Biographies & key figures
│   ├── Companies/                 # Corporate intelligence dossiers
│   └── Topics/                    # Thematic research files
├── 04_MEDIA/
│   ├── Footage/                   # Master raw/ingested B-roll
│   ├── SFX/                       # In-house sound design & Foley library
│   ├── Music/                     # Scored themes & background tracks
│   ├── Images/                    # Stills, photographs, and figures
│   └── Graphics/                  # Motion design assets & 3D models
├── 05_SHOTS/
│   ├── B-Roll/                    # Individual shot cards (SH-001, SH-002...)
│   ├── A-Roll/                    # Main presenter / interview clips
│   ├── Motion/                    # Kinetic graphics & title sequences
│   ├── Archive/                   # Unused shot candidates
│   └── Shot_Planner.md            # Master storyboard deck & Dataview shot table
├── 06_SOURCES/
│   ├── News/                      # Permanent verified source notes
│   ├── YouTube/                   # Video reference links
│   ├── Websites/                  # Web citations
│   ├── Papers/                    # Academic literature
│   └── Social/                    # Social media & public statements
├── 07_DATABASE/
│   ├── People/                    # Structured entity cards
│   ├── Companies/                 # Capitalization & corporate entities
│   ├── Topics/                    # Subject matter graphs
│   ├── Locations/                 # Geographic sites & facilities
│   └── Keywords/                  # Tag indices
├── 08_AUTOMATION/
│   ├── Scripts/                   # Python 3.14 pipeline engine
│   │   ├── core/                  # Config, models, logger, errors
│   │   ├── artistic_logic/        # Visual interpreter, narrative classifier, metaphor engine, sequence logic, coverage, music engine
│   │   ├── pipeline/              # Script, visual, footage, sfx, source, shots
│   │   ├── providers/             # Local media, Wikimedia, Archive, Stock, News
│   │   ├── scoring/               # 9-Factor editorial relevance engine
│   │   ├── output/                # Markdown writer, NLE Cut List CSV & Production Brief exporter
│   │   ├── cli.py                 # Unified CLI orchestrator
│   │   └── run_pipeline_quickadd.js  # QuickAdd Obsidian user script
│   ├── Search/                    # Local asset cache (local_media_index.json)
│   └── Logs/                      # Persistent run logs
├── 99_TEMPLATES/
│   ├── Script_Template.md
│   ├── Project_Template.md
│   ├── Visual_Unit_Template.md
│   ├── Shot_Template.md
│   ├── Source_Template.md
│   ├── Research_Inbox_Template.md
│   └── SFX_Asset_Template.md
├── run_pipeline.bat               # 1-Click Windows launcher for active script
├── create_script.bat              # Interactive script scaffolder
└── index_media.bat                # Re-indexes in-house media library
```

---

## 3. Mathematical 9-Factor Editorial Relevance Scoring

Candidate footage and audio assets are evaluated using a 9-factor composite formula:

$$S = 100 \times \left( \begin{aligned}
& 0.20 \cdot S_{\text{semantic}} + 0.15 \cdot S_{\text{narrative}} + 0.15 \cdot S_{\text{specificity}} \\
+ & 0.15 \cdot S_{\text{artistic}} + 0.10 \cdot S_{\text{cinematic}} + 0.10 \cdot S_{\text{temporal}} \\
+ & 0.05 \cdot S_{\text{geo}} + 0.05 \cdot S_{\text{utility}} + 0.05 \cdot S_{\text{source}}
\end{aligned} \right) - P_{\text{redundancy}} - P_{\text{avoid}}$$

1. **$S_{\text{semantic}}$ (Semantic Relevance - 20%)**: Script vocabulary and subject overlap.
2. **$S_{\text{narrative}}$ (Narrative Function - 15%)**: Fulfills designated visual job (Establishing, Proof, Context, etc.).
3. **$S_{\text{specificity}}$ (Visual Specificity - 15%)**: Graded 0 to 5 (0=generic stock slop, 5=exact physical representation).
4. **$S_{\text{artistic}}$ (Artistic Interpretation - 15%)**: Conceptual & metaphorical transduction alignment.
5. **$S_{\text{cinematic}}$ (Cinematic Compatibility - 10%)**: Camera framing, movement, and contrast lighting.
6. **$S_{\text{temporal}}$ (Temporal Relevance - 10%)**: Chronological era alignment.
7. **$S_{\text{geo}}$ (Geographic Relevance - 5%)**: Regional and physical site fidelity.
8. **$S_{\text{utility}}$ (Editorial Utility - 5%)**: Clean framing, typography room, duration $\ge 4s$.
9. **$S_{\text{source}}$ (Source Quality - 5%)**: Resolution (4K UHD), commercial license grade.

### Penalties
- **$P_{\text{redundancy}}$**: Deduces up to -30% if repeating previous shot's subject and framing scale.
- **$P_{\text{avoid}}$**: Deduces -40% if candidate matches visual anti-pattern tropes.

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
# Run full end-to-end pipeline (Script update + Cut List CSV + Executive Brief)
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" pipeline "02_SCRIPTS\Draft\The_Rise_of_AI.md"

# Generate musical score cues and trajectory analysis
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" music "02_SCRIPTS\Draft\The_Rise_of_AI.md"

# Export DaVinci Resolve / Premiere Pro Cut List CSV and Executive Brief
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" export "02_SCRIPTS\Draft\The_Rise_of_AI.md"

# Scaffold a new production script template
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" new-script --title "Project Title" --project "Project Name"

# Re-index in-house asset library (04_MEDIA/ and D:\MEDIA_LIBRARY)
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" index-local
```

---

## 5. Production Deliverables & Export Formats

Every pipeline run outputs three synchronized editorial deliverables:

1. **Updated Markdown Script Note (`02_SCRIPTS/Draft/<Title>.md`)**:
   - 6-Level Visual Interpretation (Literal, Contextual, Conceptual, Metaphorical, Emotional, Cinematic).
   - Ranked B-Roll recommendations with 9-Factor editorial relevance score, visual specificity (0-5), and sequence cutting rules.
   - Multi-layered SFX acoustic design table (Ambience, Mechanical, Foley, Transition, Impact).
   - Dynamic Musical Score direction (Tempo BPM, Musical Key, Instrumentation, and In-house Theme matches).
   - Factual claim verifications linked bidirectionally to canonical Source Notes in `06_SOURCES/News/`.

2. **NLE Cut List CSV (`02_SCRIPTS/Draft/<Title>_CutList.csv`)**:
   - DaVinci Resolve & Adobe Premiere Pro conformable spreadsheet.
   - Exact SMPTE timecodes (`00:00:00:00` to `HH:MM:SS:FF`), Shot IDs, Narration lines, B-Roll download URLs, camera movement specs, and SFX / Score cue metadata.

3. **Executive Production Brief (`02_SCRIPTS/Draft/<Title>_Production_Brief.md`)**:
   - Broadcast runtime analytics (total duration, word count, words-per-second pacing vs standard 2.3-2.5 wps).
   - Master Storyboard table with camera framing, narrative functions, and asset URLs.
   - Musical Score cue sheet (motifs, tempo, key, instrumentation).
   - Legal Fact Verification dossier with source publisher reputations and excerpt proof.
   - Post-production sign-off and delivery lock checklist.

