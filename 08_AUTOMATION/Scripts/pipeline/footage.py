"""
Footage Search and Ranking Pipeline.
Orchestrates multi-provider footage acquisition, runs 6-factor relevance scoring,
and structures Primary, Alternative, and Editorial recommendations.
"""

from typing import List, Dict, Any, Optional
from core.models import VisualUnit, MediaAsset, SourceFact
from providers.local_media import local_media_provider
from providers.wikimedia import wikimedia_provider
from providers.archive import archive_provider
from providers.stock import stock_footage_provider
from providers.news import news_provider
from scoring.relevance import RelevanceEngine
from artistic_logic.coverage import coverage_engine
from artistic_logic.shot_logic import sequence_engine
from core.logger import logger


class FootagePipeline:
    def __init__(self):
        self.scorer = RelevanceEngine()

    def find_broll_for_unit(self, unit: VisualUnit, previous_shot_meta: Optional[Dict[str, Any]] = None, beat_index: int = 1) -> VisualUnit:
        candidates = []

        # 0. Sequence Intelligence: Compute desired next shot type
        unit.sequence_logic = sequence_engine.get_desired_next_shot(previous_shot_meta, beat_index)

        # 1. Search Local Media Library First (Layer 5)
        for q in unit.visual_intent.primary + unit.search_queries:
            local_hits = local_media_provider.search(q, asset_type="footage", limit=2)
            candidates.extend(local_hits)

        # 2. Search Wikimedia Commons & Internet Archive
        primary_concept = unit.visual_intent.primary[0] if (unit.visual_intent and unit.visual_intent.primary) else "cinematic architecture"
        wiki_hits = wikimedia_provider.search_media(primary_concept, limit=2)
        candidates.extend(wiki_hits)

        archive_hits = archive_provider.search_video(primary_concept, limit=2)
        candidates.extend(archive_hits)

        # 3. Search Stock Providers (Pexels / Pixabay — only when API keys are set)
        stock_hits = stock_footage_provider.search_pexels(primary_concept, limit=2)
        stock_hits.extend(stock_footage_provider.search_pixabay(primary_concept, limit=2))
        candidates.extend(stock_hits)

        # Search links are always offered to the editor, but never ranked as assets.
        unit.broll_search_links = stock_footage_provider.search_links(primary_concept)

        # 4. Score all candidates using 9-Factor Editorial Relevance Engine
        scored_assets: List[MediaAsset] = []
        for cand in candidates:
            score, breakdown, why, spec, n_func = self.scorer.score_media(cand, unit, previous_shot_meta)
            scored_assets.append(MediaAsset(
                title=cand.get("title") or "Untitled asset",
                asset_type=cand.get("asset_type", "footage"),
                source=cand.get("source", "unknown"),
                url=cand.get("url", ""),
                local_path=cand.get("local_path"),
                duration=cand.get("duration") or "unknown",
                resolution=cand.get("resolution") or "unknown",
                license=cand.get("license") or "unknown — check before use",
                relevance_score=score,
                relevance_breakdown=breakdown,
                why_reason=why,
                visual_specificity=spec,
                narrative_function=n_func,
                redundancy_penalty=breakdown.get("redundancy_penalty", 0.0)
            ))

        # Sort by relevance score descending
        scored_assets.sort(key=lambda x: x.relevance_score, reverse=True)

        # Select Primary and Alternative
        if scored_assets:
            unit.primary_broll = scored_assets[0]
            if len(scored_assets) > 1:
                unit.alternative_broll = scored_assets[1]

        # 5. Editorial / News context
        claim_seed = unit.claims[0] if unit.claims else unit.text
        news_hits = news_provider.search_claim_sources(claim_seed, limit=1)
        if news_hits:
            nh = news_hits[0]
            n_score, cred = self.scorer.score_source_fact(nh, claim_seed)
            unit.editorial_news = SourceFact(
                claim_id=f"CLAIM-{unit.id.split('-')[-1]}",
                claim_text=claim_seed,
                source_type="news",
                title=nh.get("title") or "Untitled source",
                publisher=nh.get("publisher") or "Unknown publisher",
                url=nh.get("url", ""),
                published_date=nh.get("published_date") or "unknown",
                credibility=cred,
                relevance_score=n_score,
                excerpt=nh.get("excerpt", ""),
                verification_status="candidate",
                match_type=nh.get("match_type", "")
            )

        # 6. Evaluate Visual Coverage for this unit
        unit.visual_coverage = coverage_engine.evaluate_unit_coverage(unit)

        return unit


footage_pipeline = FootagePipeline()
