"""
Sequence Intelligence and Redundancy Penalization Engine.
Prevents visual repetition across adjacent beats and enforces dynamic editorial rhythm.
"""

from typing import Dict, List, Any, Optional


class SequenceEngine:
    PROGRESSION_CYCLE = [
        "wide establishing",
        "medium contextual",
        "close-up detail",
        "human interaction",
        "macro / visual metaphor",
        "wide payoff"
    ]

    def get_desired_next_shot(self, previous_shot_meta: Optional[Dict[str, Any]] = None, beat_index: int = 1) -> Dict[str, Any]:
        """
        Determines the optimal shot type and framing to cut to, avoiding visual stagnation.
        """
        if not previous_shot_meta:
            return {
                "desired_framing": "wide establishing",
                "desired_motion": "slow push-in",
                "avoid": ["extreme_closeup_first", "chaotic_handheld"],
                "editorial_intent": "Establish geographic and spatial physical reality."
            }

        prev_framing = previous_shot_meta.get("framing", "wide")
        prev_subject = previous_shot_meta.get("subject", "")
        prev_motion = previous_shot_meta.get("motion", "")

        # Cycle sequence dynamically
        next_cycle_index = (beat_index - 1) % len(self.PROGRESSION_CYCLE)
        recommended_framing = self.PROGRESSION_CYCLE[next_cycle_index]

        # Explicit transitions
        avoid_rules = [
            f"same_scale_as_{prev_framing}",
            "visual_monotony",
            "jump_cut_scale"
        ]

        if "wide" in prev_framing.lower():
            desired_framings = ["medium contextual", "close-up detail"]
        elif "medium" in prev_framing.lower():
            desired_framings = ["close-up detail", "macro / visual metaphor", "wide payoff"]
        else:
            desired_framings = ["medium contextual", "wide establishing"]

        return {
            "previous_shot": {
                "framing": prev_framing,
                "subject": prev_subject,
                "motion": prev_motion
            },
            "desired_framings": desired_framings,
            "recommended_framing": recommended_framing,
            "avoid": avoid_rules,
            "editorial_intent": f"Cut from {prev_framing} to fresh focal length to advance narrative rhythm."
        }

    def compute_redundancy_penalty(self, candidate_meta: Dict[str, Any], previous_shot_meta: Optional[Dict[str, Any]]) -> float:
        """
        Calculates penalty deduction [0.0 to 0.40] if candidate repeats previous visual state.
        """
        if not previous_shot_meta:
            return 0.0

        penalty = 0.0
        cand_title = candidate_meta.get("title", "").lower()
        cand_tags = [t.lower() for t in candidate_meta.get("tags", [])]
        prev_subject = previous_shot_meta.get("subject", "").lower()
        prev_framing = previous_shot_meta.get("framing", "").lower()

        # Same subject and same scale check
        subject_repeat = prev_subject and (prev_subject in cand_title or any(prev_subject in t for t in cand_tags))
        framing_repeat = prev_framing and any(f in cand_title for f in ["aerial", "wide", "closeup", "macro"] if f in prev_framing)

        if subject_repeat and framing_repeat:
            penalty += 0.30  # Heavy penalty for identical visual repetition

        elif subject_repeat:
            penalty += 0.12  # Mild penalty for repeated subject without varied framing

        return penalty


sequence_engine = SequenceEngine()
