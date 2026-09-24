"""
Narrative Classifier and Visual Job Engine.
Assigns explicit directorial purpose and editorial avoid guardrails to every script beat.
"""

from typing import List, Dict, Tuple
import re


class NarrativeClassifier:
    VISUAL_JOBS = [
        "establish",
        "explain",
        "illustrate",
        "contextualize",
        "prove",
        "humanize",
        "emphasize",
        "contrast",
        "transition",
        "foreshadow",
        "dramatize",
        "visualize_abstract_concept",
        "provide_atmosphere"
    ]

    NARRATIVE_FUNCTIONS = {
        "A": "Literal Evidence",
        "B": "Context",
        "C": "Explanation",
        "D": "Emotional Reinforcement",
        "E": "Visual Metaphor",
        "F": "Transition",
        "G": "Establishing",
        "H": "Humanization",
        "I": "Contrast",
        "J": "Visual Rhythm"
    }

    # Anti-patterns based on narration context
    AVOID_PATTERNS = {
        "cost_expensive": {
            "triggers": ["expensive", "cost", "billion", "spending", "margin", "capital", "burn rate"],
            "avoid": ["humanoid_robot", "random_laptop_screen", "generic_futuristic_graphics", "green_cash_flying"],
            "reason": "Communicates high-tech hype or cartoonish money, failing to convey true enterprise operational capital and balance sheet gravity."
        },
        "neural_ai": {
            "triggers": ["ai", "model", "algorithm", "intelligence", "neural", "weights"],
            "avoid": ["glowing_human_brain_render", "blue_matrix_code_stream", "robot_hand_touching_human", "smiling_cyborg"],
            "reason": "Severe AI visual slop. Lowers documentary credibility. Prefer physical silicon dies, server arrays, cleanroom technicians, or infrastructure scale."
        },
        "speed_growth": {
            "triggers": ["demand", "exponential", "growth", "surpassed", "record", "fastest"],
            "avoid": ["green_arrow_pointing_up", "sprouting_plant", "generic_stock_handshake", "clapping_executives"],
            "reason": "Amateur corporate video tropes. Replace with kinetic visual metaphors: nocturnal highway time-lapse, automated port logistics, or structural steel assembly."
        },
        "labor_robotics": {
            "triggers": ["robot", "robotics", "automation", "assembly", "factory"],
            "avoid": ["white_plastic_toy_robot", "creepy_uncanny_android_face", "sci-fi_laser_gun"],
            "reason": "Distorts real industrial manufacturing. Focus on precision six-axis articulated arms, hydraulic actuators, cleanroom testing rigs, or AGVs."
        },
        "wealth_finance": {
            "triggers": ["wealth", "rich", "luxury", "money", "investing", "portfolio", "millionaire", "billionaire", "asset", "passive income"],
            "avoid": ["guy_in_suit_throwing_money", "rolex_watch_flex_stock", "ferrari_accelerating_generic", "piggy_bank_coins", "neon_crypto_charts"],
            "reason": "Cheap get-rich-quick 'guru' cliches destroy audience trust. Direct the visual edit towards institutional finance, architectural restraint, quiet luxury, real asset custody, or historical industrial wealth."
        },
        "mental_psychology": {
            "triggers": ["mind", "mental", "brain", "psychology", "focus", "discipline", "dopamine", "anxiety", "burnout", "stoic", "ego"],
            "avoid": ["person_screaming_holding_head", "generic_brain_puzzle_pieces", "sad_face_stock_actor_against_window", "zen_stones_stacked_water"],
            "reason": "Avoids melodrama and spa wellness cliches. Direct the visual edit towards solitary deep work, stark architectural symmetry, biometric monitors, early dawn discipline, or quiet introspective movement."
        },
        "wellness_health": {
            "triggers": ["wellness", "health", "longevity", "vitality", "sleep", "fasting", "fitness", "recovery", "meditation", "diet"],
            "avoid": ["measuring_tape_around_apple", "smiling_doctor_with_stethoscope", "generic_yoga_pose_beach_sunrise", "green_salad_smiling_woman"],
            "reason": "Avoids daytime talk-show stock slop. Direct the visual edit towards cold plunges, circadian morning sunlight, endurance athletes in rain, biological laboratory assays, or physiological data tracking."
        }
    }

    def classify_visual_job(self, text: str, section_title: str) -> List[str]:
        """
        Determines the visual job(s) for a given narration line.
        """
        lower = text.lower()
        title = section_title.lower()
        jobs = []

        if any(w in title for w in ["hook", "intro", "01", "opening"]):
            jobs.append("establish")
            jobs.append("dramatize")
        elif any(w in title for w in ["climax", "revelation", "shift", "crisis"]):
            jobs.append("emphasize")
            jobs.append("dramatize")
        elif any(w in title for w in ["future", "conclusion", "resolution", "horizon"]):
            jobs.append("transition")
            jobs.append("visualize_abstract_concept")

        # Lexical indicators
        if any(w in lower for w in ["billion", "dollar", "percent", "%", "invested", "spent", "deployed", "records"]):
            jobs.append("prove")
            jobs.append("contextualize")
        if any(w in lower for w in ["because", "how", "means", "thermal", "loops", "connected", "cooling"]):
            jobs.append("explain")
            jobs.append("illustrate")
        if any(w in lower for w in ["human", "worker", "people", "doctor", "surgeon", "operator"]):
            jobs.append("humanize")
        if any(w in lower for w in ["however", "yet", "contrast", "despite", "while", "unlike"]):
            jobs.append("contrast")
        if any(w in lower for w in ["quietly", "silent", "around the clock", "ambient", "night"]):
            jobs.append("provide_atmosphere")

        if not jobs:
            jobs = ["contextualize", "illustrate"]

        return list(dict.fromkeys(jobs))[:3]

    def classify_narrative_function(self, text: str, visual_jobs: List[str]) -> List[str]:
        """
        Maps visual jobs and text into canonical letter-coded narrative functions.
        """
        functions = []
        lower = text.lower()

        if "establish" in visual_jobs:
            functions.append("G — Establishing")
        if "prove" in visual_jobs or any(char.isdigit() for char in text):
            functions.append("A — Literal Evidence")
        if "explain" in visual_jobs or "illustrate" in visual_jobs:
            functions.append("C — Explanation")
        if "contextualize" in visual_jobs:
            functions.append("B — Context")
        if "dramatize" in visual_jobs or "emphasize" in visual_jobs:
            functions.append("D — Emotional Reinforcement")
        if "humanize" in visual_jobs:
            functions.append("H — Humanization")
        if "contrast" in visual_jobs:
            functions.append("I — Contrast")
        if "visualize_abstract_concept" in visual_jobs:
            functions.append("E — Visual Metaphor")
        if "transition" in visual_jobs:
            functions.append("F — Transition")

        if not functions:
            functions = ["B — Context", "J — Visual Rhythm"]

        return functions[:3]

    def get_avoid_criteria(self, text: str) -> Tuple[List[str], str]:
        """
        Derives explicit visual tropes to reject, with editorial rationale.
        """
        lower = text.lower()
        avoid_items = []
        reasons = []

        for category, info in self.AVOID_PATTERNS.items():
            if any(t in lower for t in info["triggers"]):
                avoid_items.extend(info["avoid"])
                reasons.append(info["reason"])

        if not avoid_items:
            avoid_items = ["generic_stock_laptop", "cliché_abstract_shapes", "unmotivated_lens_flare"]
            reasons.append("Rejects low-intent stock footage without specific subject matter relevance.")

        return list(dict.fromkeys(avoid_items)), " ".join(reasons)


narrative_classifier = NarrativeClassifier()
