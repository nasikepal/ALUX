"""
Commercial Stock Footage and Video Search Provider.
Integrates Pexels API and Pixabay API (real results only, needs API keys) plus manual search links.
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
                            "resolution": f"{v['width']}x{v['height']}" if v.get("width") and v.get("height") else "unknown",
                            "license": "Pexels Commercial Free License",
                            "duration": f"{v['duration']}s" if v.get("duration") else "unknown",
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
                        large = (v.get("videos") or {}).get("large") or {}
                        results.append({
                            "title": f"Pixabay Footage: {query.title()}",
                            "asset_type": "footage",
                            "source": "Pixabay",
                            "url": v.get("pageURL"),
                            "resolution": f"{large['width']}x{large['height']}" if large.get("width") and large.get("height") else "unknown",
                            "license": "Pixabay Commercial License",
                            "duration": f"{v['duration']}s" if v.get("duration") else "unknown",
                            "tags": [query.lower()] + [t.strip() for t in v.get("tags", "").split(",")],
                            "description": f"Pixabay footage tags: {v.get('tags', '')}"
                        })
            except Exception as e:
                logger.debug(f"Pixabay search note: {e}")
        return results

    def search_links(self, query: str) -> List[Dict[str, str]]:
        """
        Search pages an editor can browse manually. These are NOT assets: no resolution,
        duration, or license is known until someone opens them and picks a clip.
        """
        q = urllib.parse.quote_plus(query)
        q_path = urllib.parse.quote(query)
        return [
            {"label": "Pexels", "url": f"https://www.pexels.com/search/videos/{q_path}/"},
            {"label": "Pixabay", "url": f"https://pixabay.com/videos/search/{q_path}/"},
            {"label": "Artgrid", "url": f"https://artgrid.io/search?term={q}"},
            {"label": "Storyblocks", "url": f"https://www.storyblocks.com/video/search/{q_path}"},
        ]


stock_footage_provider = StockFootageProvider()
