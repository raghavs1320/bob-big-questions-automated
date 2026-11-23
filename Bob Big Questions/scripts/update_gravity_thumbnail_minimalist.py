"""Upgraded Minimalist Netflix-Style Thumbnail for Episode 3:
'What If Gravity Disappeared For 60 Seconds?'

Applies the user-approved Netflix-level minimalist YouTube thumbnail design:
- NO background boxes / pills around the text.
- NO heavy stroke borders around the letters.
- Massive, ultra-readable 120pt studio typography with soft natural elevation shadow.
- High-contrast visual storytelling (Normal 1G Grounded World vs 0G Floating Chaos).
- Bottom yellow description badges completely removed for maximum clean CTR.
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

from scripts.render_gravity_disappeared_2m30s import draw_bob, draw_cat

WIDTH, HEIGHT = 1920, 1080
THUMBNAILS_DIR = BASE_DIR / "exports" / "thumbnails"
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

FONT_IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
FONT_ARIAL_ROUNDED = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"


def get_font(size: int = 40, font_type: str = "impact"):
    if font_type == "impact" and os.path.exists(FONT_IMPACT):
        try:
            return ImageFont.truetype(FONT_IMPACT, size=size)
        except Exception:
            pass
    elif font_type == "rounded" and os.path.exists(FONT_ARIAL_ROUNDED):
        try:
            return ImageFont.truetype(FONT_ARIAL_ROUNDED, size=size)
        except Exception:
            pass
    elif font_type == "futura" and os.path.exists(FONT_FUTURA):
        try:
            return ImageFont.truetype(FONT_FUTURA, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_clean_centered_text(draw, cx: int, cy: int, text: str, font, fill=(255, 255, 255), shadow_color=(0, 0, 0, 240), shadow_offset=(0, 7)):
    """Draws pure, modern, minimalist typography.
    NO border outlines, NO background boxes. Crisp studio typography with natural soft drop shadow.
    """
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    draw_x = cx - (x0 + x1) / 2.0
    draw_y = cy - (y0 + y1) / 2.0

    if shadow_color:
        sx, sy = shadow_offset
        draw.text((draw_x + sx, draw_y + sy), text, font=font, fill=shadow_color)

    draw.text((draw_x, draw_y), text, font=font, fill=fill)


def draw_coffee_cup(draw, cx, cy, floating=False, tilt=0.0):
    """Draws a cute stylized coffee mug with or without floating liquid."""
    # Cup body
    draw.rounded_rectangle([cx - 35, cy - 30, cx + 35, cy + 30], radius=8, fill=(235, 77, 75), outline=(180, 40, 40), width=4)
    # Cup handle
    draw.arc([cx + 25, cy - 20, cx + 60, cy + 20], start=-90, end=90, fill=(235, 77, 75), width=8)
    # Liquid
    draw.ellipse([cx - 28, cy - 36, cx + 28, cy - 24], fill=(109, 76, 65))
    if floating:
        # Floating coffee droplets
        draw.ellipse([cx - 50, cy - 65, cx - 35, cy - 50], fill=(109, 76, 65))
        draw.ellipse([cx + 30, cy - 80, cx + 48, cy - 62], fill=(109, 76, 65))
        draw.ellipse([cx - 10, cy - 95, cx + 8, cy - 77], fill=(109, 76, 65))


def build_minimalist_gravity_thumbnail():
    thumb_img = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 35))
    draw_th = ImageDraw.Draw(thumb_img, "RGBA")
    cx, cy = WIDTH // 2, HEIGHT // 2

    # 1. SPLIT-SCREEN BACKGROUND
    # Left half: Cozy 1G Room with warm walls and sturdy wooden floor
    draw_th.rectangle([0, 0, WIDTH // 2, HEIGHT], fill=(253, 248, 235))
    draw_th.rectangle([0, HEIGHT - 220, WIDTH // 2, HEIGHT], fill=(238, 198, 128))
    # Wood floor planks
    for y_line in range(HEIGHT - 220, HEIGHT, 45):
        draw_th.line([(0, y_line), (WIDTH // 2, y_line)], fill=(215, 175, 105), width=2)

    # Left side: Grounded desk / table
    table_top = HEIGHT - 280
    draw_th.rectangle([120, table_top, 480, table_top + 30], fill=(160, 110, 60))
    draw_th.rectangle([150, table_top + 30, 180, HEIGHT - 220], fill=(130, 90, 45))
    draw_th.rectangle([420, table_top + 30, 450, HEIGHT - 220], fill=(130, 90, 45))
    # Plant on table (grounded, upright)
    draw_th.polygon([(260, table_top), (340, table_top), (325, table_top - 50), (275, table_top - 50)], fill=(225, 112, 85))
    draw_th.ellipse([270, table_top - 95, 330, table_top - 45], fill=(46, 204, 113))
    # Grounded mug on table
    draw_coffee_cup(draw_th, 400, table_top - 32, floating=False)

    # Left side ambient window with sunny blue sky
    draw_th.rounded_rectangle([150, 250, 420, 480], radius=15, fill=(135, 206, 250), outline=(220, 220, 220), width=8)
    draw_th.line([(285, 250), (285, 480)], fill=(220, 220, 220), width=6)
    draw_th.line([(150, 365), (420, 365)], fill=(220, 220, 220), width=6)

    # Right half: Cosmic 0G Zero-Gravity Void
    draw_th.rectangle([WIDTH // 2, 0, WIDTH, HEIGHT], fill=(15, 20, 45))

    # Floating particles / stars in the zero-g void
    np.random.seed(101)
    for _ in range(60):
        sx = WIDTH // 2 + int(np.random.uniform(30, WIDTH // 2 - 30))
        sy = int(np.random.uniform(180, HEIGHT - 60))
        bright = np.random.randint(180, 255)
        r = np.random.choice([2, 3, 4])
        draw_th.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(bright, bright, bright, 220))

    # Neon Electric Cyan Dividing Line
    draw_th.line([(WIDTH // 2, 0), (WIDTH // 2, HEIGHT)], fill=(0, 230, 220), width=12)

    # 2. Right side: Floating Zero-G Objects
    # Floating giant shimmering water blob
    wb_x, wb_y = WIDTH - 280, 320
    draw_th.ellipse([wb_x - 90, wb_y - 70, wb_x + 90, wb_y + 70], fill=(9, 132, 227, 210), outline=(129, 236, 236), width=5)
    draw_th.ellipse([wb_x - 55, wb_y - 45, wb_x - 20, wb_y - 20], fill=(255, 255, 255, 180)) # highlight
    # Smaller water bubbles
    draw_th.ellipse([wb_x + 70, wb_y - 90, wb_x + 110, wb_y - 50], fill=(9, 132, 227, 190), outline=(129, 236, 236), width=3)
    draw_th.ellipse([wb_x - 110, wb_y + 60, wb_x - 80, wb_y + 90], fill=(9, 132, 227, 190), outline=(129, 236, 236), width=3)

    # Floating coffee cup with suspended droplets
    draw_coffee_cup(draw_th, WIDTH - 450, 480, floating=True)

    # Floating surprised cartoon cat
    draw_cat(draw_th, WIDTH - 240, cy + 200, angle_deg=25.0)

    # Floating apple
    draw_th.ellipse([WIDTH - 380, cy + 260, WIDTH - 330, cy + 310], fill=(235, 77, 75))
    draw_th.line([(WIDTH - 355, cy + 260), (WIDTH - 350, cy + 245)], fill=(100, 60, 30), width=4)

    # 3. Center Focal Point: Bob floating horizontally with shocked expression!
    draw_bob(draw_th, WIDTH // 2, cy + 50, mood="shocked", t_sec=1.0, floating=True, clothes="hoodie")

    # 4. NETFLIX-LEVEL MINIMALIST TYPOGRAPHY
    # Title at top: Pure white, 120pt, subtle drop shadow, NO box, NO border
    title_font = get_font(size=120, font_type="impact")
    draw_clean_centered_text(
        draw_th,
        cx=cx,
        cy=115,
        text="WHAT IF GRAVITY DISAPPEARED?",
        font=title_font,
        fill=(255, 255, 255),
        shadow_color=(0, 0, 0, 245),
        shadow_offset=(0, 7)
    )

    # 5. Export to standard 1280x720 Full HD YouTube thumbnail
    thumb_final = thumb_img.resize((1280, 720), Image.Resampling.LANCZOS)

    out_jpg = THUMBNAILS_DIR / "Gravity_Disappeared_Thumbnail.jpg"
    out_png = THUMBNAILS_DIR / "Gravity_Disappeared_Thumbnail.png"

    # Save backup of legacy version if not already saved
    legacy_jpg = THUMBNAILS_DIR / "Gravity_Disappeared_Thumbnail_legacy.jpg"
    if out_jpg.exists() and not legacy_jpg.exists():
        import shutil
        shutil.copyfile(str(out_jpg), str(legacy_jpg))

    thumb_final.save(str(out_jpg), "JPEG", quality=95)
    thumb_final.save(str(out_png), "PNG")
    print(f"✅ Generated upgraded minimalist gravity thumbnail: {out_jpg}")
    return str(out_jpg)


if __name__ == "__main__":
    build_minimalist_gravity_thumbnail()
