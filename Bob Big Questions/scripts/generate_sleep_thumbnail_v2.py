"""High-CTR YouTube Viral Thumbnail Generator for Episode 1: 'What Happens If You Don't Sleep For 7 Days?'

Fixes the text-overlapping bug from the legacy frame-grabber by building a dedicated,
high-retention split-screen composition with bold typography, zero collisions, and maximum visual punch.
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


def draw_studio_pill(draw, cx: int, center_y: int, text: str, font, fill=(255, 71, 87), text_fill=(255, 255, 255), pad_x: int = 45, pad_y: int = 16, radius: int = 24):
    """Draws a modern studio pill badge with true mathematical ink-centering and soft drop shadow."""
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    ink_w = x1 - x0
    ink_h = y1 - y0

    box_w = ink_w + pad_x * 2
    box_h = ink_h + pad_y * 2

    x_left = cx - box_w // 2
    y_top = center_y - box_h // 2
    x_right = cx + box_w // 2
    y_bottom = center_y + box_h // 2

    # Translucent drop shadow
    draw.rounded_rectangle([x_left, y_top + 5, x_right, y_bottom + 5], radius=radius, fill=(15, 15, 25))
    # Main badge
    draw.rounded_rectangle([x_left, y_top, x_right, y_bottom], radius=radius, fill=fill)

    draw_x = cx - (x0 + x1) / 2.0
    draw_y = center_y - (y0 + y1) / 2.0
    draw.text((draw_x, draw_y), text, font=font, fill=text_fill)
    return [x_left, y_top, x_right, y_bottom]


def draw_action_text(draw, cx: int, cy: int, text: str, font, fill=(255, 234, 167), stroke_fill=(30, 20, 20), stroke_width: int = 8):
    """Draws free-floating comic action typography with heavy outline and drop shadow."""
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    draw_x = cx - (x0 + x1) / 2.0
    draw_y = cy - (y0 + y1) / 2.0
    draw.text((draw_x + 5, draw_y + 6), text, font=font, fill=(10, 10, 15, 220), stroke_width=stroke_width + 3, stroke_fill=(10, 10, 15, 220))
    draw.text((draw_x, draw_y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def draw_fresh_bob(draw, cx: int, cy: int):
    """Draws Bob on Day 0: energetic, confident, holding a red coffee mug."""
    bx, by = cx, cy
    r = 95

    # Hoodie
    draw.rounded_rectangle([bx - 70, by + 65, bx + 70, by + 230], radius=28, fill=(0, 206, 201), outline=(35, 30, 30), width=5)
    # Coral pants
    draw.rounded_rectangle([bx - 65, by + 225, bx - 10, by + 300], radius=14, fill=(255, 107, 129), outline=(35, 30, 30), width=4)
    draw.rounded_rectangle([bx + 10, by + 225, bx + 65, by + 300], radius=14, fill=(255, 107, 129), outline=(35, 30, 30), width=4)
    # Head
    draw.ellipse([bx - r, by - r, bx + r, by + r], fill=(255, 224, 189), outline=(35, 30, 30), width=5)
    # Hair
    draw.arc([bx - r - 5, by - r - 5, bx + r + 5, by + 10], start=180, end=360, fill=(75, 45, 25), width=24)
    draw.polygon([(bx - 40, by - r - 5), (bx - 20, by - r - 35), (bx, by - r - 5)], fill=(75, 45, 25))
    draw.polygon([(bx + 5, by - r - 5), (bx + 30, by - r - 40), (bx + 50, by - r - 5)], fill=(75, 45, 25))
    # Energetic confident eyes
    draw.ellipse([bx - 40, by - 14, bx - 14, by + 16], fill=(35, 30, 30))
    draw.ellipse([bx + 14, by - 14, bx + 40, by + 16], fill=(35, 30, 30))
    # Big sparkling catchlight
    draw.ellipse([bx - 36, by - 10, bx - 22, by + 4], fill=(255, 255, 255))
    draw.ellipse([bx + 18, by - 10, bx + 32, by + 4], fill=(255, 255, 255))
    # Big cheerful grin
    draw.chord([bx - 35, by + 18, bx + 35, by + 65], start=0, end=180, fill=(225, 75, 75), outline=(35, 30, 30), width=5)
    # Rosy cheeks
    draw.ellipse([bx - 65, by + 22, bx - 42, by + 40], fill=(255, 140, 140))
    draw.ellipse([bx + 42, by + 22, bx + 65, by + 40], fill=(255, 140, 140))

    # Red Coffee Mug in Hand
    mug_x, mug_y = bx + 90, by + 120
    draw.rounded_rectangle([mug_x, mug_y, mug_x + 60, mug_y + 80], radius=10, fill=(231, 76, 60), outline=(35, 30, 30), width=4)
    # Mug handle
    draw.arc([mug_x + 40, mug_y + 15, mug_x + 85, mug_y + 65], start=270, end=90, fill=(231, 76, 60), width=8)
    # Rising steam waves
    draw.arc([mug_x + 15, mug_y - 35, mug_x + 35, mug_y - 10], start=0, end=180, fill=(255, 255, 255), width=3)
    draw.arc([mug_x + 35, mug_y - 45, mug_x + 55, mug_y - 20], start=0, end=180, fill=(255, 255, 255), width=3)


def draw_sleep_deprived_bob(draw, cx: int, cy: int):
    """Draws Bob on Day 7: complete zombie shock, dark purple eye bags, red veins, toothbrush banana."""
    bx, by = cx, cy
    r = 95

    # Hoodie
    draw.rounded_rectangle([bx - 70, by + 65, bx + 70, by + 230], radius=28, fill=(0, 206, 201), outline=(35, 30, 30), width=5)
    # Coral pants
    draw.rounded_rectangle([bx - 65, by + 225, bx - 10, by + 300], radius=14, fill=(255, 107, 129), outline=(35, 30, 30), width=4)
    draw.rounded_rectangle([bx + 10, by + 225, bx + 65, by + 300], radius=14, fill=(255, 107, 129), outline=(35, 30, 30), width=4)
    # Pale sickly skin
    draw.ellipse([bx - r, by - r, bx + r, by + r], fill=(245, 215, 185), outline=(35, 30, 30), width=5)
    # Disheveled hair sticking out wildly
    draw.arc([bx - r - 5, by - r - 5, bx + r + 5, by + 10], start=180, end=360, fill=(75, 45, 25), width=24)
    draw.polygon([(bx - 55, by - r - 15), (bx - 35, by - r - 45), (bx - 15, by - r - 5)], fill=(75, 45, 25))
    draw.polygon([(bx - 10, by - r - 5), (bx + 15, by - r - 55), (bx + 40, by - r - 10)], fill=(75, 45, 25))
    draw.polygon([(bx + 35, by - r - 5), (bx + 65, by - r - 45), (bx + 85, by - r - 5)], fill=(75, 45, 25))

    # Massive Dark Purple Eye Bags
    draw.ellipse([bx - 58, by - 5, bx - 4, by + 38], fill=(142, 68, 173, 140))
    draw.ellipse([bx + 4, by - 5, bx + 58, by + 38], fill=(142, 68, 173, 140))

    # Massive bloodshot shocked eyes
    draw.ellipse([bx - 55, by - 32, bx - 8, by + 20], fill=(255, 255, 255), outline=(35, 30, 30), width=4)
    draw.ellipse([bx + 8, by - 32, bx + 55, by + 20], fill=(255, 255, 255), outline=(35, 30, 30), width=4)
    # Red bloodshot veins in eyes
    draw.line([(bx - 50, by - 20), (bx - 38, by - 12)], fill=(231, 76, 60), width=2)
    draw.line([(bx - 50, by - 5), (bx - 40, by - 8)], fill=(231, 76, 60), width=2)
    draw.line([(bx + 50, by - 20), (bx + 38, by - 12)], fill=(231, 76, 60), width=2)
    draw.line([(bx + 50, by - 5), (bx + 40, by - 8)], fill=(231, 76, 60), width=2)

    # Pinpoint tiny pupils (sleep delirium)
    draw.ellipse([bx - 34, by - 8, bx - 28, by - 2], fill=(35, 30, 30))
    draw.ellipse([bx + 28, by - 8, bx + 34, by - 2], fill=(35, 30, 30))

    # Trembling wavy mouth
    draw.arc([bx - 30, by + 26, bx + 30, by + 68], start=200, end=340, fill=(35, 30, 30), width=5)

    # Sweat bead flying off head
    draw.ellipse([bx + 68, by - 45, bx + 84, by - 25], fill=(80, 200, 255), outline=(35, 30, 30), width=2)

    # Holding a yellow banana as if it's a toothbrush
    ban_x, ban_y = bx - 100, by + 110
    draw.arc([ban_x - 30, ban_y - 40, ban_x + 50, ban_y + 40], start=45, end=180, fill=(241, 196, 15), width=16)
    # White toothpaste foam on tip of banana
    draw.ellipse([ban_x + 20, ban_y - 25, ban_x + 45, ban_y], fill=(255, 255, 255), outline=(35, 30, 30), width=2)


def generate_sleep_thumbnail():
    """Generates a world-class high-CTR YouTube thumbnail with zero text collisions."""
    thumb_img = Image.new("RGB", (WIDTH, HEIGHT), (20, 25, 45))
    draw = ImageDraw.Draw(thumb_img)
    cx, cy = WIDTH // 2, HEIGHT // 2

    # 1. SPLIT-SCREEN BACKGROUND
    # Left side: Day 0 - Fresh, vibrant sunny daylight room
    draw.rectangle([0, 0, WIDTH // 2, HEIGHT], fill=(130, 204, 221))
    draw.rectangle([0, HEIGHT * 0.65, WIDTH // 2, HEIGHT], fill=(245, 222, 179))
    # Warm sunshine rays in background
    for ang in range(0, 90, 15):
        rad = math.radians(ang)
        draw.line([(0, 0), (int(math.cos(rad) * 1200), int(math.sin(rad) * 1200))], fill=(255, 240, 180, 60), width=18)

    # Right side: Day 7 - Dark purple insomnia delirium bedroom
    draw.rectangle([WIDTH // 2, 0, WIDTH, HEIGHT], fill=(24, 20, 48))
    draw.rectangle([WIDTH // 2, HEIGHT * 0.65, WIDTH, HEIGHT], fill=(15, 12, 30))
    # Glowing digital bedside clock showing 3:00 AM
    clock_x = WIDTH - 260
    draw.rounded_rectangle([clock_x, HEIGHT * 0.45, clock_x + 180, HEIGHT * 0.58], radius=16, fill=(10, 10, 20), outline=(231, 76, 60), width=4)
    clock_font = get_font(size=44, font_type="impact")
    draw.text((clock_x + 22, HEIGHT * 0.48), "3:00 AM", font=clock_font, fill=(231, 76, 60))

    # Center split neon lightning divider
    draw.line([(WIDTH // 2, 0), (WIDTH // 2, HEIGHT)], fill=(255, 234, 167), width=12)

    # 2. CHARACTERS ON BOTH SIDES
    # Left: Energetic Bob (Day 0)
    draw_fresh_bob(draw, WIDTH * 0.25, HEIGHT * 0.50)

    # Right: Hallucinating Insomniac Bob (Day 7)
    draw_sleep_deprived_bob(draw, WIDTH * 0.75, HEIGHT * 0.50)

    # 3. SIDE PILL BADGES (DAY 0 vs DAY 7)
    sub_pill_font = get_font(size=42, font_type="rounded")
    draw_studio_pill(draw, int(WIDTH * 0.25), HEIGHT * 0.24, "DAY 0: FRESH & WIRED", sub_pill_font, fill=(46, 204, 113), text_fill=(255, 255, 255), pad_x=35, pad_y=12)
    draw_studio_pill(draw, int(WIDTH * 0.75), HEIGHT * 0.24, "DAY 7: BRAIN SHUTDOWN!", sub_pill_font, fill=(231, 76, 60), text_fill=(255, 255, 255), pad_x=35, pad_y=12)

    # 4. GIANT VIRAL TITLE AT TOP (ONE SINGLE TEXT, PERFECTLY CENTERED, ZERO OVERLAPS)
    title_font = get_font(size=90, font_type="impact")
    draw_action_text(draw, cx, 88, "WHAT IF YOU NEVER SLEPT?!", title_font, fill=(255, 240, 80), stroke_fill=(30, 20, 20), stroke_width=16)

    # 5. BOTTOM STUDIO HOOK PILL
    hook_font = get_font(size=48, font_type="rounded")
    draw_studio_pill(draw, cx, HEIGHT - 95, "7 DAYS AWAKE: THE FULL BRAIN REBELLION!", hook_font, fill=(255, 71, 87), text_fill=(255, 255, 255), pad_x=45, pad_y=16)

    # Resize cleanly to 1280x720 Full HD YouTube thumbnail
    thumb_final = thumb_img.resize((1280, 720), Image.Resampling.LANCZOS)

    out_jpg = THUMBNAILS_DIR / "Cartoon_Sleep_Thumbnail.jpg"
    out_png = THUMBNAILS_DIR / "Cartoon_Sleep_Thumbnail.png"

    thumb_final.save(str(out_jpg), "JPEG", quality=95)
    thumb_final.save(str(out_png), "PNG")
    print(f"✅ Generated new clean viral thumbnail: {out_jpg}")
    return str(out_jpg)


if __name__ == "__main__":
    generate_sleep_thumbnail()
