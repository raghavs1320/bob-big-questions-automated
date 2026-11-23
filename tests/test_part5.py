"""Test suite for Part 5: Autonomous Copyright, Agency & Watermark Shield."""

from pathlib import Path
import pytest
from config import TEMP_DIR
from models import CandidateStatus, ClipCandidate, PlatformSource
from shield.blacklist import check_agency_blacklist, validate_candidate_metadata
from shield.buffer_manager import CandidateBufferManager
from shield.watermark import cleanup_sample_frames, extract_sample_frames
from utils.hardware import generate_synthetic_test_clip


def test_agency_blacklist_pattern_matching():
    """Verify that known licensing syndicators are caught by the blacklist filter."""
    blocked, agency = check_agency_blacklist("Dog slips on kitchen rug (Courtesy of ViralHog)")
    assert blocked is True
    assert agency == "viralhog"

    blocked, agency = check_agency_blacklist("Licensed to Jukin Media for broadcast")
    assert blocked is True
    assert agency == "jukin"

    blocked, agency = check_agency_blacklist("CollabDRM Protected Clip")
    assert blocked is True
    assert agency == "collabdrm"

    # Clean text should pass
    clean, agency = check_agency_blacklist("My cat tried to catch a laser pointer")
    assert clean is False
    assert agency is None


def test_candidate_metadata_validation():
    """Verify metadata validation catches agency names in author handles and URLs."""
    # 1. Unsafe author
    unsafe_author_clip = ClipCandidate(
        id="clip_bad_author",
        title="Funny dog fail",
        creator_handle="u/ViralHog_Official",
        status=CandidateStatus.DISCOVERED,
    )
    is_safe, reason = validate_candidate_metadata(unsafe_author_clip)
    assert is_safe is False
    assert "viralhog" in reason.lower()

    # 2. Clean clip
    clean_clip = ClipCandidate(
        id="clip_clean",
        title="Skater jumps over stairs cleanly",
        creator_handle="u/skater_kid",
        source_url="https://reddit.com/r/unexpected/clean",
        status=CandidateStatus.DISCOVERED,
    )
    is_safe, reason = validate_candidate_metadata(clean_clip)
    assert is_safe is True
    assert reason is None


def test_sample_frame_extraction_and_cleanup():
    """Verify frame extraction from a test video and safe cleanup."""
    test_video = TEMP_DIR / "part5_frame_test.mp4"
    if test_video.exists():
        test_video.unlink()

    # Generate small 3-second test clip
    generate_synthetic_test_clip(str(test_video), duration_sec=3.0)

    frames = extract_sample_frames(str(test_video), num_samples=3)
    assert len(frames) == 3
    for f in frames:
        assert Path(f).exists()
        assert Path(f).stat().st_size > 1000

    # Test cleanup
    cleanup_sample_frames(frames)
    for f in frames:
        assert not Path(f).exists()

    # Cleanup video
    if test_video.exists():
        test_video.unlink()


def test_buffer_manager_replacement_loop():
    """Verify that buffer manager automatically discards risky clips and secures replacements."""
    pool = [
        ClipCandidate(
            id="candidate_1_bad",
            title="Dog jumps into pool (ViralHog)",
            creator_handle="u/someone",
        ),
        ClipCandidate(
            id="candidate_2_clean",
            title="Cat stares at cucumber",
            creator_handle="u/cat_lover",
        ),
        ClipCandidate(
            id="candidate_3_bad",
            title="Crazy stunt fail",
            creator_handle="u/JukinMedia",
        ),
        ClipCandidate(
            id="candidate_4_clean",
            title="Robot slips on banana peel",
            creator_handle="u/tech_fan",
        ),
        ClipCandidate(
            id="candidate_5_clean",
            title="Parrot sings opera song",
            creator_handle="u/bird_guy",
        ),
    ]

    # Target: 2 clean clips
    manager = CandidateBufferManager(target_count=2)
    approved, rejected = manager.process_candidate_pool(pool)

    # Should have rejected candidates 1 and 3, and approved clean candidates 2 and 4
    assert len(approved) == 2
    assert approved[0].id == "candidate_2_clean"
    assert approved[1].id == "candidate_4_clean"
    assert len(rejected) == 2
    assert rejected[0].id == "candidate_1_bad"
    assert rejected[1].id == "candidate_3_bad"

