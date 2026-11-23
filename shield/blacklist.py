"""Blacklist filter for commercial licensing agencies, news syndicators, and media rights holders."""

import re
from typing import List, Optional, Tuple
from models import ClipCandidate
from utils.logger import logger

# Known commercial licensing agencies that buy viral clips and claim copyright
COMMERCIAL_AGENCIES: List[str] = [
    "viralhog",
    "jukin",
    "jukinmedia",
    "collabdrm",
    "collab drm",
    "storyful",
    "newsflare",
    "caters",
    "catersnews",
    "caters clips",
    "ladbible",
    "unilad",
    "dailymail",
    "daily mail",
    "barstool",
    "barstoolsports",
    "failarmy",
    "worldstar",
    "worldstarhiphop",
    "thesun",
    "tmz",
    "ridiculousness",
    "afv",
    "americasfunniest",
]

# Robust pattern matching: catches agencies separated by spaces, underscores, dots, hyphens, or slashes
_AGENCY_PATTERN = "|".join(re.escape(agency) for agency in COMMERCIAL_AGENCIES)
_BLACKLIST_REGEX = re.compile(
    rf"(?:^|[^a-zA-Z0-9])({_AGENCY_PATTERN})(?:[^a-zA-Z0-9]|$)",
    re.IGNORECASE,
)


def check_agency_blacklist(text: str) -> Tuple[bool, Optional[str]]:
    """Checks whether a given text string contains a blacklisted commercial agency name.

    Returns:
        (is_blacklisted, matched_agency_name)
    """
    if not text:
        return False, None

    match = _BLACKLIST_REGEX.search(text)
    if match:
        agency = match.group(1).lower()
        return True, agency

    return False, None


def validate_candidate_metadata(candidate: ClipCandidate) -> Tuple[bool, Optional[str]]:
    """Inspects candidate title, author handle, and source URL against commercial blacklists.

    Returns:
        (is_safe, rejection_reason_if_unsafe)
    """
    # 1. Check title
    is_blocked, agency = check_agency_blacklist(candidate.title)
    if is_blocked:
        reason = f"Commercial licensing agency in title: '{agency}'"
        logger.warn(f"Shield BLOCKED {candidate.id}: {reason}")
        return False, reason

    # 2. Check author / creator handle
    is_blocked, agency = check_agency_blacklist(candidate.creator_handle)
    if is_blocked:
        reason = f"Commercial licensing agency in creator handle: '{agency}'"
        logger.warn(f"Shield BLOCKED {candidate.id}: {reason}")
        return False, reason

    # 3. Check source URL
    is_blocked, agency = check_agency_blacklist(candidate.source_url)
    if is_blocked:
        reason = f"Commercial licensing agency in URL: '{agency}'"
        logger.warn(f"Shield BLOCKED {candidate.id}: {reason}")
        return False, reason

    return True, None
