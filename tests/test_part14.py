"""Test suite for Part 14: Production Packaging & Live Launch."""

from pathlib import Path
import pytest
from config import EXPORTS_DIR
from utils.hardware import get_video_info


def test_production_packaging_files():
    """Verify production Dockerfile and docker-compose files exist."""
    dockerfile = Path("Dockerfile")
    compose = Path("docker-compose.yml")
    assert dockerfile.exists(), "Dockerfile missing"
    assert compose.exists(), "docker-compose.yml missing"

    content = dockerfile.read_text(encoding="utf-8")
    assert "FROM python" in content
    assert "ffmpeg" in content
    assert "EXPOSE 8501" in content


def test_netflix_edition_video_deliverable():
    """Verify that the rendered Netflix-Grade video exists and meets high-definition specifications."""
    final_video = EXPORTS_DIR / "DailyDose_Netflix_Edition.mp4"
    assert final_video.exists(), f"Video deliverable missing: {final_video}"
    assert final_video.stat().st_size > 100000, "Video file too small"

    info = get_video_info(str(final_video))
    assert info["width"] == 1920
    assert info["height"] == 1080
    assert info["has_audio"] is True
    assert info["duration"] > 10.0
