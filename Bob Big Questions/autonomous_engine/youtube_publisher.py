#!/usr/bin/env python3
"""Autonomous YouTube Publisher for Bob Big Questions.

Supports both local runtime (using token.json) and GitHub Actions cloud runner
(using encrypted repository secrets YOUTUBE_TOKEN_JSON & CLIENT_SECRETS_JSON).
Publishes the video as PUBLIC with full SEO tags, chapters, and custom thumbnail.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
BASE_DIR = Path(__file__).resolve().parent.parent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_youtube_service():
    """Authenticates and returns the YouTube service client."""
    token_data = None
    client_secrets_data = None

    # 1. Check GitHub Actions Environment Secrets
    if "YOUTUBE_TOKEN_JSON" in os.environ and os.environ["YOUTUBE_TOKEN_JSON"].strip():
        try:
            token_data = json.loads(os.environ["YOUTUBE_TOKEN_JSON"])
        except Exception:
            pass

    # 2. Check Local Files
    local_token = BASE_DIR / "token.json"
    if not token_data and local_token.exists():
        with open(local_token, "r") as f:
            token_data = json.load(f)

    if not token_data:
        raise RuntimeError("❌ No YouTube token found in environment or local token.json!")

    creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        logging.info("Refreshing expired YouTube OAuth token...")
        creds.refresh(Request())
        # Update local file if available
        if local_token.exists():
            with open(local_token, "w") as f:
                f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def publish_to_youtube(video_path: Path, thumbnail_path: Path, metadata: Dict[str, Any], privacy: str = "public") -> Dict[str, Any]:
    """Uploads video, sets thumbnail, chapters, and publishes as Public."""
    youtube = get_youtube_service()

    title = metadata["title"]
    description = metadata["description"]
    tags = metadata.get("tags", ["bob big questions", "what if", "science cartoon", "animation"])
    category_id = metadata.get("category_id", "27")  # 27 = Education

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en"
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(str(video_path), chunksize=1024*1024*4, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    logging.info(f"📤 Uploading video to YouTube: '{title}'...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            logging.info(f"Upload Progress: {pct}%")

    video_id = response.get("id")
    watch_url = f"https://youtu.be/{video_id}"
    logging.info(f"✅ Video uploaded successfully! Video ID: {video_id} ({watch_url})")

    # Set custom thumbnail
    if thumbnail_path and thumbnail_path.exists():
        try:
            mimetype = "image/png" if thumbnail_path.suffix.lower() == ".png" else "image/jpeg"
            logging.info(f"🖼️ Setting custom thumbnail: {thumbnail_path.name}...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail_path), mimetype=mimetype)
            ).execute()
            logging.info("✅ Custom thumbnail applied successfully!")
        except Exception as e:
            logging.error(f"⚠️ Thumbnail upload warning: {e}")

    return {
        "video_id": video_id,
        "watch_url": watch_url,
        "studio_url": f"https://studio.youtube.com/video/{video_id}/edit",
        "title": title
    }
