"""
Metaphor and Conceptual Transduction Engine.
Maps non-physical or complex abstract ideas into concrete physical filmic analogies across
Finance, Wealth, Mental Health, Wellness, Stoicism, and Technology.
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
        matched_motif = "wealth_capital"

        # 1. Finance & Wealth Motifs
        if any(w in lower for w in ["wealth", "rich", "luxury", "estate", "sovereign", "legacy", "compounding", "dividend", "custody", "allocation", "net worth"]):
            matched_motif = "wealth_capital"
        elif any(w in lower for w in ["risk", "asymmetry", "arbitrage", "trade", "trading", "market", "hedge", "portfolio", "debt", "liquidity", "leverage", "valuation"]):
            matched_motif = "financial_asymmetry"
        
        # 2. Mental & Psychology Motifs
        elif any(w in lower for w in ["focus", "discipline", "deep work", "attention", "concentration", "deliberate", "habit", "monk", "monastic", "routine", "mindset"]):
            matched_motif = "mental_focus"
        elif any(w in lower for w in ["burnout", "exhausted", "exhaustion", "overwhelm", "anxiety", "depression", "insomnia", "restless", "fatigue", "overload"]):
            matched_motif = "mental_burnout"
        elif any(w in lower for w in ["stoic", "stoicism", "clarity", "stillness", "virtue", "calm", "memento mori", "equanimity", "endurance", "philosophy"]):
            matched_motif = "stoic_clarity"

        # 3. Wellness & Longevity Motifs
        elif any(w in lower for w in ["wellness", "health", "longevity", "vitality", "cold plunge", "training", "workout", "endurance", "running", "muscle", "nutrition", "fasting", "biomarker"]):
            matched_motif = "wellness_vitality"
        elif any(w in lower for w in ["sleep", "recovery", "sauna", "breathwork", "parasympathetic", "rest", "restoration", "unwind", "recharge", "meditation"]):
            matched_motif = "recovery_restoration"

        # 4. Classical Motifs (Scale, Urgency, Growth, Power, Precision, Automation)
        elif any(w in lower for w in ["demand", "urgent", "fast", "race", "rapid", "acceleration"]):
            matched_motif = "urgency"
        elif any(w in lower for w in ["build", "building", "expansion", "growth", "deployment"]):
            matched_motif = "growth"
        elif any(w in lower for w in ["billion", "power", "monopoly", "massive", "domination"]):
            matched_motif = "power"
        elif any(w in lower for w in ["uncertain", "fear", "crisis", "black box", "unseen", "doubt"]):
            matched_motif = "uncertainty"
        elif any(w in lower for w in ["precision", "sub-millimeter", "microscopic", "wafer", "lithography", "clock", "exact"]):
            matched_motif = "precision"
        elif any(w in lower for w in ["robot", "autonomous", "actuator", "assembly", "factory"]):
            matched_motif = "automation"
        elif any(w in lower for w in ["scale", "vast", "monumental", "infrastructure", "global"]):
            matched_motif = "scale"

        motif_data = self.vocabulary.get(matched_motif, self.vocabulary.get("wealth_capital", {}))
        
        # 1. Literal: Physical entities explicitly mentioned
        literal = [c for c in primary_concepts if len(c) > 2][:3]
        if not literal:
            # Context-sensitive fallback based on motif
            fallbacks = {
                "wealth_capital": ["monolithic modern architecture", "private bank vault"],
                "financial_asymmetry": ["financial market terminal", "official contract signature"],
                "mental_focus": ["solitary study desk", "handcrafted fountain pen"],
                "mental_burnout": ["night skyscraper reflection", "empty late-night office"],
                "stoic_clarity": ["ancient granite cliff", "marble sculpture"],
                "wellness_vitality": ["cold mountain plunge", "dawn outdoor track"],
                "recovery_restoration": ["dark sleeping sanctuary", "cedar wood sauna"]
            }
            literal = fallbacks.get(matched_motif, ["cinematic environmental subject", "architectural detail"])

        # 2. Contextual: Physical environment surrounding the subject
        contextual = motif_data.get("visual_language", ["cinematic architectural environment", "textured landscape"])[:3]

        # 3. Conceptual: Abstract idea communicated
        conceptual = [
            f"{matched_motif.replace('_', ' ').title()} principles",
            "strategic allocation and human agency",
            "structural systemic clarity"
        ]

        # 4. Metaphorical: Physical analogies that communicate the idea without literal depiction
        metaphorical = motif_data.get("visual_metaphors", ["mountain reservoir holding immense energy", "timeless mechanical watch escapement"])[:3]

        return {
            "motif": matched_motif,
            "literal": literal,
            "contextual": contextual,
            "conceptual": conceptual,
            "metaphorical": metaphorical,
            "primary_visual": f"Cinematic {literal[0]} with deliberate camera movement",
            "secondary_visual": f"Contextual {contextual[0]} with high atmospheric contrast",
            "abstract_visual": f"Kinetic metaphor: {metaphorical[0]}",
            "emotional_tone": motif_data.get("emotional_tone", ["gravity", "restraint", "clarity"]),
            "cinematic_cues": motif_data.get("cinematic_cues", {})
        }


metaphor_engine = MetaphorEngine()
