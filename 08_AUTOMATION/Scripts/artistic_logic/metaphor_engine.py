"""
Metaphor and Conceptual Transduction Engine.
Maps non-physical or complex abstract ideas into concrete physical filmic analogies.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
from core.logger import logger


class MetaphorEngine:
    def __init__(self):
        self.vocab_path = Path(__file__).resolve().parent / "visual_vocabulary.yaml"
        self.vocabulary: Dict[str, Any] = {}
        self.load_vocabulary()

    def load_vocabulary(self):
        if self.vocab_path.exists():
            try:
                content = self.vocab_path.read_text(encoding="utf-8")
                self.vocabulary = yaml.safe_load(content) or {}
            except Exception as e:
                logger.warning(f"Could not load visual vocabulary: {e}")

    def derive_visual_strategy(self, text: str, primary_concepts: List[str]) -> Dict[str, Any]:
        """
        Synthesizes literal, contextual, conceptual, and metaphorical visual tiers.
        """
        lower = text.lower()
        matched_motif = "scale"

        # Determine dominant thematic motif
        if any(w in lower for w in ["demand", "urgent", "fast", "race", "rapid", "acceleration"]):
            matched_motif = "urgency"
        elif any(w in lower for w in ["build", "building", "expansion", "invested", "spent", "growth", "deployment"]):
            matched_motif = "growth"
        elif any(w in lower for w in ["billion", "power", "monopoly", "sovereign", "domination", "massive"]):
            matched_motif = "power"
        elif any(w in lower for w in ["uncertain", "risk", "fear", "crisis", "black box", "unseen"]):
            matched_motif = "uncertainty"
        elif any(w in lower for w in ["precision", "sub-millimeter", "microscopic", "wafer", "lithography", "clock"]):
            matched_motif = "precision"
        elif any(w in lower for w in ["robot", "autonomous", "actuator", "assembly", "factory"]):
            matched_motif = "automation"

        motif_data = self.vocabulary.get(matched_motif, self.vocabulary.get("scale", {}))
        
        # 1. Literal: Physical entities explicitly mentioned
        literal = [c for c in primary_concepts if len(c) > 2][:3]
        if not literal:
            literal = ["hyperscale facility", "hardware assembly"]

        # 2. Contextual: Physical environment surrounding the subject
        contextual = motif_data.get("visual_language", ["industrial infrastructure", "technology facility"])[:3]

        # 3. Conceptual: Abstract idea communicated
        conceptual = [
            f"{matched_motif.replace('_', ' ')} of technological capability",
            "physical capital allocation",
            "systemic structural transformation"
        ]

        # 4. Metaphorical: Physical analogies that communicate the idea without literal depiction
        metaphorical = motif_data.get("visual_metaphors", ["arterial transit networks", "massive hydroelectric dams"])[:3]

        return {
            "motif": matched_motif,
            "literal": literal,
            "contextual": contextual,
            "conceptual": conceptual,
            "metaphorical": metaphorical,
            "primary_visual": f"Massive {literal[0]} with deliberate camera movement",
            "secondary_visual": f"Contextual {contextual[0]} with high atmospheric contrast",
            "abstract_visual": f"Kinetic metaphor: {metaphorical[0]}",
            "emotional_tone": motif_data.get("emotional_tone", ["scale", "technological gravity"]),
            "cinematic_cues": motif_data.get("cinematic_cues", {})
        }


metaphor_engine = MetaphorEngine()
