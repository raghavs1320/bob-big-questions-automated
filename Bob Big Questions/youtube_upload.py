#!/usr/bin/env python3
"""YouTube Video Uploader CLI for Bob Big Questions.

Usage Examples:
    # Check connected YouTube channel:
    python youtube_upload.py --channel

    # List latest uploaded videos:
    python youtube_upload.py --list

    # Upload an episode preset (defaults to 'private' so you can review):
    python youtube_upload.py --episode 1
    python youtube_upload.py --episode 2 --privacy unlisted
    python youtube_upload.py --episode 3 --privacy public

    # Upload any custom video file:
    python youtube_upload.py --file "path/to/video.mp4" --title "My Title" --thumb "path/to/thumb.jpg"
"""

import sys
import argparse
from pathlib import Path

# Add directory to path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from youtube_manager import (
    authenticate_youtube,
    get_channel_info,
    print_channel_banner,
    upload_video,
    list_recent_videos,
    EPISODES_CATALOG,
    MediaFileUpload,
)


def main():
    parser = argparse.ArgumentParser(description="Upload videos to YouTube automatically")
    parser.add_argument("--channel", action="store_true", help="Display connected channel details")
    parser.add_argument("--list", action="store_true", help="List recent uploads on the channel")
    parser.add_argument(
        "--episode",
        type=int,
        choices=list(EPISODES_CATALOG.keys()),
        help=f"Upload a preset episode (1 to {len(EPISODES_CATALOG)})"
    )
    parser.add_argument(
        "--privacy",
        choices=["private", "unlisted", "public"],
        default="private",
        help="Upload privacy status (default: private)"
    )
    parser.add_argument("--file", type=str, help="Custom video file path")
    parser.add_argument("--title", type=str, help="Custom video title")
    parser.add_argument("--desc", type=str, default="", help="Custom video description")
    parser.add_argument("--tags", type=str, default="", help="Comma-separated tags")
    parser.add_argument("--thumb", type=str, help="Path to custom thumbnail")
    parser.add_argument("--category", type=str, default="27", help="YouTube Category ID (default: 27 Education)")
    parser.add_argument("--set-thumb", type=str, help="Video ID to update thumbnail for (use with --thumb)")

    args = parser.parse_args()

    # Authenticate service
    youtube = authenticate_youtube()

    # 1. Channel Info
    if args.channel:
        info = get_channel_info(youtube)
        print_channel_banner(info)
        return

    # Update thumbnail for existing video
    if args.set_thumb:
        if not args.thumb or not Path(args.thumb).exists():
            print("❌ Error: Please provide a valid thumbnail path with --thumb")
            return
        mimetype = "image/png" if Path(args.thumb).suffix.lower() == ".png" else "image/jpeg"
        print(f"🖼️ Updating custom thumbnail for video {args.set_thumb}...")
        youtube.thumbnails().set(
            videoId=args.set_thumb,
            media_body=MediaFileUpload(str(args.thumb), mimetype=mimetype)
        ).execute()
        print("✅ Custom thumbnail updated successfully!")
        return

    # 2. List Recent Uploads
    if args.list:
        print("\n" + "=" * 65)
        print("📋 RECENT UPLOADS ON CHANNEL")
        print("=" * 65)
        videos = list_recent_videos(max_results=8, youtube=youtube)
        if not videos:
            print("No recent uploads found on this channel.")
        else:
            for idx, v in enumerate(videos, 1):
                print(f"{idx}. {v['title']}")
                print(f"   Published: {v['published_at']} | Link: {v['url']}")
        print("=" * 65 + "\n")
        return

    # 3. Episode Preset Upload
    if args.episode:
        ep = EPISODES_CATALOG[args.episode]
        print("\n" + "=" * 65)
        print(f"🎬 UPLOADING PRESET EPISODE {args.episode}")
        print("=" * 65)
        print(f" • Title    : {ep['title']}")
        print(f" • Video    : {ep['video_file']}")
        print(f" • Thumbnail: {ep['thumbnail_file']}")
        print(f" • Privacy  : {args.privacy.upper()}")
        print("=" * 65)

        result = upload_video(
            video_path=ep["video_file"],
            title=ep["title"],
            description=ep["description"],
            tags=ep["tags"],
            category_id=ep["category_id"],
            privacy_status=args.privacy,
            thumbnail_path=ep["thumbnail_file"],
            youtube=youtube
        )

        print("\n" + "=" * 65)
        print("🚀 UPLOAD COMPLETE!")
        print("=" * 65)
        print(f" • Video ID  : {result['video_id']}")
        print(f" • Watch URL : {result['watch_url']}")
        print(f" • Studio URL: {result['studio_url']}")
        print(f" • Privacy   : {result['privacy'].upper()}")
        print("=" * 65 + "\n")
        return

    # 4. Custom File Upload
    if args.file:
        video_file = Path(args.file)
        if not video_file.exists():
            print(f"❌ Error: Video file not found: {video_file}")
            sys.exit(1)

        title = args.title or video_file.stem.replace("_", " ").title()
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else ["bob big questions", "what if"]
        thumb_path = Path(args.thumb) if args.thumb else None

        result = upload_video(
            video_path=video_file,
            title=title,
            description=args.desc or f"{title}\n\nUploaded via Bob Big Questions Automated Studio.",
            tags=tags,
            category_id=args.category,
            privacy_status=args.privacy,
            thumbnail_path=thumb_path,
            youtube=youtube
        )

        print("\n" + "=" * 65)
        print("🚀 UPLOAD COMPLETE!")
        print("=" * 65)
        print(f" • Video ID  : {result['video_id']}")
        print(f" • Watch URL : {result['watch_url']}")
        print(f" • Studio URL: {result['studio_url']}")
        print("=" * 65 + "\n")
        return

    # No arguments provided
    parser.print_help()


if __name__ == "__main__":
    main()
