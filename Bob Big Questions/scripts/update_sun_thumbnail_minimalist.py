"""Upgraded Minimalist Netflix-Style Thumbnail for Episode 2:
'What If The Sun Disappeared For 7 Days?'

Takes the beloved split-screen composition (Sunny Paradise vs Dark Void)
and applies Netflix-level minimalist polish:
- NO background boxes / pills around the text.
- NO heavy stroke borders around the letters.
- Pure, clean, high-impact modern typography with natural elevation shadow.
"""

import math
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.render_sun_disappeared_2min import draw_bob

WIDTH, HEIGHT = 1920, 1080
THUMBNAILS_DIR = BASE_DIR / "exports" / "thumbnails"
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

FONT_ARIAL_ROUNDED = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"
FONT_IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"


def get_font(size: int = 40, font_type: str = "rounded"):
    if font_type == "rounded" and os.path.exists(FONT_ARIAL_ROUNDED):
        try:
            return ImageFont.truetype(FONT_ARIAL_ROUNDED, size=size)
        except Exception:
            pass
    elif font_type == "futura" and os.path.exists(FONT_FUTURA):
        try:
            return ImageFont.truetype(FONT_FUTURA, size=size)
        except Exception:
            pass
    elif font_type == "impact" and os.path.exists(FONT_IMPACT):
        try:
            return ImageFont.truetype(FONT_IMPACT, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_clean_centered_text(draw, cx: int, cy: int, text: str, font, fill=(255, 255, 255), shadow_color=(0, 0, 0, 220), shadow_offset=(0, 5)):
    """Draws pure, modern, minimalist typography.

    NO border outlines, NO background boxes. Just crisp studio typography with natural soft drop shadow.
    """
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    draw_x = cx - (x0 + x1) / 2.0
    draw_y = cy - (y0 + y1) / 2.0

    # Soft drop shadow for legibility without any borders
    if shadow_color:
        sx, sy = shadow_offset
        draw.text((draw_x + sx, draw_y + sy), text, font=font, fill=shadow_color)

    # Crisp clean foreground text
    draw.text((draw_x, draw_y), text, font=font, fill=fill)


def build_minimalist_split_thumbnail():
    thumb_img = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 35))
    draw_th = ImageDraw.Draw(thumb_img, "RGBA")
    cx, cy = WIDTH // 2, HEIGHT // 2

    # 1. SPLIT-SCREEN BACKGROUND (The user's preferred composition)
    # Left half: bright sunny tropical beach & azure sky
    draw_th.rectangle([0, 0, WIDTH // 2, HEIGHT], fill=(130, 204, 221))
    draw_th.chord([-200, HEIGHT - 260, WIDTH // 2 + 100, HEIGHT + 400], start=180, end=360, fill=(250, 211, 144))

    # Right half: dark cosmic void
    draw_th.rectangle([WIDTH // 2, 0, WIDTH, HEIGHT], fill=(10, 12, 24))

    # Realistic twinkling stars on the right void
    np.random.seed(42)
    for _ in range(75):
        sx = WIDTH // 2 + int(np.random.uniform(20, WIDTH // 2 - 20))
        sy = int(np.random.uniform(20, HEIGHT - 80))
        bright = np.random.randint(140, 255)
        r = np.random.choice([1, 2, 2, 3])
        draw_th.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(bright, bright, bright))

    # Center split neon lightning line
    draw_th.line([(WIDTH // 2, 0), (WIDTH // 2, HEIGHT)], fill=(255, 234, 167), width=12)

    # 2. Left side: Glowing Golden Sun with cool sunglasses
    sun_left_x, sun_left_y = 220, 250
    # Gentle warm aura
    draw_th.ellipse([sun_left_x - 110, sun_left_y - 110, sun_left_x + 110, sun_left_y + 110], fill=(255, 230, 120, 120))
    draw_th.ellipse([sun_left_x - 90, sun_left_y - 90, sun_left_x + 90, sun_left_y + 90], fill=(255, 185, 45), outline=(225, 112, 85), width=6)
    # Cool sunglasses on the sun
    draw_th.rounded_rectangle([sun_left_x - 65, sun_left_y - 20, sun_left_x + 65, sun_left_y + 15], radius=10, fill=(30, 30, 30))
    # Cheerful sun smile
    draw_th.arc([sun_left_x - 45, sun_left_y + 15, sun_left_x + 45, sun_left_y + 55], start=20, end=160, fill=(200, 60, 40), width=5)

    # 3. Right side: Extinguished Dead Sun with huge bold red X
    sun_right_x, sun_right_y = WIDTH - 220, 250
    draw_th.ellipse([sun_right_x - 90, sun_right_y - 90, sun_right_x + 90, sun_right_y + 90], fill=(25, 30, 50), outline=(100, 110, 140), width=5)
    # Huge bold red X
    draw_th.line([(sun_right_x - 70, sun_right_y - 70), (sun_right_x + 70, sun_right_y + 70)], fill=(235, 77, 75), width=14)
    draw_th.line([(sun_right_x + 70, sun_right_y - 70), (sun_right_x - 70, sun_right_y + 70)], fill=(235, 77, 75), width=14)

    # 4. Focal Point: Bob right in the center with his iconic shocked reaction!
    draw_bob(draw_th, WIDTH // 2, cy + 70, mood="shocked", t_sec=1.0, clothes="hawaiian")

    # 5. NETFLIX-LEVEL MINIMALIST TYPOGRAPHY (NO BOXES, NO BORDERS, NO BOTTOM TEXT)
    # Primary Title at top (Much larger, bold, pure white with soft elevation drop shadow)
    title_font = get_font(size=130, font_type="impact")
    draw_clean_centered_text(
        draw_th,
        cx=cx,
        cy=115,
        text="WHAT IF THE SUN VANISHED?",
        font=title_font,
        fill=(255, 255, 255),
        shadow_color=(0, 0, 0, 240),
        shadow_offset=(0, 7)
    )

    # (Bottom yellow description text completely removed per user request for ultra-clean visibility)

    # Resize cleanly to 1280x720 Full HD YouTube thumbnail
    thumb_final = thumb_img.resize((1280, 720), Image.Resampling.LANCZOS)

    out_jpg = THUMBNAILS_DIR / "Sun_Disappeared_Thumbnail.jpg"
    out_png = THUMBNAILS_DIR / "Sun_Disappeared_Thumbnail.png"

    thumb_final.save(str(out_jpg), "JPEG", quality=95)
    thumb_final.save(str(out_png), "PNG")
    print(f"✅ Generated upgraded minimalist split thumbnail: {out_jpg}")
    return str(out_jpg)


if __name__ == "__main__":
    build_minimalist_split_thumbnail()
