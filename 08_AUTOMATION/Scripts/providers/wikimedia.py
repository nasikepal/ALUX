"""
Wikimedia Commons Search Provider.
Fetches real public domain and Creative Commons video and high-res media via API.
"""

from typing import List, Dict, Any
import requests
from core.logger import logger


class WikimediaProvider:
    BASE_URL = "https://commons.wikimedia.org/w/api.php"
    VIDEO_EXTS = (".webm", ".ogv", ".mp4", ".mpg", ".mpeg")
    IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp")

    def search_media(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        params = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": f"file:{query}",
            "gsrnamespace": 6,  # File namespace
            "gsrlimit": min(50, limit * 5),  # over-fetch: non-media files get filtered out below
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
                    # Commons search also returns scanned books, PDFs, audio — only footage and stills are B-roll.
                    if not title.lower().endswith(self.VIDEO_EXTS + self.IMAGE_EXTS):
                        continue
                    infos = page.get("imageinfo", [])
                    if infos:
                        info = infos[0]
                        url = info.get("descriptionurl", info.get("url", ""))
                        meta = info.get("extmetadata", {})
                        license_name = meta.get("LicenseShortName", {}).get("value")
                        width, height = info.get("width"), info.get("height")
                        results.append({
                            "title": title.rsplit(".", 1)[0].replace("_", " "),
                            "asset_type": "footage" if title.lower().endswith(self.VIDEO_EXTS) else "image",
                            "source": "Wikimedia Commons",
                            "url": url,
                            "resolution": f"{width}x{height}" if width and height else "unknown",
                            "license": license_name or "unknown — check file page",
                            "duration": "unknown",
                            "tags": [query.lower(), "archive", "commons"],
                            "description": meta.get("ImageDescription", {}).get("value", title)
                        })
        except Exception as e:
            logger.debug(f"Wikimedia search notice for query '{query}': {e}")

        return results[:limit]


wikimedia_provider = WikimediaProvider()
