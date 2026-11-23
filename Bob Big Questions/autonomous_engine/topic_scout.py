#!/usr/bin/env python3
"""Autonomous Viral Topic Scout for Bob Big Questions.

Finds high-curiosity, child-friendly (7-year-old level) 'What-If' topics with
maximum viral potential, humor, and curiosity hooks.
"""

import os
import json
import random
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "autonomous_engine" / "topic_history.json"

# Evergreen high-curiosity viral topics (Kid & Family approved)
EVERGREEN_QUEUE = [
    {
        "topic": "What If You Drilled A Hole Straight Through Earth And Jumped In?",
        "title": "What If You Drilled Through The Center Of Earth? | Bob Big Questions",
        "thumb_line1": "WHAT IF YOU JUMPED",
        "thumb_line2": "THROUGH THE EARTH?",
        "hook": "Ever wondered what happens if you dig past your backyard, past the dinosaur bones, and jump straight into Earth's fiery glowing core?",
        "core_science": "Gravity pulling to center, terminal velocity of 18,000 mph, 42-minute trip, popping out upside down in the Indian Ocean."
    },
    {
        "topic": "What If It Rained Diamonds Instead Of Water?",
        "title": "What If It Rained Solid Diamonds? | Bob Big Questions",
        "thumb_line1": "WHAT IF IT RAINED",
        "thumb_line2": "SOLID DIAMONDS?",
        "hook": "Forget umbrellas! What happens if storm clouds overhead start dropping 24-carat sparkly diamond boulders at 100 miles per hour?",
        "core_science": "Atmospheric pressure on Neptune/Uranus crushing methane into diamond hail, Bob wearing a steel colander, jewelry prices crashing."
    },
    {
        "topic": "What If All The Animals On Earth Could Suddenly Talk?",
        "title": "What If Animals Could Talk? | Bob Big Questions",
        "thumb_line1": "WHAT IF ALL ANIMALS",
        "thumb_line2": "COULD ACTUALLY TALK?",
        "hook": "Bob thought his orange tabby cat was purring because he loved him... until the cat cleared his throat and demanded warm pancakes immediately!",
        "core_science": "Animal vocal cords, insect buzzing translations, dogs screaming 'BALL! BALL!', Bob getting roasted by squirrels."
    },
    {
        "topic": "What If The Moon Was Made Of Pure Gold?",
        "title": "What If The Moon Was Made Of Pure Gold? | Bob Big Questions",
        "thumb_line1": "WHAT IF THE MOON",
        "thumb_line2": "WAS MADE OF GOLD?",
        "hook": "Look up at the night sky! Instead of dusty grey rock, imagine a giant 2-trillion-ton shiny golden disco ball reflecting the Sun!",
        "core_science": "Gold density is 6 times heavier than lunar rock, massive tides pulling oceans onto land, daytime nights, space gold rush."
    },
    {
        "topic": "What If Humans Had Giant Bird Wings?",
        "title": "What If Humans Could Fly With Wings? | Bob Big Questions",
        "thumb_line1": "WHAT IF HUMANS",
        "thumb_line2": "HAD GIANT WINGS?",
        "hook": "No more school buses, no more traffic jams! What if you could flap two enormous feathered wings and soar right above the clouds?",
        "core_science": "Human chest muscle physics, needing 25-foot wingspan, aerial traffic jams, Bob dodging pigeons while eating a donut."
    },
    {
        "topic": "What If Earth Had Two Glowing Suns In The Sky?",
        "title": "What If Earth Had Two Suns? | Bob Big Questions",
        "thumb_line1": "WHAT IF EARTH HAD",
        "thumb_line2": "TWO SUNS IN THE SKY?",
        "hook": "Double sunrise, zero bedtime, and double the sunburn! What happens if our solar system gets a second giant blazing yellow sun?",
        "core_science": "Binary star orbits, never-ending daytime, crazy seasonal loops, Bob wearing double sunglasses and cooling his room with 50 fans."
    },
    {
        "topic": "What If We Built A Giant Elevator Straight To Space?",
        "title": "What If We Built An Elevator To Space? | Bob Big Questions",
        "thumb_line1": "WHAT IF WE BUILT AN",
        "thumb_line2": "ELEVATOR TO SPACE?",
        "hook": "Step in, press button 100,000, and enjoy smooth elevator music as you glide 62 miles straight up into zero gravity!",
        "core_science": "Carbon nanotube cable, geostationary orbit, floating candy in elevator cabin, Bob pressing all the buttons at once."
    },
    {
        "topic": "What If Everything You Touched Turned Into Chocolate?",
        "title": "What If Everything You Touched Turned To Chocolate? | Bob Big Questions",
        "thumb_line1": "WHAT IF EVERYTHING",
        "thumb_line2": "TURNED TO CHOCOLATE?",
        "hook": "It sounds like every kid's dream... until Bob tries to drink a glass of milk and his cup turns into creamy fudge that melts on his hands!",
        "core_science": "Molecular atomic conversion, King Midas paradox, melted chocolate shoes, chocolate Wi-Fi router refusing to work."
    },
    {
        "topic": "What If Earth Suddenly Lost Its Magnetic Field?",
        "title": "What If Earth Lost Its Magnetic Shield? | Bob Big Questions",
        "thumb_line1": "WHAT IF EARTH'S",
        "thumb_line2": "SHIELD DISAPPEARED?",
        "hook": "There is an invisible forcefield protecting your head right now from deadly cosmic laser radiation... what happens if it shuts down?",
        "core_science": "Solar wind stripping atmosphere, Northern Lights everywhere over daytime cities, Bob's compass spinning in circles."
    },
    {
        "topic": "What If Dinosaurs Never Went Extinct?",
        "title": "What If Dinosaurs Were Still Alive Today? | Bob Big Questions",
        "thumb_line1": "WHAT IF DINOSAURS",
        "thumb_line2": "WERE STILL ALIVE?",
        "hook": "Imagine walking to school and waiting at a crosswalk behind a 40-foot Brachiosaurus, while Bob tries to teach a baby Velociraptor how to fetch!",
        "core_science": "Chicxulub asteroid missing Earth, mammalian evolution, dinosaur pet parks, mega-sized doggy doors."
    }
]


def load_topic_history() -> list:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_topic_to_history(topic_data: dict):
    history = load_topic_history()
    history.append({
        "topic": topic_data["topic"],
        "title": topic_data["title"],
        "timestamp": os.environ.get("GITHUB_RUN_ID", "local")
    })
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def scout_viral_topic(gemini_api_key: str = None) -> dict:
    """Discovers the next high-potential viral topic via Gemini Flash or curated queue."""
    history = [h.get("topic", "").lower() for h in load_topic_history()]
    key = gemini_api_key or os.environ.get("GEMINI_API_KEY", "")

    # Try Gemini AI discovery first
    if key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={key}"
            prompt = (
                "You are the Creative Director for 'Bob Big Questions' - a mega-viral 2D animated cartoon channel "
                "for kids (7+ years old) and curious families, similar to Kurzgesagt and Meet Arnold.\n"
                "Generate ONE fresh, jaw-dropping 'What If' science topic that has extreme viral curiosity, "
                "is simple enough for a 7-year-old child to find hilarious, and features our lovable cartoon hero Bob.\n"
                "Return PURE JSON strictly formatted as:\n"
                "{\n"
                '  "topic": "What If...",\n'
                '  "title": "Viral YouTube Title | Bob Big Questions",\n'
                '  "thumb_line1": "LINE 1 (UP TO 20 CHARS, WHITE)",\n'
                '  "thumb_line2": "LINE 2 (UP TO 24 CHARS, YELLOW)",\n'
                '  "hook": "1-sentence hook for kids with humor",\n'
                '  "core_science": "Key scientific phenomena explained simply"\n'
                "}\n"
                "Do NOT wrap in markdown fences."
            )
            resp = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=10
            )
            if resp.status_code == 200:
                raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("```")[1]
                    if raw_text.startswith("json"):
                        raw_text = raw_text[4:]
                data = json.loads(raw_text.strip())
                if data["topic"].lower() not in history:
                    save_topic_to_history(data)
                    return data
        except Exception as e:
            print(f"⚠️ Gemini scout fallback triggered: {e}")

    # Fallback to Curated Evergreen Queue
    for item in EVERGREEN_QUEUE:
        if item["topic"].lower() not in history:
            save_topic_to_history(item)
            return item

    # If all used, pick random from evergreen
    item = random.choice(EVERGREEN_QUEUE)
    save_topic_to_history(item)
    return item


if __name__ == "__main__":
    t = scout_viral_topic()
    print("Selected Topic:", json.dumps(t, indent=2))
