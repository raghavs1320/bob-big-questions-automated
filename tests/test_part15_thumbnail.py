"""Tests for High-CTR YouTube Thumbnail Generator."""

import os
from pathlib import Path
from editor.thumbnail import (
    apply_cinematic_vignette,
    create_youtube_thumbnail,
    enhance_visual_pop,
    get_thumbnail_font,
    render_thumbnail_text,
)
from PIL import Image
from utils.hardware import generate_synthetic_test_clip


def test_thumbnail_font_loader():
    font = get_thumbnail_font(size=72)
    assert font is not None


def test_enhance_visual_pop_and_vignette():
    img = Image.new("RGB", (640, 480), (100, 150, 200))
    popped = enhance_visual_pop(img)
    assert popped.size == (1280, 720)


def test_render_thumbnail_text():
    img = Image.new("RGB", (1280, 720), (50, 50, 50))
    drawn = render_thumbnail_text(img, text="HE DID NOT EXPECT THIS", highlight_word="NOT")
    assert drawn.size == (1280, 720)


def test_end_to_end_thumbnail_generation(tmp_path):
    test_video = tmp_path / "test_thumb_clip.mp4"
    out_thumb = tmp_path / "thumb.jpg"

    generate_synthetic_test_clip(str(test_video), duration_sec=3.0, color="forestgreen")

    result = create_youtube_thumbnail(
        video_path=str(test_video),
        output_path=str(out_thumb),
        timestamp_sec=1.0,
        text_hook="WAIT TILL THE END...",
        highlight_word="WAIT",
    )

    assert os.path.exists(result)
    assert os.path.getsize(result) > 1000
    with Image.open(result) as im:
        assert im.size == (1280, 720)
