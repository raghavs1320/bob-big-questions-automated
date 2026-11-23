#!/usr/bin/env python3
"""Autonomous Script & Screenplay Generator for Bob Big Questions.

Picks a randomized runtime between 60s and 150s, crafts a hilarious,
child-friendly (7-year-old level) scientific adventure with 1-second visual cues,
and outputs complete scene timelines and YouTube metadata.
"""

import os
import json
import random
import requests
from typing import Dict, Any

# Random duration choices between 1:00 (60s) and 2:30 (150s)
DURATION_PRESETS = [60.0, 75.0, 90.0, 105.0, 120.0, 135.0, 150.0]


def generate_screenplay(topic_info: Dict[str, Any], gemini_api_key: str = None) -> Dict[str, Any]:
    """Generates an engaging, high-humor screenplay for Bob with randomized duration."""
    target_duration = random.choice(DURATION_PRESETS)
    key = gemini_api_key or os.environ.get("GEMINI_API_KEY", "")

    # Calculate scene count: 4 scenes for 60s, 6 for 90s, 7 for 120s, 8 for 150s
    if target_duration <= 75.0:
        scene_count = 4
    elif target_duration <= 105.0:
        scene_count = 5
    elif target_duration <= 125.0:
        scene_count = 6
    else:
        scene_count = 8

    topic = topic_info["topic"]
    title = topic_info["title"]
    hook = topic_info.get("hook", "")
    core_science = topic_info.get("core_science", "")

    if key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={key}"
            prompt = f"""
You are the Lead Writer for 'Bob Big Questions' - a high-retention animated YouTube cartoon for kids (7+ years old) and families.
Write an ultra-engaging, laugh-out-loud funny screenplay for the topic: '{topic}'.
Target Duration: Exactly {target_duration} seconds ({scene_count} scenes).

Rules for 7-year-old engagement:
1. Language: Ultra-simple words, highly energetic, funny sound words (SPLAT, BOOM, WHOOSH, CRACK!).
2. Characters: Bob (cyan hoodie, loves pancakes, innocent and curious) and his fluffy orange cat.
3. Fast Visual Beats: Each scene MUST have 3 to 5 micro visual cues describing what changes every 1.5 seconds.
4. Voice: Narrator Ava speaks naturally with comedic timing. Bob has occasional funny panicked lines.
5. Outro: Bob survives on his sofa eating pancakes; calls to like & subscribe.

Return PURE JSON strictly formatted as:
{{
  "title": "{title}",
  "target_duration": {target_duration},
  "thumb_line1": "{topic_info.get('thumb_line1', 'WHAT IF')}",
  "thumb_line2": "{topic_info.get('thumb_line2', 'HAPPENED FOR 24H?')}",
  "tags": ["bob big questions", "what if", "kids science", "animation", "fun facts", "cartoon"],
  "scenes": [
    {{
      "scene_num": 1,
      "banner": "SHORT IMPACT TITLE (ALL CAPS)",
      "narration": "Narrator voiceover text for this scene (around 20-30 words)...",
      "visual_beats": [
        "0.0s: Wide shot of Bob in kitchen eating cereal",
        "1.5s: Snappy zoom on Bob's eyes going wide",
        "3.0s: Graphic telemetry gauge pops up on screen"
      ]
    }}
  ]
}}
Ensure exactly {scene_count} scenes. Do NOT wrap in markdown fences.
"""
            resp = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=12
            )
            if resp.status_code == 200:
                raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("```")[1]
                    if raw_text.startswith("json"):
                        raw_text = raw_text[4:]
                data = json.loads(raw_text.strip())
                data["target_duration"] = target_duration
                return data
        except Exception as e:
            print(f"⚠️ Gemini screenplay fallback triggered: {e}")

    # Fallback Procedural Screenplay Generator
    scenes = []
    dur_per_scene = target_duration / scene_count
    for i in range(1, scene_count + 1):
        if i == 1:
            banner = f"STEP 01: THE {topic.split()[-1].upper()} EXPERIMENT!"
            narration = f"Meet Bob! Bob was having a completely normal morning enjoying breakfast, until he wondered: {topic}!"
        elif i == scene_count:
            banner = "SUBSCRIBE TO BOB BIG QUESTIONS!"
            narration = "Whew! Bob survived with only a squished pancake and a very dizzy cat! Hit like and subscribe so you never miss our next crazy adventure!"
        else:
            banner = f"STAGE {i:02d}: THE CHAOS ESCALATES!"
            narration = f"Suddenly, physics completely went wild! Objects started flying, alarms started beeping, and Bob screamed at the top of his lungs!"

        scenes.append({
            "scene_num": i,
            "banner": banner,
            "narration": narration,
            "visual_beats": [
                f"0.0s: Bob expression shift in Scene {i}",
                f"{dur_per_scene*0.3:.1f}s: Telemetry dial and camera zoom-in",
                f"{dur_per_scene*0.6:.1f}s: Particle burst and screen shake",
                f"{dur_per_scene*0.8:.1f}s: Cat reaction shot"
            ]
        })

    return {
        "title": title,
        "target_duration": target_duration,
        "thumb_line1": topic_info.get("thumb_line1", "WHAT IF THIS"),
        "thumb_line2": topic_info.get("thumb_line2", "HAPPENED TO EARTH?"),
        "tags": ["bob big questions", "what if", "science for kids", "physics cartoon", "animation"],
        "scenes": scenes
    }


if __name__ == "__main__":
    dummy = {
        "topic": "What If It Rained Diamonds?",
        "title": "What If It Rained Solid Diamonds? | Bob Big Questions",
        "thumb_line1": "WHAT IF IT RAINED",
        "thumb_line2": "SOLID DIAMONDS?"
    }
    s = generate_screenplay(dummy)
    print("Generated Screenplay Duration:", s["target_duration"], "s with", len(s["scenes"]), "scenes.")
