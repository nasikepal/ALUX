---
type: project
title: "{{title}}"
status: active
format: documentary
target_duration: "10:00"
deadline: 2026-10-15
completion_pct: 0
scripts_count: 1
shots_count: 0
created: {{date}}
---

# Project: {{title}}

> Production command hub for {{title}}.

## Status & Progress

- **Status**: `{{status}}`
- **Target Duration**: `10:00`
- **Format**: `Documentary / High-Ticket Video`
- **Target Channels**: YouTube, LinkedIn, Client Distribution

## Quick Actions & Pipeline Triggers
- Trigger Automation: [[00_SYSTEM/Automation|Run Production OS Automation]]
- View Command Dashboard: [[00_SYSTEM/Dashboard|Open Production OS Dashboard]]
- View Master Storyboard: [[05_SHOTS/Shot_Planner|Open Shot Planner]]
- View Research Queue: [[03_RESEARCH/_INBOX|Open Research Inbox]]

## Associated Scripts (Dataview)

```dataview
TABLE status AS "Status", duration AS "Duration", broll_status AS "B-Roll", source_status AS "Sources"
FROM "02_SCRIPTS"
WHERE project = "{{title}}"
SORT file.name ASC
```

## Sourced Footage & Shot List

```dataview
TABLE duration AS "Sec", camera AS "Camera", relevance AS "Relevance", status AS "Status"
FROM "05_SHOTS/B-Roll"
WHERE project = "{{title}}"
SORT shot_id ASC
```

## Production Notes & Deliverable Milestones
- [ ] Script Polish & Fact Check Lock
- [ ] B-Roll Ingestion & Color Pipeline conform
- [ ] Voiceover Track Assembly & SFX Mix
- [ ] Final Color Grade & Export
