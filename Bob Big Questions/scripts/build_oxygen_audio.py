"""Audio Generation Pipeline for Episode 8 (2m 30s):
'What If Earth Lost Oxygen For Just 5 Seconds?'

Target Duration: Exactly 150.0 seconds (2 minutes 30 seconds).
Voice: Edge-TTS en-US-AvaNeural at +2% rate (the beloved original pacing).
Music: Bouncy cartoon groove ducked dynamically under speech.
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path
import edge_tts

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_DIR / "audio" / "oxygen_150s"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_SOURCE = BASE_DIR / "audio" / "gravity_cartoon_music.wav"

from utils.hardware import get_ffmpeg_binary
from voice.audio_processor import get_audio_duration

FFMPEG_BIN = get_ffmpeg_binary()

TARGET_TOTAL_SECONDS = 150.0
FPS = 30
SAMPLE_RATE = 48000

SCENES_SCRIPT = [
    {
        "id": 1,
        "title": "SECOND 00: THE 5-SECOND BREATH CHALLENGE",
        "text": "Five seconds without oxygen doesn't sound so bad, right? Bob can easily hold his breath for thirty seconds while eating cereal. But what Bob doesn't know is that oxygen isn't just for breathing. It is the molecular glue holding our entire civilized planet together!"
    },
    {
        "id": 2,
        "title": "SECOND 01: CONCRETE CRUMBLES TO POWDER!",
        "text": "Second one! Oxygen is the chemical binder in all concrete. Without oxygen molecules, concrete instantly loses its structural bond and turns into fine white dust! High-rise apartments, the Hoover Dam, and suspension bridges instantly crumble like powdered sugar!"
    },
    {
        "id": 3,
        "title": "SECOND 02: THE NOON SKY TURNS PITCH BLACK!",
        "text": "Second two! Look up at the noon sky. It isn't blue anymore—it’s pitch black! Earth's daytime sky looks blue because oxygen atoms scatter sunlight. With no oxygen, daytime Earth looks like outer space, with blazing white stars and an eerie blinding sun!"
    },
    {
        "id": 4,
        "title": "SECOND 03: 21% AIR PRESSURE DROP!",
        "text": "Second three! Oxygen makes up twenty-one percent of atmospheric air pressure. When it vanishes in one millisecond, air pressure plummets instantly! It feels like teleporting to the top of Mount Everest in a blink. Everyone’s inner ear drums rupture with a painful pop!"
    },
    {
        "id": 5,
        "title": "SECOND 04: INSTANT METAL COLD WELDING!",
        "text": "Second four! The only reason metals don't fuse together when touching is a microscopic layer of oxidation. With zero oxygen, cold welding takes over instantly! Every car engine, door hinge, and metal zipper permanently welds solid into a single block of steel!"
    },
    {
        "id": 6,
        "title": "SECOND 05: 46% OF EARTH'S CRUST VANISHES!",
        "text": "Second five: the grand disaster! Oxygen makes up forty-six percent of Earth's solid crust! That's right—nearly half the rocks and dirt beneath your shoes is oxygen! The ground beneath Bob dissolves into a bottomless crumbly abyss, sending everything into a planetary freefall!"
    },
    {
        "id": 7,
        "title": "SECOND 06: OXYGEN REBOUNDS & THUNDERCLAP!",
        "text": "SNAP! Five seconds expire, and oxygen floods back into the universe! Concrete particles crash together, the sky turns vibrant blue again, and air pressure slams back with a planetary thunderclap! Bob’s sofa lands with a massive cartoon bounce right in the middle of a giant sand dune!"
    },
    {
        "id": 8,
        "title": "SAFE & FRESH AIR OUTRO",
        "text": "Covered in dust and coughing out chalk, Bob takes the biggest breath of fresh oxygen in human history. Maybe hold your breath underwater next time, Bob! Subscribe to Bob Big Questions, and tell us in the comments: what question should Bob survive next?!"
    }
]


async def synthesize_all_scenes():
    print("🎙️ Synthesizing 8 Scene Voiceovers with Edge-TTS (en-US-AvaNeural +2%)...")
    raw_files = []
    for sc in SCENES_SCRIPT:
        out_f = AUDIO_DIR / f"raw_scene{sc['id']:02d}.mp3"
        comm = edge_tts.Communicate(sc["text"], "en-US-AvaNeural", rate="+2%")
        await comm.save(str(out_f))
        raw_files.append(out_f)
        print(f"  ✓ Scene {sc['id']:02d}: {sc['title']}")
    return raw_files


def assemble_and_balance_audio():
    raw_durations = []
    for sc in SCENES_SCRIPT:
        f_p = AUDIO_DIR / f"raw_scene{sc['id']:02d}.mp3"
        dur = get_audio_duration(str(f_p))
        raw_durations.append(dur)

    raw_total = sum(raw_durations)
    remaining_time = TARGET_TOTAL_SECONDS - raw_total
    num_scenes = len(SCENES_SCRIPT)
    pad_per_scene = max(0.1, remaining_time / float(num_scenes))

    print(f"📊 Raw Voice Duration: {raw_total:.2f}s | Target: {TARGET_TOTAL_SECONDS:.1f}s")
    print(f"⏱️ Pause Padding Per Scene: {pad_per_scene:.3f}s")

    scene_specs = []
    padded_files = []
    accum_frames = 0

    for i, sc in enumerate(SCENES_SCRIPT):
        raw_dur = raw_durations[i]
        final_scene_dur = raw_dur + pad_per_scene
        scene_frames = int(round(final_scene_dur * FPS))

        start_frame = accum_frames
        end_frame = accum_frames + scene_frames
        accum_frames = end_frame

        pad_f = AUDIO_DIR / f"padded_scene{sc['id']:02d}.wav"
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(AUDIO_DIR / f"raw_scene{sc['id']:02d}.mp3"),
            "-af", f"apad=pad_dur={pad_per_scene:.3f}",
            "-ar", str(SAMPLE_RATE),
            "-ac", "2",
            str(pad_f)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        padded_files.append(pad_f)

        scene_specs.append({
            "id": sc["id"],
            "title": sc["title"],
            "start_frame": start_frame,
            "end_frame": end_frame,
            "duration_frames": scene_frames,
            "duration_seconds": final_scene_dur
        })

    # Concatenate into full_voice_150s.wav
    concat_list = AUDIO_DIR / "concat_scenes.txt"
    with open(concat_list, "w") as f:
        for pf in padded_files:
            f.write(f"file '{pf.resolve()}'\n")

    full_voice_wav = AUDIO_DIR / "full_voice_150s.wav"
    subprocess.run([
        FFMPEG_BIN, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(full_voice_wav)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Mix with looped background music
    final_mixed_audio = AUDIO_DIR / "full_audio_mix_150s.wav"
    filter_complex = (
        f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{TARGET_TOTAL_SECONDS:.2f},volume=0.25,afade=t=out:st=147:d=3[music];"
        f"[0:a]volume=1.1[voice];"
        f"[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-i", str(full_voice_wav),
        "-i", str(MUSIC_SOURCE),
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        str(final_mixed_audio)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Save scene_timings.json
    timings_path = AUDIO_DIR / "scene_timings.json"
    with open(timings_path, "w") as f:
        json.dump({
            "target_seconds": TARGET_TOTAL_SECONDS,
            "total_frames": accum_frames,
            "fps": FPS,
            "scenes": scene_specs
        }, f, indent=2)

    print(f"✅ Generated Master 150.0s Audio Mix: {final_mixed_audio}")
    print(f"🎬 Total Frames: {accum_frames} ({accum_frames / float(FPS):.2f}s)")
    return str(final_mixed_audio), str(timings_path)


def main():
    asyncio.run(synthesize_all_scenes())
    assemble_and_balance_audio()


if __name__ == "__main__":
    main()
