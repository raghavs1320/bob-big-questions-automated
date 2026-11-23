"""High-CTR YouTube Thumbnail Generator for Episode 8:
'What If Earth Lost Oxygen For 5 Seconds?'

Design & Psychological Anchors:
- 2-line minimalist typography (NO boxes around text, NO stroke outlines, NO bottom clutter text).
- Line 1: 'WHAT IF EARTH' (Pure White, 130pt Impact)
- Line 2: 'LOST OXYGEN FOR 5 SECONDS?' (Radiant Warning Yellow #FFDD33, 140pt Impact)
- Shocked Bob holding his breath with puffed-out cheeks, red face, clutching his throat.
- Daytime pitch-black sky with stars and blinding sun.
- City skyscrapers crumbling into billowing white clouds of concrete dust.
- Cracking ground with abyss sinkhole.
- Tabby cat with puffed cheeks holding breath!
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

WIDTH, HEIGHT = 1920, 1080
THUMBNAILS_DIR = BASE_DIR / "exports" / "thumbnails"
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

FONT_IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
FONT_ARIAL_ROUNDED = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"


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
    return ImageFont.load_default()


def draw_clean_centered_text(draw, cx: int, cy: int, text: str, font, fill=(255, 255, 255), shadow_color=(0, 0, 0, 245), shadow_offset=(0, 8)):
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    draw_x = cx - (x0 + x1) / 2.0
    draw_y = cy - (y0 + y1) / 2.0

    if shadow_color:
        sx, sy = shadow_offset
        draw.text((draw_x + sx, draw_y + sy), text, font=font, fill=shadow_color)
        draw.text((draw_x + sx * 1.5, draw_y + sy * 1.5), text, font=font, fill=(0, 0, 0, 160))

    draw.text((draw_x, draw_y), text, font=font, fill=fill)


def draw_bob_holding_breath(draw, bx, by, scale=1.22):
    """Draws Bob with puffed cheeks holding his breath, red face, hands clutching collar."""
    radius = int(95 * scale)

    # Cyan/Teal Hoodie Body
    draw.rounded_rectangle([bx - int(75 * scale), by + int(65 * scale), bx + int(75 * scale), by + int(230 * scale)], radius=int(28 * scale), fill=(0, 206, 201), outline=(40, 30, 30), width=int(6 * scale))
    # Coral shorts
    draw.rounded_rectangle([bx - int(70 * scale), by + int(220 * scale), bx + int(70 * scale), by + int(300 * scale)], radius=int(15 * scale), fill=(255, 107, 129), outline=(40, 30, 30), width=int(5 * scale))

    # Legs
    draw.line([(bx - int(35 * scale), by + int(300 * scale)), (bx - int(55 * scale), by + int(370 * scale))], fill=(255, 218, 185), width=int(22 * scale))
    draw.line([(bx + int(35 * scale), by + int(300 * scale)), (bx + int(55 * scale), by + int(370 * scale))], fill=(255, 218, 185), width=int(22 * scale))
    draw.ellipse([bx - int(75 * scale), by + int(365 * scale), bx - int(35 * scale), by + int(395 * scale)], fill=(254, 202, 87), outline=(40, 30, 30), width=4)
    draw.ellipse([bx + int(35 * scale), by + int(365 * scale), bx + int(75 * scale), by + int(395 * scale)], fill=(254, 202, 87), outline=(40, 30, 30), width=4)

    # Hands clutching neck/throat in panic
    arm_w = int(22 * scale)
    draw.line([(bx - int(70 * scale), by + int(100 * scale)), (bx - int(30 * scale), by + int(70 * scale))], fill=(0, 206, 201), width=arm_w)
    draw.line([(bx + int(70 * scale), by + int(100 * scale)), (bx + int(30 * scale), by + int(70 * scale))], fill=(0, 206, 201), width=arm_w)
    draw.ellipse([bx - int(45 * scale), by + int(55 * scale), bx - int(10 * scale), by + int(85 * scale)], fill=(255, 180, 160), outline=(40, 30, 30), width=3)
    draw.ellipse([bx + int(10 * scale), by + int(55 * scale), bx + int(45 * scale), by + int(85 * scale)], fill=(255, 180, 160), outline=(40, 30, 30), width=3)

    # Bob's Head (Flushed reddish peach from holding breath!)
    draw.ellipse([bx - radius, by - radius, bx + radius, by + radius], fill=(255, 180, 160), outline=(40, 30, 30), width=int(6 * scale))

    # Puffed Cheeks (huge swollen cheeks!)
    draw.ellipse([bx - int(115 * scale), by - int(10 * scale), bx - int(65 * scale), by + int(50 * scale)], fill=(255, 140, 140), outline=(220, 60, 60), width=4)
    draw.ellipse([bx + int(65 * scale), by - int(10 * scale), bx + int(115 * scale), by + int(50 * scale)], fill=(255, 140, 140), outline=(220, 60, 60), width=4)

    # Hair (Messy brown tufts)
    hair_color = (101, 67, 33)
    draw.arc([bx - radius + int(10 * scale), by - radius - int(25 * scale), bx + radius - int(10 * scale), by - radius + int(45 * scale)], start=180, end=360, fill=hair_color, width=int(22 * scale))
    draw.ellipse([bx - int(25 * scale), by - radius - int(32 * scale), bx + int(30 * scale), by - radius + int(8 * scale)], fill=hair_color)

    # Giant Wide Eyes (bulging from holding breath!)
    for eye_x in (bx - int(42 * scale), bx + int(42 * scale)):
        draw.ellipse([eye_x - int(34 * scale), by - int(18 * scale) - int(34 * scale), eye_x + int(34 * scale), by - int(18 * scale) + int(34 * scale)], fill=(255, 255, 255), outline=(40, 30, 30), width=int(5 * scale))
        draw.ellipse([eye_x - int(8 * scale), by - int(22 * scale), eye_x + int(8 * scale), by - int(6 * scale)], fill=(20, 20, 20))
        draw.ellipse([eye_x - int(4 * scale), by - int(20 * scale), eye_x, by - int(16 * scale)], fill=(255, 255, 255))
        # Bloodshot red eye veins
        draw.line([(eye_x - int(25 * scale), by - int(28 * scale)), (eye_x - int(12 * scale), by - int(22 * scale))], fill=(235, 77, 75), width=2)
        draw.line([(eye_x + int(25 * scale), by - int(28 * scale)), (eye_x + int(12 * scale), by - int(22 * scale))], fill=(235, 77, 75), width=2)

    # Tight clamped mouth (holding breath shut!)
    draw.line([(bx - int(25 * scale), by + int(32 * scale)), (bx + int(25 * scale), by + int(32 * scale))], fill=(180, 40, 40), width=int(7 * scale))

    # Floating Panic Sweat Droplets
    draw.ellipse([bx - int(115 * scale), by - int(55 * scale), bx - int(92 * scale), by - int(30 * scale)], fill=(129, 236, 236), outline=(9, 132, 227), width=3)
    draw.ellipse([bx + int(100 * scale), by - int(45 * scale), bx + int(120 * scale), by - int(20 * scale)], fill=(129, 236, 236), outline=(9, 132, 227), width=3)


def draw_cat_holding_breath(draw, cx, cy):
    """Draws Bob's orange tabby cat with puffed cheeks holding breath."""
    draw.ellipse([cx - 45, cy - 30, cx + 45, cy + 30], fill=(243, 156, 18), outline=(40, 30, 30), width=4)
    draw.ellipse([cx - 30, cy - 60, cx + 30, cy], fill=(243, 156, 18), outline=(40, 30, 30), width=4)
    # Puffed cat cheeks
    draw.ellipse([cx - 42, cy - 30, cx - 18, cy], fill=(255, 175, 175), outline=(200, 60, 60), width=3)
    draw.ellipse([cx + 18, cy - 30, cx + 42, cy], fill=(255, 175, 175), outline=(200, 60, 60), width=3)
    # Ears
    draw.polygon([(cx - 25, cy - 50), (cx - 35, cy - 80), (cx - 10, cy - 58)], fill=(230, 126, 34), outline=(40, 30, 30))
    draw.polygon([(cx + 10, cy - 58), (cx + 35, cy - 80), (cx + 25, cy - 50)], fill=(230, 126, 34), outline=(40, 30, 30))
    # Wide round green eyes
    draw.ellipse([cx - 22, cy - 44, cx - 6, cy - 26], fill=(46, 204, 113), outline=(40, 30, 30), width=3)
    draw.ellipse([cx + 6, cy - 44, cx + 22, cy - 26], fill=(46, 204, 113), outline=(40, 30, 30), width=3)
    draw.ellipse([cx - 16, cy - 38, cx - 12, cy - 32], fill=(20, 20, 20))
    draw.ellipse([cx + 12, cy - 38, cx + 16, cy - 32], fill=(20, 20, 20))


def render_thumbnail_oxygen_masterpiece():
    thumb_img = Image.new("RGB", (WIDTH, HEIGHT), (10, 12, 22))
    draw_th = ImageDraw.Draw(thumb_img, "RGBA")
    cx, cy = WIDTH // 2, HEIGHT // 2

    # 1. PITCH BLACK DAYTIME SKY (The Rayleigh scattering collapse!)
    # Deep space black with bright noon sun
    draw_th.rectangle([0, 0, WIDTH, HEIGHT], fill=(8, 10, 18))

    # Blazing bright noon sun in upper right (blazing white & yellow in black sky)
    sun_x, sun_y = WIDTH - 240, 220
    draw_th.ellipse([sun_x - 110, sun_y - 110, sun_x + 110, sun_y + 110], fill=(255, 255, 200, 100))
    draw_th.ellipse([sun_x - 70, sun_y - 70, sun_x + 70, sun_y + 70], fill=(255, 230, 0), outline=(255, 255, 255), width=6)

    # Stars in daytime black sky
    np.random.seed(88)
    for _ in range(65):
        sx = int(np.random.uniform(30, WIDTH - 30))
        sy = int(np.random.uniform(30, HEIGHT - 350))
        r = np.random.choice([2, 3, 4])
        draw_th.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255, 220))

    # 2. CRUMBLING CONCRETE SKYSCRAPERS TURNING INTO DUST
    # Left skyscraper crumbling into clouds
    draw_th.rectangle([120, HEIGHT - 520, 360, HEIGHT - 220], fill=(120, 130, 140))
    # Huge billowing white dust clouds dissolving the buildings
    dust_clusters = [
        (220, HEIGHT - 540, 95), (320, HEIGHT - 480, 110), (160, HEIGHT - 420, 105),
        (WIDTH - 380, HEIGHT - 460, 120), (WIDTH - 240, HEIGHT - 520, 100), (WIDTH - 150, HEIGHT - 380, 110)
    ]
    for dx, dy, dr in dust_clusters:
        draw_th.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=(235, 238, 242, 220), outline=(180, 190, 200), width=3)
        draw_th.ellipse([dx - dr // 2, dy - dr // 2, dx + dr // 3, dy + dr // 3], fill=(255, 255, 255, 230))

    # Cracking ground with deep sinkhole fissure
    draw_th.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(60, 45, 35))
    # Cracks
    draw_th.polygon([(cx - 200, HEIGHT - 220), (cx + 200, HEIGHT - 220), (cx + 80, HEIGHT), (cx - 80, HEIGHT)], fill=(15, 10, 8))

    # 3. TOP CINEMATIC GRADIENT (1000:1 Contrast for Text)
    for gy in range(330):
        alpha = int(255 * (1.0 - (gy / 330.0) ** 1.35))
        draw_th.line([(0, gy), (WIDTH, gy)], fill=(4, 6, 12, alpha))

    # 4. BOB: THE HERO (Center-Stage, Bulging Eyes, Clutching Throat)
    draw_bob_holding_breath(draw_th, bx=cx - 30, by=cy + 40, scale=1.24)

    # Tabby cat holding breath on right
    draw_cat_holding_breath(draw_th, cx=WIDTH - 280, cy=HEIGHT - 260)

    # 5. POWERHOUSE 2-LINE TYPOGRAPHY
    # Line 1: 'WHAT IF EARTH' (Pure White, 130pt)
    font_line1 = get_font(size=130, font_type="impact")
    draw_clean_centered_text(
        draw_th,
        cx=cx,
        cy=95,
        text="WHAT IF EARTH",
        font=font_line1,
        fill=(255, 255, 255),
        shadow_color=(0, 0, 0, 255),
        shadow_offset=(0, 8)
    )

    # Line 2: 'LOST OXYGEN FOR 5 SECONDS?' (Radiant Warning Yellow, 140pt)
    font_line2 = get_font(size=140, font_type="impact")
    draw_clean_centered_text(
        draw_th,
        cx=cx,
        cy=215,
        text="LOST OXYGEN FOR 5 SECONDS?",
        font=font_line2,
        fill=(255, 221, 51),
        shadow_color=(0, 0, 0, 255),
        shadow_offset=(0, 8)
    )

    # Resize with Lanczos downsampling to 1280x720 YouTube standard
    thumb_final = thumb_img.resize((1280, 720), Image.Resampling.LANCZOS)

    out_jpg = THUMBNAILS_DIR / "Oxygen_Lost_Thumbnail.jpg"
    out_png = THUMBNAILS_DIR / "Oxygen_Lost_Thumbnail.png"

    thumb_final.save(str(out_jpg), "JPEG", quality=96)
    thumb_final.save(str(out_png), "PNG")
    print(f"🎉 Generated High-CTR Masterpiece Thumbnail: {out_jpg}")
    return str(out_jpg)


if __name__ == "__main__":
    render_thumbnail_oxygen_masterpiece()
