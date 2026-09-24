---
type: project
title: "The Rise of AI"
status: active
format: documentary
target_duration: "08:00"
deadline: 2026-10-15
completion_pct: 65
scripts_count: 1
shots_count: 5
created: 2026-09-24
---

# Project: The Rise of AI

> High-production documentary breakdown examining hyperscale compute expansion, robotics embodiment, and frontier capital deployment.

## Production Status

- **Status**: `Active Pre-Production`
- **Format**: `Documentary / Video Essay`
- **Target Runtime**: `08:00`
- **Primary Script**: [[02_SCRIPTS/Draft/The_Rise_of_AI|The Rise of AI Script]]

## Storyboard & Pre-Vis
- Master Visual Shot List: [[05_SHOTS/Shot_Planner|View Master Shot Planner]]
- Research & Verification Queue: [[03_RESEARCH/_INBOX|View Research Inbox]]

## Associated Scripts

```dataview
TABLE duration AS "Runtime", status AS "Stage", broll_status AS "B-Roll", source_status AS "Sources"
FROM "02_SCRIPTS"
WHERE project = "The Rise of AI"
```

## Production Shots Breakdown

```dataview
TABLE duration AS "Sec", camera AS "Camera Setup", relevance AS "Match %", status AS "Status"
FROM "05_SHOTS/B-Roll"
WHERE project = "The Rise of AI"
SORT shot_id ASC
```
