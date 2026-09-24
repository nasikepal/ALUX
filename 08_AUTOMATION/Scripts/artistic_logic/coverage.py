"""
Visual Coverage Evaluation Engine.
Verifies that every script section possesses sufficient multi-angle, multi-scale,
and metaphorical shot coverage for an uninterrupted high-end edit.
"""

from typing import Dict, List, Any
from core.models import VisualUnit


class CoverageEngine:
    COVERAGE_LAYERS = [
        ("primary", "Primary Establishing / Master Shot", 0.25),
        ("secondary", "Secondary Contextual Shot", 0.20),
        ("detail", "Macro / Insert Detail Shot", 0.20),
        ("transition", "Kinetic / Transition Cutaway", 0.15),
        ("metaphor", "Conceptual Metaphorical B-Roll", 0.10),
        ("source", "Empirical Proof / Document Citation", 0.10)
    ]

    def evaluate_unit_coverage(self, unit: VisualUnit) -> Dict[str, Any]:
        """
        Calculates coverage score (0% to 100%) and generates ASCII visual telemetry.
        """
        scores = {}
        total_score = 0.0

        # 1. Primary Shot
        has_primary = unit.primary_broll is not None
        scores["primary"] = 1.0 if has_primary else 0.0
        total_score += scores["primary"] * 0.25

        # 2. Secondary Shot
        has_secondary = unit.alternative_broll is not None
        scores["secondary"] = 1.0 if has_secondary else 0.0
        total_score += scores["secondary"] * 0.20

        # 3. Detail Shot (check if visual intent or alternative broll has detail/macro)
        has_detail = any("detail" in q.lower() or "macro" in q.lower() or "closeup" in q.lower() for q in unit.search_queries) or (
            unit.primary_broll and any(k in unit.primary_broll.title.lower() for k in ["macro", "detail", "close", "die", "wafer", "rack"])
        )
        scores["detail"] = 0.9 if has_detail else 0.4
        total_score += scores["detail"] * 0.20

        # 4. Transition Shot
        has_transition = len(unit.sound_intent.transition) > 0 and len(unit.visual_intent.secondary) > 0
        scores["transition"] = 0.85 if has_transition else 0.3
        total_score += scores["transition"] * 0.15

        # 5. Metaphorical Shot
        has_metaphor = len(unit.visual_intent.abstract) > 0
        scores["metaphor"] = 0.80 if has_metaphor else 0.2
        total_score += scores["metaphor"] * 0.10

        # 6. Source / Evidence
        has_source = len(unit.source_matches) > 0 or unit.editorial_news is not None
        scores["source"] = 1.0 if has_source else 0.0
        total_score += scores["source"] * 0.10

        pct = int(round(total_score * 100))

        # Render ASCII coverage bars
        bars = []
        for key, name, weight in self.COVERAGE_LAYERS:
            val = scores.get(key, 0.0)
            fill = int(round(val * 18))
            empty = 18 - fill
            bars.append(f"{'█' * fill}{'░' * empty} {name.split()[0]}")

        status_label = "SUFFICIENT COVERAGE" if pct >= 75 else "PARTIAL COVERAGE"
        if pct < 50:
            status_label = "NEEDS B-ROLL ASSETS"

        return {
            "coverage_pct": pct,
            "status_label": status_label,
            "layer_scores": scores,
            "ascii_bars": bars,
            "summary_text": f"Coverage: {pct}% ({status_label})"
        }


coverage_engine = CoverageEngine()
