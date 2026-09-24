---
type: shot_planner
project: "Active Production"
total_shots: 0
total_duration: "00:00"
average_coverage: "0%"
updated: 2026-09-24
---

# Master Shot Planner & Storyboard Deck

> Editorial storyboard, sequence intelligence, and artistic asset mapping board.
> Populated automatically upon executing the Production OS Pipeline on an active script.

## Master Shot Database (Dataview)

```dataview
TABLE 
  duration AS "Duration", 
  narrative_function AS "Function", 
  visual_specificity AS "Specificity (0-5)", 
  camera AS "Camera Setup", 
  relevance AS "Relevance %", 
  coverage_pct AS "Coverage %", 
  status AS "Status"
FROM "05_SHOTS/B-Roll"
WHERE type = "shot"
SORT shot_id ASC
```

---

## Instructions
1. Place your script into `02_SCRIPTS/Draft/<Title>.md`.
2. Run the pipeline via QuickAdd (`Ctrl + P` $\to$ `QuickAdd: Run Production OS Pipeline`) or `run_pipeline.bat`.
3. Shot cards will populate in `05_SHOTS/B-Roll/` and render dynamically in the table above.
