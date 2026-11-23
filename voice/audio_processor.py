"""Audio post-processing and loudness normalization for voiceover tracks."""

import re
import subprocess
from pathlib import Path
from utils.hardware import get_ffmpeg_binary
from utils.logger import logger


def get_audio_duration(audio_path: str) -> float:
    """Returns the exact duration of an audio file in seconds."""
    ffmpeg_bin = get_ffmpeg_binary()
    cmd = [ffmpeg_bin, "-i", str(audio_path)]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    # Search for Duration: 00:00:04.25
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", result.stderr)
    if match:
        h = float(match.group(1))
        m = float(match.group(2))
        s = float(match.group(3))
        return round(h * 3600 + m * 60 + s, 3)
    return 0.0


def normalize_voice_audio(input_path: str, output_path: str) -> str:
    """Normalizes voiceover track to -16 LUFS broadcast standard and resamples to 48kHz."""
    ffmpeg_bin = get_ffmpeg_binary()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # -af "loudnorm=I=-16:LRA=11:TP=-1.5" -ar 48000
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", str(input_path),
        "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
        "-ar", "48000",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path),
    ]

    try:
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=15,
        )
        return str(output_path)
    except Exception as e:
        logger.warn(f"Audio normalization failed: {e}. Using original audio file.")
        return str(input_path)

