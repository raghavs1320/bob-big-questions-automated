"""Test suite for Part 2: Hardware Acceleration & Local Media Runtime."""

import os
from pathlib import Path
import pytest
from config import TEMP_DIR
from utils.hardware import (
    get_ffmpeg_binary,
    detect_hardware,
    get_video_info,
    generate_synthetic_test_clip,
    HardwareReport,
)


def test_ffmpeg_binary_exists():
    """Verify that FFmpeg binary is located and executable."""
    bin_path = get_ffmpeg_binary()
    assert bin_path is not None
    assert os.path.isfile(bin_path)
    assert os.access(bin_path, os.X_OK)


def test_hardware_detection_apple_silicon():
    """Verify that hardware acceleration correctly detects Apple Silicon and VideoToolbox."""
    report = detect_hardware()
    assert isinstance(report, HardwareReport)
    assert report.is_apple_silicon is True
    assert report.is_hardware_accelerated is True
    assert report.video_encoder == "h264_videotoolbox"
    assert report.audio_encoder == "aac"
    assert report.ffmpeg_version != "Unknown"


def test_synthetic_video_rendering_and_inspection():
    """Verify that VideoToolbox hardware encoder produces a valid, playable MP4 file."""
    test_output = TEMP_DIR / "part2_test_clip.mp4"
    if test_output.exists():
        test_output.unlink()

    # 1. Generate test video with VideoToolbox hardware encoder
    rendered_path = generate_synthetic_test_clip(
        output_path=str(test_output),
        duration_sec=3.0,
        width=1280,
        height=720,
        color="royalblue",
    )
    assert Path(rendered_path).exists()
    assert Path(rendered_path).stat().st_size > 5000  # Non-empty video file

    # 2. Inspect video metadata with get_video_info
    info = get_video_info(rendered_path)
    assert 2.8 <= info["duration"] <= 3.2
    assert info["width"] == 1280
    assert info["height"] == 720
    assert info["has_audio"] is True

    # Cleanup test artifact
    if test_output.exists():
        test_output.unlink()

