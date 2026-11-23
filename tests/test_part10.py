"""Test suite for Part 10: Kinetic Captions & Word Timing Engine."""

import subprocess
from pathlib import Path
import pytest
from captions.ass_generator import format_ass_time, generate_ass_subtitles
from captions.timing import WordTimestamp, extract_word_timing
from config import TEMP_DIR
from utils.hardware import generate_synthetic_test_clip, get_ffmpeg_binary


def test_format_ass_time():
    """Verify ASS timecode formatting."""
    assert format_ass_time(0.0) == "0:00:00.00"
    assert format_ass_time(1.25) == "0:00:01.25"
    assert format_ass_time(65.5) == "0:01:05.50"
    assert format_ass_time(3661.12) == "1:01:01.12"


def test_extract_word_timing_continuity():
    """Verify extracted word timestamps are sequential, continuous, and non-overlapping."""
    text = "This dog thought he calculated the jump perfectly."
    total_duration = 3.2
    words = extract_word_timing(text, total_duration_sec=total_duration)

    assert len(words) == 8
    assert words[0].word == "This"
    assert words[0].start_sec == 0.0

    # Verify sequential monotonicity
    for i in range(len(words) - 1):
        assert words[i].start_sec < words[i].end_sec
        assert abs(words[i].end_sec - words[i + 1].start_sec) < 0.001

    assert abs(words[-1].end_sec - total_duration) < 0.05


def test_generate_ass_subtitles_file():
    """Verify ASS subtitle file generation with karaoke tags."""
    test_ass = TEMP_DIR / "part10_test.ass"
    if test_ass.exists():
        test_ass.unlink()

    words = [
        WordTimestamp(word="Physics", start_sec=0.0, end_sec=0.8),
        WordTimestamp(word="completely", start_sec=0.8, end_sec=1.5),
        WordTimestamp(word="disagreed.", start_sec=1.5, end_sec=2.4),
    ]

    ass_path = generate_ass_subtitles(words, str(test_ass), aspect_ratio="16:9")
    assert Path(ass_path).exists()

    content = Path(ass_path).read_text(encoding="utf-8")
    assert "[Script Info]" in content
    assert "[V4+ Styles]" in content
    assert "[Events]" in content
    assert r"{\c&H0000FFFF&}" in content  # Yellow highlight tag
    assert "Physics" in content

    # Cleanup
    if test_ass.exists():
        test_ass.unlink()


def test_ffmpeg_burn_subtitles_onto_video():
    """Verify that FFmpeg can burn the generated .ass subtitles into an MP4 video."""
    test_video = TEMP_DIR / "part10_sub_source.mp4"
    test_ass = TEMP_DIR / "part10_sub.ass"
    test_output = TEMP_DIR / "part10_subbed_output.mp4"

    for f in [test_video, test_ass, test_output]:
        if f.exists():
            f.unlink()

    # Generate source video (2.5 seconds)
    generate_synthetic_test_clip(str(test_video), duration_sec=2.5)

    # Generate .ass subtitles
    words = extract_word_timing("Daily dose test caption.", total_duration_sec=2.5)
    generate_ass_subtitles(words, str(test_ass))

    ffmpeg_bin = get_ffmpeg_binary()
    # Burn subtitles using -vf "subtitles=..."
    # Escape path for FFmpeg filter graph
    escaped_ass = str(test_ass).replace(":", "\\:").replace("'", "\\'")
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", str(test_video),
        "-vf", f"subtitles='{escaped_ass}'",
        "-c:a", "copy",
        str(test_output),
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert result.returncode == 0
    assert test_output.exists()
    assert test_output.stat().st_size > 5000

    # Cleanup
    for f in [test_video, test_ass, test_output]:
        if f.exists():
            f.unlink()

