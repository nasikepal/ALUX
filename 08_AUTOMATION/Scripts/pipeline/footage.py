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
from core.logger import logger


class FootagePipeline:
    def __init__(self):
        self.scorer = RelevanceEngine()

    def find_broll_for_unit(self, unit: VisualUnit) -> VisualUnit:
        candidates = []

        # 1. Search Local Media Library First (Layer 5)
        for q in unit.visual_intent.primary + unit.search_queries:
            local_hits = local_media_provider.search(q, asset_type="footage", limit=2)
            candidates.extend(local_hits)

        # 2. Search Wikimedia Commons & Internet Archive
        primary_concept = unit.visual_intent.primary[0] if unit.visual_intent.primary else "technology"
        wiki_hits = wikimedia_provider.search_media(primary_concept, limit=2)
        candidates.extend(wiki_hits)

        archive_hits = archive_provider.search_video(primary_concept, limit=2)
        candidates.extend(archive_hits)

        # 3. Search Stock Providers (Pexels / Pixabay / Curated Reference)
        stock_hits = stock_footage_provider.search_pexels(primary_concept, limit=2)
        stock_hits.extend(stock_footage_provider.search_pixabay(primary_concept, limit=2))
        if not stock_hits:
            stock_hits = stock_footage_provider.generate_editorial_stock_suggestions(
                primary_concept,
                unit.visual_intent.abstract[0] if unit.visual_intent.abstract else "cinematic concept"
            )
        candidates.extend(stock_hits)

        # 4. Score all candidates using 6-factor relevance engine
        scored_assets: List[MediaAsset] = []
        for cand in candidates:
            score, breakdown, why = self.scorer.score_media(cand, unit)
            scored_assets.append(MediaAsset(
                title=cand.get("title", "Cinematic Footage"),
                asset_type=cand.get("asset_type", "footage"),
                source=cand.get("source", "Stock"),
                url=cand.get("url", "#"),
                local_path=cand.get("local_path"),
                duration=cand.get("duration", "12s"),
                resolution=cand.get("resolution", "4K UHD"),
                license=cand.get("license", "Commercial / Royalty-Free"),
                relevance_score=score,
                relevance_breakdown=breakdown,
                why_reason=why
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
                title=nh.get("title", "Editorial Reporting"),
                publisher=nh.get("publisher", "Reuters"),
                url=nh.get("url", "#"),
                published_date=nh.get("published_date", "2026-08-14"),
                credibility=cred,
                relevance_score=n_score,
                excerpt=nh.get("excerpt", "")
            )

        return unit


footage_pipeline = FootagePipeline()
