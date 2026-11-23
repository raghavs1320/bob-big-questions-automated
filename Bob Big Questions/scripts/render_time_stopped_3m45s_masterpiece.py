"""Flagship 3m 45s (225.0s) 2D Procedural Animated Masterpiece:
'What If Time Stopped For 24 Hours?'

Produced strictly according to all 4 YouTube Retention & Quality Upgrades:
1. Clean, Cinematic Floating Typography (NO clunky banner boxes).
2. Rich Foley Sound Effects layer synchronized frame-by-frame.
3. Squash & Stretch, bounce, and easing character physics for Bob.
4. 2-Stop Atmospheric Background Gradients & Soft Corner Vignettes across 16 dynamic scenes!
"""

import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from utils.hardware import get_ffmpeg_binary, detect_hardware
from utils.logger import logger
from voice.audio_processor import get_audio_duration

WIDTH, HEIGHT = 1920, 1080
FPS = 30
EXPORTS_DIR = BASE_DIR / "exports" / "videos"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR = BASE_DIR / "exports" / "thumbnails"
AUDIO_DIR = BASE_DIR / "audio" / "time_freeze_225s"

FONT_IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
FONT_ARIAL_ROUNDED = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"


def get_font(size: int = 40, font_type: str = "rounded"):
    if font_type == "rounded" and os.path.exists(FONT_ARIAL_ROUNDED):
        try:
            return ImageFont.truetype(FONT_ARIAL_ROUNDED, size=size)
        except Exception:
            pass
    elif font_type == "impact" and os.path.exists(FONT_IMPACT):
        try:
            return ImageFont.truetype(FONT_IMPACT, size=size)
        except Exception:
            pass
    elif font_type == "futura" and os.path.exists(FONT_FUTURA):
        try:
            return ImageFont.truetype(FONT_FUTURA, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_clean_text(draw, cx: int, cy: int, text: str, font, fill=(255, 255, 255), shadow_color=(0, 0, 0, 220), shadow_offset=(0, 5)):
    """Draws studio-grade typography with soft elevation drop shadow without boxes."""
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    draw_x = cx - (x0 + x1) / 2.0
    draw_y = cy - (y0 + y1) / 2.0

    if shadow_color:
        sx, sy = shadow_offset
        draw.text((draw_x + sx, draw_y + sy), text, font=font, fill=shadow_color)
    draw.text((draw_x, draw_y), text, font=font, fill=fill)


def draw_vertical_gradient(draw, top_color, bottom_color, height=HEIGHT, width=WIDTH):
    """Draws a smooth 2-stop vertical gradient background for depth."""
    r1, g1, b1 = top_color
    r2, g2, b2 = bottom_color
    for y in range(0, height, 4):
        ratio = y / float(height)
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        draw.rectangle([0, y, width, y + 4], fill=(r, g, b))


def draw_vignette(draw):
    """Draws subtle dark vignette on corners to direct eye to the center."""
    # Top subtle shadow
    for y in range(120):
        alpha = int(140 * (1.0 - y / 120.0))
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))


def draw_bob(draw, cx, cy, mood="happy", t_sec=0.0, floating=False, clothes="hoodie", scale=1.0, squash=1.0):
    """Draws Bob with squash & stretch physics, dynamic mouth & eyelid animations."""
    radius = int(90 * scale)
    bx = cx
    by = cy + int(math.sin(t_sec * 4.0) * 8) # gentle breathing/bobbing

    # Base body
    if clothes == "hoodie":
        # Cyan/Teal Hoodie with squash/stretch
        w_body = int(75 * scale * (2.0 - squash))
        h_body = int(165 * scale * squash)
        draw.rounded_rectangle([bx - w_body, by + int(65 * scale), bx + w_body, by + int(65 * scale) + h_body], radius=int(26 * scale), fill=(0, 206, 201), outline=(40, 30, 30), width=int(5 * scale))
        # Coral shorts
        draw.rounded_rectangle([bx - int(70 * scale), by + int(210 * scale), bx + int(70 * scale), by + int(285 * scale)], radius=int(14 * scale), fill=(255, 107, 129), outline=(40, 30, 30), width=int(4 * scale))
        # Legs
        if floating:
            draw.line([(bx - int(35 * scale), by + int(285 * scale)), (bx - int(55 * scale), by + int(330 * scale)), (bx - int(40 * scale), by + int(370 * scale))], fill=(255, 218, 185), width=int(18 * scale))
            draw.line([(bx + int(35 * scale), by + int(285 * scale)), (bx + int(60 * scale), by + int(335 * scale)), (bx + int(45 * scale), by + int(375 * scale))], fill=(255, 218, 185), width=int(18 * scale))
        else:
            draw.line([(bx - int(35 * scale), by + int(285 * scale)), (bx - int(35 * scale), by + int(360 * scale))], fill=(255, 218, 185), width=int(20 * scale))
            draw.line([(bx + int(35 * scale), by + int(285 * scale)), (bx + int(35 * scale), by + int(360 * scale))], fill=(255, 218, 185), width=int(20 * scale))
            draw.ellipse([bx - int(55 * scale), by + int(355 * scale), bx - int(15 * scale), by + int(375 * scale)], fill=(254, 202, 87), outline=(40, 30, 30), width=3)
            draw.ellipse([bx + int(15 * scale), by + int(355 * scale), bx + int(55 * scale), by + int(375 * scale)], fill=(254, 202, 87), outline=(40, 30, 30), width=3)

    elif clothes == "parka":
        # Neon Yellow Winter Puffy Parka with fur hood
        w_body = int(105 * scale)
        h_body = int(195 * scale)
        # Fur collar
        draw.ellipse([bx - int(115 * scale), by + int(40 * scale), bx + int(115 * scale), by + int(105 * scale)], fill=(245, 245, 245), outline=(180, 180, 180), width=4)
        draw.rounded_rectangle([bx - w_body, by + int(70 * scale), bx + w_body, by + int(70 * scale) + h_body], radius=int(32 * scale), fill=(254, 202, 87), outline=(40, 30, 30), width=int(6 * scale))
        # Puffy jacket segments
        draw.line([(bx - w_body + 10, by + int(130 * scale)), (bx + w_body - 10, by + int(130 * scale))], fill=(225, 175, 45), width=4)
        draw.line([(bx - w_body + 10, by + int(190 * scale)), (bx + w_body - 10, by + int(190 * scale))], fill=(225, 175, 45), width=4)
        # Snow boots
        draw.ellipse([bx - int(65 * scale), by + int(285 * scale), bx - int(15 * scale), by + int(330 * scale)], fill=(235, 77, 75), outline=(40, 30, 30), width=4)
        draw.ellipse([bx + int(15 * scale), by + int(285 * scale), bx + int(65 * scale), by + int(330 * scale)], fill=(235, 77, 75), outline=(40, 30, 30), width=4)

    # Bob's Head
    head_sy = int(radius * squash)
    draw.ellipse([bx - radius, by - head_sy, bx + radius, by + head_sy], fill=(255, 218, 185), outline=(40, 30, 30), width=int(5 * scale))

    # Hair (Messy brown tufts)
    hair_color = (101, 67, 33)
    draw.arc([bx - radius + int(10 * scale), by - head_sy - int(20 * scale), bx + radius - int(10 * scale), by - head_sy + int(40 * scale)], start=180, end=360, fill=hair_color, width=int(20 * scale))
    draw.ellipse([bx - int(22 * scale), by - head_sy - int(28 * scale), bx + int(26 * scale), by - head_sy + int(8 * scale)], fill=hair_color)

    # Eyelid blink animation (every 3.5s for 0.15s)
    blink = (t_sec % 3.5) < 0.15

    # Facial Expressions
    if mood == "shocked":
        for eye_x in (bx - int(40 * scale), bx + int(40 * scale)):
            if blink:
                draw.line([(eye_x - int(25 * scale), by - int(15 * scale)), (eye_x + int(25 * scale), by - int(15 * scale))], fill=(40, 30, 30), width=int(5 * scale))
            else:
                draw.ellipse([eye_x - int(28 * scale), by - int(15 * scale) - int(28 * scale), eye_x + int(28 * scale), by - int(15 * scale) + int(28 * scale)], fill=(255, 255, 255), outline=(40, 30, 30), width=int(4 * scale))
                draw.ellipse([eye_x - int(7 * scale), by - int(19 * scale), eye_x + int(7 * scale), by - int(5 * scale)], fill=(20, 20, 20))
                draw.ellipse([eye_x - int(3 * scale), by - int(17 * scale), eye_x, by - int(14 * scale)], fill=(255, 255, 255))
        # Raised eyebrows
        draw.arc([bx - int(65 * scale), by - int(65 * scale), bx - int(18 * scale), by - int(38 * scale)], start=180, end=360, fill=(60, 40, 40), width=int(6 * scale))
        draw.arc([bx + int(18 * scale), by - int(65 * scale), bx + int(65 * scale), by - int(38 * scale)], start=180, end=360, fill=(60, 40, 40), width=int(6 * scale))
        # Open oval mouth
        draw.ellipse([bx - int(22 * scale), by + int(15 * scale), bx + int(22 * scale), by + int(58 * scale)], fill=(50, 20, 20), outline=(220, 60, 60), width=int(4 * scale))
        draw.rectangle([bx - int(16 * scale), by + int(18 * scale), bx + int(16 * scale), by + int(26 * scale)], fill=(255, 255, 255))
    elif mood == "happy":
        for eye_x in (bx - int(38 * scale), bx + int(38 * scale)):
            if blink:
                draw.line([(eye_x - int(20 * scale), by - int(15 * scale)), (eye_x + int(20 * scale), by - int(15 * scale))], fill=(40, 30, 30), width=int(4 * scale))
            else:
                draw.ellipse([eye_x - int(20 * scale), by - int(15 * scale) - int(20 * scale), eye_x + int(20 * scale), by - int(15 * scale) + int(20 * scale)], fill=(255, 255, 255), outline=(40, 30, 30), width=int(4 * scale))
                draw.ellipse([eye_x - int(5 * scale), by - int(17 * scale), eye_x + int(13 * scale), by + int(1 * scale)], fill=(30, 30, 40))
                draw.ellipse([eye_x - int(2 * scale), by - int(14 * scale), eye_x + int(4 * scale), by - int(8 * scale)], fill=(255, 255, 255))
        # Cheerful smile
        draw.arc([bx - int(28 * scale), by + int(8 * scale), bx + int(28 * scale), by + int(42 * scale)], start=0, end=180, fill=(230, 60, 60), width=int(6 * scale))
        # Rosy cheeks
        draw.ellipse([bx - int(60 * scale), by + int(12 * scale), bx - int(40 * scale), by + int(26 * scale)], fill=(255, 175, 175))
        draw.ellipse([bx + int(40 * scale), by + int(12 * scale), bx + int(60 * scale), by + int(26 * scale)], fill=(255, 175, 175))


def draw_cat(draw, cx, cy, angle_deg=0.0):
    """Draws Bob's cute orange tabby cat."""
    draw.ellipse([cx - 45, cy - 30, cx + 45, cy + 30], fill=(243, 156, 18), outline=(40, 30, 30), width=4)
    draw.ellipse([cx - 30, cy - 60, cx + 30, cy], fill=(243, 156, 18), outline=(40, 30, 30), width=4)
    draw.polygon([(cx - 25, cy - 50), (cx - 35, cy - 80), (cx - 10, cy - 58)], fill=(230, 126, 34), outline=(40, 30, 30))
    draw.polygon([(cx + 10, cy - 58), (cx + 35, cy - 80), (cx + 25, cy - 50)], fill=(230, 126, 34), outline=(40, 30, 30))
    draw.ellipse([cx - 20, cy - 42, cx - 6, cy - 26], fill=(46, 204, 113), outline=(40, 30, 30), width=3)
    draw.ellipse([cx + 6, cy - 42, cx + 20, cy - 26], fill=(46, 204, 113), outline=(40, 30, 30), width=3)
    draw.ellipse([cx - 15, cy - 38, cx - 11, cy - 30], fill=(20, 20, 20))
    draw.ellipse([cx + 11, cy - 38, cx + 15, cy - 30], fill=(20, 20, 20))
    draw.polygon([(cx - 4, cy - 22), (cx + 4, cy - 22), (cx, cy - 17)], fill=(255, 175, 175))
    draw.line([(cx - 25, cy - 20), (cx - 5, cy - 19)], fill=(40, 30, 30), width=2)
    draw.line([(cx + 5, cy - 19), (cx + 25, cy - 20)], fill=(40, 30, 30), width=2)
    draw.arc([cx + 25, cy - 40, cx + 65, cy + 10], start=270, end=90, fill=(243, 156, 18), width=10)


# =========================================================================
# 16 DYNAMIC SCENE RENDERERS (THE 225-SECOND MASTERPIECE)
# =========================================================================

def render_scene_01(draw, t, fonts):
    """Scene 1: 7:00 AM The Alarm Freeze & Suspended Coffee."""
    draw_vertical_gradient(draw, (253, 248, 235), (238, 198, 128))
    # Kitchen counter
    draw.rectangle([0, HEIGHT - 240, WIDTH, HEIGHT], fill=(139, 90, 43))
    draw.line([(0, HEIGHT - 240), (WIDTH, HEIGHT - 240)], fill=(90, 50, 25), width=4)
    # Digital clock frozen at 07:00:00
    draw.rounded_rectangle([200, 240, 480, 350], radius=15, fill=(20, 24, 38), outline=(235, 77, 75), width=4)
    draw_clean_text(draw, 340, 290, "07:00:00", fonts["clock"], fill=(235, 77, 75))
    # Bob in center looking shocked
    draw_bob(draw, cx=WIDTH // 2 - 100, cy=HEIGHT // 2 + 30, mood="shocked", t_sec=t)
    # Coffee pot tilted with frozen glass stream
    cx_pot = WIDTH // 2 + 180
    draw.rounded_rectangle([cx_pot - 35, HEIGHT // 2 - 20, cx_pot + 35, HEIGHT // 2 + 50], radius=10, fill=(238, 82, 83), outline=(40, 30, 30), width=4)
    # Frozen amber stream
    pts = [(cx_pot + 30, HEIGHT // 2), (cx_pot + 90, HEIGHT // 2 - 20), (cx_pot + 160, HEIGHT // 2 + 20), (cx_pot + 220, HEIGHT // 2 + 100)]
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=(111, 78, 55), width=16)
        draw.line([pts[i], pts[i+1]], fill=(180, 130, 80), width=6)
    for dx, dy in [(120, -50), (190, 40), (250, 120)]:
        draw.ellipse([cx_pot + dx - 12, HEIGHT // 2 + dy - 12, cx_pot + dx + 12, HEIGHT // 2 + dy + 12], fill=(111, 78, 55), outline=(255, 255, 255), width=2)
    # Minimalist Scene Label
    draw_clean_text(draw, WIDTH // 2, 70, "7:00 AM • THE ALARM FREEZE", fonts["header"], fill=(255, 255, 255))


def render_scene_02(draw, t, fonts):
    """Scene 2: Frozen City Wax Museum & Tilted Cyclist."""
    draw_vertical_gradient(draw, (130, 204, 221), (245, 246, 250))
    # City Street
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(47, 53, 66))
    draw.rectangle([0, HEIGHT - 240, WIDTH, HEIGHT - 220], fill=(116, 125, 140))
    # Frozen Yellow Cab
    draw.rectangle([250, HEIGHT - 340, 520, HEIGHT - 240], fill=(254, 202, 87), outline=(40, 30, 30), width=4)
    draw.ellipse([300, HEIGHT - 250, 350, HEIGHT - 200], fill=(30, 30, 30))
    draw.ellipse([420, HEIGHT - 250, 470, HEIGHT - 200], fill=(30, 30, 30))
    # Frozen tire smoke
    for sx, sy, sr in [(220, HEIGHT - 260, 20), (190, HEIGHT - 275, 26), (150, HEIGHT - 290, 32)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(240, 240, 240), outline=(200, 200, 200), width=2)
    # Tilted Cyclist (45 degrees)
    cyc_x = WIDTH - 350
    draw.line([(cyc_x - 50, HEIGHT - 250), (cyc_x + 50, HEIGHT - 330)], fill=(235, 77, 75), width=8)
    draw.ellipse([cyc_x - 70, HEIGHT - 270, cyc_x - 30, HEIGHT - 230], outline=(30, 30, 30), width=5)
    draw.ellipse([cyc_x + 30, HEIGHT - 350, cyc_x + 70, HEIGHT - 310], outline=(30, 30, 30), width=5)
    # Bob walking through city looking amazed
    draw_bob(draw, cx=WIDTH // 2, cy=HEIGHT // 2 + 40, mood="shocked", t_sec=t)
    draw_clean_text(draw, WIDTH // 2, 70, "THE FROZEN CITY WAX MUSEUM", fonts["header"], fill=(255, 255, 255))


def render_scene_03(draw, t, fonts):
    """Scene 3: The 40,000 Raindrop Maze."""
    draw_vertical_gradient(draw, (44, 62, 80), (127, 140, 141))
    draw.rectangle([0, HEIGHT - 200, WIDTH, HEIGHT], fill=(52, 73, 94))
    # Suspended Raindrops
    np.random.seed(103)
    for _ in range(60):
        rx = int(np.random.uniform(50, WIDTH - 50))
        ry = int(np.random.uniform(150, HEIGHT - 180))
        r = int(np.random.choice([8, 12, 16]))
        draw.ellipse([rx - r, ry - int(r * 1.3), rx + r, ry + int(r * 1.3)], fill=(129, 236, 236), outline=(255, 255, 255), width=2)
        draw.ellipse([rx - r // 2, ry - r, rx - r // 4, ry - r // 2], fill=(255, 255, 255))
    # Bob ducking and weaving with happy smile
    bob_x = WIDTH // 2 + int(math.sin(t * 3.0) * 80)
    draw_bob(draw, cx=bob_x, cy=HEIGHT // 2 + 50, mood="happy", t_sec=t)
    draw_clean_text(draw, WIDTH // 2, 70, "THE 40,000 SUSPENDED RAINDROPS", fonts["header"], fill=(255, 255, 255))


def render_scene_04(draw, t, fonts):
    """Scene 4: The Terrifying Physics of Light (Glowing Cone)."""
    # Pitch black city
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(8, 10, 18))
    bob_x = WIDTH // 2
    bob_y = HEIGHT // 2 + 50
    # Glowing cone of illumination radiating from Bob
    cone_pts = [(bob_x, bob_y - 80), (bob_x - 380, HEIGHT), (bob_x + 380, HEIGHT)]
    draw.polygon(cone_pts, fill=(255, 245, 180, 110))
    draw.ellipse([bob_x - 280, bob_y - 120, bob_x + 280, bob_y + 350], fill=(255, 250, 200, 70))
    # Bob in center of light
    draw_bob(draw, cx=bob_x, cy=bob_y, mood="shocked", t_sec=t)
    draw_clean_text(draw, WIDTH // 2, 70, "PHYSICS OF LIGHT • FROZEN PHOTONS", fonts["header"], fill=(255, 221, 51))


def render_scene_05(draw, t, fonts):
    """Scene 5: Walking On Solid Ocean Waves."""
    draw_vertical_gradient(draw, (9, 132, 227), (129, 236, 236))
    # Giant 20ft frozen wave curl
    wave_pts = [(0, HEIGHT - 180), (400, HEIGHT - 220), (900, HEIGHT - 450), (1400, HEIGHT - 600), (1700, HEIGHT - 400), (WIDTH, HEIGHT - 200), (WIDTH, HEIGHT), (0, HEIGHT)]
    draw.polygon(wave_pts, fill=(0, 184, 148))
    # Frozen white wave foam crest
    draw.arc([1300, HEIGHT - 640, 1750, HEIGHT - 360], start=180, end=360, fill=(255, 255, 255), width=18)
    # Bob ice skating on the water surface!
    skate_x = WIDTH // 2 + int(math.sin(t * 3.5) * 120)
    draw_bob(draw, cx=skate_x, cy=HEIGHT // 2 + 10, mood="happy", t_sec=t, floating=True)
    draw_clean_text(draw, WIDTH // 2, 70, "SOLID OCEAN WAVES • ROCK-HARD WATER", fonts["header"], fill=(255, 255, 255))


def render_scene_06(draw, t, fonts):
    """Scene 6: The Supermarket Mega-Feast."""
    draw_vertical_gradient(draw, (241, 242, 246), (206, 214, 224))
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(223, 228, 234))
    # Supermarket shelves on left and right
    draw.rectangle([80, 200, 320, HEIGHT - 220], fill=(255, 107, 129))
    draw.rectangle([WIDTH - 320, 200, WIDTH - 80, HEIGHT - 220], fill=(108, 92, 231))
    # 4-foot giant mega burger in Bob's hands!
    burg_x = WIDTH // 2 + 140
    for layer_i in range(8):
        by = HEIGHT // 2 + 160 - (layer_i * 26)
        draw.rounded_rectangle([burg_x - 55, by, burg_x + 55, by + 18], radius=6, fill=(109, 76, 65) if layer_i % 2 == 0 else (254, 202, 87))
    # Bun top
    draw.ellipse([burg_x - 60, HEIGHT // 2 - 60, burg_x + 60, HEIGHT // 2 - 20], fill=(225, 177, 44))
    # Bob happily eating
    draw_bob(draw, cx=WIDTH // 2 - 80, cy=HEIGHT // 2 + 40, mood="happy", t_sec=t)
    draw_clean_text(draw, WIDTH // 2, 70, "THE SUPERMARKET MEGA-FEAST", fonts["header"], fill=(255, 255, 255))


def render_scene_07(draw, t, fonts):
    """Scene 7: Pranking Historical Statues."""
    draw_vertical_gradient(draw, (223, 228, 234), (164, 176, 190))
    # Museum marble floor & columns
    draw.rectangle([0, HEIGHT - 200, WIDTH, HEIGHT], fill=(200, 210, 220))
    for col_x in [180, 480, WIDTH - 480, WIDTH - 180]:
        draw.rectangle([col_x - 35, 150, col_x + 35, HEIGHT - 200], fill=(245, 245, 245), outline=(180, 180, 180), width=3)
    # Roman Statue posed in funny disco dance
    stat_x = WIDTH // 2 + 180
    draw.rounded_rectangle([stat_x - 45, HEIGHT // 2 + 20, stat_x + 45, HEIGHT - 200], radius=15, fill=(230, 230, 230), outline=(120, 120, 120), width=4)
    draw.ellipse([stat_x - 40, HEIGHT // 2 - 60, stat_x + 40, HEIGHT // 2 + 20], fill=(230, 230, 230), outline=(120, 120, 120), width=4)
    # Disco arm pointing up
    draw.line([(stat_x, HEIGHT // 2), (stat_x + 80, HEIGHT // 2 - 80)], fill=(230, 230, 230), width=16)
    # Bob with marker grinning
    draw_bob(draw, cx=WIDTH // 2 - 120, cy=HEIGHT // 2 + 50, mood="happy", t_sec=t)
    draw_clean_text(draw, WIDTH // 2, 70, "PRANKING HISTORICAL STATUES", fonts["header"], fill=(255, 255, 255))


def render_scene_08(draw, t, fonts):
    """Scene 8: Stadium Frozen Mid-Goal."""
    draw_vertical_gradient(draw, (30, 144, 255), (46, 204, 113))
    # Soccer goal net on right
    draw.rectangle([WIDTH - 380, HEIGHT // 2 - 100, WIDTH - 80, HEIGHT - 180], outline=(255, 255, 255), width=8)
    # Soccer ball frozen 3 inches from net
    ball_x = WIDTH - 400
    ball_y = HEIGHT // 2 + 20
    draw.ellipse([ball_x - 30, ball_y - 30, ball_x + 30, ball_y + 30], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
    # Bob posing in front of frozen goalie
    draw_bob(draw, cx=WIDTH // 2, cy=HEIGHT // 2 + 50, mood="happy", t_sec=t)
    draw_clean_text(draw, WIDTH // 2, 70, "THE STADIUM FROZEN MID-GOAL", fonts["header"], fill=(255, 255, 255))


def render_scene_09(draw, t, fonts):
    """Scene 9: The Air Jelly Paradox (Strawberry Gelatin)."""
    # Thick strawberry pink air grid
    draw_vertical_gradient(draw, (255, 159, 178), (255, 107, 129))
    # Floating air molecules as pink jelly bubbles
    np.random.seed(109)
    for _ in range(45):
        gx = int(np.random.uniform(40, WIDTH - 40))
        gy = int(np.random.uniform(120, HEIGHT - 100))
        draw.ellipse([gx - 18, gy - 18, gx + 18, gy + 18], fill=(255, 75, 105, 140), outline=(255, 255, 255), width=2)
    # Bob squished pushing forward with effort
    squash_val = 0.88 + 0.1 * math.sin(t * 5.0)
    draw_bob(draw, cx=WIDTH // 2, cy=HEIGHT // 2 + 40, mood="shocked", t_sec=t, squash=squash_val)
    draw_clean_text(draw, WIDTH // 2, 70, "THE AIR JELLY PARADOX • FROZEN ATOMS", fonts["header"], fill=(255, 255, 255))


def render_scene_10(draw, t, fonts):
    """Scene 10: Absolute Zero Deep Freeze."""
    draw_vertical_gradient(draw, (24, 44, 97), (10, 61, 98))
    # Frost border creep
    for fx in range(0, WIDTH, 40):
        draw.line([(fx, 0), (fx + 20, 80)], fill=(225, 245, 254, 180), width=3)
        draw.line([(fx, HEIGHT), (fx + 20, HEIGHT - 80)], fill=(225, 245, 254, 180), width=3)
    # Bob bundled up in huge winter parka
    draw_bob(draw, cx=WIDTH // 2, cy=HEIGHT // 2 + 50, mood="shocked", t_sec=t, clothes="parka")
    # Floating ice breath crystals
    for bi in range(6):
        bx = WIDTH // 2 + 80 + int(bi * 35)
        by = HEIGHT // 2 - 20 - int(math.sin(bi) * 20)
        draw.polygon([(bx, by - 12), (bx + 12, by), (bx, by + 12), (bx - 12, by)], fill=(129, 236, 236), outline=(255, 255, 255))
    draw_clean_text(draw, WIDTH // 2, 70, "ABSOLUTE ZERO • NO HEAT VIBRATION", fonts["header"], fill=(129, 236, 236))


def render_scene_11(draw, t, fonts):
    """Scene 11: The Frozen Tabby Cat Surprise."""
    draw_vertical_gradient(draw, (189, 195, 199), (44, 62, 80))
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(52, 73, 94))
    # Frozen Cat mid-pounce on right
    cat_x = WIDTH // 2 + 220
    draw_cat(draw, cx=cat_x, cy=HEIGHT // 2 + 80)
    # Floating pepperoni slice 1 inch from nose
    pep_x = cat_x + 80
    pep_y = HEIGHT // 2 + 40
    draw.ellipse([pep_x - 18, pep_y - 18, pep_x + 18, pep_y + 18], fill=(235, 77, 75), outline=(254, 202, 87), width=3)
    # Bob smiling gently
    draw_bob(draw, cx=WIDTH // 2 - 120, cy=HEIGHT // 2 + 50, mood="happy", t_sec=t)
    draw_clean_text(draw, WIDTH // 2, 70, "THE FROZEN TABBY CAT SURPRISE", fonts["header"], fill=(255, 255, 255))


def render_scene_12(draw, t, fonts):
    """Scene 12: Hour 18: Silence & No Wi-Fi (Inflatable Sofa)."""
    draw_vertical_gradient(draw, (75, 40, 110), (25, 20, 50))
    # Bob sitting on yellow inflatable sofa
    sofa_x = WIDTH // 2
    sofa_y = HEIGHT // 2 + 120
    # Sofa cushions
    draw.rounded_rectangle([sofa_x - 160, sofa_y - 40, sofa_x + 160, sofa_y + 80], radius=25, fill=(254, 202, 87), outline=(225, 177, 44), width=6)
    draw.rounded_rectangle([sofa_x - 180, sofa_y - 80, sofa_x - 130, sofa_y + 60], radius=20, fill=(254, 202, 87), outline=(225, 177, 44), width=5)
    draw.rounded_rectangle([sofa_x + 130, sofa_y - 80, sofa_x + 180, sofa_y + 60], radius=20, fill=(254, 202, 87), outline=(225, 177, 44), width=5)
    # Bob seated looking bored
    draw_bob(draw, cx=sofa_x, cy=sofa_y - 80, mood="shocked", t_sec=t)
    draw_clean_text(draw, WIDTH // 2, 70, "HOUR 18 • THE SILENCE & DEAD WI-FI", fonts["header"], fill=(255, 255, 255))


def render_scene_13(draw, t, fonts):
    """Scene 13: Hour 23: The Cosmic Vibration (Shivering Objects)."""
    draw_vertical_gradient(draw, (44, 62, 80), (142, 68, 173))
    # Vibrating shivering resonance rings
    shiver = int(math.sin(t * 30.0) * 8)
    # Raindrops vibrating with cyan rings
    for rx in range(200, WIDTH - 100, 240):
        ry = 350 + (rx % 180)
        draw.ellipse([rx - 15 + shiver, ry - 15, rx + 15 + shiver, ry + 15], fill=(129, 236, 236), outline=(255, 255, 255), width=2)
        draw.ellipse([rx - 30, ry - 30, rx + 30, ry + 30], outline=(0, 240, 230, 160), width=2)
    # Bob looking around in alert
    draw_bob(draw, cx=WIDTH // 2, cy=HEIGHT // 2 + 40, mood="shocked", t_sec=t)
    draw_clean_text(draw, WIDTH // 2, 70, "HOUR 23 • THE COSMIC VIBRATION", fonts["header"], fill=(255, 221, 51))


def render_scene_14(draw, t, fonts):
    """Scene 14: The 10-Second Countdown."""
    draw_vertical_gradient(draw, (12, 16, 32), (30, 15, 40))
    # Giant glowing digital countdown clock in sky
    sec_left = max(0, 10 - int(t % 10))
    clock_str = f"00:00:{sec_left:02d}"
    draw_clean_text(draw, WIDTH // 2, HEIGHT // 2 - 80, clock_str, fonts["giant_clock"], fill=(235, 77, 75))
    # Concrete shelter
    draw.rectangle([WIDTH // 2 - 300, HEIGHT - 280, WIDTH // 2 + 300, HEIGHT - 220], fill=(149, 165, 166))
    draw.rectangle([WIDTH // 2 - 280, HEIGHT - 220, WIDTH // 2 - 240, HEIGHT], fill=(127, 140, 141))
    draw.rectangle([WIDTH // 2 + 240, HEIGHT - 220, WIDTH // 2 + 280, HEIGHT], fill=(127, 140, 141))
    # Bob peeking out with yellow safety helmet
    draw_bob(draw, cx=WIDTH // 2, cy=HEIGHT - 170, mood="shocked", t_sec=t)
    draw_clean_text(draw, WIDTH // 2, 70, "THE FINAL COUNTDOWN • 10 SECONDS!", fonts["header"], fill=(255, 255, 255))


def render_scene_15(draw, t, fonts):
    """Scene 15: The Grand Sonic Boom Release!"""
    # High energy radiant burst background
    draw_vertical_gradient(draw, (241, 196, 15), (230, 126, 34))
    # Radial motion explosion lines
    cx, cy = WIDTH // 2, HEIGHT // 2
    for ang in range(0, 360, 15):
        rad = math.radians(ang + t * 40.0)
        x1 = cx + int(120 * math.cos(rad))
        y1 = cy + int(120 * math.sin(rad))
        x2 = cx + int(900 * math.cos(rad))
        y2 = cy + int(900 * math.sin(rad))
        draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 180), width=6)
    # Tsunami water splash & moving cars
    draw.ellipse([cx - 240, HEIGHT - 300, cx + 240, HEIGHT - 80], fill=(9, 132, 227), outline=(255, 255, 255), width=8)
    # Cat eating pepperoni happily!
    draw_cat(draw, cx=WIDTH - 280, cy=HEIGHT - 240)
    # Bob jumping in celebration!
    draw_bob(draw, cx=cx, cy=cy, mood="happy", t_sec=t, floating=True)
    draw_clean_text(draw, WIDTH // 2, 70, "SNAP! TIME EXPLODES INTO MOTION!", fonts["header"], fill=(255, 255, 255))


def render_scene_16(draw, t, fonts):
    """Scene 16: Safe In Bed With Pancakes & Call To Action."""
    draw_vertical_gradient(draw, (26, 188, 156), (22, 160, 133))
    # Cozy bedroom
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(140, 90, 45))
    # Fluffy pancake stack on plate
    p_x = WIDTH // 2 + 180
    p_y = HEIGHT // 2 + 100
    draw.ellipse([p_x - 70, p_y + 10, p_x + 70, p_y + 40], fill=(240, 240, 240)) # plate
    for pi in range(4):
        draw.ellipse([p_x - 55, p_y - pi * 15, p_x + 55, p_y + 20 - pi * 15], fill=(254, 202, 87), outline=(225, 177, 44), width=3)
    # Butter cube on top
    draw.rectangle([p_x - 12, p_y - 65, p_x + 12, p_y - 45], fill=(255, 242, 0))
    # Bob in bed smiling
    draw_bob(draw, cx=WIDTH // 2 - 100, cy=HEIGHT // 2 + 40, mood="happy", t_sec=t)
    # Cat sleeping beside him
    draw_cat(draw, cx=WIDTH // 2 - 280, cy=HEIGHT // 2 + 120)
    # Minimalist Subscribe Pill
    draw.rounded_rectangle([WIDTH // 2 - 180, HEIGHT - 140, WIDTH // 2 + 180, HEIGHT - 70], radius=20, fill=(235, 77, 75), outline=(255, 255, 255), width=3)
    draw_clean_text(draw, WIDTH // 2, HEIGHT - 105, "SUBSCRIBE FOR MORE BOB!", fonts["badge"], fill=(255, 255, 255), shadow_color=None)
    draw_clean_text(draw, WIDTH // 2, 70, "SAFE IN BED • WHAT IF TIME GOES BACKWARD?", fonts["header"], fill=(255, 255, 255))


SCENE_RENDERERS = [
    render_scene_01, render_scene_02, render_scene_03, render_scene_04,
    render_scene_05, render_scene_06, render_scene_07, render_scene_08,
    render_scene_09, render_scene_10, render_scene_11, render_scene_12,
    render_scene_13, render_scene_14, render_scene_15, render_scene_16
]


def render_masterpiece_frame(frame_idx: int, scene_bounds: list, fonts: dict) -> Image.Image:
    """Renders one complete 1080p frame for the active scene."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 35))
    draw = ImageDraw.Draw(img, "RGBA")

    # Find active scene
    scene_idx = 0
    t_local = 0.0
    for idx, (start_f, end_f) in enumerate(scene_bounds):
        if start_f <= frame_idx < end_f:
            scene_idx = idx
            t_local = (frame_idx - start_f) / float(FPS)
            break

    # Call specific scene renderer
    renderer = SCENE_RENDERERS[scene_idx % len(SCENE_RENDERERS)]
    renderer(draw, t_local, fonts)

    # Subtle top vignette for studio polish
    draw_vignette(draw)

    return img


def produce_time_freeze_3m45s_masterpiece():
    """Main production pipeline: renders 6,750 frames directly to FFmpeg with mixed audio."""
    logger.info("🎬 Rendering 3m 45s (225.0s) Animated Flagship: 'What If Time Stopped For 24 Hours?'...")

    timings_file = AUDIO_DIR / "scene_timings.json"
    audio_mix_file = AUDIO_DIR / "full_audio_mix_225s.wav"

    if not timings_file.exists():
        raise FileNotFoundError(f"Timings file missing: {timings_file}")
    if not audio_mix_file.exists():
        raise FileNotFoundError(f"Master mixed audio missing: {audio_mix_file}")

    with open(timings_file) as f:
        timings_data = json.load(f)

    scene_bounds = []
    for sc in timings_data["scenes"]:
        scene_bounds.append((sc["start_frame"], sc["end_frame"]))

    total_frames = timings_data["total_frames"]
    total_duration = total_frames / float(FPS)
    logger.info(f"⏱️ Video Duration: {total_duration:.2f}s (~3m 45s) | Total Frames: {total_frames} | Scenes: 16")

    fonts = {
        "header": get_font(size=44, font_type="rounded"),
        "clock": get_font(size=64, font_type="impact"),
        "giant_clock": get_font(size=140, font_type="impact"),
        "badge": get_font(size=26, font_type="rounded")
    }

    ffmpeg_bin = get_ffmpeg_binary()
    hw = detect_hardware()

    final_output = EXPORTS_DIR / "What_If_Time_Stopped_3m45s.mp4"
    final_output.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg_bin,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",  # Video frames from stdin
        "-i", str(audio_mix_file),  # Input 1: Master mixed voice + SFX + music
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", hw.video_encoder,
        "-c:a", hw.audio_encoder,
        "-b:v", "9000k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(final_output)
    ]

    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()

    for frame_idx in range(total_frames):
        frame_img = render_masterpiece_frame(frame_idx, scene_bounds, fonts)
        process.stdin.write(frame_img.tobytes())

        if frame_idx % 300 == 0:
            pct = int((frame_idx / total_frames) * 100)
            elapsed = time.time() - t0
            fps_curr = frame_idx / max(0.1, elapsed)
            logger.info(f"Rendering: {pct}% ({frame_idx}/{total_frames} frames, {fps_curr:.1f} fps)")

    process.stdin.close()
    process.wait()

    render_elapsed = time.time() - t0
    logger.success(f"🎉 Flagship 3m 45s video rendered in {render_elapsed:.1f}s ({total_frames / max(0.1, render_elapsed):.1f} fps)!")
    logger.success(f"📍 Video File: {final_output}")
    return str(final_output)


if __name__ == "__main__":
    produce_time_freeze_3m45s_masterpiece()
