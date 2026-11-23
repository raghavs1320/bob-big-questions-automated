"""Procedural 2D Animated Cartoon: 'What Happens If All Oceans Dried Up For 24 Hours?'

Bob Big Questions - Episode 6 (2m 17s Flagship Special):
- Exact Runtime: Exactly 2 minutes 17 seconds (137.0s / 4,110 frames @ 30fps)
- Signature Channel 1 Procedural Vector Aesthetic:
    * Clean mathematical curves, rich procedural gradients, dynamic particles.
    * Character: Bob (beach lounger, cliff edge, firefighter whale rescuer, sofa, tsunami surfer).
    * True Ink-Centered Modern Studio Pill Badges & Free-Floating Comic Typography.
    * Screen Rumbles, Tsunami Crests, Martian Dust Storms, Hydrothermal Vents.
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
TOTAL_FRAMES = 4110  # 137.0 seconds @ 30fps = 2m 17s

EXPORTS_DIR = BASE_DIR / "exports" / "videos"
THUMBNAILS_DIR = BASE_DIR / "exports" / "thumbnails"
AUDIO_DIR = BASE_DIR / "audio" / "ocean_137s"

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

    # Drop shadow
    draw.rounded_rectangle([x_left, y_top + 4, x_right, y_bottom + 4], radius=radius, fill=(20, 20, 30))
    # Main badge
    draw.rounded_rectangle([x_left, y_top, x_right, y_bottom], radius=radius, fill=fill)

    draw_x = cx - (x0 + x1) / 2.0
    draw_y = center_y - (y0 + y1) / 2.0
    draw.text((draw_x, draw_y), text, font=font, fill=text_fill)
    return [x_left, y_top, x_right, y_bottom]


def draw_action_text(draw, cx: int, cy: int, text: str, font, fill=(255, 234, 167), stroke_fill=(40, 20, 20), stroke_width: int = 6):
    """Draws free-floating comic action typography with bold outlines and drop shadow."""
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


def draw_bob(draw, cx: int, cy: int, mood="happy", t_sec: float = 0.0, pose="standing", hat=None):
    """Draws Bob in Channel 1's beloved procedural vector style."""
    bx, by = cx, cy
    radius = 85

    # 1. Clothing & Body
    if pose == "standing":
        draw.rounded_rectangle([bx - 65, by + 55, bx + 65, by + 210], radius=26, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
        draw.rounded_rectangle([bx - 60, by + 205, bx - 10, by + 285], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx + 10, by + 205, bx + 60, by + 285], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx - 75, by + 275, bx - 5, by + 305], radius=10, fill=(254, 202, 87), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx + 5, by + 275, bx + 75, by + 305], radius=10, fill=(254, 202, 87), outline=(40, 30, 30), width=4)

    elif pose == "lounging":
        # Relaxing horizontal body on beach towel
        draw.rounded_rectangle([bx - 120, by + 40, bx + 40, by + 130], radius=24, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
        draw.rounded_rectangle([bx + 30, by + 55, bx + 130, by + 115], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx + 120, by + 75, bx + 160, by + 110], radius=8, fill=(254, 202, 87), outline=(40, 30, 30), width=3)

    elif pose == "holding_hose":
        draw.rounded_rectangle([bx - 65, by + 55, bx + 65, by + 210], radius=26, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
        draw.rounded_rectangle([bx - 60, by + 205, bx - 10, by + 285], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx + 10, by + 205, bx + 60, by + 285], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx - 75, by + 275, bx - 5, by + 305], radius=10, fill=(254, 202, 87), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx + 5, by + 275, bx + 75, by + 305], radius=10, fill=(254, 202, 87), outline=(40, 30, 30), width=4)
        # Green garden hose nozzle
        draw.line([(bx + 30, by + 110), (bx + 120, by + 80)], fill=(46, 204, 113), width=18)
        draw.polygon([(bx + 115, by + 70), (bx + 145, by + 80), (bx + 115, by + 90)], fill=(241, 196, 15))

    elif pose == "surfing":
        draw.rounded_rectangle([bx - 55, by + 45, bx + 55, by + 180], radius=22, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
        # Deep crouch surfing legs
        draw.rounded_rectangle([bx - 80, by + 160, bx - 20, by + 230], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        draw.rounded_rectangle([bx + 20, by + 160, bx + 80, by + 230], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        # Outstretched balancing arms
        draw.line([(bx - 50, by + 65), (bx - 120, by + 30)], fill=(0, 206, 201), width=18)
        draw.line([(bx + 50, by + 65), (bx + 120, by + 30)], fill=(0, 206, 201), width=18)

    elif pose == "sitting_sofa":
        draw.rounded_rectangle([bx - 65, by + 55, bx + 65, by + 200], radius=26, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
        draw.rounded_rectangle([bx - 60, by + 195, bx + 60, by + 265], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)

    # 2. Head
    draw.ellipse([bx - radius, by - radius, bx + radius, by + radius], fill=(255, 224, 189), outline=(40, 30, 30), width=5)

    # 3. Messy Hair
    draw.arc([bx - radius - 5, by - radius - 5, bx + radius + 5, by + 10], start=180, end=360, fill=(75, 45, 25), width=24)
    draw.polygon([(bx - 40, by - radius - 5), (bx - 20, by - radius - 35), (bx, by - radius - 5)], fill=(75, 45, 25))
    draw.polygon([(bx + 5, by - radius - 5), (bx + 30, by - radius - 40), (bx + 50, by - radius - 5)], fill=(75, 45, 25))

    # Optional Hat
    if hat == "firefighter":
        draw.chord([bx - 70, by - radius - 10, bx + 70, by - radius + 40], start=180, end=360, fill=(231, 76, 60), outline=(40, 30, 30), width=4)
        draw.polygon([(bx - 20, by - radius - 20), (bx, by - radius - 45), (bx + 20, by - radius - 20)], fill=(254, 202, 87))

    # 4. Expressions
    if mood == "happy":
        draw.ellipse([bx - 36, by - 12, bx - 14, by + 14], fill=(35, 30, 30))
        draw.ellipse([bx + 14, by - 12, bx + 36, by + 14], fill=(35, 30, 30))
        draw.ellipse([bx - 32, by - 8, bx - 22, by + 2], fill=(255, 255, 255))
        draw.ellipse([bx + 18, by - 8, bx + 28, by + 2], fill=(255, 255, 255))
        draw.arc([bx - 32, by + 12, bx + 32, by + 52], start=15, end=165, fill=(35, 30, 30), width=5)
        draw.ellipse([bx - 58, by + 18, bx - 38, by + 34], fill=(255, 150, 150))
        draw.ellipse([bx + 38, by + 18, bx + 58, by + 34], fill=(255, 150, 150))

    elif mood == "sunglasses":
        # Cool black sunglasses
        draw.rounded_rectangle([bx - 55, by - 18, bx - 8, by + 16], radius=6, fill=(25, 25, 30), outline=(10, 10, 15), width=3)
        draw.rounded_rectangle([bx + 8, by - 18, bx + 55, by + 16], radius=6, fill=(25, 25, 30), outline=(10, 10, 15), width=3)
        draw.line([(bx - 8, by - 4), (bx + 8, by - 4)], fill=(10, 10, 15), width=4)
        # White highlight shine on sunglasses
        draw.line([(bx - 48, by - 10), (bx - 36, by + 6)], fill=(255, 255, 255), width=3)
        draw.line([(bx + 15, by - 10), (bx + 27, by + 6)], fill=(255, 255, 255), width=3)
        # Smug beach grin
        draw.arc([bx - 26, by + 16, bx + 26, by + 48], start=20, end=160, fill=(35, 30, 30), width=5)

    elif mood == "shocked":
        draw.ellipse([bx - 50, by - 30, bx - 10, by + 20], fill=(255, 255, 255), outline=(35, 30, 30), width=4)
        draw.ellipse([bx + 10, by - 30, bx + 50, by + 20], fill=(255, 255, 255), outline=(35, 30, 30), width=4)
        draw.ellipse([bx - 33, by - 8, bx - 27, by - 2], fill=(35, 30, 30))
        draw.ellipse([bx + 27, by - 8, bx + 33, by - 2], fill=(35, 30, 30))
        draw.ellipse([bx - 22, by + 24, bx + 22, by + 68], fill=(180, 40, 50), outline=(35, 30, 30), width=4)
        draw.ellipse([bx + 55, by - 45, bx + 70, by - 25], fill=(80, 200, 255), outline=(35, 30, 30), width=3)

    elif mood == "sweating":
        draw.ellipse([bx - 40, by - 15, bx - 12, by + 10], fill=(255, 255, 255), outline=(35, 30, 30), width=4)
        draw.ellipse([bx + 12, by - 15, bx + 40, by + 10], fill=(255, 255, 255), outline=(35, 30, 30), width=4)
        draw.ellipse([bx - 28, by - 6, bx - 20, by + 2], fill=(35, 30, 30))
        draw.ellipse([bx + 20, by - 6, bx + 28, by + 2], fill=(35, 30, 30))
        # Drooping mouth
        draw.arc([bx - 28, by + 28, bx + 28, by + 60], start=200, end=340, fill=(35, 30, 30), width=5)
        # Massive sweat drops
        draw.ellipse([bx - 60, by - 30, bx - 45, by - 10], fill=(80, 200, 255), outline=(35, 30, 30), width=3)
        draw.ellipse([bx + 50, by - 20, bx + 65, by], fill=(80, 200, 255), outline=(35, 30, 30), width=3)

    elif mood == "determined":
        # Fierce focused eyes
        draw.polygon([(bx - 45, by - 15), (bx - 15, by - 5), (bx - 20, by + 10)], fill=(35, 30, 30))
        draw.polygon([(bx + 45, by - 15), (bx + 15, by - 5), (bx + 20, by + 10)], fill=(35, 30, 30))
        draw.line([(bx - 25, by + 30), (bx + 25, by + 30)], fill=(35, 30, 30), width=5)


def draw_cat(draw, cx: int, cy: int, mood="eating"):
    """Draws Bob's signature orange tabby cat."""
    # Body
    draw.ellipse([cx - 45, cy - 25, cx + 45, cy + 35], fill=(255, 159, 67), outline=(40, 30, 30), width=4)
    # Head
    draw.ellipse([cx - 32, cy - 60, cx + 32, cy], fill=(255, 159, 67), outline=(40, 30, 30), width=4)
    # Ears
    draw.polygon([(cx - 30, cy - 50), (cx - 20, cy - 80), (cx - 5, cy - 55)], fill=(255, 159, 67), outline=(40, 30, 30))
    draw.polygon([(cx + 5, cy - 55), (cx + 20, cy - 80), (cx + 30, cy - 50)], fill=(255, 159, 67), outline=(40, 30, 30))
    # Green eyes
    draw.ellipse([cx - 18, cy - 38, cx - 6, cy - 22], fill=(46, 204, 113), outline=(40, 30, 30), width=2)
    draw.ellipse([cx + 6, cy - 38, cx + 18, cy - 22], fill=(46, 204, 113), outline=(40, 30, 30), width=2)
    # Nose & Whiskers
    draw.polygon([(cx - 4, cy - 22), (cx + 4, cy - 22), (cx, cy - 17)], fill=(255, 107, 129))
    draw.line([(cx - 15, cy - 18), (cx - 40, cy - 20)], fill=(40, 30, 30), width=2)
    draw.line([(cx + 15, cy - 18), (cx + 40, cy - 20)], fill=(40, 30, 30), width=2)
    # Tail curled up
    draw.arc([cx + 30, cy - 40, cx + 75, cy + 30], start=270, end=90, fill=(255, 159, 67), width=10)


def draw_blue_whale(draw, cx: int, cy: int, t_sec: float):
    """Draws a giant, friendly, stranded cartoon blue whale."""
    # Main Body
    draw.chord([cx - 380, cy - 180, cx + 380, cy + 180], start=0, end=180, fill=(52, 152, 219), outline=(40, 30, 30), width=6)
    # White belly grooves
    draw.chord([cx - 240, cy, cx + 240, cy + 175], start=0, end=180, fill=(236, 240, 241), outline=(40, 30, 30), width=4)
    # Tail fin
    draw.polygon([(cx - 360, cy + 20), (cx - 440, cy - 60), (cx - 420, cy + 10)], fill=(41, 128, 185), outline=(40, 30, 30), width=4)
    draw.polygon([(cx - 360, cy + 20), (cx - 440, cy + 80), (cx - 420, cy + 10)], fill=(41, 128, 185), outline=(40, 30, 30), width=4)
    # Eye with worried expression
    draw.ellipse([cx + 220, cy + 10, cx + 250, cy + 40], fill=(255, 255, 255), outline=(40, 30, 30), width=3)
    draw.ellipse([cx + 235, cy + 20, cx + 245, cy + 30], fill=(40, 30, 30))
    # Blowhole with tiny puff of steam
    puff_y = cy - 20 + int(math.sin(t_sec * 6.0) * 15)
    draw.ellipse([cx + 60, puff_y, cx + 100, puff_y + 35], fill=(255, 255, 255, 180))


def render_ocean_frame(frame_idx: int, total_frames: int, t_sec: float, title_font, banner_font, sub_font, giant_font):
    """Renders an individual frame of the 2m 17s flagship masterpiece."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (245, 246, 250))
    draw = ImageDraw.Draw(img, "RGBA")
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Scene boundaries (total: 4,110 frames = 137.0s)
    # S1: 0 - 556 (18.53s) | S2: 556 - 1107 (18.37s) | S3: 1107 - 1796 (22.97s)
    # S4: 1796 - 2355 (18.63s) | S5: 2355 - 2962 (20.23s) | S6: 2962 - 3566 (20.13s) | S7: 3566 - 4110 (18.13s)

    shake_x, shake_y = 0, 0

    # -------------------------------------------------------------
    # SCENE 1: THE BEACH & THE 350 QUINTILLION GALLON DRAIN (0 - 556)
    # -------------------------------------------------------------
    if frame_idx < 556:
        t_loc = t_sec
        # Sunny cyan beach sky
        draw.rectangle([0, 0, WIDTH, HEIGHT * 0.55], fill=(135, 206, 235))
        # Sun
        draw.ellipse([WIDTH - 240, 60, WIDTH - 100, 200], fill=(254, 202, 87), outline=(243, 156, 18), width=5)
        # Sandy beach
        draw.rectangle([0, HEIGHT * 0.55, WIDTH, HEIGHT], fill=(245, 222, 179))

        # Water receding animation: starts full, rapidly pulls away leaving mud & fish
        recede_progress = min(1.0, max(0.0, (t_loc - 4.0) / 7.0))
        water_left = int(recede_progress * (WIDTH + 400))
        if water_left < WIDTH:
            # Ocean water
            draw.rectangle([water_left, HEIGHT * 0.52, WIDTH, HEIGHT * 0.85], fill=(9, 132, 227))
            # White foamy wave line
            draw.line([(water_left, HEIGHT * 0.52), (water_left, HEIGHT * 0.85)], fill=(255, 255, 255), width=8)

        # Beach Umbrella
        draw.line([(320, HEIGHT * 0.65), (320, HEIGHT * 0.40)], fill=(120, 100, 80), width=10)
        draw.chord([200, HEIGHT * 0.30, 440, HEIGHT * 0.48], start=180, end=360, fill=(255, 71, 87), outline=(40, 30, 30), width=4)

        # Bob lounging on beach towel
        bob_mood = "sunglasses" if t_loc < 5.0 else "shocked"
        draw.rounded_rectangle([420, HEIGHT * 0.62, 680, HEIGHT * 0.72], radius=16, fill=(254, 202, 87), outline=(40, 30, 30), width=4)
        draw_bob(draw, 520, HEIGHT * 0.56, mood=bob_mood, t_sec=t_loc, pose="lounging")

        # Glass of lemonade with straw
        draw.rounded_rectangle([710, HEIGHT * 0.60, 745, HEIGHT * 0.68], radius=6, fill=(255, 250, 101), outline=(40, 30, 30), width=3)
        draw.line([(735, HEIGHT * 0.57), (750, HEIGHT * 0.53)], fill=(255, 71, 87), width=4)

        if t_loc > 4.5 and t_loc < 12.0:
            draw_action_text(draw, cx + 180, HEIGHT * 0.42, "SLUUUURP!", giant_font, fill=(255, 234, 167), stroke_fill=(30, 20, 20), stroke_width=12)

        # Badges
        draw_studio_pill(draw, cx, 80, "WHAT IF ALL OCEANS DRIED UP FOR 24 HOURS?", title_font, fill=(9, 132, 227))
        draw_studio_pill(draw, cx, HEIGHT - 75, "HOUR 0: 350 QUINTILLION GALLONS VANISH INTO THIN AIR!", banner_font, fill=(255, 71, 87))

    # -------------------------------------------------------------
    # SCENE 2: THE ABYSSAL CANYON & SUNKEN PIRATE SECRETS (556 - 1107)
    # -------------------------------------------------------------
    elif frame_idx < 1107:
        t_loc = t_sec - 18.53
        # Deep dark blue twilight oceanic abyss background
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(20, 25, 45))

        # Continental shelf cliff edge on left side
        draw.polygon([(0, HEIGHT * 0.40), (450, HEIGHT * 0.40), (700, HEIGHT), (0, HEIGHT)], fill=(87, 101, 116), outline=(40, 30, 30), width=5)

        # Bob standing at the edge looking down in shock
        draw_bob(draw, 380, HEIGHT * 0.28, mood="shocked", t_sec=t_loc, pose="standing")

        # Sunken 17th Century Pirate Galleon Ship on canyon floor
        ship_x, ship_y = WIDTH * 0.68, HEIGHT * 0.70
        draw.polygon([(ship_x - 140, ship_y), (ship_x + 140, ship_y - 20), (ship_x + 120, ship_y + 80), (ship_x - 100, ship_y + 80)], fill=(120, 80, 50), outline=(30, 20, 15), width=4)
        # Mast & Tattered Jolly Roger flag
        draw.line([(ship_x, ship_y), (ship_x, ship_y - 160)], fill=(90, 60, 40), width=8)
        draw.polygon([(ship_x, ship_y - 150), (ship_x + 70, ship_y - 130), (ship_x, ship_y - 110)], fill=(30, 30, 35))

        # Glowing golden treasure chest
        chest_glow = int(math.sin(t_loc * 5.0) * 8)
        draw.rounded_rectangle([ship_x + 160, ship_y + 30, ship_x + 230, ship_y + 80], radius=8, fill=(254, 202, 87), outline=(40, 30, 30), width=3)
        draw.ellipse([ship_x + 150, ship_y + 20, ship_x + 240, ship_y + 90], outline=(255, 234, 167), width=3 + chest_glow)

        # Glowing deep-sea anglerfish floating in air
        angler_x = int(WIDTH * 0.52 + math.sin(t_loc * 3.0) * 40)
        angler_y = int(HEIGHT * 0.48 + math.cos(t_loc * 3.0) * 25)
        draw.ellipse([angler_x - 45, angler_y - 30, angler_x + 45, angler_y + 30], fill=(44, 62, 80), outline=(20, 20, 25), width=3)
        # Lure with glowing light
        draw.arc([angler_x + 20, angler_y - 65, angler_x + 75, angler_y - 10], start=180, end=360, fill=(46, 204, 113), width=4)
        draw.ellipse([angler_x + 70, angler_y - 45, angler_x + 95, angler_y - 20], fill=(46, 204, 113))

        draw_action_text(draw, cx + 180, 180, "12,000 FT DEEP CANYON!", giant_font, fill=(255, 240, 80), stroke_fill=(30, 20, 20), stroke_width=10)

        # Badges
        draw_studio_pill(draw, cx, 80, "WHAT IF ALL OCEANS DRIED UP FOR 24 HOURS?", title_font, fill=(9, 132, 227))
        draw_studio_pill(draw, cx, HEIGHT - 75, "HOUR 1: LOST PIRATE GALLEONS & GLOWING ANGLERFISH EXPOSED", banner_font, fill=(241, 196, 15), text_fill=(40, 30, 30))

    # -------------------------------------------------------------
    # SCENE 3: THE CLIMATE COLLAPSE & OXYGEN HALT (1107 - 1796)
    # -------------------------------------------------------------
    elif frame_idx < 1796:
        t_loc = t_sec - 36.90
        # Scorching orange & crimson heatwave sky
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(235, 94, 40))

        # Blazing sun with pulsing solar flare rays
        sun_pulse = int(math.sin(t_loc * 6.0) * 20)
        draw.ellipse([cx - 180 - sun_pulse, 120 - sun_pulse, cx + 180 + sun_pulse, 480 + sun_pulse], fill=(255, 107, 129, 120))
        draw.ellipse([cx - 140, 160, cx + 140, 440], fill=(254, 202, 87), outline=(231, 76, 60), width=6)

        # Dry cracked mud earth ground
        draw.rectangle([0, HEIGHT * 0.65, WIDTH, HEIGHT], fill=(139, 69, 19))
        for crx in range(100, WIDTH, 160):
            draw.line([(crx, HEIGHT * 0.65), (crx + 40, HEIGHT * 0.78), (crx - 20, HEIGHT)], fill=(60, 30, 10), width=4)

        # Bob sweating profusely with ice pack on head
        draw_bob(draw, cx - 180, HEIGHT * 0.52, mood="sweating", t_sec=t_loc, pose="standing")
        # Ice pack
        draw.ellipse([cx - 210, HEIGHT * 0.52 - 120, cx - 150, HEIGHT * 0.52 - 80], fill=(80, 200, 255), outline=(40, 30, 30), width=3)

        # Giant Thermometer HUD on Right
        therm_x = WIDTH - 260
        draw.rounded_rectangle([therm_x, HEIGHT * 0.25, therm_x + 90, HEIGHT * 0.85], radius=45, fill=(255, 255, 255), outline=(40, 30, 30), width=6)
        # Rising Mercury column
        merc_h = min(HEIGHT * 0.50, HEIGHT * 0.25 + t_loc * 18.0)
        draw.rounded_rectangle([therm_x + 15, HEIGHT * 0.80 - merc_h, therm_x + 75, HEIGHT * 0.80], radius=25, fill=(231, 76, 60))
        draw.ellipse([therm_x - 10, HEIGHT * 0.76, therm_x + 100, HEIGHT * 0.87], fill=(231, 76, 60), outline=(40, 30, 30), width=5)

        draw_action_text(draw, cx + 120, HEIGHT * 0.45, "125°F SCORCHING!", giant_font, fill=(255, 234, 167), stroke_fill=(30, 20, 20), stroke_width=12)

        # Badges
        draw_studio_pill(draw, cx, 80, "WHAT IF ALL OCEANS DRIED UP FOR 24 HOURS?", title_font, fill=(9, 132, 227))
        draw_studio_pill(draw, cx, HEIGHT - 75, "HOUR 3: 50% OF PLANETARY O2 HALTS & TEMPERATURE SPIKES TO 125°F!", banner_font, fill=(255, 71, 87))

    # -------------------------------------------------------------
    # SCENE 4: THE GREAT WHALE RESCUE & CAT SUSHI FEAST (1796 - 2355)
    # -------------------------------------------------------------
    elif frame_idx < 2355:
        t_loc = t_sec - 59.87
        # Sandy coral reef backdrop
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(250, 177, 160))
        draw.rectangle([0, HEIGHT * 0.60, WIDTH, HEIGHT], fill=(225, 112, 85))

        # Giant friendly blue whale stranded on seabed
        draw_blue_whale(draw, cx + 180, HEIGHT * 0.62, t_sec)

        # Bob in firefighter helmet spraying hose
        draw_bob(draw, cx - 280, HEIGHT * 0.48, mood="determined", t_sec=t_loc, pose="holding_hose", hat="firefighter")

        # Water droplets spraying from hose toward whale
        for di in range(12):
            drop_x = cx - 140 + di * 35 + int(math.sin(t_loc * 12.0 + di) * 10)
            drop_y = HEIGHT * 0.50 + int(math.cos(t_loc * 10.0 + di) * 20) - di * 3
            draw.ellipse([drop_x, drop_y, drop_x + 16, drop_y + 16], fill=(52, 152, 219))

        # Bob's cat enjoying mountains of fish on left
        draw_cat(draw, cx - 440, HEIGHT * 0.70)
        # Fish pile
        for fi in range(6):
            fx = cx - 520 + fi * 25
            fy = HEIGHT * 0.72 + (fi % 2) * 12
            draw.ellipse([fx, fy, fx + 30, fy + 14], fill=(129, 236, 236), outline=(40, 30, 30), width=2)

        draw_action_text(draw, cx, 180, "SAVE THE WHALE!", giant_font, fill=(255, 240, 80), stroke_fill=(30, 20, 20), stroke_width=12)

        # Badges
        draw_studio_pill(draw, cx, 80, "WHAT IF ALL OCEANS DRIED UP FOR 24 HOURS?", title_font, fill=(9, 132, 227))
        draw_studio_pill(draw, cx, HEIGHT - 75, "HOUR 12: BOB'S RESCUE SQUAD VS CAT'S FREE SUSHI BUFFET!", banner_font, fill=(46, 204, 113))

    # -------------------------------------------------------------
    # SCENE 5: THE GLOBAL DUST STORM & BROKEN WATER CYCLE (2355 - 2962)
    # -------------------------------------------------------------
    elif frame_idx < 2962:
        t_loc = t_sec - 78.50
        # Crimson dusty Mars-like sky
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(192, 57, 43))

        # City Skyline Silhouette in background
        buildings = [(100, 380, 180), (320, 480, 220), (580, 350, 190), (810, 520, 240), (1100, 420, 200), (1350, 460, 210), (1600, 390, 220)]
        for bx, by, bw in buildings:
            draw.rectangle([bx, HEIGHT - by, bx + bw, HEIGHT], fill=(120, 35, 25))

        # Swirling animated dust storm particles
        np.random.seed(frame_idx % 25)
        for _ in range(40):
            px = np.random.randint(0, WIDTH)
            py = np.random.randint(0, HEIGHT)
            plen = np.random.randint(40, 120)
            draw.line([(px, py), (px + plen, py + 15)], fill=(243, 156, 18, 160), width=np.random.randint(2, 6))

        # Bob coughing in shock with goggles
        draw_bob(draw, cx, HEIGHT * 0.50, mood="shocked", t_sec=t_loc, pose="standing")

        draw_action_text(draw, cx, 180, "EARTH TURNS INTO MARS!", giant_font, fill=(255, 234, 167), stroke_fill=(30, 20, 20), stroke_width=12)

        # Badges
        draw_studio_pill(draw, cx, 80, "WHAT IF ALL OCEANS DRIED UP FOR 24 HOURS?", title_font, fill=(9, 132, 227))
        draw_studio_pill(draw, cx, HEIGHT - 75, "HOUR 18: ZERO EVAPORATION, NO RAIN & APOCALYPTIC DUST STORMS!", banner_font, fill=(230, 126, 34))

    # -------------------------------------------------------------
    # SCENE 6: THE RETURN COUNTDOWN & SKY WATERFALL (2962 - 3566)
    # -------------------------------------------------------------
    elif frame_idx < 3566:
        t_loc = t_sec - 98.73
        # Dark dramatic pre-impact stormy indigo sky
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(24, 32, 54))

        # Inflatable Yellow Sofa on dry seabed
        draw.rounded_rectangle([cx - 200, HEIGHT * 0.65, cx + 200, HEIGHT * 0.85], radius=35, fill=(254, 202, 87), outline=(40, 30, 30), width=6)
        draw.rounded_rectangle([cx - 230, HEIGHT * 0.58, cx - 170, HEIGHT * 0.82], radius=25, fill=(225, 177, 44), outline=(40, 30, 30), width=5)
        draw.rounded_rectangle([cx + 170, HEIGHT * 0.58, cx + 230, HEIGHT * 0.82], radius=25, fill=(225, 177, 44), outline=(40, 30, 30), width=5)

        # Bob sitting on emergency sofa looking up
        draw_bob(draw, cx, HEIGHT * 0.44, mood="shocked", t_sec=t_loc, pose="sitting_sofa")

        # Titanic waterfall opening up from heaven
        waterfall_w = int(min(WIDTH, t_loc * 180))
        draw.rectangle([cx - waterfall_w // 2, 0, cx + waterfall_w // 2, HEIGHT * 0.50], fill=(52, 152, 219, 200))
        for stream_x in range(cx - waterfall_w // 2, cx + waterfall_w // 2, 60):
            draw.line([(stream_x, 0), (stream_x, HEIGHT * 0.50)], fill=(255, 255, 255), width=6)

        # Digital Countdown Clock
        countdown_secs = max(0, int(20.0 - t_loc))
        count_str = f"23:59:{40 + countdown_secs:02d}" if countdown_secs > 0 else "24:00:00 (RETURN!)"
        draw_studio_pill(draw, cx, 180, count_str, giant_font, fill=(231, 76, 60), text_fill=(255, 255, 255), pad_x=50, pad_y=18)

        # Screen shake when waterfall hits
        if t_loc > 14.0:
            shake_x = int(math.sin(t_sec * 45.0) * 18)
            shake_y = int(math.cos(t_sec * 40.0) * 16)
            draw_action_text(draw, cx, HEIGHT * 0.35, "THE SKY CRACKS OPEN!", giant_font, fill=(255, 240, 80), stroke_fill=(30, 20, 20), stroke_width=14)

        # Badges
        draw_studio_pill(draw, cx, 80, "WHAT IF ALL OCEANS DRIED UP FOR 24 HOURS?", title_font, fill=(9, 132, 227))
        draw_studio_pill(draw, cx, HEIGHT - 75, "HOUR 23:59: THE 24-HOUR CLOCK EXPIRES & OCEANS ROAR BACK!", banner_font, fill=(155, 89, 182))

    # -------------------------------------------------------------
    # SCENE 7: THE 2,000-FOOT TSUNAMI SURF & CELEBRATION OUTRO (3566 - 4110)
    # -------------------------------------------------------------
    else:
        t_loc = t_sec - 118.87
        # Brilliant bright tropical sky
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(129, 236, 236))

        # Colossal 2,000-foot dynamic blue curling wave
        wave_curl = int(math.sin(t_loc * 5.0) * 40)
        draw.chord([-300, HEIGHT * 0.15 + wave_curl, WIDTH + 300, HEIGHT + 800], start=180, end=360, fill=(9, 132, 227), outline=(40, 30, 30), width=6)
        # Giant foaming crest
        for fx in range(-100, WIDTH + 200, 90):
            fy = HEIGHT * 0.20 + int(math.sin(t_loc * 6.0 + fx) * 25)
            draw.ellipse([fx, fy, fx + 110, fy + 55], fill=(255, 255, 255))

        # Bob's Surfboard (Red & Golden Yellow)
        surf_x, surf_y = cx, HEIGHT * 0.40
        draw.ellipse([surf_x - 180, surf_y + 190, surf_x + 180, surf_y + 240], fill=(255, 71, 87), outline=(40, 30, 30), width=5)
        draw.line([(surf_x - 170, surf_y + 215), (surf_x + 170, surf_y + 215)], fill=(254, 202, 87), width=8)

        # Bob surfing in sunglasses and cheering
        draw_bob(draw, surf_x, surf_y, mood="sunglasses", t_sec=t_loc, pose="surfing")

        # Flying happy dolphins in wave spray
        dolph_x = int(cx + 380 + math.sin(t_loc * 4.0) * 40)
        dolph_y = int(HEIGHT * 0.30 + math.cos(t_loc * 4.0) * 30)
        draw.chord([dolph_x - 70, dolph_y - 40, dolph_x + 70, dolph_y + 40], start=180, end=360, fill=(52, 152, 219), outline=(40, 30, 30), width=3)

        draw_action_text(draw, cx, 180, "TSUNAMI SURFING HOME!", giant_font, fill=(255, 240, 80), stroke_fill=(30, 20, 20), stroke_width=12)

        # Badges & Outro
        draw_studio_pill(draw, cx, 80, "WHAT IF ALL OCEANS DRIED UP FOR 24 HOURS?", title_font, fill=(9, 132, 227))
        draw_studio_pill(draw, cx, HEIGHT - 75, "SUBSCRIBE TO BOB BIG QUESTIONS FOR MORE CURIOUS SCIENCE!", banner_font, fill=(46, 204, 113))

        # Channel CTA Badges
        draw_vector_bell(draw, cx - 440, HEIGHT - 75)
        draw_vector_thumbs_up(draw, cx + 440, HEIGHT - 75)

    # Apply screen shake offset if active
    if abs(shake_x) > 0 or abs(shake_y) > 0:
        shaken = Image.new("RGB", (WIDTH, HEIGHT), (10, 10, 15))
        shaken.paste(img, (shake_x, shake_y))
        img = shaken

    return img


def produce_ocean_dried_up_masterpiece():
    """Renders the full 2m 17s flagship masterpiece in Apple Silicon hardware."""
    logger.info("🎬 Rendering 2m 17s Flagship Masterpiece: 'What Happens If All Oceans Dried Up For 24 Hours?'...")

    voice_path = str(AUDIO_DIR / "full_voice_137s.m4a")
    music_path = str(AUDIO_DIR / "cartoon_music_137s.wav")

    voice_dur = get_audio_duration(voice_path)
    logger.info(f"🎤 Voiceover Duration: {voice_dur:.2f}s (~2m 17s)")
    logger.info(f"⏱️ Total Frames to Render: {TOTAL_FRAMES} @ {FPS}fps (Exactly 137.0 seconds)")

    title_font = get_font(size=46, font_type="rounded")
    banner_font = get_font(size=32, font_type="rounded")
    sub_font = get_font(size=26, font_type="rounded")
    giant_font = get_font(size=86, font_type="impact")

    ffmpeg_bin = get_ffmpeg_binary()
    hw = detect_hardware()

    final_output = EXPORTS_DIR / "What_If_Oceans_Dried_Up_2m17s.mp4"
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
    log_file_path = BASE_DIR / "ffmpeg_render_ocean.log"
    ffmpeg_log = open(log_file_path, "w")
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=ffmpeg_log, stderr=ffmpeg_log)

    t0 = time.time()
    for frame_idx in range(TOTAL_FRAMES):
        t_sec = frame_idx / float(FPS)
        frame_img = render_ocean_frame(frame_idx, TOTAL_FRAMES, t_sec, title_font, banner_font, sub_font, giant_font)
        try:
            process.stdin.write(frame_img.tobytes())
        except BrokenPipeError:
            logger.error("Broken pipe writing to FFmpeg!")
            break

        if frame_idx % 300 == 0:
            pct = int((frame_idx / TOTAL_FRAMES) * 100)
            logger.info(f"Rendering: {pct}% ({frame_idx}/{TOTAL_FRAMES} frames)")

    process.stdin.close()
    process.wait()
    ffmpeg_log.close()

    if process.returncode != 0:
        err_msg = ""
        if log_file_path.exists():
            err_msg = log_file_path.read_text()
        raise RuntimeError(f"FFmpeg failed with exit code {process.returncode}: {err_msg}")

    render_elapsed = time.time() - t0
    logger.success(f"🎉 2m 17s Render completed in {render_elapsed:.1f}s ({TOTAL_FRAMES / max(0.1, render_elapsed):.1f} fps)!")

    # High-CTR YouTube Viral Thumbnail (1280x720 16:9)
    logger.info("🖼️ Creating High-CTR YouTube Thumbnail...")
    cx, cy = WIDTH // 2, HEIGHT // 2
    thumb_path_jpg = THUMBNAILS_DIR / "Ocean_Dried_Up_Thumbnail.jpg"
    thumb_path_png = THUMBNAILS_DIR / "Ocean_Dried_Up_Thumbnail.png"
    thumb_img = Image.new("RGB", (WIDTH, HEIGHT), (20, 25, 45))
    draw_th = ImageDraw.Draw(thumb_img)

    # Split composition: Left is Dry Seabed Abyss with Sunken Ship / Right is Giant Approaching Tsunami
    draw_th.rectangle([0, 0, WIDTH // 2, HEIGHT], fill=(25, 30, 50))
    # Sunken Galleon on left
    draw_th.polygon([(200, HEIGHT * 0.70), (450, HEIGHT * 0.67), (430, HEIGHT * 0.85), (220, HEIGHT * 0.85)], fill=(120, 80, 50), outline=(20, 15, 10), width=4)
    draw_th.line([(320, HEIGHT * 0.70), (320, HEIGHT * 0.48)], fill=(90, 60, 40), width=8)

    # Right side: Roaring Tsunami Wall
    draw_th.rectangle([WIDTH // 2, 0, WIDTH, HEIGHT], fill=(9, 132, 227))
    for fx in range(WIDTH // 2, WIDTH + 100, 80):
        draw_th.ellipse([fx, HEIGHT * 0.25, fx + 100, HEIGHT * 0.40], fill=(255, 255, 255))

    # Center glowing neon divider
    draw_th.line([(WIDTH // 2, 0), (WIDTH // 2, HEIGHT)], fill=(255, 234, 167), width=12)

    # Bob in dead center in complete shock
    draw_bob(draw_th, WIDTH // 2, HEIGHT * 0.52, mood="shocked", t_sec=1.0, pose="standing")

    # Giant Comic Title (No box, clean drop shadow)
    thumb_font = get_font(size=84, font_type="impact")
    draw_action_text(draw_th, cx, 95, "WHAT IF ALL OCEANS DRIED UP?!", thumb_font, fill=(255, 240, 80), stroke_fill=(30, 20, 20), stroke_width=14)

    pill_font = get_font(size=46, font_type="rounded")
    draw_studio_pill(draw_th, cx, HEIGHT - 110, "350 QUINTILLION GALLONS GONE FOR 24 HOURS!", pill_font, fill=(255, 71, 87), text_fill=(255, 255, 255), pad_x=45, pad_y=16)

    thumb_final = thumb_img.resize((1280, 720), Image.Resampling.LANCZOS)
    thumb_final.save(str(thumb_path_jpg), "JPEG", quality=95)
    thumb_final.save(str(thumb_path_png), "PNG")

    info = get_video_info(str(final_output))
    logger.success("==================================================")
    logger.success("🎉 PRODUCTION-READY 2M 17S MASTERPIECE READY!")
    logger.success(f"📍 Video File: {final_output}")
    logger.success(f"⏱️ Runtime: {info.get('duration', 0):.1f} seconds (Target: 137.0s / 2m 17s)")
    logger.success(f"📐 Resolution: {info.get('width')}x{info.get('height')} 1080p Full HD")
    logger.success(f"🖼️ Thumbnail: {thumb_path_jpg}")
    logger.success("==================================================")

    return str(final_output), str(thumb_path_jpg)


if __name__ == "__main__":
    produce_ocean_dried_up_masterpiece()
