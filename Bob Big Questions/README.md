# 📺 BOB BIG QUESTIONS — CHANNEL BIBLE & AI HANDOVER SPEC

> **Official Channel Name:** **Bob Big Questions**  
> **Genre:** 2D Procedural Animated Science & "What-If" Storytelling  
> **Target Audience:** Universal (Kids, Teens & Adults) — Global Family-Friendly  
> **Production Cost:** **$0.00 per video** (100% Free Tiers & Local Hardware Acceleration)  
> **Monetization Status:** 100% Original IP & Animation — Fully Compliant with YouTube Partner Program (YPP)

---

## 1. Executive Summary & Brand Identity

**Bob Big Questions** explores absurd, hilarious, and scientifically accurate *"What Happens If...?"* questions through the misadventures of **Bob**—a lovable, curious cartoon hero who frequently gets catapulted, frozen, weightless, or launched into cosmic events, yet always survives with his favorite food or cat in hand.

### Key Character: Bob
* **Appearance:** Warm peach skin (`#FFDAB9`), messy brown hair tufts (`#654321`), signature cyan hoodie (`#00CEC9`), and coral red shorts (`#FF6B81`).
* **Personality:** Curious, innocent, expressive, resilient.
* **Signature Props:** 
  * Stack of fluffy golden pancakes topped with square yellow butter pat
  * Red coffee mug
  * Orange tabby cat with green round eyes
  * Inflatable emergency yellow sofa

---

## 2. Technical Production Specifications

Any future AI or developer continuing this channel **MUST** adhere to the following rules:

### A. Video & Animation Standards
* **Resolution:** 1080p Full HD ($1920 \times 1080$).
* **Framerate:** 30 FPS.
* **Encoding Engine:** Apple Silicon Hardware VideoToolbox (`-c:v h264_videotoolbox`, `-b:v 9000k`, `-pix_fmt yuv420p`).
* **Render Speed:** ~110–130 FPS on Apple Silicon (~28–40 seconds for a full 2-minute video).

### B. Frame-Accurate Zero-Drift Synchronization
* **The Rule:** NEVER use static hardcoded timestamps for scene cuts (e.g. `if t < 10: Scene 1`).
* **The Mathematical Solution:**
  1. Synthesize voiceover audio for each scene/sentence independently (`scene1.m4a`, `scene2.m4a`, etc.).
  2. Measure each audio file's exact duration to the millisecond using `get_audio_duration()`.
  3. Calculate the exact frame count:
     $$\text{frames}_i = \text{int}(\text{round}(\text{duration}_i \times 30))$$
  4. Render Scene $i$ for **exactly** $\text{frames}_i$ frames.
  5. Concatenate audio tracks in matching sequence.
  6. **Result:** $0.000\text{s}$ audio-visual drift across the entire video.

### C. Typography Standards
* **Primary Cartoon Font (Titles & Dialogues):** **`Arial Rounded MT Bold`** (`/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf`).
  * Plump, friendly, modern cartoon aesthetic used by Netflix Kids, Cartoon Network, and Duolingo.
* **Secondary Telemetry / Data / HUD Font:** **`Futura Bold`** (`/System/Library/Fonts/Supplemental/Futura.ttc`).
  * Clean, geometric, modernist scientific look (Kurzgesagt style).
* **High-Impact Thumbnail Font:** **`Impact`** (`/System/Library/Fonts/Supplemental/Impact.ttf`) or `Arial Rounded MT Bold`.

### D. Banner & Badge Design Rules
* **NO Harsh White Outlines:** Never put heavy white borders around text boxes.
* **Modern Clean Flat Studio Pills:** Use vibrant solid rounded rectangles (`fill=(255, 71, 87)` or `(254, 202, 87)`) with soft, translucent drop shadows underneath.
* **True Mathematical Ink-Centering Formula:**
  ```python
  x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
  ink_w = x1 - x0
  ink_h = y1 - y0

  box_w = ink_w + pad_x * 2
  box_h = ink_h + pad_y * 2

  box = [cx - box_w // 2, center_y - box_h // 2, cx + box_w // 2, center_y + box_h // 2]
  shadow = [box[0], box[1] + 4, box[2], box[3] + 4]

  draw.rounded_rectangle(shadow, radius=radius, fill=(20, 20, 30))
  draw.rounded_rectangle(box, radius=radius, fill=fill)

  # Ink-centered text coordinate:
  draw_x = cx - (x0 + x1) / 2.0
  draw_y = center_y - (y0 + y1) / 2.0
  draw.text((draw_x, draw_y), text, font=font, fill=text_fill)
  ```
  This guarantees identical padding on all 4 sides ($L = R = 38\text{px}$, $T = B = 14\text{px}$) with zero text clipping or border overflow.

### E. Action Words & Comic Sound Effects
* Words like *"SKRRRRRRRT!"*, *"WHOOSH!"*, *"SLAM!"*, *"TSUNAMI SURF!"* float **freely** over the action.
* Rendered with bold outlines (`stroke_width=8`, `stroke_fill=(30, 30, 40)`) and drop shadows—never trapped in boxes.

### F. Zero Emoji Tofu Boxes
* Never pass raw Unicode emojis to PIL text routines (causes `[ ]` missing glyph boxes).
* All icons (golden bells, stars, thumbs-up badges, speedometers, checkmarks) are **custom procedural vector shapes** drawn with PIL primitives.

### G. Audio & Music Specifications
* **Narrator Voice:** Edge-TTS **`en-US-AvaNeural`** (Ava — Studio-grade, natural, warm American female voice).
* **Speed:** `rate='+2%'` for high-retention cartoon cadence.
* **Soundtrack:** Algorithmic procedural 48kHz stereo animated marimba & walking bass groove synthesized via NumPy (100% royalty-free, zero copyright risk).
* **Sound Mixing:** Audio ducking ($30\%$ background music under voice) normalized to **-14 LUFS** (YouTube broadcast standard).

---

## 3. Catalog of Produced Episodes

| Episode | Title | Runtime | Resolution | Video File | Thumbnail File | Status |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- |
| **01** | What Happens If You Don't Sleep For 7 Days? | 57.5s | 1080p 30fps | `exports/videos/What_Happens_If_You_Dont_Sleep_7_Days.mp4` | `exports/thumbnails/Cartoon_Sleep_Thumbnail.jpg` | **LIVE (PUBLIC):** [youtu.be/xq7n3SZvbV4](https://youtu.be/xq7n3SZvbV4) |
| **02** | What Happens If The Sun Disappeared For 7 Days? | 2:03 (123.2s) | 1080p 30fps | `exports/videos/What_If_The_Sun_Disappeared_2Min.mp4` | `exports/thumbnails/Sun_Disappeared_Thumbnail.jpg` | **LIVE (PUBLIC):** [youtu.be/tWmkCW4GxLY](https://youtu.be/tWmkCW4GxLY) |
| **03** | What Happens If Gravity Disappeared For 60 Seconds? | 2:33 (153.2s) | 1080p 30fps | `exports/videos/What_If_Gravity_Disappeared_2m30s.mp4` | `exports/thumbnails/Gravity_Disappeared_Thumbnail.jpg` | Ready for Upload |
| **04** | What Happens If The Earth Stopped Spinning For 5 Seconds? | 1:48 (107.7s) | 1080p 30fps | `exports/videos/What_If_Earth_Stopped_Spinning_5s.mp4` | `exports/thumbnails/Earth_Stopped_Spinning_Thumbnail.jpg` | Ready for Upload |
| **06** | What If All Oceans Dried Up For 24 Hours? | 2:17 (137.0s) | 1080p 30fps | `exports/videos/What_If_Oceans_Dried_Up_2m17s.mp4` | `exports/thumbnails/Ocean_Dried_Up_Thumbnail.jpg` | Ready for Upload (Flagship 2m 17s) |

*(Note: Episode 5 "What If Everyone Jumped" was deleted from local disk by user).*

---

## 4. YouTube API & One-Click Uploader Automation

* **Official Channel Handle:** **@bobbigquestions**
* **Channel ID:** `UC-42OsmeaYfyfenNXSBlFNA`
* **OAuth Credentials:** `client_secrets.json` (Desktop App Client: `147565475363-pl2a2317ivn77ce66pdr4427806975pk...`)
* **Live OAuth Token:** `token.json` (Active, auto-refreshing offline token)
* **Phone Verification:** Completed & Verified (unlocked custom thumbnails & videos >15m)

### One-Command CLI Usage:
```bash
# Check channel identity & stats:
python youtube_upload.py --channel

# List recent uploads:
python youtube_upload.py --list

# Upload any episode preset (1 to 6) as public, unlisted, or private:
python youtube_upload.py --episode 1 --privacy public
python youtube_upload.py --episode 6 --privacy private

# Update thumbnail on an existing video:
python youtube_upload.py --set-thumb <VIDEO_ID> --thumb "exports/thumbnails/My_Thumb.jpg"
```

---

## 5. Multi-Language Audio Expansion Guide

To expand **Bob Big Questions** into non-English markets without re-animating:
1. Translate the scene strings into Spanish, Hindi, French, German, or Japanese.
2. Synthesize using the matching neural voice:
   * **Hindi:** `hi-IN-SwaraNeural` (Female) or `hi-IN-MadhurNeural` (Male)
   * **Spanish:** `es-MX-DaliaNeural`
   * **French:** `fr-FR-DeniseNeural`
3. Upload as a **Multi-Language Audio Track** on the same YouTube video so viewers globally hear their native language.

---

## 5. Folder Structure Reference

```
Bob Big Questions/
├── .env                               <- Live API keys & credentials
├── .env.example                       <- Credential template for new environments
├── config.py                          <- Self-contained path & credential loader
├── README.md                          <- This Master Channel Bible & AI Spec
├── CHAT_HISTORY_AND_DECISIONS.md      <- Full record of requests, feedback & iterations
├── scripts/                           <- Production Python renderers
│   ├── render_earth_stopped_spinning_masterpiece.py
│   ├── render_gravity_disappeared_2m30s.py
│   ├── render_sun_disappeared_2min.py
│   └── render_cartoon_sleep_masterpiece.py
├── exports/
│   ├── videos/                        <- 1080p Full HD master exports
│   └── thumbnails/                    <- 1280x720 high-CTR thumbnails (.jpg & .png)
└── audio/                             <- Master voiceovers & synthesized music grooves
```

---

## 6. Environment Variables, API Keys & Zero-Cost Infrastructure

Every AI and developer working in this folder operates at **$0.00 infrastructure cost**:

1. **Google Gemini API Key (`GEMINI_API_KEY`):**
   * Configured in `.env` (and root `.env`).
   * **Free Tier Quota:** 15 RPM / 1,500 requests per day on Google AI Studio (`gemini-3.5-flash-lite`).
   * Generates story scripts, YouTube titles, and descriptions at $0.00 cost.
2. **Microsoft Azure Neural Voice Engine (`edge-tts`):**
   * **No API Key Required:** Fully free, unlimited, studio-grade 48kHz neural synthesis.
   * Default narrator: `en-US-AvaNeural` at `+2%` speech rate.
3. **NumPy Procedural Music Synthesizer:**
   * Pure Python algorithmic sound synthesis.
   * Generates full 48kHz stereo animated marimba and walking bass grooves locally in 1 second.
   * Zero copyright claims, 100% royalty-free.
4. **Apple Silicon Hardware VideoToolbox:**
   * Uses `-c:v h264_videotoolbox` directly on your Mac's M-chip.
   * Renders 1080p Full HD at ~110–130 FPS (full 2-minute video in under 35 seconds).

