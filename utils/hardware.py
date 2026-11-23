"""Hardware acceleration and local media runtime detector."""

import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from pydantic import BaseModel
from utils.logger import logger


class HardwareReport(BaseModel):
    """System hardware acceleration report."""
    os_name: str
    architecture: str
    is_apple_silicon: bool
    ffmpeg_path: str
    ffmpeg_version: str
    video_encoder: str
    audio_encoder: str
    is_hardware_accelerated: bool


def get_ffmpeg_binary() -> str:
    """Finds the best available FFmpeg binary (System or imageio-ffmpeg bundled)."""
    # 1. Check system path
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    # 2. Check Homebrew default paths
    for brew_path in ["/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
        if os.path.isfile(brew_path) and os.access(brew_path, os.X_OK):
            return brew_path

    # 3. Fallback to imageio-ffmpeg official static binary
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.isfile(exe) and os.access(exe, os.X_OK):
            return exe
    except Exception as e:
        logger.warn(f"imageio_ffmpeg check failed: {e}")

    raise RuntimeError(
        "FFmpeg binary not found. Please install imageio-ffmpeg or ffmpeg."
    )


def get_supported_encoders(ffmpeg_bin: str) -> str:
    """Runs ffmpeg -encoders to find available codecs."""
    try:
        result = subprocess.run(
            [ffmpeg_bin, "-encoders"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        return result.stdout
    except Exception as e:
        logger.warn(f"Could not query ffmpeg encoders: {e}")
        return ""


def detect_hardware() -> HardwareReport:
    """Detects system hardware, Apple Silicon acceleration, and best video encoder."""
    os_name = platform.system()
    machine = platform.machine().lower()
    is_apple_silicon = (os_name == "Darwin" and ("arm" in machine or "aarch" in machine))

    ffmpeg_bin = get_ffmpeg_binary()

    # Get FFmpeg version
    ffmpeg_version = "Unknown"
    try:
        ver_res = subprocess.run(
            [ffmpeg_bin, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        first_line = ver_res.stdout.splitlines()[0] if ver_res.stdout else ""
        match = re.search(r"ffmpeg version (\S+)", first_line)
        if match:
            ffmpeg_version = match.group(1)
    except Exception:
        pass

    encoders_output = get_supported_encoders(ffmpeg_bin)

    # Determine best video encoder
    is_hardware_accel = False
    if is_apple_silicon and "h264_videotoolbox" in encoders_output:
        video_encoder = "h264_videotoolbox"
        is_hardware_accel = True
    elif "h264_nvenc" in encoders_output:
        video_encoder = "h264_nvenc"
        is_hardware_accel = True
    elif "h264_qsv" in encoders_output:
        video_encoder = "h264_qsv"
        is_hardware_accel = True
    else:
        video_encoder = "libx264"

    audio_encoder = "aac"

    report = HardwareReport(
        os_name=os_name,
        architecture=machine,
        is_apple_silicon=is_apple_silicon,
        ffmpeg_path=ffmpeg_bin,
        ffmpeg_version=ffmpeg_version,
        video_encoder=video_encoder,
        audio_encoder=audio_encoder,
        is_hardware_accelerated=is_hardware_accel,
    )

    if report.is_hardware_accelerated:
        logger.success(
            f"Hardware acceleration ACTIVE: using '{video_encoder}' on Apple Silicon"
        )
    else:
        logger.info(f"Using CPU video encoder '{video_encoder}'")

    return report


def get_video_info(file_path: str) -> Dict[str, Optional[float]]:
    """Extracts duration, width, height, and audio presence using FFmpeg."""
    ffmpeg_bin = get_ffmpeg_binary()
    path_obj = Path(file_path)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Run ffmpeg -i and parse stderr (FFmpeg prints file info to stderr)
    cmd = [ffmpeg_bin, "-i", str(file_path)]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stderr = result.stderr

    duration: float = 0.0
    width: int = 0
    height: int = 0
    has_audio: bool = "Audio:" in stderr

    # Extract Duration: 00:00:10.50
    dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", stderr)
    if dur_match:
        hours = float(dur_match.group(1))
        minutes = float(dur_match.group(2))
        seconds = float(dur_match.group(3))
        duration = hours * 3600 + minutes * 60 + seconds

    # Extract Video dimensions: 1920x1080
    dim_match = re.search(r"Video:.*?,.*?(\d{2,5})x(\d{2,5})", stderr)
    if dim_match:
        width = int(dim_match.group(1))
        height = int(dim_match.group(2))

    return {
        "duration": duration,
        "width": width,
        "height": height,
        "has_audio": has_audio,
    }


def generate_synthetic_test_clip(
    output_path: str,
    duration_sec: float = 3.0,
    width: int = 1280,
    height: int = 720,
    color: str = "blue",
) -> str:
    """Generates a clean synthetic MP4 video with a test audio tone for testing."""
    ffmpeg_bin = get_ffmpeg_binary()
    hw = detect_hardware()

    # Generate synthetic video with audio beep
    # -f lavfi -i color=c=blue:s=1280x720:d=3 -f lavfi -i sine=frequency=440:duration=3
    cmd = [
        ffmpeg_bin,
        "-y",
        "-f", "lavfi",
        "-i", f"color=c={color}:s={width}x{height}:d={duration_sec}:r=30",
        "-f", "lavfi",
        "-i", f"sine=frequency=440:duration={duration_sec}",
        "-c:v", hw.video_encoder,
        "-c:a", hw.audio_encoder,
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        timeout=15,
    )
    return str(output_path)

