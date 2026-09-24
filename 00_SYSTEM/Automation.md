---
type: system_automation
title: "Production OS Automation Engine"
status: operational
runtime: "Python 3.14 + uv"
---

# PRODUCTION OS — AUTOMATION ENGINE

> Deep technical architecture and command reference for the production pipeline.

## System Architecture

```
┌────────────────────────────────────────────────────────┐
│                   LAYER 1 — OBSIDIAN                   │
│   Scripts • Shot Lists • Sources • Research • Dashboard│
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               LAYER 2 — AUTOMATION ENGINE              │
│       Python 3.14 CLI • Parsing • Scoring • Writing    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                   LAYER 3 — AI / NLP                   │
│     Narrative → Physical Visual Intent & SFX Layers    │
└──────────────────────────┬─────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│ LAYER 5 — LOCAL ASSETS    │ │ LAYER 4 — WEB SOURCES    │
│ D:\MEDIA_LIBRARY          │ │ Wikimedia • Pexels       │
│ SFX • Footage • Masters   │ │ Archive.org • Reuters    │
└───────────────────────────┘ └──────────────────────────┘
```

## CLI Command Palette Reference

All commands are executed using the vault's embedded Python environment:

```powershell
# 1. Run the Full End-to-End Pipeline
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" pipeline "02_SCRIPTS\Draft\<script_name>.md"

# 2. Extract Visual Units & Cinematic Intent
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" analyze "02_SCRIPTS\Draft\<script_name>.md"

# 3. Find and Score B-Roll Footage
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" broll "02_SCRIPTS\Draft\<script_name>.md"

# 4. Search and Match SFX Sound Layers
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" sfx "02_SCRIPTS\Draft\<script_name>.md"

# 5. Fact Check Claims and Generate Source Notes
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" news "02_SCRIPTS\Draft\<script_name>.md"

# 6. Generate Shot Cards & Master Shot Planner
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" shots "02_SCRIPTS\Draft\<script_name>.md"

# 7. Compose Musical Score Trajectory & Emotional Cues
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" music "02_SCRIPTS\Draft\<script_name>.md"

# 8. Export DaVinci/Premiere NLE Cut List CSV & Executive Brief
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" export "02_SCRIPTS\Draft\<script_name>.md"

# 9. Scan and Index In-House Media Library
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" index-local

# 10. Scaffold a New Production Script
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" new-script --title "The Psychology of Money" --project "Finance Series"
```
