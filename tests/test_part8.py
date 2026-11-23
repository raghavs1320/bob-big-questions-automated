"""Test suite for Part 8: Comedic Scriptwriting Engine."""

from unittest.mock import MagicMock, patch
import pytest
from brain.prompts import DDOI_INTRO, DDOI_OUTRO
from brain.scriptwriter import generate_clip_script
from models import ClipAnalysis, ClipCandidate, NicheTopic


def test_first_clip_intro_greeting():
    """Verify the first clip in the compilation includes the signature DDoI intro."""
    candidate = ClipCandidate(
        id="c1",
        title="Cat slips on banana",
        creator_handle="@funnycats",
    )
    analysis = ClipAnalysis(
        summary="A cat attempts to jump and slips",
        punchline_sec=4.0,
    )

    script = generate_clip_script(
        candidate=candidate,
        analysis=analysis,
        clip_index=1,
        total_clips=10,
        topic=NicheTopic.FUNNY_FAILS,
    )

    assert script.clip_index == 1
    assert script.commentary.startswith(DDOI_INTRO)
    assert "To start off," in script.commentary
    assert script.creator_credit == "Credit: @funnycats"
    assert script.voiceover_duration_sec > 0


def test_final_clip_outro_signoff():
    """Verify the last clip in the compilation concludes with the DDoI outro."""
    candidate = ClipCandidate(
        id="c10",
        title="Robot folds shirt perfectly",
        creator_handle="u/robotics_fan",
    )
    analysis = ClipAnalysis(
        summary="A robot folds a laundry basket in seconds",
        punchline_sec=5.0,
    )

    script = generate_clip_script(
        candidate=candidate,
        analysis=analysis,
        clip_index=10,
        total_clips=10,
        topic=NicheTopic.GADGETS,
    )

    assert script.clip_index == 10
    assert "And finally," in script.commentary
    assert DDOI_OUTRO in script.commentary
    assert script.creator_credit == "Credit: u/robotics_fan"


def test_middle_clip_formatting():
    """Verify middle clips do not have intro or outro tags."""
    candidate = ClipCandidate(
        id="c4",
        title="Dog catches frisbee in mid-air",
        creator_handle="@doggo",
    )
    analysis = ClipAnalysis(
        summary="A dog makes an acrobatic leap for a frisbee",
        punchline_sec=3.5,
    )

    script = generate_clip_script(
        candidate=candidate,
        analysis=analysis,
        clip_index=4,
        total_clips=10,
        topic=NicheTopic.ANIMALS,
    )

    assert DDOI_INTRO not in script.commentary
    assert DDOI_OUTRO not in script.commentary
    assert script.creator_credit == "Credit: @doggo"
    assert len(script.commentary.split()) <= 25


def test_scriptwriter_with_mock_gemini():
    """Verify scriptwriter parses custom commentary from Gemini."""
    candidate = ClipCandidate(
        id="c2",
        title="Skater tries rail",
        creator_handle="@skate",
    )
    analysis = ClipAnalysis(
        summary="Skater slips on metal rail",
        punchline_sec=3.0,
    )

    mock_response = MagicMock()
    mock_response.text = '{"commentary": "This skater thought gravity was just a suggestion."}'

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("brain.scriptwriter.is_gemini_available", return_value=True):
        with patch("brain.scriptwriter.get_gemini_client", return_value=mock_client):
            script = generate_clip_script(
                candidate=candidate,
                analysis=analysis,
                clip_index=2,
                total_clips=5,
            )
            assert "This skater thought gravity was just a suggestion." in script.commentary

