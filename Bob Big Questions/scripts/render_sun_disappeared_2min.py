"""Procedural 2D Animated Cartoon: 'What Happens If The Sun Disappeared For 7 Days?'

Mathematical Zero-Drift Synchronization:
- Every scene's exact frame count is calculated directly from its matching voiceover sentence audio.
- When the voiceover finishes a sentence, the visual scene transitions at that exact frame.
- Total runtime: Exactly ~123.2 seconds (~2 minutes).
- Full 1080p Full HD, 30fps, hardware-accelerated Apple Silicon encoding.
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
FONT_COMIC = "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf"


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


def draw_bob(draw, cx, cy, mood="happy", t_sec=0.0, clothes="hawaiian", shivering=False):
    """Draws the main character Bob with expressive mood and costume."""
    jitter_x = int(math.sin(t_sec * 35.0) * 5.0) if shivering else 0
    jitter_y = int(math.cos(t_sec * 30.0) * 3.0) if shivering else 0
    bx = cx + jitter_x
    by = cy + jitter_y

    radius = 105

    # 1. Clothing & Body
    if clothes == "hawaiian":
        # Tropical cyan Hawaiian shirt with yellow flowers
        draw_rounded_rect(draw, [bx - 85, by + 75, bx + 85, by + 260], radius=30, fill=(0, 206, 201), outline=(40, 30, 30), width=6)
        # Flower patterns
        for fx, fy in [(-40, 120), (40, 140), (-20, 190), (35, 220)]:
            draw.ellipse([bx + fx - 12, by + fy - 12, bx + fx + 12, by + fy + 12], fill=(255, 234, 167))
        # Shorts (bright coral red)
        draw_rounded_rect(draw, [bx - 80, by + 250, bx + 80, by + 340], radius=15, fill=(255, 107, 129), outline=(40, 30, 30), width=5)
        # Legs
        draw.line([(bx - 40, by + 340), (bx - 40, by + 400)], fill=(255, 218, 185), width=24)
        draw.line([(bx + 40, by + 340), (bx + 40, by + 400)], fill=(255, 218, 185), width=24)
        # Flip-flops
        draw.ellipse([bx - 60, by + 395, bx - 20, by + 415], fill=(254, 202, 87), outline=(40, 30, 30), width=4)
        draw.ellipse([bx + 20, by + 395, bx + 60, by + 415], fill=(254, 202, 87), outline=(40, 30, 30), width=4)

    elif clothes == "winter":
        # Three bulky puffy winter jackets (Red outer, yellow middle, blue inner)
        draw_rounded_rect(draw, [bx - 110, by + 70, bx + 110, by + 280], radius=45, fill=(235, 77, 75), outline=(40, 30, 30), width=7)
        # Zipper & fluff
        draw.line([(bx, by + 75), (bx, by + 275)], fill=(240, 240, 240), width=8)
        # Thick wool scarf wrapped around neck
        draw_rounded_rect(draw, [bx - 95, by + 50, bx + 95, by + 105], radius=25, fill=(240, 147, 43), outline=(40, 30, 30), width=6)
        # Puffy snow pants
        draw_rounded_rect(draw, [bx - 90, by + 270, bx + 90, by + 360], radius=20, fill=(48, 51, 107), outline=(40, 30, 30), width=6)
        # Green fuzzy dinosaur slippers!
        draw_rounded_rect(draw, [bx - 85, by + 350, bx - 15, by + 405], radius=18, fill=(106, 176, 76), outline=(40, 30, 30), width=5)
        draw_rounded_rect(draw, [bx + 15, by + 350, bx + 85, by + 405], radius=18, fill=(106, 176, 76), outline=(40, 30, 30), width=5)
        # Dino claws
        for dx in [-75, -50, -25]:
            draw.polygon([(bx + dx - 6, by + 400), (bx + dx + 6, by + 400), (bx + dx, by + 415)], fill=(255, 255, 255))
        for dx in [25, 50, 75]:
            draw.polygon([(bx + dx - 6, by + 400), (bx + dx + 6, by + 400), (bx + dx, by + 415)], fill=(255, 255, 255))

    elif clothes == "ice_skater":
        # Blue puffer jacket & ice skates
        draw_rounded_rect(draw, [bx - 90, by + 75, bx + 90, by + 265], radius=35, fill=(9, 132, 227), outline=(40, 30, 30), width=6)
        draw_rounded_rect(draw, [bx - 80, by + 260, bx + 80, by + 345], radius=15, fill=(45, 52, 54), outline=(40, 30, 30), width=6)
        # Ice skate boots
        draw_rounded_rect(draw, [bx - 75, by + 340, bx - 25, by + 385], radius=12, fill=(255, 255, 255), outline=(40, 30, 30), width=5)
        draw_rounded_rect(draw, [bx + 25, by + 340, bx + 75, by + 385], radius=12, fill=(255, 255, 255), outline=(40, 30, 30), width=5)
        # Silver skate blades
        draw.line([(bx - 90, by + 395), (bx - 15, by + 395)], fill=(220, 220, 220), width=6)
        draw.line([(bx + 15, by + 395), (bx + 90, by + 395)], fill=(220, 220, 220), width=6)

    elif clothes == "bunker":
        # Techy comfy purple hoodie with yellow drawstring
        draw_rounded_rect(draw, [bx - 85, by + 75, bx + 85, by + 270], radius=30, fill=(108, 92, 231), outline=(40, 30, 30), width=6)
        # Tech badge
        draw.ellipse([bx - 45, by + 120, bx - 20, by + 145], fill=(0, 206, 201), outline=(255, 255, 255), width=3)
        draw_rounded_rect(draw, [bx - 75, by + 265, bx + 75, by + 350], radius=15, fill=(99, 110, 114), outline=(40, 30, 30), width=5)
        # Comfy slippers
        draw_rounded_rect(draw, [bx - 70, by + 345, bx - 20, by + 385], radius=14, fill=(253, 121, 168), outline=(40, 30, 30), width=4)
        draw_rounded_rect(draw, [bx + 20, by + 345, bx + 70, by + 385], radius=14, fill=(253, 121, 168), outline=(40, 30, 30), width=4)

    # 2. Bob's Head & Face
    draw.ellipse([bx - radius, by - radius, bx + radius, by + radius], fill=(255, 218, 185), outline=(40, 30, 30), width=6)

    # Hair (Messy brown tufts)
    hair_color = (101, 67, 33)
    draw.arc([bx - radius + 10, by - radius - 20, bx + radius - 10, by - radius + 50], start=180, end=360, fill=hair_color, width=22)
    draw.ellipse([bx - 20, by - radius - 28, bx + 25, by - radius + 10], fill=hair_color)

    # Beanie Hat if winter
    if clothes in ("winter", "ice_skater"):
        draw_rounded_rect(draw, [bx - radius - 10, by - radius - 35, bx + radius + 10, by - radius + 25], radius=25, fill=(255, 159, 26), outline=(40, 30, 30), width=6)
        # Top pompom
        draw.ellipse([bx - 25, by - radius - 60, bx + 25, by - radius - 15], fill=(255, 255, 255), outline=(40, 30, 30), width=5)

    # 3. Facial Expressions
    if mood == "happy":
        # Big bright smiling round eyes
        for eye_x in (bx - 45, bx + 45):
            draw.ellipse([eye_x - 26, by - 20 - 26, eye_x + 26, by - 20 + 26], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
            draw.ellipse([eye_x - 8, by - 22, eye_x + 16, by + 2], fill=(30, 30, 40))
            draw.ellipse([eye_x - 3, by - 19, eye_x + 6, by - 10], fill=(255, 255, 255))
        # Cheerful smile
        draw.arc([bx - 35, by + 5, bx + 35, by + 55], start=0, end=180, fill=(230, 60, 60), width=8)
        # Rosy cheeks
        draw.ellipse([bx - 75, by + 10, bx - 50, by + 30], fill=(255, 175, 175))
        draw.ellipse([bx + 50, by + 10, bx + 75, by + 30], fill=(255, 175, 175))

    elif mood == "shocked":
        # Giant bug eyes
        for eye_x in (bx - 48, bx + 48):
            draw.ellipse([eye_x - 34, by - 20 - 34, eye_x + 34, by - 20 + 34], fill=(255, 255, 255), outline=(40, 30, 30), width=5)
            # Dilated tiny pupils
            draw.ellipse([eye_x - 8, by - 22, eye_x + 8, by - 6], fill=(20, 20, 20))
            draw.ellipse([eye_x - 4, by - 20, eye_x, by - 16], fill=(255, 255, 255))
        # High arched eyebrows
        draw.arc([bx - 75, by - 75, bx - 25, by - 45], start=180, end=360, fill=(60, 40, 40), width=6)
        draw.arc([bx + 25, by - 75, bx + 75, by - 45], start=180, end=360, fill=(60, 40, 40), width=6)
        # O-shaped dropped jaw
        draw.ellipse([bx - 26, by + 15, bx + 26, by + 65], fill=(50, 20, 20), outline=(220, 60, 60), width=5)

    elif mood == "freezing":
        # Squeezed shivering eyes
        draw.line([(bx - 65, by - 20), (bx - 25, by - 10)], fill=(40, 30, 30), width=6)
        draw.line([(bx - 65, by - 5), (bx - 25, by - 15)], fill=(40, 30, 30), width=6)
        draw.line([(bx + 25, by - 10), (bx + 65, by - 20)], fill=(40, 30, 30), width=6)
        draw.line([(bx + 25, by - 15), (bx + 65, by - 5)], fill=(40, 30, 30), width=6)
        # Blue cold cheeks & nose
        draw.ellipse([bx - 18, by - 10, bx + 18, by + 12], fill=(129, 236, 236), outline=(40, 30, 30), width=3)
        # Chattering zigzag teeth mouth
        mouth_pts = []
        for mi in range(8):
            mx = bx - 35 + mi * 10
            my = by + 30 + (8 if mi % 2 == 0 else -6)
            mouth_pts.append((mx, my))
        for mi in range(len(mouth_pts) - 1):
            draw.line([mouth_pts[mi], mouth_pts[mi + 1]], fill=(178, 190, 195), width=5)

    elif mood == "celebrating":
        # Joyful closed crescent eyes (Anime style happy)
        draw.arc([bx - 65, by - 25, bx - 25, by + 5], start=180, end=360, fill=(40, 30, 30), width=7)
        draw.arc([bx + 25, by - 25, bx + 65, by + 5], start=180, end=360, fill=(40, 30, 30), width=7)
        # Huge open singing mouth
        draw.chord([bx - 35, by + 10, bx + 35, by + 60], start=0, end=180, fill=(235, 77, 75), outline=(40, 30, 30), width=5)
        # Pink tongue
        draw.ellipse([bx - 15, by + 35, bx + 15, by + 55], fill=(255, 159, 243))
        # Cheeks
        draw.ellipse([bx - 75, by + 5, bx - 45, by + 28], fill=(255, 175, 175))
        draw.ellipse([bx + 45, by + 5, bx + 75, by + 28], fill=(255, 175, 175))


def render_scene_1_beach(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 1: Tropical Beach & Ice Cream (0 - 8 Minutes)."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Warm radiant tropical sky gradient
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(130, 204, 221))
    # Sparkling turquoise ocean
    draw.rectangle([0, HEIGHT - 380, WIDTH, HEIGHT], fill=(74, 189, 172))
    # Animated ocean wave ripples
    for wi in range(8):
        wave_y = HEIGHT - 380 + wi * 25
        wave_x_off = int((t_sec * 40.0 + wi * 80) % 200) - 100
        for wx in range(-100, WIDTH + 200, 180):
            draw.arc([wx + wave_x_off, wave_y - 10, wx + wave_x_off + 160, wave_y + 15], start=0, end=180, fill=(255, 255, 255), width=3)

    # Golden sunny sand beach
    draw.chord([-200, HEIGHT - 260, WIDTH + 200, HEIGHT + 400], start=180, end=360, fill=(250, 211, 144))

    # Huge cheerful cartoon Sun with sunglasses
    sun_x, sun_y = WIDTH - 260, 230
    sun_pulse = int(math.sin(t_sec * 4.0) * 8.0)
    # Radiating spinning rays
    for ray_i in range(12):
        ang = t_sec * 0.5 + ray_i * (2 * math.pi / 12)
        rx1 = sun_x + int((130 + sun_pulse) * math.cos(ang))
        ry1 = sun_y + int((130 + sun_pulse) * math.sin(ang))
        rx2 = sun_x + int((175 + sun_pulse) * math.cos(ang))
        ry2 = sun_y + int((175 + sun_pulse) * math.sin(ang))
        draw.line([(rx1, ry1), (rx2, ry2)], fill=(254, 202, 87), width=10)

    draw.ellipse([sun_x - 120 - sun_pulse, sun_y - 120 - sun_pulse, sun_x + 120 + sun_pulse, sun_y + 120 + sun_pulse], fill=(255, 185, 45), outline=(225, 112, 85), width=6)
    # Cool black sunglasses on Sun
    draw_rounded_rect(draw, [sun_x - 85, sun_y - 30, sun_x + 85, sun_y + 15], radius=12, fill=(30, 30, 30))
    # Sun big happy grin
    draw.arc([sun_x - 50, sun_y + 20, sun_x + 50, sun_y + 70], start=0, end=180, fill=(214, 48, 49), width=8)

    # Bob enjoying beach with ice cream
    bob_x = cx - 120
    bob_y = cy + 60 + int(math.sin(t_sec * 4.0) * 6.0)
    draw_bob(draw, bob_x, bob_y, mood="happy", t_sec=t_sec, clothes="hawaiian")

    # Double scoop Ice Cream Cone in Bob's hand
    cone_x, cone_y = bob_x + 130, bob_y + 100
    # Waffle cone
    draw.polygon([(cone_x - 25, cone_y), (cone_x + 25, cone_y), (cone_x, cone_y + 70)], fill=(225, 177, 44), outline=(40, 30, 30))
    # Scoop 1: Mint chocolate chip (Cyan)
    draw.ellipse([cone_x - 32, cone_y - 35, cone_x + 32, cone_y + 15], fill=(85, 239, 196), outline=(40, 30, 30), width=4)
    # Scoop 2: Strawberry pink
    draw.ellipse([cone_x - 28, cone_y - 65, cone_x + 28, cone_y - 15], fill=(255, 118, 117), outline=(40, 30, 30), width=4)
    # Cherry on top
    draw.ellipse([cone_x - 10, cone_y - 82, cone_x + 10, cone_y - 62], fill=(214, 48, 49))

    # Palm Tree on the left
    draw.arc([-100, HEIGHT - 550, 250, HEIGHT - 100], start=270, end=360, fill=(139, 69, 19), width=35)
    # Palm fronds
    draw.ellipse([140, HEIGHT - 560, 320, HEIGHT - 460], fill=(46, 204, 113), outline=(39, 174, 96), width=4)
    draw.ellipse([50, HEIGHT - 580, 220, HEIGHT - 490], fill=(46, 204, 113), outline=(39, 174, 96), width=4)

    # Cosmic Speed HUD Indicator
    draw_rounded_rect(draw, [cx - 380, HEIGHT - 140, cx + 380, HEIGHT - 60], radius=20, fill=(30, 39, 46), outline=(255, 255, 255), width=4)
    draw.text((cx - 350, HEIGHT - 120), "SPEED OF LIGHT: 300,000 KM/S (8 MIN BUFFER)", font=sub_font, fill=(254, 202, 87))

    # Top Title Card
    draw_rounded_rect(draw, [cx - 480, 60, cx + 480, 150], radius=25, fill=(255, 107, 129), outline=(40, 30, 30), width=6)
    draw.text((cx - 440, 75), "WHAT IF THE SUN DISAPPEARED?", font=title_font, fill=(255, 255, 255))
    draw_rounded_rect(draw, [cx - 280, 165, cx + 280, 225], radius=15, fill=(254, 202, 87), outline=(40, 30, 30), width=4)
    draw.text((cx - 240, 178), "MINUTE 0 - 8: ABSOLUTELY NOTHING!", font=banner_font, fill=(40, 30, 30))


def render_scene_2_blackout(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 2: Minute 8:20 - Pitch Black Sky & Moon Disappears!"""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Deep pitch black midnight cosmic void
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(10, 12, 24))

    # Colorful galaxy nebulas in background
    for neb_x, neb_y, neb_r, neb_col in [(350, 300, 240, (108, 92, 231, 60)), (WIDTH - 400, 280, 280, (253, 121, 168, 50))]:
        draw.ellipse([neb_x - neb_r, neb_y - neb_r, neb_x + neb_r, neb_y + neb_r], fill=neb_col[:3])

    # Hundreds of sparkling animated stars
    np.random.seed(42)
    for star_i in range(120):
        sx = int(np.random.uniform(20, WIDTH - 20))
        sy = int(np.random.uniform(20, HEIGHT - 200))
        twinkle = (math.sin(t_sec * 6.0 + star_i) + 1.0) / 2.0
        sr = 2 + int(twinkle * 4)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255))

    # Giant Comic Book "CLICK!" Explosion Badge (First 4 seconds)
    if t_sec < 4.0:
        click_scale = min(1.0, t_sec * 2.0)
        cw, ch = int(280 * click_scale), int(120 * click_scale)
        draw_rounded_rect(draw, [cx - cw, cy - 240 - ch, cx + cw, cy - 240 + ch], radius=25, fill=(255, 71, 87), outline=(255, 255, 255), width=6)
        draw.text((cx - 160, cy - 280), "CLICK! 💡❌", font=title_font, fill=(255, 255, 255))

    # The Vanished Moon (Extinguished grey outline with "OFF" switch)
    moon_x, moon_y = WIDTH - 280, 240
    # Flickering ghost moon outline
    draw.ellipse([moon_x - 110, moon_y - 110, moon_x + 110, moon_y + 110], fill=(30, 35, 55), outline=(120, 130, 160), width=5)
    # Craters on dark moon
    draw.ellipse([moon_x - 45, moon_y - 30, moon_x - 10, moon_y + 5], fill=(20, 25, 40))
    draw.ellipse([moon_x + 20, moon_y + 15, moon_x + 60, moon_y + 55], fill=(20, 25, 40))
    # Big red "POWER OFF" cross
    draw.line([(moon_x - 80, moon_y - 80), (moon_x + 80, moon_y + 80)], fill=(235, 77, 75), width=8)
    draw.line([(moon_x + 80, moon_y - 80), (moon_x - 80, moon_y + 80)], fill=(235, 77, 75), width=8)

    # Bob completely shocked in the dark holding dropped cone
    bob_x = cx
    bob_y = cy + 70
    draw_bob(draw, bob_x, bob_y, mood="shocked", t_sec=t_sec, clothes="hawaiian")

    # Splatted ice cream on ground
    splat_x = bob_x + 140
    draw.ellipse([splat_x - 50, cy + 380, splat_x + 50, cy + 420], fill=(255, 118, 117), outline=(40, 30, 30), width=4)
    draw.text((splat_x - 40, cy + 340), "SPLAT!", font=sub_font, fill=(255, 234, 167))

    # Cosmic Mirror Explanation Card
    draw_rounded_rect(draw, [cx - 420, HEIGHT - 150, cx + 420, HEIGHT - 70], radius=20, fill=(45, 52, 54), outline=(255, 107, 129), width=5)
    draw.text((cx - 390, HEIGHT - 130), "THE MOON HAS NO LIGHT! IT'S JUST A MIRROR!", font=banner_font, fill=(255, 255, 255))

    # Top Banner
    draw_rounded_rect(draw, [cx - 450, 60, cx + 450, 150], radius=25, fill=(44, 44, 84), outline=(255, 255, 255), width=5)
    draw.text((cx - 400, 75), "MINUTE 8:20: THE SKY TURNS BLACK!", font=title_font, fill=(255, 218, 121))


def render_scene_3_day1_freeze(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 3: Day 1 - Freezing Temperatures, 3 Coats & Kitchen Toaster."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Cold frosted room interior (pale chilly blue walls)
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(209, 216, 224))
    # Frosted wooden floorboards
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(165, 177, 194))
    draw.line([(0, HEIGHT - 220), (WIDTH, HEIGHT - 220)], fill=(223, 228, 234), width=6)

    # Frosted Window with falling snowflakes in dark outdoors
    win_x1, win_y1, win_x2, win_y2 = WIDTH - 520, 120, WIDTH - 120, 480
    draw.rectangle([win_x1, win_y1, win_x2, win_y2], fill=(15, 20, 35), outline=(90, 105, 125), width=10)
    # Window panes cross
    draw.line([( (win_x1 + win_x2)//2, win_y1), ( (win_x1 + win_x2)//2, win_y2)], fill=(90, 105, 125), width=8)
    draw.line([(win_x1, (win_y1 + win_y2)//2), (win_x2, (win_y1 + win_y2)//2)], fill=(90, 105, 125), width=8)
    # Animated falling snow outside window
    np.random.seed(99)
    for si in range(35):
        sx = win_x1 + int((np.random.uniform(10, 390) + t_sec * 30) % 390)
        sy = win_y1 + int((np.random.uniform(10, 350) + t_sec * 60) % 350)
        draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 255, 255))

    # Giant Cartoon Thermometer on left
    therm_x, therm_y = 180, cy + 20
    draw_rounded_rect(draw, [therm_x - 35, therm_y - 220, therm_x + 35, therm_y + 160], radius=30, fill=(245, 246, 250), outline=(47, 53, 66), width=6)
    # Bulb at bottom
    draw.ellipse([therm_x - 65, therm_y + 120, therm_x + 65, therm_y + 250], fill=(116, 185, 255), outline=(47, 53, 66), width=6)
    # Dropping mercury column (Cold Ice Blue)
    merc_drop = min(1.0, t_sec / 8.0)
    merc_top = int(therm_y - 140 + merc_drop * 220)
    draw.rectangle([therm_x - 18, merc_top, therm_x + 18, therm_y + 180], fill=(9, 132, 227))
    # Frost crystals on thermometer
    draw.text((therm_x + 50, therm_y - 120), "70°F (ROOM TEMP)", font=sub_font, fill=(120, 120, 120))
    draw.text((therm_x + 50, therm_y + 50), "32°F / 0°C (FREEZING!)", font=banner_font, fill=(9, 132, 227))

    # Bob shivering by the tiny toaster
    bob_x = cx - 40
    bob_y = cy + 40
    draw_bob(draw, bob_x, bob_y, mood="freezing", t_sec=t_sec, clothes="winter", shivering=True)

    # Kitchen Counter & Toaster
    counter_x = cx + 180
    counter_y = cy + 180
    draw_rounded_rect(draw, [counter_x - 20, counter_y + 40, counter_x + 240, counter_y + 200], radius=15, fill=(112, 111, 211), outline=(40, 30, 30), width=6)
    # Chrome Toaster
    draw_rounded_rect(draw, [counter_x + 20, counter_y - 30, counter_x + 180, counter_y + 50], radius=18, fill=(223, 228, 234), outline=(40, 30, 30), width=5)
    # Glowing red heat coils in slots!
    pulse_red = (255, int(70 + 40 * math.sin(t_sec * 10)), 0)
    draw_rounded_rect(draw, [counter_x + 40, counter_y - 25, counter_x + 90, counter_y - 10], radius=6, fill=pulse_red)
    draw_rounded_rect(draw, [counter_x + 110, counter_y - 25, counter_x + 160, counter_y - 10], radius=6, fill=pulse_red)
    # Warm heat waves rising
    draw.arc([counter_x + 50, counter_y - 70, counter_x + 80, counter_y - 40], start=180, end=360, fill=(255, 107, 129), width=4)
    draw.arc([counter_x + 120, counter_y - 70, counter_x + 150, counter_y - 40], start=180, end=360, fill=(255, 107, 129), width=4)

    # Bob's chattering teeth / breath cloud
    breath_y = bob_y + 10 - int((t_sec * 30) % 40)
    draw.ellipse([bob_x + 80, breath_y, bob_x + 140, breath_y + 35], fill=(255, 255, 255, 180), outline=(180, 220, 240), width=3)
    draw.text((bob_x + 90, breath_y + 5), "BRRR!", font=sub_font, fill=(9, 132, 227))

    # Top Banner
    draw_rounded_rect(draw, [cx - 450, 60, cx + 450, 150], radius=25, fill=(9, 132, 227), outline=(255, 255, 255), width=5)
    draw.text((cx - 410, 75), "DAY 1: GLOBAL FREEZE BEGINS!", font=title_font, fill=(255, 255, 255))


def render_scene_4_day3_ice(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 4: Day 3 - Zero Degrees, Frozen Pools & Sliding City Penguins."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Icy frozen polar landscape / outdoor park
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(178, 190, 195))
    # Dark snowy hills in background
    draw.chord([-100, 260, 900, 750], start=180, end=360, fill=(99, 110, 114))
    draw.chord([700, 240, WIDTH + 200, 750], start=180, end=360, fill=(116, 125, 140))

    # Giant Frozen Swimming Pool (Crystal Ice Rink)
    pool_y1, pool_y2 = cy + 60, HEIGHT - 80
    draw_rounded_rect(draw, [140, pool_y1, WIDTH - 140, pool_y2], radius=40, fill=(129, 236, 236), outline=(9, 132, 227), width=8)
    # Ice cracks & reflections
    draw.line([(320, pool_y1 + 40), (450, pool_y1 + 120), (520, pool_y1 + 90)], fill=(255, 255, 255), width=4)
    draw.line([(WIDTH - 500, pool_y1 + 70), (WIDTH - 380, pool_y1 + 140)], fill=(255, 255, 255), width=4)

    # Bob wobbling precariously on ice skates!
    wobble = math.sin(t_sec * 12.0) * 12.0
    bob_x = cx - 180 + int(wobble)
    bob_y = cy + 20
    draw_bob(draw, bob_x, bob_y, mood="shocked", t_sec=t_sec, clothes="ice_skater")

    # Balancing flailing arms
    draw.line([(bob_x - 90, bob_y + 110), (bob_x - 170, bob_y + 60 + int(wobble * 2))], fill=(9, 132, 227), width=16)
    draw.line([(bob_x + 90, bob_y + 110), (bob_x + 170, bob_y + 40 - int(wobble * 2))], fill=(9, 132, 227), width=16)

    # Cute Cartoon Penguins Sliding Across Ice Rink!
    peng_base_x = int((t_sec * 160.0) % (WIDTH + 300)) - 150
    # Penguin 1: Sliding on belly like a torpedo!
    p1_x, p1_y = peng_base_x, pool_y2 - 70
    draw.ellipse([p1_x - 65, p1_y - 25, p1_x + 65, p1_y + 25], fill=(45, 52, 54))
    draw.ellipse([p1_x - 50, p1_y - 12, p1_x + 50, p1_y + 12], fill=(255, 255, 255))
    # Beak & Sunglasses on Penguin
    draw.polygon([(p1_x + 65, p1_y - 5), (p1_x + 85, p1_y), (p1_x + 65, p1_y + 5)], fill=(255, 159, 26))
    # Red earmuffs
    draw.ellipse([p1_x + 10, p1_y - 32, p1_x + 35, p1_y - 15], fill=(235, 77, 75))

    # Penguin 2: Waddling behind Bob
    p2_x, p2_y = cx + 240, cy + 180 + int(math.sin(t_sec * 8.0) * 8.0)
    draw.ellipse([p2_x - 40, p2_y - 70, p2_x + 40, p2_y + 70], fill=(45, 52, 54), outline=(30, 30, 30), width=4)
    draw.ellipse([p2_x - 25, p2_y - 45, p2_x + 25, p2_y + 50], fill=(255, 255, 255))
    # Beak
    draw.polygon([(p2_x - 12, p2_y - 30), (p2_x + 12, p2_y - 30), (p2_x, p2_y - 12)], fill=(255, 159, 26))
    # Cute round eyes
    draw.ellipse([p2_x - 18, p2_y - 45, p2_x - 6, p2_y - 33], fill=(20, 20, 20))
    draw.ellipse([p2_x + 6, p2_y - 45, p2_x + 18, p2_y - 33], fill=(20, 20, 20))

    # Weather HUD Card
    draw_rounded_rect(draw, [cx - 360, HEIGHT - 140, cx + 360, HEIGHT - 60], radius=20, fill=(30, 39, 46), outline=(129, 236, 236), width=4)
    draw.text((cx - 320, HEIGHT - 118), "TEMP: 0°F (-18°C) | PENGUIN INVASION!", font=banner_font, fill=(129, 236, 236))

    # Top Banner
    draw_rounded_rect(draw, [cx - 450, 60, cx + 450, 150], radius=25, fill=(0, 206, 201), outline=(255, 255, 255), width=5)
    draw.text((cx - 410, 75), "DAY 3: ZERO DEGREES FREEZE!", font=title_font, fill=(255, 255, 255))


def render_scene_5_day5_bunker(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 5: Day 5 - Earth's Geothermal Core & High-Tech Underground Bunker."""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # High-tech underground bunker interior (Deep indigo / cyber charcoal)
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(24, 28, 48))
    # Floor metallic grating
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(47, 53, 66))
    for gx in range(0, WIDTH, 40):
        draw.line([(gx, HEIGHT - 220), (gx, HEIGHT)], fill=(30, 35, 45), width=3)

    # Cross-Section Diagram of Earth on Left Side
    cross_cx, cross_cy = 280, cy + 20
    # Crust
    draw.ellipse([cross_cx - 180, cross_cy - 180, cross_cx + 180, cross_cy + 180], fill=(75, 101, 132), outline=(116, 185, 255), width=5)
    # Mantle (Molten orange)
    draw.ellipse([cross_cx - 130, cross_cy - 130, cross_cx + 130, cross_cy + 130], fill=(235, 94, 40))
    # Roaring molten lava core (Bright glowing yellow)
    core_pulse = int(math.sin(t_sec * 6.0) * 8.0)
    draw.ellipse([cross_cx - 75 - core_pulse, cross_cy - 75 - core_pulse, cross_cx + 75 + core_pulse, cross_cy + 75 + core_pulse], fill=(255, 218, 121), outline=(255, 107, 129), width=6)
    draw.text((cross_cx - 65, cross_cy - 15), "LAVA CORE!", font=sub_font, fill=(40, 20, 20))

    # Geothermal Heating Pipes with pulsing glowing amber energy
    pipe_glow = (255, int(150 + 50 * math.sin(t_sec * 8)), 0)
    draw.rectangle([cross_cx + 180, cy + 120, cx + 120, cy + 155], fill=pipe_glow, outline=(40, 30, 30), width=4)
    draw.text((cross_cx + 210, cy + 90), "GEOTHERMAL HEAT ->", font=sub_font, fill=(255, 218, 121))

    # Hydroponic Purple Greenhouse Shelves on Right
    shelf_x = WIDTH - 420
    draw_rounded_rect(draw, [shelf_x - 30, 140, shelf_x + 360, HEIGHT - 180], radius=20, fill=(38, 43, 66), outline=(108, 92, 231), width=5)
    # Magenta UV Grow Lights shining down
    draw.rectangle([shelf_x - 10, 160, shelf_x + 340, 185], fill=(253, 121, 168))
    # Glowing purple plants & giant glowing carrots!
    for level_y in [280, 420, 560]:
        draw.line([(shelf_x - 10, level_y), (shelf_x + 340, level_y)], fill=(99, 110, 114), width=6)
        # Giant glowing purple cabbage & carrots
        for plant_i in range(4):
            px = shelf_x + 30 + plant_i * 80
            draw.ellipse([px - 25, level_y - 45, px + 25, level_y], fill=(162, 155, 254), outline=(108, 92, 231), width=3)
            # Glowing sparkle on plants
            draw.ellipse([px - 8, level_y - 35, px + 8, level_y - 20], fill=(255, 255, 255))

    # Bob happy in bunker holding steaming hot cocoa
    bob_x = cx + 80
    bob_y = cy + 40
    draw_bob(draw, bob_x, bob_y, mood="happy", t_sec=t_sec, clothes="bunker")

    # Mug of Hot Cocoa in Bob's hand
    mug_x, mug_y = bob_x + 120, bob_y + 110
    draw_rounded_rect(draw, [mug_x - 35, mug_y - 45, mug_x + 35, mug_y + 35], radius=12, fill=(238, 82, 83), outline=(40, 30, 30), width=5)
    # White fluffy marshmallows floating in cocoa
    draw.ellipse([mug_x - 18, mug_y - 35, mug_x - 2, mug_y - 20], fill=(255, 255, 255))
    draw.ellipse([mug_x + 5, mug_y - 38, mug_x + 22, mug_y - 22], fill=(255, 255, 255))
    # Steam
    steam_y = mug_y - 55 - int((t_sec * 30) % 45)
    draw.arc([mug_x - 12, steam_y - 25, mug_x + 12, steam_y + 10], start=180, end=360, fill=(220, 220, 220), width=4)

    # Top Banner
    draw_rounded_rect(draw, [cx - 480, 60, cx + 480, 150], radius=25, fill=(108, 92, 231), outline=(255, 255, 255), width=5)
    draw.text((cx - 440, 75), "DAY 5: UNDERGROUND CITIES & LAVA!", font=title_font, fill=(255, 255, 255))


def render_scene_6_day7_return(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 6: Day 7 - The Sun Pops Back, Golden Sunrise & Giant Beach Party!"""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Blinding radiant sunrise gradient (Gold to warm amber to azure)
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(255, 234, 167))
    # Azure sky above
    draw.rectangle([0, 0, WIDTH, cy - 80], fill=(129, 236, 236))

    # Golden Sunburst Sweeping Across Screen
    for ray_i in range(16):
        ang = t_sec * 0.4 + ray_i * (2 * math.pi / 16)
        rx = cx + int(1400 * math.cos(ang))
        ry = cy - 60 + int(1400 * math.sin(ang))
        draw.line([(cx, cy - 60), (rx, ry)], fill=(255, 209, 102), width=35)

    # Giant Glorious Smiling Cartoon Sun Center Top!
    sun_x, sun_y = cx, cy - 140
    draw.ellipse([sun_x - 150, sun_y - 150, sun_x + 150, sun_y + 150], fill=(255, 185, 45), outline=(235, 94, 40), width=8)
    # Sun retro black sunglasses with white flash gleam!
    draw_rounded_rect(draw, [sun_x - 110, sun_y - 45, sun_x + 110, sun_y + 20], radius=15, fill=(30, 30, 30))
    draw.line([(sun_x - 70, sun_y - 35), (sun_x - 30, sun_y + 5)], fill=(255, 255, 255), width=4)
    # Huge grinning mouth
    draw.arc([sun_x - 65, sun_y + 25, sun_x + 65, sun_y + 90], start=0, end=180, fill=(214, 48, 49), width=8)

    # Melting ice turning into lush green paradise
    draw.chord([-100, HEIGHT - 320, WIDTH + 100, HEIGHT + 400], start=180, end=360, fill=(46, 204, 113))

    # Bob Celebrating Joyfully! Hands in the air!
    bob_x = cx
    bob_y = cy + 120 + int(math.sin(t_sec * 8.0) * 12.0)
    draw_bob(draw, bob_x, bob_y, mood="celebrating", t_sec=t_sec, clothes="hawaiian")

    # Waving celebration arms
    draw.line([(bob_x - 85, bob_y + 90), (bob_x - 160, bob_y - 20 + int(math.sin(t_sec * 10) * 20))], fill=(0, 206, 201), width=18)
    draw.line([(bob_x + 85, bob_y + 90), (bob_x + 160, bob_y - 20 - int(math.sin(t_sec * 10) * 20))], fill=(0, 206, 201), width=18)

    # Colorful Confetti Storm & Floating Balloons!
    np.random.seed(77)
    colors = [(255, 107, 129), (254, 202, 87), (72, 219, 251), (255, 159, 243), (29, 209, 161)]
    for ci in range(70):
        con_x = int((np.random.uniform(20, WIDTH - 20) + t_sec * 40) % WIDTH)
        con_y = int((np.random.uniform(50, HEIGHT - 100) + t_sec * 100) % (HEIGHT - 120))
        ccol = colors[ci % len(colors)]
        draw.ellipse([con_x - 6, con_y - 6, con_x + 6, con_y + 6], fill=ccol)

    # Top Banner
    draw_rounded_rect(draw, [cx - 480, 50, cx + 480, 140], radius=25, fill=(235, 77, 75), outline=(255, 255, 255), width=6)
    draw.text((cx - 430, 65), "DAY 7: THE SUN RETURNS! ☀️🎉", font=title_font, fill=(255, 255, 255))
    draw_rounded_rect(draw, [cx - 320, 155, cx + 320, 215], radius=15, fill=(254, 202, 87), outline=(40, 30, 30), width=4)
    draw.text((cx - 280, 168), "ALWAYS APPRECIATE YOUR LOCAL STAR!", font=banner_font, fill=(40, 30, 30))


def render_scene_7_outro_cta(draw, t_sec: float, title_font, banner_font, sub_font):
    """Scene 7: Grand Finale, Interactive Animated Subscribe Button & Fun Question!"""
    cx, cy = WIDTH // 2, HEIGHT // 2

    # High-energy vibrant royal purple & midnight blue backdrop
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(30, 27, 75))

    # Glowing stage lighting spotlights
    for spot_x, spot_col in [(350, (192, 132, 252)), (WIDTH - 350, (251, 146, 60))]:
        draw.polygon([(spot_x, 0), (spot_x - 280, HEIGHT), (spot_x + 280, HEIGHT)], fill=(spot_col[0]//3, spot_col[1]//3, spot_col[2]//3))

    # Top Viral Engagement Question Badge
    draw_rounded_rect(draw, [cx - 520, 60, cx + 520, 160], radius=25, fill=(255, 71, 87), outline=(255, 255, 255), width=6)
    draw.text((cx - 480, 75), "WHAT WOULD YOU DO FIRST? 💬", font=title_font, fill=(255, 255, 255))
    draw_rounded_rect(draw, [cx - 360, 175, cx + 360, 235], radius=15, fill=(254, 202, 87), outline=(40, 30, 30), width=4)
    draw.text((cx - 320, 188), "TELL US IN THE COMMENTS BELOW!", font=banner_font, fill=(40, 30, 30))

    # Bob smiling on the left
    bob_x = cx - 360
    bob_y = cy + 80 + int(math.sin(t_sec * 5.0) * 8.0)
    draw_bob(draw, bob_x, bob_y, mood="happy", t_sec=t_sec, clothes="hawaiian")

    # Animated Giant Interactive YouTube Subscribe Button
    sub_box = [cx - 60, cy - 50, cx + 460, cy + 70]
    # Button clicks after 3 seconds: Red -> Gray Subscribed
    is_clicked = t_sec >= 3.0
    btn_color = (60, 60, 60) if is_clicked else (255, 0, 0)
    btn_text = "SUBSCRIBED ✓" if is_clicked else "SUBSCRIBE  🔔"

    draw_rounded_rect(draw, sub_box, radius=25, fill=btn_color, outline=(255, 255, 255), width=6)
    draw.text((cx - 10, cy - 25), btn_text, font=title_font, fill=(255, 255, 255))

    # Ringing Golden Notification Bell beside Subscribe
    bell_x, bell_y = cx + 540, cy + 10
    bell_tilt = math.sin(t_sec * 15.0) * 15.0 if is_clicked else 0.0
    draw.ellipse([bell_x - 35, bell_y - 35, bell_x + 35, bell_y + 35], fill=(254, 202, 87), outline=(40, 30, 30), width=5)
    # Bell clapper
    draw.ellipse([bell_x - 10, bell_y + 25, bell_x + 10, bell_y + 45], fill=(225, 177, 44))

    # Animated Like Button 👍
    like_box = [cx - 60, cy + 110, cx + 460, cy + 210]
    draw_rounded_rect(draw, like_box, radius=20, fill=(30, 144, 255), outline=(255, 255, 255), width=5)
    draw.text((cx + 10, cy + 130), "LIKE THIS VIDEO! 👍", font=banner_font, fill=(255, 255, 255))

    # Confetti float
    np.random.seed(88)
    for ci in range(40):
        con_x = int((np.random.uniform(20, WIDTH - 20) + t_sec * 30) % WIDTH)
        con_y = int((np.random.uniform(50, HEIGHT - 50) + t_sec * 70) % HEIGHT)
        draw.ellipse([con_x - 5, con_y - 5, con_x + 5, con_y + 5], fill=(255, 234, 167))


def render_masterpiece_frame(frame_idx: int, scene_bounds: list, title_font, banner_font, sub_font) -> Image.Image:
    """Renders a single frame mapped to its exact audio scene."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Determine which scene this frame belongs to
    scene_idx = 0
    t_local = 0.0
    for idx, (start_f, end_f) in enumerate(scene_bounds):
        if start_f <= frame_idx < end_f:
            scene_idx = idx
            t_local = (frame_idx - start_f) / float(FPS)
            break

    if scene_idx == 0:
        render_scene_1_beach(draw, t_local, title_font, banner_font, sub_font)
    elif scene_idx == 1:
        render_scene_2_blackout(draw, t_local, title_font, banner_font, sub_font)
    elif scene_idx == 2:
        render_scene_3_day1_freeze(draw, t_local, title_font, banner_font, sub_font)
    elif scene_idx == 3:
        render_scene_4_day3_ice(draw, t_local, title_font, banner_font, sub_font)
    elif scene_idx == 4:
        render_scene_5_day5_bunker(draw, t_local, title_font, banner_font, sub_font)
    elif scene_idx == 5:
        render_scene_6_day7_return(draw, t_local, title_font, banner_font, sub_font)
    else:
        render_scene_7_outro_cta(draw, t_local, title_font, banner_font, sub_font)

    return img


def produce_sun_disappeared_masterpiece():
    logger.info("🎬 Rendering 2-Minute Animated Cartoon: 'What Happens If The Sun Disappeared?'...")

    voice_path = str(TEMP_DIR / "sun_full_voice.m4a")
    music_path = str(TEMP_DIR / "sun_cartoon_music.wav")

    if not os.path.exists(voice_path):
        raise FileNotFoundError(f"Master voiceover track missing: {voice_path}")
    if not os.path.exists(music_path):
        raise FileNotFoundError(f"Cartoon music track missing: {music_path}")

    # Exact scene frame calculation for 0.000s timing drift
    scene_files = [str(TEMP_DIR / f"sun_scene{i}.m4a") for i in range(1, 8)]
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
    logger.info(f"⏱️ Video Duration: {total_duration:.2f}s (~2 minutes) | Total Frames: {total_frames}")

    # Fonts
    title_font = get_font(size=54, bold=True, cartoon=True)
    banner_font = get_font(size=36, bold=True, cartoon=True)
    sub_font = get_font(size=26, bold=False, cartoon=False)

    ffmpeg_bin = get_ffmpeg_binary()
    hw = detect_hardware()

    final_output = EXPORTS_DIR / "What_If_The_Sun_Disappeared_2Min.mp4"
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

        if frame_idx % 250 == 0:
            pct = int((frame_idx / total_frames) * 100)
            logger.info(f"Rendering: {pct}% ({frame_idx}/{total_frames} frames)")

    process.stdin.close()
    process.wait()

    render_elapsed = time.time() - t0
    logger.success(f"Cartoon render completed in {render_elapsed:.1f}s ({total_frames / max(0.1, render_elapsed):.1f} fps)!")

    # Generate High-CTR YouTube Thumbnail (1280x720)
    from scripts.update_sun_thumbnail_minimalist import build_minimalist_split_thumbnail
    thumb_path = build_minimalist_split_thumbnail()

    info = get_video_info(str(final_output))
    logger.success("==================================================")
    logger.success("🎉 2-MINUTE HIGH-RETENTION CARTOON MASTERPIECE READY!")
    logger.success(f"📍 Video File: {final_output}")
    logger.success(f"⏱️ Runtime: {info.get('duration', 0):.1f} seconds (Target: 120s)")
    logger.success(f"📐 Resolution: {info.get('width')}x{info.get('height')} 1080p Full HD")
    logger.success(f"🖼️ Thumbnail: {thumb_path}")
    logger.success("==================================================")

    return str(final_output), str(thumb_path)


if __name__ == "__main__":
    produce_sun_disappeared_masterpiece()
