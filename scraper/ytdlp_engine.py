"""Universal media downloader for YouTube Shorts, TikTok, Instagram Reels, and direct video links."""

import re
from pathlib import Path
from typing import List, Optional
import yt_dlp
from config import DOWNLOADS_DIR
from models import CandidateStatus, ClipCandidate, PlatformSource
from utils.hardware import get_ffmpeg_binary, get_video_info
from utils.logger import logger


def detect_platform(url: str) -> PlatformSource:
    """Identifies the platform source from a video URL."""
    url_lower = url.lower()
    if "tiktok.com" in url_lower:
        return PlatformSource.TIKTOK
    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
        return PlatformSource.YOUTUBE
    elif "reddit.com" in url_lower or "v.redd.it" in url_lower:
        return PlatformSource.REDDIT
    return PlatformSource.MANUAL_UPLOAD


def clean_id(raw_id: str) -> str:
    """Sanitizes raw video IDs for safe filesystem paths."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", raw_id)


def extract_clip_metadata(url: str) -> Optional[ClipCandidate]:
    """Inspects a video URL using yt-dlp to extract metadata without downloading."""
    ffmpeg_bin = get_ffmpeg_binary()
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "ffmpeg_location": ffmpeg_bin,
        "socket_timeout": 10,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None

            raw_id = info.get("id", "clip")
            platform = detect_platform(url)
            platform_prefix = platform.value
            clip_id = f"{platform_prefix}_{clean_id(raw_id)}"

            title = info.get("title", "")
            uploader = info.get("uploader") or info.get("channel") or "Creator"
            creator_handle = f"@{uploader.lstrip('@')}"
            duration = float(info.get("duration", 0.0) or 0.0)
            likes = int(info.get("like_count", 0) or info.get("view_count", 0) or 0)

            # Filter out videos longer than 65s
            if duration > 65.0:
                logger.info(f"Video {url} exceeds 65s duration ({duration:.1f}s), skipping.")
                return None

            return ClipCandidate(
                id=clip_id,
                title=title,
                source_url=url,
                source_platform=platform,
                creator_handle=creator_handle,
                duration_sec=duration,
                upvotes_or_likes=likes,
                viral_velocity=float(likes),
                status=CandidateStatus.DISCOVERED,
            )
    except Exception as e:
        logger.warn(f"Could not extract metadata for {url}: {e}")
        return None


def search_trending_shorts(query: str, limit: int = 10) -> List[ClipCandidate]:
    """Searches for trending short-form viral videos on YouTube Shorts."""
    ffmpeg_bin = get_ffmpeg_binary()
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "ffmpeg_location": ffmpeg_bin,
        "socket_timeout": 10,
    }

    candidates: List[ClipCandidate] = []
    search_query = f"ytsearch{limit * 2}:{query} shorts"
    logger.search(f"Searching trending Shorts for '{query}'...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(search_query, download=False)
            entries = results.get("entries", []) if results else []

            for entry in entries:
                if not entry:
                    continue

                duration = float(entry.get("duration", 0.0) or 0.0)
                # Keep only short clips (<60s)
                if duration > 60.0 or (duration > 0 and duration < 3.0):
                    continue

                video_id = entry.get("id", "")
                url = entry.get("url") or f"https://www.youtube.com/watch?v={video_id}"
                title = entry.get("title", "")
                uploader = entry.get("uploader") or entry.get("channel") or "Creator"

                candidate = ClipCandidate(
                    id=f"youtube_{clean_id(video_id)}",
                    title=title,
                    source_url=url,
                    source_platform=PlatformSource.YOUTUBE,
                    creator_handle=f"@{uploader.lstrip('@')}",
                    duration_sec=duration,
                    upvotes_or_likes=int(entry.get("view_count", 0) or 0),
                    viral_velocity=float(entry.get("view_count", 0) or 0),
                    status=CandidateStatus.DISCOVERED,
                )
                candidates.append(candidate)
                if len(candidates) >= limit:
                    break

        logger.success(f"Found {len(candidates)} candidate Shorts for '{query}'")
        return candidates

    except Exception as e:
        logger.warn(f"Shorts search failed: {e}")
        return []


def download_media_clip(
    candidate: ClipCandidate,
    output_dir: Path = DOWNLOADS_DIR,
) -> Optional[str]:
    """Downloads any video candidate into local MP4 storage using yt-dlp."""
    output_dir.mkdir(parents=True, exist_ok=True)
    target_path = output_dir / f"{candidate.id}.mp4"

    if target_path.exists() and target_path.stat().st_size > 10000:
        candidate.video_path = str(target_path)
        candidate.status = CandidateStatus.DOWNLOADED
        return str(target_path)

    ffmpeg_bin = get_ffmpeg_binary()
    ydl_opts = {
        "outtmpl": str(output_dir / f"{candidate.id}.%(ext)s"),
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "ffmpeg_location": ffmpeg_bin,
        "extractor_args": {"youtube": {"player_client": ["android", "ios", "web"]}},
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 15,
    }

    logger.search(f"Downloading clip: {candidate.id}...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([candidate.source_url])

        if target_path.exists():
            info = get_video_info(str(target_path))
            candidate.video_path = str(target_path)
            candidate.duration_sec = info.get("duration", candidate.duration_sec)
            candidate.status = CandidateStatus.DOWNLOADED
            logger.success(f"Downloaded: {candidate.id} ({candidate.duration_sec:.1f}s)")
            return str(target_path)
        return None

    except Exception as e:
        logger.warn(f"Failed to download {candidate.id}: {e}")
        candidate.status = CandidateStatus.REJECTED
        candidate.rejection_reason = str(e)
        return None

