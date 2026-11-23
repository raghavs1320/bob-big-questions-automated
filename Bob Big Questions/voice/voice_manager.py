"""Unified voice manager for Daily Dose Studio."""

from typing import Optional
from config import TEMP_DIR
from voice.audio_processor import get_audio_duration
from voice.kokoro_engine import synthesize_kokoro_speech


def generate_voiceover_track(
    text: str,
    clip_id: str,
    voice_name: Optional[str] = None,
) -> str:
    """Generates a complete, normalized voiceover audio track for a clip.

    Returns:
        Absolute path to the rendered 48kHz audio track.
    """
    output_audio_path = str(TEMP_DIR / f"{clip_id}_voice.m4a")
    return synthesize_kokoro_speech(text, output_audio_path, voice=voice_name)

