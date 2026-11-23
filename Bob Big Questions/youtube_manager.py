"""YouTube API Authentication, Channel Management, and Video Uploader for Bob Big Questions."""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("YouTubeManager")

# OAuth 2.0 Scopes required for video uploads and channel management
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent

# Preset Catalog of Produced Episodes
EPISODES_CATALOG = {
    1: {
        "title": "What Happens If You Don't Sleep For 7 Days? | Bob Big Questions",
        "video_file": BASE_DIR / "exports" / "videos" / "What_Happens_If_You_Dont_Sleep_7_Days.mp4",
        "thumbnail_file": BASE_DIR / "exports" / "thumbnails" / "Cartoon_Sleep_Thumbnail.jpg",
        "category_id": "27",  # Education
        "tags": [
            "what if", "sleep deprivation", "what happens if you dont sleep",
            "bob big questions", "animation", "science animation", "fun science",
            "educational cartoon", "biology", "human body"
        ],
        "description": (
            "What really happens to the human body and brain if you try to stay awake for 7 whole days?\n"
            "Join Bob on an absurd scientific journey from 24 hours of fake superhero energy to Day 7 hallucinations!\n\n"
            "⏱️ Chapters:\n"
            "0:00 - The 24-Hour Dopamine Rush\n"
            "0:15 - Day 2: Brain Lag & The Banana Toothbrush\n"
            "0:30 - Day 3 to 5: Hallucinations & The Donut\n"
            "0:45 - Day 7: Total Shutdown & The 16-Hour Sleep\n\n"
            "🔔 Subscribe to Bob Big Questions for curious science and absurd what-if cartoons!\n"
            "#BobBigQuestions #WhatIf #Science #Animation #Sleep"
        )
    },
    2: {
        "title": "What If The Sun Disappeared For 7 Days? | Bob Big Questions",
        "video_file": BASE_DIR / "exports" / "videos" / "What_If_The_Sun_Disappeared_2Min.mp4",
        "thumbnail_file": BASE_DIR / "exports" / "thumbnails" / "Sun_Disappeared_Thumbnail.jpg",
        "category_id": "27",
        "tags": [
            "what if the sun disappeared", "sun vanishes", "solar system",
            "bob big questions", "astronomy", "physics", "earth science",
            "space facts", "animation", "what if"
        ],
        "description": (
            "What if our Sun vanished into thin air for 7 full days? How long before Earth freezes?\n"
            "Follow Bob as gravity lets go, global temperatures plummet to -100°F, and Earth drifts through frozen darkness!\n\n"
            "⏱️ Chapters:\n"
            "0:00 - Minute 8: The Lights Go Out\n"
            "0:30 - Day 1: Global Panic & Flashlights\n"
            "1:00 - Day 3: Oceans Freeze & Power Grid Fails\n"
            "1:30 - Day 7: The Cosmic Thaw or Eternal Winter?\n\n"
            "🔔 Subscribe to Bob Big Questions for more wild cosmic science!\n"
            "#BobBigQuestions #WhatIf #SunDisappeared #Space #Astronomy"
        )
    },
    3: {
        "title": "What If Gravity Disappeared For 60 Seconds? | Bob Big Questions",
        "video_file": BASE_DIR / "exports" / "videos" / "What_If_Gravity_Disappeared_2m30s.mp4",
        "thumbnail_file": BASE_DIR / "exports" / "thumbnails" / "Gravity_Disappeared_Thumbnail.jpg",
        "category_id": "27",
        "tags": [
            "what if gravity disappeared", "zero gravity", "physics",
            "bob big questions", "earth science", "science experiment",
            "cartoon animation", "what if", "gravity"
        ],
        "description": (
            "What if gravity suddenly turned OFF for exactly 60 seconds?\n"
            "Watch Bob, his breakfast pancakes, and trillions of gallons of ocean water float into the stratosphere—and brace for the crash when gravity snaps back!\n\n"
            "⏱️ Chapters:\n"
            "0:00 - Second 0: The Floating Breakfast\n"
            "0:40 - Second 20: Cars and Oceans in the Sky\n"
            "1:20 - Second 59: The Final Countdown\n"
            "1:45 - The SNAP-BACK Impact!\n\n"
            "🔔 Subscribe to Bob Big Questions for hilarious animated physics!\n"
            "#BobBigQuestions #Gravity #WhatIf #Physics #Animation"
        )
    },
    4: {
        "title": "What If Earth Stopped Spinning For 5 Seconds? | Bob Big Questions",
        "video_file": BASE_DIR / "exports" / "videos" / "What_If_Earth_Stopped_Spinning_5s.mp4",
        "thumbnail_file": BASE_DIR / "exports" / "thumbnails" / "Earth_Stopped_Spinning_Thumbnail.jpg",
        "category_id": "27",
        "tags": [
            "what if earth stopped spinning", "earth rotation", "physics",
            "bob big questions", "supersonic winds", "geology",
            "science cartoon", "animation", "what if"
        ],
        "description": (
            "The Earth rotates at over 1,000 mph. What happens if it slams on the cosmic brakes for just 5 seconds?\n"
            "Bob finds out the hard way as everything not bolted down launches at supersonic speed across the planet!\n\n"
            "⏱️ Chapters:\n"
            "0:00 - 1,000 MPH Inertia Shockwave\n"
            "0:30 - Supersonic Winds & Megatsunamis\n"
            "1:00 - 5 Seconds Later: The Spin Resumes\n"
            "1:25 - How Bob Survived on His Inflatable Sofa\n\n"
            "🔔 Subscribe to Bob Big Questions for mind-bending planetary science!\n"
            "#BobBigQuestions #Earth #WhatIf #Science #Animation"
        )
    },
    5: {
        "title": "What If Everyone Jumped At The Same Time? | Bob Big Questions",
        "video_file": BASE_DIR / "exports" / "videos" / "What_If_Everyone_Jumped_2m15s.mp4",
        "thumbnail_file": BASE_DIR / "exports" / "thumbnails" / "Everyone_Jumped_2m15s_Thumbnail.jpg",
        "category_id": "27",
        "tags": [
            "what if everyone jumped", "everyone jumps at once", "earthquake",
            "bob big questions", "physics calculation", "curious science",
            "fun facts", "animation", "what if"
        ],
        "description": (
            "What if all 8 billion humans on Earth gathered in one place and jumped at the exact same second?\n"
            "Could we knock Earth out of orbit, or cause a magnitude 8 earthquake? Bob and 8 billion friends put it to the test!\n\n"
            "⏱️ Chapters:\n"
            "0:00 - Gathering 8 Billion People (Rhode Island Rule)\n"
            "0:35 - The Countdown: 3, 2, 1... JUMP!\n"
            "1:10 - The Impact Energy Calculation\n"
            "1:45 - Did the Earth Move? The Surprising Truth\n\n"
            "🔔 Subscribe to Bob Big Questions for epic science experiments!\n"
            "#BobBigQuestions #Physics #EveryoneJumped #Science #Animation"
        )
    },
    6: {
        "title": "What If All Oceans Dried Up For 24 Hours? | Bob Big Questions",
        "video_file": BASE_DIR / "exports" / "videos" / "What_If_Oceans_Dried_Up_2m17s.mp4",
        "thumbnail_file": BASE_DIR / "exports" / "thumbnails" / "Ocean_Dried_Up_Thumbnail.jpg",
        "category_id": "27",
        "tags": [
            "what if all oceans dried up", "oceans disappear", "ocean science",
            "bob big questions", "earth science", "tsunami", "marine biology",
            "what if", "animation", "science cartoon"
        ],
        "description": (
            "What if all 350 quintillion gallons of ocean water suddenly vanished for 24 hours?\n"
            "Watch Bob explore the 12,000-foot deep oceanic abyssal plain, survive a 125°F planetary heatwave, and ride the greatest 2,000-foot returning tsunami in history!\n\n"
            "⏱️ Chapters:\n"
            "0:00 - The 350 Quintillion Gallon Drain\n"
            "0:18 - Lost Pirate Galleons & Deep Sea Secrets\n"
            "0:37 - Oxygen Depletion & 125°F Heatwave\n"
            "1:00 - Operation Save The Whale & Cat Sushi Feast\n"
            "1:18 - Martian Dust Storms & Broken Water Cycle\n"
            "1:38 - The 24-Hour Return Countdown\n"
            "1:58 - The 2,000-Foot Tsunami Surf Back Home!\n\n"
            "🔔 Subscribe to Bob Big Questions for curious science and absurd what-if cartoons!\n"
            "#BobBigQuestions #WhatIf #Ocean #EarthScience #Animation #Science"
        )
    },
    7: {
        "title": "What If Time Stopped For 24 Hours? (Except For You) | Bob Big Questions",
        "video_file": BASE_DIR / "exports" / "videos" / "What_If_Time_Stopped_3m45s.mp4",
        "thumbnail_file": BASE_DIR / "exports" / "thumbnails" / "Time_Stopped_Thumbnail.jpg",
        "category_id": "27",
        "tags": [
            "what if time stopped", "time freeze", "what if time froze for 24 hours",
            "bob big questions", "physics", "time travel", "relativity",
            "science animation", "what if", "educational cartoon"
        ],
        "description": (
            "What really happens if time freezes for 24 hours for everyone on Earth except YOU?\n"
            "Join Bob on a mind-bending 3-minute 45-second adventure dodging 40,000 suspended raindrops, sliding across rock-solid ocean waves, wading through thick air jelly, and surviving the explosive sonic boom when the clock snaps back!\n\n"
            "⏱️ Chapters:\n"
            "0:00 - The 7:00 AM Alarm Freeze\n"
            "0:14 - The Frozen City Wax Museum\n"
            "0:28 - The 40,000 Suspended Raindrops\n"
            "0:42 - The Terrifying Physics of Light\n"
            "0:56 - Walking On Solid Ocean Waves\n"
            "1:10 - The Supermarket Mega-Feast\n"
            "1:24 - Pranking Historical Statues\n"
            "1:38 - The Stadium Frozen Mid-Goal\n"
            "1:52 - The Air Jelly Paradox\n"
            "2:06 - Absolute Zero Deep Freeze\n"
            "2:20 - The Frozen Tabby Cat Surprise\n"
            "2:34 - Hour 18: Silence & Dead Wi-Fi\n"
            "2:48 - Hour 23: The Cosmic Vibration\n"
            "3:02 - The 10-Second Countdown\n"
            "3:16 - SNAP! The Grand Sonic Boom Release\n"
            "3:30 - Pancakes & The Next Question\n\n"
            "🔔 Subscribe to Bob Big Questions for curious science and absurd what-if cartoons!\n"
            "#BobBigQuestions #WhatIf #TimeFreeze #Physics #Science #Animation"
        )
    },
    8: {
        "title": "What If Earth Lost Oxygen For Just 5 Seconds? | Bob Big Questions",
        "video_file": BASE_DIR / "exports" / "videos" / "What_If_Earth_Lost_Oxygen_2m30s.mp4",
        "thumbnail_file": BASE_DIR / "exports" / "thumbnails" / "Oxygen_Lost_Thumbnail.jpg",
        "category_id": "27",
        "tags": [
            "what if earth lost oxygen", "oxygen vanishes", "earth science",
            "what if", "bob big questions", "physics", "science cartoon",
            "animation", "what if for 5 seconds", "chemistry"
        ],
        "description": (
            "What if all oxygen disappeared from Earth for just 5 seconds? You can hold your breath, but Earth can't!\n"
            "Watch Bob experience what happens when concrete buildings crumble into dust, daytime turns pitch black, untreated metals cold-weld, and 46% of Earth's solid crust vanishes beneath our feet!\n\n"
            "⏱️ Chapters:\n"
            "0:00 - Second 00: The 5-Second Breath Challenge\n"
            "0:18 - Second 01: Concrete Crumbles to Powder\n"
            "0:38 - Second 02: Daytime Sky Turns Pitch Black\n"
            "0:56 - Second 03: 21% Air Pressure Drop & Ears Pop\n"
            "1:14 - Second 04: Instant Metal Cold Welding\n"
            "1:32 - Second 05: 46% of Earth's Crust Vanishes\n"
            "1:52 - Second 06: SNAP! The Planetary Thunderclap\n"
            "2:12 - Safe in Bed & Pancake Victory\n\n"
            "🔔 Subscribe to Bob Big Questions for curious science and absurd what-if cartoons!\n"
            "#BobBigQuestions #WhatIf #Oxygen #EarthScience #Animation #Science"
        )
    }
}


def find_client_secrets_file() -> Optional[Path]:
    """Search for the OAuth client_secrets JSON file in local, parent, and Downloads folders."""
    candidates = [
        BASE_DIR / "client_secrets.json",
        PARENT_DIR / "client_secrets.json",
        Path.home() / "Downloads" / "client_secret_147565475363-pl2a2317ivn77ce66pdr4427806975pk.apps.googleusercontent.com.json",
    ]
    for p in candidates:
        if p.exists():
            return p
            
    # Glob search in project directories
    for match in list(BASE_DIR.glob("client_secret*.json")) + list(PARENT_DIR.glob("client_secret*.json")):
        return match

    # Search in user Downloads
    downloads = Path.home() / "Downloads"
    for match in downloads.glob("client_secret*.json"):
        try:
            with open(match, "r") as f:
                data = json.load(f)
                if "installed" in data:
                    return match
        except Exception:
            continue

    return None


def get_token_file() -> Path:
    """Return the path to the persistent OAuth token file."""
    # Check if exists in parent
    if (PARENT_DIR / "token.json").exists():
        return PARENT_DIR / "token.json"
    return BASE_DIR / "token.json"


def authenticate_youtube(force_reauth: bool = False):
    """Authenticate and return an authorized YouTube Data API v3 service."""
    token_path = get_token_file()
    creds = None

    if token_path.exists() and not force_reauth:
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            logger.info(f"Loaded existing credentials from: {token_path}")
        except Exception as e:
            logger.warning(f"Failed to load token file: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired OAuth token...")
            try:
                creds.refresh(Request())
                with open(token_path, "w") as token_file:
                    token_file.write(creds.to_json())
                logger.info(f"Token refreshed and saved to: {token_path}")
            except Exception as e:
                logger.warning(f"Token refresh failed ({e}), initiating fresh browser login...")
                creds = None

        if not creds:
            secrets_file = find_client_secrets_file()
            if not secrets_file or not secrets_file.exists():
                raise FileNotFoundError(
                    "❌ No OAuth client_secrets.json file found!\n"
                    "Please download your OAuth 2.0 Client credentials (Desktop Application) from:\n"
                    "https://console.cloud.google.com/apis/credentials\n"
                    f"and place it in: {BASE_DIR / 'client_secrets.json'}"
                )

            logger.info(f"Using client secrets from: {secrets_file}")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(secrets_file),
                scopes=SCOPES
            )
            print("\n" + "=" * 70)
            print("🚀 OPENING YOUR BROWSER FOR 1-CLICK YOUTUBE AUTHORIZATION...")
            print("Please log in with the Google Account that owns your YouTube channel.")
            print("=" * 70 + "\n")

            try:
                creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")
            except OSError:
                logger.info("Port 8080 in use, selecting random available port...")
                creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())
            logger.info(f"✅ Authorization successful! Saved persistent token to: {token_path}")

    return build("youtube", "v3", credentials=creds)


def get_channel_info(youtube=None) -> Dict[str, Any]:
    """Retrieve details of the authenticated YouTube channel."""
    if youtube is None:
        youtube = authenticate_youtube()

    response = youtube.channels().list(
        mine=True,
        part="snippet,contentDetails,statistics"
    ).execute()

    items = response.get("items", [])
    if not items:
        return {"error": "No YouTube channel found for the authenticated account."}

    channel = items[0]
    snippet = channel.get("snippet", {})
    stats = channel.get("statistics", {})

    info = {
        "channel_id": channel.get("id"),
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "custom_url": snippet.get("customUrl", ""),
        "subscribers": stats.get("subscriberCount", "0"),
        "videos": stats.get("videoCount", "0"),
        "views": stats.get("viewCount", "0"),
        "country": snippet.get("country", "N/A"),
    }
    return info


def print_channel_banner(info: Dict[str, Any]):
    """Print an attractive summary of the connected YouTube channel."""
    print("\n" + "=" * 65)
    print("📺 CONNECTED YOUTUBE CHANNEL")
    print("=" * 65)
    print(f" • Channel Name : {info.get('title')}")
    print(f" • Handle / URL : {info.get('custom_url') or 'https://youtube.com/channel/' + info.get('channel_id', '')}")
    print(f" • Channel ID   : {info.get('channel_id')}")
    print(f" • Subscribers  : {int(info.get('subscribers', 0)):,}")
    print(f" • Total Videos : {int(info.get('videos', 0)):,}")
    print(f" • Total Views  : {int(info.get('views', 0)):,}")
    print("=" * 65 + "\n")


def upload_video(
    video_path: Path,
    title: str,
    description: str,
    tags: List[str],
    category_id: str = "27",
    privacy_status: str = "private",
    thumbnail_path: Optional[Path] = None,
    youtube=None
) -> Dict[str, Any]:
    """Upload a video to YouTube with resumable chunks and upload matching thumbnail."""
    if not Path(video_path).exists():
        raise FileNotFoundError(f"Video file not found at: {video_path}")

    if youtube is None:
        youtube = authenticate_youtube()

    video_path = Path(video_path)
    file_size_mb = video_path.stat().st_size / (1024 * 1024)

    logger.info(f"Preparing upload: {video_path.name} ({file_size_mb:.1f} MB)")
    logger.info(f"Title: {title}")
    logger.info(f"Privacy: {privacy_status}")

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],
            "categoryId": str(category_id),
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en"
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    # Use 4MB chunk size for reliable resumable upload
    chunk_size = 4 * 1024 * 1024
    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        chunksize=chunk_size,
        resumable=True
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    print(f"\n📤 Uploading '{video_path.name}' to YouTube...")
    response = None
    last_reported_pct = -1

    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            if pct // 10 != last_reported_pct:
                last_reported_pct = pct // 10
                sys.stdout.write(f"\r progress: {pct}% uploaded...")
                sys.stdout.flush()

    sys.stdout.write("\r progress: 100% uploaded! Finalizing on YouTube...\n")
    sys.stdout.flush()

    video_id = response.get("id")
    watch_url = f"https://youtu.be/{video_id}"
    studio_url = f"https://studio.youtube.com/video/{video_id}/edit"

    logger.info(f"✅ Video successfully uploaded! Video ID: {video_id}")
    logger.info(f"Watch URL: {watch_url}")
    logger.info(f"Studio Editor: {studio_url}")

    # Upload custom thumbnail if supplied
    thumbnail_uploaded = False
    if thumbnail_path and Path(thumbnail_path).exists():
        thumb_path = Path(thumbnail_path)
        logger.info(f"Uploading custom thumbnail: {thumb_path.name}...")
        try:
            mimetype = "image/png" if thumb_path.suffix.lower() == ".png" else "image/jpeg"
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumb_path), mimetype=mimetype)
            ).execute()
            thumbnail_uploaded = True
            logger.info("✅ Custom thumbnail uploaded successfully!")
        except Exception as e:
            logger.warning(f"Could not upload custom thumbnail: {e}")
            logger.info("Note: Custom thumbnails require a phone-verified YouTube channel.")

    return {
        "video_id": video_id,
        "watch_url": watch_url,
        "studio_url": studio_url,
        "title": title,
        "privacy": privacy_status,
        "thumbnail_uploaded": thumbnail_uploaded
    }


def list_recent_videos(max_results: int = 5, youtube=None) -> List[Dict[str, Any]]:
    """List recently uploaded videos for the channel."""
    if youtube is None:
        youtube = authenticate_youtube()

    # Get uploads playlist ID
    channels_resp = youtube.channels().list(mine=True, part="contentDetails").execute()
    items = channels_resp.get("items", [])
    if not items:
        return []

    uploads_playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    playlist_items = youtube.playlistItems().list(
        playlistId=uploads_playlist_id,
        part="snippet,status",
        maxResults=max_results
    ).execute()

    videos = []
    for item in playlist_items.get("items", []):
        snippet = item.get("snippet", {})
        vid_id = snippet.get("resourceId", {}).get("videoId")
        videos.append({
            "video_id": vid_id,
            "title": snippet.get("title"),
            "published_at": snippet.get("publishedAt"),
            "url": f"https://youtu.be/{vid_id}"
        })
    return videos
