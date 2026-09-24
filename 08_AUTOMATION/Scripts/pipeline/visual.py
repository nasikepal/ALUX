"""
Visual Intent and Semantic Analysis Engine.
Translates literal narrative lines into physical, shootable cinematic concepts across
Finance, Wealth, Mental Health, Wellness, Stoicism, and Technology.
"""

from typing import List, Dict, Any, Tuple
import re
from core.models import VisualUnit, VisualIntent
from core.logger import logger


class VisualAnalyzer:
    # High-signal domain semantic visual mappings
    DOMAIN_ONTOLOGY = {
        "wealth_luxury": {
            "keywords": ["wealth", "rich", "luxury", "asset", "estate", "capital", "private equity", "portfolio", "passive income", "cash flow", "compounding", "financial freedom", "sovereign", "legacy", "billionaire", "millionaire", "patek", "family office"],
            "primary": ["monolithic modern marble architecture", "executive penthouse skyline view", "tactile fountain pen on bond paper"],
            "secondary": ["private bank vault door", "architectural living room with natural stone", "antique mechanical watch movement"],
            "abstract": ["generational wealth preservation", "financial sovereignty"],
            "camera": "Slow deliberate slider push-in with 50mm prime",
            "lighting": "Warm architectural raking sunlight cutting across textured stone",
            "movement": "Smooth controlled motorized dolly"
        },
        "finance_markets": {
            "keywords": ["market", "stock", "trade", "trading", "hedge fund", "wall street", "federal reserve", "interest rate", "inflation", "bond", "valuation", "balance sheet", "asymmetry", "arbitrage", "liquidity", "leverage", "invest"],
            "primary": ["financial trading floor multi-monitors", "bloomberg terminal data stream", "corporate headquarters skyscraper"],
            "secondary": ["executive contract signing", "central bank architectural facade", "financial district crosswalk"],
            "abstract": ["capital allocation dynamics", "systemic economic forces"],
            "camera": "Low-angle wide tilt looking up at high-rise financial center",
            "lighting": "Crisp corporate cool daylight with sharp reflections",
            "movement": "Vertical crane tilt-up"
        },
        "mental_psychology": {
            "keywords": ["mental", "mind", "brain", "psychology", "focus", "discipline", "dopamine", "addiction", "habit", "anxiety", "stress", "burnout", "depression", "ego", "mindset", "subconscious", "cognitive", "meditation", "attention", "deep work"],
            "primary": ["solitary individual writing in leather journal", "clock ticking in minimalist room", "person meditating in tranquil interior"],
            "secondary": ["rain streaking across dark window pane", "person walking through morning mist", "dense personal library bookshelf"],
            "abstract": ["cognitive clarity and emotional mastery", "monastic focus and inner stillness"],
            "camera": "Intimate close-up macro probe on journal or eyes",
            "lighting": "Natural directional morning window light with soft shadow",
            "movement": "Imperceptible slow push-in"
        },
        "wellness_longevity": {
            "keywords": ["wellness", "health", "longevity", "lifespan", "sleep", "circadian", "fitness", "workout", "training", "nutrition", "diet", "fasting", "recovery", "sauna", "cold plunge", "breathwork", "energy", "vitality", "biomarker", "athletic", "physical"],
            "primary": ["athlete immersing into cold plunge bath", "morning sunlight hitting face outdoors at dawn", "runner breath in crisp cold air"],
            "secondary": ["clean preparation of whole organic foods", "cedar wood sauna with steam rising", "biometric wearable device tracking heart rate"],
            "abstract": ["cellular vitality and biological resilience", "somatic equilibrium and physical peak"],
            "camera": "Low-angle dynamic tracking with 35mm lens",
            "lighting": "Golden dawn backlighting with high dynamic range",
            "movement": "Organic steadycam glide"
        },
        "philosophy_stoicism": {
            "keywords": ["philosophy", "stoic", "stoicism", "virtue", "wisdom", "marcus aurelius", "seneca", "epictetus", "memento mori", "death", "time", "purpose", "meaning", "character", "stillness", "calm"],
            "primary": ["classical marble bust in museum shadow", "monolithic granite cliff against ocean waves", "ancient stone temple ruins"],
            "secondary": ["hourglass sand falling steadily", "solitary figure standing in heavy rain", "old leather-bound philosophy book"],
            "abstract": ["timeless human endurance", "stoic equanimity"],
            "camera": "Static locked-off symmetrical tableau",
            "lighting": "Moody overcast soft slate-grey daylight",
            "movement": "Completely locked tripod"
        },
        "datacenter": {
            "keywords": ["data center", "datacenter", "server", "infrastructure", "compute", "cloud", "hyperscale", "gpu", "clusters"],
            "primary": ["hyperscale data center", "server racks with blinking LEDs", "high-density GPU infrastructure"],
            "secondary": ["cleanroom engineers inspecting hardware", "liquid cooling tubes", "data center aerial exterior"],
            "abstract": ["exponential computing power", "technological capital scaling"],
            "camera": "Slow forward tracking shot through server aisle",
            "lighting": "Deep cobalt blue with bright green/cyan status indicators",
            "movement": "Steady motorized slider push-in"
        },
        "society": {
            "keywords": ["people", "human", "society", "worker", "user", "everyday", "public", "world", "crowd", "community"],
            "primary": ["people walking in modern metropolis", "crowded urban crosswalk", "individual sitting thoughtfully in architectural cafe"],
            "secondary": ["modern light-filled workspace", "commuters on transit", "quiet evening park"],
            "abstract": ["human societal evolution", "collective consciousness"],
            "camera": "Medium tracking shot following protagonist",
            "lighting": "Natural cinematic daylight with soft diffusion",
            "movement": "Handheld steadycam glide"
        }
    }

    ENTITY_PATTERNS = [
        # Finance & Institutions
        r"\b(?:BlackRock|Vanguard|Berkshire Hathaway|Federal Reserve|Goldman Sachs|JPMorgan|Bridgewater|Citadel)\b",
        r"\b(?:OpenAI|Microsoft|NVIDIA|Google|Apple|Tesla|Amazon)\b",
        r"\b(?:New York|London|Singapore|Tokyo|Zurich|Geneva|San Francisco)\b",
        # Figures across Finance, Philosophy, Health
        r"\b(?:Warren Buffett|Charlie Munger|Ray Dalio|Naval Ravikant|Marcus Aurelius|Seneca|Epictetus)\b",
        r"\b(?:Peter Attia|Andrew Huberman|Matthew Walker|David Goggins|Carl Jung|Friedrich Nietzsche)\b",
        # Numeric Claims & Financial Assertions
        r"\b(?:\$\d+(?:\.\d+)?\s*(?:billion|trillion|million|k)?)\b",
        r"\b(?:\d+(?:\.\d+)?\s*(?:%|percent))\b",
        r"\b(?:20\d\d(?:\s*-\s*20\d\d)?)\b"
    ]

    def analyze_unit(self, unit: VisualUnit) -> VisualUnit:
        text = unit.text.lower()
        
        # 1. Extract Entities, Dates, Numbers
        entities = []
        for pat in self.ENTITY_PATTERNS:
            found = re.findall(pat, unit.text, re.IGNORECASE)
            entities.extend(found)
        unit.entities = list(dict.fromkeys(entities))  # Deduplicate

        # 2. Extract Claims (sentences with quantities, declarative investments, or factual assertions)
        claims = []
        sentences = [s.strip() for s in re.split(r"[.!?]", unit.text) if s.strip()]
        for s in sentences:
            if any(k in s.lower() for k in ["billion", "million", "dollar", "percent", "%", "invest", "habit", "study", "research", "shows", "proved", "demonstrated", "rule", "principle"]):
                claims.append(s)
        if not claims and len(sentences) > 0:
            claims.append(sentences[0])
        unit.claims = claims

        # 3. Derive Visual Intent (Primary, Secondary, Abstract, Cinematic Direction)
        matched_domains = []
        for domain, info in self.DOMAIN_ONTOLOGY.items():
            matches = [k for k in info["keywords"] if k in text]
            if matches:
                matched_domains.append((domain, len(matches), info))

        matched_domains.sort(key=lambda x: x[1], reverse=True)

        if matched_domains:
            top_info = matched_domains[0][2]
            primary = list(top_info["primary"])
            secondary = list(top_info["secondary"])
            abstract = list(top_info["abstract"])
            camera = top_info["camera"]
            lighting = top_info["lighting"]
            movement = top_info["movement"]

            # Merge with second domain if available for richer composite intent
            if len(matched_domains) > 1:
                second_info = matched_domains[1][2]
                secondary.append(second_info["primary"][0])
                abstract.append(second_info["abstract"][0])
        else:
            # Fallback for general unclassified narration
            primary = ["cinematic environmental portrait", "architectural minimalism"]
            secondary = ["ambient landscape details", "tactile object closeup"]
            abstract = ["thematic gravity", "narrative progression"]
            camera = "Medium slow push-in with 50mm prime lens"
            lighting = "Cinematic natural directional daylight"
            movement = "Slow smooth slider track"

        # 4. Integrate Full Artistic Logic Engine (6-Level Interpretation & Search Matrix)
        from artistic_logic.visual_interpreter import visual_interpreter
        
        unit.visual_intent = VisualIntent(
            primary=primary,
            secondary=secondary,
            abstract=abstract,
            camera=camera,
            lighting=lighting,
            movement=movement
        )

        interpretation = visual_interpreter.interpret_unit(unit)
        unit.visual_jobs = interpretation["visual_jobs"]
        unit.narrative_functions = interpretation["narrative_functions"]
        unit.visual_strategy = interpretation["strategy"]
        unit.interpretation_levels = interpretation["interpretation_levels"]
        unit.search_matrix = interpretation["search_matrix"]
        unit.avoid_criteria = interpretation["avoid"]
        unit.search_queries = interpretation["prioritized_queries"]

        # Override cinematic attributes from artistic logic engine
        unit.visual_intent.camera = interpretation["cinematic"]["preferred_framing"]
        unit.visual_intent.movement = interpretation["cinematic"]["camera_motion"]
        unit.visual_intent.lighting = interpretation["cinematic"]["lighting_mood"]

        return unit


visual_analyzer = VisualAnalyzer()
