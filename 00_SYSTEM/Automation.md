---
type: system_automation
title: "Production OS Automation Engine"
status: operational
runtime: "Python 3.14 + uv"
updated: 2026-09-24
tags:
  - system
  - automation
  - pipeline
  - visual-breakdown
  - artistic-logic
---

# PRODUCTION OS — AUTOMATION ENGINE

> **Central Pipeline Orchestrator & Script-to-Visual Transduction System**  
> Enforces mathematical and artistic rational constraints to convert raw narration scripts into production-ready **Visual Markdown Panel Breakdowns**, conformed NLE cut lists, and verified factual dossiers.

---

## 🧭 Vault Knowledge Graph & Core System Links

This automation engine operates as the operational nexus connecting all core system nodes across the vault:

| System Node | Role in Pipeline | Bidirectional Graph Link |
|---|---|---|
| **Command Center** | High-level project status & one-click action triggers | [[00_SYSTEM/Dashboard\|Command Dashboard]] |
| **Art Direction Engine** | 6-Level Interpretation Hierarchy, Metaphors, Anti-Patterns | [[00_SYSTEM/ARTISTIC_LOGIC_ENGINE\|Artistic Logic Engine]] |
| **System Settings** | 9-Factor scoring weights, redundancy penalties & thresholds | [[00_SYSTEM/Settings\|System Settings & Scoring Weights]] |
| **Production SOP** | Lifecycle stages from idea to final export lock | [[00_SYSTEM/Workflows\|Production SOP & Workflows]] |
| **Master Storyboard** | Dynamic visual shot deck & coverage analytics | [[05_SHOTS/Shot_Planner\|Master Storyboard & Shot Planner]] |
| **Script Schema** | Master template for draft scripts | [[99_TEMPLATES/Script_Template\|Script Template]] |
| **Visual Unit Schema** | Atomic visual unit data model | [[99_TEMPLATES/Visual_Unit_Template\|Visual Unit Template]] |
| **Shot Card Schema** | Template for individual B-roll cards | [[99_TEMPLATES/Shot_Template\|Shot Template]] |
| **Source Citation Schema** | Permanent verified journalism dossiers | [[99_TEMPLATES/Source_Template\|Source Template]] |
| **Acoustic Design Schema** | Sound design & Foley layer specification | [[99_TEMPLATES/SFX_Asset_Template\|SFX Asset Template]] |
| **Human Review Triage** | Discovered claim verification inbox | [[99_TEMPLATES/Research_Inbox_Template\|Research Inbox Template]] |
| **Project Schema** | Production milestone & budget tracker | [[99_TEMPLATES/Project_Template\|Project Template]] |
| **Master Index** | Vault root architecture & documentation | [[README\|System Master Index]] |

---

## 📐 Rational Constraints: Converting Script into Visual Markdown Panels

The automation does not blindly concatenate search queries to text. It operates under four **rational constraints** that govern the conversion of spoken prose into shootable, editable visual panels:

```
┌────────────────────────────────────────────────────────────────────────┐
│             INPUT: RAW NARRATION SCRIPT (Markdown / YAML)              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             RATIONAL CONSTRAINT 1: TEMPORAL PACING WINDOW              │
│       • Speech Rate: R = 2.4 words/sec                                 │
│       • Duration: T = Words / 2.4                                      │
│       • Shot Duration Clamp: 3.5s ≤ T_shot ≤ 7.0s                      │
│       • Visual Deconstruction: Beats > 7.0s split into N cuts          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             RATIONAL CONSTRAINT 2: ARTISTIC & EDITORIAL LOGIC          │
│       • 13 Visual Jobs (establish, prove, explain, humanize...)        │
│       • 6-Level Hierarchy (Literal → Context → Metaphor → Cinematic)   │
│       • Anti-Slop Guardrails: DO NOT MATCH trope filters               │
│       • Sequence Intelligence: Adjacent cut redundancy penalty (-30%)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             RATIONAL CONSTRAINT 3: MULTI-LAYER ACOUSTIC DESIGN         │
│       • 4 SFX Layers: Ambience • Mechanical • Transition • Impact       │
│       • Harmonic Score Bed: Tempo (BPM) • Key • Mood Instrumentation   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│     OUTPUT: PRODUCTION-READY VISUAL MARKDOWN PANEL BREAKDOWN           │
│       • Two-Column A/V Script Structure (Audio VO vs. Visual Direction)│
│       • Conformed NLE Timeline CSV (SMPTE 00:00:00:00 timecodes)       │
│       • Bidirectional Wikilinks to Shot Cards & Source Dossiers        │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Temporal Pacing & Cut Duration Window
- **Speech Rate Metric**: Fixed at broadcast standard $R_{\text{speech}} = 2.4 \text{ words/second}$.
- **Duration Formula**:
  $$T_{\text{beat}} = \frac{W_{\text{words}}}{2.4}$$
- **Cognitive Visual Saturation**: Viewer attention on static framing degrades after $5.0 - 7.0 \text{ seconds}$.
- **Rational Cut Constraint**: If $T_{\text{beat}} > 7.0\text{s}$, the pipeline enforces multi-shot segmentation:
  $$N_{\text{shots}} = \left\lceil \frac{T_{\text{beat}}}{5.0} \right\rceil$$
  - Shot 1: Primary Establishing / Literal Proof ($40\%$ duration)
  - Shot 2: Macro Insert / Detail Mechanism ($35\%$ duration)
  - Shot 3: Kinetic Transition / Metaphorical Analogy ($25\%$ duration)

### 2. Two-Column Audio/Visual (AV) Panel Architecture
Each narration beat is converted into an Obsidian-native **Visual Markdown Panel**, structuring voiceover narration alongside concrete visual and acoustic specifications:

```markdown
> [!panel|audio] AUDIO TRACK (VO) — 00:00 - 00:06 (6s)
> *"The fund quietly reallocated $4 billion into physical real estate and hard infrastructure..."*
> - **Pacing**: 14 words @ 2.4 wps = 5.8s | **Claim status**: `candidate` (awaiting Research Inbox review)
> - **Fact Citation**: [[Source - Bloomberg - Fund reallocates $4B into real assets]]

> [!panel|visual] VISUAL DIRECTION & B-ROLL SPEC — SH-001
> - **Visual Job**: `prove, establish` | **Narrative Function**: `A — Literal Evidence`
> - **Cinematic Framing**: `low-angle slow tracking` | **Lighting**: `warm raking dawn light`
> - **Primary Asset**: [Monolithic Modern Architecture](https://...) (Relevance: 84% | Specificity: 4/5)
> - **Editorial Avoid**: `throwing_cash, generic_powerpoint_charts`

> [!panel|sound] SOUND DESIGN & SCORE DIRECTION
> - **Ambience**: `quiet high-ceiling penthouse room tone`
> - **Mechanical**: `fountain pen signature on bond paper`
> - **Score Cue**: `CUE-01` | `72-85 BPM` | `B Minor` (*Quiet Luxury / Restrained Power*)
```

### 3. Visual Specificity & Anti-Pattern Filters
- **Specificity Threshold ($S_{\text{spec}} \ge 3/5$)**: Assets scoring $< 3/5$ are rejected from Primary B-Roll placement unless explicitly classified as abstract kinetic metaphors.
- **Anti-Pattern Guardrail ($P_{\text{avoid}} = -40\%$)**: Eliminates stock clichés across:
  - *Finance*: Rejects suits throwing cash, fake crypto charts, and luxury flex videos.
  - *Mental Health*: Rejects melodramatic head-clutching and stacked zen stones.
  - *Wellness*: Rejects tape measures around apples and generic salad-eating stock.

### 4. Sequence Redundancy Penalty ($P_{\text{redundancy}} \le -30\%$)
The system tracks adjacent shot history ($shot_{i-1} \to shot_i$). If a candidate repeats the same lens framing scale or subject matter, a $-30\%$ penalty forces editorial cut variety (e.g., Wide $\to$ Macro $\to$ Medium).

---

## 🛠️ CLI Command Reference

All pipeline operations run through the vault's embedded runtime:

```powershell
# 1. Run the Full End-to-End Pipeline (Generates Panels, Cut List CSV, and Brief)
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

---

## ⚡ Obsidian QuickAdd & Desktop Integration

- **Obsidian Hotkey**: Press `Ctrl + P` $\to$ Select `QuickAdd: Run Production OS Pipeline` on any active script note.
- **Windows Desktop Launcher**: Double-click `run_pipeline.bat` at vault root to automatically detect and process draft scripts.
- **Scaffolding Launcher**: Double-click `create_script.bat` to interactively generate a new script from [[99_TEMPLATES/Script_Template\|Script Template]].
