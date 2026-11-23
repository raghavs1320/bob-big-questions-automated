"""Self-contained configuration for Bob Big Questions production pipeline."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load credentials from local .env if present, otherwise from parent .env
BASE_DIR = Path(__file__).resolve().parent
local_env = BASE_DIR / ".env"
parent_env = BASE_DIR.parent / ".env"

if local_env.exists():
    load_dotenv(local_env)
elif parent_env.exists():
    load_dotenv(parent_env)

# Directories
EXPORTS_DIR = BASE_DIR / "exports" / "videos"
THUMBNAILS_DIR = BASE_DIR / "exports" / "thumbnails"
AUDIO_DIR = BASE_DIR / "audio"
TEMP_DIR = AUDIO_DIR

EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Credentials & Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-3.5-flash-lite")
NARRATOR_VOICE = os.getenv("NARRATOR_VOICE", "en-US-AvaNeural")
NARRATOR_RATE = os.getenv("NARRATOR_RATE", "+2%")
AUDIO_LUFS = int(os.getenv("AUDIO_LUFS", "-14"))
MUSIC_DUCKING_VOLUME = float(os.getenv("MUSIC_DUCKING_VOLUME", "0.30"))
VIDEO_ENCODER = os.getenv("VIDEO_ENCODER", "h264_videotoolbox")
