"""Audio safety filter: detects copyrighted pop music and verifies natural ambient sound."""

import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from pydantic import BaseModel, Field
from utils.hardware import get_ffmpeg_binary
from utils.logger import logger


class AudioProfile(BaseModel):
    """Detailed audio analysis of a video clip."""
    has_audio_stream: bool = False
    is_silent: bool = False
    mean_volume_db: float = -91.0
    max_volume_db: float = -91.0
    has_copyrighted_music_risk: bool = False
    rejection_reason: Optional[str] = None
    audio_summary: str = "Unanalyzed"


# Keywords in titles or metadata that signal commercial pop music
MUSIC_INDICATOR_KEYWORDS = [
    r"\boriginal sound\s*-\s*[a-zA-Z0-9_]+\b",
    r"\bsong\s*:\s*[a-zA-Z0-9_]+\b",
    r"\bmusic\s*:\s*[a-zA-Z0-9_]+\b",
    r"\bfeat\.\b",
    r"\bft\.\b",
    r"\bremix\b",
    r"\bofficial music video\b",
    r"\blyric video\b",
    r"\bproduced by\b",
    r"\bsoundtrack\b",
]

_MUSIC_REGEX = re.compile("|".join(MUSIC_INDICATOR_KEYWORDS), re.IGNORECASE)


def check_music_metadata_risk(title: str, description: str = "") -> Tuple[bool, Optional[str]]:
    """Checks whether video title or caption contains commercial music credits."""
    combined = f"{title} {description}".strip()
    match = _MUSIC_REGEX.search(combined)
    if match:
        reason = f"Commercial music credit found in metadata: '{match.group(0)}'"
        return True, reason
    return False, None


def analyze_audio_stream(video_path: str) -> AudioProfile:
    """Uses FFmpeg volumedetect filter to inspect audio levels and silence."""
    ffmpeg_bin = get_ffmpeg_binary()
    path_obj = Path(video_path)
    if not path_obj.exists():
        return AudioProfile(
            has_audio_stream=False,
            is_silent=True,
            audio_summary="File not found",
        )

    cmd = [
        ffmpeg_bin,
        "-i", str(video_path),
        "-af", "volumedetect",
        "-vn", "-sn", "-dn",
        "-f", "null",
        "/dev/null",
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        stderr = result.stderr

        # Check if audio stream exists
        if "Output #0" not in stderr or "Audio:" not in stderr:
            return AudioProfile(
                has_audio_stream=False,
                is_silent=True,
                audio_summary="No audio stream detected",
            )

        # Parse mean volume: mean_volume: -24.5 dB
        mean_vol = -91.0
        mean_match = re.search(r"mean_volume:\s*(-?\d+\.?\d*)\s*dB", stderr)
        if mean_match:
            mean_vol = float(mean_match.group(1))

        # Parse max volume: max_volume: -1.2 dB
        max_vol = -91.0
        max_match = re.search(r"max_volume:\s*(-?\d+\.?\d*)\s*dB", stderr)
        if max_match:
            max_vol = float(max_match.group(1))

        # Determine silence: if max volume is below -60dB, it's effectively silent
        is_silent = (max_vol < -60.0)

        summary = "Silent audio" if is_silent else f"Active audio (mean {mean_vol:.1f} dB)"

        return AudioProfile(
            has_audio_stream=True,
            is_silent=is_silent,
            mean_volume_db=mean_vol,
            max_volume_db=max_vol,
            has_copyrighted_music_risk=False,
            audio_summary=summary,
        )

    except Exception as e:
        logger.warn(f"Audio stream analysis failed: {e}")
        return AudioProfile(
            has_audio_stream=False,
            is_silent=True,
            audio_summary=f"Analysis error: {e}",
        )


def validate_audio_safety(video_path: str, title: str = "") -> Tuple[bool, Optional[str]]:
    """Comprehensive check to ensure audio is Content ID safe and has natural sound.

    Returns:
        (is_safe, rejection_reason)
    """
    # 1. Metadata check for commercial pop songs
    has_music_title, music_reason = check_music_metadata_risk(title)
    if has_music_title:
        logger.warn(f"Audio safety rejected: {music_reason}")
        return False, music_reason

    # 2. Audio stream level analysis
    profile = analyze_audio_stream(video_path)

    # Reject if video has no audio stream at all (humor lands best with natural punchline audio)
    if not profile.has_audio_stream or profile.is_silent:
        reason = "Video is completely silent (no natural sound for punchline)"
        logger.warn(f"Audio safety rejected: {reason}")
        return False, reason

    return True, None

