---
type: system_dashboard
title: "Production OS Command Center"
updated: 2026-09-24
---

# PRODUCTION OS — COMMAND CENTER

> **Artistic Logic & Pre-Production Engine**
> Directorial Reasoning • 6-Level Visual Hierarchy • 9-Factor Editorial Scoring • Sequence Intelligence

---

## 🚀 PIPELINE ACTIONS (ONE-CLICK LAUNCHERS)

| Action | Command / Trigger | Target Scope |
|---|---|---|
| ⚡ **Run End-to-End Pipeline** | `cli.py pipeline <file>` | Script → Artistic Interpretation → B-Roll → SFX → Sources → Shots |
| 🎨 **Artistic Reasoning & Intent** | `cli.py analyze <file>` | Visual Job, Metaphor, 6-Level Hierarchy, DO NOT MATCH |
| 🎥 **Find & Score B-Roll** | `cli.py broll <file>` | 9-factor editorial scoring, sequence logic & redundancy filter |
| 📰 **Verify Claims & Sources** | `cli.py news <file>` | Fact checking & Source Note generation |
| 🔊 **Generate SFX Sound Design** | `cli.py sfx <file>` | Ambience, mechanical, transition, and emphasis |
| 🎵 **Musical Score Direction** | `cli.py music <file>` | Harmonic key, BPM tempo, mood & instrumentation cues |
| 📋 **Generate Shot Planner** | `cli.py shots <file>` | Visual Unit → Shot cards, sequence rules & Storyboard deck |
| ⏱️ **Export NLE Cut List & Brief** | `cli.py export <file>` | Generates DaVinci/Premiere CSV cut list & Executive Brief |
| 📦 **Index Local Media Library** | `cli.py index-local` | Scans `D:\MEDIA_LIBRARY` or `04_MEDIA` |

---

## 🎬 ACTIVE PROJECTS & VISUAL COVERAGE

```dataview
TABLE 
  status AS "Project Status", 
  format AS "Format", 
  target_duration AS "Duration", 
  deadline AS "Target Date"
FROM "01_PROJECTS"
WHERE type = "project"
SORT deadline ASC
```

---

## 📜 PRODUCTION SCRIPTS STATUS

```dataview
TABLE 
  project AS "Project", 
  duration AS "Length", 
  artistic_engine AS "Artistic Engine", 
  broll_status AS "B-Roll", 
  source_status AS "Sources", 
  status AS "Stage"
FROM "02_SCRIPTS"
WHERE type = "script"
SORT file.mtime DESC
```

---

## 🎯 SHOT SEQUENCE & COVERAGE MONITOR

```dataview
TABLE 
  narrative_function AS "Narrative Function", 
  visual_specificity AS "Specificity", 
  camera AS "Camera Setup", 
  relevance AS "Score %", 
  coverage_pct AS "Coverage %"
FROM "05_SHOTS/B-Roll"
WHERE type = "shot"
SORT shot_id ASC
```

---

## 🛡️ NEEDS ATTENTION & TRIAGE QUEUE

```dataview
TABLE 
  status AS "Status", 
  source AS "Source Publisher", 
  relevance AS "Relevance Score", 
  related_visual AS "Visual Unit"
FROM "03_RESEARCH/_INBOX"
WHERE status = "unreviewed"
SORT relevance DESC
```

---

## 📊 SYSTEM DOCUMENTATION & ARCHITECTURE

- **Artistic Logic Specification**: [[00_SYSTEM/ARTISTIC_LOGIC_ENGINE|Open Artistic Logic Engine Spec]]
- **Master Shot Planner**: [[05_SHOTS/Shot_Planner|Open Storyboard Deck]]
- **Visual Vocabulary Knowledge Base**: `08_AUTOMATION/Scripts/artistic_logic/visual_vocabulary.yaml`
- **System Settings & 9-Factor Weights**: [[00_SYSTEM/Settings|Configure Production Engine]]
