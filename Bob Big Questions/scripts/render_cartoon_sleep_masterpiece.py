"""High-Retention Animated Cartoon: 'What Happens If You Don't Sleep For 7 Days?'

Features:
- 100% Procedurally rendered colorful cartoon vector animation (No downloaded clips, zero watermarks).
- Expressive animated character (Bob) with dynamic facial expressions, squashes, stretches, and props.
- 6 Entertaining Story Acts:
    1. Day 0: The Coffee Addiction & The Big Question
    2. Hour 24: Fake Superhero Mode (Dopamine Rush)
    3. Hour 48: 20% Battery Drain & Banana Toothbrush Gag
    4. Day 3: Hallucinations (Dancing Sunglasses Donut)
    5. Day 5: Micro-Sleep Cereal Bowl SPLAT
    6. Day 7: Brain Rebellion, Marshmallow Bed & 16-Hour Sleep
- Audio Design: Friendly voiceover, bouncy marimba groove, and cartoon sound effects.
- Output: 1080p Full HD, 60/30fps, Apple Silicon hardware accelerated.
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


def get_font(size: int = 40, cartoon: bool = True):
    fp = FONT_CHALKBOARD if cartoon and os.path.exists(FONT_CHALKBOARD) else FONT_FUTURA
    if os.path.exists(fp):
        try:
            return ImageFont.truetype(fp, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)


def draw_bob_head(draw, cx, cy, radius=110, mood="happy", t_sec=0.0):
    """Draws Bob's cute expressive cartoon face."""
    # Head skin (warm friendly peach)
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(255, 218, 185), outline=(50, 40, 40), width=6)

    # Bob's brown messy hair tufts
    hair_color = (101, 67, 33)
    draw.arc([cx - radius + 10, cy - radius - 20, cx + radius - 10, cy - radius + 50], start=180, end=360, fill=hair_color, width=22)
    # Cute hair curl
    draw.ellipse([cx - 20, cy - radius - 28, cx + 25, cy - radius + 10], fill=hair_color)

    # Eyes & Expressions
    if mood == "happy":
        # Big bright curious round eyes
        eye_r = 26
        # Left eye
        draw.ellipse([cx - 45 - eye_r, cy - 20 - eye_r, cx - 45 + eye_r, cy - 20 + eye_r], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
        draw.ellipse([cx - 40, cy - 22, cx - 22, cy - 4], fill=(30, 30, 40))
        draw.ellipse([cx - 36, cy - 20, cx - 28, cy - 12], fill=(255, 255, 255)) # Glint
        # Right eye
        draw.ellipse([cx + 45 - eye_r, cy - 20 - eye_r, cx + 45 + eye_r, cy - 20 + eye_r], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
        draw.ellipse([cx + 50, cy - 22, cx + 68, cy - 4], fill=(30, 30, 40))
        draw.ellipse([cx + 54, cy - 20, cx + 62, cy - 12], fill=(255, 255, 255))
        # Cheerful smile
        draw.arc([cx - 35, cy + 5, cx + 35, cy + 55], start=0, end=180, fill=(230, 60, 60), width=8)

    elif mood == "superhero":
        # Fierce determined superhero eyes with mask
        mask_color = (255, 75, 75)
        draw_rounded_rect(draw, [cx - 95, cy - 45, cx + 95, cy + 10], radius=15, fill=mask_color, outline=(40, 30, 30), width=4)
        # Eyes shining inside mask
        draw.ellipse([cx - 55, cy - 35, cx - 15, cy - 5], fill=(255, 255, 255))
        draw.ellipse([cx + 15, cy - 35, cx + 55, cy - 5], fill=(255, 255, 255))
        draw.ellipse([cx - 38, cy - 25, cx - 22, cy - 9], fill=(20, 20, 20))
        draw.ellipse([cx + 32, cy - 25, cx + 48, cy - 9], fill=(20, 20, 20))
        # Confident superhero smirk
        draw.arc([cx - 25, cy + 18, cx + 35, cy + 50], start=20, end=170, fill=(220, 40, 40), width=7)

    elif mood == "tired":
        # Heavy droopy eyelids and purple eye bags
        # Dark purple eye bags
        draw.arc([cx - 75, cy - 10, cx - 15, cy + 30], start=0, end=180, fill=(162, 155, 254), width=6)
        draw.arc([cx + 15, cy - 10, cx + 75, cy + 30], start=0, end=180, fill=(162, 155, 254), width=6)
        # Half-closed eyes
        draw.ellipse([cx - 65, cy - 25, cx - 25, cy + 15], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
        draw.ellipse([cx + 25, cy - 25, cx + 65, cy + 15], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
        # Drooping lids
        draw.chord([cx - 65, cy - 25, cx - 25, cy + 15], start=180, end=360, fill=(255, 218, 185), outline=(40, 30, 30), width=4)
        draw.chord([cx + 25, cy - 25, cx + 65, cy + 15], start=180, end=360, fill=(255, 218, 185), outline=(40, 30, 30), width=4)
        # Pupils
        draw.ellipse([cx - 50, cy - 4, cx - 40, cy + 6], fill=(40, 40, 40))
        draw.ellipse([cx + 40, cy - 4, cx + 50, cy + 6], fill=(40, 40, 40))
        # Droopy wavy mouth
        draw.arc([cx - 30, cy + 25, cx + 30, cy + 45], start=180, end=360, fill=(180, 80, 80), width=6)

    elif mood == "spiral":
        # Crazy cartoon hypnotic spiral eyes (Hallucination mode!)
        for side, eye_x in [(-1, cx - 45), (1, cx + 45)]:
            draw.ellipse([eye_x - 30, cy - 20 - 30, eye_x + 30, cy - 20 + 30], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
            # Animated rotating spiral
            for r_s in range(6, 26, 6):
                ang = t_sec * 8.0 * side + r_s
                draw.arc([eye_x - r_s, cy - 20 - r_s, eye_x + r_s, cy - 20 + r_s], start=int(ang*50)%360, end=(int(ang*50)+160)%360, fill=(255, 107, 129), width=3)
        # Wobbly shocked open mouth
        draw.ellipse([cx - 20, cy + 15, cx + 20, cy + 50], fill=(50, 20, 20), outline=(230, 80, 80), width=4)

    elif mood == "sleeping":
        # Peaceful closed curved eyes with eyelashes
        draw.arc([cx - 65, cy - 20, cx - 25, cy + 10], start=0, end=180, fill=(40, 30, 30), width=6)
        draw.arc([cx + 25, cy - 20, cx + 65, cy + 10], start=0, end=180, fill=(40, 30, 30), width=6)
        # Sweet gentle sleeping smile
        draw.arc([cx - 25, cy + 18, cx + 25, cy + 42], start=0, end=180, fill=(230, 80, 80), width=5)
        # Cute pink cheeks
        draw.ellipse([cx - 85, cy + 5, cx - 55, cy + 25], fill=(255, 175, 175))
        draw.ellipse([cx + 55, cy + 5, cx + 85, cy + 25], fill=(255, 175, 175))


def render_cartoon_frame(t_sec: float, total_dur: float, title_font, banner_font, body_font) -> Image.Image:
    """Renders a single 1080p frame for the 6-act cartoon."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = WIDTH // 2, HEIGHT // 2

    # Act 1 (0.0s - 8.0s): Day 0 - Meet Bob with 5 Coffee Mugs
    if t_sec < 8.0:
        # Warm sunny room background
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(254, 249, 231))
        # Wall baseboard & warm floor
        draw.rectangle([0, HEIGHT - 240, WIDTH, HEIGHT], fill=(247, 215, 148))
        draw.line([(0, HEIGHT - 240), (WIDTH, HEIGHT - 240)], fill=(225, 177, 44), width=6)

        # Bob standing happily with coffee
        bob_y = cy + 40 + int(math.sin(t_sec * 5.0) * 8.0)
        # Body (Cyan hoodie)
        draw_rounded_rect(draw, [cx - 90, bob_y + 80, cx + 90, bob_y + 260], radius=35, fill=(0, 201, 167), outline=(40, 30, 30), width=6)
        draw_bob_head(draw, cx, bob_y, radius=105, mood="happy", t_sec=t_sec)

        # Huge Coffee Mug in Bob's hand
        mug_x, mug_y = cx + 130, bob_y + 110
        draw_rounded_rect(draw, [mug_x - 40, mug_y - 50, mug_x + 40, mug_y + 40], radius=15, fill=(238, 82, 83), outline=(40, 30, 30), width=5)
        # Mug handle
        draw.arc([mug_x + 30, mug_y - 30, mug_x + 65, mug_y + 20], start=270, end=90, fill=(238, 82, 83), width=10)
        # Rising coffee steam
        steam_y = mug_y - 60 - int((t_sec * 40) % 50)
        draw.arc([mug_x - 15, steam_y - 30, mug_x + 15, steam_y + 10], start=180, end=360, fill=(180, 180, 180), width=4)

        # Pop-in Banner at top
        draw_rounded_rect(draw, [cx - 480, 70, cx + 480, 160], radius=25, fill=(255, 107, 129), outline=(40, 30, 30), width=5)
        draw.text((cx - 430, 85), "WHAT IF YOU NEVER SLEEP?", font=title_font, fill=(255, 255, 255))
        # Sub-badge
        draw_rounded_rect(draw, [cx - 260, 180, cx + 260, 240], radius=15, fill=(254, 202, 87), outline=(40, 30, 30), width=4)
        draw.text((cx - 210, 192), "DAY 0: 5 CUPS OF COFFEE", font=banner_font, fill=(40, 30, 30))

    # Act 2 (8.0s - 18.0s): Hour 24 - Superhero Dopamine Mode
    elif t_sec < 18.0:
        # High-energy radiant yellow & orange background
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(255, 209, 102))
        # Radiating sunburst rays
        for ray_i in range(12):
            ang = t_sec * 0.8 + ray_i * (2 * math.pi / 12)
            rx = cx + int(1400 * math.cos(ang))
            ry = cy + int(1400 * math.sin(ang))
            draw.line([(cx, cy), (rx, ry)], fill=(255, 185, 45, 100), width=35)

        # Bob flying in superhero pose!
        fly_y = cy - 20 + int(math.sin(t_sec * 8.0) * 16.0)
        # Flowing Red Superhero Cape
        cape_pts = [(cx - 90, fly_y + 80), (cx - 240, fly_y + 160 + int(math.sin(t_sec * 10) * 30)), (cx - 180, fly_y + 240), (cx - 60, fly_y + 180)]
        draw.polygon(cape_pts, fill=(238, 82, 83), outline=(40, 30, 30))
        # Superhero suit
        draw_rounded_rect(draw, [cx - 85, fly_y + 70, cx + 85, fly_y + 240], radius=35, fill=(10, 61, 98), outline=(40, 30, 30), width=6)
        draw_bob_head(draw, cx, fly_y, radius=105, mood="superhero", t_sec=t_sec)

        # Dopamine Power Meter HUD
        draw_rounded_rect(draw, [cx - 400, HEIGHT - 180, cx + 400, HEIGHT - 90], radius=25, fill=(30, 39, 46), outline=(255, 255, 255), width=5)
        # Glowing green battery bar
        draw_rounded_rect(draw, [cx - 380, HEIGHT - 165, cx + 380, HEIGHT - 105], radius=15, fill=(46, 204, 113))
        draw.text((cx - 330, HEIGHT - 155), "DOPAMINE RUSH: 200% SUPERHUMAN!", font=banner_font, fill=(255, 255, 255))

        # Title Badge
        draw_rounded_rect(draw, [cx - 360, 70, cx + 360, 160], radius=25, fill=(235, 47, 6), outline=(40, 30, 30), width=5)
        draw.text((cx - 310, 85), "HOUR 24: I CAN FIGHT GRAVITY!", font=title_font, fill=(255, 255, 255))

    # Act 3 (18.0s - 28.0s): Hour 48 - Battery 20% & Banana Toothbrush
    elif t_sec < 28.0:
        # Sleepy lavender / dusky violet room
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(223, 230, 233))
        draw.rectangle([0, HEIGHT - 240, WIDTH, HEIGHT], fill=(178, 190, 195))

        bob_y = cy + 40
        # Slumped body
        draw_rounded_rect(draw, [cx - 90, bob_y + 80, cx + 90, bob_y + 260], radius=35, fill=(99, 110, 114), outline=(40, 30, 30), width=6)
        draw_bob_head(draw, cx, bob_y, radius=105, mood="tired", t_sec=t_sec)

        # Banana in Bob's hand with white foam toothpaste
        banana_x, banana_y = cx + 110, bob_y + 100
        draw.arc([banana_x - 30, banana_y - 60, banana_x + 70, banana_y + 60], start=120, end=300, fill=(255, 234, 167), width=24)
        # White toothpaste blob on banana tip
        draw.ellipse([banana_x + 40, banana_y - 50, banana_x + 75, banana_y - 25], fill=(255, 255, 255), outline=(100, 100, 255), width=3)

        # Flashing Battery Gauge Over Head (Red 20%)
        flash = int(t_sec * 6.0) % 2 == 0
        bat_color = (235, 77, 75) if flash else (180, 40, 40)
        draw_rounded_rect(draw, [cx - 160, bob_y - 200, cx + 160, bob_y - 130], radius=15, fill=(45, 52, 54), outline=(255, 255, 255), width=4)
        draw_rounded_rect(draw, [cx - 150, bob_y - 190, cx - 80, bob_y - 140], radius=10, fill=bat_color)
        draw.text((cx - 60, bob_y - 180), "BATTERY: 20%", font=banner_font, fill=(255, 255, 255))

        # Title Badge
        draw_rounded_rect(draw, [cx - 450, 70, cx + 450, 160], radius=25, fill=(108, 92, 231), outline=(40, 30, 30), width=5)
        draw.text((cx - 410, 85), "HOUR 48: BANANA TOOTHBRUSH!", font=title_font, fill=(255, 255, 255))

    # Act 4 (28.0s - 38.0s): Day 3 - Hallucinations & The Dancing Donut
    elif t_sec < 38.0:
        # Psychedelic pastel cartoon room with floating bubbles
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(250, 211, 144))
        # Floating dream bubbles
        for bi in range(10):
            bx = int((bi * 210 + t_sec * 60) % WIDTH)
            by = int((bi * 120 + math.sin(t_sec + bi) * 50) % (HEIGHT - 200) + 100)
            draw.ellipse([bx - 30, by - 30, bx + 30, by + 30], fill=(255, 255, 255, 120), outline=(255, 107, 129), width=3)

        bob_y = cy + 40
        draw_rounded_rect(draw, [cx - 240, bob_y + 80, cx - 60, bob_y + 260], radius=35, fill=(116, 185, 255), outline=(40, 30, 30), width=6)
        draw_bob_head(draw, cx - 150, bob_y, radius=100, mood="spiral", t_sec=t_sec)

        # GIANT DANCING PINK DONUT with Sunglasses!
        donut_x = cx + 220
        donut_y = cy + 40 + int(math.sin(t_sec * 10.0) * 22.0)
        # Donut dough
        draw.ellipse([donut_x - 120, donut_y - 120, donut_x + 120, donut_y + 120], fill=(243, 156, 18), outline=(40, 30, 30), width=6)
        # Pink frosting
        draw.ellipse([donut_x - 105, donut_y - 105, donut_x + 105, donut_y + 105], fill=(255, 121, 198))
        # Donut hole
        draw.ellipse([donut_x - 40, donut_y - 40, donut_x + 40, donut_y + 40], fill=(250, 211, 144), outline=(40, 30, 30), width=6)
        # Cool Sunglasses on Donut
        draw_rounded_rect(draw, [donut_x - 80, donut_y - 45, donut_x + 80, donut_y - 10], radius=12, fill=(30, 30, 30))
        # Donut dancing stick arms & legs
        draw.line([(donut_x - 110, donut_y), (donut_x - 160, donut_y - 40)], fill=(40, 30, 30), width=7)
        draw.line([(donut_x + 110, donut_y), (donut_x + 160, donut_y - 40)], fill=(40, 30, 30), width=7)

        # Title Badge
        draw_rounded_rect(draw, [cx - 430, 70, cx + 430, 160], radius=25, fill=(232, 67, 147), outline=(40, 30, 30), width=5)
        draw.text((cx - 390, 85), "DAY 3: THE DANCING DONUT!", font=title_font, fill=(255, 255, 255))

    # Act 5 (38.0s - 48.0s): Day 5 - Micro-Sleep Cereal Faceplant SPLAT!
    elif t_sec < 48.0:
        # Kitchen table background
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(241, 242, 246))
        # Big wooden dining table
        draw.rectangle([0, cy + 90, WIDTH, HEIGHT], fill=(205, 133, 63))
        draw.line([(0, cy + 90), (WIDTH, cy + 90)], fill=(139, 69, 19), width=8)

        # Giant Red Cereal Bowl on Table
        bowl_x, bowl_y = cx, cy + 130
        draw.chord([bowl_x - 170, bowl_y - 80, bowl_x + 170, bowl_y + 110], start=0, end=180, fill=(235, 47, 6), outline=(40, 30, 30), width=6)
        # White milk inside
        draw.ellipse([bowl_x - 150, bowl_y - 25, bowl_x + 150, bowl_y + 25], fill=(255, 255, 255), outline=(200, 200, 255), width=3)
        # Colorful cereal rings
        for ci, color in enumerate([(255, 75, 75), (46, 204, 113), (255, 204, 0), (155, 89, 182)]):
            draw.ellipse([bowl_x - 90 + ci * 50, bowl_y - 12, bowl_x - 65 + ci * 50, bowl_y + 12], fill=color)

        # Bob Faceplanted into the bowl!
        # Head tilted down into the cereal bowl
        draw.ellipse([cx - 85, cy + 20, cx + 85, cy + 130], fill=(255, 218, 185), outline=(50, 40, 40), width=6)
        # Hair
        draw.ellipse([cx - 70, cy - 10, cx + 70, cy + 45], fill=(101, 67, 33))
        # Body slumped over table
        draw_rounded_rect(draw, [cx - 100, cy + 80, cx + 100, cy + 240], radius=35, fill=(0, 201, 167), outline=(40, 30, 30), width=6)

        # Cartoon Milk Splash Droplets!
        for si in range(8):
            ang = si * (math.pi / 7)
            drop_x = cx + int((130 + math.sin(t_sec * 12) * 20) * math.cos(ang))
            drop_y = cy + 20 - int((80 + math.cos(t_sec * 12) * 20) * math.sin(ang))
            draw.ellipse([drop_x - 10, drop_y - 10, drop_x + 10, drop_y + 10], fill=(255, 255, 255), outline=(150, 150, 255), width=2)

        # Title Badge
        draw_rounded_rect(draw, [cx - 440, 70, cx + 440, 160], radius=25, fill=(225, 112, 85), outline=(40, 30, 30), width=5)
        draw.text((cx - 390, 85), "DAY 5: CEREAL BOWL SPLAT!", font=title_font, fill=(255, 255, 255))

    # Act 6 (48.0s - 57.5s): Day 7 - Marshmallow Cloud Bed & The Big Sleep
    else:
        # Cozy starlit midnight blue night sky
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(44, 62, 80))
        # Golden crescent moon
        draw.chord([WIDTH - 250, 80, WIDTH - 110, 220], start=45, end=270, fill=(241, 196, 15))
        draw.chord([WIDTH - 225, 70, WIDTH - 95, 210], start=45, end=270, fill=(44, 62, 80)) # Cutout to make crescent

        # Giant Fluffy Marshmallow Cloud Bed!
        bed_y = cy + 100
        # Cloud puffs
        for ci, cx_c in enumerate([cx - 200, cx - 100, cx, cx + 100, cx + 200]):
            draw.ellipse([cx_c - 110, bed_y - 50, cx_c + 110, bed_y + 110], fill=(236, 240, 241), outline=(189, 195, 199), width=4)
        # Cozy blanket
        draw_rounded_rect(draw, [cx - 260, bed_y, cx + 260, bed_y + 160], radius=30, fill=(52, 152, 219), outline=(41, 128, 185), width=6)

        # Bob Sleeping Peacefully with Nightcap
        draw_bob_head(draw, cx, bed_y - 45, radius=95, mood="sleeping", t_sec=t_sec)
        # Nightcap on head
        draw.polygon([(cx - 70, bed_y - 120), (cx + 70, bed_y - 120), (cx + 140, bed_y - 60)], fill=(231, 76, 60))
        draw.ellipse([cx + 130, bed_y - 70, cx + 160, bed_y - 40], fill=(255, 255, 255)) # Pompom

        # Big Floating "Z Z Z" Letters Rising
        for zi in range(3):
            z_y = bed_y - 140 - zi * 55 - int((t_sec * 25) % 40)
            z_x = cx + 80 + zi * 35
            draw.text((z_x, z_y), "Z", font=title_font, fill=(255, 255, 255))

        # Final Victory Title Badge
        draw_rounded_rect(draw, [cx - 450, 60, cx + 450, 150], radius=25, fill=(46, 204, 113), outline=(40, 30, 30), width=5)
        draw.text((cx - 390, 75), "DAY 7: BEDTIME IS KING! 👑", font=title_font, fill=(255, 255, 255))
        # Sub-badge
        draw_rounded_rect(draw, [cx - 300, 170, cx + 300, 230], radius=15, fill=(243, 156, 18), outline=(40, 30, 30), width=4)
        draw.text((cx - 260, 182), "+16 HOURS OF GLORIOUS SLEEP!", font=banner_font, fill=(255, 255, 255))

    return img


def produce_cartoon_sleep_masterpiece():
    logger.info("🎨 Rendering High-Retention 2D Animated Cartoon: 'What Happens If You Don't Sleep 7 Days?'...")

    voice_path = str(TEMP_DIR / "cartoon_sleep_voice.m4a")
    music_path = str(TEMP_DIR / "cartoon_music.wav")

    if not os.path.exists(voice_path):
        raise FileNotFoundError(f"Voiceover track missing: {voice_path}")

    total_duration = get_audio_duration(voice_path)
    total_frames = int(total_duration * FPS)
    logger.info(f"⏱️ Video Duration: {total_duration:.2f}s | Total Frames: {total_frames}")

    # Fonts
    title_font = get_font(size=56, cartoon=True)
    banner_font = get_font(size=36, cartoon=True)
    body_font = get_font(size=26, cartoon=False)

    ffmpeg_bin = get_ffmpeg_binary()
    hw = detect_hardware()

    final_output = EXPORTS_DIR / "What_Happens_If_You_Dont_Sleep_7_Days.mp4"
    final_output.parent.mkdir(parents=True, exist_ok=True)

    # FFmpeg command: mixes raw cartoon frames from stdin with voiceover + bouncy cartoon music
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
        "-i", music_path,  # Input 2: Cheerful Marimba Music Groove
        "-filter_complex",
        # Duck music groove under voiceover so story is crystal clear
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
        t_sec = frame_idx / FPS
        frame_img = render_cartoon_frame(t_sec, total_duration, title_font, banner_font, body_font)
        process.stdin.write(frame_img.tobytes())

        if frame_idx % 200 == 0:
            pct = int((frame_idx / total_frames) * 100)
            logger.info(f"Rendering Cartoon: {pct}% ({frame_idx}/{total_frames} frames)")

    process.stdin.close()
    process.wait()

    render_elapsed = time.time() - t0
    logger.success(f"Cartoon render completed in {render_elapsed:.1f}s ({total_frames / max(0.1, render_elapsed):.1f} fps)!")

    # Generate High-CTR Cartoon Thumbnail
    from scripts.generate_sleep_thumbnail_v2 import generate_sleep_thumbnail
    thumb_path = generate_sleep_thumbnail()

    info = get_video_info(str(final_output))
    logger.success("==================================================")
    logger.success("🎉 HIGH-RETENTION 2D CARTOON MASTERPIECE READY!")
    logger.success(f"📍 Video File: {final_output}")
    logger.success(f"⏱️ Runtime: {info.get('duration', 0):.1f} seconds")
    logger.success(f"📐 Resolution: {info.get('width')}x{info.get('height')} 1080p Full HD")
    logger.success(f"🖼️ Thumbnail: {thumb_path}")
    logger.success("==================================================")
    return str(final_output), str(thumb_path)


if __name__ == "__main__":
    produce_cartoon_sleep_masterpiece()
