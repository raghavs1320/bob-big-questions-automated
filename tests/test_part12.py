"""Test suite for Part 12: Autonomous Scheduler & Mobile Notification Bot."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from config import EXPORTS_DIR, TEMP_DIR
from daemon.macos_notify import send_macos_notification
from daemon.scheduler import run_full_pipeline
from daemon.telegram_bot import get_pending_approvals, record_pending_approval
from models import (
    CandidateStatus,
    ClipCandidate,
    JobStatus,
    NicheTopic,
    PlatformSource,
    ProcessedClip,
    VideoJob,
)
from utils.hardware import generate_synthetic_test_clip, get_video_info


def test_macos_notification_call():
    """Verify macOS desktop notification executes without error."""
    success = send_macos_notification("Daily Dose Test", "Test notification body")
    assert isinstance(success, bool)


def test_pending_approvals_queue():
    """Verify local pending approval queue records and reads items."""
    import uuid
    unique_job_id = f"job_test_{uuid.uuid4().hex[:8]}"
    test_video_path = str(TEMP_DIR / "dummy_preview.mp4")
    record_pending_approval(unique_job_id, test_video_path, "Test approval caption")

    items = get_pending_approvals()
    assert len(items) >= 1
    matched = [i for i in items if i.get("job_id") == unique_job_id]
    assert len(matched) == 1
    assert matched[0]["status"] == "pending"


def test_end_to_end_autonomous_pipeline_execution():
    """Executes the full automated pipeline with 2 clips and verifies end-to-end completion."""
    clip1_path = TEMP_DIR / "part12_clip1.mp4"
    clip2_path = TEMP_DIR / "part12_clip2.mp4"

    generate_synthetic_test_clip(str(clip1_path), duration_sec=2.5, color="purple")
    generate_synthetic_test_clip(str(clip2_path), duration_sec=2.5, color="maroon")

    c1 = ClipCandidate(
        id="autojob_clip_1",
        title="Cat slips while running",
        creator_handle="@speedycat",
        video_path=str(clip1_path),
        status=CandidateStatus.DOWNLOADED,
    )
    c2 = ClipCandidate(
        id="autojob_clip_2",
        title="Skater pulls off stunt",
        creator_handle="@skateboy",
        video_path=str(clip2_path),
        status=CandidateStatus.DOWNLOADED,
    )

    job = VideoJob(
        job_id="test_autojob_001",
        mode="manual_upload",
        topic=NicheTopic.FUNNY_FAILS,
        target_clip_count=2,
        clips=[
            ProcessedClip(candidate=c1),
            ProcessedClip(candidate=c2),
        ],
    )

    progress_records = []
    def on_progress(pct: int, msg: str):
        progress_records.append((pct, msg))

    completed_job = run_full_pipeline(job, progress_callback=on_progress)

    assert completed_job.status == JobStatus.COMPLETED
    assert completed_job.progress_percent == 100
    assert completed_job.final_video_path is not None
    assert Path(completed_job.final_video_path).exists()
    assert Path(completed_job.final_video_path).stat().st_size > 30000

    # Verify final video properties
    info = get_video_info(completed_job.final_video_path)
    assert info["width"] == 1920
    assert info["height"] == 1080
    assert info["has_audio"] is True
    assert 4.0 <= info["duration"] <= 6.5

    # Verify progress callbacks were tracked
    assert len(progress_records) >= 5
    assert progress_records[-1][0] == 100

    # Cleanup
    for f in [clip1_path, clip2_path, Path(completed_job.final_video_path)]:
        if f.exists():
            f.unlink()
