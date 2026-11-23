"""Hardware-accelerated video compositor and multi-clip timeline stitcher."""

import os
import subprocess
from pathlib import Path
from typing import List, Optional
from captions.ass_generator import generate_ass_subtitles
from captions.timing import extract_word_timing
from config import EXPORTS_DIR, TEMP_DIR
from editor.audio_ducking import build_audio_ducking_filter
from editor.effects import build_aspect_ratio_filter
from models import ProcessedClip, VideoJob
from utils.hardware import detect_hardware, get_ffmpeg_binary, get_video_info
from utils.logger import logger
from voice.audio_processor import get_audio_duration
from voice.voice_manager import generate_voiceover_track


def render_clip_segment(
    clip: ProcessedClip,
    output_path: str,
    aspect_ratio: str = "16:9",
) -> str:
    """Renders a single video clip segment with trimming, audio ducking, and kinetic subtitles."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_binary()
    hw = detect_hardware()

    raw_video = clip.trimmed_video_path or clip.candidate.video_path
    if not raw_video or not Path(raw_video).exists():
        raise FileNotFoundError(f"Source video not found for {clip.candidate.id}")

    # Determine trim window
    start_sec = max(0.0, clip.analysis.suggested_start_sec)
    end_sec = clip.analysis.suggested_end_sec
    info = get_video_info(raw_video)
    video_dur = info.get("duration", 0.0) or 5.0
    if end_sec <= start_sec or end_sec > video_dur:
        end_sec = video_dur
    trimmed_duration = end_sec - start_sec

    # 1. Voiceover track preparation
    voice_track = clip.voiceover_audio_path
    if not voice_track or not Path(voice_track).exists():
        voice_track = generate_voiceover_track(clip.script.commentary, clip.candidate.id)
        clip.voiceover_audio_path = voice_track

    voice_dur = get_audio_duration(voice_track)

    # 2. Subtitles preparation
    sub_path = clip.subtitles_ass_path
    if not sub_path or not Path(sub_path).exists():
        sub_file = TEMP_DIR / f"{clip.candidate.id}_sub.ass"
        words = extract_word_timing(clip.script.commentary, total_duration_sec=voice_dur)
        generate_ass_subtitles(words, str(sub_file), aspect_ratio=aspect_ratio)
        clip.subtitles_ass_path = str(sub_file)
        sub_path = str(sub_file)

    escaped_sub = str(sub_path).replace(":", "\\:").replace("'", "\\'")

    # 3. Video Filters: Aspect Ratio normalization + Subtitles burn
    tw, th, _ = build_aspect_ratio_filter(aspect_ratio)

    # Video filter chain: scale and pad to target resolution, then burn subtitles
    video_filter = (
        f"scale={tw}:{th}:force_original_aspect_ratio=decrease,"
        f"pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"subtitles='{escaped_sub}'"
    )

    # 4. Audio Filter: Audio Ducking
    audio_duck_graph = build_audio_ducking_filter(voice_dur)

    # Assemble FFmpeg Command
    cmd = [
        ffmpeg_bin,
        "-y",
        "-ss", f"{start_sec:.2f}",
        "-to", f"{end_sec:.2f}",
        "-i", str(raw_video),
        "-i", str(voice_track),
        "-filter_complex", f"[0:v]{video_filter}[vout];{audio_duck_graph}",
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", hw.video_encoder,
        "-c:a", hw.audio_encoder,
        "-b:a", "192k",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    logger.edit(f"Rendering segment: {clip.candidate.id} ({trimmed_duration:.1f}s)...")
    try:
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=60,
        )
        if Path(output_path).exists() and Path(output_path).stat().st_size > 10000:
            logger.success(f"Segment rendered: {clip.candidate.id}")
            return str(output_path)
        raise RuntimeError("Segment render produced empty file.")

    except subprocess.CalledProcessError as e:
        logger.warn(f"Hardware render failed, falling back to CPU encoder: {e.stderr.decode('utf-8', errors='ignore')[-300:]}")
        # CPU Fallback
        cmd[cmd.index("-c:v") + 1] = "libx264"
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=60)
        return str(output_path)


def concatenate_segments(
    segment_paths: List[str],
    final_output_path: str,
) -> str:
    """Losslessly concatenates processed clip segments into the final compilation video."""
    ffmpeg_bin = get_ffmpeg_binary()
    Path(final_output_path).parent.mkdir(parents=True, exist_ok=True)

    concat_txt_path = TEMP_DIR / "concat_segments.txt"
    lines = [f"file '{Path(p).resolve()}'" for p in segment_paths]
    with open(concat_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    cmd = [
        ffmpeg_bin,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_txt_path),
        "-c", "copy",
        str(final_output_path),
    ]

    logger.edit(f"Stitching {len(segment_paths)} segments into final compilation...")
    try:
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=120,
        )
        if Path(final_output_path).exists() and Path(final_output_path).stat().st_size > 50000:
            logger.success(f"Final compilation ready: '{Path(final_output_path).name}'")
            return str(final_output_path)
        raise RuntimeError("Final stitched video was empty.")

    except Exception as e:
        logger.error(f"Concatenation error: {e}")
        raise e

