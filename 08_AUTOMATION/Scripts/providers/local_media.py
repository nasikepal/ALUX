"""
Local Media Library Indexer and Search Provider.
Prioritizes in-house b-roll, sfx, and assets before web lookups.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import os
import re
from core.config import config
from core.logger import logger


class LocalMediaProvider:
    # Files below this size are placeholders or broken copies, not usable media.
    MIN_MEDIA_BYTES = 1024

    @classmethod
    def is_usable_file(cls, path_str: Optional[str]) -> bool:
        if not path_str:
            return False
        try:
            p = Path(path_str)
            return p.is_file() and p.stat().st_size >= cls.MIN_MEDIA_BYTES
        except OSError:
            return False

    def __init__(self):
        self.index_path = config.local_media_index_path
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_data: List[Dict[str, Any]] = []
        self.load_index()

    def load_index(self):
        if self.index_path.exists():
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    self.index_data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load local media index: {e}")
                self.index_data = []

    def save_index(self):
        try:
            with open(self.index_path, "w", encoding="utf-8") as f:
                json.dump(self.index_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved local media index with {len(self.index_data)} assets.")
        except Exception as e:
            logger.error(f"Failed to save local media index: {e}")

    def build_index(self, scan_paths: Optional[List[Path]] = None) -> int:
        """
        Recursively scans directories and builds searchable asset records.
        """
        if not scan_paths:
            scan_paths = [
                config.local_media_root,
                config.media_dir,
            ]

        valid_exts = {
            ".mp4", ".mov", ".mkv", ".webm", ".avi",  # Video
            ".wav", ".mp3", ".flac", ".aac", ".ogg",  # Audio / SFX
            ".png", ".jpg", ".jpeg", ".webp", ".exr",  # Images
            ".blend", ".fbx", ".obj"                  # 3D
        }

        indexed = []
        for base in scan_paths:
            if not base.exists():
                continue
            logger.info(f"Scanning local media path: {base}")
            for root, _, files in os.walk(base):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in valid_exts:
                        full_path = Path(root) / file
                        if not self.is_usable_file(str(full_path)):
                            logger.warning(f"Skipping placeholder/empty media file: {full_path}")
                            continue
                        rel_parts = full_path.relative_to(base).parts
                        
                        # Infer asset type
                        asset_type = "footage"
                        if ext in {".wav", ".mp3", ".flac", ".aac", ".ogg"}:
                            asset_type = "sfx" if "sfx" in [p.lower() for p in rel_parts] or "sound" in [p.lower() for p in rel_parts] else "music"
                        elif ext in {".png", ".jpg", ".jpeg", ".webp"}:
                            asset_type = "image"
                        elif ext in {".blend", ".fbx", ".obj"}:
                            asset_type = "graphic"

                        # Extract tags from folder path and filename
                        clean_name = re.sub(r"[^\w\s-]", " ", full_path.stem)
                        tags = [t.lower() for t in clean_name.split() if len(t) > 2]
                        tags.extend([p.lower() for p in rel_parts[:-1]])

                        indexed.append({
                            "title": full_path.stem.replace("_", " ").replace("-", " ").title(),
                            "asset_type": asset_type,
                            "source": "local",
                            "url": f"file:///{full_path.as_posix()}",
                            "local_path": str(full_path),
                            "duration": "unknown",
                            "resolution": "unknown",
                            "license": "Internal Studio Ownership",
                            "tags": list(set(tags)),
                            "description": f"Internal asset from {full_path.parent.name}"
                        })

        self.index_data = indexed
        self.save_index()
        return len(indexed)

    def search(self, query: str, asset_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches indexed local assets by keyword matching against title and tags."""
        if not self.index_data:
            return []

        tokens = set(re.findall(r"\w+", query.lower()))
        matches = []
        for item in self.index_data:
            if asset_type and item["asset_type"] != asset_type:
                continue
            # The index can be stale (built on another machine, files moved or emptied) — only offer files that exist here.
            if not self.is_usable_file(item.get("local_path")):
                continue

            item_tokens = set(item.get("tags", []))
            item_tokens.update(re.findall(r"\w+", item.get("title", "").lower()))

            overlap = len(tokens.intersection(item_tokens))
            if overlap > 0:
                score = overlap / max(1, len(tokens))
                item_copy = dict(item)
                item_copy["internal_match_score"] = score
                matches.append(item_copy)

        matches.sort(key=lambda x: x.get("internal_match_score", 0), reverse=True)
        return matches[:limit]


local_media_provider = LocalMediaProvider()
