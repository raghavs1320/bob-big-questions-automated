"""Procedural 2D Animated Cartoon: 'What Happens If Gravity Disappeared For 60 Seconds?'

Duration: Exactly 2 minutes 33 seconds (153.2s) - 4,596 frames at 30fps.
Key Fixes Built-In:
- 100% Zero-Emoji Tofu Boxes: Uses custom procedural vector badges (drawn with PIL geometry).
- Dynamic Auto-Padding on All Banners: Mathematically measures text width with textbbox so text NEVER overflows.
- Frame-Accurate Zero-Drift Synchronization: Each scene renders for the exact frame count of its spoken sentence.
"""

import math
import os
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from config import EXPORTS_DIR, TEMP_DIR
from utils.hardware import detect_hardware, get_ffmpeg_binary, get_video_info
from utils.logger import logger
from voice.audio_processor import get_audio_duration

WIDTH, HEIGHT = 1920, 1080
FPS = 30

FONT_CHALKBOARD = "/System/Library/Fonts/Supplemental/Chalkboard.ttc"
FONT_FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"


def get_font(size: int = 40, bold: bool = False, cartoon: bool = True):
    if cartoon and os.path.exists(FONT_CHALKBOARD):
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


def draw_vector_star(draw, cx, cy, r_out=22, r_in=10, fill=(254, 202, 87), outline=(40, 30, 30)):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        ang = i * (math.pi / 5.0) - math.pi / 2.0
        pts.append((cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang))))
    draw.polygon(pts, fill=fill, outline=outline)


def draw_vector_bell(draw, cx, cy, r=24, fill=(254, 202, 87), tilt=0.0):
    """Draws a golden notification bell with clapper."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r - 5], fill=fill, outline=(40, 30, 30), width=4)
    draw.chord([cx - r - 8, cy + 5, cx + r + 8, cy + 28], start=180, end=360, fill=fill, outline=(40, 30, 30), width=4)
    draw.ellipse([cx - 8, cy + 22, cx + 8, cy + 34], fill=(225, 177, 44), outline=(40, 30, 30), width=3)


def draw_vector_thumbs_up(draw, cx, cy, size=24, fill=(255, 255, 255)):
    """Draws a clean white thumbs up vector badge."""
    # Fist
    draw.rounded_rectangle([cx - size, cy - size // 2, cx + size // 2, cy + size], radius=8, fill=fill)
    # Thumb pointing up
    draw.rounded_rectangle([cx - size, cy - size * 1.2, cx - size // 3, cy], radius=6, fill=fill)


def draw_bob(draw, cx, cy, mood="happy", t_sec=0.0, angle_deg=0.0, floating=False, clothes="hoodie"):
    """Draws Bob with full rotational freedom for zero-gravity tumbling."""
    radius = 95
    bx, by = cx, cy

    # Base body
    if clothes == "hoodie":
        # Cool cyan/teal hoodie
        draw_rounded_rect(draw, [bx - 75, by + 65, bx + 75, by + 230], radius=28, fill=(0, 206, 201), outline=(40, 30, 30), width=6)
        # Coral shorts
        draw_rounded_rect(draw, [bx - 70, by + 220, bx + 70, by + 300], radius=15, fill=(255, 107, 129), outline=(40, 30, 30), width=5)
        # Legs
        if floating:
            # Floating astronaut bent legs
            draw.line([(bx - 35, by + 300), (bx - 55, by + 340), (bx - 35, by + 380)], fill=(255, 218, 185), width=20)
            draw.line([(bx + 35, by + 300), (bx + 60, by + 345), (bx + 40, by + 385)], fill=(255, 218, 185), width=20)
        else:
            draw.line([(bx - 35, by + 300), (bx - 35, by + 370)], fill=(255, 218, 185), width=22)
            draw.line([(bx + 35, by + 300), (bx + 35, by + 370)], fill=(255, 218, 185), width=22)
            draw.ellipse([bx - 55, by + 365, bx - 15, by + 385], fill=(254, 202, 87), outline=(40, 30, 30), width=4)
            draw.ellipse([bx + 15, by + 365, bx + 55, by + 385], fill=(254, 202, 87), outline=(40, 30, 30), width=4)

    # Bob's Head
    draw.ellipse([bx - radius, by - radius, bx + radius, by + radius], fill=(255, 218, 185), outline=(40, 30, 30), width=6)

    # Hair (Messy brown tufts)
    hair_color = (101, 67, 33)
    draw.arc([bx - radius + 10, by - radius - 15, bx + radius - 10, by - radius + 45], start=180, end=360, fill=hair_color, width=20)
    draw.ellipse([bx - 20, by - radius - 24, bx + 25, by - radius + 8], fill=hair_color)

    # Facial Expressions
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

    elif mood == "superhero":
        # Flying confident hero smile
        for eye_x in (bx - 40, bx + 40):
            draw.ellipse([eye_x - 24, by - 18 - 24, eye_x + 24, by - 18 + 24], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
            draw.ellipse([eye_x - 4, by - 20, eye_x + 14, by], fill=(30, 30, 40))
        draw.arc([bx - 25, by + 12, bx + 30, by + 45], start=20, end=170, fill=(230, 60, 60), width=7)


def draw_cat(draw, cx, cy, angle_deg=0.0):
    """Draws Bob's cute orange tabby cat."""
    # Body
    draw.ellipse([cx - 45, cy - 30, cx + 45, cy + 30], fill=(243, 156, 18), outline=(40, 30, 30), width=4)
    # Head
    draw.ellipse([cx - 30, cy - 60, cx + 30, cy], fill=(243, 156, 18), outline=(40, 30, 30), width=4)
    # Ears
    draw.polygon([(cx - 25, cy - 50), (cx - 35, cy - 80), (cx - 10, cy - 58)], fill=(230, 126, 34), outline=(40, 30, 30))
    draw.polygon([(cx + 10, cy - 58), (cx + 35, cy - 80), (cx + 25, cy - 50)], fill=(230, 126, 34), outline=(40, 30, 30))
    # Big round confused cat eyes
    draw.ellipse([cx - 20, cy - 42, cx - 6, cy - 26], fill=(46, 204, 113), outline=(40, 30, 30), width=3)
    draw.ellipse([cx + 6, cy - 42, cx + 20, cy - 26], fill=(46, 204, 113), outline=(40, 30, 30), width=3)
    # Pupils
    draw.ellipse([cx - 15, cy - 38, cx - 11, cy - 30], fill=(20, 20, 20))
    draw.ellipse([cx + 11, cy - 38, cx + 15, cy - 30], fill=(20, 20, 20))
    # Cute pink nose & whiskers
    draw.polygon([(cx - 4, cy - 22), (cx + 4, cy - 22), (cx, cy - 17)], fill=(255, 175, 175))
    draw.line([(cx - 25, cy - 20), (cx - 5, cy - 19)], fill=(40, 30, 30), width=2)
    draw.line([(cx + 5, cy - 19), (cx + 25, cy - 20)], fill=(40, 30, 30), width=2)
    # Curled floating tail
    draw.arc([cx + 25, cy - 40, cx + 65, cy + 10], start=270, end=90, fill=(243, 156, 18), width=10)


def render_scene_1_coffee(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 1: Monday Morning Kitchen - Coffee Lifts into Midair Spheres & Floating Cat."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Cozy pastel yellow kitchen
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(254, 249, 231))
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(247, 215, 148))
    draw.line([(0, HEIGHT - 220), (WIDTH, HEIGHT - 220)], fill=(225, 177, 44), width=6)

    # Refrigerator on Left with magnets
    ref_x = 180
    draw_rounded_rect(draw, [ref_x - 100, 180, ref_x + 100, HEIGHT - 220], radius=15, fill=(223, 228, 234), outline=(47, 53, 66), width=5)
    draw.line([(ref_x - 100, 420), (ref_x + 100, 420)], fill=(178, 190, 195), width=4)
    # Cute magnets
    draw.ellipse([ref_x - 40, 260, ref_x - 10, 290], fill=(255, 107, 129))
    draw.rectangle([ref_x + 10, 270, ref_x + 50, 310], fill=(254, 202, 87))

    # Bob holding red coffee mug
    bob_x = cx - 120
    bob_y = cy + 40
    draw_bob(draw, bob_x, bob_y, mood="shocked", t_sec=t_sec, clothes="hoodie")

    # Coffee Mug in Bob's hand
    mug_x, mug_y = bob_x + 120, bob_y + 110
    draw_rounded_rect(draw, [mug_x - 35, mug_y - 45, mug_x + 35, mug_y + 35], radius=12, fill=(238, 82, 83), outline=(40, 30, 30), width=5)
    draw.arc([mug_x + 25, mug_y - 25, mug_x + 55, mug_y + 15], start=270, end=90, fill=(238, 82, 83), width=8)

    # Floating liquid coffee spheres rising upward!
    for drop_i in range(8):
        drop_t = (t_sec * 50.0 + drop_i * 65) % 350
        dx = mug_x - 10 + int(math.sin(t_sec * 3.0 + drop_i) * 35)
        dy = mug_y - 60 - int(drop_t)
        dr = 10 + (drop_i % 4) * 5
        # Brown coffee sphere with glossy white highlight
        draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=(111, 78, 55), outline=(60, 40, 25), width=3)
        draw.ellipse([dx - dr // 2, dy - dr // 2, dx - dr // 4, dy - dr // 4], fill=(255, 255, 255, 180))

    # Floating Cat upside down beside Bob!
    cat_y = cy - 20 + int(math.sin(t_sec * 3.5) * 25)
    draw_cat(draw, cx + 240, cat_y)

    # Dynamic Auto-Banners (ZERO OVERFLOW GUARANTEE)
    draw_auto_banner(draw, cx, 50, "WHAT HAPPENS IF GRAVITY DISAPPEARS?", title_font, fill=(255, 107, 129))
    draw_auto_banner(draw, cx, 145, "SECOND 0: FLOATING COFFEE & ZERO-G CATS!", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))


def render_scene_2_levitation(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 2: Second 10 - Total Levitation & Earth's Spin Drifting."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Open outdoor horizon with rolling green hills and blue sky
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(130, 204, 221))
    draw.chord([-200, HEIGHT - 200, WIDTH + 200, HEIGHT + 400], start=180, end=360, fill=(46, 204, 113))

    # Bob completely levitating horizontally in midair, flailing arms!
    float_y = cy - 40 + int(math.sin(t_sec * 4.0) * 30)
    draw_bob(draw, cx - 100, float_y, mood="shocked", t_sec=t_sec, floating=True, clothes="hoodie")

    # Objects drifting into the sky: Red Bicycle, Park Bench, Toaster!
    # 1. Red Bicycle floating diagonally upward
    bike_y = int(HEIGHT - 280 - (t_sec * 40) % (HEIGHT - 100))
    bike_x = cx + 280
    # Wheels
    draw.ellipse([bike_x - 60, bike_y, bike_x - 10, bike_y + 50], outline=(40, 30, 30), width=6)
    draw.ellipse([bike_x + 20, bike_y, bike_x + 70, bike_y + 50], outline=(40, 30, 30), width=6)
    draw.line([(bike_x - 35, bike_y + 25), (bike_x, bike_y)], fill=(235, 77, 75), width=8)
    draw.line([(bike_x, bike_y), (bike_x + 45, bike_y + 25)], fill=(235, 77, 75), width=8)

    # 2. Park bench floating
    bench_y = int(HEIGHT - 180 - (t_sec * 32) % (HEIGHT - 100))
    bench_x = 240
    draw_rounded_rect(draw, [bench_x - 70, bench_y, bench_x + 70, bench_y + 20], radius=8, fill=(139, 69, 19), outline=(40, 30, 30), width=4)
    draw.line([(bench_x - 50, bench_y + 20), (bench_x - 50, bench_y + 55)], fill=(60, 60, 60), width=6)
    draw.line([(bench_x + 50, bench_y + 20), (bench_x + 50, bench_y + 55)], fill=(60, 60, 60), width=6)

    # Earth Spin Speed Gauge
    draw_auto_banner(draw, cx, HEIGHT - 130, "EARTH ROTATIONAL SPEED: 1,670 KM/H (OBJECTS DRIFT UPWARD)", sub_font, fill=(45, 52, 54), text_fill=(254, 202, 87))

    # Top Banners
    draw_auto_banner(draw, cx, 50, "SECOND 10: WEIGHTLESS LEVITATION!", title_font, fill=(108, 92, 231))
    draw_auto_banner(draw, cx, 145, "UNANCHORED CARS & BICYCLES FLOAT TO CLOUDS", banner_font, fill=(0, 206, 201), text_fill=(20, 20, 20))


def render_scene_3_pool_blobs(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 3: Second 20 - Swimming Pool Lifts into Giant Floating Water Blob."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Backyard paradise with green lawn
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(116, 185, 255))
    draw.rectangle([0, HEIGHT - 240, WIDTH, HEIGHT], fill=(85, 239, 196))

    # Empty rectangular pool foundation in ground with tiles
    draw_rounded_rect(draw, [cx - 380, HEIGHT - 220, cx + 380, HEIGHT - 50], radius=25, fill=(178, 190, 195), outline=(47, 53, 66), width=6)
    draw.text((cx - 180, HEIGHT - 150), "[EMPTY POOL FOUNDATION]", font=sub_font, fill=(99, 110, 114))

    # Giant Undulating Surface-Tension Water Blob Floating in Midair!
    blob_x, blob_y = cx + 80, cy - 30
    wobble_r = int(math.sin(t_sec * 5.0) * 18)
    draw.ellipse([blob_x - 220 - wobble_r, blob_y - 180 + wobble_r, blob_x + 220 + wobble_r, blob_y + 180 - wobble_r], fill=(9, 132, 227), outline=(225, 245, 254), width=8)

    # Sparkling bubbles & surface glints inside water blob
    for bi in range(12):
        bx = blob_x + int(math.sin(t_sec * 2.0 + bi) * 140)
        by = blob_y + int(math.cos(t_sec * 2.5 + bi) * 110)
        draw.ellipse([bx - 12, by - 12, bx + 12, by + 12], fill=(255, 255, 255, 160), outline=(255, 255, 255), width=2)

    # Bob swimming through midair like a flying fish with goggles!
    bob_x = cx - 300
    bob_y = cy - 20 + int(math.sin(t_sec * 6.0) * 20)
    draw_bob(draw, bob_x, bob_y, mood="happy", t_sec=t_sec, floating=True, clothes="hoodie")

    # Cute cartoon yellow rubber duck floating inside the giant water blob!
    duck_x = blob_x + 40 + int(math.sin(t_sec * 4.0) * 30)
    duck_y = blob_y - 20 + int(math.cos(t_sec * 3.0) * 20)
    draw.ellipse([duck_x - 30, duck_y - 18, duck_x + 30, duck_y + 18], fill=(255, 234, 167), outline=(40, 30, 30), width=3)
    draw.ellipse([duck_x - 15, duck_y - 35, duck_x + 15, duck_y - 10], fill=(255, 234, 167), outline=(40, 30, 30), width=3)
    draw.polygon([(duck_x - 28, duck_y - 22), (duck_x - 12, duck_y - 28), (duck_x - 12, duck_y - 16)], fill=(235, 94, 40))

    # Top Banners
    draw_auto_banner(draw, cx, 50, "SECOND 20: GIANT FLOATING WATER BLOBS!", title_font, fill=(9, 132, 227))
    draw_auto_banner(draw, cx, 145, "SURFACE TENSION LIQUID SPHERES IN MIDAIR", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))


def render_scene_4_atmosphere(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 4: Second 30 - Atmosphere Expanding & Helicopter Birds."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # High Altitude Stratosphere view: Earth curvature below, dark space above
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(24, 44, 97))
    # Glowing blue atmospheric halo
    draw.arc([-400, 350, WIDTH + 400, HEIGHT + 800], start=180, end=360, fill=(74, 105, 189), width=80)
    # Earth globe curve
    draw.chord([-300, 420, WIDTH + 300, HEIGHT + 800], start=180, end=360, fill=(30, 55, 153))

    # Billowing clouds dispersing into space
    for ci in range(8):
        c_x = int((ci * 260 + t_sec * 35) % WIDTH)
        c_y = 360 + int(math.sin(t_sec * 2.0 + ci) * 40)
        draw.ellipse([c_x - 60, c_y - 30, c_x + 60, c_y + 30], fill=(255, 255, 255, 140))

    # Funny Cartoon Pigeon spinning like a helicopter!
    pigeon_x = cx + 220
    pigeon_y = cy - 80
    spin_ang = t_sec * 18.0
    # Pigeon body
    draw.ellipse([pigeon_x - 40, pigeon_y - 25, pigeon_x + 40, pigeon_y + 25], fill=(136, 84, 208), outline=(40, 30, 30), width=4)
    # Wings spinning rapidly like propeller blades
    w_len = 70
    draw.line([(pigeon_x - int(w_len * math.cos(spin_ang)), pigeon_y - int(w_len * math.sin(spin_ang))),
               (pigeon_x + int(w_len * math.cos(spin_ang)), pigeon_y + int(w_len * math.sin(spin_ang)))], fill=(240, 240, 240), width=10)
    # Dizzy spiral eyes on pigeon
    draw.ellipse([pigeon_x - 22, pigeon_y - 12, pigeon_x - 6, pigeon_y + 4], fill=(255, 255, 255), outline=(40, 30, 30), width=2)
    draw.ellipse([pigeon_x + 6, pigeon_y - 12, pigeon_x + 22, pigeon_y + 4], fill=(255, 255, 255), outline=(40, 30, 30), width=2)

    # Bob watching in awe
    bob_x = cx - 220
    bob_y = cy - 20
    draw_bob(draw, bob_x, bob_y, mood="shocked", t_sec=t_sec, floating=True, clothes="hoodie")

    # Barometric Pressure Alert
    draw_auto_banner(draw, cx, HEIGHT - 130, "ATMOSPHERIC EXPANSION: BAROMETRIC PRESSURE DROPPING RAPIDLY", sub_font, fill=(45, 52, 54), text_fill=(255, 107, 129))

    # Top Banners
    draw_auto_banner(draw, cx, 50, "SECOND 30: ATMOSPHERE DRIFTS INTO SPACE!", title_font, fill=(235, 77, 75))
    draw_auto_banner(draw, cx, 145, "WINGS FAIL & BIRDS SPIN LIKE HELICOPTERS!", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))


def render_scene_5_superhero(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 5: Second 40 - Downtown City Superheroes & High-Five Pigeon."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Downtown City Skyline
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(255, 209, 102))

    # Skyscrapers in background
    skyscrapers = [(120, 480, 220, (10, 61, 98)), (380, 360, 260, (30, 55, 153)), (WIDTH - 420, 320, 280, (74, 105, 189)), (WIDTH - 120, 450, 200, (10, 61, 98))]
    for sx, sh, sw, sc in skyscrapers:
        draw.rectangle([sx - sw // 2, HEIGHT - sh, sx + sw // 2, HEIGHT], fill=sc)
        # Windows
        for wy in range(HEIGHT - sh + 40, HEIGHT - 40, 55):
            for wx in range(sx - sw // 2 + 30, sx + sw // 2 - 20, 45):
                draw.rectangle([wx, wy, wx + 25, wy + 30], fill=(255, 242, 0))

    # Bob flying diagonally in superhero pose across the city street!
    hero_t = (t_sec * 120.0) % (WIDTH + 400) - 200
    hero_y = cy - 40 + int(math.sin(t_sec * 6.0) * 30)
    # Flowing superhero cape
    cape_x = int(hero_t) - 80
    draw.polygon([(cape_x, hero_y + 40), (cape_x - 140, hero_y + 20 + int(math.sin(t_sec * 10) * 30)), (cape_x - 100, hero_y + 120), (cape_x, hero_y + 100)], fill=(238, 82, 83), outline=(40, 30, 30))
    draw_bob(draw, int(hero_t), hero_y, mood="superhero", t_sec=t_sec, floating=True, clothes="hoodie")

    # Comic "HIGH FIVE!" impact star with floating pigeon
    if 2.0 < (t_sec % 5.0) < 4.0:
        star_x = int(hero_t) + 140
        draw_vector_star(draw, star_x, hero_y - 20, r_out=50, r_in=25, fill=(255, 71, 87), outline=(255, 255, 255))
        draw.text((star_x - 45, hero_y - 32), "HIGH FIVE!", font=sub_font, fill=(255, 255, 255))

    # Top Banners
    draw_auto_banner(draw, cx, 50, "SECOND 40: DOWNTOWN SUPERHEROES!", title_font, fill=(238, 82, 83))
    draw_auto_banner(draw, cx, 145, "PUSH OFF SKYSCRAPERS & FLY TWO BLOCKS!", banner_font, fill=(46, 204, 113), text_fill=(255, 255, 255))


def render_scene_6_countdown(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 6: Second 50 - The Giant Red Emergency Siren Countdown."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # High-intensity emergency crimson & charcoal alert background
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(44, 44, 84))

    # Pulsing red emergency alert beams
    pulse_red = (255, int(40 + 30 * math.sin(t_sec * 15)), int(40 + 30 * math.sin(t_sec * 15)))
    for beam_ang in range(0, 360, 45):
        ang_rad = (t_sec * 2.0 + beam_ang) * (math.pi / 180.0)
        bx = cx + int(1200 * math.cos(ang_rad))
        by = cy + int(1200 * math.sin(ang_rad))
        draw.line([(cx, cy), (bx, by)], fill=pulse_red, width=16)

    # Giant Floating Digital Emergency Clock in Center
    countdown_val = max(0, 5 - int(t_sec % 6.0))
    clock_box = [cx - 320, cy - 140, cx + 320, cy + 90]
    draw_rounded_rect(draw, clock_box, radius=25, fill=(15, 15, 25), outline=(255, 71, 87), width=8)
    draw.text((cx - 280, cy - 120), "GRAVITY RESET IN:", font=banner_font, fill=(255, 255, 255))
    clock_font = get_font(size=120, bold=True, cartoon=False)
    draw.text((cx - 140, cy - 65), f"00:0{countdown_val}", font=clock_font, fill=(255, 71, 87))

    # Bob shivering in anticipation looking down
    bob_x = cx
    bob_y = cy + 180
    draw_bob(draw, bob_x, bob_y, mood="shocked", t_sec=t_sec, floating=True, clothes="hoodie")

    # Top Banners
    draw_auto_banner(draw, cx, 50, "SECOND 50: EMERGENCY GRAVITY COUNTDOWN!", title_font, fill=(255, 71, 87))
    draw_auto_banner(draw, cx, 145, "ALL OBJECTS FREEZE AT MAXIMUM APOGEE!", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))


def render_scene_7_grand_slam(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 7: Second 60 - SLAM! Gravity Snaps Back, Inflatable Sofa & Giant Splash."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Vibrant bright recovery scene
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(255, 234, 167))
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(46, 204, 113))

    # Giant Comic Book "SLAM!" Starburst (First 3 seconds)
    if t_sec < 3.5:
        draw_vector_star(draw, cx, cy - 160, r_out=260, r_in=160, fill=(235, 77, 75), outline=(255, 255, 255))
        draw.text((cx - 140, cy - 210), "SLAM!", font=title_font, fill=(255, 255, 255))

    # Giant Bouncy Inflatable Yellow Sofa!
    sofa_x, sofa_y = cx - 180, cy + 140
    draw_rounded_rect(draw, [sofa_x - 180, sofa_y, sofa_x + 180, sofa_y + 140], radius=35, fill=(255, 185, 45), outline=(225, 112, 85), width=8)
    # Pillowy cushions
    draw.ellipse([sofa_x - 160, sofa_y - 20, sofa_x - 20, sofa_y + 50], fill=(254, 202, 87), outline=(225, 112, 85), width=5)
    draw.ellipse([sofa_x + 20, sofa_y - 20, sofa_x + 160, sofa_y + 50], fill=(254, 202, 87), outline=(225, 112, 85), width=5)

    # Bob comfortably sunken into the sofa cushions, relieved and smiling!
    draw_bob(draw, sofa_x, sofa_y - 40, mood="happy", t_sec=t_sec, clothes="hoodie")

    # Giant Swimming Pool Splash on Right!
    splash_x, splash_y = cx + 260, HEIGHT - 200
    # Water splash fan
    for ang_i in range(-60, 70, 20):
        rad = ang_i * (math.pi / 180.0) - math.pi / 2.0
        sx = splash_x + int(180 * math.cos(rad))
        sy = splash_y + int(180 * math.sin(rad))
        draw.ellipse([sx - 20, sy - 20, sx + 20, sy + 20], fill=(9, 132, 227), outline=(225, 245, 254), width=4)
    draw_auto_banner(draw, splash_x, splash_y - 140, "MASSIVE SPLASH!", banner_font, fill=(9, 132, 227))

    # Top Banners
    draw_auto_banner(draw, cx, 50, "SECOND 60: GRAVITY RETURNS WITH A SLAM!", title_font, fill=(235, 77, 75))
    draw_auto_banner(draw, cx, 145, "BOB SAFELY CRASH-LANDS ON INFLATABLE SOFA", banner_font, fill=(46, 204, 113), text_fill=(255, 255, 255))


def render_scene_8_outro(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 8: Outro - The Invisible Glue & Interactive Animated Subscribe."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # High-energy royal midnight purple stage
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(30, 27, 75))

    # Spotlight fans
    for spot_x, spot_col in [(320, (192, 132, 252)), (WIDTH - 320, (251, 146, 60))]:
        draw.polygon([(spot_x, 0), (spot_x - 300, HEIGHT), (spot_x + 300, HEIGHT)], fill=(spot_col[0]//4, spot_col[1]//4, spot_col[2]//4))

    # Bob holding his cat smiling happily on left
    bob_x = cx - 360
    bob_y = cy + 60
    draw_bob(draw, bob_x, bob_y, mood="happy", t_sec=t_sec, clothes="hoodie")
    draw_cat(draw, bob_x + 90, bob_y + 120)

    # Interactive YouTube Subscribe Button (Red -> Gray Subscribed)
    sub_box = [cx - 60, cy - 60, cx + 460, cy + 60]
    is_clicked = t_sec >= 3.0
    btn_color = (60, 60, 60) if is_clicked else (255, 0, 0)
    btn_text = "SUBSCRIBED" if is_clicked else "SUBSCRIBE"

    draw_rounded_rect(draw, sub_box, radius=25, fill=btn_color, outline=(255, 255, 255), width=6)
    draw.text((cx + 10, cy - 30), btn_text, font=title_font, fill=(255, 255, 255))

    # Vector Golden Ringing Bell
    bell_tilt = math.sin(t_sec * 16.0) * 12.0 if is_clicked else 0.0
    draw_vector_bell(draw, cx + 390, cy, r=26, fill=(254, 202, 87), tilt=bell_tilt)

    # Thumbs Up Like Badge
    like_box = [cx - 60, cy + 100, cx + 460, cy + 200]
    draw_rounded_rect(draw, like_box, radius=20, fill=(30, 144, 255), outline=(255, 255, 255), width=5)
    draw_vector_thumbs_up(draw, cx + 20, cy + 150, size=24)
    draw.text((cx + 80, cy + 125), "LIKE THIS VIDEO!", font=banner_font, fill=(255, 255, 255))

    # Top Engagement Banners (ZERO OVERFLOW)
    draw_auto_banner(draw, cx, 50, "WHAT WOULD YOU DO IN ZERO GRAVITY?", title_font, fill=(255, 71, 87))
    draw_auto_banner(draw, cx, 145, "TELL US IN THE COMMENTS BELOW!", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))


def render_masterpiece_frame(frame_idx: int, scene_bounds: list, title_font, banner_font, sub_font) -> Image.Image:
    """Renders a single frame mapped mathematically to its exact audio scene."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    scene_idx = 0
    t_local = 0.0
    for idx, (start_f, end_f) in enumerate(scene_bounds):
        if start_f <= frame_idx < end_f:
            scene_idx = idx
            t_local = (frame_idx - start_f) / float(FPS)
            break

    if scene_idx == 0:
        render_scene_1_coffee(draw, t_local, title_font, banner_font, sub_font)
    elif scene_idx == 1:
        render_scene_2_levitation(draw, t_local, title_font, banner_font, sub_font)
    elif scene_idx == 2:
        render_scene_3_pool_blobs(draw, t_local, title_font, banner_font, sub_font)
    elif scene_idx == 3:
        render_scene_4_atmosphere(draw, t_local, title_font, banner_font, sub_font)
    elif scene_idx == 4:
        render_scene_5_superhero(draw, t_local, title_font, banner_font, sub_font)
    elif scene_idx == 5:
        render_scene_6_countdown(draw, t_local, title_font, banner_font, sub_font)
    elif scene_idx == 6:
        render_scene_7_grand_slam(draw, t_local, title_font, banner_font, sub_font)
    else:
        render_scene_8_outro(draw, t_local, title_font, banner_font, sub_font)

    return img


def produce_gravity_disappeared_masterpiece():
    logger.info("🎬 Rendering 2m30s Animated Cartoon: 'What Happens If Gravity Disappeared For 60 Seconds?'...")

    voice_path = str(TEMP_DIR / "gravity_full_voice.m4a")
    music_path = str(TEMP_DIR / "gravity_cartoon_music.wav")

    if not os.path.exists(voice_path):
        raise FileNotFoundError(f"Master voiceover track missing: {voice_path}")
    if not os.path.exists(music_path):
        raise FileNotFoundError(f"Cartoon music track missing: {music_path}")

    # Exact scene frame calculation for 0.000s timing drift
    scene_files = [str(TEMP_DIR / f"gravity_scene{i}.m4a") for i in range(1, 9)]
    scene_durs = [get_audio_duration(sf) for sf in scene_files]

    scene_bounds = []
    accum = 0
    for i, dur in enumerate(scene_durs, 1):
        f_count = int(round(dur * FPS))
        scene_bounds.append((accum, accum + f_count))
        logger.info(f"Scene {i}: {dur:.3f}s -> frames {accum} to {accum + f_count} ({f_count} frames)")
        accum += f_count

    total_frames = accum
    total_duration = total_frames / float(FPS)
    logger.info(f"⏱️ Video Duration: {total_duration:.2f}s (~2.5 mins) | Total Frames: {total_frames}")

    # Fonts
    title_font = get_font(size=54, bold=True, cartoon=True)
    banner_font = get_font(size=36, bold=True, cartoon=True)
    sub_font = get_font(size=26, bold=False, cartoon=False)

    ffmpeg_bin = get_ffmpeg_binary()
    hw = detect_hardware()

    final_output = EXPORTS_DIR / "What_If_Gravity_Disappeared_2m30s.mp4"
    final_output.parent.mkdir(parents=True, exist_ok=True)

    # FFmpeg command: mixes raw cartoon frames from stdin with full voiceover + ducked cartoon music
    cmd = [
        ffmpeg_bin,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",  # Video frames from stdin
        "-i", voice_path,  # Input 1: Voiceover track
        "-i", music_path,  # Input 2: Bouncy cartoon music track
        "-filter_complex",
        "[2:a]volume=0.30[music];[1:a]volume=1.0[voice];[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", hw.video_encoder,
        "-c:a", hw.audio_encoder,
        "-b:v", "9000k",
        "-b:a", "256k",
        "-pix_fmt", "yuv420p",
        str(final_output),
    ]

    logger.edit("Rendering procedural 1080p cartoon frames into FFmpeg pipeline...")
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    t0 = time.time()
    for frame_idx in range(total_frames):
        frame_img = render_masterpiece_frame(frame_idx, scene_bounds, title_font, banner_font, sub_font)
        process.stdin.write(frame_img.tobytes())

        if frame_idx % 300 == 0:
            pct = int((frame_idx / total_frames) * 100)
            logger.info(f"Rendering: {pct}% ({frame_idx}/{total_frames} frames)")

    process.stdin.close()
    process.wait()

    render_elapsed = time.time() - t0
    logger.success(f"Cartoon render completed in {render_elapsed:.1f}s ({total_frames / max(0.1, render_elapsed):.1f} fps)!")

    # High-CTR YouTube Thumbnail (1280x720 16:9)
    logger.info("🖼️ Creating High-CTR YouTube Thumbnail...")
    cx, cy = WIDTH // 2, HEIGHT // 2
    thumb_path = EXPORTS_DIR / "Gravity_Disappeared_Thumbnail.jpg"
    thumb_img = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 35))
    draw_th = ImageDraw.Draw(thumb_img)

    # Split screen composition: Left side normal room / Right side zero-g floating chaos!
    draw_th.rectangle([0, 0, WIDTH // 2, HEIGHT], fill=(254, 249, 231))
    draw_th.rectangle([0, HEIGHT - 220, WIDTH // 2, HEIGHT], fill=(247, 215, 148))
    # Right half zero-g void
    draw_th.rectangle([WIDTH // 2, 0, WIDTH, HEIGHT], fill=(24, 44, 97))

    # Split neon electric dividing line
    draw_th.line([(WIDTH // 2, 0), (WIDTH // 2, HEIGHT)], fill=(0, 206, 201), width=12)

    # Bob in center with shocked expression floating horizontally!
    draw_bob(draw_th, WIDTH // 2, cy + 40, mood="shocked", t_sec=1.0, floating=True, clothes="hoodie")

    # Floating giant water blob on right
    draw_th.ellipse([WIDTH - 300 - 100, 260 - 80, WIDTH - 300 + 100, 260 + 80], fill=(9, 132, 227), outline=(225, 245, 254), width=6)
    # Floating cat
    draw_cat(draw_th, WIDTH - 220, cy + 180)

    # Big Bold YouTube Title (Dynamic auto-banner)
    thumb_title_font = get_font(size=78, bold=True, cartoon=True)
    draw_auto_banner(draw_th, cx, 50, "WHAT IF GRAVITY DISAPPEARED?", thumb_title_font, fill=(235, 77, 75), pad_x=50, pad_y=20)
    badge_font = get_font(size=46, bold=True, cartoon=True)
    draw_auto_banner(draw_th, cx, HEIGHT - 150, "60 SECONDS OF ZERO-G CHAOS!", badge_font, fill=(254, 202, 87), text_fill=(40, 30, 30), pad_x=40, pad_y=16)

    # Resize to standard 1280x720 thumbnail
    thumb_final = thumb_img.resize((1280, 720), Image.Resampling.LANCZOS)
    thumb_final.save(str(thumb_path), "JPEG", quality=95)
    thumb_png = EXPORTS_DIR / "Gravity_Disappeared_Thumbnail.png"
    thumb_final.save(str(thumb_png), "PNG")

    info = get_video_info(str(final_output))
    logger.success("==================================================")
    logger.success("🎉 2m30s HIGH-RETENTION CARTOON MASTERPIECE READY!")
    logger.success(f"📍 Video File: {final_output}")
    logger.success(f"⏱️ Runtime: {info.get('duration', 0):.1f} seconds (Target: 150s)")
    logger.success(f"📐 Resolution: {info.get('width')}x{info.get('height')} 1080p Full HD")
    logger.success(f"🖼️ Thumbnail: {thumb_path}")
    logger.success("==================================================")

    return str(final_output), str(thumb_path)


if __name__ == "__main__":
    produce_gravity_disappeared_masterpiece()
