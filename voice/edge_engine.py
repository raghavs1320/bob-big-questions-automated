"""High-Definition neural voice synthesis powered by Edge-TTS (100% Free & Unlimited)."""

import asyncio
from pathlib import Path
from typing import Optional
import edge_tts
from config import settings
from voice.audio_processor import normalize_voice_audio
from utils.logger import logger


async def _async_generate_speech(text: str, raw_output_path: str, voice: str) -> None:
    """Async voice generation using edge_tts Communicate."""
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(raw_output_path)


def synthesize_edge_speech(
    text: str,
    output_path: str,
    voice: Optional[str] = None,
) -> str:
    """Synthesizes high-definition narrator speech with natural deadpan cadence.

    Args:
        text: Script text to speak.
        output_path: Target path for the final normalized audio file.
        voice: Voice name (default: en-US-ChristopherNeural).

    Returns:
        Path to normalized, broadcast-ready 48kHz audio file.
    """
    selected_voice = voice or settings.NARRATOR_VOICE
    out_obj = Path(output_path)
    out_obj.parent.mkdir(parents=True, exist_ok=True)

    raw_temp_file = out_obj.parent / f"raw_{out_obj.stem}.mp3"

    logger.voice(f"Synthesizing voice: \"{text[:45]}...\" [{selected_voice}]")
    try:
        # Run async voice generation in event loop
        asyncio.run(_async_generate_speech(text, str(raw_temp_file), selected_voice))

        if raw_temp_file.exists() and raw_temp_file.stat().st_size > 1000:
            # Normalize audio to -16 LUFS broadcast standard
            final_audio = normalize_voice_audio(str(raw_temp_file), str(output_path))
            if raw_temp_file.exists():
                raw_temp_file.unlink()
            logger.success(f"Voice ready: '{Path(final_audio).name}'")
            return final_audio
        else:
            raise RuntimeError("Generated voice audio was empty or missing.")

    except Exception as e:
        logger.warn(f"Voice generation error: {e}")
        if raw_temp_file.exists():
            raw_temp_file.unlink()
        raise e

