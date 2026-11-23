"""Telegram bot integration for mobile preview delivery and 30-second approval."""

import json
from pathlib import Path
from typing import Dict, List, Optional
import requests
from config import CACHE_DIR, settings
from utils.logger import logger

APPROVALS_FILE = CACHE_DIR / "pending_approvals.json"


def get_pending_approvals() -> List[Dict]:
    """Returns list of videos waiting for human review."""
    if not APPROVALS_FILE.exists():
        return []
    try:
        with open(APPROVALS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def record_pending_approval(job_id: str, video_path: str, caption: str) -> None:
    """Saves pending approval to local disk."""
    items = get_pending_approvals()
    items.append({
        "job_id": job_id,
        "video_path": str(video_path),
        "caption": caption,
        "status": "pending",
    })
    APPROVALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(APPROVALS_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def send_telegram_preview(
    video_path: str,
    caption: str,
    job_id: str,
) -> bool:
    """Sends a 30-second video preview and approval buttons to the user's phone via Telegram."""
    bot_token = settings.TELEGRAM_BOT_TOKEN.strip()
    chat_id = settings.TELEGRAM_CHAT_ID.strip()

    # Record to local approval queue regardless
    record_pending_approval(job_id, video_path, caption)

    if not bot_token or not chat_id:
        logger.info("Telegram bot not configured. Video recorded to local approval dashboard.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve & Publish", "callback_data": f"approve_{job_id}"},
                {"text": "🔄 Swap Clip", "callback_data": f"swap_{job_id}"},
            ]
        ]
    }

    try:
        with open(video_path, "rb") as video_file:
            files = {"video": video_file}
            data = {
                "chat_id": chat_id,
                "caption": caption,
                "reply_markup": json.dumps(reply_markup),
            }
            res = requests.post(url, data=data, files=files, timeout=30)
            if res.status_code == 200:
                logger.success(f"30-second preview sent to your phone via Telegram for job: {job_id}")
                return True
            else:
                logger.warn(f"Telegram API returned code {res.status_code}: {res.text}")
                return False
    except Exception as e:
        logger.warn(f"Failed to send Telegram message: {e}")
        return False

