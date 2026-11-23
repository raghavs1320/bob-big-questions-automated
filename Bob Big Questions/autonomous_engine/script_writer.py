#!/usr/bin/env python3
"""Autonomous Script & Screenplay Generator for Bob Big Questions.

Generates a hilarious, 7-year-old child-friendly screenplay with zero repetition,
distinct scene themes, and full story arcs featuring Bob and his cat.
"""

import os
import json
import random
import requests
from typing import Dict, Any

# Truly randomized dynamic duration: 1m 50s (110s) to 3m 05s (185s)
def pick_random_duration() -> float:
    base_sec = random.randint(115, 180)
    fraction = random.choice([0.0, 0.2, 0.4, 0.6, 0.8])
    return round(base_sec + fraction, 1)


def generate_screenplay(topic_info: Dict[str, Any], gemini_api_key: str = None) -> Dict[str, Any]:
    """Generates an engaging, high-humor screenplay for Bob with randomized duration."""
    target_duration = pick_random_duration()
    key = gemini_api_key or os.environ.get("GEMINI_API_KEY", "")

    # 6 to 8 scenes based on duration
    if target_duration < 130.0:
        scene_count = 6
    elif target_duration < 160.0:
        scene_count = 7
    else:
        scene_count = 8

    topic = topic_info["topic"]
    title = topic_info.get("title", f"{topic} | Bob Big Questions")

    # Try Gemini AI models (Prioritizing Gemini 3.5 Flash)
    if key:
        models = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]
        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
                prompt = f"""
You are the Lead Writer for 'Bob Big Questions' - a high-retention animated YouTube cartoon for kids (7+ years old) and families.
Write an ultra-engaging, laugh-out-loud funny screenplay for the topic: '{topic}'.
Target Duration: Exactly {target_duration} seconds ({scene_count} scenes).

Rules for 7-year-old engagement:
1. Language: Simple words, highly energetic, funny sound words (SPLAT, BOOM, WHOOSH, CRACK!).
2. Characters: Bob (cyan hoodie, loves pancakes, innocent and curious) and his fluffy orange tabby cat.
3. CRITICAL: Every single scene MUST have completely DIFFERENT, UNIQUE narration that advances the story! NEVER repeat lines or phrases across scenes!
4. Story Beats:
   - Scene 1: Morning breakfast surprise with Bob and his cereal/cat.
   - Scene 2: The initial shock / catalyst happens.
   - Scene 3: Citywide / global domino effect.
   - Scene 4: Extreme scientific phenomenon explained simply.
   - Scene 5: Peak comedic chaos & Bob panic.
   - Scene 6: The resolution / how physics snaps back.
   - Scene 7 (or last scene): Outro with Bob eating pancakes, cat purring, and call to subscribe!

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
      "sub_banner": "COMIC DETAIL OR SCIENTIFIC FACT",
      "narration": "Narrator voiceover text for this scene (around 25-35 words with unique story details)..."
    }}
  ]
}}
Ensure exactly {scene_count} scenes with 100% unique, non-repeating narration. Do NOT wrap in markdown fences.
"""
                resp = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=15
                )
                if resp.status_code == 200:
                    raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    # Clean markdown code blocks if any
                    if "```" in raw_text:
                        raw_text = raw_text.split("```")[1]
                        if raw_text.startswith("json"):
                            raw_text = raw_text[4:]
                    raw_text = raw_text.strip()
                    data = json.loads(raw_text)
                    # Verify each scene has unique narration
                    narrations = [s["narration"] for s in data["scenes"]]
                    if len(set(narrations)) == len(narrations) and len(data["scenes"]) >= 5:
                        data["target_duration"] = target_duration
                        return data
            except Exception as e:
                print(f"⚠️ Gemini model {model} attempt error: {e}")

    # Robust Handcrafted Story Fallback (ZERO repetition guarantee)
    scenes = [
        {
            "scene_num": 1,
            "banner": "MEET BOB & THE MORNING SURPRISE!",
            "sub_banner": "A COMPLETELY NORMAL TUESDAY MORNING",
            "narration": f"Meet Bob! Bob was having a completely peaceful morning enjoying a warm bowl of crunchy cereal, until he asked a question: {topic}!"
        },
        {
            "scene_num": 2,
            "banner": "STAGE 01: THE UNTHINKABLE HAPPENS!",
            "sub_banner": "INITIAL SCIENTIFIC CATALYST",
            "narration": "Suddenly, reality completely flipped upside down! Before Bob could even take a second spoonful, a strange cosmic sound echoed through the atmosphere!"
        },
        {
            "scene_num": 3,
            "banner": "STAGE 02: CITYWIDE PANDEMONIUM!",
            "sub_banner": "DOMINO EFFECT ACROSS THE GLOBE",
            "narration": "Outside Bob's window, the entire city went into utter confusion! Cars came to a screeching halt, pigeons stared in disbelief, and alarms started beeping everywhere!"
        },
        {
            "scene_num": 4,
            "banner": "STAGE 03: THE LAWS OF PHYSICS BREAK!",
            "sub_banner": "EXTREME SCIENTIFIC PHENOMENON",
            "narration": "Here is the mind-blowing science: the basic forces holding our daily world together suddenly took a vacation, leaving Bob clutching his head in pure shock!"
        },
        {
            "scene_num": 5,
            "banner": "STAGE 04: PEAK COMEDIC CHAOS!",
            "sub_banner": "BOB'S INFLATABLE SOFA TO THE RESCUE",
            "narration": "Objects were floating, unexpected surprises were dropping from the sky, and Bob's orange tabby cat looked completely offended by the entire situation!"
        },
        {
            "scene_num": 6,
            "banner": "STAGE 05: THE GRAND SNAP BACK!",
            "sub_banner": "EQUILIBRIUM RESTORED WITH A BANG",
            "narration": "With an enormous cosmic WHOOSH, reality snapped back into place! Gravity stabilized, the atmosphere normalized, and Bob bounced safely onto his yellow sofa!"
        },
        {
            "scene_num": 7,
            "banner": "SUBSCRIBE TO BOB BIG QUESTIONS!",
            "sub_banner": "FRESH PANCAKES & CAT PURRS",
            "narration": "Whew! Bob survived with only a squished blueberry pancake and a very dizzy cat! Hit like and subscribe so you never miss our next crazy adventure!"
        }
    ]

    # Trim or expand to scene_count
    final_scenes = scenes[:scene_count]
    if len(final_scenes) < scene_count:
        final_scenes.insert(-1, {
            "scene_num": len(final_scenes),
            "banner": "STAGE 06: THE SURVIVAL PROTOCOL!",
            "sub_banner": "HOW TO NAVIGATE PLANETARY DISASTERS",
            "narration": "Scientists worldwide scrambled to calculate the odds, while Bob wisely decided to stay indoors with a helmet and a giant spoon!"
        })

    # Renumber sequentially
    for idx, sc in enumerate(final_scenes, 1):
        sc["scene_num"] = idx

    return {
        "title": title,
        "target_duration": target_duration,
        "thumb_line1": topic_info.get("thumb_line1", "WHAT HAPPENS IF"),
        "thumb_line2": topic_info.get("thumb_line2", "THIS OCCURS?"),
        "tags": ["bob big questions", "what if", "kids science", "animation", "cartoon"],
        "scenes": final_scenes
    }


if __name__ == "__main__":
    dummy = {
        "topic": "What If All Animals On Earth Could Suddenly Talk?",
        "title": "What If Animals Could Talk? | Bob Big Questions",
        "thumb_line1": "WHAT IF ANIMALS",
        "thumb_line2": "COULD ACTUALLY TALK?"
    }
    s = generate_screenplay(dummy)
    print("Duration:", s["target_duration"], "with", len(s["scenes"]), "scenes.")
    for sc in s["scenes"]:
        print(f"Scene {sc['scene_num']}: {sc['banner']} -> {sc['narration']}")
