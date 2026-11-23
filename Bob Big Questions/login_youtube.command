#!/bin/bash
# ==============================================================================
# 1-CLICK YOUTUBE CHANNEL LOGIN & AUTHORIZATION
# Double-click this file in macOS Finder or run from terminal to link your channel.
# ==============================================================================

cd "$(dirname "$0")"

echo ""
echo "================================================================="
echo "  🎬 BOB BIG QUESTIONS — YOUTUBE CHANNEL AUTHORIZATION"
echo "================================================================="
echo " Opening your browser to log in with your YouTube channel account..."
echo "================================================================="
echo ""

if [ -f "./.venv/bin/python3" ]; then
    ./.venv/bin/python3 youtube_auth.py
elif [ -f "./Bob Big Questions/youtube_auth.py" ]; then
    python3 "./Bob Big Questions/youtube_auth.py"
else
    python3 youtube_auth.py
fi

echo ""
echo "Done! Press any key to close this terminal window."
read -n 1
