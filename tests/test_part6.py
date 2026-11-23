"""Test suite for Part 6: Audio Safety & Commercial Music Filter."""

import subprocess
from pathlib import Path
import pytest
from config import TEMP_DIR
from shield.audio_check import (
    analyze_audio_stream,
    check_music_metadata_risk,
    validate_audio_safety,
)
from utils.hardware import generate_synthetic_test_clip, get_ffmpeg_binary


def test_music_metadata_keywords():
    """Verify commercial music title and hashtag detection."""
    # 1. Pop song credit
    is_music, reason = check_music_metadata_risk("Funny cat video (Song: Espresso by Sabrina Carpenter)")
    assert is_music is True
    assert "Song: Espresso" in reason

    # 2. Remix keyword
    is_music, reason = check_music_metadata_risk("Skater does backflip (Remix)")
    assert is_music is True
    assert "remix" in reason.lower()

    # 3. Clean title
    is_music, reason = check_music_metadata_risk("Dog jumps over sofa and misses")
    assert is_music is False
    assert reason is None


def test_analyze_audio_with_sound():
    """Verify audio analysis detects valid audible sound in video."""
    test_video = TEMP_DIR / "part6_sound_clip.mp4"
    if test_video.exists():
        test_video.unlink()

    # Generate test video with 440Hz sine wave tone
    generate_synthetic_test_clip(str(test_video), duration_sec=2.0)

    profile = analyze_audio_stream(str(test_video))
    assert profile.has_audio_stream is True
    assert profile.is_silent is False
    assert profile.max_volume_db > -40.0

    # Cleanup
    if test_video.exists():
        test_video.unlink()


def test_analyze_silent_video():
    """Verify audio analysis flags video without audio stream as silent."""
    test_silent_video = TEMP_DIR / "part6_silent_clip.mp4"
    if test_silent_video.exists():
        test_silent_video.unlink()

    ffmpeg_bin = get_ffmpeg_binary()
    # Generate video without any audio stream (-an)
    cmd = [
        ffmpeg_bin,
        "-y",
        "-f", "lavfi",
        "-i", "color=c=black:s=640x360:d=2:r=30",
        "-an",
        "-pix_fmt", "yuv420p",
        str(test_silent_video),
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    profile = analyze_audio_stream(str(test_silent_video))
    assert profile.has_audio_stream is False
    assert profile.is_silent is True

    # Validate audio safety rejects silent clip
    is_safe, reason = validate_audio_safety(str(test_silent_video), "Silent funny dog")
    assert is_safe is False
    assert "silent" in reason.lower()

    # Cleanup
    if test_silent_video.exists():
        test_silent_video.unlink()

