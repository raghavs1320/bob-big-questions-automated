#!/usr/bin/env python3
"""Classic Masterpiece Visual Director for Bob Big Questions.

Renders 1080p 30fps cartoon episodes adhering to our proven classic aesthetic:
- Distinct handcrafted environments per scene (Kitchen, Cityscape, Cosmic Space, Telemetry Lab, Fissure Abyss, Freefall Sofa, Pancake Outro)
- Iconic 3-tier rounded comic auto-banners (Top Title, Mid Headline, Bottom Telemetry)
- Expressive vector Bob (cyan hoodie, coral shorts, animated moods, puffy cheeks)
- Orange tabby cat, cereal bowls, and fluffy golden pancakes with butter
- Universal encoder detection (h264_videotoolbox on Mac, libx264 on Linux)
"""

import math
import random
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont

try:
    import imageio_ffmpeg
    DEFAULT_FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    DEFAULT_FFMPEG = shutil.which("ffmpeg") or "ffmpeg"


def get_ffmpeg_bin() -> str:
    return shutil.which("ffmpeg") or DEFAULT_FFMPEG


WIDTH, HEIGHT = 1920, 1080
FPS = 30


def get_font(size: int):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
        "/System/Library/Fonts/Supplemental/Futura.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/Library/Fonts/Arial.ttf"
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()


def check_encoder() -> Tuple[str, List[str]]:
    """Detects available FFmpeg video encoder."""
    try:
        res = subprocess.run([get_ffmpeg_bin(), "-encoders"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        if "h264_videotoolbox" in res.stdout:
            return "h264_videotoolbox", ["-c:v", "h264_videotoolbox", "-b:v", "9000k", "-pix_fmt", "yuv420p"]
    except Exception:
        pass
    return "libx264", ["-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p"]


def draw_auto_banner(draw: ImageDraw.ImageDraw, cx: int, y_pos: int, text: str, font: ImageFont.ImageFont,
                     fill=(255, 107, 129), text_fill=(255, 255, 255), outline=(40, 30, 30)):
    """Draws iconic Bob Big Questions rounded comic pill banner with drop shadow."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    pad_x, pad_y = 36, 14
    box_w = min(WIDTH - 80, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    box_x = cx - box_w // 2
    box_y = y_pos

    # Soft drop shadow
    draw.rounded_rectangle(
        [box_x + 5, box_y + 6, box_x + box_w + 5, box_y + box_h + 6],
        radius=20, fill=(0, 0, 0, 120)
    )
    # Vibrant pill badge
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=20, fill=fill, outline=outline, width=4
    )
    # Centered text
    draw.text(
        (cx - text_w // 2, box_y + pad_y - bbox[1]),
        text, font=font, fill=text_fill
    )


def draw_bob(draw: ImageDraw.ImageDraw, bx: int, by: int, mood: str = "curious", t_sec: float = 0.0, floating: bool = False):
    """Draws Bob in his classic vector outfit with animated emotions."""
    radius = 85
    bob_dy = int(math.sin(t_sec * 5.0) * 8.0) if floating else int(math.sin(t_sec * 3.5) * 4.0)
    by += bob_dy

    # Cyan Hoodie
    draw.rounded_rectangle([bx - 68, by + 55, bx + 68, by + 210], radius=24, fill=(0, 206, 201), outline=(40, 30, 30), width=5)
    # Coral Shorts
    draw.rounded_rectangle([bx - 62, by + 200, bx + 62, by + 270], radius=14, fill=(255, 107, 129), outline=(40, 30, 30), width=4)

    # Legs & Shoes
    if floating:
        draw.line([(bx - 30, by + 270), (bx - 50, by + 310), (bx - 30, by + 345)], fill=(255, 218, 185), width=18)
        draw.line([(bx + 30, by + 270), (bx + 55, by + 315), (bx + 35, by + 350)], fill=(255, 218, 185), width=18)
    else:
        draw.line([(bx - 30, by + 270), (bx - 30, by + 340)], fill=(255, 218, 185), width=18)
        draw.line([(bx + 30, by + 270), (bx + 30, by + 340)], fill=(255, 218, 185), width=18)
        draw.ellipse([bx - 48, by + 335, bx - 12, by + 355], fill=(254, 202, 87), outline=(40, 30, 30), width=3)
        draw.ellipse([bx + 12, by + 335, bx + 48, by + 355], fill=(254, 202, 87), outline=(40, 30, 30), width=3)

    # Head
    skin = (255, 160, 160) if mood == "holding_breath" else (255, 218, 185)
    draw.ellipse([bx - radius, by - radius, bx + radius, by + radius], fill=skin, outline=(40, 30, 30), width=5)

    # Hair Tufts
    draw.arc([bx - radius + 10, by - radius - 15, bx + radius - 10, by - radius + 35], start=180, end=360, fill=(101, 67, 33), width=18)
    draw.ellipse([bx - 18, by - radius - 20, bx + 22, by - radius + 8], fill=(101, 67, 33))

    if mood == "holding_breath":
        # Huge puffy red cheeks
        draw.ellipse([bx - 110, by - 5, bx - 55, by + 50], fill=(255, 120, 120), outline=(220, 40, 40), width=4)
        draw.ellipse([bx + 55, by - 5, bx + 110, by + 50], fill=(255, 120, 120), outline=(220, 40, 40), width=4)
        for eye_x in (bx - 38, bx + 38):
            draw.ellipse([eye_x - 26, by - 16 - 26, eye_x + 26, by - 16 + 26], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
            draw.ellipse([eye_x - 6, by - 20, eye_x + 6, by - 8], fill=(20, 20, 20))
        draw.line([(bx - 20, by + 30), (bx + 20, by + 30)], fill=(180, 40, 40), width=6)
    elif mood == "shocked":
        for eye_x in (bx - 38, bx + 38):
            draw.ellipse([eye_x - 28, by - 16 - 28, eye_x + 28, by - 16 + 28], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
            draw.ellipse([eye_x - 6, by - 18, eye_x + 6, by - 6], fill=(20, 20, 20))
        # Open shocked mouth
        draw.ellipse([bx - 20, by + 16, bx + 20, by + 56], fill=(50, 20, 20), outline=(220, 50, 50), width=4)
    elif mood == "happy":
        for eye_x in (bx - 36, bx + 36):
            draw.ellipse([eye_x - 20, by - 16 - 20, eye_x + 20, by - 16 + 20], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
            draw.ellipse([eye_x - 5, by - 18, eye_x + 12, by], fill=(30, 30, 40))
        draw.arc([bx - 26, by + 8, bx + 26, by + 45], start=0, end=180, fill=(230, 60, 60), width=6)
    else: # Curious
        for eye_x in (bx - 36, bx + 36):
            draw.ellipse([eye_x - 20, by - 16 - 20, eye_x + 20, by - 16 + 20], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
            p_dx = int(math.sin(t_sec * 3.5) * 6.0)
            draw.ellipse([eye_x + p_dx - 6, by - 22, eye_x + p_dx + 6, by - 10], fill=(20, 20, 20))
        draw.ellipse([bx - 10, by + 28, bx + 10, by + 38], fill=(80, 40, 40))


def draw_cat(draw: ImageDraw.ImageDraw, cx: int, cy: int):
    """Draws Bob's signature orange tabby cat."""
    draw.ellipse([cx - 40, cy - 25, cx + 40, cy + 25], fill=(243, 156, 18), outline=(40, 30, 30), width=3)
    draw.ellipse([cx - 26, cy - 55, cx + 26, cy], fill=(243, 156, 18), outline=(40, 30, 30), width=3)
    draw.polygon([(cx - 22, cy - 45), (cx - 30, cy - 72), (cx - 8, cy - 52)], fill=(230, 126, 34), outline=(40, 30, 30))
    draw.polygon([(cx + 8, cy - 52), (cx + 30, cy - 72), (cx + 22, cy - 45)], fill=(230, 126, 34), outline=(40, 30, 30))
    draw.ellipse([cx - 18, cy - 38, cx - 4, cy - 22], fill=(46, 204, 113), outline=(40, 30, 30), width=2)
    draw.ellipse([cx + 4, cy - 38, cx + 18, cy - 22], fill=(46, 204, 113), outline=(40, 30, 30), width=2)
    draw.arc([cx + 20, cy - 35, cx + 55, cy + 10], start=270, end=90, fill=(243, 156, 18), width=8)


def render_scene_frame(img: Image.Image, draw: ImageDraw.ImageDraw, theme_idx: int, t: float,
                       sc_data: Dict[str, Any], title_font, banner_font, sub_font, is_outro: bool = False):
    """Draws rich, distinct environments for each scene."""
    cx, cy = WIDTH // 2, HEIGHT // 2
    banner_text = sc_data.get("banner", "BOB BIG QUESTIONS")
    sub_text = sc_data.get("sub_banner", "INTERESTING SCIENCE PHENOMENON")

    if is_outro:
        # Theme: Cozy Kitchen Pancake Victory
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(254, 249, 231))
        draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(247, 215, 148))
        draw.line([(0, HEIGHT - 220), (WIDTH, HEIGHT - 220)], fill=(225, 177, 44), width=6)

        # Fluffy Pancakes on Kitchen Table
        table_top = HEIGHT - 280
        draw.rectangle([cx + 40, table_top, cx + 450, table_top + 25], fill=(160, 110, 60))
        draw.rectangle([cx + 60, table_top + 25, cx + 90, HEIGHT - 220], fill=(130, 90, 45))
        draw.rectangle([cx + 400, table_top + 25, cx + 430, HEIGHT - 220], fill=(130, 90, 45))
        # Plate with 3 fluffy golden pancakes
        draw.ellipse([cx + 170, table_top - 40, cx + 330, table_top + 15], fill=(240, 240, 240), outline=(40, 30, 30), width=3)
        for pi in range(3):
            py = table_top - 35 - pi * 16
            draw.rounded_rectangle([cx + 190, py, cx + 310, py + 22], radius=10, fill=(245, 180, 65), outline=(40, 30, 30), width=3)
        # Butter pat
        draw.rectangle([cx + 235, table_top - 90, cx + 265, table_top - 72], fill=(255, 235, 70), outline=(40, 30, 30), width=2)

        draw_bob(draw, cx - 120, cy + 30, mood="happy", t_sec=t)
        draw_cat(draw, cx - 340, cy + 140)

        draw_auto_banner(draw, cx, 50, "SUBSCRIBE TO BOB BIG QUESTIONS!", title_font, fill=(46, 204, 113))
        draw_auto_banner(draw, cx, 145, "HIT LIKE & NEVER MISS A CRAZY ADVENTURE!", banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))
        draw_auto_banner(draw, cx, HEIGHT - 130, "NEW EPISODES EVERY MORNING AT 4:00 AM!", sub_font, fill=(45, 52, 54), text_fill=(254, 202, 87))
        return

    # Cycle through 6 distinct visual themes for scenes 1 to N-1
    env_type = theme_idx % 6

    if env_type == 0:
        # 1. Breakfast Kitchen with Cereal Bowl
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(254, 249, 231))
        draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(247, 215, 148))
        draw.line([(0, HEIGHT - 220), (WIDTH, HEIGHT - 220)], fill=(225, 177, 44), width=6)

        table_top = HEIGHT - 280
        draw.rectangle([cx + 60, table_top, cx + 450, table_top + 25], fill=(160, 110, 60))
        draw.chord([cx + 200, table_top - 60, cx + 320, table_top + 10], start=0, end=180, fill=(235, 77, 75), outline=(40, 30, 30), width=4)
        draw.ellipse([cx + 210, table_top - 60, cx + 310, table_top - 40], fill=(254, 202, 87))

        draw_bob(draw, cx - 100, cy + 30, mood="curious", t_sec=t)
        draw_cat(draw, cx - 320, cy + 140)

        draw_auto_banner(draw, cx, 50, banner_text, title_font, fill=(255, 107, 129))
        draw_auto_banner(draw, cx, 145, sub_text, banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))
        draw_auto_banner(draw, cx, HEIGHT - 130, "A COMPLETELY NORMAL DAY TURNS ABSURD", sub_font, fill=(45, 52, 54), text_fill=(254, 202, 87))

    elif env_type == 1:
        # 2. Crumbling Cityscape & Dust Clouds
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(223, 230, 233))
        draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(178, 190, 195))

        skyscrapers = [(180, 520, 220), (450, 620, 260), (WIDTH - 450, 580, 260), (WIDTH - 180, 480, 200)]
        for sx, sh, sw in skyscrapers:
            crumble_h = int(sh * max(0.3, 1.0 - ((t % 4.0) * 0.15)))
            draw.rectangle([sx - sw // 2, HEIGHT - crumble_h, sx + sw // 2, HEIGHT], fill=(99, 110, 114))
            for c_i in range(5):
                dx = sx - sw // 2 + c_i * 45
                dy = HEIGHT - crumble_h - int(math.sin(t * 3.0 + c_i) * 20)
                draw.ellipse([dx - 45, dy - 45, dx + 45, dy + 45], fill=(255, 255, 255), outline=(200, 200, 200), width=2)

        draw_bob(draw, cx, cy + 30, mood="shocked", t_sec=t)

        draw_auto_banner(draw, cx, 50, banner_text, title_font, fill=(235, 77, 75))
        draw_auto_banner(draw, cx, 145, sub_text, banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))
        draw_auto_banner(draw, cx, HEIGHT - 130, "PHYSICS CATALYST DESTABILIZES CIVILIZATION", sub_font, fill=(45, 52, 54), text_fill=(255, 107, 129))

    elif env_type == 2:
        # 3. Cosmic Midnight Space / Noon Pitch Black Sky
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(10, 12, 22))
        draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(47, 53, 66))

        # Blazing Sun
        sun_x, sun_y = WIDTH - 260, 260
        draw.ellipse([sun_x - 90, sun_y - 90, sun_x + 90, sun_y + 90], fill=(255, 255, 200, 80))
        draw.ellipse([sun_x - 60, sun_y - 60, sun_x + 60, sun_y + 60], fill=(255, 230, 0), outline=(255, 255, 255), width=5)

        # Stars
        for i in range(40):
            sx = (i * 97 + int(t * 10)) % WIDTH
            sy = (i * 61) % (HEIGHT - 280)
            draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255, 200))

        draw_bob(draw, cx, cy + 30, mood="holding_breath", t_sec=t)

        draw_auto_banner(draw, cx, 50, banner_text, title_font, fill=(108, 92, 231))
        draw_auto_banner(draw, cx, 145, sub_text, banner_font, fill=(0, 206, 201), text_fill=(20, 20, 20))
        draw_auto_banner(draw, cx, HEIGHT - 130, "COSMIC FORCES ALTER PLANETARY EQUILIBRIUM", sub_font, fill=(45, 52, 54), text_fill=(254, 202, 87))

    elif env_type == 3:
        # 4. Telemetry Laboratory & Gauge Control
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(255, 209, 102))
        draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(238, 90, 36))

        # Big Telemetry HUD Gauge on Left
        draw.rounded_rectangle([120, 260, 460, 540], radius=20, fill=(45, 52, 54), outline=(235, 77, 75), width=6)
        draw.text((150, 290), "MEASUREMENT HUD", font=banner_font, fill=(254, 202, 87))
        progress = (math.sin(t * 3.5) + 1.0) / 2.0
        val_text = f"{int(progress * 100)}%"
        draw.text((180, 360), val_text, font=title_font, fill=(235, 77, 75))
        draw.text((160, 450), "ANOMALY IN PROGRESS", font=sub_font, fill=(255, 255, 255))

        draw_bob(draw, cx + 120, cy + 30, mood="shocked", t_sec=t)

        draw_auto_banner(draw, cx, 50, banner_text, title_font, fill=(238, 90, 36))
        draw_auto_banner(draw, cx, 145, sub_text, banner_font, fill=(254, 202, 87), text_fill=(40, 30, 30))
        draw_auto_banner(draw, cx, HEIGHT - 130, "ATMOSPHERIC & GRAVITATIONAL SENSORS SPIKING", sub_font, fill=(45, 52, 54), text_fill=(255, 209, 102))

    elif env_type == 4:
        # 5. Cracking Earth Fissures & Deep Abyss
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(130, 88, 159))
        draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(44, 62, 80))

        # Magma fissures
        draw.polygon([(640, HEIGHT - 220), (600, HEIGHT), (680, HEIGHT)], fill=(231, 76, 60))
        draw.polygon([(300, HEIGHT - 180), (270, HEIGHT), (330, HEIGHT)], fill=(243, 156, 18))
        draw.polygon([(WIDTH - 300, HEIGHT - 190), (WIDTH - 330, HEIGHT), (WIDTH - 270, HEIGHT)], fill=(231, 76, 60))

        shake = int(math.sin(t * 20.0) * 6.0)
        draw_bob(draw, cx + shake, cy + 30, mood="shocked", t_sec=t)

        draw_auto_banner(draw, cx, 50, banner_text, title_font, fill=(231, 76, 60))
        draw_auto_banner(draw, cx, 145, sub_text, banner_font, fill=(241, 196, 15), text_fill=(40, 30, 30))
        draw_auto_banner(draw, cx, HEIGHT - 130, "GEOLOGICAL CRUST CRACKS UNDER EXTREME FORCES", sub_font, fill=(45, 52, 54), text_fill=(241, 196, 15))

    else:
        # 6. High-Speed Freefall on Bob's Inflatable Yellow Couch
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(116, 185, 255))
        draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(9, 132, 227))

        # Speed wind lines
        for l_i in range(12):
            lx = (l_i * 160 + int(t * 120)) % WIDTH
            ly = (l_i * 90) % HEIGHT
            draw.line([(lx, ly), (lx + 80, ly - 40)], fill=(255, 255, 255, 180), width=4)

        # Inflatable Yellow Sofa
        sofa_x, sofa_y = cx, cy + 180
        draw.rounded_rectangle([sofa_x - 180, sofa_y - 40, sofa_x + 180, sofa_y + 40], radius=25, fill=(253, 203, 110), outline=(40, 30, 30), width=5)
        draw.rounded_rectangle([sofa_x - 170, sofa_y - 120, sofa_x + 170, sofa_y - 30], radius=20, fill=(255, 234, 167), outline=(40, 30, 30), width=5)

        draw_bob(draw, cx, cy - 30, mood="holding_breath", t_sec=t, floating=True)
        draw_cat(draw, cx + 180, cy + 90)

        draw_auto_banner(draw, cx, 50, banner_text, title_font, fill=(9, 132, 227))
        draw_auto_banner(draw, cx, 145, sub_text, banner_font, fill=(255, 234, 167), text_fill=(40, 30, 30))
        draw_auto_banner(draw, cx, HEIGHT - 130, "INFLATABLE SOFA PROVIDES MINIMAL PLANETARY PROTECTION", sub_font, fill=(45, 52, 54), text_fill=(255, 234, 167))


def render_masterpiece_video(screenplay: Dict[str, Any], scene_data: List[Dict[str, Any]],
                             audio_path: Path, output_video_path: Path):
    """Renders 1080p Full HD video stream directly through FFmpeg."""
    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    encoder_name, encoder_flags = check_encoder()
    print(f"🎬 Starting render with encoder: {encoder_name}")

    total_frames = sum(s["frames"] for s in scene_data)
    title_font = get_font(42)
    banner_font = get_font(30)
    sub_font = get_font(24)

    # Launch FFmpeg pipe
    cmd = [
        get_ffmpeg_bin(), "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS),
        "-i", "pipe:0",
        "-i", str(audio_path),
        *encoder_flags,
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_video_path)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    global_frame = 0
    num_scenes = len(scene_data)

    for sc_idx, sc in enumerate(scene_data):
        sc_frames = sc["frames"]
        is_outro = (sc_idx == num_scenes - 1)

        for f in range(sc_frames):
            global_frame += 1
            t_sec = f / FPS

            img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
            draw = ImageDraw.Draw(img)

            render_scene_frame(img, draw, sc_idx, t_sec, sc, title_font, banner_font, sub_font, is_outro=is_outro)

            proc.stdin.write(img.tobytes())

            if global_frame % 300 == 0 or global_frame == total_frames:
                pct = int(global_frame / total_frames * 100)
                print(f"🎬 Render Progress: {pct}% ({global_frame}/{total_frames} frames)")

    proc.stdin.close()
    proc.wait()
    print(f"✅ Master Video rendered successfully at: {output_video_path}")
    return output_video_path
