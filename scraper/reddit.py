"""Reddit viral video scraper and candidate extractor."""

import time
from pathlib import Path
from typing import Dict, List, Optional
import requests
import yt_dlp
from config import DOWNLOADS_DIR
from models import CandidateStatus, ClipCandidate, NicheTopic, PlatformSource
from utils.hardware import get_ffmpeg_binary, get_video_info
from utils.logger import logger

# Recommended subreddits grouped by niche topic
NICHE_SUBREDDITS: Dict[NicheTopic, List[str]] = {
    NicheTopic.FUNNY_FAILS: [
        "unexpected",
        "holdmybeer",
        "instant_regret",
        "Whatcouldgowrong",
        "maybemaybemaybe",
    ],
    NicheTopic.ANIMALS: [
        "AnimalsBeingDerps",
        "aww",
        "AnimalsBeingGeniuses",
    ],
    NicheTopic.SATISFYING: [
        "oddlysatisfying",
        "mildlyinteresting",
        "Damnthatsinteresting",
    ],
    NicheTopic.GADGETS: [
        "specializedtools",
        "gadgets",
    ],
}

# Browser User-Agent to ensure reliable access to Reddit's public API
REDDIT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 DailyDoseStudio/1.0"


def calculate_viral_velocity(score: int, num_comments: int, created_utc: float) -> float:
    """Calculates how fast a clip is gaining traction in the last 24 hours."""
    now_ts = time.time()
    hours_old = max(0.5, (now_ts - created_utc) / 3600.0)
    # Velocity = Upvotes per hour * engagement multiplier (comments/upvotes)
    engagement_factor = 1.0 + (num_comments / max(1.0, score))
    velocity = (score / hours_old) * engagement_factor
    return round(velocity, 2)


def parse_reddit_post(post_data: dict) -> Optional[ClipCandidate]:
    """Parses a Reddit post JSON dict into a ClipCandidate if it contains a valid video."""
    data = post_data.get("data", {})

    # Check for crossposts
    if "crosspost_parent_list" in data and len(data["crosspost_parent_list"]) > 0:
        data = data["crosspost_parent_list"][0]

    # Verify if the post is a video
    is_video = data.get("is_video", False)
    media = data.get("media") or {}
    reddit_video = media.get("reddit_video") or {}

    if not is_video and not reddit_video:
        # Check if URL ends with .mp4 or is a known video domain
        url = data.get("url", "")
        if not (url.endswith(".mp4") or "v.redd.it" in url):
            return None

    post_id = data.get("id", "")
    if not post_id:
        return None

    title = data.get("title", "")
    author = data.get("author", "Unknown")
    permalink = data.get("permalink", "")
    full_url = f"https://www.reddit.com{permalink}" if permalink else data.get("url", "")
    score = data.get("score", 0)
    num_comments = data.get("num_comments", 0)
    created_utc = data.get("created_utc", time.time())
    duration = float(reddit_video.get("duration", 0.0))

    # Reject very long videos (over 60 seconds) or very short (<3s)
    if duration > 65.0 or (duration > 0 and duration < 3.0):
        return None

    velocity = calculate_viral_velocity(score, num_comments, created_utc)

    return ClipCandidate(
        id=f"reddit_{post_id}",
        title=title,
        source_url=full_url,
        source_platform=PlatformSource.REDDIT,
        creator_handle=f"u/{author}",
        duration_sec=duration,
        upvotes_or_likes=score,
        viral_velocity=velocity,
        status=CandidateStatus.DISCOVERED,
    )


def fetch_reddit_candidates(
    subreddits: List[str],
    time_filter: str = "day",
    limit_per_sub: int = 15,
) -> List[ClipCandidate]:
    """Scrapes top viral video candidates across given subreddits for the specified timeframe."""
    candidates: List[ClipCandidate] = []
    seen_ids = set()

    headers = {"User-Agent": REDDIT_USER_AGENT}

    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/top.json?t={time_filter}&limit={limit_per_sub}"
        logger.search(f"Scanning r/{sub} (Top 24h)...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.warn(f"r/{sub} returned HTTP {response.status_code}")
                continue

            payload = response.json()
            children = payload.get("data", {}).get("children", [])

            for child in children:
                candidate = parse_reddit_post(child)
                if candidate and candidate.id not in seen_ids:
                    seen_ids.add(candidate.id)
                    candidates.append(candidate)

        except Exception as e:
            logger.warn(f"Failed to fetch r/{sub}: {e}")

    # Sort all candidates by viral velocity (highest virality first)
    candidates.sort(key=lambda c: c.viral_velocity, reverse=True)
    logger.success(f"Discovered {len(candidates)} viral candidates from Reddit")
    return candidates


def download_candidate(
    candidate: ClipCandidate,
    output_dir: Path = DOWNLOADS_DIR,
) -> Optional[str]:
    """Downloads a video candidate using yt-dlp into local storage."""
    output_dir.mkdir(parents=True, exist_ok=True)
    target_filepath = output_dir / f"{candidate.id}.mp4"

    # If already downloaded, return existing path
    if target_filepath.exists() and target_filepath.stat().st_size > 10000:
        candidate.video_path = str(target_filepath)
        candidate.status = CandidateStatus.DOWNLOADED
        return str(target_filepath)

    ffmpeg_bin = get_ffmpeg_binary()

    ydl_opts = {
        "outtmpl": str(output_dir / f"{candidate.id}.%(ext)s"),
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "ffmpeg_location": ffmpeg_bin,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": 15,
    }

    logger.search(f"Downloading: '{candidate.title[:45]}...'")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([candidate.source_url])

        if target_filepath.exists():
            # Update candidate metadata with actual video specs
            info = get_video_info(str(target_filepath))
            candidate.video_path = str(target_filepath)
            candidate.duration_sec = info.get("duration", candidate.duration_sec)
            candidate.status = CandidateStatus.DOWNLOADED
            logger.success(f"Downloaded: {candidate.id} ({candidate.duration_sec:.1f}s)")
            return str(target_filepath)
        else:
            logger.warn(f"File did not exist after download: {target_filepath}")
            candidate.status = CandidateStatus.REJECTED
            candidate.rejection_reason = "Download file missing"
            return None

    except Exception as e:
        logger.warn(f"Failed to download {candidate.id}: {e}")
        candidate.status = CandidateStatus.REJECTED
        candidate.rejection_reason = f"Download failed: {e}"
        return None

