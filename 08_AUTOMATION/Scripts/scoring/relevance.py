"""
Editorial Relevance Scoring Engine for Obsidian Production OS.
Implements the 9-Factor Multidimensional Editorial Relevance formula,
Visual Specificity grading (0-5), sequence redundancy penalization, and anti-pattern avoidance.
"""

from typing import Dict, Tuple, List, Optional, Any
import re
from core.config import config
from core.models import VisualUnit, MediaAsset, SourceFact
from artistic_logic.shot_logic import sequence_engine


def render_progress_bar(percentage: int, length: int = 18) -> str:
    """Renders a high-signal ASCII block progress bar (e.g. ██████████████░░░░ 78%)."""
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

    def score_media(
        self,
        candidate: Dict[str, Any],
        unit: VisualUnit,
        previous_shot_meta: Optional[Dict[str, Any]] = None
    ) -> Tuple[float, Dict[str, float], str, int, str]:
        """
        Computes 9-Factor Editorial Relevance Score S in [0.0, 1.0].
        Returns (composite_score, breakdown_dict, why_reason, specificity_score, narrative_function).
        """
        cand_title = candidate.get("title", "")
        cand_desc = candidate.get("description", "")
        cand_tags = candidate.get("tags", [])
        cand_text = f"{cand_title} {cand_desc} {' '.join(cand_tags)}".lower()
        cand_tokens = self._tokenize(cand_text)

        # 0. Anti-Pattern / AVOID Check (Editorial Guardrail)
        avoid_items = unit.avoid_criteria.get("items", [])
        matched_avoid = [a for a in avoid_items if a.replace("_", " ") in cand_text]
        avoid_penalty = 0.0
        if matched_avoid:
            avoid_penalty = 0.40  # Heavy penalty for matching visual anti-pattern

        # 1. Semantic Relevance (20%)
        script_tokens = self._tokenize(unit.text)
        s_semantic = 0.5
        if script_tokens:
            overlap = len(cand_tokens.intersection(script_tokens)) / min(len(script_tokens), 6)
            s_semantic = min(1.0, max(0.1, overlap * 1.3))

        # 2. Narrative Function (15%)
        # Does the candidate perform the specific job?
        primary_job = unit.visual_jobs[0] if unit.visual_jobs else "contextualize"
        narrative_func = unit.narrative_functions[0] if unit.narrative_functions else "B — Context"
        s_narrative = 0.75
        if "establish" in primary_job and any(w in cand_text for w in ["aerial", "wide", "landscape", "panoramic", "exterior"]):
            s_narrative = 1.0
            narrative_func = "G — Establishing"
        elif "prove" in primary_job and any(w in cand_text for w in ["document", "chart", "screen", "macro", "close"]):
            s_narrative = 1.0
            narrative_func = "A — Literal Evidence"
        elif "humanize" in primary_job and any(w in cand_text for w in ["engineer", "worker", "face", "hands", "person", "team"]):
            s_narrative = 1.0
            narrative_func = "H — Humanization"

        # 3. Visual Specificity (15%) — Grade 0 to 5
        # 0 = generic, 1 = loosely related, 2 = contextual, 3 = directly relevant, 4 = highly specific, 5 = exact
        specificity = 2
        strat = unit.visual_strategy
        literal_matches = sum(1 for lit in strat.get("literal", []) if lit.lower() in cand_text)
        if literal_matches >= 2:
            specificity = 5
        elif literal_matches == 1:
            specificity = 4
        elif any(ctx.lower() in cand_text for ctx in strat.get("contextual", [])):
            specificity = 3
        elif any(meta.lower() in cand_text for meta in strat.get("metaphorical", [])):
            specificity = 3
        elif s_semantic >= 0.6:
            specificity = 2
        else:
            specificity = 1

        s_specificity = specificity / 5.0

        # 4. Artistic Interpretation (15%)
        # Does it match conceptual/metaphorical motif from MetaphorEngine?
        artistic_matches = 0
        for concept in strat.get("conceptual", []) + strat.get("metaphorical", []):
            concept_tokens = self._tokenize(concept)
            if cand_tokens.intersection(concept_tokens):
                artistic_matches += 1
        s_artistic = min(1.0, 0.5 + (artistic_matches * 0.25))

        # 5. Cinematic Compatibility (10%)
        # Framing, motion, composition
        cinema_pref = unit.interpretation_levels.get("level_06_cinematic", {})
        preferred_shots = [s.lower() for s in cinema_pref.get("preferred_shots", [])]
        s_cinematic = 0.70
        if any(p in cand_text for p in preferred_shots) or any(m in cand_text for m in ["4k", "cinematic", "dolly", "slow"]):
            s_cinematic = 0.95

        # 6. Temporal Relevance (10%)
        s_temporal = 0.80
        if unit.time_period:
            s_temporal = 1.0 if any(p.lower() in cand_text for p in unit.time_period) else 0.50

        # 7. Geographic Relevance (5%)
        s_geo = 0.85
        if unit.locations:
            s_geo = 1.0 if any(loc.lower() in cand_text for loc in unit.locations) else 0.40

        # 8. Editorial Utility (5%)
        # Clean framing, resolution, duration
        res = candidate.get("resolution", "").lower()
        duration_str = candidate.get("duration", "")
        s_utility = 0.80
        if "4k" in res or "uhd" in res or "3840" in res:
            s_utility = 1.0
        elif "1080" in res or "hd" in res:
            s_utility = 0.85

        # 9. Source Quality (5%)
        s_source = 0.75
        lic = candidate.get("license", "").lower()
        if "commercial" in lic or "internal" in lic or "public domain" in lic:
            s_source = 1.0
        elif "creative commons" in lic:
            s_source = 0.90

        # 10. Sequence Redundancy Penalty (Deduction)
        redundancy_penalty = sequence_engine.compute_redundancy_penalty(candidate, previous_shot_meta)

        # Composite calculation
        composite = (
            self.weights.semantic_relevance * s_semantic
            + self.weights.narrative_function * s_narrative
            + self.weights.visual_specificity * s_specificity
            + self.weights.artistic_interpretation * s_artistic
            + self.weights.cinematic_compatibility * s_cinematic
            + self.weights.temporal_relevance * s_temporal
            + self.weights.geographic_relevance * s_geo
            + self.weights.editorial_utility * s_utility
            + self.weights.source_quality * s_source
        )

        composite = max(0.10, min(1.0, composite - avoid_penalty - redundancy_penalty))

        breakdown = {
            "semantic_relevance": round(s_semantic, 2),
            "narrative_function": round(s_narrative, 2),
            "visual_specificity": round(s_specificity, 2),
            "artistic_interpretation": round(s_artistic, 2),
            "cinematic_compatibility": round(s_cinematic, 2),
            "temporal_relevance": round(s_temporal, 2),
            "geographic_relevance": round(s_geo, 2),
            "editorial_utility": round(s_utility, 2),
            "source_quality": round(s_source, 2),
            "redundancy_penalty": round(redundancy_penalty, 2),
            "avoid_penalty": round(avoid_penalty, 2)
        }

        # Editorial Why Justification
        why_parts = [
            f"Fulfills visual job '{primary_job}' as {narrative_func} (Specificity {specificity}/5)",
            f"Artistically conveys '{strat.get('motif', 'core theme')}' with {cinema_pref.get('lighting', 'cinematic contrast')}"
        ]
        if redundancy_penalty > 0:
            why_parts.append(f"[-{int(redundancy_penalty*100)}% sequence redundancy penalty applied]")
        if avoid_penalty > 0:
            why_parts.append(f"[-{int(avoid_penalty*100)}% anti-pattern penalty: {matched_avoid[0]}]")

        why_reason = "; ".join(why_parts) + "."

        return round(composite, 3), breakdown, why_reason, specificity, narrative_func

    def score_source_fact(self, source_dict: Dict, claim: str) -> Tuple[float, str]:
        """Calculates credibility and relevance for journalistic facts."""
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

        claim_tokens = self._tokenize(claim)
        title_tokens = self._tokenize(source_dict.get("title", ""))
        overlap = len(claim_tokens.intersection(title_tokens)) / max(1, min(len(claim_tokens), 4))
        score = min(0.99, max(0.50, base_score + (overlap * 0.1)))
        return round(score, 3), credibility


relevance_engine = RelevanceEngine()
