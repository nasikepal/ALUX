"""
Internet Archive Search Provider (archive.org).
Fetches historical clips, documentary b-roll, and open-source recordings.
"""

from typing import List, Dict, Any
import requests
import urllib.parse
from core.logger import logger


class ArchiveOrgProvider:
    BASE_URL = "https://archive.org/advancedsearch.php"

    def search_video(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        clean_q = query.replace('"', '')
        q_string = f'({clean_q}) AND mediatype:(movies)'
        params = {
            "q": q_string,
            "fl[]": ["identifier", "title", "description", "year", "licenseurl"],
            "sort[]": "downloads desc",
            "rows": limit,
            "page": 1,
            "output": "json"
        }
        headers = {
            "User-Agent": "ObsidianProductionOS/1.0"
        }

        results = []
        try:
            resp = requests.get(self.BASE_URL, params=params, headers=headers, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                docs = data.get("response", {}).get("docs", [])
                for doc in docs:
                    identifier = doc.get("identifier")
                    title = doc.get("title", identifier)
                    # archive.org items carry mixed rights; only report a license the item declares.
                    license_url = doc.get("licenseurl")
                    results.append({
                        "title": title,
                        "asset_type": "footage",
                        "source": "Internet Archive",
                        "url": f"https://archive.org/details/{identifier}",
                        "resolution": "unknown",
                        "license": f"Declared: {license_url}" if license_url else "unknown — check item page",
                        "duration": "unknown",
                        "tags": [query.lower(), "archive", "historical", str(doc.get("year", ""))],
                        "description": doc.get("description", title)
                    })
        except Exception as e:
            logger.debug(f"Internet Archive search notice for query '{query}': {e}")

        return results


archive_provider = ArchiveOrgProvider()
