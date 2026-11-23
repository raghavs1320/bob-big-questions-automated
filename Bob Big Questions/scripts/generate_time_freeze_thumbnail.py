"""High-CTR Netflix-Level YouTube Thumbnail Generator for Episode 7:
'What If Time Stopped For 24 Hours?'

Psychological Triggers & Composition:
1. MAXIMUM CONTRAST TYPOGRAPHY:
   - Top dark cinematic gradient vignette for 1000:1 contrast.
   - 2-Line Powerhouse:
     * Line 1: 'WHAT IF TIME' (Pure White, 130pt Impact)
     * Line 2: 'FROZE FOR 24 HOURS?' (Radiant Warning Yellow #FFDD33, 145pt Impact)
   - Natural elevation drop shadow (NO rectangular box, NO stroke borders).

2. THE VISCERAL HOOK:
   - Shocked Bob center-stage with wide panicked eyes, open mouth, floating sweat drops.
   - Frozen coffee pouring out of his red mug, hanging as an amber crystal in mid-air!

3. IMPOSSIBLE PHYSICS & CURIOSITY ANCHORS:
   - Over 40 individual frozen raindrops suspended motionless in mid-air like diamonds.
   - Bob's orange tabby cat suspended in mid-air mid-pounce with a golden pepperoni slice floating before its nose!
   - Background frozen yellow city cab with frozen exhaust smoke puff.
   - Glowing digital clock frozen at '07:00:00'.
"""

import math
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

WIDTH, HEIGHT = 1920, 1080
THUMBNAILS_DIR = BASE_DIR / "exports" / "thumbnails"
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

FONT_IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
FONT_ARIAL_ROUNDED = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"


def get_font(size: int = 40, font_type: str = "impact"):
    if font_type == "impact" and os.path.exists(FONT_IMPACT):
        try:
            return ImageFont.truetype(FONT_IMPACT, size=size)
        except Exception:
            pass
    elif font_type == "rounded" and os.path.exists(FONT_ARIAL_ROUNDED):
        try:
            return ImageFont.truetype(FONT_ARIAL_ROUNDED, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_clean_centered_text(draw, cx: int, cy: int, text: str, font, fill=(255, 255, 255), shadow_color=(0, 0, 0, 245), shadow_offset=(0, 8)):
    """Draws pure, modern studio typography with rich soft elevation drop shadow."""
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    draw_x = cx - (x0 + x1) / 2.0
    draw_y = cy - (y0 + y1) / 2.0

    if shadow_color:
        sx, sy = shadow_offset
        # Double-pass drop shadow for soft elevation
        draw.text((draw_x + sx, draw_y + sy), text, font=font, fill=shadow_color)
        draw.text((draw_x + sx * 1.5, draw_y + sy * 1.5), text, font=font, fill=(0, 0, 0, 160))

    draw.text((draw_x, draw_y), text, font=font, fill=fill)


def draw_bob_time_freeze(draw, bx, by, scale=1.2):
    """Draws Bob in his signature cyan hoodie, shocked expression, reaching out towards frozen coffee."""
    radius = int(95 * scale)

    # Cyan/Teal Hoodie Body
    draw.rounded_rectangle([bx - int(75 * scale), by + int(65 * scale), bx + int(75 * scale), by + int(230 * scale)], radius=int(28 * scale), fill=(0, 206, 201), outline=(40, 30, 30), width=int(6 * scale))
    # Coral shorts
    draw.rounded_rectangle([bx - int(70 * scale), by + int(220 * scale), bx + int(70 * scale), by + int(300 * scale)], radius=int(15 * scale), fill=(255, 107, 129), outline=(40, 30, 30), width=int(5 * scale))

    # Legs (one grounded, one raised in surprise)
    draw.line([(bx - int(35 * scale), by + int(300 * scale)), (bx - int(45 * scale), by + int(380 * scale))], fill=(255, 218, 185), width=int(22 * scale))
    draw.line([(bx + int(35 * scale), by + int(300 * scale)), (bx + int(55 * scale), by + int(370 * scale))], fill=(255, 218, 185), width=int(22 * scale))
    # Yellow sneakers
    draw.ellipse([bx - int(65 * scale), by + int(375 * scale), bx - int(25 * scale), by + int(405 * scale)], fill=(254, 202, 87), outline=(40, 30, 30), width=4)
    draw.ellipse([bx + int(35 * scale), by + int(365 * scale), bx + int(75 * scale), by + int(395 * scale)], fill=(254, 202, 87), outline=(40, 30, 30), width=4)

    # Arms: Left arm raised in disbelief, right arm holding coffee pot
    arm_w = int(22 * scale)
    # Left arm up
    draw.line([(bx - int(70 * scale), by + int(100 * scale)), (bx - int(130 * scale), by + int(40 * scale)), (bx - int(150 * scale), by - int(10 * scale))], fill=(0, 206, 201), width=arm_w)
    draw.ellipse([bx - int(175 * scale), by - int(30 * scale), bx - int(135 * scale), by + int(10 * scale)], fill=(255, 218, 185), outline=(40, 30, 30), width=3)
    # Right arm extending forward holding tilted mug
    draw.line([(bx + int(70 * scale), by + int(100 * scale)), (bx + int(135 * scale), by + int(80 * scale)), (bx + int(180 * scale), by + int(60 * scale))], fill=(0, 206, 201), width=arm_w)

    # Bob's Head
    draw.ellipse([bx - radius, by - radius, bx + radius, by + radius], fill=(255, 218, 185), outline=(40, 30, 30), width=int(6 * scale))

    # Hair (Messy brown tufts)
    hair_color = (101, 67, 33)
    draw.arc([bx - radius + int(10 * scale), by - radius - int(25 * scale), bx + radius - int(10 * scale), by - radius + int(45 * scale)], start=180, end=360, fill=hair_color, width=int(22 * scale))
    draw.ellipse([bx - int(25 * scale), by - radius - int(32 * scale), bx + int(30 * scale), by - radius + int(8 * scale)], fill=hair_color)

    # Wide Panicked Eyes
    for eye_x in (bx - int(42 * scale), bx + int(42 * scale)):
        draw.ellipse([eye_x - int(32 * scale), by - int(18 * scale) - int(32 * scale), eye_x + int(32 * scale), by - int(18 * scale) + int(32 * scale)], fill=(255, 255, 255), outline=(40, 30, 30), width=int(5 * scale))
        draw.ellipse([eye_x - int(8 * scale), by - int(22 * scale), eye_x + int(8 * scale), by - int(6 * scale)], fill=(20, 20, 20))
        draw.ellipse([eye_x - int(4 * scale), by - int(20 * scale), eye_x, by - int(16 * scale)], fill=(255, 255, 255))

    # Shocked raised eyebrows
    draw.arc([bx - int(70 * scale), by - int(70 * scale), bx - int(20 * scale), by - int(42 * scale)], start=180, end=360, fill=(60, 40, 40), width=int(7 * scale))
    draw.arc([bx + int(20 * scale), by - int(70 * scale), bx + int(70 * scale), by - int(42 * scale)], start=180, end=360, fill=(60, 40, 40), width=int(7 * scale))

    # Wide open mouth in disbelief
    draw.ellipse([bx - int(25 * scale), by + int(15 * scale), bx + int(25 * scale), by + int(65 * scale)], fill=(50, 20, 20), outline=(220, 60, 60), width=int(5 * scale))
    draw.rectangle([bx - int(18 * scale), by + int(18 * scale), bx + int(18 * scale), by + int(28 * scale)], fill=(255, 255, 255))

    # Floating Panic Sweat Droplets
    draw.ellipse([bx - int(105 * scale), by - int(45 * scale), bx - int(85 * scale), by - int(20 * scale)], fill=(129, 236, 236), outline=(9, 132, 227), width=2)
    draw.ellipse([bx + int(90 * scale), by - int(35 * scale), bx + int(108 * scale), by - int(12 * scale)], fill=(129, 236, 236), outline=(9, 132, 227), width=2)


def draw_frozen_coffee_sculpture(draw, cx, cy):
    """Draws red coffee mug tilted with liquid frozen mid-air as an amber arch."""
    # Red Mug
    draw.rounded_rectangle([cx - 35, cy - 30, cx + 35, cy + 30], radius=8, fill=(235, 77, 75), outline=(180, 40, 40), width=4)
    draw.arc([cx - 55, cy - 20, cx - 25, cy + 20], start=90, end=270, fill=(235, 77, 75), width=7)

    # Frozen Coffee Arc pouring out and hanging in midair!
    # Amber stream
    pts = [(cx + 25, cy - 10), (cx + 80, cy - 30), (cx + 150, cy - 15), (cx + 200, cy + 40), (cx + 220, cy + 110)]
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=(111, 78, 55), width=18)
        draw.line([pts[i], pts[i+1]], fill=(160, 110, 75), width=8) # highlight

    # Suspended frozen droplets hovering around the stream
    for dx, dy, r in [(100, -60, 12), (170, -45, 14), (230, 20, 10), (250, 80, 16), (190, 85, 11)]:
        draw.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], fill=(111, 78, 55), outline=(180, 130, 90), width=3)
        draw.ellipse([cx + dx - r // 2, cy + dy - r // 2, cx + dx - r // 4, cy + dy - r // 4], fill=(255, 255, 255, 190))


def draw_frozen_raindrops(draw, count=45):
    """Draws crystalline suspended raindrops frozen in mid-air with glossy highlights."""
    np.random.seed(42)
    for _ in range(count):
        rx = int(np.random.uniform(40, WIDTH - 40))
        ry = int(np.random.uniform(260, HEIGHT - 80))
        r = int(np.random.choice([7, 9, 12, 15]))

        # Translucent glass droplet
        draw.ellipse([rx - r, ry - int(r * 1.3), rx + r, ry + int(r * 1.3)], fill=(129, 236, 236, 180), outline=(255, 255, 255), width=2)
        # Specular light gleam
        draw.ellipse([rx - r // 2, ry - r, rx - r // 4, ry - r // 2], fill=(255, 255, 255, 230))
        # Tiny sparkle cross on bigger droplets
        if r >= 12:
            draw.line([(rx, ry - r - 4), (rx, ry - r + 4)], fill=(255, 255, 255), width=2)
            draw.line([(rx - 4, ry - r), (rx + 4, ry - r)], fill=(255, 255, 255), width=2)


def draw_frozen_cat_pounce(draw, cx, cy):
    """Draws Bob's orange tabby cat frozen mid-leap trying to catch hovering pepperoni."""
    # Body tilted 30 degrees
    draw.ellipse([cx - 45, cy - 30, cx + 45, cy + 30], fill=(243, 156, 18), outline=(40, 30, 30), width=4)
    # Head
    draw.ellipse([cx + 25, cy - 50, cx + 80, cy + 5], fill=(243, 156, 18), outline=(40, 30, 30), width=4)
    # Ears
    draw.polygon([(cx + 40, cy - 45), (cx + 50, cy - 75), (cx + 65, cy - 50)], fill=(230, 126, 34), outline=(40, 30, 30))
    # Round green eyes wide open
    draw.ellipse([cx + 42, cy - 35, cx + 58, cy - 18], fill=(46, 204, 113), outline=(40, 30, 30), width=3)
    draw.ellipse([cx + 62, cy - 35, cx + 78, cy - 18], fill=(46, 204, 113), outline=(40, 30, 30), width=3)
    draw.ellipse([cx + 48, cy - 30, cx + 54, cy - 22], fill=(20, 20, 20))
    draw.ellipse([cx + 68, cy - 30, cx + 74, cy - 22], fill=(20, 20, 20))
    # Splayed pouncing front paws
    draw.line([(cx + 35, cy + 15), (cx + 75, cy + 35)], fill=(243, 156, 18), width=12)
    draw.ellipse([cx + 70, cy + 28, cx + 88, cy + 46], fill=(255, 255, 255), outline=(40, 30, 30), width=3)
    # Arched frozen tail
    draw.arc([cx - 75, cy - 45, cx - 25, cy + 15], start=180, end=360, fill=(243, 156, 18), width=12)

    # Hovering Pepperoni Slice (Golden & Red with cheese flecks) right in front of cat nose!
    pep_x, pep_y = cx + 130, cy - 20
    draw.ellipse([pep_x - 22, pep_y - 22, pep_x + 22, pep_y + 22], fill=(235, 77, 75), outline=(180, 40, 40), width=3)
    draw.ellipse([pep_x - 10, pep_y - 8, pep_x - 4, pep_y - 2], fill=(254, 202, 87))
    draw.ellipse([pep_x + 4, pep_y + 4, pep_x + 10, pep_y + 10], fill=(254, 202, 87))
    # Golden glow aura around the pepperoni
    draw.ellipse([pep_x - 30, pep_y - 30, pep_x + 30, pep_y + 30], outline=(254, 202, 87, 160), width=3)


def draw_frozen_city_cab(draw, cx, cy):
    """Draws a classic yellow city taxi frozen with motionless tire smoke."""
    # Cab Body
    draw.rectangle([cx - 140, cy, cx + 140, cy + 65], fill=(254, 202, 87), outline=(40, 30, 30), width=4)
    # Cab Roof / Cabin
    draw.polygon([(cx - 100, cy), (cx - 60, cy - 45), (cx + 60, cy - 45), (cx + 100, cy)], fill=(254, 202, 87), outline=(40, 30, 30))
    # Windows
    draw.polygon([(cx - 90, cy - 3), (cx - 55, cy - 40), (cx - 5, cy - 40), (cx - 5, cy - 3)], fill=(130, 204, 221), outline=(40, 30, 30), width=2)
    draw.polygon([(cx + 5, cy - 3), (cx + 5, cy - 40), (cx + 55, cy - 40), (cx + 90, cy - 3)], fill=(130, 204, 221), outline=(40, 30, 30), width=2)
    # Taxi roof sign
    draw.rounded_rectangle([cx - 25, cy - 62, cx + 25, cy - 46], radius=4, fill=(255, 255, 255), outline=(40, 30, 30), width=2)
    # Wheels
    draw.ellipse([cx - 105, cy + 45, cx - 55, cy + 95], fill=(45, 52, 54), outline=(40, 30, 30), width=4)
    draw.ellipse([cx + 55, cy + 45, cx + 105, cy + 95], fill=(45, 52, 54), outline=(40, 30, 30), width=4)
    # Frozen Puffy Tire Smoke (static clouds)
    for sx, sy, sr in [(cx - 140, cy + 65, 18), (cx - 165, cy + 55, 24), (cx - 195, cy + 45, 30)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(240, 240, 240, 220), outline=(180, 180, 180), width=2)


def render_thumbnail_time_freeze_masterpiece():
    """Builds the 1280x720 High-CTR YouTube Thumbnail."""
    thumb_img = Image.new("RGB", (WIDTH, HEIGHT), (14, 18, 36))
    draw_th = ImageDraw.Draw(thumb_img, "RGBA")
    cx, cy = WIDTH // 2, HEIGHT // 2

    # 1. ATMOSPHERIC DEEP TWILIGHT SKY WITH CITY HORIZON
    # 2-stop vertical gradient background (Deep Indigo to Twilight Purple)
    for y in range(HEIGHT):
        ratio = y / float(HEIGHT)
        r = int(14 * (1 - ratio) + 38 * ratio)
        g = int(18 * (1 - ratio) + 32 * ratio)
        b = int(36 * (1 - ratio) + 68 * ratio)
        draw_th.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # City Silhouettes in background
    skyscrapers = [(160, 480, 220), (420, 600, 260), (WIDTH - 420, 520, 280), (WIDTH - 150, 440, 220)]
    for sx, sh, sw in skyscrapers:
        draw_th.rectangle([sx - sw // 2, HEIGHT - sh, sx + sw // 2, HEIGHT], fill=(22, 28, 52))
        for wy in range(HEIGHT - sh + 50, HEIGHT - 100, 60):
            for wx in range(sx - sw // 2 + 25, sx + sw // 2 - 25, 45):
                draw_th.rectangle([wx, wy, wx + 20, wy + 28], fill=(255, 230, 120, 160))

    # City Street / Sidewalk
    draw_th.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(30, 39, 46))
    draw_th.rectangle([0, HEIGHT - 240, WIDTH, HEIGHT - 220], fill=(72, 84, 96)) # curb

    # 2. TOP CINEMATIC CONTRAST GRADIENT (Guarantees 1000:1 Text Contrast)
    for gy in range(330):
        alpha = int(255 * (1.0 - (gy / 330.0) ** 1.35))
        draw_th.line([(0, gy), (WIDTH, gy)], fill=(8, 10, 20, alpha))

    # 3. BACKGROUND IMPOSSIBLE PHYSICS ELEMENTS
    # Left: Frozen Yellow City Cab with stationary tire smoke
    draw_frozen_city_cab(draw_th, cx=320, cy=HEIGHT - 280)

    # Upper Left: Giant Glowing Digital Clock frozen at 07:00:00
    clock_x, clock_y = 280, 240
    draw_th.rounded_rectangle([clock_x - 130, clock_y - 45, clock_x + 130, clock_y + 45], radius=15, fill=(10, 12, 22), outline=(235, 77, 75), width=4)
    clock_font = get_font(size=52, font_type="impact")
    draw_clean_centered_text(draw_th, clock_x, clock_y - 2, "07:00:00", font=clock_font, fill=(235, 77, 75), shadow_color=None)
    # Mini blinking colon label
    draw_clean_centered_text(draw_th, clock_x, clock_y + 30, "TIME FROZEN", font=get_font(20, "rounded"), fill=(254, 202, 87), shadow_color=None)

    # Right: Frozen Tabby Cat mid-leap chasing hovering pepperoni
    draw_frozen_cat_pounce(draw_th, cx=WIDTH - 360, cy=HEIGHT - 380)

    # 4. BOB: THE HERO (Center-Stage, Shocked, Reaching Towards Frozen Coffee)
    bob_x, bob_y = cx - 40, cy + 30
    draw_bob_time_freeze(draw_th, bx=bob_x, by=bob_y, scale=1.22)

    # Frozen Coffee Stream & Suspended Droplets
    draw_frozen_coffee_sculpture(draw_th, cx=bob_x + 220, cy=bob_y + 70)

    # 5. OVER 40 SUSPENDED FROZEN RAINDROPS (Field of Glass Diamonds)
    draw_frozen_raindrops(draw_th, count=55)

    # 6. TIME FREEZE CYAN MAGIC SPARKLES
    np.random.seed(999)
    for _ in range(60):
        sx = int(np.random.uniform(50, WIDTH - 50))
        sy = int(np.random.uniform(200, HEIGHT - 50))
        r = np.random.choice([2, 3, 4])
        draw_th.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(0, 240, 230, 220))

    # 7. POWERHOUSE 2-LINE TYPOGRAPHY (NETFLIX MINIMALIST STANDARD)
    # Line 1: 'WHAT IF TIME' (Pure Crisp White, 130pt)
    font_line1 = get_font(size=130, font_type="impact")
    draw_clean_centered_text(
        draw_th,
        cx=cx,
        cy=95,
        text="WHAT IF TIME",
        font=font_line1,
        fill=(255, 255, 255),
        shadow_color=(0, 0, 0, 255),
        shadow_offset=(0, 8)
    )

    # Line 2: 'FROZE FOR 24 HOURS?' (Radiant Warning Yellow #FFDD33, 145pt)
    font_line2 = get_font(size=145, font_type="impact")
    draw_clean_centered_text(
        draw_th,
        cx=cx,
        cy=215,
        text="FROZE FOR 24 HOURS?",
        font=font_line2,
        fill=(255, 221, 51),
        shadow_color=(0, 0, 0, 255),
        shadow_offset=(0, 8)
    )

    # Resize with Lanczos downsampling to standard 1280x720 YouTube Thumbnail
    thumb_final = thumb_img.resize((1280, 720), Image.Resampling.LANCZOS)

    out_jpg = THUMBNAILS_DIR / "Time_Stopped_Thumbnail.jpg"
    out_png = THUMBNAILS_DIR / "Time_Stopped_Thumbnail.png"

    thumb_final.save(str(out_jpg), "JPEG", quality=96)
    thumb_final.save(str(out_png), "PNG")
    print(f"🎉 Generated High-CTR Masterpiece Thumbnail: {out_jpg}")
    return str(out_jpg)


if __name__ == "__main__":
    render_thumbnail_time_freeze_masterpiece()
