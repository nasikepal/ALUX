---
type: system_workflow
title: "Production Workflows & SOP"
updated: 2026-09-24
---

# PRODUCTION OS — WORKFLOWS & SOP

> Complete operational lifecycle from initial concept to locked production brief.

## Workflow Pipeline Sequence

```
┌─────────────────┐
│   VIDEO IDEA    │ ───► New Note in 02_SCRIPTS/Draft/ using Script_Template.md
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SCRIPT NOTE   │ ───► Write narration sentences under H2 headings (Hook, Context, Climax...)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SCRIPT ANALYZER │ ───► Deconstructs into Visual Units (VU-001, VU-002...)
└────────┬────────┘      Derives Physical Visual Intent & Acoustic Sound Intent
         │
         ▼
┌─────────────────────────────────┐
│  PARALLEL DISCOVERY ENGINES     │
├───────────────┬─────────────────┤
│ Footage Search│ Fact Checking   │ ───► Searches Local Media first, then Wikimedia / Stock
│ & 6-Way Score │ & Source Verify │ ───► Matches claims to Reuters/Bloomberg citations
└───────┬───────┴────────┬────────┘
        │                │
        ▼                ▼
┌─────────────────────────────────┐
│    OUTPUT SYNTHESIS LAYER       │
├─────────────────────────────────┤
│ 1. Script Note updated with B-Roll recommendations & SFX tables
│ 2. Master Shot Planner populated in 05_SHOTS/Shot_Planner.md
│ 3. Canonical Source Notes written in 06_SOURCES/News/
│ 4. Triage cards written in 03_RESEARCH/_INBOX/ (Human-in-the-loop review)
└─────────────────────────────────┘
```

## Step-by-Step SOP

### Step 1: Draft the Script
Create a new note in `02_SCRIPTS/Draft/` with the standard frontmatter (`type: script`, `project: ...`, `format: youtube`). Write your voiceover lines using markdown blockquotes (`> ...`) under each section heading.

### Step 2: Trigger Automation
Run `run_pipeline.bat` or execute via CLI:
```powershell
& "d:\Obsidian Vaults\ALUX\.venv\Scripts\python.exe" "08_AUTOMATION\Scripts\cli.py" pipeline "02_SCRIPTS\Draft\Your_Script.md"
```

### Step 3: Human-in-the-Loop Review
1. Check `03_RESEARCH/_INBOX/` to accept or reject discovered sources.
2. Review [[05_SHOTS/Shot_Planner|Master Shot Planner]] to confirm shot framing and camera movement.
3. Review B-Roll recommendations inside the script note and adjust cut timings.

### Step 4: Production Lock
Once all shots and sources are approved:
- Move script note to `02_SCRIPTS/Production/`
- Export shot list for editor / cinematographer
