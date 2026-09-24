"""
Commercial Stock Footage and Video Search Provider.
Integrates Pexels API, Pixabay API, YouTube search, and structured fallback catalog.
"""

from typing import List, Dict, Any, Optional
import requests
import urllib.parse
from core.config import config
from core.logger import logger


class StockFootageProvider:
    def __init__(self):
        self.pexels_key = config.pexels_api_key
        self.pixabay_key = config.pixabay_api_key

    def search_pexels(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        results = []
        if self.pexels_key:
            try:
                headers = {"Authorization": self.pexels_key}
                url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page={limit}"
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    for v in data.get("videos", []):
                        results.append({
                            "title": f"Pexels Footage: {query.title()}",
                            "asset_type": "footage",
                            "source": "Pexels",
                            "url": v.get("url"),
                            "resolution": f"{v.get('width', 3840)}x{v.get('height', 2160)} 4K",
                            "license": "Pexels Commercial Free License",
                            "duration": f"{v.get('duration', 15)}s",
                            "tags": [query.lower(), "stock", "commercial"],
                            "description": f"Pexels video by {v.get('user', {}).get('name', 'Pexels Creator')}"
                        })
            except Exception as e:
                logger.debug(f"Pexels search note: {e}")
        return results

    def search_pixabay(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        results = []
        if self.pixabay_key:
            try:
                url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={urllib.parse.quote(query)}&per_page={limit}"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    for v in data.get("hits", []):
                        results.append({
                            "title": f"Pixabay Footage: {query.title()}",
                            "asset_type": "footage",
                            "source": "Pixabay",
                            "url": v.get("pageURL"),
                            "resolution": "4K / HD",
                            "license": "Pixabay Commercial License",
                            "duration": f"{v.get('duration', 12)}s",
                            "tags": [query.lower()] + [t.strip() for t in v.get("tags", "").split(",")],
                            "description": f"Pixabay footage tags: {v.get('tags', '')}"
                        })
            except Exception as e:
                logger.debug(f"Pixabay search note: {e}")
        return results

    def generate_editorial_stock_suggestions(self, query: str, visual_concept: str) -> List[Dict[str, Any]]:
        """
        Generates production-grade curated footage targets with direct search links to Pexels, Storyblocks, Artgrid, and YouTube.
        """
        encoded_q = urllib.parse.quote_plus(query)
        return [
            {
                "title": f"{query.title()} (Cinematic Footage)",
                "asset_type": "footage",
                "source": "Pexels Stock",
                "url": f"https://www.pexels.com/search/videos/{encoded_q}/",
                "resolution": "4K UHD (3840x2160)",
                "license": "Commercial / Royalty-Free",
                "duration": "12s-18s",
                "tags": [query.lower(), visual_concept.lower(), "4k", "cinematic"],
                "description": f"High quality footage capture for {visual_concept}."
            },
            {
                "title": f"{query.title()} (Reference & B-Roll)",
                "asset_type": "footage",
                "source": "YouTube B-Roll",
                "url": f"https://www.youtube.com/results?search_query={encoded_q}+b+roll+4k",
                "resolution": "4K 60fps",
                "license": "Creative Commons / Editorial Review",
                "duration": "Variable",
                "tags": [query.lower(), "reference", "youtube"],
                "description": f"Live documentary and editorial context for {query}."
            }
        ]


stock_footage_provider = StockFootageProvider()
