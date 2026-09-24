---
type: system_specification
title: "Artistic Logic Engine — Architectural Specification"
status: canonical
layer: "Layer 3 (AI / Creative Direction)"
updated: 2026-09-24
---

# ARTISTIC LOGIC ENGINE — SPECIFICATION

> **Non-Negotiable System Axiom:**
> *"Do not search for what the script says. Search for what the script needs the audience to see."*

---

## 1. The Core Problem & Conceptual Shift

A standard naive search algorithm operates literally:
$$\text{Narration: "The company spent billions building AI infrastructure"} \longrightarrow \text{Query: "company spent billions AI infrastructure"}$$

A world-class visual director or senior film editor processes narration through an artistic transduction chain:
1. **What is the core idea?** Capital concentration, unprecedented technological scaling, industrial physical expansion.
2. **What should the audience understand?** Massive, tangible physical reality behind ephemeral digital intelligence.
3. **What should the audience feel?** Scale, gravitational power, technological momentum.
4. **What visual metaphor communicates that?** Server monoliths with pulsating status indicators, aerial panoramic expanses of hyperscale data centers, robotic silicon wire-bonding.
5. **What footage is usable in an edit?** Stable motorized push-in, deep contrast ratio, generous negative space for motion graphics/typography, clean 4K composition.

The **Artistic Logic Engine** sits between Script Parsing and Footage Search:

```
                         SCRIPT
                           │
                           ▼
                 ┌─────────────────┐
                 │ SCRIPT PARSER   │
                 └────────┬────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  ARTISTIC LOGIC       │
              │       ENGINE          │
              │                       │
              │ • Visual Job (13 types)│
              │ • Narrative Function  │
              │ • 6-Level Hierarchy   │
              │ • Visual Metaphor     │
              │ • DO NOT MATCH Rules  │
              │ • Sequence Intent     │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ SEARCH STRATEGY       │
              │                       │
              │ Literal • Contextual  │
              │ Conceptual • Cinematic│
              │ Detail queries        │
              └───────────┬───────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ FOOTAGE SEARCH  │
                 └────────┬────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ EDITORIAL RELEVANCE   │
              │ (9-Factor Scoring)    │
              │                       │
              │ Specificity (0 to 5)  │
              │ Sequence Redundancy - │
              │ Anti-Pattern Guard -  │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ SEQUENCE INTELLIGENCE │
              │ & VISUAL COVERAGE     │
              │                       │
              │ Cycle: Wide→Med→Macro │
              │ Section Coverage %    │
              └───────────┬───────────┘
                          │
                          ▼
                    B-ROLL BOARD
```

---

## 2. Visual Job Taxonomy

Every script beat is classified into its primary visual duty:

| Visual Job | Directorial Purpose |
|---|---|
| `establish` | Anchor physical environment, geographic location, or spatial reality |
| `explain` | Demystify technical mechanics, physical architecture, or operating principles |
| `illustrate` | Provide direct pictorial accompaniment to narration |
| `contextualize` | Reveal the surrounding economic, industrial, or cultural landscape |
| `prove` | Display empirical documentation, benchmark graphs, or verified physical evidence |
| `humanize` | Focus on human agency, physical fatigue, precision craft, or emotional reaction |
| `emphasize` | Punctuate dramatic climax or monumental structural shift |
| `contrast` | Juxtapose opposing states (e.g. analog obsolescence vs automated hyper-speed) |
| `transition` | Facilitate seamless temporal, spatial, or thematic cuts |
| `foreshadow` | Visually hint at subsequent complications or existential bottlenecks |
| `dramatize` | Heighten narrative stakes, scale, or cinematic tension |
| `visualize_abstract_concept` | Translate non-physical phenomena (weights, algorithms) into physical analogies |
| `provide_atmosphere` | Establish acoustic and lighting room tone, suspense, or stillness |

---

## 3. The 6-Level Visual Interpretation Hierarchy

```yaml
visual_reasoning:
  level_01_literal:
    - What is explicitly stated or physical present in the line?
  level_02_contextual:
    - What facility, environment, or industry sector surrounds the event?
  level_03_conceptual:
    - What is the fundamental intellectual thesis of the line?
  level_04_metaphorical:
    - What physical visual communicates this concept without literal depiction?
  level_05_emotional:
    - What visceral feeling should the audience experience (scale, dread, awe)?
  level_06_cinematic:
    - Framing: (wide aerial, medium contextual, extreme macro)
    - Motion: (slow motorized dolly, locked-off tripod, kinetic whip)
    - Lighting: (high-contrast cobalt/cyan LED, dawn rim light)
```

---

## 4. Multi-Tier Search Matrix

Instead of querying a single generic phrase, the system generates an artistic search matrix:

1. **Literal Search**: Physical subject + resolution (`hyperscale data center 4k`, `server room 4k`)
2. **Contextual Search**: Environmental b-roll (`technology infrastructure construction`, `cloud facility b-roll`)
3. **Conceptual Search**: Scale and power (`massive industrial infrastructure 4k`)
4. **Cinematic Search**: Camera direction and motion (`data center aerial cinematic`, `server room slow tracking shot`)
5. **Detail Search**: Macro inserts for pacing (`GPU server close up`, `cooling loop rack focus detail`)

---

## 5. DO NOT MATCH Guardrails (Anti-Pattern Filter)

Prevents standard stock footage slop from infiltrating high-end documentary sequences:

```yaml
avoid:
  - generic_ai_interface: "Communicates dated corporate slide deck tropes, not authentic machine learning."
  - humanoid_robot_white_plastic: "Uncanny toy caricature that destroys serious industrial credibility."
  - glowing_hologram_brain: "Severe AI visual slop. Replace with silicon wafer lithography or server clusters."
  - generic_stock_laptop: "Zero narrative specificity; conveys no scale."
  - green_arrow_growth: "Executive PowerPoint slop. Replace with highway traffic time-lapse or construction cranes."
```

---

## 6. Visual Specificity Metric (0 to 5)

Candidates are graded on direct visual relevance:
- **Level 0 (Generic)**: Unrelated abstract graphics, stock laptops, out-of-context people.
- **Level 1 (Loosely Related)**: High-tech office, generic glass office building.
- **Level 2 (Contextual)**: Technology server room, generic software interface.
- **Level 3 (Directly Relevant)**: Enterprise data center aisle, GPU cluster with status lights.
- **Level 4 (Highly Specific)**: Liquid-cooled hyperscale server rack, cleanroom semiconductor wafer.
- **Level 5 (Exact Representation)**: Specific named hardware, verified facility, or exact historical archival clip.

---

## 7. The 9-Factor Editorial Relevance Formula

$$S = 100 \times \left( \begin{aligned}
& 0.20 \cdot S_{\text{semantic}} + 0.15 \cdot S_{\text{narrative}} + 0.15 \cdot S_{\text{specificity}} \\
+ & 0.15 \cdot S_{\text{artistic}} + 0.10 \cdot S_{\text{cinematic}} + 0.10 \cdot S_{\text{temporal}} \\
+ & 0.05 \cdot S_{\text{geo}} + 0.05 \cdot S_{\text{utility}} + 0.05 \cdot S_{\text{source}}
\end{aligned} \right) - P_{\text{redundancy}} - P_{\text{avoid}}$$

- **$P_{\text{redundancy}}$**: Penalty (up to -30%) if candidate repeats previous shot's subject and framing scale.
- **$P_{\text{avoid}}$**: Penalty (-40%) if candidate matches visual anti-pattern keywords.

---

## 8. Sequence Intelligence & Visual Coverage

### Sequence Rhythm
The system tracks adjacent shot history ($shot_{i-1} \to shot_i$) to enforce dynamic editing variety:
$$\text{Wide Establishing} \longrightarrow \text{Medium Contextual} \longrightarrow \text{Macro Detail} \longrightarrow \text{Human Agency} \longrightarrow \text{Visual Metaphor} \longrightarrow \text{Wide Payoff}$$

### Section Coverage Evaluation
Every section requires multi-layered visual coverage before production lock:
- Primary Establishing Shot (25%)
- Secondary Contextual Shot (20%)
- Macro / Detail Insert Shot (20%)
- Kinetic / Transition Cutaway (15%)
- Conceptual Metaphorical B-Roll (10%)
- Empirical Proof / Source Citation (10%)

---

## 9. Musical Score Direction & Emotional Pacing

Visual pacing is bound directly to musical tempo, harmonic mode, and instrumentation:

| Narrative Section | Motif | Target BPM | Musical Key | Dominant Instrumentation |
|---|---|---|---|---|
| **01 — Hook** | `scale` | 80-95 BPM | D Minor / C Major | Sub-bass drone, brass swell, modular synth arpeggio |
| **02 — Conflict / Investment** | `growth` | 95-108 BPM | A Major | Driving percussion, electric guitar ambience, forward momentum |
| **03 — Exposition / Machine** | `precision` | 90-100 BPM | G Minor | Glass marimba, crisp electronic clicks, clockwork rhythm |
| **04 — Human Tension** | `automation` | 80-95 BPM | D Minor / C Major | Solo cello, organic textures, subtle electronic bass |
| **05 — Climax / Economic** | `scale` | 80-95 BPM | D Minor / C Major | Full orchestral synth hybrid, monumental percussion impact |

---

## 10. NLE Conform & Timeline Export

Outputs a frame-accurate CSV cut list formatted with SMPTE timecodes (`00:00:00:00`) for direct import into DaVinci Resolve (Edit Index) and Adobe Premiere Pro, alongside an Executive Production Brief detailing broadcast speech pacing, source dossiers, and post-production lock checklists.

---

## 11. System & Graph Interconnections

- **Automation & Breakdown Engine**: [[00_SYSTEM/Automation|Automation Pipeline & Panel Breakdown Engine]]
- **Command Dashboard**: [[00_SYSTEM/Dashboard|Production OS Command Center]]
- **Scoring & Constraint Rules**: [[00_SYSTEM/Settings|System Settings & 9-Factor Weights]]
- **Production SOP**: [[00_SYSTEM/Workflows|Production SOP & Lifecycle]]
- **Master Storyboard Deck**: [[05_SHOTS/Shot_Planner|Master Shot Planner]]


