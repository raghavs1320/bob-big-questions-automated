"""Test suite for Part 1: Core System Architecture & Models."""

import pytest
from pathlib import Path
from config import (
    BASE_DIR,
    STORAGE_DIR,
    DOWNLOADS_DIR,
    CACHE_DIR,
    TEMP_DIR,
    EXPORTS_DIR,
    settings,
)
from models import (
    ClipCandidate,
    ClipAnalysis,
    ClipScript,
    ProcessedClip,
    VideoJob,
    PlatformSource,
    NicheTopic,
    CandidateStatus,
    JobStatus,
)
from utils.logger import logger


def test_storage_directories_exist():
    """Verify that all required storage directories are created and writable."""
    directories = [STORAGE_DIR, DOWNLOADS_DIR, CACHE_DIR, TEMP_DIR, EXPORTS_DIR]
    for directory in directories:
        assert directory.exists(), f"Directory does not exist: {directory}"
        assert directory.is_dir(), f"Path is not a directory: {directory}"


def test_default_settings():
    """Verify default configuration settings."""
    assert settings.NARRATOR_VOICE == "en-US-ChristopherNeural"
    assert settings.INTRO_TEXT.startswith("Hello everyone")
    assert settings.OUTRO_TEXT.startswith("Thank you for watching")
    assert settings.PUNCHLINE_ZOOM_FACTOR == 1.15
    assert settings.AUDIO_DUCK_LEVEL == 0.15
    assert settings.DEFAULT_ASPECT_RATIO in ["16:9", "9:16"]


def test_models_instantiation():
    """Verify that Pydantic models validate and instantiate correctly."""
    # 1. Candidate
    candidate = ClipCandidate(
        id="clip_001",
        title="Cat slips on banana peel",
        source_url="https://reddit.com/r/unexpected/test",
        source_platform=PlatformSource.REDDIT,
        creator_handle="@funnycat",
        duration_sec=12.5,
        upvotes_or_likes=14500,
        viral_velocity=480.0,
        status=CandidateStatus.VERIFIED_CLEAN,
    )
    assert candidate.id == "clip_001"
    assert candidate.source_platform == PlatformSource.REDDIT

    # 2. Analysis
    analysis = ClipAnalysis(
        summary="A playful cat jumps for a toy but slips on kitchen tile",
        is_engaging=True,
        suggested_start_sec=2.0,
        suggested_end_sec=10.5,
        punchline_sec=6.2,
        has_commercial_watermark=False,
        has_copyrighted_music=False,
    )
    assert analysis.punchline_sec == 6.2
    assert not analysis.has_commercial_watermark

    # 3. Script
    script = ClipScript(
        clip_index=1,
        commentary="This cat thought he calculated the jump perfectly. Physics disagreed.",
        creator_credit="Credit: @funnycat",
        voiceover_duration_sec=4.2,
    )
    assert "Physics disagreed" in script.commentary

    # 4. Processed Clip
    processed = ProcessedClip(
        candidate=candidate,
        analysis=analysis,
        script=script,
    )
    assert processed.candidate.id == "clip_001"
    assert processed.script.creator_credit == "Credit: @funnycat"

    # 5. Video Job
    job = VideoJob(
        job_id="job_20261116_01",
        mode="magic_search",
        topic=NicheTopic.FUNNY_FAILS,
        target_clip_count=10,
        aspect_ratio="16:9",
        status=JobStatus.COMPLETED,
        progress_percent=100,
        status_message="Video ready!",
        clips=[processed],
    )
    assert job.target_clip_count == 10
    assert len(job.clips) == 1
    assert job.status == JobStatus.COMPLETED


def test_logger_output(capsys):
    """Verify logger output formatting."""
    logger.info("Test information message")
    logger.success("Test success message")
    captured = capsys.readouterr()
    assert "DailyDose" in captured.out
    assert "Test information message" in captured.out
    assert "Test success message" in captured.out

