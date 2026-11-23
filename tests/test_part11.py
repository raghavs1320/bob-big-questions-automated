"""Test suite for Part 11: Hardware Video Compositor & Stitcher."""

from pathlib import Path
import pytest
from captions.ass_generator import generate_ass_subtitles
from captions.timing import extract_word_timing
from config import EXPORTS_DIR, TEMP_DIR
from editor.audio_ducking import build_audio_ducking_filter
from editor.compositor import concatenate_segments, render_clip_segment
from editor.effects import build_aspect_ratio_filter
from models import (
    CandidateStatus,
    ClipAnalysis,
    ClipCandidate,
    ClipScript,
    PlatformSource,
    ProcessedClip,
)
from utils.hardware import generate_synthetic_test_clip, get_video_info
from voice.voice_manager import generate_voiceover_track


def test_aspect_ratio_filter_builder():
    """Verify aspect ratio filter returns correct dimensions."""
    w, h, fg = build_aspect_ratio_filter("16:9")
    assert (w, h) == (1920, 1080)
    assert "scale" in fg

    w, h, fg = build_aspect_ratio_filter("9:16")
    assert (w, h) == (1080, 1920)


def test_audio_ducking_filter_builder():
    """Verify ducking filter includes volume ducking and amix."""
    fg = build_audio_ducking_filter(voice_duration_sec=3.2)
    assert "volume=0.15" in fg
    assert "amix" in fg


def test_render_clip_segment_and_concatenation():
    """End-to-end integration test: renders 2 clips with ducking, subtitles, and stitches them."""
    test_raw_1 = TEMP_DIR / "part11_raw1.mp4"
    test_raw_2 = TEMP_DIR / "part11_raw2.mp4"
    seg_1 = TEMP_DIR / "part11_seg1.mp4"
    seg_2 = TEMP_DIR / "part11_seg2.mp4"
    final_output = EXPORTS_DIR / "part11_test_compilation.mp4"

    for f in [test_raw_1, test_raw_2, seg_1, seg_2, final_output]:
        if f.exists():
            f.unlink()

    # Generate 2 synthetic raw clips (each 3 seconds)
    generate_synthetic_test_clip(str(test_raw_1), duration_sec=3.0, color="navy")
    generate_synthetic_test_clip(str(test_raw_2), duration_sec=3.0, color="darkgreen")

    # Clip 1 Setup
    c1 = ClipCandidate(
        id="test_clip_1",
        title="Cat tries impossible jump",
        creator_handle="@catguy",
        video_path=str(test_raw_1),
        status=CandidateStatus.DOWNLOADED,
    )
    a1 = ClipAnalysis(summary="Cat slips", punchline_sec=2.0, suggested_start_sec=0.0, suggested_end_sec=3.0)
    s1 = ClipScript(clip_index=1, commentary="To start off, this cat miscalculated.", creator_credit="Credit: @catguy")
    processed_1 = ProcessedClip(candidate=c1, analysis=a1, script=s1)

    # Clip 2 Setup
    c2 = ClipCandidate(
        id="test_clip_2",
        title="Skater does amazing flip",
        creator_handle="@skatepro",
        video_path=str(test_raw_2),
        status=CandidateStatus.DOWNLOADED,
    )
    a2 = ClipAnalysis(summary="Skater lands trick", punchline_sec=1.8, suggested_start_sec=0.0, suggested_end_sec=3.0)
    s2 = ClipScript(clip_index=2, commentary="And finally, this skater landed it cleanly.", creator_credit="Credit: @skatepro")
    processed_2 = ProcessedClip(candidate=c2, analysis=a2, script=s2)

    # 1. Render Segment 1
    out_seg_1 = render_clip_segment(processed_1, str(seg_1), aspect_ratio="16:9")
    assert Path(out_seg_1).exists()
    assert Path(out_seg_1).stat().st_size > 10000

    # 2. Render Segment 2
    out_seg_2 = render_clip_segment(processed_2, str(seg_2), aspect_ratio="16:9")
    assert Path(out_seg_2).exists()
    assert Path(out_seg_2).stat().st_size > 10000

    # 3. Concatenate both into final compilation video
    compilation_path = concatenate_segments([out_seg_1, out_seg_2], str(final_output))
    assert Path(compilation_path).exists()
    assert Path(compilation_path).stat().st_size > 30000

    # 4. Verify Final Video Properties
    final_info = get_video_info(compilation_path)
    assert final_info["width"] == 1920
    assert final_info["height"] == 1080
    assert final_info["has_audio"] is True
    # Combined duration should be ~5 to 6 seconds
    assert 4.5 <= final_info["duration"] <= 7.0

    # Cleanup test files
    for f in [test_raw_1, test_raw_2, seg_1, seg_2, final_output]:
        if f.exists():
            f.unlink()

