"""
Core configuration for the Obsidian Production OS.
"""

from dataclasses import dataclass, field
from pathlib import Path
import json
import os
import yaml


# Vault root is 2 levels up from 08_AUTOMATION/Scripts/core
VAULT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


@dataclass
class RelevanceWeights:
    semantic_relevance: float = 0.20
    narrative_function: float = 0.15
    visual_specificity: float = 0.15
    artistic_interpretation: float = 0.15
    cinematic_compatibility: float = 0.10
    temporal_relevance: float = 0.10
    geographic_relevance: float = 0.05
    editorial_utility: float = 0.05
    source_quality: float = 0.05

    def validate(self) -> bool:
        total = (
            self.semantic_relevance
            + self.narrative_function
            + self.visual_specificity
            + self.artistic_interpretation
            + self.cinematic_compatibility
            + self.temporal_relevance
            + self.geographic_relevance
            + self.editorial_utility
            + self.source_quality
        )
        return abs(total - 1.0) < 1e-4


@dataclass
class Config:
    vault_root: Path = field(default_factory=lambda: VAULT_ROOT)
    local_media_root: Path = field(default_factory=lambda: Path(r"D:\MEDIA_LIBRARY"))
    
    # Vault subdirectories
    system_dir: Path = field(default_factory=lambda: VAULT_ROOT / "00_SYSTEM")
    projects_dir: Path = field(default_factory=lambda: VAULT_ROOT / "01_PROJECTS")
    scripts_dir: Path = field(default_factory=lambda: VAULT_ROOT / "02_SCRIPTS")
    research_dir: Path = field(default_factory=lambda: VAULT_ROOT / "03_RESEARCH")
    media_dir: Path = field(default_factory=lambda: VAULT_ROOT / "04_MEDIA")
    shots_dir: Path = field(default_factory=lambda: VAULT_ROOT / "05_SHOTS")
    sources_dir: Path = field(default_factory=lambda: VAULT_ROOT / "06_SOURCES")
    database_dir: Path = field(default_factory=lambda: VAULT_ROOT / "07_DATABASE")
    automation_dir: Path = field(default_factory=lambda: VAULT_ROOT / "08_AUTOMATION")
    templates_dir: Path = field(default_factory=lambda: VAULT_ROOT / "99_TEMPLATES")
    
    # Specific specialized paths
    research_inbox_dir: Path = field(default_factory=lambda: VAULT_ROOT / "03_RESEARCH" / "_INBOX")
    local_media_index_path: Path = field(default_factory=lambda: VAULT_ROOT / "08_AUTOMATION" / "Search" / "local_media_index.json")
    
    # Settings & Scoring
    weights: RelevanceWeights = field(default_factory=RelevanceWeights)
    words_per_second: float = 2.4  # ~144 words per minute speaking rate
    
    # API configuration
    pexels_api_key: str = field(default_factory=lambda: os.environ.get("PEXELS_API_KEY", ""))
    pixabay_api_key: str = field(default_factory=lambda: os.environ.get("PIXABAY_API_KEY", ""))
    youtube_api_key: str = field(default_factory=lambda: os.environ.get("YOUTUBE_API_KEY", ""))
    openai_api_key: str = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY", ""))
    gemini_api_key: str = field(default_factory=lambda: os.environ.get("GEMINI_API_KEY", ""))
    
    def load_from_settings(self):
        """Loads optional overrides from 00_SYSTEM/Settings.md if available."""
        settings_file = self.system_dir / "Settings.md"
        if not settings_file.exists():
            return
            
        try:
            content = settings_file.read_text(encoding="utf-8")
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    if isinstance(frontmatter, dict):
                        if "local_media_root" in frontmatter and frontmatter["local_media_root"]:
                            self.local_media_root = Path(frontmatter["local_media_root"])
                        if "weights" in frontmatter and isinstance(frontmatter["weights"], dict):
                            w = frontmatter["weights"]
                            self.weights = RelevanceWeights(
                                visual_similarity=float(w.get("visual_similarity", 0.30)),
                                script_relevance=float(w.get("script_relevance", 0.25)),
                                entity_match=float(w.get("entity_match", 0.15)),
                                temporal_relevance=float(w.get("temporal_relevance", 0.10)),
                                geographic_relevance=float(w.get("geographic_relevance", 0.10)),
                                source_quality=float(w.get("source_quality", 0.10)),
                            )
        except Exception:
            pass


config = Config()
config.load_from_settings()
