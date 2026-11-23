"""Central configuration and path management for Daily Dose Studio."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env file if it exists
load_dotenv()

# Project Root Directory
BASE_DIR = Path(__file__).resolve().parent

# Media Storage Directories
STORAGE_DIR = BASE_DIR / "storage"
DOWNLOADS_DIR = STORAGE_DIR / "downloads"
CACHE_DIR = STORAGE_DIR / "cache"
TEMP_DIR = STORAGE_DIR / "temp"
EXPORTS_DIR = STORAGE_DIR / "exports"

# Ensure all media storage folders exist automatically
for folder in [STORAGE_DIR, DOWNLOADS_DIR, CACHE_DIR, TEMP_DIR, EXPORTS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


class Settings:
    """Application settings and API keys."""

    # 1. AI Vision & Brain
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # 2. Voice & Narrator Settings
    # Microsoft Neural Voice: Ava/Nicole is warm, conversational, and natural
    NARRATOR_VOICE: str = os.getenv("NARRATOR_VOICE", "en-US-AvaNeural")
    VOICE_RATE: str = "+0%"  # Normal natural speaking speed

    # 3. Video Composition & Style Constants
    HOST_NAME: str = "Alex"
    INTRO_TEXT: str = "Hey everyone, I'm Alex. Welcome back to some of the craziest clips on the internet."
    OUTRO_TEXT: str = "Thank you so much for watching! I'm Alex, and I'll see you in the next one. Bye!"

    # Comedic Timing & Audio Defaults
    DEFAULT_ASPECT_RATIO: str = os.getenv("DEFAULT_ASPECT_RATIO", "16:9")
    PUNCHLINE_ZOOM_FACTOR: float = 1.15  # 15% smooth zoom on funny moments
    AUDIO_DUCK_LEVEL: float = 0.15      # Lowers video audio to 15% during voiceover
    NORMAL_AUDIO_LEVEL: float = 1.0     # 100% volume for punchlines

    # Clip Constraints
    MIN_CLIP_DURATION_SEC: float = 4.0
    MAX_CLIP_DURATION_SEC: float = 30.0
    TARGET_CLIPS_DEFAULT: int = 10

    # 4. Optional Phone Notification
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")


settings = Settings()

