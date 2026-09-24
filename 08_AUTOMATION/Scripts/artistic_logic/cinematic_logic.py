"""
Cinematic Direction and Editorial Utility Engine.
Defines camera behavior, lighting palettes, composition ratios, and cutting usability.
"""

from typing import Dict, List, Any


class CinematicLogic:
    SHOT_TYPES = ["wide", "medium", "closeup", "macro", "aerial", "pov"]
    CAMERA_MOTIONS = ["slow_push", "tracking", "crane_pedestal", "static", "kinetic_handheld"]

    def determine_cinematic_profile(self, visual_job: List[str], motif: str) -> Dict[str, Any]:
        """
        Derives concrete camera direction and edit behavior.
        """
        # Default cinematic attributes
        framing = "wide establishing"
        motion = "slow motorized push-in"
        lighting = "high-contrast cinematic with rim highlights"
        composition = "strict symmetry with dedicated lower-third graphic space"
        pacing = "deliberate (6s-10s)"

        if "establish" in visual_job:
            framing = "ultra-wide aerial panoramic"
            motion = "smooth forward drone sweep"
            lighting = "horizon backlight with atmospheric haze"
        elif "explain" in visual_job or "illustrate" in visual_job:
            framing = "medium eye-level contextual"
            motion = "slow lateral dolly track"
            lighting = "clean clinical illumination, neutral contrast"
        elif "prove" in visual_job:
            framing = "close-up detail or macro rack-focus"
            motion = "locked-off tripod or micro-slider"
            lighting = "focused directional key light"
        elif "humanize" in visual_job:
            framing = "medium close-up"
            motion = "subtle organic handheld"
            lighting = "soft diffused ambient daylight"
        elif "emphasize" in visual_job or "dramatize" in visual_job:
            framing = "low-angle monolithic wide"
            motion = "steady acceleration push-in"
            lighting = "deep cobalt blue with amber point source"

        return {
            "preferred_framing": framing,
            "camera_motion": motion,
            "lighting_mood": lighting,
            "composition_guide": composition,
            "pacing": pacing,
            "editorial_utility_checks": [
                "minimum_usable_duration >= 4s",
                "clean_negative_space_for_type",
                "stable_motion_no_abrupt_whip",
                "color_grading_latitude"
            ]
        }


cinematic_logic = CinematicLogic()
