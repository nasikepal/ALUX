"""
Fact Verification and Source Research Pipeline.
Separates factual claims from visual styling, validates journalistic sources,
generates permanent Source Notes and Research Inbox triage cards.
"""

from typing import List, Dict, Any, Tuple
from pathlib import Path
import re
import yaml
from core.models import VisualUnit, SourceFact
from providers.news import news_provider
from scoring.relevance import RelevanceEngine
from core.config import config
from core.logger import logger


def sanitize_filename(name: str) -> str:
    clean = re.sub(r'[\\/*?:"<>|#^\[\]]', "", name)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:60]


def source_note_name(fact: SourceFact) -> str:
    """Note name (no extension) of a source note — shared by the writer and every wikilink to it."""
    return f"Source - {sanitize_filename(fact.publisher)} - {sanitize_filename(fact.title)}"


class SourcePipeline:
    def __init__(self):
        self.scorer = RelevanceEngine()

    sanitize_filename = staticmethod(sanitize_filename)

    def process_claims_for_unit(self, unit: VisualUnit) -> List[SourceFact]:
        """
        Searches for sources per claim. Found sources become *candidates* (source note + inbox card
        for human review). Claims with nothing found get an inbox card with research leads and no
        source note — 06_SOURCES only ever holds material a search actually returned.
        """
        candidate_facts: List[SourceFact] = []
        unit.unsourced_claims = {}
        for idx, claim in enumerate(unit.claims):
            claim_id = f"CLAIM-{unit.id.split('-')[-1]}-{idx+1:02d}"
            hits = news_provider.search_claim_sources(claim, limit=2)
            if not hits:
                leads = news_provider.research_leads(claim)
                unit.unsourced_claims[claim] = leads
                self.write_unsourced_inbox_card(claim_id, claim, leads, unit)
                continue

            for hit in hits:
                score, cred = self.scorer.score_source_fact(hit, claim)
                fact = SourceFact(
                    claim_id=claim_id,
                    claim_text=claim,
                    source_type="news",
                    title=hit.get("title") or "Untitled source",
                    publisher=hit.get("publisher") or "Unknown publisher",
                    url=hit.get("url", ""),
                    published_date=hit.get("published_date") or "unknown",
                    credibility=cred,
                    relevance_score=score,
                    excerpt=hit.get("excerpt", ""),
                    verification_status="candidate",
                    match_type=hit.get("match_type", "")
                )
                candidate_facts.append(fact)

                # 1. Write candidate Source Note in 06_SOURCES/News/
                self.write_source_note(fact)

                # 2. Write triage card in 03_RESEARCH/_INBOX/
                self.write_inbox_card(fact, unit)

        unit.source_matches = candidate_facts
        return candidate_facts

    def write_source_note(self, fact: SourceFact) -> Path:
        """Writes canonical source note in 06_SOURCES/News/"""
        target_dir = config.sources_dir / "News"
        target_dir.mkdir(parents=True, exist_ok=True)

        file_path = target_dir / f"{source_note_name(fact)}.md"

        frontmatter = {
            "type": "source",
            "source_type": fact.source_type,
            "title": fact.title,
            "publisher": fact.publisher,
            "url": fact.url,
            "published": fact.published_date,
            "credibility": fact.credibility,
            "keyword_match": int(round(fact.relevance_score * 100)),
            "verification_status": fact.verification_status,
            "match_type": fact.match_type,
            "related_claims": [fact.claim_id]
        }

        content = f"""---
{yaml.dump(frontmatter, sort_keys=False).strip()}
---

# {fact.title}

> [!warning] Candidate source — not verified
> Found automatically by search. A human must open the link and confirm it actually supports the claim
> before it is cited on screen. Mark the Research Inbox card as Accept to promote it.

- **Publisher**: {fact.publisher}
- **URL**: [{fact.url}]({fact.url})
- **Published Date**: {fact.published_date}
- **Publisher Reputation**: `{fact.credibility.upper()}`
- **Keyword Match with Claim**: {int(round(fact.relevance_score * 100))}% (topical overlap only — not proof)

## Claim Under Review
> {fact.claim_text}

## Excerpt (as returned by search)
> {fact.excerpt or '(no excerpt returned)'}

## Production Cross-References
- Related Claim ID: `{fact.claim_id}`
- Status: `{fact.verification_status}`
"""
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def write_inbox_card(self, fact: SourceFact, unit: VisualUnit) -> Path:
        """Writes triage note in 03_RESEARCH/_INBOX/ for human-in-the-loop validation."""
        target_dir = config.research_inbox_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        safe_title = self.sanitize_filename(fact.title)
        filename = f"INBOX - {unit.id} - {safe_title}.md"
        file_path = target_dir / filename

        frontmatter = {
            "type": "research_result",
            "status": "unreviewed",
            "source": fact.publisher,
            "keyword_match": int(round(fact.relevance_score * 100)),
            "verification_status": fact.verification_status,
            "related_visual": unit.id,
            "claim_id": fact.claim_id
        }

        content = f"""---
{yaml.dump(frontmatter, sort_keys=False).strip()}
---

# Research Inbox: {fact.title}

- **Source**: {fact.publisher}
- **URL**: [{fact.url}]({fact.url})
- **Keyword Match**: {int(round(fact.relevance_score * 100))}% (topical overlap only)
- **Publisher Reputation**: `{fact.credibility.upper()}`
- **Related Visual Unit**: [[{unit.id}]] (`{unit.script_section}`)

### Claim Under Examination
> {fact.claim_text}

### What to check
> Search returned this page for the claim. Open it and confirm it states the specific fact
> (numbers, dates, names) — a page on the same topic is not confirmation.

### Production Decision
- [ ] Accept (source confirms the claim — set `verification_status: verified`)
- [ ] Reject (does not support the claim)
- [ ] Save for Archive
"""
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def write_unsourced_inbox_card(self, claim_id: str, claim: str, leads: List[Dict[str, str]], unit: VisualUnit) -> Path:
        """Writes a triage card for a claim no search could source — research leads only, no source note."""
        target_dir = config.research_inbox_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        filename = f"INBOX - {unit.id} - {claim_id} - NO SOURCE FOUND.md"
        file_path = target_dir / filename

        frontmatter = {
            "type": "research_result",
            "status": "unreviewed",
            "verification_status": "unverified",
            "related_visual": unit.id,
            "claim_id": claim_id
        }
        lead_lines = "\n".join(f"- [{l['label']}]({l['url']})" for l in leads)

        content = f"""---
{yaml.dump(frontmatter, sort_keys=False).strip()}
---

# Research Inbox: {claim_id} — no source found

> [!danger] Unsourced claim
> Automated search found nothing for this claim. Do not put it on screen until a researcher finds a source.

- **Related Visual Unit**: [[{unit.id}]] (`{unit.script_section}`)

### Claim
> {claim}

### Research leads (search links — not sources)
{lead_lines}

### Production Decision
- [ ] Source found (create a note in 06_SOURCES and link it here)
- [ ] Rewrite or cut the claim
"""
        file_path.write_text(content, encoding="utf-8")
        return file_path


source_pipeline = SourcePipeline()
