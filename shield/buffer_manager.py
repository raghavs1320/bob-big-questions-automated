"""Candidate Buffer & Auto-Replacement Engine."""

from typing import List, Tuple
from models import CandidateStatus, ClipCandidate
from shield.blacklist import validate_candidate_metadata
from shield.watermark import inspect_clip_for_watermarks
from utils.logger import logger


class CandidateBufferManager:
    """Filters a candidate pool and auto-replaces rejected clips until the target count is satisfied."""

    def __init__(self, target_count: int = 10):
        self.target_count = target_count

    def process_candidate_pool(
        self,
        candidate_pool: List[ClipCandidate],
    ) -> Tuple[List[ClipCandidate], List[ClipCandidate]]:
        """Evaluates candidates in order, rejecting unsafe/blacklisted ones and pulling replacements.

        Returns:
            (approved_clean_clips, rejected_clips)
        """
        approved_clips: List[ClipCandidate] = []
        rejected_clips: List[ClipCandidate] = []

        logger.info(
            f"Processing candidate pool ({len(candidate_pool)} clips) to secure {self.target_count} clean clips..."
        )

        for candidate in candidate_pool:
            # If we already have enough approved clips, we can stop
            if len(approved_clips) >= self.target_count:
                break

            # 1. Metadata & Agency Blacklist Check
            is_safe, reason = validate_candidate_metadata(candidate)
            if not is_safe:
                candidate.status = CandidateStatus.REJECTED
                candidate.rejection_reason = reason
                rejected_clips.append(candidate)
                logger.warn(f"Discarded {candidate.id} -> Fetching replacement from buffer")
                continue

            # 2. Visual Watermark Check (if video is already downloaded locally)
            if candidate.video_path:
                has_watermark, wm_reason = inspect_clip_for_watermarks(candidate.video_path)
                if has_watermark:
                    candidate.status = CandidateStatus.REJECTED
                    candidate.rejection_reason = wm_reason or "Commercial watermark detected"
                    rejected_clips.append(candidate)
                    logger.warn(f"Discarded {candidate.id} (Watermark) -> Fetching replacement")
                    continue

            # Passed all checks!
            candidate.status = CandidateStatus.VERIFIED_CLEAN
            approved_clips.append(candidate)
            logger.success(f"Verified Clean [{len(approved_clips)}/{self.target_count}]: {candidate.id}")

        logger.info(
            f"Buffer result: {len(approved_clips)} clean approved, {len(rejected_clips)} discarded/replaced"
        )
        return approved_clips, rejected_clips

