---
type: shot_planner
project: "The Rise of AI"
total_shots: 5
total_duration: 44s
updated: 2026-09-24
---

# Master Shot Planner — The Rise of AI

> Production storyboard and shot-by-shot asset mapping board.

## Visual Shot Deck

### SH-001 — [[SH-001 - Silicon Wafer Microchip Closeup (Ci|Silicon Wafer Microchip Closeup (Cinematic Footage)]]
> **Narration**: "AI is no longer something that exists only inside research labs. From automated trading desks to surgical operating theaters, machine learning models are fundamentally rewriting the physical rules of human production."

- **Relevance**: `██████████████░░░░░░ 70%`
- 🎥 **Footage**: [Silicon Wafer Microchip Closeup (Cinematic Footage)](https://www.pexels.com/search/videos/silicon+wafer+microchip+closeup/) (`Pexels Stock`)
- 🔊 **SFX**: `deep binaural synthetic tone`
- 📰 **Source**: `Financial & Industry Analysis: AI is no longer som`
- ⏱️ **Duration**: `13s` | **Camera**: `Extreme macro rack-focus across silicon circuit paths` | **Status**: `planned`

---
### SH-002 — [[SH-002 - Cavium ThunderX2, 54-core 3Ghz 14nm|Cavium ThunderX2, 54-core 3Ghz 14nm ARM Server Processor]]
> **Narration**: "The company spent billions building infrastructure for artificial intelligence, deploying over $10 billion into hyperscale compute centers across North America."

- **Relevance**: `█████████████████░░░ 83%`
- 🎥 **Footage**: [Cavium ThunderX2, 54-core 3Ghz 14nm ARM Server Processor](https://archive.org/details/CaviumThunderx254-core3ghz14nmArmServerProcessor) (`Internet Archive`)
- 🔊 **SFX**: `server room low drone`
- 📰 **Source**: `Financial & Industry Analysis: The company spent b`
- ⏱️ **Duration**: `8s` | **Camera**: `Slow forward tracking shot through server aisle` | **Status**: `planned`

---
### SH-003 — [[SH-003 - Cavium ThunderX2, 54-core 3Ghz 14nm|Cavium ThunderX2, 54-core 3Ghz 14nm ARM Server Processor]]
> **Narration**: "Thousands of servers are running around the clock, cooled by liquid thermal loops and connected by miles of high-bandwidth fiber optic conduits."

- **Relevance**: `█████████████████░░░ 83%`
- 🎥 **Footage**: [Cavium ThunderX2, 54-core 3Ghz 14nm ARM Server Processor](https://archive.org/details/CaviumThunderx254-core3ghz14nmArmServerProcessor) (`Internet Archive`)
- 🔊 **SFX**: `server room low drone`
- 📰 **Source**: `Financial & Industry Analysis: Thousands of server`
- ⏱️ **Duration**: `9s` | **Camera**: `Slow forward tracking shot through server aisle` | **Status**: `planned`

---
### SH-004 — [[SH-004 - Dcuo CelticMinx's Story Seasons 1 -|Dcuo CelticMinx's Story Seasons 1 - 3]]
> **Narration**: "Next-generation humanoid robots are now stepping off laboratory test benches and entering automotive factory assembly floors."

- **Relevance**: `██████████████████░░ 92%`
- 🎥 **Footage**: [Dcuo CelticMinx's Story Seasons 1 - 3](https://archive.org/details/mysticfire-dcuo-celticminxs-story-seasons-1-3) (`Internet Archive`)
- 🔊 **SFX**: `server room low drone`
- 📰 **Source**: `Financial & Industry Analysis: Next-generation hum`
- ⏱️ **Duration**: `7s` | **Camera**: `Close-up macro pan across metallic articulated fingers` | **Status**: `planned`

---
### SH-005 — [[SH-005 - LEGO Military AI: DOLLAR COLLAPSE —|LEGO Military AI: DOLLAR COLLAPSE — 31% in 24 Hours, No Surrender]]
> **Narration**: "Venture investment in frontier cognitive architectures surpassed historical records in 2026, creating an undeniable technological paradigm shift."

- **Relevance**: `████████████████░░░░ 80%`
- 🎥 **Footage**: [LEGO Military AI: DOLLAR COLLAPSE — 31% in 24 Hours, No Surrender](https://archive.org/details/youtube-VTA_89aQmD4) (`Internet Archive`)
- 🔊 **SFX**: `server room low drone`
- 📰 **Source**: `Financial & Industry Analysis: Venture investment `
- ⏱️ **Duration**: `7s` | **Camera**: `Low angle wide tilt looking up at glass skyscraper` | **Status**: `planned`

---


## Shot Database Query (Dataview)

```dataview
TABLE duration AS "Duration (s)", priority AS "Priority", shot_type AS "Type", camera AS "Camera", relevance AS "Relevance %", status AS "Status"
FROM "05_SHOTS/B-Roll"
WHERE type = "shot"
SORT shot_id ASC
```
