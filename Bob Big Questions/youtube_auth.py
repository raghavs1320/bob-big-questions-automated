#!/usr/bin/env python3
"""One-click YouTube Authentication script.

Usage:
    python youtube_auth.py [--force-reauth]
"""

import sys
import argparse
from pathlib import Path

# Add directory to path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from youtube_manager import authenticate_youtube, get_channel_info, print_channel_banner


def main():
    parser = argparse.ArgumentParser(description="Authorize YouTube Channel via OAuth 2.0")
    parser.add_argument(
        "--force-reauth",
        action="store_true",
        help="Ignore cached token.json and force a fresh browser login"
    )
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print("🔐 BOB BIG QUESTIONS — YOUTUBE OAUTH LOGIN SETUP")
    print("=" * 65)

    try:
        youtube = authenticate_youtube(force_reauth=args.force_reauth)
        channel_info = get_channel_info(youtube)

        if "error" in channel_info:
            print(f"⚠️ {channel_info['error']}")
        else:
            print_channel_banner(channel_info)
            print("🎉 Success! Your YouTube account is linked and ready.")
            print("You can now upload videos directly using:\n")
            print("  python youtube_upload.py --episode 1 --privacy private\n")

    except Exception as e:
        print(f"\n❌ Login Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
