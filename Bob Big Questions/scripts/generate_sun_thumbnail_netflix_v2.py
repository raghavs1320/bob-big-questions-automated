"""Netflix-Level Minimalist High-CTR YouTube Thumbnail Generator for Episode 2:
'What If The Sun Disappeared For 7 Days?'

Design & Psychology Specifications:
- High-Concept Visual Storytelling: Deep space void, extinguished dark eclipse Sun with dying corona ring.
- Minimalist Typography: NO background boxes, NO heavy stroke borders. Pure crisp modern typography.
- Human Psychology & Focal Point: Extreme lighting contrast—shivering Bob illuminated by a warm flashlight cone in a frozen -100°F void.
- Text: Instant 2-word cognitive hook: 'NO SUN.' in pure crisp white with soft elevation shadow.
"""

import math
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

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


def draw_clean_text(draw, cx: int, cy: int, text: str, font, fill=(255, 255, 255), shadow_color=(0, 0, 0, 160), shadow_offset=(0, 6)):
    """Draws pure, modern, minimalist typography with soft drop shadow.

    NO border outlines, NO background boxes. Just crisp studio typography.
    """
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    draw_x = cx - (x0 + x1) / 2.0
    draw_y = cy - (y0 + y1) / 2.0

    # Soft elevation shadow for readability across any backdrop
    if shadow_color:
        sx, sy = shadow_offset
        draw.text((draw_x + sx, draw_y + sy), text, font=font, fill=shadow_color)

    # Crisp primary text
    draw.text((draw_x, draw_y), text, font=font, fill=fill)


def draw_left_clean_text(draw, left_x: int, top_y: int, text: str, font, fill=(255, 255, 255), shadow_color=(0, 0, 0, 180), shadow_offset=(0, 6)):
    """Draws left-aligned clean text without boxes or outlines."""
    if shadow_color:
        sx, sy = shadow_offset
        draw.text((left_x + sx, top_y + sy), text, font=font, fill=shadow_color)
    draw.text((left_x, top_y), text, font=font, fill=fill)


def create_netflix_sun_thumbnail():
    # 1. Base Canvas - Deep Cinematic Space Gradient (Dark Navy into Pitch Black)
    base = Image.new("RGB", (WIDTH, HEIGHT), (6, 9, 18))
    draw_base = ImageDraw.Draw(base)

    # Subtle radial nebula glow on the top-right where the dying sun is
    for r in range(600, 0, -15):
        alpha = int((1.0 - (r / 600.0)) * 40)
        draw_base.ellipse([WIDTH * 0.75 - r, HEIGHT * 0.35 - r, WIDTH * 0.75 + r, HEIGHT * 0.35 + r], fill=(20, 35, 75))

    # Distant pinpoint stars
    np.random.seed(1337)
    for _ in range(120):
        sx = np.random.randint(0, WIDTH)
        sy = np.random.randint(0, HEIGHT * 0.75)
        bright = np.random.randint(100, 240)
        size = np.random.choice([1, 2, 2, 3])
        draw_base.ellipse([sx, sy, sx + size, sy + size], fill=(bright, bright, bright))

    # 2. Frozen Earth Horizon Curve at Bottom
    earth_y = HEIGHT + 900
    earth_r = 1450
    draw_base.ellipse([WIDTH // 2 - earth_r, earth_y - earth_r, WIDTH // 2 + earth_r, earth_y + earth_r], fill=(12, 17, 32))
    # Glowing icy blue atmospheric limb
    draw_base.arc([WIDTH // 2 - earth_r, earth_y - earth_r, WIDTH // 2 + earth_r, earth_y + earth_r], start=210, end=330, fill=(74, 144, 226), width=6)
    draw_base.arc([WIDTH // 2 - earth_r, earth_y - earth_r, WIDTH // 2 + earth_r, earth_y + earth_r], start=210, end=330, fill=(116, 185, 255), width=2)

    # 3. The Extinguished Sun (Top Right)
    sun_x, sun_y = int(WIDTH * 0.74), int(HEIGHT * 0.32)
    sun_r = 160

    # Dying faint coronal ember ring (pale solar flare ghost)
    for cr in range(sun_r + 40, sun_r, -4):
        draw_base.ellipse([sun_x - cr, sun_y - cr, sun_x + cr, sun_y + cr], outline=(255, 120, 60), width=2)

    # Pitch black cold core of the vanished sun
    draw_base.ellipse([sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r], fill=(3, 4, 8), outline=(255, 90, 40), width=4)

    # Dramatic "OFF" indicator: A minimalist subtle glowing red power icon inside the dead sun
    draw_base.arc([sun_x - 45, sun_y - 45, sun_x + 45, sun_y + 45], start=120, end=420, fill=(235, 77, 75), width=8)
    draw_base.line([(sun_x, sun_y - 65), (sun_x, sun_y - 15)], fill=(235, 77, 75), width=8)

    # 4. Flashlight Beam Cutting Through the Freezing Darkness
    # Bob is on the left-center, aiming his flashlight across to the right
    bob_x, bob_y = int(WIDTH * 0.32), int(HEIGHT * 0.62)
    flash_x, flash_y = bob_x + 95, bob_y + 40

    # Flashlight warm glowing light cone
    light_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_light = ImageDraw.Draw(light_layer)

    cone_poly = [
        (flash_x, flash_y),
        (WIDTH + 200, HEIGHT * 0.05),
        (WIDTH + 200, HEIGHT * 0.85)
    ]
    draw_light.polygon(cone_poly, fill=(255, 235, 150, 45))

    # Inner bright core beam
    core_poly = [
        (flash_x, flash_y),
        (WIDTH + 200, HEIGHT * 0.25),
        (WIDTH + 200, HEIGHT * 0.65)
    ]
    draw_light.polygon(core_poly, fill=(255, 250, 210, 65))

    # Composite light beam with blur
    light_layer = light_layer.filter(ImageFilter.GaussianBlur(radius=14))
    base.paste(light_layer, (0, 0), light_layer)

    # 5. Bob (Shivering, Cold Winter Scarf, Flashlight)
    draw = ImageDraw.Draw(base, "RGBA")

    # Hoodie & Winter Scarf
    draw.rounded_rectangle([bob_x - 70, bob_y + 60, bob_x + 70, bob_y + 230], radius=28, fill=(0, 206, 201), outline=(20, 25, 40), width=4)
    # Cozy thick red knit winter scarf wrapped around neck
    draw.rounded_rectangle([bob_x - 85, bob_y + 35, bob_x + 85, bob_y + 90], radius=16, fill=(231, 76, 60), outline=(20, 25, 40), width=4)
    draw.rounded_rectangle([bob_x + 20, bob_y + 80, bob_x + 65, bob_y + 170], radius=10, fill=(231, 76, 60), outline=(20, 25, 40), width=3)

    # Bob's Head (Peach skin, slightly cold-tinted)
    r = 95
    draw.ellipse([bob_x - r, bob_y - r, bob_x + r, bob_y + r], fill=(255, 220, 195), outline=(20, 25, 40), width=4)

    # Winter Ear Muffs (fluffy blue muffs on sides of head)
    draw.arc([bob_x - r - 5, bob_y - r - 5, bob_x + r + 5, bob_y], start=180, end=360, fill=(52, 152, 219), width=10)
    draw.ellipse([bob_x - r - 15, bob_y - 25, bob_x - r + 20, bob_y + 35], fill=(52, 152, 219), outline=(20, 25, 40), width=4)
    draw.ellipse([bob_x + r - 20, bob_y - 25, bob_x + r + 15, bob_y + 35], fill=(52, 152, 219), outline=(20, 25, 40), width=4)

    # Hair tufts sticking out of ear muffs
    draw.polygon([(bob_x - 40, bob_y - r - 5), (bob_x - 20, bob_y - r - 35), (bob_x, bob_y - r - 5)], fill=(75, 45, 25))
    draw.polygon([(bob_x + 5, bob_y - r - 5), (bob_x + 30, bob_y - r - 40), (bob_x + 50, bob_y - r - 5)], fill=(75, 45, 25))

    # Shivering Frozen Expressions
    # Huge shocked, shivering white eyes
    draw.ellipse([bob_x - 55, bob_y - 28, bob_x - 8, by_eye := bob_y + 22], fill=(255, 255, 255), outline=(20, 25, 40), width=4)
    draw.ellipse([bob_x + 8, bob_y - 28, bob_x + 55, by_eye], fill=(255, 255, 255), outline=(20, 25, 40), width=4)
    # Tiny shivering pupils
    draw.ellipse([bob_x - 34, bob_y - 8, bob_x - 26, bob_y], fill=(20, 25, 40))
    draw.ellipse([bob_x + 26, bob_y - 8, bob_x + 34, bob_y], fill=(20, 25, 40))

    # Chattering, wavy teeth mouth (freezing cold)
    draw.rounded_rectangle([bob_x - 30, bob_y + 25, bob_x + 30, bob_y + 55], radius=6, fill=(255, 255, 255), outline=(20, 25, 40), width=3)
    for tx in range(bob_x - 20, bob_x + 25, 10):
        draw.line([(tx, bob_y + 26), (tx, bob_y + 54)], fill=(20, 25, 40), width=2)
    draw.line([(bob_x - 28, bob_y + 40), (bob_x + 28, bob_y + 40)], fill=(20, 25, 40), width=2)

    # Pale frozen blue blush on cheeks
    draw.ellipse([bob_x - 65, bob_y + 20, bob_x - 40, bob_y + 42], fill=(160, 220, 255, 180))
    draw.ellipse([bob_x + 40, bob_y + 20, bob_x + 65, bob_y + 42], fill=(160, 220, 255, 180))

    # Ice icicles hanging from chin & ears
    for ix in [bob_x - 20, bob_x + 5, bob_x + 25]:
        draw.polygon([(ix, bob_y + 55), (ix + 6, bob_y + 55), (ix + 3, bob_y + 80)], fill=(200, 235, 255))

    # Flashlight in hand
    draw.rounded_rectangle([flash_x - 45, flash_y - 14, flash_x + 10, flash_y + 14], radius=6, fill=(254, 202, 87), outline=(20, 25, 40), width=3)
    draw.polygon([(flash_x + 10, flash_y - 20), (flash_x + 25, flash_y - 28), (flash_x + 25, flash_y + 28), (flash_x + 10, flash_y + 20)], fill=(225, 177, 44), outline=(20, 25, 40))
    # Glowing lens
    draw.ellipse([flash_x + 20, flash_y - 28, flash_x + 30, flash_y + 28], fill=(255, 255, 255))

    # 6. MINIMALIST NETFLIX-LEVEL TYPOGRAPHY
    # NO boxes, NO borders around letters. Pure bold high-impact text with soft drop shadow.
    title_font = get_font(size=130, font_type="impact")
    sub_font = get_font(size=56, font_type="rounded")
    badge_font = get_font(size=44, font_type="futura")

    # Primary Hook: 'NO SUN.' (Instant 2-word cognitive hook)
    draw_left_clean_text(
        draw,
        left_x=120,
        top_y=110,
        text="NO SUN.",
        font=title_font,
        fill=(255, 255, 255),
        shadow_color=(0, 0, 0, 220),
        shadow_offset=(4, 8)
    )

    # Sub-Hook: 'WHAT HAPPENS IN 7 DAYS?'
    draw_left_clean_text(
        draw,
        left_x=125,
        top_y=255,
        text="WHAT HAPPENS IN 7 DAYS?",
        font=sub_font,
        fill=(254, 202, 87),
        shadow_color=(0, 0, 0, 200),
        shadow_offset=(3, 5)
    )

    # Telemetry Stat at bottom left: '-100°F GLOBAL FREEZE'
    draw_left_clean_text(
        draw,
        left_x=125,
        top_y=HEIGHT - 130,
        text="-100°F GLOBAL FREEZE",
        font=badge_font,
        fill=(116, 185, 255),
        shadow_color=(0, 0, 0, 220),
        shadow_offset=(3, 5)
    )

    # Resize cleanly to 1280x720 Full HD YouTube thumbnail
    thumb_final = base.resize((1280, 720), Image.Resampling.LANCZOS)

    out_jpg = THUMBNAILS_DIR / "Sun_Disappeared_Thumbnail.jpg"
    out_png = THUMBNAILS_DIR / "Sun_Disappeared_Thumbnail.png"

    thumb_final.save(str(out_jpg), "JPEG", quality=95)
    thumb_final.save(str(out_png), "PNG")
    print(f"✅ Generated new clean Netflix-style viral thumbnail: {out_jpg}")
    return str(out_jpg)


if __name__ == "__main__":
    create_netflix_sun_thumbnail()
