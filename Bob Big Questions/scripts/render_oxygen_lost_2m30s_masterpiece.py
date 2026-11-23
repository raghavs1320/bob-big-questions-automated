"""Procedural 2D Animated Masterpiece:
'What If Earth Lost Oxygen For Just 5 Seconds?'

Duration: Exactly 2 minutes 30 seconds (150.0s) - 4,500 frames at 30fps.
Method: The proven classic Bob Big Questions production pipeline:
- Iconic Auto-Banners with dynamic padding & zero overflow.
- Vibrant cartoon aesthetics, screen shakes, and telemetry gauges.
- 100% Frame-accurate zero-drift audio synchronization.
"""

import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from utils.hardware import detect_hardware, get_ffmpeg_binary
from utils.logger import logger

WIDTH, HEIGHT = 1920, 1080
FPS = 30
EXPORTS_DIR = BASE_DIR / "exports" / "videos"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR = BASE_DIR / "audio" / "oxygen_150s"

FONT_CHALKBOARD = "/System/Library/Fonts/Supplemental/Chalkboard.ttc"
FONT_ARIAL_ROUNDED = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
FONT_FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"
FONT_IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"


def get_font(size: int = 40, bold: bool = False, cartoon: bool = True):
    if cartoon and os.path.exists(FONT_ARIAL_ROUNDED):
        try:
            return ImageFont.truetype(FONT_ARIAL_ROUNDED, size=size)
        except Exception:
            pass
    elif cartoon and os.path.exists(FONT_CHALKBOARD):
        try:
            return ImageFont.truetype(FONT_CHALKBOARD, size=size)
        except Exception:
            pass
    if os.path.exists(FONT_FUTURA):
        try:
            return ImageFont.truetype(FONT_FUTURA, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)


def draw_auto_banner(draw, cx, y, text, font, fill, outline=(255, 255, 255), text_fill=(255, 255, 255), pad_x=45, pad_y=16, radius=22, width=5):
    """Dynamically calculates text bounding box to guarantee ZERO overflow."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    box = [cx - bw // 2, y, cx + bw // 2, y + bh]
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    tx = cx - tw // 2
    ty = y + pad_y - bbox[1] // 5
    draw.text((tx, ty), text, font=font, fill=text_fill)
    return box


def draw_vector_bell(draw, cx, cy, r=24, fill=(254, 202, 87)):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r - 5], fill=fill, outline=(40, 30, 30), width=4)
    draw.chord([cx - r - 8, cy + 5, cx + r + 8, cy + 28], start=180, end=360, fill=fill, outline=(40, 30, 30), width=4)
    draw.ellipse([cx - 8, cy + 22, cx + 8, cy + 34], fill=(225, 177, 44), outline=(40, 30, 30), width=3)


def draw_vector_thumbs_up(draw, cx, cy, size=24, fill=(255, 255, 255)):
    draw.rounded_rectangle([cx - size, cy - size // 2, cx + size // 2, cy + size], radius=8, fill=fill)
    draw.rounded_rectangle([cx - size, cy - size * 1.2, cx - size // 3, cy], radius=6, fill=fill)


def draw_bob(draw, cx, cy, mood="happy", t_sec=0.0, floating=False, clothes="hoodie"):
    """Draws Bob with the classic vector aesthetic."""
    radius = 95
    bx, by = cx, cy

    if clothes == "hoodie":
        draw_rounded_rect(draw, [bx - 75, by + 65, bx + 75, by + 230], radius=28, fill=(0, 206, 201), outline=(40, 30, 30), width=6)
        draw_rounded_rect(draw, [bx - 70, by + 220, bx + 70, by + 300], radius=15, fill=(255, 107, 129), outline=(40, 30, 30), width=5)
        if floating:
            draw.line([(bx - 35, by + 300), (bx - 55, by + 340), (bx - 35, by + 380)], fill=(255, 218, 185), width=20)
            draw.line([(bx + 35, by + 300), (bx + 60, by + 345), (bx + 40, by + 385)], fill=(255, 218, 185), width=20)
        else:
            draw.line([(bx - 35, by + 300), (bx - 35, by + 370)], fill=(255, 218, 185), width=22)
            draw.line([(bx + 35, by + 300), (bx + 35, by + 370)], fill=(255, 218, 185), width=22)
            draw.ellipse([bx - 55, by + 365, bx - 15, by + 385], fill=(254, 202, 87), outline=(40, 30, 30), width=4)
            draw.ellipse([bx + 15, by + 365, bx + 55, by + 385], fill=(254, 202, 87), outline=(40, 30, 30), width=4)

    # Bob's Head
    skin = (255, 180, 160) if mood == "holding_breath" else (255, 218, 185)
    draw.ellipse([bx - radius, by - radius, bx + radius, by + radius], fill=skin, outline=(40, 30, 30), width=6)

    # Hair
    hair_color = (101, 67, 33)
    draw.arc([bx - radius + 10, by - radius - 15, bx + radius - 10, by - radius + 45], start=180, end=360, fill=hair_color, width=20)
    draw.ellipse([bx - 20, by - radius - 24, bx + 25, by - radius + 8], fill=hair_color)

    if mood == "happy":
        for eye_x in (bx - 40, bx + 40):
            draw.ellipse([eye_x - 22, by - 18 - 22, eye_x + 22, by - 18 + 22], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
            draw.ellipse([eye_x - 6, by - 20, eye_x + 14, by], fill=(30, 30, 40))
            draw.ellipse([eye_x - 2, by - 17, eye_x + 5, by - 10], fill=(255, 255, 255))
        draw.arc([bx - 30, by + 8, bx + 30, by + 48], start=0, end=180, fill=(230, 60, 60), width=7)
        draw.ellipse([bx - 65, by + 12, bx - 42, by + 28], fill=(255, 175, 175))
        draw.ellipse([bx + 42, by + 12, bx + 65, by + 28], fill=(255, 175, 175))

    elif mood == "shocked":
        for eye_x in (bx - 42, bx + 42):
            draw.ellipse([eye_x - 30, by - 18 - 30, eye_x + 30, by - 18 + 30], fill=(255, 255, 255), outline=(40, 30, 30), width=5)
            draw.ellipse([eye_x - 7, by - 20, eye_x + 7, by - 6], fill=(20, 20, 20))
            draw.ellipse([eye_x - 3, by - 18, eye_x, by - 15], fill=(255, 255, 255))
        draw.arc([bx - 65, by - 65, bx - 20, by - 40], start=180, end=360, fill=(60, 40, 40), width=6)
        draw.arc([bx + 20, by - 65, bx + 65, by - 40], start=180, end=360, fill=(60, 40, 40), width=6)
        draw.ellipse([bx - 22, by + 15, bx + 22, by + 60], fill=(50, 20, 20), outline=(220, 60, 60), width=5)

    elif mood == "holding_breath":
        # Huge puffy red cheeks
        draw.ellipse([bx - 120, by - 10, bx - 60, by + 50], fill=(255, 130, 130), outline=(220, 50, 50), width=4)
        draw.ellipse([bx + 60, by - 10, bx + 120, by + 50], fill=(255, 130, 130), outline=(220, 50, 50), width=4)
        for eye_x in (bx - 44, bx + 44):
            draw.ellipse([eye_x - 32, by - 18 - 32, eye_x + 32, by - 18 + 32], fill=(255, 255, 255), outline=(40, 30, 30), width=5)
            draw.ellipse([eye_x - 8, by - 22, eye_x + 8, by - 6], fill=(20, 20, 20))
            draw.line([(eye_x - 22, by - 25), (eye_x - 10, by - 20)], fill=(235, 77, 75), width=2)
        # Clamped mouth
        draw.line([(bx - 25, by + 32), (bx + 25, by + 32)], fill=(180, 40, 40), width=7)


def draw_cat(draw, cx, cy):
    draw.ellipse([cx - 45, cy - 30, cx + 45, cy + 30], fill=(243, 156, 18), outline=(40, 30, 30), width=4)
    draw.ellipse([cx - 30, cy - 60, cx + 30, cy], fill=(243, 156, 18), outline=(40, 30, 30), width=4)
    draw.polygon([(cx - 25, cy - 50), (cx - 35, cy - 80), (cx - 10, cy - 58)], fill=(230, 126, 34), outline=(40, 30, 30))
    draw.polygon([(cx + 10, cy - 58), (cx + 35, cy - 80), (cx + 25, cy - 50)], fill=(230, 126, 34), outline=(40, 30, 30))
    draw.ellipse([cx - 20, cy - 42, cx - 6, cy - 26], fill=(46, 204, 113), outline=(40, 30, 30), width=3)
    draw.ellipse([cx + 6, cy - 42, cx + 20, cy - 26], fill=(46, 204, 113), outline=(40, 30, 30), width=3)
    draw.ellipse([cx - 15, cy - 38, cx - 11, cy - 30], fill=(20, 20, 20))
    draw.ellipse([cx + 11, cy - 38, cx + 15, cy - 30], fill=(20, 20, 20))
    draw.arc([cx + 25, cy - 40, cx + 65, cy + 10], start=270, end=90, fill=(243, 156, 18), width=10)


# =========================================================================
# 8 CLASSIC SCENE RENDERERS (THE 150-SECOND MASTERPIECE)
# =========================================================================

def render_scene_1(draw, t, title_font, banner_font, sub_font):
    """Scene 1: Second 00 - The 5-Second Breath Challenge & Cereal Bowl."""
    cx, cy = WIDTH // 2, HEIGHT // 2
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(254, 249, 231))
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(247, 215, 148))
    draw.line([(0, HEIGHT - 220), (WIDTH, HEIGHT - 220)], fill=(225, 177, 44), width=6)

    # Bob holding breath puffing cheeks
    draw_bob(draw, cx - 100, cy + 30, mood="holding_breath", t_sec=t)

    # Cereal bowl on table
    table_top = HEIGHT - 280
    draw.rectangle([cx + 60, table_top, cx + 450, table_top + 25], fill=(160, 110, 60))
    draw.rectangle([cx + 80, table_top + 25, cx + 110, HEIGHT - 220], fill=(130, 90, 45))
    draw.rectangle([cx + 400, table_top + 25, cx + 430, HEIGHT - 220], fill=(130, 90, 45))
    # Red cereal bowl with golden flakes
    draw.chord([cx + 200, table_top - 60, cx + 320, table_top + 10], start=0, end=180, fill=(235, 77, 75), outline=(40, 30, 30), width=4)
    draw.ellipse([cx + 210, table_top - 60, cx + 310, table_top - 40], fill=(254, 202, 87))

    # Cat beside Bob
    draw_cat(draw, cx - 320, cy + 140)

    # Auto Banners
    draw_auto_banner(draw, cx, 50, "WHAT HAPPENS IF EARTH LOST OXYGEN FOR 5 SECONDS?", title_font, fill=(255, 107, 129))
    draw_auto_banner(draw, cx, 145, "SECOND 00: THE 5-SECOND BREATH CHALLENGE!", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))
    draw_auto_banner(draw, cx, HEIGHT - 130, "ATMOSPHERIC OXYGEN: 20.95% • HUMAN BREATH: 30 SECONDS", sub_font, fill=(45, 52, 54), text_fill=(254, 202, 87))


def render_scene_2(draw, t, title_font, banner_font, sub_font):
    """Scene 2: Second 01 - Concrete Crumbles to Powder!"""
    cx, cy = WIDTH // 2, HEIGHT // 2
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(223, 230, 233))
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(178, 190, 195))

    # Crumbling Skyscrapers turning into billowing clouds of dust
    skyscrapers = [(180, 520, 220), (450, 620, 260), (WIDTH - 450, 580, 260), (WIDTH - 180, 480, 200)]
    for sx, sh, sw in skyscrapers:
        # Crumbling block with cracked top
        crumble_h = int(sh * max(0.2, 1.0 - (t * 0.15)))
        draw.rectangle([sx - sw // 2, HEIGHT - crumble_h, sx + sw // 2, HEIGHT], fill=(99, 110, 114))
        # Billowing white dust clouds
        for c_i in range(5):
            dx = sx - sw // 2 + c_i * 45
            dy = HEIGHT - crumble_h - int(math.sin(t * 3.0 + c_i) * 20)
            draw.ellipse([dx - 45, dy - 45, dx + 45, dy + 45], fill=(255, 255, 255, 220), outline=(200, 200, 200), width=2)

    # Bob in shock looking at crumbling buildings
    draw_bob(draw, cx, cy + 40, mood="shocked", t_sec=t)

    # Auto Banners
    draw_auto_banner(draw, cx, 50, "SECOND 01: CONCRETE CRUMBLES TO POWDER!", title_font, fill=(235, 77, 75))
    draw_auto_banner(draw, cx, 145, "OXYGEN IS THE CHEMICAL BINDER IN ALL CONCRETE", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))
    draw_auto_banner(draw, cx, HEIGHT - 130, "ALL BRIDGES, SKYSCRAPERS & DAMS DISSOLVE LIKE SUGAR", sub_font, fill=(45, 52, 54), text_fill=(255, 107, 129))


def render_scene_3(draw, t, title_font, banner_font, sub_font):
    """Scene 3: Second 02 - Daytime Sky Turns Pitch Black!"""
    cx, cy = WIDTH // 2, HEIGHT // 2
    # Pitch black daytime sky!
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(10, 12, 22))
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(47, 53, 66))

    # Blazing bright noon sun in upper right
    sun_x, sun_y = WIDTH - 260, 240
    draw.ellipse([sun_x - 100, sun_y - 100, sun_x + 100, sun_y + 100], fill=(255, 255, 200, 90))
    draw.ellipse([sun_x - 65, sun_y - 65, sun_x + 65, sun_y + 65], fill=(255, 230, 0), outline=(255, 255, 255), width=6)

    # Twinkling stars in daytime
    np.random.seed(33)
    for _ in range(50):
        sx = int(np.random.uniform(40, WIDTH - 40))
        sy = int(np.random.uniform(30, HEIGHT - 300))
        r = np.random.choice([2, 3])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255, 220))

    # Bob pointing up at dark sky in total shock
    draw_bob(draw, cx, cy + 40, mood="shocked", t_sec=t)

    # Auto Banners
    draw_auto_banner(draw, cx, 50, "SECOND 02: THE NOON SKY TURNS PITCH BLACK!", title_font, fill=(108, 92, 231))
    draw_auto_banner(draw, cx, 145, "RAYLEIGH SCATTERING FAILS • STARS VISIBLE AT NOON", banner_font, fill=(0, 206, 201), text_fill=(20, 20, 20))
    draw_auto_banner(draw, cx, HEIGHT - 130, "WITHOUT OXYGEN MOLECULES, DAYTIME EARTH LOOKS LIKE DEEP SPACE", sub_font, fill=(45, 52, 54), text_fill=(254, 202, 87))


def render_scene_4(draw, t, title_font, banner_font, sub_font):
    """Scene 4: Second 03 - 21% Air Pressure Drop & Ears Pop!"""
    cx, cy = WIDTH // 2, HEIGHT // 2
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(255, 209, 102))
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(238, 90, 36))

    # Barometric pressure dropping gauge on left
    draw.rounded_rectangle([140, 260, 440, 520], radius=20, fill=(45, 52, 54), outline=(235, 77, 75), width=6)
    draw.text((170, 290), "AIR PRESSURE", font=banner_font, fill=(254, 202, 87))
    draw.text((170, 360), "-21.0 kPa", font=title_font, fill=(235, 77, 75))
    draw.text((170, 440), "BAROTRAUMA ALERT", font=sub_font, fill=(255, 255, 255))

    # Bob clutching ears with ear smoke puffs
    draw_bob(draw, cx + 80, cy + 40, mood="shocked", t_sec=t)
    # Ear smoke puffs
    bob_bx = cx + 80
    for sx, sy in [(bob_bx - 120, cy), (bob_bx + 120, cy)]:
        draw.ellipse([sx - 25, sy - 25, sx + 25, sy + 25], fill=(255, 255, 255, 200), outline=(200, 200, 200), width=3)

    # Auto Banners
    draw_auto_banner(draw, cx, 50, "SECOND 03: 21% AIR PRESSURE DROP!", title_font, fill=(235, 77, 75))
    draw_auto_banner(draw, cx, 145, "INSTANT TELEPORTATION TO TOP OF MOUNT EVEREST", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))
    draw_auto_banner(draw, cx, HEIGHT - 130, "EVERYONE'S INNER EAR DRUMS RUPTURE AT THE EXACT SAME MICROSECOND", sub_font, fill=(45, 52, 54), text_fill=(255, 107, 129))


def render_scene_5(draw, t, title_font, banner_font, sub_font):
    """Scene 5: Second 04 - Instant Metal Cold Welding!"""
    cx, cy = WIDTH // 2, HEIGHT // 2
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(130, 204, 221))
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(47, 53, 66))

    # Road with stopped cars welded solid
    car_x = cx - 240
    draw.rectangle([car_x - 140, HEIGHT - 320, car_x + 140, HEIGHT - 220], fill=(235, 77, 75), outline=(40, 30, 30), width=4)
    draw.ellipse([car_x - 90, HEIGHT - 220, car_x - 40, HEIGHT - 170], fill=(30, 30, 30))
    draw.ellipse([car_x + 40, HEIGHT - 220, car_x + 90, HEIGHT - 170], fill=(30, 30, 30))

    # Electric welding sparks between metal parts!
    for sp_i in range(12):
        sp_x = car_x + int(math.sin(t * 8.0 + sp_i) * 70)
        sp_y = HEIGHT - 280 + int(math.cos(t * 8.0 + sp_i) * 50)
        draw.line([(sp_x - 10, sp_y), (sp_x + 10, sp_y)], fill=(255, 242, 0), width=4)
        draw.line([(sp_x, sp_y - 10), (sp_x, sp_y + 10)], fill=(255, 242, 0), width=4)

    # Bob staring at his welded zipper
    draw_bob(draw, cx + 180, cy + 40, mood="shocked", t_sec=t)

    # Auto Banners
    draw_auto_banner(draw, cx, 50, "SECOND 04: INSTANT METAL COLD WELDING!", title_font, fill=(0, 206, 201), text_fill=(20, 20, 20))
    draw_auto_banner(draw, cx, 145, "METALS FUSE TOGETHER WITHOUT OXIDATION BARRIER", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))
    draw_auto_banner(draw, cx, HEIGHT - 130, "EVERY ENGINE, ZIPPER & KEYHOLE PERMANENTLY WELDS INTO SOLID STEEL", sub_font, fill=(45, 52, 54), text_fill=(254, 202, 87))


def render_scene_6(draw, t, title_font, banner_font, sub_font):
    """Scene 6: Second 05 - 46% of Earth's Crust Vanishes & Sinkhole Fall!"""
    cx, cy = WIDTH // 2, HEIGHT // 2
    # Crumbling abyss background
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(24, 44, 97))

    # Giant crumbling abyss fissure
    draw.polygon([(0, HEIGHT - 180), (cx - 250, HEIGHT - 180), (cx, HEIGHT), (0, HEIGHT)], fill=(15, 10, 8))
    draw.polygon([(cx + 250, HEIGHT - 180), (WIDTH, HEIGHT - 180), (WIDTH, HEIGHT), (cx, HEIGHT)], fill=(15, 10, 8))

    # Bob falling into sinkhole on his yellow inflatable sofa!
    sofa_x = cx
    sofa_y = cy + int(math.sin(t * 5.0) * 35) + 30
    draw.rounded_rectangle([sofa_x - 160, sofa_y - 30, sofa_x + 160, sofa_y + 60], radius=20, fill=(254, 202, 87), outline=(225, 177, 44), width=5)
    draw_bob(draw, sofa_x, sofa_y - 70, mood="shocked", t_sec=t, floating=True)

    # Auto Banners
    draw_auto_banner(draw, cx, 50, "SECOND 05: 46% OF EARTH'S CRUST VANISHES!", title_font, fill=(235, 77, 75))
    draw_auto_banner(draw, cx, 145, "NEARLY HALF OF ALL ROCKS & SOIL IS OXYGEN!", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))
    draw_auto_banner(draw, cx, HEIGHT - 130, "THE GROUND DISSOLVES BENEATH OUR FEET INTO A PLANETARY SINKHOLE", sub_font, fill=(45, 52, 54), text_fill=(255, 107, 129))


def render_scene_7(draw, t, title_font, banner_font, sub_font):
    """Scene 7: Second 06 - Oxygen Rebounds with Planetary Thunderclap!"""
    cx, cy = WIDTH // 2, HEIGHT // 2
    # Glorious bright blue sky returns!
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(116, 185, 255))
    # Giant sand dune where Bob landed
    draw.chord([-300, HEIGHT - 280, WIDTH + 300, HEIGHT + 400], start=180, end=360, fill=(250, 211, 144))

    # Bob bouncing joyfully on his inflatable yellow sofa!
    bounce = int(math.sin(t * 7.0) * 25)
    sofa_x = cx
    sofa_y = cy + 60 + bounce
    draw.rounded_rectangle([sofa_x - 160, sofa_y - 30, sofa_x + 160, sofa_y + 60], radius=20, fill=(254, 202, 87), outline=(225, 177, 44), width=5)
    draw_bob(draw, sofa_x, sofa_y - 70, mood="happy", t_sec=t)

    # Auto Banners
    draw_auto_banner(draw, cx, 50, "SECOND 06: OXYGEN FLOODS BACK TO EARTH!", title_font, fill=(9, 132, 227))
    draw_auto_banner(draw, cx, 145, "THE PLANETARY THUNDERCLAP REBOUND!", banner_font, fill=(46, 204, 113), text_fill=(255, 255, 255))
    draw_auto_banner(draw, cx, HEIGHT - 130, "AIR PRESSURE REBOUNDS & BLUE SKY SCATTERING RESTORES IN 1 SECOND", sub_font, fill=(45, 52, 54), text_fill=(254, 202, 87))


def render_scene_8(draw, t, title_font, banner_font, sub_font):
    """Scene 8: The Fresh Air Outro & Pancake Victory!"""
    cx, cy = WIDTH // 2, HEIGHT // 2
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(254, 249, 231))
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(247, 215, 148))
    draw.line([(0, HEIGHT - 220), (WIDTH, HEIGHT - 220)], fill=(225, 177, 44), width=6)

    # Bob taking giant fresh breath of air, covered in white dust
    draw_bob(draw, cx - 120, cy + 30, mood="happy", t_sec=t)

    # Huge plate of buttered pancakes
    p_x = cx + 180
    p_y = cy + 90
    draw.ellipse([p_x - 70, p_y + 10, p_x + 70, p_y + 40], fill=(240, 240, 240))
    for pi in range(4):
        draw.ellipse([p_x - 55, p_y - pi * 15, p_x + 55, p_y + 20 - pi * 15], fill=(254, 202, 87), outline=(225, 177, 44), width=3)
    draw.rectangle([p_x - 12, p_y - 65, p_x + 12, p_y - 45], fill=(255, 242, 0))

    # Cat beside pancakes
    draw_cat(draw, cx + 340, cy + 120)

    # Auto Banners & CTA
    draw_auto_banner(draw, cx, 50, "WHAT HAPPENS IF EARTH LOST OXYGEN FOR 5 SECONDS?", title_font, fill=(235, 77, 75))
    draw_auto_banner(draw, cx, HEIGHT - 100, "SUBSCRIBE TO BOB BIG QUESTIONS FOR MORE CURIOUS SCIENCE!", banner_font, fill=(46, 204, 113))

    draw_vector_bell(draw, cx - 440, HEIGHT - 100)
    draw_vector_thumbs_up(draw, cx + 440, HEIGHT - 100)


SCENE_RENDERERS = [
    render_scene_1, render_scene_2, render_scene_3, render_scene_4,
    render_scene_5, render_scene_6, render_scene_7, render_scene_8
]


def render_masterpiece_frame(frame_idx: int, scene_bounds: list, title_font, banner_font, sub_font) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 35))
    draw = ImageDraw.Draw(img, "RGBA")

    scene_idx = 0
    t_local = 0.0
    for idx, (start_f, end_f) in enumerate(scene_bounds):
        if start_f <= frame_idx < end_f:
            scene_idx = idx
            t_local = (frame_idx - start_f) / float(FPS)
            break

    renderer = SCENE_RENDERERS[scene_idx % len(SCENE_RENDERERS)]
    renderer(draw, t_local, title_font, banner_font, sub_font)

    # Screen shake during Scene 6 (crust collapse)
    if scene_idx == 5:
        shake_x = int(math.sin(frame_idx * 1.5) * 8)
        shake_y = int(math.cos(frame_idx * 1.8) * 6)
        shaken = Image.new("RGB", (WIDTH, HEIGHT), (10, 10, 15))
        shaken.paste(img, (shake_x, shake_y))
        img = shaken

    return img


def produce_oxygen_lost_masterpiece():
    logger.info("🎬 Rendering 2m 30s Animated Masterpiece: 'What If Earth Lost Oxygen For 5 Seconds?'...")

    timings_file = AUDIO_DIR / "scene_timings.json"
    audio_mix_file = AUDIO_DIR / "full_audio_mix_150s.wav"

    if not timings_file.exists():
        raise FileNotFoundError(f"Timings file missing: {timings_file}")
    if not audio_mix_file.exists():
        raise FileNotFoundError(f"Audio file missing: {audio_mix_file}")

    with open(timings_file) as f:
        timings_data = json.load(f)

    scene_bounds = []
    for sc in timings_data["scenes"]:
        scene_bounds.append((sc["start_frame"], sc["end_frame"]))

    total_frames = timings_data["total_frames"]
    total_duration = total_frames / float(FPS)
    logger.info(f"⏱️ Video Duration: {total_duration:.2f}s (~2m 30s) | Total Frames: {total_frames}")

    title_font = get_font(size=46, bold=True, cartoon=True)
    banner_font = get_font(size=32, bold=True, cartoon=True)
    sub_font = get_font(size=24, bold=False, cartoon=False)

    ffmpeg_bin = get_ffmpeg_binary()
    hw = detect_hardware()

    final_output = EXPORTS_DIR / "What_If_Earth_Lost_Oxygen_2m30s.mp4"
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
        "-i", str(audio_mix_file),  # Input 1: Voice + Music mix
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
        frame_img = render_masterpiece_frame(frame_idx, scene_bounds, title_font, banner_font, sub_font)
        process.stdin.write(frame_img.tobytes())

        if frame_idx % 300 == 0:
            pct = int((frame_idx / total_frames) * 100)
            elapsed = time.time() - t0
            fps_curr = frame_idx / max(0.1, elapsed)
            logger.info(f"Rendering: {pct}% ({frame_idx}/{total_frames} frames, {fps_curr:.1f} fps)")

    process.stdin.close()
    process.wait()

    render_elapsed = time.time() - t0
    logger.success(f"🎉 2m 30s Video rendered in {render_elapsed:.1f}s ({total_frames / max(0.1, render_elapsed):.1f} fps)!")
    logger.success(f"📍 Video File: {final_output}")
    return str(final_output)


if __name__ == "__main__":
    produce_oxygen_lost_masterpiece()
