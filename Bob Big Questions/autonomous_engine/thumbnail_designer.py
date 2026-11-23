#!/usr/bin/env python3
"""Autonomous High-CTR Thumbnail Designer for Bob Big Questions.

Follows the tested studio formula:
- Clean 2-line minimalist typography (Line 1: White, Line 2: Radiant Yellow #FFDD33)
- No rectangular text boxes or clunky borders
- High-contrast background with dramatic dark vignette
- Shocked, bulging-eyes Bob and terrified orange cat center-stage
- Curiosity-inducing visual spectacle
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH, HEIGHT = 1280, 720


def get_font(size: int):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
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


def create_high_ctr_thumbnail(line1: str, line2: str, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (WIDTH, HEIGHT), (12, 16, 28))
    draw = ImageDraw.Draw(img)

    # 1. Background Gradient / Cosmic Atmosphere
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(10 + ratio * 35)
        g = int(14 + ratio * 20)
        b = int(28 + ratio * 45)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # 2. Dramatic Light Beam / Planetary Glow
    glow_center_x, glow_center_y = 640, 480
    for rad in range(350, 40, -25):
        alpha = int(12 + (1.0 - rad / 350) * 45)
        draw.ellipse(
            [glow_center_x - rad * 1.5, glow_center_y - rad, glow_center_x + rad * 1.5, glow_center_y + rad],
            fill=(255, 180, 50, alpha)
        )

    # 3. Ground / Horizon Fissure
    horizon_y = 520
    draw.rectangle([0, horizon_y, WIDTH, HEIGHT], fill=(22, 25, 34))
    # Cracks & energy glow in ground
    draw.polygon([(640, horizon_y), (620, HEIGHT), (660, HEIGHT)], fill=(255, 120, 30))
    draw.polygon([(400, horizon_y + 40), (370, HEIGHT), (430, HEIGHT)], fill=(255, 200, 50))
    draw.polygon([(880, horizon_y + 30), (850, HEIGHT), (910, HEIGHT)], fill=(255, 140, 40))

    # 4. Shocked Bob (Center Stage)
    bob_x, bob_y = 640, 470
    head_r = 95
    skin_color = (255, 218, 185)

    # Bob's cyan hoodie
    draw.polygon([
        (bob_x - 130, bob_y + 220),
        (bob_x + 130, bob_y + 220),
        (bob_x + 90, bob_y + 70),
        (bob_x - 90, bob_y + 70)
    ], fill=(0, 206, 201), outline=(0, 160, 155), width=4)

    # Bob's head
    draw.ellipse([bob_x - head_r, bob_y - head_r, bob_x + head_r, bob_y + head_r], fill=skin_color, outline=(220, 180, 150), width=4)

    # Messy brown hair
    draw.polygon([(bob_x - head_r, bob_y - 30), (bob_x - head_r + 20, bob_y - head_r - 20), (bob_x - 20, bob_y - head_r + 10)], fill=(101, 67, 33))
    draw.polygon([(bob_x - 40, bob_y - head_r), (bob_x, bob_y - head_r - 35), (bob_x + 40, bob_y - head_r)], fill=(101, 67, 33))
    draw.polygon([(bob_x + 20, bob_y - head_r + 10), (bob_x + head_r - 20, bob_y - head_r - 20), (bob_x + head_r, bob_y - 30)], fill=(101, 67, 33))

    # Puffed red cheeks (Panicked holding breath)
    draw.ellipse([bob_x - head_r - 10, bob_y + 10, bob_x - 40, bob_y + 65], fill=(255, 110, 110))
    draw.ellipse([bob_x + 40, bob_y + 10, bob_x + head_r + 10, bob_y + 65], fill=(255, 110, 110))

    # Giant Bulging Saucer Eyes
    eye_r = 32
    draw.ellipse([bob_x - 55 - eye_r, bob_y - 15 - eye_r, bob_x - 55 + eye_r, bob_y - 15 + eye_r], fill=(255, 255, 255), outline=(30, 30, 30), width=4)
    draw.ellipse([bob_x + 55 - eye_r, bob_y - 15 - eye_r, bob_x + 55 + eye_r, bob_y - 15 + eye_r], fill=(255, 255, 255), outline=(30, 30, 30), width=4)
    # Tiny terrified pupils
    draw.ellipse([bob_x - 55 - 8, bob_y - 15 - 8, bob_x - 55 + 8, bob_y - 15 + 8], fill=(20, 20, 20))
    draw.ellipse([bob_x + 55 - 8, bob_y - 15 - 8, bob_x + 55 + 8, bob_y - 15 + 8], fill=(20, 20, 20))

    # Shocked O-shaped mouth
    draw.ellipse([bob_x - 18, bob_y + 35, bob_x + 18, bob_y + 65], fill=(60, 20, 20), outline=(20, 20, 20), width=3)

    # 5. Terrified Orange Tabby Cat
    cat_x, cat_y = 860, 520
    cat_r = 50
    draw.ellipse([cat_x - cat_r, cat_y - cat_r, cat_x + cat_r, cat_y + cat_r], fill=(255, 150, 50), outline=(200, 110, 30), width=3)
    # Cat ears
    draw.polygon([(cat_x - 40, cat_y - 30), (cat_x - 30, cat_y - 75), (cat_x - 10, cat_y - 45)], fill=(255, 130, 40))
    draw.polygon([(cat_x + 10, cat_y - 45), (cat_x + 30, cat_y - 75), (cat_x + 40, cat_y - 30)], fill=(255, 130, 40))
    # Cat green eyes
    draw.ellipse([cat_x - 30, cat_y - 15, cat_x - 10, cat_y + 10], fill=(50, 255, 120), outline=(0, 0, 0), width=2)
    draw.ellipse([cat_x + 10, cat_y - 15, cat_x + 30, cat_y + 10], fill=(50, 255, 120), outline=(0, 0, 0), width=2)

    # 6. Dark Cinematic Vignette across Top for Clean Typography
    top_dark = Image.new("RGBA", (WIDTH, 320), (0, 0, 0, 0))
    top_draw = ImageDraw.Draw(top_dark)
    for y in range(320):
        alpha = int(220 * (1.0 - (y / 320) ** 1.3))
        top_draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))
    img.paste(top_dark, (0, 0), top_dark)

    # 7. Studio Minimalist Typography (130pt White / 140pt Radiant Yellow #FFDD33)
    font_line1 = get_font(105)
    font_line2 = get_font(115)

    def draw_studio_text(text, font, y_pos, color):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x_pos = (WIDTH - text_w) // 2
        # Deep soft shadow for contrast
        for sx, sy in [(-4, 4), (4, 4), (0, 6), (0, 8)]:
            draw.text((x_pos + sx, y_pos + sy), text, font=font, fill=(0, 0, 0))
        # Crisp face
        draw.text((x_pos, y_pos), text, font=font, fill=color)

    draw_studio_text(line1.upper(), font_line1, 40, (255, 255, 255))
    draw_studio_text(line2.upper(), font_line2, 160, (255, 221, 51))

    # Save output
    img.save(str(output_path), quality=95)
    return output_path


if __name__ == "__main__":
    t_path = BASE_DIR / "exports" / "thumbnails" / "test_auto_thumb.jpg"
    create_high_ctr_thumbnail("WHAT IF YOU DRILLED", "THROUGH THE EARTH?", t_path)
    print("Thumbnail created at:", t_path)
