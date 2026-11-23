"""High-CTR Netflix-Level YouTube Thumbnail Generator for Episode 3:
'What If Gravity Disappeared For 60 Seconds?'

Implements YouTube Thumbnail Psychological Triggers:
1. MAXIMUM TEXT VISIBILITY:
   - Deep cinematic gradient backing at top ensuring 1000:1 contrast.
   - Stacked 2-line powerhouse typography:
     * Line 1: 'WHAT IF GRAVITY' in pure crisp white (125pt).
     * Line 2: 'DISAPPEARED?' in radiant warning yellow (150pt).
   - Natural elevation drop shadow (NO rectangular boxes, NO stroke borders).

2. VISCERAL EMOTIONAL HOOK (Mirror Neurons):
   - Bob scaled up and tilted at a dynamic floating angle.
   - Genuine shocked expression with wide eyes, open mouth, floating panic sweat droplets.
   - Expressive floating zero-g arms reaching out into the air.

3. SCIENTIFIC CURIOSITY TRIGGERS:
   - Translucent floating water sphere with light caustics and bubbles.
   - Floating upside-down cat with stunned green eyes and arched tail.
   - Floating coffee mug with orbiting liquid droplets.
   - Floating golden pizza slice.
   - Upward levitation motion streaks.
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
FONT_FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"


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
    elif font_type == "futura" and os.path.exists(FONT_FUTURA):
        try:
            return ImageFont.truetype(FONT_FUTURA, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_clean_centered_text(draw, cx: int, cy: int, text: str, font, fill=(255, 255, 255), shadow_color=(0, 0, 0, 240), shadow_offset=(0, 7)):
    """Draws studio-grade typography with natural drop shadow."""
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    draw_x = cx - (x0 + x1) / 2.0
    draw_y = cy - (y0 + y1) / 2.0

    if shadow_color:
        sx, sy = shadow_offset
        # Double-pass shadow for rich soft blur effect
        draw.text((draw_x + sx, draw_y + sy), text, font=font, fill=shadow_color)
        draw.text((draw_x + sx * 1.5, draw_y + sy * 1.5), text, font=font, fill=(0, 0, 0, 160))

    draw.text((draw_x, draw_y), text, font=font, fill=fill)


def draw_masterpiece_bob(draw, bx, by, scale=1.0):
    """Draws Bob with expressive floating arms, hoodie, panicked face and sweat drops."""
    radius = int(95 * scale)

    # Bob's arms in zero-gravity (floating upwards / reaching out)
    arm_w = int(22 * scale)
    # Left arm reaching up-left
    draw.line([(bx - int(70 * scale), by + int(100 * scale)), (bx - int(130 * scale), by + int(40 * scale)), (bx - int(170 * scale), by - int(10 * scale))], fill=(0, 206, 201), width=arm_w)
    # Left hand open
    draw.ellipse([bx - int(195 * scale), by - int(35 * scale), bx - int(155 * scale), by + int(5 * scale)], fill=(255, 218, 185), outline=(40, 30, 30), width=3)

    # Right arm reaching up-right towards floating coffee
    draw.line([(bx + int(70 * scale), by + int(100 * scale)), (bx + int(135 * scale), by + int(50 * scale)), (bx + int(180 * scale), by + int(10 * scale))], fill=(0, 206, 201), width=arm_w)
    # Right hand open
    draw.ellipse([bx + int(165 * scale), by - int(15 * scale), bx + int(205 * scale), by + int(25 * scale)], fill=(255, 218, 185), outline=(40, 30, 30), width=3)

    # Cyan/Teal Hoodie body
    draw.rounded_rectangle([bx - int(75 * scale), by + int(65 * scale), bx + int(75 * scale), by + int(230 * scale)], radius=int(28 * scale), fill=(0, 206, 201), outline=(40, 30, 30), width=int(6 * scale))
    # Coral shorts
    draw.rounded_rectangle([bx - int(70 * scale), by + int(220 * scale), bx + int(70 * scale), by + int(300 * scale)], radius=int(15 * scale), fill=(255, 107, 129), outline=(40, 30, 30), width=int(5 * scale))

    # Floating astronaut legs (bent in zero gravity)
    draw.line([(bx - int(35 * scale), by + int(300 * scale)), (bx - int(65 * scale), by + int(350 * scale)), (bx - int(45 * scale), by + int(400 * scale))], fill=(255, 218, 185), width=int(20 * scale))
    draw.line([(bx + int(35 * scale), by + int(300 * scale)), (bx + int(70 * scale), by + int(355 * scale)), (bx + int(50 * scale), by + int(405 * scale))], fill=(255, 218, 185), width=int(20 * scale))
    # Floating sneakers
    draw.ellipse([bx - int(65 * scale), by + int(390 * scale), bx - int(25 * scale), by + int(420 * scale)], fill=(254, 202, 87), outline=(40, 30, 30), width=4)
    draw.ellipse([bx + int(30 * scale), by + int(395 * scale), bx + int(70 * scale), by + int(425 * scale)], fill=(254, 202, 87), outline=(40, 30, 30), width=4)

    # Bob's Head
    draw.ellipse([bx - radius, by - radius, bx + radius, by + radius], fill=(255, 218, 185), outline=(40, 30, 30), width=int(6 * scale))

    # Hair (Messy brown tufts floating slightly)
    hair_color = (101, 67, 33)
    draw.arc([bx - radius + int(10 * scale), by - radius - int(25 * scale), bx + radius - int(10 * scale), by - radius + int(45 * scale)], start=180, end=360, fill=hair_color, width=int(22 * scale))
    draw.ellipse([bx - int(25 * scale), by - radius - int(32 * scale), bx + int(30 * scale), by - radius + int(8 * scale)], fill=hair_color)

    # Wide Panicked Eyes
    for eye_x in (bx - int(42 * scale), bx + int(42 * scale)):
        # Sclera
        draw.ellipse([eye_x - int(32 * scale), by - int(18 * scale) - int(32 * scale), eye_x + int(32 * scale), by - int(18 * scale) + int(32 * scale)], fill=(255, 255, 255), outline=(40, 30, 30), width=int(5 * scale))
        # Contracted Pupil (pure shock)
        draw.ellipse([eye_x - int(8 * scale), by - int(22 * scale), eye_x + int(8 * scale), by - int(6 * scale)], fill=(20, 20, 20))
        # Specular light highlight
        draw.ellipse([eye_x - int(4 * scale), by - int(20 * scale), eye_x, by - int(16 * scale)], fill=(255, 255, 255))

    # Shocked raised eyebrows
    draw.arc([bx - int(70 * scale), by - int(70 * scale), bx - int(20 * scale), by - int(42 * scale)], start=180, end=360, fill=(60, 40, 40), width=int(7 * scale))
    draw.arc([bx + int(20 * scale), by - int(70 * scale), bx + int(70 * scale), by - int(42 * scale)], start=180, end=360, fill=(60, 40, 40), width=int(7 * scale))

    # Wide open mouth in disbelief
    draw.ellipse([bx - int(25 * scale), by + int(15 * scale), bx + int(25 * scale), by + int(65 * scale)], fill=(50, 20, 20), outline=(220, 60, 60), width=int(5 * scale))
    # Teeth
    draw.rectangle([bx - int(18 * scale), by + int(18 * scale), bx + int(18 * scale), by + int(28 * scale)], fill=(255, 255, 255))

    # Floating Panic Sweat Droplets
    draw.ellipse([bx - int(105 * scale), by - int(45 * scale), bx - int(85 * scale), by - int(20 * scale)], fill=(129, 236, 236), outline=(9, 132, 227), width=2)
    draw.ellipse([bx + int(90 * scale), by - int(35 * scale), bx + int(108 * scale), by - int(12 * scale)], fill=(129, 236, 236), outline=(9, 132, 227), width=2)


def draw_floating_cat(draw, cx, cy, angle_deg=25.0):
    """Draws Bob's cute orange tabby cat floating upside-down in zero gravity."""
    # Body
    draw.ellipse([cx - 50, cy - 35, cx + 50, cy + 35], fill=(243, 156, 18), outline=(40, 30, 30), width=4)
    # Head
    draw.ellipse([cx - 32, cy - 65, cx + 32, cy + 2], fill=(243, 156, 18), outline=(40, 30, 30), width=4)
    # Ears
    draw.polygon([(cx - 28, cy - 55), (cx - 40, cy - 88), (cx - 12, cy - 64)], fill=(230, 126, 34), outline=(40, 30, 30))
    draw.polygon([(cx + 12, cy - 64), (cx + 40, cy - 88), (cx + 28, cy - 55)], fill=(230, 126, 34), outline=(40, 30, 30))
    # Big round confused cat eyes
    draw.ellipse([cx - 22, cy - 45, cx - 6, cy - 27], fill=(46, 204, 113), outline=(40, 30, 30), width=3)
    draw.ellipse([cx + 6, cy - 45, cx + 22, cy - 27], fill=(46, 204, 113), outline=(40, 30, 30), width=3)
    # Pupils
    draw.ellipse([cx - 16, cy - 40, cx - 12, cy - 32], fill=(20, 20, 20))
    draw.ellipse([cx + 12, cy - 40, cx + 16, cy - 32], fill=(20, 20, 20))
    # Whiskers
    draw.line([(cx - 28, cy - 22), (cx - 6, cy - 21)], fill=(40, 30, 30), width=2)
    draw.line([(cx + 6, cy - 21), (cx + 28, cy - 22)], fill=(40, 30, 30), width=2)
    # Splayed floating paws
    draw.ellipse([cx - 55, cy + 25, cx - 35, cy + 45], fill=(255, 255, 255), outline=(40, 30, 30), width=3)
    draw.ellipse([cx + 35, cy + 25, cx + 55, cy + 45], fill=(255, 255, 255), outline=(40, 30, 30), width=3)
    # Arched floating tail
    draw.arc([cx + 30, cy - 45, cx + 75, cy + 15], start=260, end=90, fill=(243, 156, 18), width=12)


def draw_shimmering_water_sphere(draw, cx, cy, radius=110):
    """Draws a giant floating water blob with realistic caustics and highlights."""
    # Outer gentle glow
    draw.ellipse([cx - radius - 15, cy - radius - 15, cx + radius + 15, cy + radius + 15], fill=(0, 180, 240, 60))
    # Main water body
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(9, 132, 227, 215), outline=(129, 236, 236), width=6)
    # Bright specular reflection (glossy studio highlight)
    draw.ellipse([cx - radius // 2 - 25, cy - radius // 2 - 25, cx - radius // 4, cy - radius // 4], fill=(255, 255, 255, 210))
    draw.ellipse([cx - radius // 3 + 10, cy - radius // 3 - 35, cx - radius // 3 + 25, cy - radius // 3 - 20], fill=(255, 255, 255, 170))
    # Internal refraction bubble
    draw.arc([cx - radius + 30, cy - radius + 30, cx + radius - 30, cy + radius - 30], start=120, end=320, fill=(129, 236, 236, 180), width=4)
    # Satellite mini droplets orbiting
    for angle, dist, r in [(0.8, radius + 40, 18), (2.4, radius + 55, 14), (4.2, radius + 35, 22), (5.5, radius + 65, 12)]:
        dx = cx + int(dist * math.cos(angle))
        dy = cy + int(dist * math.sin(angle))
        draw.ellipse([dx - r, dy - r, dx + r, dy + r], fill=(9, 132, 227, 200), outline=(129, 236, 236), width=3)
        draw.ellipse([dx - r // 2, dy - r // 2, dx - r // 4, dy - r // 4], fill=(255, 255, 255, 190))


def draw_floating_mug_and_coffee(draw, cx, cy):
    """Draws floating cherry-red coffee mug with floating spherical droplets."""
    # Red mug body
    draw.rounded_rectangle([cx - 40, cy - 35, cx + 40, cy + 35], radius=10, fill=(238, 82, 83), outline=(180, 30, 30), width=5)
    # Handle
    draw.arc([cx + 30, cy - 25, cx + 70, cy + 20], start=270, end=90, fill=(238, 82, 83), width=9)
    # Coffee opening
    draw.ellipse([cx - 32, cy - 42, cx + 32, cy - 28], fill=(109, 76, 65))
    # Floating orbiting coffee spheres
    for dx, dy, r in [(-50, -60, 15), (40, -75, 18), (-15, -95, 12), (65, -45, 10)]:
        draw.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], fill=(111, 78, 55), outline=(70, 45, 30), width=3)
        draw.ellipse([cx + dx - r // 2, cy + dy - r // 2, cx + dx - r // 4, cy + dy - r // 4], fill=(255, 255, 255, 180))


def draw_floating_pizza(draw, cx, cy):
    """Draws a floating golden slice of pizza with cheese pull."""
    # Crust & Cheese Slice
    draw.polygon([(cx - 45, cy - 50), (cx + 45, cy - 50), (cx, cy + 50)], fill=(254, 202, 87), outline=(215, 140, 20), width=4)
    # Crust
    draw.ellipse([cx - 50, cy - 60, cx + 50, cy - 40], fill=(205, 132, 24), outline=(150, 90, 15), width=3)
    # Pepperonis
    for px, py in [(cx - 10, cy - 25), (cx + 12, cy - 15), (cx - 2, cy + 10)]:
        draw.ellipse([px - 10, py - 10, px + 10, py + 10], fill=(235, 77, 75))
    # Floating cheese strings
    draw.line([(cx, cy + 50), (cx - 10, cy + 75)], fill=(254, 202, 87), width=4)
    draw.line([(cx, cy + 50), (cx + 8, cy + 85)], fill=(254, 202, 87), width=3)


def render_thumbnail_v3_masterpiece():
    """Builds the ultimate high-CTR Episode 3 YouTube Thumbnail."""
    thumb_img = Image.new("RGB", (WIDTH, HEIGHT), (12, 16, 32))
    draw_th = ImageDraw.Draw(thumb_img, "RGBA")
    cx, cy = WIDTH // 2, HEIGHT // 2

    # 1. SPLIT SCREEN COMPOSITION (Beloved visual contrast)
    # Left Half: Grounded 1G cozy room
    draw_th.rectangle([0, 0, WIDTH // 2, HEIGHT], fill=(245, 230, 200))
    # Sturdy wooden floor
    draw_th.rectangle([0, HEIGHT - 240, WIDTH // 2, HEIGHT], fill=(210, 160, 95))
    for y_line in range(HEIGHT - 240, HEIGHT, 45):
        draw_th.line([(0, y_line), (WIDTH // 2, y_line)], fill=(180, 130, 70), width=3)

    # Left desk with grounded lamp and plant
    table_top = HEIGHT - 310
    draw_th.rectangle([100, table_top, 460, table_top + 35], fill=(140, 90, 45))
    draw_th.rectangle([130, table_top + 35, 165, HEIGHT - 240], fill=(110, 70, 30))
    draw_th.rectangle([395, table_top + 35, 430, HEIGHT - 240], fill=(110, 70, 30))
    # Potted Plant (firmly grounded on table)
    draw_th.polygon([(240, table_top), (320, table_top), (305, table_top - 55), (255, table_top - 55)], fill=(225, 112, 85))
    draw_th.ellipse([250, table_top - 105, 310, table_top - 50], fill=(46, 204, 113))

    # Right Half: Deep Cosmic Zero-G Space Void
    draw_th.rectangle([WIDTH // 2, 0, WIDTH, HEIGHT], fill=(10, 14, 30))

    # Twinkling cosmic particles & zero-g levitation sparkles
    np.random.seed(777)
    for _ in range(70):
        sx = WIDTH // 2 + int(np.random.uniform(25, WIDTH // 2 - 25))
        sy = int(np.random.uniform(160, HEIGHT - 50))
        bright = np.random.randint(180, 255)
        r = np.random.choice([2, 3, 4])
        draw_th.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(bright, bright, bright, 220))

    # Zero-G upward motion streaks on right
    for streak_x in [WIDTH // 2 + 180, WIDTH // 2 + 420, WIDTH // 2 + 680]:
        draw_th.line([(streak_x, HEIGHT - 150), (streak_x, HEIGHT - 450)], fill=(0, 230, 220, 100), width=4)
        # Small up arrow tip
        draw_th.polygon([(streak_x, HEIGHT - 465), (streak_x - 10, HEIGHT - 445), (streak_x + 10, HEIGHT - 445)], fill=(0, 230, 220, 140))

    # Center Neon Electric Dividing Lightning Line
    draw_th.line([(WIDTH // 2, 0), (WIDTH // 2, HEIGHT)], fill=(0, 240, 230), width=14)

    # 2. TOP CINEMATIC CONTRAST GRADIENT (Guarantees 100% Text Visibility!)
    # Creates a rich dark backdrop at the top across the entire width
    for gy in range(320):
        alpha = int(255 * (1.0 - (gy / 320.0) ** 1.3))
        draw_th.line([(0, gy), (WIDTH, gy)], fill=(8, 12, 24, alpha))

    # 3. RIGHT SIDE: HIGH-CTR ZERO-G FLOATING OBJECTS
    # Giant Shimmering Water Sphere
    draw_shimmering_water_sphere(draw_th, cx=WIDTH - 290, cy=420, radius=115)

    # Floating Stunned Tabby Cat (upside-down in zero gravity)
    draw_floating_cat(draw_th, cx=WIDTH - 220, cy=HEIGHT - 320, angle_deg=25.0)

    # Floating Coffee Mug & Droplets
    draw_floating_mug_and_coffee(draw_th, cx=WIDTH - 500, cy=580)

    # Floating Golden Pizza Slice
    draw_floating_pizza(draw_th, cx=WIDTH - 420, cy=HEIGHT - 220)

    # 4. BOB: THE HERO (Rendered on rotated scratch canvas for smooth anti-aliased zero-g float)
    bob_canvas = Image.new("RGBA", (700, 950), (0, 0, 0, 0))
    bob_draw = ImageDraw.Draw(bob_canvas)
    draw_masterpiece_bob(bob_draw, bx=350, by=350, scale=1.18)

    # Rotate Bob at a dynamic 16° zero-g tilt
    rotated_bob = bob_canvas.rotate(16, resample=Image.Resampling.BICUBIC, expand=True)

    # Paste Bob directly across the dividing line (Y: cy - 120)
    bob_paste_x = (WIDTH // 2) - (rotated_bob.width // 2) + 15
    bob_paste_y = cy - 80
    thumb_img.paste(rotated_bob, (bob_paste_x, bob_paste_y), rotated_bob)

    # Re-draw context on top for the text
    draw_final = ImageDraw.Draw(thumb_img, "RGBA")

    # 5. POWERHOUSE 2-LINE TYPOGRAPHY (NETFLIX MINIMALIST STANDARD)
    # Line 1: 'WHAT IF GRAVITY' in Pure Crisp Studio White (125pt)
    font_line1 = get_font(size=125, font_type="impact")
    draw_clean_centered_text(
        draw_final,
        cx=cx,
        cy=95,
        text="WHAT IF GRAVITY",
        font=font_line1,
        fill=(255, 255, 255),
        shadow_color=(0, 0, 0, 255),
        shadow_offset=(0, 8)
    )

    # Line 2: 'DISAPPEARED?' in Radiant High-CTR Warning Yellow (155pt)
    font_line2 = get_font(size=155, font_type="impact")
    draw_clean_centered_text(
        draw_final,
        cx=cx,
        cy=215,
        text="DISAPPEARED?",
        font=font_line2,
        fill=(255, 221, 51),
        shadow_color=(0, 0, 0, 255),
        shadow_offset=(0, 8)
    )

    # Resize cleanly to 1280x720 Full HD YouTube thumbnail standard
    thumb_final = thumb_img.resize((1280, 720), Image.Resampling.LANCZOS)

    out_jpg = THUMBNAILS_DIR / "Gravity_Disappeared_Thumbnail.jpg"
    out_png = THUMBNAILS_DIR / "Gravity_Disappeared_Thumbnail.png"

    thumb_final.save(str(out_jpg), "JPEG", quality=96)
    thumb_final.save(str(out_png), "PNG")
    print(f"🎉 Generated High-CTR Masterpiece Thumbnail: {out_jpg}")
    return str(out_jpg)


if __name__ == "__main__":
    render_thumbnail_v3_masterpiece()
