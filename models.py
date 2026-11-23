"""Pydantic data models for Daily Dose Studio."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class PlatformSource(str, Enum):
    """Source platform where the clip came from."""
    REDDIT = "reddit"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    MANUAL_UPLOAD = "manual_upload"


class NicheTopic(str, Enum):
    """Channel niche or style."""
    FUNNY_FAILS = "funny"
    ANIMALS = "animals"
    SATISFYING = "satisfying"
    GADGETS = "gadgets"
    CUSTOM = "custom"


class CandidateStatus(str, Enum):
    """Lifecycle status of a video candidate."""
    DISCOVERED = "discovered"
    DOWNLOADED = "downloaded"
    VERIFIED_CLEAN = "verified_clean"
    REJECTED = "rejected"


class ClipCandidate(BaseModel):
    """A raw video candidate discovered from the internet or uploaded."""
    id: str = Field(description="Unique clip identifier")
    title: str = Field(default="", description="Original video title or caption")
    source_url: str = Field(default="", description="URL of the original post")
    source_platform: PlatformSource = Field(default=PlatformSource.REDDIT)
    creator_handle: str = Field(default="Unknown", description="Original creator for attribution")
    video_path: Optional[str] = Field(default=None, description="Local path to downloaded video")
    duration_sec: float = Field(default=0.0, description="Video length in seconds")
    upvotes_or_likes: int = Field(default=0, description="Total likes or upvotes")
    viral_velocity: float = Field(default=0.0, description="Calculated speed of virality")
    status: CandidateStatus = Field(default=CandidateStatus.DISCOVERED)
    rejection_reason: Optional[str] = Field(default=None, description="Why clip was filtered out")


class ClipAnalysis(BaseModel):
    """AI vision understanding and comedic timing metadata."""
    summary: str = Field(default="", description="What happens in the video")
    is_engaging: bool = Field(default=True, description="Whether clip meets humor/quality bar")
    suggested_start_sec: float = Field(default=0.0, description="Optimal start time trimming dead air")
    suggested_end_sec: float = Field(default=0.0, description="Optimal end time after punchline")
    punchline_sec: float = Field(default=0.0, description="Exact timestamp of the funniest moment")
    has_commercial_watermark: bool = Field(default=False, description="Watermark check")
    has_copyrighted_music: bool = Field(default=False, description="Commercial pop music check")


class ClipScript(BaseModel):
    """Generated Daily Dose commentary and creator attribution."""
    clip_index: int = Field(default=1, description="Order in the compilation (1-15)")
    commentary: str = Field(default="", description="Deadpan context spoken by narrator")
    creator_credit: str = Field(default="", description="On-screen text e.g. Credit: @creator")
    voiceover_duration_sec: float = Field(default=0.0, description="Length of spoken voice track")


class ProcessedClip(BaseModel):
    """A fully prepared clip segment ready for final stitching."""
    candidate: ClipCandidate
    analysis: ClipAnalysis = Field(default_factory=ClipAnalysis)
    script: ClipScript = Field(default_factory=ClipScript)
    trimmed_video_path: Optional[str] = None
    voiceover_audio_path: Optional[str] = None
    subtitles_ass_path: Optional[str] = None


class JobStatus(str, Enum):
    """Overall status of a video creation job."""
    IDLE = "idle"
    SEARCHING = "searching"
    DOWNLOADING = "downloading"
    ANALYZING = "analyzing"
    VOICING = "voicing"
    EDITING = "editing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoJob(BaseModel):
    """Complete tracking for one video generation session."""
    job_id: str = Field(description="Unique job ID")
    mode: str = Field(default="magic_search", description="'magic_search' or 'manual_upload'")
    topic: NicheTopic = Field(default=NicheTopic.FUNNY_FAILS)
    custom_keyword: Optional[str] = None
    target_clip_count: int = Field(default=10, description="Number of clips: 5, 10, or 15")
    aspect_ratio: str = Field(default="16:9", description="'16:9' YouTube or '9:16' Shorts")
    status: JobStatus = Field(default=JobStatus.IDLE)
    progress_percent: int = Field(default=0, ge=0, le=100)
    status_message: str = Field(default="Ready")
    clips: List[ProcessedClip] = Field(default_factory=list)
    final_video_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

