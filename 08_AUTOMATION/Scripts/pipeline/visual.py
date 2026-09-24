"""
Visual Intent and Semantic Analysis Engine.
Translates literal narrative lines into physical, shootable cinematic concepts.
"""

from typing import List, Dict, Any, Tuple
import re
from core.models import VisualUnit, VisualIntent
from core.logger import logger


class VisualAnalyzer:
    # High-signal domain semantic visual mappings
    DOMAIN_ONTOLOGY = {
        "datacenter": {
            "keywords": ["data center", "datacenter", "server", "infrastructure", "compute", "cloud", "hyperscale", "gpu", "clusters"],
            "primary": ["hyperscale data center", "server racks with blinking LEDs", "high-density GPU infrastructure"],
            "secondary": ["cleanroom engineers inspecting hardware", "liquid cooling tubes", "data center aerial exterior"],
            "abstract": ["exponential computing power", "technological capital scaling"],
            "camera": "Slow forward tracking shot through server aisle",
            "lighting": "Deep cobalt blue with bright green/cyan status indicators",
            "movement": "Steady motorized slider push-in"
        },
        "robotics": {
            "keywords": ["robot", "robotics", "humanoid", "automation", "actuator", "dexterous", "cybernetic", "mechanic"],
            "primary": ["humanoid robot walking", "robotic mechanical arm assembling", "bipedal robotic actuators"],
            "secondary": ["engineers calibrating robotic joints", "wire harnesses and electric motors", "laboratory testing floor"],
            "abstract": ["autonomous physical agency", "human-machine synthesis"],
            "camera": "Close-up macro pan across metallic articulated fingers",
            "lighting": "Clean surgical clinical white with rim lighting",
            "movement": "Slow orbital arc around the robot"
        },
        "neural": {
            "keywords": ["neural", "weights", "parameters", "algorithm", "intelligence", "model", "llm", "deep learning", "transformer"],
            "primary": ["silicon wafer microchip closeup", "holographic neural node graph", "macro view of GPU die"],
            "secondary": ["programmer dual monitor code reflection", "quantum circuit schematics", "glass-walled research lab"],
            "abstract": ["synthetic cognition", "digital consciousness matrix"],
            "camera": "Extreme macro rack-focus across silicon circuit paths",
            "lighting": "High-contrast darkroom with amber and teal neon glow",
            "movement": "Gliding slow tilt downward"
        },
        "finance": {
            "keywords": ["billion", "dollar", "capital", "invest", "spending", "venture", "market", "valuation", "trillion"],
            "primary": ["financial trading floor screens", "modern skyscraper corporate headquarters", "digitized financial ticker tape"],
            "secondary": ["executive boardroom meeting", "documents signing and handshake", "money counting machine"],
            "abstract": ["massive capital deployment", "economic market domination"],
            "camera": "Low angle wide tilt looking up at glass skyscraper",
            "lighting": "Sunset golden hour reflecting off high-rise windows",
            "movement": "Rising crane shot"
        },
        "society": {
            "keywords": ["people", "human", "society", "worker", "user", "everyday", "public", "world", "crowd"],
            "primary": ["people using futuristic mobile interfaces", "crowded urban metropolis crosswalk", "creative professional working on tablet"],
            "secondary": ["diverse modern workspace", "people looking at smartphones on subway", "coffee shop remote workers"],
            "abstract": ["mass technological adoption", "societal paradigm transition"],
            "camera": "Medium tracking shot following a walking protagonist",
            "lighting": "Natural cinematic daylight with soft diffusion",
            "movement": "Handheld steadycam glide"
        },
        "laboratory": {
            "keywords": ["lab", "laboratory", "scientist", "researcher", "experiment", "breakthrough", "discovery"],
            "primary": ["scientific research cleanroom", "scientists examining microscopes", "laser optical bench in lab"],
            "secondary": ["gloved hands handling microfluidic chips", "glass whiteboards covered in formulas", "pipettes and test tubes"],
            "abstract": ["scientific exploration", "empirical truth discovery"],
            "camera": "Eye-level medium closeup through laboratory glass partition",
            "lighting": "Clean fluorescent ambient with tungsten accent",
            "movement": "Slow lateral dolly track"
        }
    }

    ENTITY_PATTERNS = [
        r"\b(?:OpenAI|Microsoft|NVIDIA|Google|Meta|Apple|Amazon|Anthropic|Tesla|TSMC|ASML)\b",
        r"\b(?:San Francisco|Silicon Valley|Shenzhen|Tokyo|New York|London|Singapore)\b",
        r"\b(?:Sam Altman|Jensen Huang|Satya Nadella|Elon Musk|Dario Amodei|Demis Hassabis)\b",
        r"\b(?:\$\d+(?:\.\d+)?\s*(?:billion|trillion|million))\b",
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
            if any(k in s.lower() for k in ["billion", "trillion", "invest", "percent", "%", "spent", "built", "invented", "first", "surpassed", "record"]):
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
            # Fallback for generic narration
            words = [w for w in re.findall(r"\w+", unit.text) if len(w) > 4][:3]
            kw_str = " ".join(words)
            primary = [f"{kw_str} conceptual representation", "cinematic technology sequence"]
            secondary = ["modern technology workspace", "focused specialist at workstation"]
            abstract = ["digital era progression", "complex systems operation"]
            camera = "Medium slow push-in"
            lighting = "Atmospheric contrast lighting"
            movement = "Slow smooth forward track"

        unit.visual_intent = VisualIntent(
            primary=primary,
            secondary=secondary,
            abstract=abstract,
            camera=camera,
            lighting=lighting,
            movement=movement
        )

        # 4. Generate targeted search queries for b-roll engines
        search_queries = []
        for p in primary[:2]:
            search_queries.append(f"{p} 4k b-roll")
        for s in secondary[:1]:
            search_queries.append(f"{s} cinematic footage")
        unit.search_queries = search_queries

        return unit


visual_analyzer = VisualAnalyzer()
