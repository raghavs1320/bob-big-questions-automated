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
    },
    {
        "topic": "What If You Fell Into A Black Hole?",
        "title": "What Happens If You Fall Into A Black Hole? | Bob Big Questions",
        "thumb_line1": "WHAT HAPPENS INSIDE",
        "thumb_line2": "A BLACK HOLE?",
        "hook": "Bob dropped his keys near an event horizon... and what happens next stretches his body like warm mozzarella cheese!",
        "core_science": "Spaghettification, extreme gravitational tidal forces, time dilation, light trapped forever."
    },
    {
        "topic": "What If The Ocean Turned Into Fresh Soda?",
        "title": "What If All Oceans Turned Into Soda? | Bob Big Questions",
        "thumb_line1": "WHAT IF OCEANS",
        "thumb_line2": "TURNED TO SODA?",
        "hook": "Grab your giant straw! Imagine 352 quintillion gallons of fizzing cherry cola sloshing against beaches worldwide!",
        "core_science": "Carbonic acid dissolving coral reefs, marine life chaos, massive sticky sugar hurricanes."
    },
    {
        "topic": "What If Humans Never Needed To Sleep?",
        "title": "What If Humans Never Had To Sleep? | Bob Big Questions",
        "thumb_line1": "WHAT IF NOBODY",
        "thumb_line2": "NEEDED TO SLEEP?",
        "hook": "No bedtime, no alarm clocks, and 8 extra hours every single night! Sounds awesome until Bob's boss asks for a 24-hour shift!",
        "core_science": "Brain adenosine buildup, 33% more daytime consumption, midnight supermarkets, endless entertainment."
    },
    {
        "topic": "What If Plants Could Walk And Talk?",
        "title": "What If Trees Could Walk And Talk? | Bob Big Questions",
        "thumb_line1": "WHAT IF TREES",
        "thumb_line2": "STARTED WALKING?",
        "hook": "Bob woke up to water his houseplant, but the potted fern packed its bags and marched out the front door looking for better sunlight!",
        "core_science": "Plant neurobiology, phototropism, migratory forests crossing highways, squirrels getting evictions."
    },
    {
        "topic": "What If Volcanoes Erupted Ice Cream Instead Of Lava?",
        "title": "What If Volcanoes Erupted Ice Cream? | Bob Big Questions",
        "thumb_line1": "WHAT IF VOLCANOES",
        "thumb_line2": "ERUPTED ICE CREAM?",
        "hook": "Get a giant waffle cone! What if Mount Fuji erupted 10 million tons of soft-serve strawberry swirl onto the town below?",
        "core_science": "Cryovolcanism on Saturn's moons, thermal dynamics, melting sugar avalanches, brain freezes."
    },
    {
        "topic": "What If All Mosquitoes Disappeared Tomorrow?",
        "title": "What If All Mosquitoes Went Extinct? | Bob Big Questions",
        "thumb_line1": "WHAT IF MOSQUITOES",
        "thumb_line2": "WENT EXTINCT?",
        "hook": "Zero itchy red bites ever again! But wait... what happens to the frogs, bats, and flowers who rely on them?",
        "core_science": "Food web ecology, arctic tundra bird feeding, pollinating cocoa plants (no mosquitoes = no chocolate!)."
    },
    {
        "topic": "What If You Traveled At The Speed Of Light?",
        "title": "What If You Moved At Light Speed? | Bob Big Questions",
        "thumb_line1": "WHAT IF YOU MOVED AT",
        "thumb_line2": "THE SPEED OF LIGHT?",
        "hook": "7.5 trips around the entire Earth in a single blink of an eye! Bob puts on running sneakers and bends Einstein's universe!",
        "core_science": "Einstein's Special Relativity, infinite mass paradox, time stopping completely, Doppler color shifts."
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


def is_topic_too_similar(new_topic: str, past_topics: list) -> bool:
    """Returns True if the topic is too similar to any previously published topic."""
    new_lower = new_topic.lower()
    stop_words = {"what", "if", "the", "and", "a", "an", "for", "in", "of", "to", "you", "earth"}
    new_words = {w for w in new_lower.replace("?", "").replace(",", "").split() if w not in stop_words}

    for past in past_topics:
        past_lower = past.lower()
        if new_lower in past_lower or past_lower in new_lower:
            return True
        past_words = {w for w in past_lower.replace("?", "").replace(",", "").split() if w not in stop_words}
        overlap = new_words.intersection(past_words)
        # If 3 or more key content words match (e.g. "diamonds", "rained", "solid"), treat as duplicate
        if len(overlap) >= 3:
            return True
    return False


def scout_viral_topic(gemini_api_key: str = None) -> dict:
    """Discovers the next high-potential viral topic via Gemini Flash or curated queue."""
    history = [h.get("topic", "") for h in load_topic_history()]
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
                f"DO NOT repeat or closely match any of these previous topics: {json.dumps(history[-30:])}\n"
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
                if not is_topic_too_similar(data["topic"], history):
                    save_topic_to_history(data)
                    return data
        except Exception as e:
            print(f"⚠️ Gemini scout fallback triggered: {e}")

    # Fallback to Curated Evergreen Queue
    for item in EVERGREEN_QUEUE:
        if not is_topic_too_similar(item["topic"], history):
            save_topic_to_history(item)
            return item

    # If all used, pick random from evergreen
    item = random.choice(EVERGREEN_QUEUE)
    save_topic_to_history(item)
    return item


if __name__ == "__main__":
    t = scout_viral_topic()
    print("Selected Topic:", json.dumps(t, indent=2))
