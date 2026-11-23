"""Test suite for Part 9: Kokoro Neural Voice Studio."""

from pathlib import Path
import pytest
from config import TEMP_DIR
from utils.hardware import generate_synthetic_test_clip
from voice.audio_processor import get_audio_duration, normalize_voice_audio
from voice.edge_engine import synthesize_edge_speech
from voice.voice_manager import generate_voiceover_track


def test_get_audio_duration_on_synthetic_clip():
    """Verify audio duration measurement on a known 3-second clip."""
    test_clip = TEMP_DIR / "part9_dur_test.mp4"
    if test_clip.exists():
        test_clip.unlink()

    generate_synthetic_test_clip(str(test_clip), duration_sec=3.0)
    dur = get_audio_duration(str(test_clip))
    assert 2.8 <= dur <= 3.2

    if test_clip.exists():
        test_clip.unlink()


def test_normalize_voice_audio():
    """Verify loudness normalization output."""
    test_input = TEMP_DIR / "part9_norm_input.mp4"
    test_output = TEMP_DIR / "part9_norm_output.m4a"
    if test_input.exists():
        test_input.unlink()
    if test_output.exists():
        test_output.unlink()

    generate_synthetic_test_clip(str(test_input), duration_sec=2.0)
    normalized = normalize_voice_audio(str(test_input), str(test_output))
    assert Path(normalized).exists()
    assert Path(normalized).stat().st_size > 1000

    # Cleanup
    if test_input.exists():
        test_input.unlink()
    if test_output.exists():
        test_output.unlink()


def test_live_neural_voice_synthesis():
    """Verify live neural voice synthesis generates natural, audible speech."""
    test_audio = TEMP_DIR / "part9_live_voice.m4a"
    if test_audio.exists():
        test_audio.unlink()

    script_text = "Hello everyone, this is your daily dose of internet."
    rendered_path = synthesize_edge_speech(
        text=script_text,
        output_path=str(test_audio),
        voice="en-US-ChristopherNeural",
    )

    assert Path(rendered_path).exists()
    assert Path(rendered_path).stat().st_size > 3000

    # Spoken length should be between 2.0 and 4.5 seconds
    duration = get_audio_duration(rendered_path)
    assert 2.0 <= duration <= 4.5

    # Cleanup
    if test_audio.exists():
        test_audio.unlink()


def test_voice_manager_unified_generation():
    """Verify unified generate_voiceover_track entry point."""
    rendered_path = generate_voiceover_track(
        text="A family noticed something strange in their backyard.",
        clip_id="test_clip_voice",
    )
    assert Path(rendered_path).exists()
    assert Path(rendered_path).stat().st_size > 3000

    # Cleanup
    if Path(rendered_path).exists():
        Path(rendered_path).unlink()

