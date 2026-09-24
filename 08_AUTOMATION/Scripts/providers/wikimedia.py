"""
Wikimedia Commons Search Provider.
Fetches real public domain and Creative Commons video and high-res media via API.
"""

from typing import List, Dict, Any
import requests
from core.logger import logger


class WikimediaProvider:
    BASE_URL = "https://commons.wikimedia.org/w/api.php"

    def search_media(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        params = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": f"file:{query}",
            "gsrnamespace": 6,  # File namespace
            "gsrlimit": limit,
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata",
        }
        headers = {
            "User-Agent": "ObsidianProductionOS/1.0 (production-vault-engine)"
        }

        results = []
        try:
            resp = requests.get(self.BASE_URL, params=params, headers=headers, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                for pid, page in pages.items():
                    title = page.get("title", "").replace("File:", "")
                    infos = page.get("imageinfo", [])
                    if infos:
                        info = infos[0]
                        url = info.get("descriptionurl", info.get("url", ""))
                        meta = info.get("extmetadata", {})
                        license_name = meta.get("LicenseShortName", {}).get("value", "Creative Commons")
                        results.append({
                            "title": title.rsplit(".", 1)[0].replace("_", " "),
                            "asset_type": "footage" if title.lower().endswith((".webm", ".ogv", ".mp4")) else "image",
                            "source": "Wikimedia Commons",
                            "url": url,
                            "resolution": f"{info.get('width', 'HD')}x{info.get('height', '')}",
                            "license": f"CC: {license_name}",
                            "duration": "Variable",
                            "tags": [query.lower(), "archive", "commons"],
                            "description": meta.get("ImageDescription", {}).get("value", title)
                        })
        except Exception as e:
            logger.debug(f"Wikimedia search notice for query '{query}': {e}")

        return results


wikimedia_provider = WikimediaProvider()
