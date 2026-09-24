"""
Relevance Scoring Engine for Obsidian Production OS.
Computes multi-dimensional weighted relevance scores for candidate media and sources.
"""

from typing import Dict, Tuple, List, Optional
import re
from core.config import config
from core.models import VisualUnit, MediaAsset, SourceFact


def render_progress_bar(percentage: int, length: int = 20) -> str:
    """Renders a high-signal ASCII block progress bar (e.g. ████████████████░░░░ 82%)."""
    filled = int(round((percentage / 100.0) * length))
    filled = max(0, min(length, filled))
    empty = length - filled
    return f"{'█' * filled}{'░' * empty} {percentage}%"


class RelevanceEngine:
    def __init__(self):
        self.weights = config.weights

    @staticmethod
    def _tokenize(text: str) -> set:
        if not text:
            return set()
        clean = re.sub(r"[^\w\s]", " ", text.lower())
        stopwords = {
            "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with",
            "of", "by", "from", "is", "are", "was", "were", "be", "been", "that", "this",
            "it", "as", "into", "video", "footage", "clip", "shot"
        }
        return {word for word in clean.split() if len(word) > 2 and word not in stopwords}

    def score_media(self, candidate: Dict, unit: VisualUnit) -> Tuple[float, Dict[str, float], str]:
        """
        Computes 6-factor composite relevance score S in [0.0, 1.0].
        Returns (composite_score, breakdown_dict, why_explanation).
        """
        cand_text = f"{candidate.get('title', '')} {candidate.get('description', '')} {' '.join(candidate.get('tags', []))}"
        cand_tokens = self._tokenize(cand_text)

        # 1. Visual Similarity (30%)
        vis_tokens = set()
        for p in unit.visual_intent.primary:
            vis_tokens.update(self._tokenize(p))
        for s in unit.visual_intent.secondary:
            vis_tokens.update(self._tokenize(s))
        for a in unit.visual_intent.abstract:
            vis_tokens.update(self._tokenize(a))

        if vis_tokens:
            vis_overlap = len(cand_tokens.intersection(vis_tokens)) / min(len(vis_tokens), 6)
            s_vis = min(1.0, max(0.1, vis_overlap * 1.2))
        else:
            s_vis = 0.5

        # 2. Script Relevance (25%)
        script_tokens = self._tokenize(unit.text)
        if script_tokens:
            script_overlap = len(cand_tokens.intersection(script_tokens)) / min(len(script_tokens), 5)
            s_script = min(1.0, max(0.1, script_overlap * 1.1))
        else:
            s_script = 0.5

        # 3. Entity Match (15%)
        s_entity = 0.5
        if unit.entities:
            entity_matched = False
            for ent in unit.entities:
                if ent.lower() in cand_text.lower():
                    entity_matched = True
                    break
            s_entity = 1.0 if entity_matched else 0.3
        else:
            s_entity = 0.8  # No entity constraint required

        # 4. Temporal Relevance (10%)
        s_temporal = 0.8
        if unit.time_period:
            period_matched = any(p.lower() in cand_text.lower() for p in unit.time_period)
            s_temporal = 1.0 if period_matched else 0.4

        # 5. Geographic Relevance (10%)
        s_geo = 0.8
        if unit.locations:
            geo_matched = any(loc.lower() in cand_text.lower() for loc in unit.locations)
            s_geo = 1.0 if geo_matched else 0.4

        # 6. Source Quality (10%)
        quality = 0.7
        res = candidate.get("resolution", "").lower()
        if "4k" in res or "uhd" in res:
            quality = 1.0
        elif "1080" in res or "hd" in res:
            quality = 0.85
        if candidate.get("license", "").lower().startswith("commercial") or "creative commons" in candidate.get("license", "").lower():
            quality = min(1.0, quality + 0.1)
        s_source = quality

        # Composite calculation
        composite = (
            self.weights.visual_similarity * s_vis
            + self.weights.script_relevance * s_script
            + self.weights.entity_match * s_entity
            + self.weights.temporal_relevance * s_temporal
            + self.weights.geographic_relevance * s_geo
            + self.weights.source_quality * s_source
        )

        breakdown = {
            "visual_similarity": round(s_vis, 2),
            "script_relevance": round(s_script, 2),
            "entity_match": round(s_entity, 2),
            "temporal_relevance": round(s_temporal, 2),
            "geographic_relevance": round(s_geo, 2),
            "source_quality": round(s_source, 2),
        }

        # Human-interpretable Why explanation
        matched_aspects = []
        if s_vis >= 0.7:
            matched_aspects.append(f"strong alignment with '{', '.join(unit.visual_intent.primary[:2])}'")
        if s_entity >= 0.9:
            matched_aspects.append(f"entity match on {unit.entities[0] if unit.entities else 'subject'}")
        if s_source >= 0.8:
            matched_aspects.append(f"high-fidelity asset ({candidate.get('resolution', 'HD')})")

        if matched_aspects:
            why = f"Visually communicates {unit.visual_intent.primary[0] if unit.visual_intent.primary else 'the core concept'}; " + "; ".join(matched_aspects) + "."
        else:
            why = f"Contextual representation for {unit.script_section} narrative."

        return round(composite, 3), breakdown, why

    def score_source_fact(self, source_dict: Dict, claim: str) -> Tuple[float, str]:
        """Calculates credibility and relevance for fact checking."""
        pub = source_dict.get("publisher", "").lower()
        high_cred = ["reuters", "bloomberg", "ap news", "financial times", "sec", "nature", "science", "ieee", "wall street journal", "mit technology review"]
        med_cred = ["the verge", "techcrunch", "wired", "arstechnica", "cnbc", "forbes"]

        credibility = "medium"
        base_score = 0.75
        if any(h in pub for h in high_cred):
            credibility = "high"
            base_score = 0.94
        elif any(m in pub for m in med_cred):
            credibility = "high"
            base_score = 0.86

        # Claim keyword match
        claim_tokens = self._tokenize(claim)
        title_tokens = self._tokenize(source_dict.get("title", ""))
        overlap = len(claim_tokens.intersection(title_tokens)) / max(1, min(len(claim_tokens), 4))
        score = min(0.99, max(0.50, base_score + (overlap * 0.1)))
        return round(score, 3), credibility
