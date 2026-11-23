"""Test suite for Part 4: TikTok, Shorts & Deduplication Engine."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from config import TEMP_DIR
from models import CandidateStatus, ClipCandidate, PlatformSource
from scraper.dedup import DeduplicationRegistry
from scraper.ytdlp_engine import clean_id, detect_platform, extract_clip_metadata, search_trending_shorts


def test_detect_platform():
    """Verify platform detection from various URLs."""
    assert detect_platform("https://www.tiktok.com/@user/video/1234567") == PlatformSource.TIKTOK
    assert detect_platform("https://www.youtube.com/shorts/abc123xyz") == PlatformSource.YOUTUBE
    assert detect_platform("https://youtu.be/shortId123") == PlatformSource.YOUTUBE
    assert detect_platform("https://www.reddit.com/r/unexpected/comments/123") == PlatformSource.REDDIT
    assert detect_platform("https://mywebsite.com/video.mp4") == PlatformSource.MANUAL_UPLOAD


def test_clean_id():
    """Verify ID sanitization for filesystem safety."""
    assert clean_id("abc/123:xyz?foo=bar") == "abc_123_xyz_foo_bar"
    assert clean_id("valid_id-123") == "valid_id-123"


def test_deduplication_registry():
    """Verify that clips are never repeated across videos."""
    test_registry_file = TEMP_DIR / "test_seen_clips.json"
    if test_registry_file.exists():
        test_registry_file.unlink()

    registry = DeduplicationRegistry(registry_file=test_registry_file)

    c1 = ClipCandidate(
        id="clip_001",
        title="Cat fail",
        source_url="https://youtube.com/shorts/111",
        status=CandidateStatus.DISCOVERED,
    )
    c2 = ClipCandidate(
        id="clip_002",
        title="Dog park stunt",
        source_url="https://youtube.com/shorts/222",
        status=CandidateStatus.DISCOVERED,
    )

    # Initially neither is duplicate
    assert not registry.is_duplicate(c1)
    assert not registry.is_duplicate(c2)

    # Mark c1 as used
    registry.mark_used(c1)
    assert registry.is_duplicate(c1)
    assert not registry.is_duplicate(c2)

    # Test filtering
    filtered = registry.filter_candidates([c1, c2])
    assert len(filtered) == 1
    assert filtered[0].id == "clip_002"

    # Test persistence (reload new instance from disk)
    reloaded_registry = DeduplicationRegistry(registry_file=test_registry_file)
    assert reloaded_registry.is_duplicate(c1)
    assert not reloaded_registry.is_duplicate(c2)

    # Cleanup
    if test_registry_file.exists():
        test_registry_file.unlink()


def test_search_trending_shorts_mock():
    """Verify search_trending_shorts parses flat results correctly."""
    mock_results = {
        "entries": [
            {
                "id": "vid1",
                "title": "Funny Dog Reaction",
                "url": "https://www.youtube.com/watch?v=vid1",
                "duration": 15.0,
                "view_count": 500000,
                "uploader": "DogChannel",
            },
            {
                "id": "vid2_toolong",
                "title": "Long 2 minute video",
                "url": "https://www.youtube.com/watch?v=vid2",
                "duration": 120.0,  # Too long, should be skipped
                "view_count": 10000,
                "uploader": "LongChannel",
            },
        ]
    }

    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = mock_results

        candidates = search_trending_shorts("funny animals", limit=5)
        assert len(candidates) == 1
        assert candidates[0].id == "youtube_vid1"
        assert candidates[0].creator_handle == "@DogChannel"
        assert candidates[0].duration_sec == 15.0

