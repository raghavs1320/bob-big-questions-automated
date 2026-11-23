#!/usr/bin/env python3
"""Autonomous Visual Director for Bob Big Questions.

Renders 1080p 30fps cartoon masterpiece with an ultra-high visual cadence
(dynamic micro-cuts, camera zooms, screen shakes, comic stickers, and expressions
changing every 1.0 to 1.5 seconds) to achieve Netflix-documentary level engagement.
Automatically detects hardware encoder (h264_videotoolbox on Mac, libx264 on Linux).
"""

import math
import random
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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


def draw_auto_banner(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont,
                     y_pos: int = 50, fill_color=(255, 71, 87), border_color=(255, 255, 255)):
    """Draws iconic Bob Big Questions rounded comic pill banner with drop shadow."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    pad_x, pad_y = 40, 18
    box_w = text_w + pad_x * 2
    box_h = text_h + pad_y * 2
    box_x = (WIDTH - box_w) // 2
    box_y = y_pos

    # Drop shadow
    draw.rounded_rectangle(
        [box_x + 6, box_y + 8, box_x + box_w + 6, box_y + box_h + 8],
        radius=22, fill=(0, 0, 0, 140)
    )
    # Main badge pill
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=22, fill=fill_color, outline=border_color, width=4
    )
    # Ink-centered text
    draw.text(
        (box_x + pad_x - bbox[0], box_y + pad_y - bbox[1]),
        text, font=font, fill=(255, 255, 255)
    )


def draw_bob_character(draw: ImageDraw.ImageDraw, cx: int, cy: int, emotion: str = "curious", t: float = 0.0):
    """Draws Bob in his signature cyan hoodie with animated expressions."""
    # Gentle breathing bob
    bob_offset_y = int(math.sin(t * 6.0) * 8.0)
    cy += bob_offset_y

    head_r = 80
    skin = (255, 218, 185)

    # Cyan Hoodie & Shoulders
    draw.polygon([
        (cx - 120, cy + 200),
        (cx + 120, cy + 200),
        (cx + 80, cy + 60),
        (cx - 80, cy + 60)
    ], fill=(0, 206, 201), outline=(0, 150, 145), width=4)

    # Bob's Head
    draw.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r], fill=skin, outline=(220, 180, 150), width=4)

    # Messy Hair Tufts
    draw.polygon([(cx - head_r, cy - 25), (cx - head_r + 15, cy - head_r - 18), (cx - 15, cy - head_r + 10)], fill=(101, 67, 33))
    draw.polygon([(cx - 35, cy - head_r), (cx, cy - head_r - 30), (cx + 35, cy - head_r)], fill=(101, 67, 33))
    draw.polygon([(cx + 15, cy - head_r + 10), (cx + head_r - 15, cy - head_r - 18), (cx + head_r, cy - 25)], fill=(101, 67, 33))

    eye_r = 25
    left_eye_x, right_eye_x = cx - 45, cx + 45
    eye_y = cy - 10

    if emotion == "panicked" or emotion == "shocked":
        # Puffed cheeks
        draw.ellipse([cx - head_r - 5, cy + 10, cx - 35, cy + 55], fill=(255, 110, 110))
        draw.ellipse([cx + 35, cy + 10, cx + head_r + 5, cy + 55], fill=(255, 110, 110))
        # Giant saucer eyes
        draw.ellipse([left_eye_x - eye_r - 6, eye_y - eye_r - 6, left_eye_x + eye_r + 6, eye_y + eye_r + 6], fill=(255, 255, 255), outline=(30, 30, 30), width=3)
        draw.ellipse([right_eye_x - eye_r - 6, eye_y - eye_r - 6, right_eye_x + eye_r + 6, eye_y + eye_r + 6], fill=(255, 255, 255), outline=(30, 30, 30), width=3)
        # Tiny frantic pupils
        draw.ellipse([left_eye_x - 6, eye_y - 6, left_eye_x + 6, eye_y + 6], fill=(20, 20, 20))
        draw.ellipse([right_eye_x - 6, eye_y - 6, right_eye_x + 6, eye_y + 6], fill=(20, 20, 20))
        # Open screaming O-mouth
        draw.ellipse([cx - 16, cy + 30, cx + 16, cy + 58], fill=(60, 20, 20), outline=(20, 20, 20), width=3)
    elif emotion == "happy":
        # Happy arched eyes
        draw.arc([left_eye_x - eye_r, eye_y - eye_r, left_eye_x + eye_r, eye_y + eye_r], 190, 350, fill=(30, 30, 30), width=4)
        draw.arc([right_eye_x - eye_r, eye_y - eye_r, right_eye_x + eye_r, eye_y + eye_r], 190, 350, fill=(30, 30, 30), width=4)
        # Big smile
        draw.arc([cx - 30, cy + 20, cx + 30, cy + 55], 10, 170, fill=(180, 50, 50), width=5)
    else: # Curious / Default
        # White eyes
        draw.ellipse([left_eye_x - eye_r, eye_y - eye_r, left_eye_x + eye_r, eye_y + eye_r], fill=(255, 255, 255), outline=(30, 30, 30), width=3)
        draw.ellipse([right_eye_x - eye_r, eye_y - eye_r, right_eye_x + eye_r, eye_y + eye_r], fill=(255, 255, 255), outline=(30, 30, 30), width=3)
        # Looking up/curious pupils
        pupil_dx = int(math.sin(t * 4.0) * 8.0)
        draw.ellipse([left_eye_x + pupil_dx - 8, eye_y - 12, left_eye_x + pupil_dx + 8, eye_y + 4], fill=(20, 20, 20))
        draw.ellipse([right_eye_x + pupil_dx - 8, eye_y - 12, right_eye_x + pupil_dx + 8, eye_y + 4], fill=(20, 20, 20))
        # Small curious mouth
        draw.ellipse([cx - 10, cy + 35, cx + 10, cy + 45], fill=(80, 40, 40))


def draw_telemetry_gauge(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, value_text: str, progress: float, font: ImageFont.ImageFont):
    """Draws sci-fi / comic dashboard dial with needle."""
    radius = 65
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(20, 26, 40), outline=(254, 202, 87), width=4)
    # Dial markings
    for angle_deg in range(140, 400, 35):
        rad = math.radians(angle_deg)
        x1 = x + math.cos(rad) * (radius - 12)
        y1 = y + math.sin(rad) * (radius - 12)
        x2 = x + math.cos(rad) * (radius - 4)
        y2 = y + math.sin(rad) * (radius - 4)
        draw.line([(x1, y1), (x2, y2)], fill=(200, 200, 200), width=2)
    # Needle
    needle_angle = math.radians(140 + progress * 260)
    nx = x + math.cos(needle_angle) * (radius - 15)
    ny = y + math.sin(needle_angle) * (radius - 15)
    draw.line([(x, y), (nx, ny)], fill=(255, 71, 87), width=4)
    draw.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(254, 202, 87))
    # Labels
    draw.text((x - 45, y + radius + 10), label, font=font, fill=(255, 255, 255))
    draw.text((x - 45, y + radius + 32), value_text, font=font, fill=(254, 202, 87))


def render_masterpiece_video(screenplay: Dict[str, Any], scene_data: List[Dict[str, Any]],
                             audio_path: Path, output_video_path: Path):
    """Renders 1080p Full HD video stream directly through FFmpeg."""
    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    encoder_name, encoder_flags = check_encoder()
    print(f"🎬 Starting render with encoder: {encoder_name}")

    total_frames = sum(s["frames"] for s in scene_data)
    banner_font = get_font(42)
    hud_font = get_font(22)
    sticker_font = get_font(72)

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
        banner_text = sc["banner"]
        is_outro = (sc_idx == num_scenes - 1)
        is_climax = (sc_idx == num_scenes - 2)

        # Scene color palette
        if sc_idx % 3 == 0:
            bg_top = (15, 23, 42)    # Slate dark
            bg_bot = (30, 41, 59)
            banner_color = (255, 71, 87)
        elif sc_idx % 3 == 1:
            bg_top = (24, 15, 45)    # Cosmic purple
            bg_bot = (45, 25, 80)
            banner_color = (254, 202, 87)
        else:
            bg_top = (10, 30, 45)    # Oceanic cyan-dark
            bg_bot = (20, 60, 85)
            banner_color = (46, 213, 115)

        for f in range(sc_frames):
            global_frame += 1
            t_sec = f / FPS
            progress = f / sc_frames

            # High-Frequency Beat Cadence (Every 1.2s switch visual sub-beat)
            beat_phase = int(t_sec / 1.2) % 4
            shake_x, shake_y = 0, 0

            # Screen shake on climax or action beats
            if is_climax and (beat_phase == 1 or beat_phase == 2):
                shake_x = random.randint(-8, 8)
                shake_y = random.randint(-8, 8)

            img = Image.new("RGB", (WIDTH, HEIGHT), bg_top)
            draw = ImageDraw.Draw(img)

            # 1. Background Gradient
            for y_line in range(0, HEIGHT, 16):
                ratio = y_line / HEIGHT
                r = int(bg_top[0] + ratio * (bg_bot[0] - bg_top[0]))
                g = int(bg_top[1] + ratio * (bg_bot[1] - bg_top[1]))
                b = int(bg_top[2] + ratio * (bg_bot[2] - bg_top[2]))
                draw.rectangle([0, y_line, WIDTH, y_line + 16], fill=(r, g, b))

            # 2. Dynamic Floating Particles (Stars / Dust)
            for i in range(25):
                px = (i * 77 + int(f * 4.5)) % WIDTH
                py = (i * 53 + int(math.sin(f * 0.05 + i) * 60) + 200) % 800
                p_rad = 3 if i % 2 == 0 else 5
                draw.ellipse([px - p_rad, py - p_rad, px + p_rad, py + p_rad], fill=(255, 255, 255, 120))

            # 3. Dynamic Horizon Ground
            horizon_y = 780 + shake_y
            draw.rectangle([0, horizon_y, WIDTH, HEIGHT], fill=(20, 24, 33))
            draw.line([(0, horizon_y), (WIDTH, horizon_y)], fill=(50, 60, 80), width=4)

            # 4. Characters & Action Beats
            bob_x = 960 + shake_x
            bob_y = 660 + shake_y

            if is_outro:
                emotion = "happy"
                # Draw fluffy pancakes on plate
                draw.ellipse([bob_x + 90, bob_y + 40, bob_x + 230, bob_y + 90], fill=(230, 230, 230), outline=(180, 180, 180), width=3)
                for p_i in range(3):
                    py = bob_y + 45 - p_i * 14
                    draw.rounded_rectangle([bob_x + 110, py, bob_x + 210, py + 18], radius=8, fill=(245, 180, 65))
                # Butter pat
                draw.rectangle([bob_x + 150, bob_y + 10, bob_x + 170, bob_y + 22], fill=(255, 230, 70))
            elif is_climax:
                emotion = "panicked"
            elif beat_phase == 1:
                emotion = "shocked"
            else:
                emotion = "curious"

            draw_bob_character(draw, bob_x, bob_y, emotion=emotion, t=t_sec)

            # Tabby Cat on the left
            cat_x = bob_x - 320
            cat_y = horizon_y - 45
            draw.ellipse([cat_x - 40, cat_y - 35, cat_x + 40, cat_y + 35], fill=(255, 150, 50), outline=(200, 110, 30), width=3)
            draw.polygon([(cat_x - 30, cat_y - 20), (cat_x - 20, cat_y - 55), (cat_x - 5, cat_y - 30)], fill=(255, 130, 40))
            draw.polygon([(cat_x + 5, cat_y - 30), (cat_x + 20, cat_y - 55), (cat_x + 30, cat_y - 20)], fill=(255, 130, 40))

            # 5. Telemetry Gauge (Beat 2 & 3)
            if not is_outro:
                dial_progress = (math.sin(t_sec * 3.0) + 1.0) / 2.0
                draw_telemetry_gauge(draw, 220, 420, "PHYSICS GAUGE", f"{int(dial_progress*100)}%", dial_progress, hud_font)

            # 6. Action Sound Word Comic Sticker (e.g. WHOOSH! / BOOM!)
            if is_climax and (f % 40 < 20):
                draw.text((WIDTH // 2 - 180, 340), "KABOOM!", font=sticker_font, fill=(255, 221, 51))

            # 7. Iconic Top Banner
            draw_auto_banner(draw, banner_text, banner_font, y_pos=50, fill_color=banner_color)

            # Pipe RGB frame to FFmpeg
            proc.stdin.write(img.tobytes())

            if global_frame % 300 == 0 or global_frame == total_frames:
                pct = int(global_frame / total_frames * 100)
                print(f"🎬 Render Progress: {pct}% ({global_frame}/{total_frames} frames)")

    proc.stdin.close()
    proc.wait()
    print(f"✅ Master Video rendered successfully at: {output_video_path}")
    return output_video_path
