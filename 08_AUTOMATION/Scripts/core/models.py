"""
Domain models for the Obsidian Production OS.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path


@dataclass
class VisualIntent:
    primary: List[str] = field(default_factory=list)
    secondary: List[str] = field(default_factory=list)
    abstract: List[str] = field(default_factory=list)
    camera: str = "Wide establishing shot"
    lighting: str = "Cinematic high-contrast"
    movement: str = "Slow push-in / dolly"


@dataclass
class SoundIntent:
    ambience: List[str] = field(default_factory=list)
    mechanical: List[str] = field(default_factory=list)
    transition: List[str] = field(default_factory=list)
    emphasis: List[str] = field(default_factory=list)


@dataclass
class MediaAsset:
    title: str
    asset_type: str  # footage, sfx, music, image, graphic
    source: str      # local, pexels, pixabay, wikimedia, youtube, archive, freesound
    url: str
    local_path: Optional[str] = None
    duration: Optional[str] = "unknown"
    resolution: Optional[str] = "unknown"
    license: str = "unknown — check before use"
    relevance_score: float = 0.0
    relevance_breakdown: Dict[str, float] = field(default_factory=dict)
    why_reason: str = ""
    visual_specificity: int = 4  # 0 to 5 (0=generic, 5=exact)
    narrative_function: str = "C — Explanation"
    editorial_utility_passed: bool = True
    redundancy_penalty: float = 0.0


@dataclass
class SourceFact:
    claim_id: str
    claim_text: str
    source_type: str  # news, paper, company_report, book, official_record
    title: str
    publisher: str
    url: str
    published_date: str
    credibility: str = "unrated"  # high, medium, unrated — publisher reputation only, not proof
    relevance_score: float = 0.0  # keyword match between claim and source text, not a verification score
    excerpt: str = ""
    # unverified: nothing found · candidate: found by search, awaiting human review
    # verified: only ever set by a human in the Research Inbox, never by the pipeline
    verification_status: str = "unverified"
    match_type: str = ""


@dataclass
class VisualUnit:
    id: str  # e.g. "VU-001"
    script_section: str  # e.g. "01 — Hook"
    text: str  # Narration sentence/paragraph
    duration_sec: int = 5
    visual_intent: VisualIntent = field(default_factory=VisualIntent)
    sound_intent: SoundIntent = field(default_factory=SoundIntent)
    claims: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    time_period: List[str] = field(default_factory=list)
    search_queries: List[str] = field(default_factory=list)
    asset_types: List[str] = field(default_factory=lambda: ["footage", "news", "image", "graphic"])
    
    # Artistic Logic Engine attributes
    visual_jobs: List[str] = field(default_factory=list)
    narrative_functions: List[str] = field(default_factory=list)
    visual_strategy: Dict[str, Any] = field(default_factory=dict)
    interpretation_levels: Dict[str, Any] = field(default_factory=dict)
    search_matrix: Dict[str, List[str]] = field(default_factory=dict)
    avoid_criteria: Dict[str, Any] = field(default_factory=dict)
    visual_coverage: Dict[str, Any] = field(default_factory=dict)
    sequence_logic: Dict[str, Any] = field(default_factory=dict)
    
    # Sourced recommendations
    primary_broll: Optional[MediaAsset] = None
    alternative_broll: Optional[MediaAsset] = None
    editorial_news: Optional[SourceFact] = None
    sfx_matches: List[MediaAsset] = field(default_factory=list)
    source_matches: List[SourceFact] = field(default_factory=list)

    # Honest fallbacks when nothing real was found — search links, never presented as assets/sources
    broll_search_links: List[Dict[str, str]] = field(default_factory=list)
    unsourced_claims: Dict[str, List[Dict[str, str]]] = field(default_factory=dict)  # claim -> research leads


@dataclass
class ShotItem:
    shot_id: str  # e.g. "SH-001"
    visual_unit_id: str  # e.g. "VU-001"
    duration_sec: int = 5
    priority: str = "high"  # high, medium, low
    shot_type: str = "b-roll"  # b-roll, a-roll, motion, graphic
    visual_description: str = ""
    camera: str = "slow push-in"
    movement: str = "subtle"
    transition: str = "cut"
    source: str = "stock"
    primary_asset: Optional[MediaAsset] = None
    status: str = "planned"  # planned, sourcing, approved, locked


@dataclass
class ScriptDocument:
    file_path: Path
    title: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_content: str = ""
    sections: List[Dict[str, Any]] = field(default_factory=list)
    visual_units: List[VisualUnit] = field(default_factory=list)
    claims: List[SourceFact] = field(default_factory=list)
    shots: List[ShotItem] = field(default_factory=list)
