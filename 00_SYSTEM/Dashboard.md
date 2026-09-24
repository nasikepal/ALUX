---
type: system_dashboard
title: "Production OS Command Center"
updated: 2026-09-24
---

# PRODUCTION OS — COMMAND CENTER

> **Polymath Video Production & Pre-Production Engine**
> Machine-Readable Script Decomposition • 6-Factor B-Roll Scoring • Source Verification • SFX Cues

---

## 🚀 PIPELINE ACTIONS (ONE-CLICK LAUNCHERS)

| Action | Command / Trigger | Target Scope |
|---|---|---|
| ⚡ **Run End-to-End Pipeline** | `cli.py pipeline <file>` | Full Script → Visuals → Footage → SFX → Sources → Shots |
| 🔍 **Analyze Script & Visual Intent** | `cli.py analyze <file>` | Narrative → Physical Cinematic Units & Framing |
| 🎥 **Find & Score B-Roll** | `cli.py broll <file>` | Multi-factor scored stock & local footage |
| 📰 **Verify Claims & Sources** | `cli.py news <file>` | Fact checking & Source Note generation |
| 🔊 **Generate SFX Sound Design** | `cli.py sfx <file>` | Ambience, mechanical, transition, and emphasis |
| 📋 **Generate Shot Planner** | `cli.py shots <file>` | Visual Unit → Shot cards & Storyboard deck |
| 📦 **Index Local Media Library** | `cli.py index-local` | Scans `D:\MEDIA_LIBRARY` or `04_MEDIA` |

---

## 🎬 ACTIVE PROJECTS OVERVIEW

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
  status AS "Script State", 
  broll_status AS "B-Roll", 
  source_status AS "Sources", 
  research_status AS "Research"
FROM "02_SCRIPTS"
WHERE type = "script"
SORT file.mtime DESC
```

---

## 🎯 NEEDS ATTENTION QUEUE

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

### Critical Production Checks
- [ ] Review pending items in [[03_RESEARCH/_INBOX|Research Inbox]]
- [ ] Confirm licensed B-Roll in [[05_SHOTS/Shot_Planner|Master Shot Planner]]
- [ ] Verify claims against generated [[06_SOURCES/News|Canonical Source Notes]]
- [ ] Match SFX tracks in [[04_MEDIA/SFX|Local SFX Vault]]

---

## 📊 MEDIA & SHOT ARCHITECTURE

- **Master Shot Planner**: [[05_SHOTS/Shot_Planner|Open Storyboard Deck]]
- **Draft Scripts Folder**: `02_SCRIPTS/Draft/`
- **Verified Sources Vault**: `06_SOURCES/News/`
- **Research Inbox (Triage)**: `03_RESEARCH/_INBOX/`
- **Local Asset Index**: `08_AUTOMATION/Search/local_media_index.json`
- **System Settings & Weights**: [[00_SYSTEM/Settings|Configure Production Engine]]
