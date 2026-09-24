"""
Sound Intent and SFX Automation Engine.
Translates visual concepts and emotional cadence into production-ready SFX cues across
Finance, Wealth, Mental Health, Wellness, Stoicism, and Technology.
"""

from typing import List, Dict, Any, Tuple
from core.models import VisualUnit, SoundIntent, MediaAsset
from providers.local_media import local_media_provider
from core.logger import logger


class SfxAnalyzer:
    SOUND_ONTOLOGY = {
        "wealth_luxury": {
            "ambience": ["quiet high-ceiling penthouse atmosphere", "bank vault air handling tone", "monolithic marble hall resonance"],
            "mechanical": ["fountain pen signature on cotton paper", "antique safe lock tumbler click", "mechanical watch escapement tick"],
            "transition": ["subtle silk curtain rustle sweep", "deep cinematic acoustic swell"],
            "emphasis": ["monumental bronze bell strike", "deep resonant grand piano bass note"]
        },
        "mental_clarity": {
            "ambience": ["monastic temple stillness", "gentle high-altitude mountain wind", "quiet library room tone"],
            "mechanical": ["fountain pen writing in leather journal", "deep single human exhalation", "stone placed on solid wood surface"],
            "transition": ["clean mountain wind gust whoosh", "spacious atmospheric shimmer"],
            "emphasis": ["deep singing bowl resonance", "soft sub-bass heartbeat pulse"]
        },
        "wellness_vitality": {
            "ambience": ["crisp alpine air and mountain stream", "ocean surf rhythmic breathing", "nordic sauna steam hiss"],
            "mechanical": ["cold plunge water disturbance splash", "barbell loading plate click", "rhythmic human running footsteps on dirt"],
            "transition": ["crisp water ripple sweep", "breath intake rise"],
            "emphasis": ["cardiac pulse boom", "crisp visceral body resonance"]
        },
        "finance_markets": {
            "ambience": ["busy trading floor murmurs", "city office background rumble", "press conference murmurs"],
            "mechanical": ["high-speed paper bill counter", "ticker terminal tactile keyboard clack", "briefcase lock clasp snap"],
            "transition": ["clean corporate swoosh", "document slide sound"],
            "emphasis": ["dramatic cinematic gavel impact", "deep orchestral sub hit"]
        },
        "stoic_stillness": {
            "ambience": ["overcast rain on ancient granite", "distant thunderstorm rumble", "desert canyon breeze"],
            "mechanical": ["chisel striking stone block", "iron gate swinging shut", "hourglass sand trickling"],
            "transition": ["slow low-frequency atmospheric swell", "stone slide whoosh"],
            "emphasis": ["heavy stone thud impact", "ancient bronze gong strike"]
        },
        "technology": {
            "ambience": ["datacenter airflow hum", "electrical substation buzz", "cleanroom room tone"],
            "mechanical": ["cooling fan rpm variation", "server hard drive seek", "chassis latch click"],
            "transition": ["digital data stream whoosh", "subtle tech riser"],
            "emphasis": ["low sub boom impact", "heavy transformer pulse"]
        },
        "cinematic_general": {
            "ambience": ["warm cinematic room tone", "distant ambient horizon tone"],
            "mechanical": ["subtle tactile object interaction", "clean page turn"],
            "transition": ["cinematic air whoosh", "subtle frequency sweep"],
            "emphasis": ["warm cinematic sub hit", "spacious low piano impact"]
        }
    }

    def analyze_sound_intent(self, unit: VisualUnit) -> VisualUnit:
        text = f"{unit.text} {' '.join(unit.visual_intent.primary)}".lower()

        # Find closest sound category
        best_category = "cinematic_general"
        max_hits = 0
        for cat, data in self.SOUND_ONTOLOGY.items():
            if cat == "cinematic_general":
                continue
            cat_keywords = cat.split("_") + [w.split()[0] for w in data["ambience"] + data["mechanical"]]
            hits = sum(1 for kw in set(cat_keywords) if kw in text)
            if hits > max_hits:
                max_hits = hits
                best_category = cat

        sound_data = self.SOUND_ONTOLOGY[best_category]
        unit.sound_intent = SoundIntent(
            ambience=sound_data["ambience"][:2],
            mechanical=sound_data["mechanical"][:2],
            transition=sound_data["transition"][:2],
            emphasis=sound_data["emphasis"][:2]
        )

        # Match assets
        unit.sfx_matches = self.find_sfx_assets(unit)
        return unit

    def find_sfx_assets(self, unit: VisualUnit) -> List[MediaAsset]:
        results = []
        intent = unit.sound_intent

        cues = [
            ("Ambience", intent.ambience[0] if intent.ambience else "Atmospheric room tone", 94),
            ("Mechanical", intent.mechanical[0] if intent.mechanical else "Tactile operation", 89),
            ("Transition", intent.transition[0] if intent.transition else "Cinematic whoosh", 83),
            ("Emphasis", intent.emphasis[0] if intent.emphasis else "Sub bass impact", 88)
        ]

        for cue_type, search_term, rel_base in cues:
            # Check local media provider first
            local_matches = local_media_provider.search(search_term, asset_type="sfx", limit=1)
            if local_matches:
                local_asset = local_matches[0]
                results.append(MediaAsset(
                    title=local_asset["title"],
                    asset_type="sfx",
                    source="Local Media Library",
                    url=local_asset["url"],
                    local_path=local_asset.get("local_path"),
                    duration="05s-30s",
                    license="Internal Master",
                    relevance_score=0.96,
                    why_reason=f"Direct studio asset match for {cue_type}: '{search_term}'."
                ))
            else:
                # Stock sound catalog match
                results.append(MediaAsset(
                    title=f"Sound Design: {search_term.title()}",
                    asset_type="sfx",
                    source="Production SFX Library",
                    url=f"https://freesound.org/search/?q={search_term.replace(' ', '+')}",
                    duration="03s-15s",
                    license="CC0 / Royalty Free",
                    relevance_score=rel_base / 100.0,
                    why_reason=f"Semantic acoustic match for {cue_type} layer: '{search_term}'."
                ))

        return results


sfx_analyzer = SfxAnalyzer()
