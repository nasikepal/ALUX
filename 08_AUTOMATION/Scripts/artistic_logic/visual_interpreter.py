"""
Visual Interpreter and Artistic Reasoning Layer.
Executes the 6-Level Visual Interpretation Hierarchy and generates multi-tier search matrices.
"""

from typing import Dict, List, Any, Tuple
from core.models import VisualUnit, VisualIntent
from artistic_logic.narrative_classifier import narrative_classifier
from artistic_logic.metaphor_engine import metaphor_engine
from artistic_logic.cinematic_logic import cinematic_logic


class VisualInterpreter:
    def interpret_unit(self, unit: VisualUnit) -> Dict[str, Any]:
        """
        Executes the full 6-level artistic reasoning chain.
        """
        # 1. Visual Job & Narrative Function
        visual_jobs = narrative_classifier.classify_visual_job(unit.text, unit.script_section)
        narrative_funcs = narrative_classifier.classify_narrative_function(unit.text, visual_jobs)
        avoid_items, avoid_reason = narrative_classifier.get_avoid_criteria(unit.text)

        # 2. Metaphorical Transduction
        concepts = unit.visual_intent.primary if unit.visual_intent.primary else [unit.script_section]
        strategy = metaphor_engine.derive_visual_strategy(unit.text, concepts)

        # 3. Cinematic Direction
        cinema = cinematic_logic.determine_cinematic_profile(visual_jobs, strategy["motif"])

        # 4. Synthesize 6-Level Interpretation
        levels = {
            "level_01_literal": strategy["literal"],
            "level_02_contextual": strategy["contextual"],
            "level_03_conceptual": strategy["conceptual"],
            "level_04_metaphorical": strategy["metaphorical"],
            "level_05_emotional": strategy["emotional_tone"],
            "level_06_cinematic": {
                "preferred_shots": [cinema["preferred_framing"]],
                "camera_motion": cinema["camera_motion"],
                "lighting": cinema["lighting_mood"],
                "pacing": cinema["pacing"]
            }
        }

        # 5. Build Artistic Search Matrix
        primary_literal = strategy["literal"][0] if strategy["literal"] else "technology infrastructure"
        primary_context = strategy["contextual"][0] if strategy["contextual"] else "modern industry"
        primary_concept = strategy["conceptual"][0] if strategy["conceptual"] else "massive scale"
        primary_metaphor = strategy["metaphorical"][0] if strategy["metaphorical"] else "transit network"

        search_matrix = {
            "literal_search": [
                f"{primary_literal} 4k",
                f"{strategy['literal'][1] if len(strategy['literal']) > 1 else 'server room'} 4k"
            ],
            "contextual_search": [
                f"{primary_context} b roll",
                f"{strategy['contextual'][1] if len(strategy['contextual']) > 1 else 'technology facility'} 4k"
            ],
            "conceptual_search": [
                f"{primary_concept} footage",
                f"massive industrial infrastructure 4k"
            ],
            "cinematic_search": [
                f"{primary_literal} {cinema['preferred_framing']} cinematic",
                f"{primary_literal} {cinema['camera_motion']}"
            ],
            "detail_search": [
                f"{primary_literal} macro close up",
                f"{primary_literal} rack focus detail"
            ]
        }

        # Flatten into prioritized search queries
        prioritized_queries = (
            search_matrix["cinematic_search"]
            + search_matrix["literal_search"]
            + search_matrix["contextual_search"]
            + search_matrix["detail_search"]
            + search_matrix["conceptual_search"]
        )

        return {
            "visual_jobs": visual_jobs,
            "narrative_functions": narrative_funcs,
            "interpretation_levels": levels,
            "search_matrix": search_matrix,
            "prioritized_queries": prioritized_queries,
            "avoid": {
                "items": avoid_items,
                "reason": avoid_reason
            },
            "strategy": strategy,
            "cinematic": cinema
        }


visual_interpreter = VisualInterpreter()
