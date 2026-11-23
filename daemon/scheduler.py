"""Autonomous background pipeline orchestrator and scheduler."""

import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional
from brain.analyzer import analyze_clip_vision
from brain.scriptwriter import generate_clip_script
from config import EXPORTS_DIR, TEMP_DIR
from daemon.macos_notify import send_macos_notification
from daemon.telegram_bot import send_telegram_preview
from editor.compositor import concatenate_segments, render_clip_segment
from models import (
    CandidateStatus,
    ClipAnalysis,
    ClipCandidate,
    ClipScript,
    JobStatus,
    NicheTopic,
    ProcessedClip,
    VideoJob,
)
from scraper.dedup import dedup_registry
from scraper.reddit import NICHE_SUBREDDITS, download_candidate, fetch_reddit_candidates
from shield.buffer_manager import CandidateBufferManager
from utils.logger import logger


def run_full_pipeline(
    job: VideoJob,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> VideoJob:
    """Executes the entire end-to-end video creation pipeline autonomously.

    Workflow:
    1. Viral Search & Deduplication
    2. Copyright & Agency Shield
    3. Download Clean Clips
    4. AI Multimodal Vision Analysis
    5. Daily Dose Comedic Scriptwriting
    6. Neural Voiceover & Karaoke Captions
    7. Hardware Video Compositing & Stitching
    8. Desktop & Phone Approval Notification
    """
    def update_progress(pct: int, msg: str):
        job.progress_percent = pct
        job.status_message = msg
        logger.info(f"[{pct}%] {msg}")
        if progress_callback:
            progress_callback(pct, msg)

    try:
        update_progress(5, f"Starting video creation for niche: {job.topic.value}")

        # Step 1: Ingestion (if magic search mode)
        clean_candidates: List[ClipCandidate] = []
        if job.mode == "magic_search":
            update_progress(10, "Searching internet feeds for top viral clips from today...")
            subreddits = NICHE_SUBREDDITS.get(job.topic, NICHE_SUBREDDITS[NicheTopic.FUNNY_FAILS])
            raw_pool = fetch_reddit_candidates(subreddits, limit_per_sub=12)

            # Deduplication
            fresh_pool = dedup_registry.filter_candidates(raw_pool)

            # Copyright & Agency Shield with Buffer Auto-Replacement
            update_progress(20, "Inspecting clips for copyright agencies & watermarks...")
            buffer_manager = CandidateBufferManager(target_count=job.target_clip_count)
            clean_candidates, _ = buffer_manager.process_candidate_pool(fresh_pool)

            if not clean_candidates:
                raise RuntimeError("No clean viral candidates found passing all safety checks.")

            # Download certified clean candidates
            update_progress(35, f"Downloading {len(clean_candidates)} clean clips...")
            for idx, candidate in enumerate(clean_candidates):
                download_candidate(candidate)
        else:
            # Manual upload mode
            clean_candidates = [clip.candidate for clip in job.clips]

        # Step 2: AI Analysis & Scriptwriting
        processed_clips: List[ProcessedClip] = []
        total_clips = len(clean_candidates)

        for idx, candidate in enumerate(clean_candidates):
            step_pct = 40 + int(30 * (idx / max(1, total_clips)))
            update_progress(step_pct, f"AI watching clip [{idx+1}/{total_clips}]: '{candidate.title[:30]}...'")

            if candidate.video_path and Path(candidate.video_path).exists():
                analysis = analyze_clip_vision(candidate.video_path, candidate.title)
            else:
                analysis = ClipAnalysis(summary=candidate.title, punchline_sec=3.0)

            script = generate_clip_script(
                candidate=candidate,
                analysis=analysis,
                clip_index=idx + 1,
                total_clips=total_clips,
                topic=job.topic,
            )

            p_clip = ProcessedClip(candidate=candidate, analysis=analysis, script=script)
            processed_clips.append(p_clip)

        job.clips = processed_clips

        # Step 3: Hardware Video Compositing
        rendered_segments: List[str] = []
        for idx, p_clip in enumerate(job.clips):
            step_pct = 70 + int(20 * (idx / max(1, total_clips)))
            update_progress(step_pct, f"Editing clip [{idx+1}/{total_clips}] with zooms and captions...")
            seg_output = str(TEMP_DIR / f"{job.job_id}_seg_{idx+1}.mp4")
            out_path = render_clip_segment(p_clip, seg_output, aspect_ratio=job.aspect_ratio)
            rendered_segments.append(out_path)

        # Step 4: Final Stitching
        update_progress(92, "Stitching all clips into final compilation video...")
        final_video_name = f"DailyDose_{job.topic.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        final_video_path = str(EXPORTS_DIR / final_video_name)

        concatenate_segments(rendered_segments, final_video_path)
        job.final_video_path = final_video_path
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now()

        # Step 5: Mark used in deduplication registry
        for p_clip in job.clips:
            dedup_registry.mark_used(p_clip.candidate)

        # Step 6: Dispatch Notifications
        update_progress(100, "Compilation video complete and ready!")
        send_macos_notification(
            title="Daily Dose Studio",
            message=f"Your {job.topic.value} compilation is ready! ({total_clips} clips)",
            subtitle="Click to preview",
        )
        send_telegram_preview(
            video_path=final_video_path,
            caption=f"🎬 Daily Dose Video Ready!\nNiche: {job.topic.value}\nClips: {total_clips}",
            job_id=job.job_id,
        )

        return job

    except Exception as e:
        logger.error(f"Pipeline error for job {job.job_id}: {e}")
        job.status = JobStatus.FAILED
        job.status_message = f"Error: {e}"
        raise e

