"""Test suite for Part 3: Reddit Viral Scraper Engine."""

import time
import pytest
from unittest.mock import patch, MagicMock
from models import CandidateStatus, ClipCandidate, NicheTopic, PlatformSource
from scraper.reddit import (
    NICHE_SUBREDDITS,
    calculate_viral_velocity,
    parse_reddit_post,
    fetch_reddit_candidates,
)


def test_niche_subreddits_mapping():
    """Verify that all major video niches have configured subreddits."""
    assert NicheTopic.FUNNY_FAILS in NICHE_SUBREDDITS
    assert NicheTopic.ANIMALS in NICHE_SUBREDDITS
    assert NicheTopic.SATISFYING in NICHE_SUBREDDITS
    assert "unexpected" in NICHE_SUBREDDITS[NicheTopic.FUNNY_FAILS]
    assert "AnimalsBeingDerps" in NICHE_SUBREDDITS[NicheTopic.ANIMALS]


def test_viral_velocity_math():
    """Verify that newer, high-engagement clips have higher viral velocity."""
    now = time.time()
    # 1. Very viral recent post (2 hours old, 5000 score, 200 comments)
    fast_velocity = calculate_viral_velocity(
        score=5000, num_comments=200, created_utc=now - 7200
    )
    # 2. Slower, older post (20 hours old, 500 score, 10 comments)
    slow_velocity = calculate_viral_velocity(
        score=500, num_comments=10, created_utc=now - 72000
    )
    assert fast_velocity > slow_velocity
    assert fast_velocity > 2000.0


def test_parse_reddit_video_post():
    """Verify parsing a valid Reddit video post."""
    mock_post = {
        "data": {
            "id": "abc123z",
            "title": "Dog accidentally kicks ball into goal",
            "author": "viral_puppy",
            "permalink": "/r/unexpected/comments/abc123z/dog_accidentally/",
            "score": 8420,
            "num_comments": 150,
            "created_utc": time.time() - 3600,
            "is_video": True,
            "media": {
                "reddit_video": {
                    "duration": 14.5,
                    "fallback_url": "https://v.redd.it/dummy/DASH_720.mp4",
                }
            },
        }
    }

    candidate = parse_reddit_post(mock_post)
    assert candidate is not None
    assert candidate.id == "reddit_abc123z"
    assert candidate.title == "Dog accidentally kicks ball into goal"
    assert candidate.creator_handle == "u/viral_puppy"
    assert candidate.duration_sec == 14.5
    assert candidate.upvotes_or_likes == 8420
    assert candidate.viral_velocity > 0
    assert candidate.status == CandidateStatus.DISCOVERED


def test_parse_reddit_non_video_post():
    """Verify that text/image posts are skipped."""
    mock_text_post = {
        "data": {
            "id": "text999",
            "title": "A funny text joke",
            "is_video": False,
            "media": None,
            "url": "https://www.reddit.com/r/funny/comments/text999/",
        }
    }
    candidate = parse_reddit_post(mock_text_post)
    assert candidate is None


def test_parse_reddit_too_long_video():
    """Verify that excessively long videos (>65s) are filtered out."""
    mock_long_video = {
        "data": {
            "id": "long123",
            "title": "Full 10 minute podcast",
            "is_video": True,
            "media": {
                "reddit_video": {
                    "duration": 180.0,
                }
            },
        }
    }
    candidate = parse_reddit_post(mock_long_video)
    assert candidate is None


def test_fetch_reddit_candidates_with_mock():
    """Verify fetch_reddit_candidates correctly aggregates and sorts by viral velocity."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "children": [
                {
                    "data": {
                        "id": "clip_slow",
                        "title": "Slow clip",
                        "author": "user1",
                        "permalink": "/r/test/1",
                        "score": 100,
                        "num_comments": 5,
                        "created_utc": time.time() - 36000,
                        "is_video": True,
                        "media": {"reddit_video": {"duration": 10.0}},
                    }
                },
                {
                    "data": {
                        "id": "clip_fast",
                        "title": "Viral hit clip",
                        "author": "user2",
                        "permalink": "/r/test/2",
                        "score": 12000,
                        "num_comments": 400,
                        "created_utc": time.time() - 1800,
                        "is_video": True,
                        "media": {"reddit_video": {"duration": 12.0}},
                    }
                },
            ]
        }
    }

    with patch("requests.get", return_value=mock_response):
        candidates = fetch_reddit_candidates(["unexpected"], limit_per_sub=5)
        assert len(candidates) == 2
        # Most viral should be first
        assert candidates[0].id == "reddit_clip_fast"
        assert candidates[1].id == "reddit_clip_slow"
        assert candidates[0].viral_velocity > candidates[1].viral_velocity

