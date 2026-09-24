---
type: system_settings
title: "Production OS Settings"
local_media_root: "D:\\MEDIA_LIBRARY"
words_per_second: 2.4
weights:
  semantic_relevance: 0.20
  narrative_function: 0.15
  visual_specificity: 0.15
  artistic_interpretation: 0.15
  cinematic_compatibility: 0.10
  temporal_relevance: 0.10
  geographic_relevance: 0.05
  editorial_utility: 0.05
  source_quality: 0.05
anti_pattern_penalty: 0.40
redundancy_penalty_max: 0.30
api_endpoints:
  pexels_enabled: true
  pixabay_enabled: true
  wikimedia_enabled: true
  archive_org_enabled: true
  duckduckgo_enabled: true
---

# PRODUCTION OS — SYSTEM SETTINGS

> Configuration parameters for the 9-factor editorial relevance scoring engine and artistic logic layers.

## 1. Editorial Relevance Scoring Weights ($S \in [0.0, 1.0]$)

$$S = 100 \times \left( \begin{aligned}
& 0.20 \cdot S_{\text{semantic}} + 0.15 \cdot S_{\text{narrative}} + 0.15 \cdot S_{\text{specificity}} \\
+ & 0.15 \cdot S_{\text{artistic}} + 0.10 \cdot S_{\text{cinematic}} + 0.10 \cdot S_{\text{temporal}} \\
+ & 0.05 \cdot S_{\text{geo}} + 0.05 \cdot S_{\text{utility}} + 0.05 \cdot S_{\text{source}}
\end{aligned} \right) - P_{\text{redundancy}} - P_{\text{avoid}}$$

| Dimension | Weight | Purpose |
|---|---:|---|
| **Semantic Relevance ($S_{\text{semantic}}$)** | `20%` | Subject matter vocabulary and keyword overlap |
| **Narrative Function ($S_{\text{narrative}}$)** | `15%` | Fulfills assigned visual job (Establishing, Proof, Context, etc.) |
| **Visual Specificity ($S_{\text{specificity}}$)** | `15%` | Degree of direct representation vs generic stock (0 to 5) |
| **Artistic Interpretation ($S_{\text{artistic}}$)** | `15%` | Alignment with underlying conceptual motif and physical metaphor |
| **Cinematic Compatibility ($S_{\text{cinematic}}$)** | `10%` | Framing (wide/macro), camera motion, and contrast lighting |
| **Temporal Relevance ($S_{\text{temporal}}$)** | `10%` | Chronological era and historical coherence |
| **Geographic Relevance ($S_{\text{geo}}$)** | `5%` | Regional and physical setting accuracy |
| **Editorial Utility ($S_{\text{utility}}$)** | `5%` | Clean composition, typography space, absence of watermarks |
| **Source Quality ($S_{\text{source}}$)** | `5%` | Resolution (4K UHD), bitrate, and commercial license grade |

$$\sum w_i = 0.20 + 0.15 + 0.15 + 0.15 + 0.10 + 0.10 + 0.05 + 0.05 + 0.05 = 1.00$$

## 2. Editorial Penalties
- **Visual Redundancy ($P_{\text{redundancy}}$)**: `-30%` penalty if candidate repeats previous shot's subject and framing scale.
- **Anti-Pattern Guardrail ($P_{\text{avoid}}$)**: `-40%` penalty if candidate matches banned visual slop tropes.

## 3. Visual Coverage Requirements
A section is deemed production-ready when its coverage metric reaches $\ge 75\%$:
- Primary Establishing / Master Shot (`25%`)
- Secondary Contextual Shot (`20%`)
- Macro / Detail Insert Shot (`20%`)
- Kinetic / Transition Cutaway (`15%`)
- Conceptual Metaphorical B-Roll (`10%`)
- Empirical Proof / Source Citation (`10%`)

---

## 4. System & Graph Interconnections

- **Orchestration Engine**: [[00_SYSTEM/Automation|Automation Pipeline & Panel Breakdown Engine]]
- **Art Direction Hierarchy**: [[00_SYSTEM/ARTISTIC_LOGIC_ENGINE|Artistic Logic Engine Specification]]
- **Command Dashboard**: [[00_SYSTEM/Dashboard|Production OS Command Center]]
- **Production SOP**: [[00_SYSTEM/Workflows|Production SOP & Lifecycle]]
- **Master Storyboard Deck**: [[05_SHOTS/Shot_Planner|Master Shot Planner]]

