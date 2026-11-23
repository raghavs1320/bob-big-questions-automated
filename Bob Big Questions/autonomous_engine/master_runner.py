#!/usr/bin/env python3
"""Master Autonomous Daily Production Runner for Bob Big Questions.

Orchestrates the entire end-to-end pipeline:
1. Scouts viral topic (Gemini / Queue)
2. Writes comedic 7-year-old child-friendly screenplay (60s to 150s random duration)
3. Synthesizes Microsoft Ava voiceover + procedural ducked music
4. Renders 1080p 30fps animation with every-second visual shift
5. Designs high-CTR 2-line studio thumbnail
6. Publishes live to YouTube as PUBLIC at 4:00 AM

Can be run locally or autonomously via GitHub Actions.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to path
ENGINE_DIR = Path(__file__).resolve().parent
BASE_DIR = ENGINE_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from autonomous_engine.topic_scout import scout_viral_topic
from autonomous_engine.script_writer import generate_screenplay
from autonomous_engine.audio_pipeline import synthesize_all_scenes, assemble_and_mix_audio
from autonomous_engine.visual_director import render_masterpiece_video
from autonomous_engine.thumbnail_designer import create_high_ctr_thumbnail
from autonomous_engine.youtube_publisher import publish_to_youtube


def run_daily_production(dry_run: bool = False, privacy: str = "public"):
    print("\n" + "=" * 70)
    print("🚀 BOB BIG QUESTIONS — AUTONOMOUS DAILY PRODUCTION RUNNER")
    print(f"⏰ Execution Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔒 Privacy Mode : {privacy.upper()}")
    print("=" * 70)

    # Output directory for today's run
    run_id = time.strftime("%Y%m%d_%H%M%S")
    work_dir = BASE_DIR / "exports" / "runs" / f"run_{run_id}"
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1. Topic Scout
    print("\n[Stage 1/6] 🔍 Scouting High-Curiosity Viral Topic...")
    topic_data = scout_viral_topic()
    print(f" • Topic Selected: {topic_data['topic']}")
    print(f" • YouTube Title : {topic_data['title']}")

    # 2. Screenplay & Random Duration
    print("\n[Stage 2/6] 📝 Generating Child-Friendly Screenplay & Pacing...")
    screenplay = generate_screenplay(topic_data)
    target_dur = screenplay["target_duration"]
    num_scenes = len(screenplay["scenes"])
    print(f" • Random Duration Chosen: {target_dur}s ({num_scenes} scenes)")

    with open(work_dir / "screenplay.json", "w") as f:
        json.dump(screenplay, f, indent=2)

    # 3. Audio Synthesis (Microsoft Ava Neural)
    print("\n[Stage 3/6] 🎙️ Synthesizing Voiceover (AvaNeural +2%) & Procedural Music...")
    audio_dir = work_dir / "audio"
    scene_audio = synthesize_all_scenes(screenplay, audio_dir)
    master_audio = assemble_and_mix_audio(scene_audio, target_dur, audio_dir)
    print(f" • Master Audio Mix Ready: {master_audio.name}")

    # 4. 1080p Master Video Render (Every-Second Visual Shift)
    print("\n[Stage 4/6] 🎬 Rendering 1080p Masterpiece Video...")
    clean_title = "".join(c for c in topic_data["title"] if c.isalnum() or c in (" ", "_", "-")).strip()
    clean_title = clean_title.replace(" ", "_")[:50]
    video_out = work_dir / f"{clean_title}.mp4"
    render_masterpiece_video(screenplay, scene_audio, master_audio, video_out)
    print(f" • Master Video File: {video_out.resolve()}")

    # 5. High-CTR Thumbnail Design
    print("\n[Stage 5/6] 🖼️ Designing Studio High-CTR Thumbnail...")
    thumb_out = work_dir / f"{clean_title}_Thumbnail.jpg"
    create_high_ctr_thumbnail(screenplay["thumb_line1"], screenplay["thumb_line2"], thumb_out)
    print(f" • Thumbnail File: {thumb_out.resolve()}")

    # Build YouTube Description & Chapters
    chapters_text = "⏱️ Chapters:\n"
    cur_t = 0.0
    for sc in scene_audio:
        m, s = int(cur_t // 60), int(cur_t % 60)
        chapters_text += f"{m}:{s:02d} - {sc['banner']}\n"
        cur_t += sc.get("final_duration", 15.0)

    description = (
        f"{topic_data.get('hook', topic_data['topic'])}\n"
        f"Bob finds out what happens when {topic_data['topic'].lower()}!\n\n"
        f"{chapters_text}\n"
        f"🔔 Subscribe to Bob Big Questions for curious science and absurd what-if cartoons!\n"
        f"#BobBigQuestions #WhatIf #Science #Animation #KidsScience #Cartoon"
    )

    metadata = {
        "title": screenplay["title"],
        "description": description,
        "tags": screenplay.get("tags", ["bob big questions", "what if", "science cartoon", "animation"]),
        "category_id": "27"
    }

    # 6. YouTube Auto-Publish
    if dry_run:
        print("\n[Stage 6/6] ⏸️ DRY RUN COMPLETE: Video ready, skipping YouTube upload.")
        return {"status": "dry_run", "video": str(video_out), "thumbnail": str(thumb_out)}

    print("\n[Stage 6/6] 🔴 Uploading & Publishing to YouTube as PUBLIC...")
    result = publish_to_youtube(video_out, thumb_out, metadata, privacy=privacy)

    print("\n" + "=" * 70)
    print("🎉 EPISODE SUCCESSFULLY PUBLISHED LIVE ON YOUTUBE!")
    print("=" * 70)
    print(f" • Watch URL : {result['watch_url']}")
    print(f" • Studio URL: {result['studio_url']}")
    print(f" • Video ID  : {result['video_id']}")
    print("=" * 70 + "\n")

    # Save to history log
    log_file = BASE_DIR / "autonomous_engine" / "published_episodes.json"
    log = []
    if log_file.exists():
        try:
            with open(log_file, "r") as f:
                log = json.load(f)
        except Exception:
            pass
    log.append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "title": screenplay["title"],
        "video_id": result["video_id"],
        "watch_url": result["watch_url"],
        "duration": target_dur,
        "privacy": privacy
    })
    with open(log_file, "w") as f:
        json.dump(log, f, indent=2)

    return result


if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    run_daily_production(dry_run=is_dry)
