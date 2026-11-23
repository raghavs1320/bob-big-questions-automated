"""High-CTR YouTube Thumbnail Generator for Daily Dose Studio.

Produces broadcast-ready, eye-catching 1280x720 thumbnails:
- Peak-action frame extraction with sub-second accuracy.
- Cinematic color enhancement (saturation, contrast, sharpness).
- Dark radial vignette to focus viewer eyes on the central subject.
- Bold, legible text hooks in Impact / Arial Black typography.
- High-visibility yellow keyword highlighting and heavy black drop-strokes.
- YouTube UI safe zone placement (never covered by the bottom-right timestamp).
"""

import math
import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from config import EXPORTS_DIR, TEMP_DIR
from utils.hardware import get_ffmpeg_binary
from utils.logger import logger

# Recommended system font paths on macOS
SYSTEM_FONTS = [
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/SFNS.ttf",
]


def get_thumbnail_font(size: int = 76) -> ImageFont.FreeTypeFont:
    """Finds the best available high-impact font on the system."""
    for font_path in SYSTEM_FONTS:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def extract_video_frame(video_path: str, timestamp_sec: float, output_path: str) -> str:
    """Extracts a single high-quality frame from a video at the specified timestamp."""
    ffmpeg_bin = get_ffmpeg_binary()
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg_bin,
        "-y",
        "-ss",
        f"{timestamp_sec:.2f}",
        "-i",
        video_path,
        "-vframes",
        "1",
        "-q:v",
        "2",
        str(out_file),
    ]

    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return str(out_file)


def apply_cinematic_vignette(image: Image.Image, intensity: float = 0.45) -> Image.Image:
    """Applies a smooth radial dark vignette around the edges of the image."""
    width, height = image.size
    vignette = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(vignette)

    max_dist = math.sqrt((width / 2) ** 2 + (height / 2) ** 2)
    center_x, center_y = width / 2, height / 2

    # Draw gradient rings from center outward
    steps = 40
    for i in range(steps):
        r_ratio = i / steps
        radius_x = (width / 2) * (0.6 + 0.5 * r_ratio)
        radius_y = (height / 2) * (0.6 + 0.5 * r_ratio)
        alpha = int(255 * (r_ratio ** 2) * intensity)
        bbox = [
            center_x - radius_x,
            center_y - radius_y,
            center_x + radius_x,
            center_y + radius_y,
        ]
        draw.ellipse(bbox, outline=alpha, width=int(max_dist / steps) + 2)

    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=30))
    black_layer = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    black_layer.putalpha(vignette)

    base = image.convert("RGBA")
    base.paste(black_layer, (0, 0), black_layer)
    return base.convert("RGB")


def enhance_visual_pop(image: Image.Image) -> Image.Image:
    """Enhances saturation, contrast, and sharpness for high-CTR mobile and desktop display."""
    # 1. Resize and crop to 1280x720 (16:9) preserving aspect ratio
    target_w, target_h = 1280, 720
    img_w, img_h = image.size
    scale = max(target_w / img_w, target_h / img_h)
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)
    resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Center crop
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    cropped = resized.crop((left, top, left + target_w, top + target_h))

    # 2. Boost Saturation (+25%)
    sat_enhancer = ImageEnhance.Color(cropped)
    popped = sat_enhancer.enhance(1.25)

    # 3. Boost Contrast (+15%)
    contrast_enhancer = ImageEnhance.Contrast(popped)
    popped = contrast_enhancer.enhance(1.15)

    # 4. Boost Sharpness (+20%)
    sharp_enhancer = ImageEnhance.Sharpness(popped)
    popped = sharp_enhancer.enhance(1.20)

    # 5. Apply subtle edge vignette
    vignetted = apply_cinematic_vignette(popped, intensity=0.40)
    return vignetted


def render_thumbnail_text(
    image: Image.Image,
    text: str,
    highlight_word: Optional[str] = None,
    position: str = "top",
) -> Image.Image:
    """Renders bold high-contrast text with thick black outline and drop shadow."""
    draw = ImageDraw.Draw(image)
    font = get_thumbnail_font(size=82)

    words = text.strip().split()
    if not words:
        return image

    # Measure total line width and height
    space_w = font.getbbox(" ")[2] - font.getbbox(" ")[0]
    word_boxes = [font.getbbox(w) for w in words]
    word_widths = [b[2] - b[0] for b in word_boxes]
    line_h = max(b[3] - b[1] for b in word_boxes)
    total_w = sum(word_widths) + space_w * (len(words) - 1)

    # Position coordinates (safe from YouTube bottom-right timestamp badge)
    canvas_w, canvas_h = image.size
    start_x = (canvas_w - total_w) // 2
    if position == "top":
        start_y = 60
    elif position == "center":
        start_y = (canvas_h - line_h) // 2
    else:
        # Bottom, but leave margin for YouTube's 140x40px bottom-right badge
        start_y = canvas_h - line_h - 100

    stroke_width = 8
    cur_x = start_x

    for word, w_width in zip(words, word_widths):
        # Determine word color: Highlight word in electric yellow, others in pure white
        is_highlight = highlight_word and (word.upper() == highlight_word.upper())
        fill_color = (255, 235, 59) if is_highlight else (255, 255, 255)

        # Draw deep drop shadow
        draw.text(
            (cur_x + 6, start_y + 8),
            word,
            font=font,
            fill=(0, 0, 0, 200),
            stroke_width=stroke_width,
            stroke_fill=(0, 0, 0),
        )

        # Draw main text with bold black stroke
        draw.text(
            (cur_x, start_y),
            word,
            font=font,
            fill=fill_color,
            stroke_width=stroke_width,
            stroke_fill=(0, 0, 0),
        )

        cur_x += w_width + space_w

    return image


def add_red_focal_ring(
    image: Image.Image,
    center_xy: Tuple[int, int],
    radius: int = 90,
) -> Image.Image:
    """Draws a clean, viral red attention circle around the main focal point."""
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = center_xy

    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]

    # Outer glow
    draw.ellipse(
        [cx - radius - 3, cy - radius - 3, cx + radius + 3, cy + radius + 3],
        outline=(0, 0, 0, 160),
        width=10,
    )
    # Bright neon red stroke
    draw.ellipse(bbox, outline=(255, 42, 42, 255), width=7)

    base = image.convert("RGBA")
    combined = Image.alpha_composite(base, overlay)
    return combined.convert("RGB")


def create_youtube_thumbnail(
    video_path: str,
    output_path: Optional[str] = None,
    timestamp_sec: float = 2.0,
    text_hook: str = "WAIT FOR THE END...",
    highlight_word: Optional[str] = "WAIT",
    focal_point: Optional[Tuple[int, int]] = None,
) -> str:
    """End-to-end generator: extracts peak frame, optimizes color/contrast, and adds high-CTR text."""
    if output_path is None:
        output_path = str(EXPORTS_DIR / "DailyDose_Thumbnail.jpg")

    temp_frame = str(TEMP_DIR / "raw_thumb_frame.png")

    logger.info(f"🎨 Generating High-CTR Thumbnail from '{video_path}' at {timestamp_sec:.1f}s...")
    extract_video_frame(video_path, timestamp_sec, temp_frame)

    with Image.open(temp_frame) as raw_img:
        popped_img = enhance_visual_pop(raw_img)

        # Add red focal ring if coordinates provided
        if focal_point:
            popped_img = add_red_focal_ring(popped_img, focal_point)

        # Render bold text hook
        final_img = render_thumbnail_text(
            popped_img,
            text=text_hook,
            highlight_word=highlight_word,
            position="top",
        )

        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Save high quality JPEG (quality 95)
        final_img.save(str(out_path), "JPEG", quality=95, optimize=True)

        # Also save crisp PNG version
        png_path = out_path.with_suffix(".png")
        final_img.save(str(png_path), "PNG")

    logger.success(f"🖼️ High-CTR Thumbnail ready: {out_path} (1280x720 16:9)")
    return str(out_path)
