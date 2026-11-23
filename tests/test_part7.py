"""Test suite for Part 7: Multimodal AI Brain & Temporal Climax Detector."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from brain.analyzer import (
    analyze_clip_heuristics,
    analyze_clip_vision,
    clean_json_response,
)
from config import TEMP_DIR
from models import ClipAnalysis
from utils.hardware import generate_synthetic_test_clip


def test_clean_json_response():
    """Verify markdown fences are stripped from LLM JSON responses."""
    raw = "```json\n{\"summary\": \"Cat jumps\", \"punchline_sec\": 4.2}\n```"
    cleaned = clean_json_response(raw)
    data = json.loads(cleaned)
    assert data["summary"] == "Cat jumps"
    assert data["punchline_sec"] == 4.2


def test_analyze_clip_heuristics_on_video():
    """Verify heuristic analyzer computes valid temporal cuts on a video file."""
    test_video = TEMP_DIR / "part7_heuristic_test.mp4"
    if test_video.exists():
        test_video.unlink()

    # Generate 4-second synthetic test video
    generate_synthetic_test_clip(str(test_video), duration_sec=4.0)

    analysis = analyze_clip_heuristics(str(test_video), title="Skater slips on rail")
    assert isinstance(analysis, ClipAnalysis)
    assert analysis.suggested_start_sec == 0.0
    assert analysis.suggested_end_sec == 4.0
    assert 2.0 <= analysis.punchline_sec <= 3.0
    assert analysis.is_engaging is True

    # Cleanup
    if test_video.exists():
        test_video.unlink()


def test_analyze_clip_vision_with_mock_gemini():
    """Verify Gemini multimodal response parsing."""
    test_video = TEMP_DIR / "part7_vision_test.mp4"
    if test_video.exists():
        test_video.unlink()
    generate_synthetic_test_clip(str(test_video), duration_sec=5.0)

    mock_gemini_json = {
        "summary": "Dog attempts to jump onto sofa but slips on rug",
        "is_engaging": True,
        "suggested_start_sec": 1.0,
        "suggested_end_sec": 4.5,
        "punchline_sec": 3.2,
        "has_commercial_watermark": False,
        "has_copyrighted_music": False,
    }

    mock_response = MagicMock()
    mock_response.text = f"```json\n{json.dumps(mock_gemini_json)}\n```"

    mock_client = MagicMock()
    mock_client.files.upload.return_value = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("brain.analyzer.is_gemini_available", return_value=True):
        with patch("brain.analyzer.get_gemini_client", return_value=mock_client):
            analysis = analyze_clip_vision(str(test_video), title="Dog jump fail")

            assert analysis.summary == "Dog attempts to jump onto sofa but slips on rug"
            assert analysis.suggested_start_sec == 1.0
            assert analysis.suggested_end_sec == 4.5
            assert analysis.punchline_sec == 3.2
            assert analysis.is_engaging is True

    # Cleanup
    if test_video.exists():
        test_video.unlink()

