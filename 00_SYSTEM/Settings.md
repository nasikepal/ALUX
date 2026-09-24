---
type: system_settings
title: "Production OS Settings"
local_media_root: "D:\\MEDIA_LIBRARY"
words_per_second: 2.4
weights:
  visual_similarity: 0.30
  script_relevance: 0.25
  entity_match: 0.15
  temporal_relevance: 0.10
  geographic_relevance: 0.10
  source_quality: 0.10
api_endpoints:
  pexels_enabled: true
  pixabay_enabled: true
  wikimedia_enabled: true
  archive_org_enabled: true
  duckduckgo_enabled: true
---

# PRODUCTION OS — SYSTEM SETTINGS

> Configuration parameters for the multi-factor relevance scoring engine and media providers.

## 1. Relevance Scoring Weights ($S \in [0.0, 1.0]$)
The scoring engine computes composite relevance according to Charlie Munger inversion & Bayesian principles:
- **Visual Similarity ($S_{vis}$)**: `0.30` (Direct semantic overlap with primary/secondary physical concepts)
- **Script Relevance ($S_{script}$)**: `0.25` (Narrative sentence contextual fit)
- **Entity Match ($S_{entity}$)**: `0.15` (Company, person, hardware, or model match)
- **Temporal Relevance ($S_{temporal}$)**: `0.10` (Era / year coherence)
- **Geographic Relevance ($S_{geo}$)**: `0.10` (Location / regional accuracy)
- **Source Quality ($S_{source}$)**: `0.10` (Resolution, bitrate, and license rating)

$$\sum w_i = 0.30 + 0.25 + 0.15 + 0.10 + 0.10 + 0.10 = 1.00$$

## 2. Media Providers & Local Asset Library
- **Primary Search Target**: Local in-house media library at `D:\MEDIA_LIBRARY` or `04_MEDIA/`
- **Fallback Web Providers**:
  - `Wikimedia Commons` (Public domain & Creative Commons 4K/HD video and photos)
  - `Internet Archive` (Historical footage, documentary archives)
  - `Pexels & Pixabay` (Commercial stock footage)
  - `DuckDuckGo & Reuters` (Journalistic source verification)

## 3. Pacing & Word Count Calculation
- **Speaking Rate**: `2.4 words/second` (~144 words/minute)
- **Minimum Visual Unit Duration**: `4 seconds`
- **Maximum Recommended Single Shot**: `12 seconds`
