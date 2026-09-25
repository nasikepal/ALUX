"""
News, Scientific, and Official Source Discovery Provider.

Honesty rule: this provider only returns sources that a search actually found.
It never invents a publisher, excerpt, date, or credibility grade. When nothing
is found, callers get an empty list and can offer `research_leads()` instead —
search links a human researcher can follow, clearly labelled as NOT sources.
"""

from typing import List, Dict, Any
import requests
import urllib.parse
import re
from core.logger import logger


class NewsProvider:
    def search_claim_sources(self, claim: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Looks up real reference material for a claim via the DuckDuckGo Instant Answer API.
        Returns only what the API actually returned. Every hit is a *candidate* that still
        needs human review — a topical reference page is not proof of a specific claim.
        """
        results = []
        encoded = urllib.parse.quote_plus(claim)

        try:
            ddg_url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
            headers = {"User-Agent": "ALUXProductionOS/1.0 (research-assistant)"}
            resp = requests.get(ddg_url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("AbstractText") and data.get("AbstractURL"):
                    results.append({
                        "title": data.get("Heading") or claim[:60],
                        "publisher": data.get("AbstractSource") or "Unknown publisher",
                        "url": data.get("AbstractURL"),
                        "published_date": "unknown",
                        "match_type": "reference_abstract",
                        "excerpt": data.get("AbstractText", "")
                    })
                for topic in data.get("RelatedTopics", []):
                    if len(results) >= limit:
                        break
                    if "Text" in topic and "FirstURL" in topic:
                        results.append({
                            "title": topic["Text"][:80],
                            "publisher": "DuckDuckGo related topic",
                            "url": topic["FirstURL"],
                            "published_date": "unknown",
                            "match_type": "related_topic",
                            "excerpt": topic["Text"]
                        })
        except Exception as e:
            logger.debug(f"DuckDuckGo search note: {e}")

        return results[:limit]

    def research_leads(self, claim: str) -> List[Dict[str, str]]:
        """
        Search links for a human researcher to follow up on an unsourced claim.
        These are starting points, not sources — nothing here verifies anything.
        """
        clean = re.sub(r"[^\w\s$%.,-]", "", claim).strip()
        q = urllib.parse.quote_plus(clean)
        lower = clean.lower()

        leads = [
            {"label": "Google News", "url": f"https://news.google.com/search?q={q}"},
            {"label": "Reuters search", "url": f"https://www.reuters.com/site-search/?query={q}"},
            {"label": "AP News search", "url": f"https://apnews.com/search?q={q}"},
        ]
        if any(w in lower for w in ["brain", "psycholog", "dopamine", "anxiety", "depression",
                                     "sleep", "health", "longevity", "study", "research", "scientist"]):
            leads.append({"label": "PubMed search", "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={q}"})
            leads.append({"label": "Google Scholar", "url": f"https://scholar.google.com/scholar?q={q}"})
        if any(w in lower for w in ["billion", "million", "$", "%", "market", "fund", "revenue",
                                     "wealth", "invest", "company", "stock"]):
            leads.append({"label": "Bloomberg search", "url": f"https://www.bloomberg.com/search?query={q}"})
            leads.append({"label": "SEC EDGAR full-text", "url": f"https://www.sec.gov/edgar/search/#/q={q}"})
        return leads


news_provider = NewsProvider()
