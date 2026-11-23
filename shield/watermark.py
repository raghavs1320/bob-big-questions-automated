"""Visual watermark, logo, and broadcast banner detection engine."""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from config import TEMP_DIR
from utils.hardware import get_ffmpeg_binary, get_video_info
from utils.logger import logger


def extract_sample_frames(
    video_path: str,
    num_samples: int = 3,
    output_dir: Path = TEMP_DIR,
) -> List[str]:
    """Extracts evenly spaced sample frames from a video file for visual inspection."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_binary()
    info = get_video_info(video_path)
    duration = info.get("duration", 0.0) or 0.0

    if duration <= 0.5:
        logger.warn(f"Cannot extract frames: video duration too short ({duration}s)")
        return []

    # Calculate sample timestamps (e.g. 20%, 50%, 80% into the video)
    sample_timestamps = [
        duration * (i + 1) / (num_samples + 1) for i in range(num_samples)
    ]

    base_name = Path(video_path).stem
    extracted_frames: List[str] = []

    for idx, ts in enumerate(sample_timestamps):
        frame_file = output_dir / f"{base_name}_sample_{idx}.jpg"
        cmd = [
            ffmpeg_bin,
            "-y",
            "-ss", f"{ts:.2f}",
            "-i", str(video_path),
            "-vframes", "1",
            "-q:v", "2",
            str(frame_file),
        ]
        try:
            subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=8,
                check=True,
            )
            if frame_file.exists() and frame_file.stat().st_size > 1000:
                extracted_frames.append(str(frame_file))
        except Exception as e:
            logger.warn(f"Failed to extract frame at {ts:.2f}s: {e}")

    return extracted_frames


def cleanup_sample_frames(frame_paths: List[str]) -> None:
    """Safely removes temporary sample frame files from disk."""
    for p in frame_paths:
        try:
            path_obj = Path(p)
            if path_obj.exists():
                path_obj.unlink()
        except Exception:
            pass


def inspect_clip_for_watermarks(video_path: str) -> Tuple[bool, Optional[str]]:
    """Inspects a video clip for commercial watermarks or logos.

    Returns:
        (has_watermark, label_or_reason)
    """
    frames = extract_sample_frames(video_path, num_samples=3)
    if not frames:
        return False, None

    try:
        # In Part 5, we verify frames can be extracted cleanly and are non-empty.
        # When Gemini API is attached in Part 7, it performs visual OCR over these frames.
        for frame_path in frames:
            if not os.path.exists(frame_path) or os.path.getsize(frame_path) < 1000:
                return False, None

        return False, None
    finally:
        cleanup_sample_frames(frames)

