"""Procedural 2D Animated Cartoon: 'What Happens If Everyone On Earth Jumped At The Same Second?'

Bob Big Questions - Episode 4 (Flagship 2m 15s Special):
- Exact Runtime: 2 minutes 15 seconds (134.99s / 4,050 frames @ 30fps)
- Signature Beloved Channel 1 Vector Visual Style:
    * Clean mathematical curves, vibrant cartoon gradients, and rich procedural vector art.
    * Character: Bob (sitting, jumping, shock, convertible car, flamingo paddling, eating pancakes).
    * True Ink-Centered Studio Pill Badges & Free-Floating Comic Typography.
    * Dynamic Screen Rumbles, Sonic Boom Shockwaves, Atom Scale HUD, and Golden Rays.
- Hardware-Accelerated Apple Silicon VideoToolbox H.264 at 1080p Full HD.
"""

import math
import os
import sys
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
ROOT_DIR = BASE_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.hardware import detect_hardware, get_ffmpeg_binary, get_video_info
from utils.logger import logger
from voice.audio_processor import get_audio_duration

WIDTH, HEIGHT = 1920, 1080
FPS = 30

EXPORTS_DIR = BASE_DIR / "exports" / "videos"
THUMBNAILS_DIR = BASE_DIR / "exports" / "thumbnails"
AUDIO_DIR = BASE_DIR / "audio" / "jump_135s"

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


def draw_studio_pill(draw, cx: int, center_y: int, text: str, font, fill=(255, 71, 87), text_fill=(255, 255, 255), pad_x: int = 38, pad_y: int = 14, radius: int = 22):
    """Draws a modern studio pill badge with mathematical ink-centering and soft drop shadow."""
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    ink_w = x1 - x0
    ink_h = y1 - y0

    box_w = ink_w + pad_x * 2
    box_h = ink_h + pad_y * 2

    x_left = cx - box_w // 2
    y_top = center_y - box_h // 2
    x_right = cx + box_w // 2
    y_bottom = center_y + box_h // 2

    # Drop shadow
    draw.rounded_rectangle([x_left, y_top + 4, x_right, y_bottom + 4], radius=radius, fill=(20, 20, 30))
    # Main badge
    draw.rounded_rectangle([x_left, y_top, x_right, y_bottom], radius=radius, fill=fill)

    draw_x = cx - (x0 + x1) / 2.0
    draw_y = center_y - (y0 + y1) / 2.0
    draw.text((draw_x, draw_y), text, font=font, fill=text_fill)
    return [x_left, y_top, x_right, y_bottom]


def draw_action_text(draw, cx: int, cy: int, text: str, font, fill=(255, 234, 167), stroke_fill=(40, 20, 20), stroke_width: int = 6):
    """Draws floating comic action typography with heavy outline and drop shadow."""
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    draw_x = cx - (x0 + x1) / 2.0
    draw_y = cy - (y0 + y1) / 2.0
    draw.text((draw_x + 4, draw_y + 5), text, font=font, fill=(10, 10, 15, 200), stroke_width=stroke_width + 2, stroke_fill=(10, 10, 15, 200))
    draw.text((draw_x, draw_y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def draw_vector_bell(draw, cx: int, cy: int, r: int = 24, fill=(254, 202, 87)):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r - 5], fill=fill, outline=(40, 30, 30), width=4)
    draw.chord([cx - r - 8, cy + 5, cx + r + 8, cy + 28], start=180, end=360, fill=fill, outline=(40, 30, 30), width=4)
    draw.ellipse([cx - 8, cy + 22, cx + 8, cy + 34], fill=(225, 177, 44), outline=(40, 30, 30), width=3)


def draw_vector_thumbs_up(draw, cx: int, cy: int, size: int = 24, fill=(255, 255, 255)):
    draw.rounded_rectangle([cx - size, cy - size // 2, cx + size // 2, cy + size], radius=8, fill=fill)
    draw.rounded_rectangle([cx - size, cy - size * 1.2, cx - size // 3, cy], radius=6, fill=fill)


def draw_bob(draw, cx: int, cy: int, mood="happy", t_sec: float = 0.0, pose="standing"):
    """Draws Bob in Channel 1's beloved procedural vector style."""
    bx, by = cx, cy
    radius = 85

    # 1. Clothing & Body
    if pose == "standing":
        # Teal hoodie
        draw.rounded_rectangle([bx - 65, by + 55, bx + 65, by + 210], radius=26, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
        # Pink pants
        draw.rounded_rectangle([bx - 60, by + 205, bx - 10, by + 285], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx + 10, by + 205, bx + 60, by + 285], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        # Yellow sneakers
        draw.rounded_rectangle([bx - 75, by + 275, bx - 5, by + 305], radius=10, fill=(254, 202, 87), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx + 5, by + 275, bx + 75, by + 305], radius=10, fill=(254, 202, 87), outline=(40, 30, 30), width=4)

    elif pose == "jumping":
        # In air with tucked knees
        draw.rounded_rectangle([bx - 65, by + 45, bx + 65, by + 190], radius=26, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
        # Tucked legs
        draw.rounded_rectangle([bx - 75, by + 175, bx - 15, by + 245], radius=16, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx + 15, by + 175, bx + 75, by + 245], radius=16, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx - 85, by + 235, bx - 20, by + 265], radius=10, fill=(254, 202, 87), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx + 20, by + 235, bx + 85, by + 265], radius=10, fill=(254, 202, 87), outline=(40, 30, 30), width=4)
        # Arms raised in excitement!
        draw.line([(bx - 55, by + 70), (bx - 105, by - 20)], fill=(0, 206, 201), width=18)
        draw.line([(bx + 55, by + 70), (bx + 105, by - 20)], fill=(0, 206, 201), width=18)

    elif pose == "sitting":
        draw.rounded_rectangle([bx - 65, by + 55, bx + 65, by + 200], radius=26, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
        draw.rounded_rectangle([bx - 60, by + 195, bx + 60, by + 265], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)

    # 2. Head
    draw.ellipse([bx - radius, by - radius, bx + radius, by + radius], fill=(255, 224, 189), outline=(40, 30, 30), width=5)

    # 3. Messy Cartoon Hair
    draw.arc([bx - radius - 5, by - radius - 5, bx + radius + 5, by + 10], start=180, end=360, fill=(75, 45, 25), width=24)
    # Hair tufts
    draw.polygon([(bx - 40, by - radius - 5), (bx - 20, by - radius - 35), (bx, by - radius - 5)], fill=(75, 45, 25))
    draw.polygon([(bx + 5, by - radius - 5), (bx + 30, by - radius - 40), (bx + 50, by - radius - 5)], fill=(75, 45, 25))

    # 4. Expressions
    if mood == "happy":
        draw.ellipse([bx - 36, by - 12, bx - 14, by + 14], fill=(35, 30, 30))
        draw.ellipse([bx + 14, by - 12, bx + 36, by + 14], fill=(35, 30, 30))
        # Catchlight
        draw.ellipse([bx - 32, by - 8, bx - 22, by + 2], fill=(255, 255, 255))
        draw.ellipse([bx + 18, by - 8, bx + 28, by + 2], fill=(255, 255, 255))
        # Cheerful smile
        draw.arc([bx - 32, by + 12, bx + 32, by + 52], start=15, end=165, fill=(35, 30, 30), width=5)
        # Rosy cheeks
        draw.ellipse([bx - 58, by + 18, bx - 38, by + 34], fill=(255, 150, 150, 180))
        draw.ellipse([bx + 38, by + 18, bx + 58, by + 34], fill=(255, 150, 150, 180))

    elif mood == "shocked":
        # Massive wide eyes
        draw.ellipse([bx - 50, by - 30, bx - 10, by + 20], fill=(255, 255, 255), outline=(35, 30, 30), width=4)
        draw.ellipse([bx + 10, by - 30, bx + 50, by + 20], fill=(255, 255, 255), outline=(35, 30, 30), width=4)
        # Tiny shocked dot pupils
        draw.ellipse([bx - 33, by - 8, bx - 27, by - 2], fill=(35, 30, 30))
        draw.ellipse([bx + 27, by - 8, bx + 33, by - 2], fill=(35, 30, 30))
        # Screaming O mouth
        draw.ellipse([bx - 22, by + 24, bx + 22, by + 68], fill=(180, 40, 50), outline=(35, 30, 30), width=4)
        # Floating sweat bead
        draw.ellipse([bx + 55, by - 45, bx + 70, by - 25], fill=(80, 200, 255), outline=(35, 30, 30), width=3)

    elif mood == "cheering":
        # Starry eyes
        draw.ellipse([bx - 38, by - 14, bx - 12, by + 12], fill=(255, 215, 0), outline=(35, 30, 30), width=4)
        draw.ellipse([bx + 12, by - 14, bx + 38, by + 12], fill=(255, 215, 0), outline=(35, 30, 30), width=4)
        # Big open laughing mouth
        draw.chord([bx - 35, by + 15, bx + 35, by + 58], start=0, end=180, fill=(220, 60, 60), outline=(35, 30, 30), width=4)


def draw_crowd(draw, base_y: int, count: int = 14, jump_offset: float = 0.0):
    """Draws a colorful procedural crowd of cute friends shoulder-to-shoulder."""
    shirt_colors = [
        (255, 107, 129), (0, 206, 201), (254, 202, 87), (108, 92, 231),
        (255, 159, 67), (46, 204, 113), (52, 152, 219), (231, 76, 60)
    ]
    spacing = WIDTH // (count + 1)
    for i in range(count):
        cx = spacing * (i + 1) + ((i % 3) - 1) * 20
        cy = base_y - int(jump_offset)
        color = shirt_colors[i % len(shirt_colors)]

        # Body
        draw.rounded_rectangle([cx - 28, cy - 35, cx + 28, cy + 65], radius=14, fill=color, outline=(40, 30, 30), width=3)
        # Head
        draw.ellipse([cx - 24, cy - 80, cx + 24, cy - 32], fill=(255, 224, 189), outline=(40, 30, 30), width=3)
        # Hair
        draw.arc([cx - 26, cy - 82, cx + 26, cy - 50], start=180, end=360, fill=(60, 40, 25), width=8)
        # Dot eyes & smile
        draw.ellipse([cx - 10, cy - 60, cx - 4, cy - 54], fill=(30, 30, 30))
        draw.ellipse([cx + 4, cy - 60, cx + 10, cy - 54], fill=(30, 30, 30))
        draw.arc([cx - 8, cy - 50, cx + 8, cy - 40], start=0, end=180, fill=(30, 30, 30), width=2)


def render_jump_frame(frame_idx, total_frames, t_sec, title_font, banner_font, sub_font, giant_font):
    """Renders a single Full HD frame with Channel 1 vector storytelling."""
    frame = Image.new("RGB", (WIDTH, HEIGHT), (240, 245, 250))
    draw = ImageDraw.Draw(frame)

    cx, cy = WIDTH // 2, HEIGHT // 2
    idle_bob = math.sin(t_sec * 6.0) * 5.0
    shake_x, shake_y = 0, 0

    # =========================================================================
    # SCENE 1: 0.0s - 16.5s (The 8 Billion Calendar Invite)
    # =========================================================================
    if t_sec < 16.5:
        # Sunny cyan-blue sky with rolling green hill
        draw.rectangle([0, 0, WIDTH, HEIGHT * 0.65], fill=(130, 204, 255))
        # Sun in corner
        draw.ellipse([WIDTH - 240, -40, WIDTH + 60, 260], fill=(254, 202, 87))
        # Rolling green meadow
        draw.chord([-200, HEIGHT * 0.50, WIDTH + 200, HEIGHT * 1.3], start=180, end=360, fill=(106, 176, 76))

        # Bob in center holding giant smartphone
        bob_x = int(WIDTH * 0.40)
        bob_y = int(HEIGHT * 0.62 + idle_bob)
        draw_bob(draw, bob_x, bob_y, mood="happy", t_sec=t_sec, pose="standing")

        # Giant calendar smartphone next to Bob
        phone_x, phone_y = bob_x + 220, bob_y - 20
        draw.rounded_rectangle([phone_x - 110, phone_y - 180, phone_x + 110, phone_y + 180], radius=24, fill=(44, 62, 80), outline=(20, 20, 30), width=6)
        draw.rounded_rectangle([phone_x - 95, phone_y - 150, phone_x + 95, phone_y + 155], radius=14, fill=(255, 255, 255))
        # Calendar header
        draw.rectangle([phone_x - 95, phone_y - 150, phone_x + 95, phone_y - 80], fill=(255, 71, 87))
        draw_action_text(draw, phone_x, phone_y - 115, "GLOBAL JUMP", banner_font, fill=(255, 255, 255), stroke_fill=(180, 20, 30), stroke_width=4)
        draw_action_text(draw, phone_x, phone_y - 20, "8,000,000,000", title_font, fill=(44, 62, 80), stroke_fill=(255, 255, 255), stroke_width=2)
        draw_action_text(draw, phone_x, phone_y + 40, "GOING!", banner_font, fill=(46, 204, 113), stroke_fill=(30, 80, 40), stroke_width=3)

        # Background crowd gathering
        draw_crowd(draw, int(HEIGHT * 0.72), count=10, jump_offset=0)

        # Header Studio Badge
        draw_studio_pill(draw, cx, 80, "WHAT IF EVERYONE JUMPED AT ONCE?", title_font, fill=(9, 132, 227), text_fill=(255, 255, 255), pad_x=45, pad_y=16)
        draw_studio_pill(draw, cx, HEIGHT - 75, "SCENE 1: THE 8-BILLION-PERSON CALENDAR INVITE", banner_font, fill=(46, 204, 113), text_fill=(255, 255, 255))

    # =========================================================================
    # SCENE 2: 16.5s - 36.5s (The Countdown & 3, 2, 1... JUMP!)
    # =========================================================================
    elif t_sec < 36.5:
        s2_t = t_sec - 16.5
        # Rhode Island stadium field view
        draw.rectangle([0, 0, WIDTH, HEIGHT * 0.60], fill=(130, 204, 255))
        draw.rectangle([0, HEIGHT * 0.60, WIDTH, HEIGHT], fill=(120, 224, 143))

        # Stadium lights & bunting
        draw.line([(0, 160), (WIDTH, 160)], fill=(80, 80, 90), width=4)

        if s2_t < 14.0:
            # Bob on wooden stage counting down with golden megaphone
            stage_y = int(HEIGHT * 0.58)
            draw.rounded_rectangle([cx - 240, stage_y, cx + 240, stage_y + 120], radius=16, fill=(139, 69, 19), outline=(40, 20, 10), width=5)

            # Bob holding golden megaphone
            bob_y = stage_y - 120 + int(idle_bob)
            draw_bob(draw, cx, bob_y, mood="cheering", t_sec=t_sec, pose="standing")

            # Megaphone
            mega_x, mega_y = cx + 80, bob_y + 30
            draw.polygon([(mega_x, mega_y), (mega_x + 90, mega_y - 45), (mega_x + 90, mega_y + 45)], fill=(254, 202, 87), outline=(40, 30, 30), width=4)
            draw.ellipse([mega_x + 80, mega_y - 45, mega_x + 100, mega_y + 45], fill=(240, 180, 50), outline=(40, 30, 30), width=3)

            # Countdown text pops at 20s, 24s, 28s
            if s2_t > 9.0:
                draw_action_text(draw, cx, 190, "3... 2... 1...", giant_font, fill=(255, 71, 87), stroke_fill=(30, 20, 20), stroke_width=10)
            elif s2_t > 5.0:
                draw_action_text(draw, cx, 190, "RHODE ISLAND: 8 BILLION HUMANS ASSEMBLED!", banner_font, fill=(255, 234, 167), stroke_fill=(40, 30, 20), stroke_width=6)

            # Crowd on ground
            draw_crowd(draw, int(HEIGHT * 0.82), count=16, jump_offset=0)
        else:
            # 30.5s - 36.5s: THE JUMP! Everyone in the air!
            jump_h = math.sin((s2_t - 14.0) / 6.0 * math.pi) * 220.0
            # Bob jumping high
            bob_y = int(HEIGHT * 0.52 - jump_h)
            draw_bob(draw, cx, bob_y, mood="cheering", t_sec=t_sec, pose="jumping")

            # Entire crowd floating in the air!
            draw_crowd(draw, int(HEIGHT * 0.82), count=16, jump_offset=jump_h * 0.75)

            # Wind speed lines below feet
            for i in range(12):
                wx = int(WIDTH * 0.08 * i + 80)
                draw.line([(wx, HEIGHT * 0.85), (wx, HEIGHT * 0.85 - 50)], fill=(255, 255, 255, 200), width=5)

            draw_action_text(draw, cx, 190, "JUMP!! 30 CENTIMETERS IN THE AIR!", giant_font, fill=(254, 202, 87), stroke_fill=(30, 20, 20), stroke_width=10)

        draw_studio_pill(draw, cx, 80, "WHAT IF EVERYONE JUMPED AT ONCE?", title_font, fill=(9, 132, 227), text_fill=(255, 255, 255), pad_x=45, pad_y=16)
        draw_studio_pill(draw, cx, HEIGHT - 75, "SCENE 2: THE 8-BILLION-PERSON SYNCHRONIZED JUMP", banner_font, fill=(255, 107, 129), text_fill=(255, 255, 255))

    # =========================================================================
    # SCENE 3: 36.5s - 55.5s (The Great Impact & Sonic Shockwave)
    # =========================================================================
    elif t_sec < 55.5:
        s3_t = t_sec - 36.5

        # Ground impact scene
        draw.rectangle([0, 0, WIDTH, HEIGHT * 0.55], fill=(225, 112, 85))  # Sunset shockwave sky
        draw.rectangle([0, HEIGHT * 0.55, WIDTH, HEIGHT], fill=(99, 110, 114))  # Cracking ground

        # Expanding radial sonic shockwaves
        for r_ring in [150, 320, 520, 750, 980]:
            ring_r = int((r_ring + s3_t * 240) % 1100)
            draw.ellipse([cx - ring_r, HEIGHT * 0.65 - ring_r // 3, cx + ring_r, HEIGHT * 0.65 + ring_r // 3], outline=(255, 234, 167), width=6)

        # Violent camera rumble on impact (first 4 seconds)
        if s3_t < 4.0:
            decay = max(0.0, 1.0 - s3_t / 4.0)
            shake_x = int(math.sin(t_sec * 60.0) * 24.0 * decay)
            shake_y = int(math.cos(t_sec * 52.0) * 20.0 * decay)

        # Bob in center holding ears in shock
        bob_y = int(HEIGHT * 0.58)
        draw_bob(draw, cx, bob_y, mood="shocked", t_sec=t_sec, pose="standing")

        # Sonic boom decibel badge
        draw_action_text(draw, cx, 200, "KABOOOM!!", giant_font, fill=(255, 71, 87), stroke_fill=(30, 20, 20), stroke_width=12)
        draw_action_text(draw, cx, 290, "200 DECIBELS! LOUDER THAN A ROCKET LAUNCH!", banner_font, fill=(254, 202, 87), stroke_fill=(40, 20, 10), stroke_width=6)

        draw_crowd(draw, int(HEIGHT * 0.78), count=16, jump_offset=0)

        draw_studio_pill(draw, cx, 80, "WHAT IF EVERYONE JUMPED AT ONCE?", title_font, fill=(9, 132, 227), text_fill=(255, 255, 255), pad_x=45, pad_y=16)
        draw_studio_pill(draw, cx, HEIGHT - 75, "SCENE 3: THE SNEAKER SLAP HEARD AROUND THE WORLD", banner_font, fill=(214, 48, 49), text_fill=(255, 255, 255))

    # =========================================================================
    # SCENE 4: 55.5s - 78.5s (The 6 Sextillion Ton Secret & Atom Shift)
    # =========================================================================
    elif t_sec < 78.5:
        s4_t = t_sec - 55.5
        # Deep space background with twinkling stars
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(15, 18, 30))
        for sx, sy in [(120, 140), (340, 280), (600, 120), (950, 180), (1400, 120), (1680, 220), (1800, 90), (250, 680), (1700, 720)]:
            draw.ellipse([sx, sy, sx + 5, sy + 5], fill=(255, 255, 255))

        # Planet Earth in center (Diameter 460px)
        earth_r = 230
        earth_x = int(WIDTH * 0.38)
        earth_y = cy + int(math.sin(t_sec * 3.0) * 6.0)

        # Atmosphere glow
        draw.ellipse([earth_x - earth_r - 18, earth_y - earth_r - 18, earth_x + earth_r + 18, earth_y + earth_r + 18], fill=(0, 168, 255, 50))
        # Blue ocean
        draw.ellipse([earth_x - earth_r, earth_y - earth_r, earth_x + earth_r, earth_y + earth_r], fill=(9, 132, 227), outline=(40, 30, 30), width=6)
        # Continents
        draw.ellipse([earth_x - 140, earth_y - 120, earth_x + 20, earth_y + 40], fill=(46, 204, 113))
        draw.ellipse([earth_x + 40, earth_y - 60, earth_x + 160, earth_y + 90], fill=(46, 204, 113))
        draw.ellipse([earth_x - 80, earth_y + 60, earth_x + 60, earth_y + 160], fill=(46, 204, 113))

        # Scientific HUD Info Card on Right
        hud_x = int(WIDTH * 0.74)
        hud_w, hud_h = 440, 380
        draw.rounded_rectangle([hud_x - hud_w // 2, cy - hud_h // 2, hud_x + hud_w // 2, cy + hud_h // 2], radius=20, fill=(30, 39, 46), outline=(0, 206, 201), width=4)

        draw_action_text(draw, hud_x, cy - 130, "EARTH MASS:", banner_font, fill=(255, 234, 167), stroke_fill=(10, 10, 10), stroke_width=4)
        draw_action_text(draw, hud_x, cy - 80, "6 SEXTILLION TONS", title_font, fill=(255, 71, 87), stroke_fill=(30, 10, 10), stroke_width=4)
        draw_action_text(draw, hud_x, cy - 30, "(6,000,000,000,000,000,000,000 kg)", sub_font, fill=(180, 200, 220), stroke_fill=(10, 10, 10), stroke_width=2)

        draw.line([(hud_x - 180, cy + 15), (hud_x + 180, cy + 15)], fill=(100, 110, 120), width=2)
        draw_action_text(draw, hud_x, cy + 50, "EARTH DISPLACEMENT:", banner_font, fill=(255, 234, 167), stroke_fill=(10, 10, 10), stroke_width=4)
        draw_action_text(draw, hud_x, cy + 105, "< 0.00000000000001 mm", title_font, fill=(46, 204, 113), stroke_fill=(10, 30, 10), stroke_width=4)
        draw_action_text(draw, hud_x, cy + 145, "(LESS THAN 1 HYDROGEN ATOM!)", sub_font, fill=(0, 206, 201), stroke_fill=(10, 10, 10), stroke_width=2)

        draw_studio_pill(draw, cx, 80, "WHAT IF EVERYONE JUMPED AT ONCE?", title_font, fill=(9, 132, 227), text_fill=(255, 255, 255), pad_x=45, pad_y=16)
        draw_studio_pill(draw, cx, HEIGHT - 75, "SCENE 4: PLANET EARTH IS AN INDESTRUCTIBLE BEAST", banner_font, fill=(9, 132, 227), text_fill=(255, 255, 255))

    # =========================================================================
    # SCENE 5: 78.5s - 101.5s (The REAL Disaster: World's Worst Traffic Jam!)
    # =========================================================================
    elif t_sec < 101.5:
        s5_t = t_sec - 78.5
        # Sunset orange/red highway sky
        draw.rectangle([0, 0, WIDTH, HEIGHT * 0.45], fill=(250, 177, 160))
        # Multi-lane highway gridlock
        draw.rectangle([0, HEIGHT * 0.45, WIDTH, HEIGHT], fill=(87, 96, 111))
        for line_y in [HEIGHT * 0.58, HEIGHT * 0.72, HEIGHT * 0.86]:
            for lx in range(0, WIDTH, 120):
                draw.line([(lx, line_y), (lx + 60, line_y)], fill=(255, 234, 167), width=6)

        # Row of colorful bumper-to-bumper cars
        car_colors = [(255, 71, 87), (46, 204, 113), (9, 132, 227), (254, 202, 87), (155, 89, 182), (230, 126, 34)]
        for i, car_x in enumerate(range(80, WIDTH, 280)):
            car_y = int(HEIGHT * 0.65 + ((i % 2) * 90))
            col = car_colors[i % len(car_colors)]
            draw.rounded_rectangle([car_x - 85, car_y - 35, car_x + 85, car_y + 35], radius=16, fill=col, outline=(30, 30, 30), width=4)
            # Wheels
            draw.ellipse([car_x - 65, car_y + 25, car_x - 35, car_y + 45], fill=(30, 30, 30))
            draw.ellipse([car_x + 35, car_y + 25, car_x + 65, car_y + 45], fill=(30, 30, 30))

        # Bob in red convertible in foreground looking shocked at GPS
        bob_x = int(WIDTH * 0.30)
        bob_y = int(HEIGHT * 0.62 + idle_bob)
        draw_bob(draw, bob_x, bob_y, mood="shocked", t_sec=t_sec, pose="sitting")

        # Giant GPS screen on right
        gps_x = int(WIDTH * 0.70)
        gps_y = int(HEIGHT * 0.48)
        draw.rounded_rectangle([gps_x - 180, gps_y - 120, gps_x + 180, gps_y + 120], radius=18, fill=(47, 53, 66), outline=(255, 71, 87), width=5)
        draw_action_text(draw, gps_x, gps_y - 75, "📍 ROUTE HOME", banner_font, fill=(255, 234, 167), stroke_fill=(20, 20, 20), stroke_width=4)
        draw_action_text(draw, gps_x, gps_y - 15, "ETA: 140 YEARS!", title_font, fill=(255, 71, 87), stroke_fill=(30, 10, 10), stroke_width=5)
        draw_action_text(draw, gps_x, gps_y + 55, "TRAFFIC DELAY: +1,226,400 HRS", sub_font, fill=(241, 242, 246), stroke_fill=(20, 20, 20), stroke_width=2)

        # Honk speech bubbles
        draw_action_text(draw, 240, HEIGHT * 0.38, "BEEP!", sub_font, fill=(255, 234, 167), stroke_fill=(40, 20, 20), stroke_width=4)
        draw_action_text(draw, WIDTH - 260, HEIGHT * 0.35, "HONK!!", sub_font, fill=(255, 71, 87), stroke_fill=(40, 20, 20), stroke_width=4)

        draw_studio_pill(draw, cx, 80, "WHAT IF EVERYONE JUMPED AT ONCE?", title_font, fill=(9, 132, 227), text_fill=(255, 255, 255), pad_x=45, pad_y=16)
        draw_studio_pill(draw, cx, HEIGHT - 75, "SCENE 5: THE 8-BILLION-PERSON GLOBAL TRAFFIC JAM", banner_font, fill=(230, 126, 34), text_fill=(255, 255, 255))

    # =========================================================================
    # SCENE 6: 101.5s - 121.0s (Pizza Shortage & Inflatable Flamingo Ocean Walk)
    # =========================================================================
    elif t_sec < 121.0:
        s6_t = t_sec - 101.5
        # Blue ocean water with gentle wave motion
        draw.rectangle([0, 0, WIDTH, HEIGHT * 0.40], fill=(130, 204, 255))
        draw.rectangle([0, HEIGHT * 0.40, WIDTH, HEIGHT], fill=(0, 168, 255))

        # Sine waves across ocean
        for wy in range(int(HEIGHT * 0.45), HEIGHT, 65):
            wave_pts = []
            for wx in range(0, WIDTH + 40, 40):
                w_offset = math.sin((wx * 0.01) + t_sec * 4.0 + wy) * 12.0
                wave_pts.append((wx, wy + w_offset))
            draw.line(wave_pts, fill=(255, 255, 255, 180), width=4)

        # Giant Inflatable Pool Flamingo in ocean!
        flam_x = cx + int(math.sin(t_sec * 3.0) * 30.0)
        flam_y = int(HEIGHT * 0.65 + math.cos(t_sec * 3.0) * 10.0)

        # Flamingo body (Bright Pink)
        draw.ellipse([flam_x - 120, flam_y - 50, flam_x + 90, flam_y + 50], fill=(255, 107, 129), outline=(40, 30, 30), width=5)
        # Flamingo neck & head
        draw.arc([flam_x + 50, flam_y - 140, flam_x + 130, flam_y + 20], start=180, end=360, fill=(255, 107, 129), width=24)
        draw.ellipse([flam_x + 85, flam_y - 145, flam_x + 135, flam_y - 100], fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        # Beak
        draw.polygon([(flam_x + 130, flam_y - 130), (flam_x + 165, flam_y - 120), (flam_x + 130, flam_y - 110)], fill=(254, 202, 87), outline=(40, 30, 30), width=3)

        # Bob happily riding the inflatable flamingo with sunglasses
        draw_bob(draw, flam_x - 20, flam_y - 110, mood="cheering", t_sec=t_sec, pose="sitting")

        # Floating sign: "OUT OF PIZZA 🍕❌" on left
        draw.rounded_rectangle([120, HEIGHT * 0.25, 420, HEIGHT * 0.40], radius=16, fill=(255, 255, 255), outline=(214, 48, 49), width=5)
        draw_action_text(draw, 270, HEIGHT * 0.32, "PIZZA: SOLD OUT!", banner_font, fill=(214, 48, 49), stroke_fill=(255, 255, 255), stroke_width=2)

        draw_studio_pill(draw, cx, 80, "WHAT IF EVERYONE JUMPED AT ONCE?", title_font, fill=(9, 132, 227), text_fill=(255, 255, 255), pad_x=45, pad_y=16)
        draw_studio_pill(draw, cx, HEIGHT - 75, "SCENE 6: WALKING ACROSS OCEANS ON INFLATABLE FLAMINGOS", banner_font, fill=(255, 107, 129), text_fill=(255, 255, 255))

    # =========================================================================
    # SCENE 7: 121.0s - 135.0s (Cosmic Kitchen & Golden Subscribe Outro)
    # =========================================================================
    else:
        # Cozy warm kitchen interior with golden sunshine
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(254, 249, 231))
        # Warm wooden table
        draw.rectangle([0, HEIGHT - 240, WIDTH, HEIGHT], fill=(247, 215, 148))

        # Golden sunbeams radiating from window
        for i in range(24):
            angle = (2 * math.pi / 24) * i + t_sec * 0.2
            x1 = cx + math.cos(angle) * 1200
            y1 = cy + math.sin(angle) * 1200
            draw.polygon([(cx, cy), (x1, y1), (x1 + 50, y1 + 50)], fill=(255, 220, 100, 35))

        # Bob at table happily enjoying a stack of pancakes
        bob_x = int(WIDTH * 0.35)
        bob_y = int(HEIGHT - 380 + idle_bob)
        draw_bob(draw, bob_x, bob_y, mood="happy", t_sec=t_sec, pose="sitting")

        # Giant stack of 5 golden pancakes on a plate
        plate_x = bob_x + 190
        plate_y = HEIGHT - 210
        draw.ellipse([plate_x - 90, plate_y - 25, plate_x + 90, plate_y + 25], fill=(240, 240, 245), outline=(40, 30, 30), width=4)
        for p_i in range(5):
            py = plate_y - 18 - p_i * 16
            draw.ellipse([plate_x - 70, py - 16, plate_x + 70, py + 16], fill=(243, 156, 18), outline=(40, 30, 30), width=3)
        # Butter cube on top
        draw.rectangle([plate_x - 14, plate_y - 110, plate_x + 14, plate_y - 85], fill=(254, 202, 87), outline=(40, 30, 30), width=3)

        # Big Interactive Subscribe Box on Right
        sub_cx = int(WIDTH * 0.72)
        sub_cy = int(HEIGHT * 0.50 + math.sin(t_sec * 8.0) * 8.0)
        draw_studio_pill(draw, sub_cx, sub_cy - 60, "ALWAYS WEAR YOUR COSMIC SEATBELT!", banner_font, fill=(9, 132, 227), text_fill=(255, 255, 255), pad_x=32, pad_y=12)

        # Red Subscribe Button Pill with ringing bell
        sub_btn = draw_studio_pill(draw, sub_cx, sub_cy + 40, "SMASH SUBSCRIBE!", title_font, fill=(255, 71, 87), text_fill=(255, 255, 255), pad_x=45, pad_y=16)
        draw_vector_bell(draw, sub_btn[0] - 25, sub_cy + 40, r=26, fill=(254, 202, 87))

        draw_studio_pill(draw, cx, 80, "WHAT IF EVERYONE JUMPED AT ONCE?", title_font, fill=(9, 132, 227), text_fill=(255, 255, 255), pad_x=45, pad_y=16)
        draw_studio_pill(draw, cx, HEIGHT - 75, "OUTRO: SEE YOU IN THE NEXT BIG QUESTION!", banner_font, fill=(46, 204, 113), text_fill=(255, 255, 255))

    # Apply screen shake offset if active
    if abs(shake_x) > 0 or abs(shake_y) > 0:
        shaken = Image.new("RGB", (WIDTH, HEIGHT), (10, 10, 15))
        shaken.paste(frame, (shake_x, shake_y))
        frame = shaken

    return frame


def produce_everyone_jumped_masterpiece():
    """Renders the full 2m 15s masterpiece in Channel 1's beloved style."""
    logger.info("🎬 Rendering 2m 15s Flagship Masterpiece: 'What If Everyone On Earth Jumped At Once?'...")

    voice_path = str(AUDIO_DIR / "full_voice_135s.m4a")
    music_path = str(AUDIO_DIR / "cartoon_music_135s.wav")

    voice_dur = get_audio_duration(voice_path)
    logger.info(f"🎤 Voiceover Duration: {voice_dur:.2f}s (~2m 15s)")

    total_frames = int(voice_dur * FPS)
    logger.info(f"⏱️ Total Frames to Render: {total_frames} @ {FPS}fps")

    title_font = get_font(size=48, font_type="rounded")
    banner_font = get_font(size=34, font_type="rounded")
    sub_font = get_font(size=26, font_type="rounded")
    giant_font = get_font(size=88, font_type="impact")

    ffmpeg_bin = get_ffmpeg_binary()
    hw = detect_hardware()

    final_output = EXPORTS_DIR / "What_If_Everyone_Jumped_2m15s.mp4"
    final_output.parent.mkdir(parents=True, exist_ok=True)
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg_bin,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",  # Video frames from stdin
        "-i", voice_path,  # Input 1: Voiceover
        "-i", music_path,  # Input 2: Dynamic soundtrack
        "-filter_complex",
        "[2:a]volume=0.28[music];[1:a]volume=1.05[voice];[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", hw.video_encoder,
        "-c:a", hw.audio_encoder,
        "-b:v", "9000k",
        "-b:a", "256k",
        "-pix_fmt", "yuv420p",
        str(final_output),
    ]

    logger.info("Rendering frames into FFmpeg pipeline with Apple Silicon VideoToolbox...")
    ffmpeg_log = open(BASE_DIR / "ffmpeg_render_jump.log", "w")
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=ffmpeg_log, stderr=ffmpeg_log)

    t0 = time.time()
    for frame_idx in range(total_frames):
        t_sec = frame_idx / float(FPS)
        frame_img = render_jump_frame(frame_idx, total_frames, t_sec, title_font, banner_font, sub_font, giant_font)
        try:
            process.stdin.write(frame_img.tobytes())
        except BrokenPipeError:
            logger.error("Broken pipe writing to FFmpeg!")
            break

        if frame_idx % 300 == 0:
            pct = int((frame_idx / total_frames) * 100)
            logger.info(f"Rendering: {pct}% ({frame_idx}/{total_frames} frames)")

    process.stdin.close()
    process.wait()
    ffmpeg_log.close()

    if process.returncode != 0:
        err_msg = ""
        log_file = BASE_DIR / "ffmpeg_render_jump.log"
        if log_file.exists():
            err_msg = log_file.read_text()
        raise RuntimeError(f"FFmpeg failed with exit code {process.returncode}: {err_msg}")

    render_elapsed = time.time() - t0
    logger.success(f"🎉 2m 15s Render completed in {render_elapsed:.1f}s ({total_frames / max(0.1, render_elapsed):.1f} fps)!")

    # High-CTR YouTube Viral Thumbnail (1280x720 16:9)
    logger.info("🖼️ Creating High-CTR YouTube Thumbnail...")
    cx, cy = WIDTH // 2, HEIGHT // 2
    thumb_path = THUMBNAILS_DIR / "Everyone_Jumped_2m15s_Thumbnail.jpg"
    thumb_img = Image.new("RGB", (WIDTH, HEIGHT), (20, 25, 45))
    draw_th = ImageDraw.Draw(thumb_img)

    # Split composition: Space Planet Earth on Left / Rhode Island Jump Crowd on Right
    draw_th.rectangle([0, 0, WIDTH // 2, HEIGHT], fill=(15, 20, 35))
    # Earth on left
    draw_th.ellipse([WIDTH // 4 - 240, HEIGHT // 2 - 240, WIDTH // 4 + 240, HEIGHT // 2 + 240], fill=(9, 132, 227), outline=(40, 30, 30), width=6)
    draw_th.ellipse([WIDTH // 4 - 150, HEIGHT // 2 - 130, WIDTH // 4 + 50, HEIGHT // 2 + 50], fill=(46, 204, 113))

    # Right side: Sunset Jump field
    draw_th.rectangle([WIDTH // 2, 0, WIDTH, HEIGHT], fill=(225, 112, 85))
    draw_th.rectangle([WIDTH // 2, HEIGHT * 0.60, WIDTH, HEIGHT], fill=(99, 110, 114))

    # Center neon divider
    draw_th.line([(WIDTH // 2, 0), (WIDTH // 2, HEIGHT)], fill=(255, 71, 87), width=12)

    # Bob jumping with shock face on right side
    draw_bob(draw_th, WIDTH * 0.75, HEIGHT * 0.48, mood="shocked", t_sec=1.0, pose="jumping")

    # Giant Comic Title (No box, clean drop shadow)
    thumb_font = get_font(size=82, font_type="impact")
    draw_action_text(draw_th, cx, 90, "WHAT IF EVERYONE JUMPED AT ONCE?!", thumb_font, fill=(255, 240, 80), stroke_fill=(30, 20, 20), stroke_width=14)

    pill_font = get_font(size=48, font_type="rounded")
    draw_studio_pill(draw_th, cx, HEIGHT - 110, "8 BILLION HUMANS VS PLANET EARTH!", pill_font, fill=(255, 71, 87), text_fill=(255, 255, 255), pad_x=45, pad_y=16)

    thumb_final = thumb_img.resize((1280, 720), Image.Resampling.LANCZOS)
    thumb_final.save(str(thumb_path), "JPEG", quality=95)

    info = get_video_info(str(final_output))
    logger.success("==================================================")
    logger.success("🎉 PRODUCTION-READY 2M 15S MASTERPIECE READY!")
    logger.success(f"📍 Video File: {final_output}")
    logger.success(f"⏱️ Runtime: {info.get('duration', 0):.1f} seconds (Target: 135.0s / 2m 15s)")
    logger.success(f"📐 Resolution: {info.get('width')}x{info.get('height')} 1080p Full HD")
    logger.success(f"🖼️ Thumbnail: {thumb_path}")
    logger.success("==================================================")

    return str(final_output), str(thumb_path)


if __name__ == "__main__":
    produce_everyone_jumped_masterpiece()
