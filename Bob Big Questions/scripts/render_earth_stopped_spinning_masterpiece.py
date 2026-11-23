"""Procedural 2D Animated Cartoon: 'What Happens If The Earth Stopped Spinning For 5 Seconds?'

Duration: Exactly 1 minute 48 seconds (107.7s) - 3,231 frames at 30fps.
Production Upgrades:
- Typography: Arial Rounded MT Bold (friendly modern cartoon font) + Futura Bold (HUD / data).
- Bounding Boxes: Modern Clean Flat Pill Badges with soft shadows (NO thick harsh white borders).
- True Ink-Centering: Mathematical midpoint symmetry (identical padding on all 4 sides).
- Floating Action Typography: Onomatopoeias (SKRRRRT!, WHOOSH!, TSUNAMI SURF!) float freely with outlines.
- Zero-Emoji Tofu Boxes: Only clean text and procedural vector icons.
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
    """Draws a modern studio pill badge with true mathematical ink-centering and soft shadow."""
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    ink_w = x1 - x0
    ink_h = y1 - y0

    box_w = ink_w + pad_x * 2
    box_h = ink_h + pad_y * 2

    x_left = cx - box_w // 2
    y_top = center_y - box_h // 2
    x_right = cx + box_w // 2
    y_bottom = center_y + box_h // 2

    # Subtle soft drop shadow underneath for depth (studio grade!)
    shadow_box = [x_left, y_top + 4, x_right, y_bottom + 4]
    draw.rounded_rectangle(shadow_box, radius=radius, fill=(20, 20, 30))

    # Clean flat pill badge (NO harsh white border!)
    box = [x_left, y_top, x_right, y_bottom]
    draw.rounded_rectangle(box, radius=radius, fill=fill)

    # True mathematical ink centering formula
    draw_x = cx - (x0 + x1) / 2.0
    draw_y = center_y - (y0 + y1) / 2.0
    draw.text((draw_x, draw_y), text, font=font, fill=text_fill)
    return box


def draw_action_text(draw, cx: int, cy: int, text: str, font, fill=(255, 234, 167), stroke_fill=(40, 20, 20), stroke_width: int = 6):
    """Draws free-floating comic action typography directly over the scene."""
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    draw_x = cx - (x0 + x1) / 2.0
    draw_y = cy - (y0 + y1) / 2.0
    draw.text((draw_x, draw_y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def draw_vector_bell(draw, cx: int, cy: int, r: int = 24, fill=(254, 202, 87), tilt: float = 0.0):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r - 5], fill=fill, outline=(40, 30, 30), width=4)
    draw.chord([cx - r - 8, cy + 5, cx + r + 8, cy + 28], start=180, end=360, fill=fill, outline=(40, 30, 30), width=4)
    draw.ellipse([cx - 8, cy + 22, cx + 8, cy + 34], fill=(225, 177, 44), outline=(40, 30, 30), width=3)


def draw_vector_thumbs_up(draw, cx: int, cy: int, size: int = 24, fill=(255, 255, 255)):
    draw.rounded_rectangle([cx - size, cy - size // 2, cx + size // 2, cy + size], radius=8, fill=fill)
    draw.rounded_rectangle([cx - size, cy - size * 1.2, cx - size // 3, cy], radius=6, fill=fill)


def draw_bob(draw, cx: int, cy: int, mood="happy", t_sec: float = 0.0, pose="sitting", clothes="hoodie"):
    """Draws Bob with rich expressions and dynamic poses."""
    bx, by = cx, cy
    radius = 95

    # 1. Clothing & Body
    if pose == "sitting":
        draw.rounded_rectangle([bx - 75, by + 65, bx + 75, by + 220], radius=28, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
        # Sitting legs
        draw.rounded_rectangle([bx - 70, by + 210, bx + 70, by + 280], radius=15, fill=(255, 107, 129), outline=(40, 30, 30), width=4)

    elif pose == "catapulted":
        # Flying horizontal bullet pose
        draw.rounded_rectangle([bx - 120, by - 45, bx + 80, by + 45], radius=25, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
        # Trailing legs
        draw.rounded_rectangle([bx - 180, by - 35, bx - 110, by + 35], radius=15, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        # Feet
        draw.ellipse([bx - 200, by - 30, bx - 170, by - 10], fill=(254, 202, 87), outline=(40, 30, 30), width=3)
        draw.ellipse([bx - 200, by + 10, bx - 170, by + 30], fill=(254, 202, 87), outline=(40, 30, 30), width=3)

    elif pose == "surfing":
        # Surfing crouch pose
        draw.rounded_rectangle([bx - 60, by + 65, bx + 60, by + 200], radius=25, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
        # Surf shorts
        draw.rounded_rectangle([bx - 55, by + 190, bx + 55, by + 260], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        # Bent knees on board
        draw.line([(bx - 35, by + 260), (bx - 50, by + 310)], fill=(255, 218, 185), width=20)
        draw.line([(bx + 35, by + 260), (bx + 50, by + 310)], fill=(255, 218, 185), width=20)

    else:
        # Standing happy
        draw.rounded_rectangle([bx - 75, by + 65, bx + 75, by + 230], radius=28, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
        draw.rounded_rectangle([bx - 70, by + 220, bx + 70, by + 300], radius=15, fill=(255, 107, 129), outline=(40, 30, 30), width=4)
        draw.line([(bx - 35, by + 300), (bx - 35, by + 370)], fill=(255, 218, 185), width=22)
        draw.line([(bx + 35, by + 300), (bx + 35, by + 370)], fill=(255, 218, 185), width=22)
        draw.ellipse([bx - 55, by + 365, bx - 15, by + 385], fill=(254, 202, 87), outline=(40, 30, 30), width=4)
        draw.ellipse([bx + 15, by + 365, bx + 55, by + 385], fill=(254, 202, 87), outline=(40, 30, 30), width=4)

    # 2. Bob's Head
    draw.ellipse([bx - radius, by - radius, bx + radius, by + radius], fill=(255, 218, 185), outline=(40, 30, 30), width=5)

    # Messy brown hair tufts
    hair_color = (101, 67, 33)
    draw.arc([bx - radius + 10, by - radius - 15, bx + radius - 10, by - radius + 45], start=180, end=360, fill=hair_color, width=20)
    draw.ellipse([bx - 20, by - radius - 24, bx + 25, by - radius + 8], fill=hair_color)

    # 3. Facial Expressions
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
        draw.arc([bx - 65, by - 65, bx - 20, by - 40], start=180, end=360, fill=(60, 40, 40), width=5)
        draw.arc([bx + 20, by - 65, bx + 65, by - 40], start=180, end=360, fill=(60, 40, 40), width=5)
        draw.ellipse([bx - 24, by + 15, bx + 24, by + 65], fill=(50, 20, 20), outline=(220, 60, 60), width=5)

    elif mood == "sunglasses":
        # Cool black sunglasses
        draw.rounded_rectangle([bx - 70, by - 35, bx + 70, by + 10], radius=12, fill=(30, 30, 30))
        draw.line([(bx - 40, by - 25), (bx - 10, by + 5)], fill=(255, 255, 255), width=3)
        # Confident surfer grin
        draw.arc([bx - 30, by + 18, bx + 30, by + 50], start=20, end=170, fill=(230, 60, 60), width=7)


def draw_pancakes(draw, cx: int, cy: int):
    """Draws a cute plate with stacked golden pancakes, butter and maple syrup."""
    # White ceramic plate
    draw.ellipse([cx - 55, cy - 10, cx + 55, cy + 30], fill=(245, 246, 250), outline=(200, 200, 210), width=3)
    # Stack of 3 pancakes
    for pi in range(3):
        py = cy - 5 - pi * 10
        draw.ellipse([cx - 40, py - 8, cx + 40, py + 12], fill=(245, 205, 121), outline=(225, 177, 44), width=3)
    # Square butter pat on top
    draw.rectangle([cx - 10, cy - 35, cx + 10, cy - 20], fill=(255, 242, 0), outline=(225, 177, 44), width=2)


def render_scene_1_secret(draw, t_sec: float, title_font, banner_font, sub_font, hud_font):
    """Scene 1: The 1,000 MPH Secret - Bob Eating Morning Pancakes."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Cozy pastel breakfast room
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(254, 249, 231))
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(247, 215, 148))
    draw.line([(0, HEIGHT - 220), (WIDTH, HEIGHT - 220)], fill=(225, 177, 44), width=6)

    # Kitchen dining table
    table_x, table_y = cx + 80, cy + 180
    draw.rounded_rectangle([table_x - 140, table_y, table_x + 140, table_y + 120], radius=15, fill=(205, 133, 63), outline=(40, 30, 30), width=5)

    # Bob happily sitting eating pancakes
    bob_x, bob_y = cx - 100, cy + 40
    draw_bob(draw, bob_x, bob_y, mood="happy", t_sec=t_sec, pose="sitting")

    # Pancakes on table
    draw_pancakes(draw, table_x, table_y - 10)

    # Mini Hologram Earth spinning on left
    earth_cx, earth_cy = 280, cy + 20
    draw.ellipse([earth_cx - 130, earth_cy - 130, earth_cx + 130, earth_cy + 130], fill=(30, 55, 153), outline=(0, 206, 201), width=6)
    # Continents
    draw.chord([earth_cx - 100, earth_cy - 90, earth_cx + 30, earth_cy + 40], start=180, end=360, fill=(46, 204, 113))
    draw.chord([earth_cx + 10, earth_cy - 30, earth_cx + 100, earth_cy + 80], start=180, end=360, fill=(46, 204, 113))
    # Spinning orbital speed arrows
    spin_ang = t_sec * 4.0
    for ai in range(4):
        a_rad = spin_ang + ai * (math.pi / 2.0)
        ax = earth_cx + int(160 * math.cos(a_rad))
        ay = earth_cy + int(160 * math.sin(a_rad))
        draw.ellipse([ax - 8, ay - 8, ax + 8, ay + 8], fill=(255, 234, 167))

    # HUD speed badge
    draw_studio_pill(draw, earth_cx, earth_cy + 180, "SPEED: 1,670 KM/H (1,000 MPH)", hud_font, fill=(30, 39, 46), text_fill=(254, 202, 87), pad_x=25, pad_y=10)

    # Clean Flat Studio Pills (NO harsh white borders)
    draw_studio_pill(draw, cx, 55, "WHAT HAPPENS IF THE EARTH STOPS SPINNING?", title_font, fill=(255, 71, 87))
    draw_studio_pill(draw, cx, 135, "THE 1,000 MPH SECRET YOU NEVER FEEL", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))


def render_scene_2_halt(draw, t_sec: float, title_font, banner_font, sub_font, hud_font):
    """Scene 2: Second 0.01 - The Sudden Cosmic Halt & Catapult Launch!"""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # High-intensity speed streak background
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(235, 77, 75))

    # Fast motion speed lines across the screen
    np.random.seed(42)
    for li in range(35):
        lx = int((li * 65 + t_sec * 800) % WIDTH)
        ly = int(np.random.uniform(50, HEIGHT - 50))
        draw.line([(lx, ly), (lx + 220, ly)], fill=(255, 255, 255, 180), width=4)

    # Bob launched horizontally like a human bullet!
    bob_t = (t_sec * 350.0) % (WIDTH + 600) - 300
    bob_y = cy + int(math.sin(t_sec * 8.0) * 25)
    draw_bob(draw, int(bob_t), bob_y, mood="shocked", t_sec=t_sec, pose="catapulted")

    # Pancakes flying in formation in front of Bob!
    draw_pancakes(draw, int(bob_t) + 160, bob_y)

    # Free-Floating Comic Action Text (NO BOX)
    draw_action_text(draw, cx, cy - 160, "CATAPULTED AT 1,000 MPH!", title_font, fill=(255, 234, 167), stroke_fill=(40, 20, 20), stroke_width=8)

    # Clean Flat Studio Pills
    draw_studio_pill(draw, cx, 55, "SECOND 0.01: THE COSMIC BRAKES SLAM!", title_font, fill=(45, 52, 54))
    draw_studio_pill(draw, cx, 135, "PLANET HALTS BUT INERTIA KEEPS HURTLING!", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))


def render_scene_3_winds(draw, t_sec: float, title_font, banner_font, sub_font, hud_font):
    """Scene 3: Second 2 - Global Supersonic Mega-Hurricane Winds."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Moody sky with sweeping cyan and purple storm winds
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(47, 53, 66))

    # Sweeping gale-force wind spirals
    for wi in range(12):
        w_y = int((wi * 85 + t_sec * 50) % (HEIGHT - 100)) + 60
        w_off = int((t_sec * 900) % 400)
        draw.arc([-200 + w_off, w_y - 40, WIDTH + 200 + w_off, w_y + 40], start=0, end=180, fill=(116, 185, 255), width=6)

    # Skyscrapers in background bending slightly with wind
    skyscrapers = [(200, 450, 160), (450, 380, 200), (WIDTH - 400, 420, 220), (WIDTH - 150, 480, 150)]
    for sx, sh, sw in skyscrapers:
        draw.rectangle([sx - sw // 2, HEIGHT - sh, sx + sw // 2, HEIGHT], fill=(30, 39, 46))
        # Street sign spinning past
        draw.rectangle([sx - 20, HEIGHT - sh - 50, sx + 20, HEIGHT - sh - 20], fill=(255, 234, 167))

    # Bob flying horizontally through the hurricane with goggles!
    bob_x = cx - 40
    bob_y = cy + 20 + int(math.sin(t_sec * 6.0) * 30)
    draw_bob(draw, bob_x, bob_y, mood="shocked", t_sec=t_sec, pose="catapulted")
    # Still clutching his pancake plate
    draw_pancakes(draw, bob_x + 150, bob_y)

    # Free-Floating Sound Effect (NO BOX)
    draw_action_text(draw, cx + 220, cy - 140, "WHOOSH!", title_font, fill=(255, 234, 167), stroke_fill=(30, 30, 50), stroke_width=8)

    # Clean Flat Studio Pills
    draw_studio_pill(draw, cx, 55, "SECOND 2: SUPERSONIC MEGA-HURRICANE!", title_font, fill=(9, 132, 227))
    draw_studio_pill(draw, cx, 135, "ATMOSPHERE CREATES 1,000 MPH WINDS!", banner_font, fill=(0, 206, 201), text_fill=(20, 20, 20))


def render_scene_4_tsunami(draw, t_sec: float, title_font, banner_font, sub_font, hud_font):
    """Scene 4: Second 3 - The Ocean Megatsunami & Table Surfing."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Coastal sky with colossal tidal wave
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(130, 204, 221))

    # Giant Colossal Megatsunami Wave
    wave_pulse = int(math.sin(t_sec * 4.0) * 35)
    wave_crest_y = cy - 40 + wave_pulse
    draw.chord([-300, wave_crest_y, WIDTH + 300, HEIGHT + 600], start=180, end=360, fill=(9, 132, 227))
    # Sparkling white foam crest
    for fx in range(-50, WIDTH + 100, 70):
        fy = wave_crest_y + int(math.sin(t_sec * 5.0 + fx) * 15)
        draw.ellipse([fx - 35, fy - 25, fx + 35, fy + 25], fill=(255, 255, 255))

    # Bob surfing on a floating wooden dining table like a pro!
    surf_x = cx - 120
    surf_y = wave_crest_y - 90
    # Wooden dining table as surfboard
    draw.rounded_rectangle([surf_x - 120, surf_y + 120, surf_x + 120, surf_y + 145], radius=10, fill=(205, 133, 63), outline=(40, 30, 30), width=4)
    draw_bob(draw, surf_x, surf_y, mood="sunglasses", t_sec=t_sec, pose="surfing")

    # Cute Dolphin leaping beside Bob with sunglasses!
    dolph_x = cx + 240 + int(math.sin(t_sec * 3.0) * 40)
    dolph_y = wave_crest_y - 60 + int(math.cos(t_sec * 4.0) * 40)
    draw.ellipse([dolph_x - 65, dolph_y - 30, dolph_x + 65, dolph_y + 30], fill=(116, 185, 255), outline=(40, 30, 30), width=4)
    # Dolphin snout & sunglasses
    draw.polygon([(dolph_x + 50, dolph_y - 10), (dolph_x + 85, dolph_y), (dolph_x + 50, dolph_y + 10)], fill=(116, 185, 255))
    draw.rounded_rectangle([dolph_x + 10, dolph_y - 18, dolph_x + 45, dolph_y - 2], radius=6, fill=(30, 30, 30))

    # Free-Floating Comic Action Text
    draw_action_text(draw, cx, cy - 210, "TSUNAMI SURF!", title_font, fill=(255, 234, 167), stroke_fill=(9, 132, 227), stroke_width=8)

    # Clean Flat Studio Pills
    draw_studio_pill(draw, cx, 55, "SECOND 3: THE OCEAN MEGATSUNAMI!", title_font, fill=(0, 168, 255))
    draw_studio_pill(draw, cx, 135, "TRILLIONS OF TONS OF SLOSHING OCEAN WATER", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))


def render_scene_5_restart(draw, t_sec: float, title_font, banner_font, sub_font, hud_font):
    """Scene 5: Second 5 - The Spin Restarts & Giant Marshmallow Foam Pit."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # High-energy radiant gold and amber background
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(255, 234, 167))

    # Giant Bouncy Marshmallow Foam Pit at Bottom!
    pit_y = cy + 100
    draw.rounded_rectangle([120, pit_y, WIDTH - 120, HEIGHT - 60], radius=35, fill=(255, 175, 175), outline=(235, 77, 75), width=6)
    # Individual fluffy marshmallows
    np.random.seed(88)
    for mi in range(40):
        mx = 180 + int((mi * 45) % (WIDTH - 360))
        my = pit_y + 30 + int((mi * 25) % 180)
        draw.ellipse([mx - 30, my - 20, mx + 30, my + 20], fill=(255, 255, 255), outline=(240, 200, 200), width=2)

    # Bob happily sunken into the marshmallow pit, smiling, holding intact pancakes!
    bob_x, bob_y = cx, pit_y + 20
    draw_bob(draw, bob_x, bob_y, mood="happy", t_sec=t_sec, pose="sitting")
    draw_pancakes(draw, bob_x + 90, bob_y + 80)

    # Planetary Tire Screech Action Text (Free-Floating with 3D drop shadow)
    draw_action_text(draw, cx, cy - 180, "SKRRRRRRRT!", title_font, fill=(235, 77, 75), stroke_fill=(255, 255, 255), stroke_width=10)

    # Clean Flat Studio Pills
    draw_studio_pill(draw, cx, 55, "SECOND 5: THE PLANET RESTARTS ITS MOTOR!", title_font, fill=(235, 77, 75))
    draw_studio_pill(draw, cx, 135, "BOB CRASH-LANDS SAFELY INTO MARSHMALLOW PIT", banner_font, fill=(46, 204, 113), text_fill=(255, 255, 255))


def render_scene_6_outro(draw, t_sec: float, title_font, banner_font, sub_font, hud_font):
    """Scene 6: Outro - The Cosmic Seatbelt & Interactive Subscribe."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Royal midnight purple studio backdrop
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(30, 27, 75))

    # Golden stage spotlights
    for spot_x, spot_col in [(350, (251, 191, 36)), (WIDTH - 350, (192, 132, 252))]:
        draw.polygon([(spot_x, 0), (spot_x - 300, HEIGHT), (spot_x + 300, HEIGHT)], fill=(spot_col[0]//5, spot_col[1]//5, spot_col[2]//5))

    # Bob giving double thumbs up on left
    bob_x, bob_y = cx - 360, cy + 80
    draw_bob(draw, bob_x, bob_y, mood="happy", t_sec=t_sec, pose="standing")

    # Interactive YouTube Subscribe Button (Flat, NO harsh white border)
    is_clicked = t_sec >= 3.0
    btn_color = (60, 60, 60) if is_clicked else (235, 77, 75)
    btn_text = "SUBSCRIBED" if is_clicked else "SUBSCRIBE"

    sub_box = [cx - 60, cy - 60, cx + 460, cy + 60]
    draw.rounded_rectangle(sub_box, radius=25, fill=btn_color)
    draw_action_text(draw, cx + 160, cy, btn_text, title_font, fill=(255, 255, 255), stroke_width=0)

    # Golden Vector Bell
    bell_tilt = math.sin(t_sec * 16.0) * 12.0 if is_clicked else 0.0
    draw_vector_bell(draw, cx + 390, cy, r=26, fill=(254, 202, 87), tilt=bell_tilt)

    # Flat Blue Like Button
    like_box = [cx - 60, cy + 90, cx + 460, cy + 180]
    draw.rounded_rectangle(like_box, radius=20, fill=(30, 144, 255))
    draw_vector_thumbs_up(draw, cx + 30, cy + 135, size=24)
    draw_action_text(draw, cx + 240, cy + 135, "LIKE THIS VIDEO!", banner_font, fill=(255, 255, 255), stroke_width=0)

    # Clean Flat Studio Pills
    draw_studio_pill(draw, cx, 55, "WHERE WOULD YOU HIDE FOR 5 SECONDS?", title_font, fill=(255, 71, 87))
    draw_studio_pill(draw, cx, 135, "TELL US IN THE COMMENTS BELOW!", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))


def render_masterpiece_frame(frame_idx: int, scene_bounds: list, title_font, banner_font, sub_font, hud_font) -> Image.Image:
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
        render_scene_1_secret(draw, t_local, title_font, banner_font, sub_font, hud_font)
    elif scene_idx == 1:
        render_scene_2_halt(draw, t_local, title_font, banner_font, sub_font, hud_font)
    elif scene_idx == 2:
        render_scene_3_winds(draw, t_local, title_font, banner_font, sub_font, hud_font)
    elif scene_idx == 3:
        render_scene_4_tsunami(draw, t_local, title_font, banner_font, sub_font, hud_font)
    elif scene_idx == 4:
        render_scene_5_restart(draw, t_local, title_font, banner_font, sub_font, hud_font)
    else:
        render_scene_6_outro(draw, t_local, title_font, banner_font, sub_font, hud_font)

    return img


def produce_earth_stopped_spinning_masterpiece():
    logger.info("🎬 Rendering Studio-Grade Cartoon: 'What Happens If The Earth Stopped Spinning For 5 Seconds?'...")

    voice_path = str(TEMP_DIR / "spin_full_voice.m4a")
    music_path = str(TEMP_DIR / "spin_cartoon_music.wav")

    if not os.path.exists(voice_path):
        raise FileNotFoundError(f"Master voiceover track missing: {voice_path}")
    if not os.path.exists(music_path):
        raise FileNotFoundError(f"Cartoon music track missing: {music_path}")

    # Exact scene frame calculation for 0.000s timing drift
    scene_files = [str(TEMP_DIR / f"spin_scene{i}.m4a") for i in range(1, 7)]
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
    logger.info(f"⏱️ Video Duration: {total_duration:.2f}s (~1.8 mins) | Total Frames: {total_frames}")

    # Premium Fonts
    title_font = get_font(size=52, font_type="rounded")
    banner_font = get_font(size=34, font_type="rounded")
    sub_font = get_font(size=26, font_type="rounded")
    hud_font = get_font(size=24, font_type="futura")

    ffmpeg_bin = get_ffmpeg_binary()
    hw = detect_hardware()

    final_output = EXPORTS_DIR / "What_If_Earth_Stopped_Spinning_5s.mp4"
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
        frame_img = render_masterpiece_frame(frame_idx, scene_bounds, title_font, banner_font, sub_font, hud_font)
        process.stdin.write(frame_img.tobytes())

        if frame_idx % 250 == 0:
            pct = int((frame_idx / total_frames) * 100)
            logger.info(f"Rendering: {pct}% ({frame_idx}/{total_frames} frames)")

    process.stdin.close()
    process.wait()

    render_elapsed = time.time() - t0
    logger.success(f"Cartoon render completed in {render_elapsed:.1f}s ({total_frames / max(0.1, render_elapsed):.1f} fps)!")

    # High-CTR YouTube Thumbnail (1280x720 16:9)
    logger.info("🖼️ Creating High-CTR YouTube Thumbnail with Premium Typography...")
    cx, cy = WIDTH // 2, HEIGHT // 2
    thumb_path = EXPORTS_DIR / "Earth_Stopped_Spinning_Thumbnail.jpg"
    thumb_img = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 35))
    draw_th = ImageDraw.Draw(thumb_img)

    # Split screen composition: Left side normal breakfast / Right side supersonic inertia launch!
    draw_th.rectangle([0, 0, WIDTH // 2, HEIGHT], fill=(254, 249, 231))
    draw_th.rectangle([0, HEIGHT - 220, WIDTH // 2, HEIGHT], fill=(247, 215, 148))
    # Right half fiery supersonic void
    draw_th.rectangle([WIDTH // 2, 0, WIDTH, HEIGHT], fill=(235, 77, 75))

    # Split neon divider line
    draw_th.line([(WIDTH // 2, 0), (WIDTH // 2, HEIGHT)], fill=(0, 206, 201), width=12)

    # Bob launched horizontally right across the divider line!
    draw_bob(draw_th, WIDTH // 2, cy + 40, mood="shocked", t_sec=1.0, pose="catapulted")
    draw_pancakes(draw_th, WIDTH // 2 + 160, cy + 40)

    # Left side: Earth globe
    draw_th.ellipse([200 - 100, 260 - 100, 200 + 100, 260 + 100], fill=(30, 55, 153), outline=(0, 206, 201), width=6)
    draw_th.chord([200 - 80, 260 - 70, 200 + 30, 260 + 40], start=180, end=360, fill=(46, 204, 113))

    # Giant Impact Typography on Thumbnail (NO BOX - Clean drop shadow)
    thumb_font = get_font(size=78, font_type="rounded")
    draw_action_text(draw_th, cx, 75, "WHAT IF EARTH STOPPED SPINNING?", thumb_font, fill=(255, 255, 255), stroke_fill=(30, 30, 40), stroke_width=10)

    badge_font = get_font(size=48, font_type="rounded")
    draw_studio_pill(draw_th, cx, HEIGHT - 130, "5 SECONDS OF SUPERSONIC CHAOS!", badge_font, fill=(254, 202, 87), text_fill=(40, 30, 30), pad_x=45, pad_y=16)

    # Resize to standard 1280x720 thumbnail
    thumb_final = thumb_img.resize((1280, 720), Image.Resampling.LANCZOS)
    thumb_final.save(str(thumb_path), "JPEG", quality=95)
    thumb_png = EXPORTS_DIR / "Earth_Stopped_Spinning_Thumbnail.png"
    thumb_final.save(str(thumb_png), "PNG")

    info = get_video_info(str(final_output))
    logger.success("==================================================")
    logger.success("🎉 PRODUCTION-READY CARTOON MASTERPIECE READY!")
    logger.success(f"📍 Video File: {final_output}")
    logger.success(f"⏱️ Runtime: {info.get('duration', 0):.1f} seconds (Target: >90s)")
    logger.success(f"📐 Resolution: {info.get('width')}x{info.get('height')} 1080p Full HD")
    logger.success(f"🖼️ Thumbnail: {thumb_path}")
    logger.success("==================================================")

    return str(final_output), str(thumb_path)


if __name__ == "__main__":
    produce_earth_stopped_spinning_masterpiece()
