"""Persistent deduplication engine to ensure clips are never reused across videos."""

import json
from pathlib import Path
from typing import List, Set
from config import CACHE_DIR
from models import ClipCandidate
from utils.logger import logger

SEEN_CLIPS_FILE = CACHE_DIR / "seen_clips.json"


class DeduplicationRegistry:
    """Tracks all previously used clips to prevent duplicate content across channels."""

    def __init__(self, registry_file: Path = SEEN_CLIPS_FILE):
        self.registry_file = registry_file
        self.seen_ids: Set[str] = set()
        self.seen_urls: Set[str] = set()
        self._load()

    def _load(self) -> None:
        """Loads seen clip IDs and URLs from disk."""
        if not self.registry_file.exists():
            self._save()
            return

        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.seen_ids = set(data.get("seen_ids", []))
                self.seen_urls = set(data.get("seen_urls", []))
        except Exception as e:
            logger.warn(f"Could not load deduplication registry: {e}")
            self.seen_ids = set()
            self.seen_urls = set()

    def _save(self) -> None:
        """Saves current seen registry to disk."""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "seen_ids": sorted(list(self.seen_ids)),
                        "seen_urls": sorted(list(self.seen_urls)),
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            logger.warn(f"Could not save deduplication registry: {e}")

    def is_duplicate(self, candidate: ClipCandidate) -> bool:
        """Checks if a candidate clip has already been used in an earlier video."""
        if candidate.id in self.seen_ids:
            return True
        if candidate.source_url and candidate.source_url in self.seen_urls:
            return True
        return False

    def mark_used(self, candidate: ClipCandidate) -> None:
        """Marks a clip as used so it will never be chosen again."""
        self.seen_ids.add(candidate.id)
        if candidate.source_url:
            self.seen_urls.add(candidate.source_url)
        self._save()

    def filter_candidates(self, candidates: List[ClipCandidate]) -> List[ClipCandidate]:
        """Removes all previously used clips from a list of candidate clips."""
        clean_candidates = []
        for c in candidates:
            if not self.is_duplicate(c):
                clean_candidates.append(c)
            else:
                logger.info(f"Skipping duplicate clip previously used: {c.id}")
        return clean_candidates

    def clear(self) -> None:
        """Resets the deduplication registry (mainly for testing)."""
        self.seen_ids.clear()
        self.seen_urls.clear()
        self._save()


# Default global registry
dedup_registry = DeduplicationRegistry()

