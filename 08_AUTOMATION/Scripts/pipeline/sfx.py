"""
Sound Intent and SFX Automation Engine.
Translates visual concepts and emotional cadence into production-ready SFX cues.
"""

from typing import List, Dict, Any, Tuple
from core.models import VisualUnit, SoundIntent, MediaAsset
from providers.local_media import local_media_provider
from core.logger import logger


class SfxAnalyzer:
    SOUND_ONTOLOGY = {
        "datacenter": {
            "ambience": ["server room low drone", "datacenter airflow hum", "electrical substation buzz"],
            "mechanical": ["cooling fan rpm variation", "server hard drive array seek", "chassis latch click"],
            "transition": ["digital data stream whoosh", "subtle tech riser"],
            "emphasis": ["low sub boom impact", "heavy transformer pulse"]
        },
        "robotics": {
            "ambience": ["cleanroom laboratory room tone", "pneumatic compressor hum"],
            "mechanical": ["precision servo motor whine", "metallic finger tap", "hydraulic actuator hiss"],
            "transition": ["mechanical whip pan whoosh", "glitch cyber sweep"],
            "emphasis": ["solid metallic footstep thud", "power-on surge"]
        },
        "neural": {
            "ambience": ["deep binaural synthetic tone", "sub-audible low frequency hum"],
            "mechanical": ["microchip electrical arcing", "relay contact tick", "fast mechanical keyboard"],
            "transition": ["digital stutter sweep", "reverse holographic swell"],
            "emphasis": ["synaptic bass drop", "digital resonant bell"]
        },
        "finance": {
            "ambience": ["busy trading floor murmurs", "city office background rumble"],
            "mechanical": ["high-speed paper bill counter", "fountain pen signature scritch"],
            "transition": ["clean corporate swoosh", "document slide sound"],
            "emphasis": ["dramatic cinematic gavel impact", "deep orchestral sub hit"]
        },
        "society": {
            "ambience": ["distant urban street traffic", "pedestrian crosswalk atmosphere"],
            "mechanical": ["smartphone haptic feedback click", "subway turnstile beep"],
            "transition": ["cinematic wind pass whoosh", "lens shutter snap"],
            "emphasis": ["warm cinematic kick boom", "deep ambient piano chord"]
        }
    }

    def analyze_sound_intent(self, unit: VisualUnit) -> VisualUnit:
        text = f"{unit.text} {' '.join(unit.visual_intent.primary)}".lower()

        # Find closest sound category
        best_category = "datacenter"
        max_hits = 0
        for cat, data in self.SOUND_ONTOLOGY.items():
            hits = sum(1 for word in [cat] + data["ambience"] + data["mechanical"] if word.split()[0] in text)
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
            ("Mechanical", intent.mechanical[0] if intent.mechanical else "Mechanical operation", 89),
            ("Transition", intent.transition[0] if intent.transition else "Digital whoosh", 83),
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
